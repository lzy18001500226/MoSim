"""Audited lifecycle core shared by Model Studio and Flight Console."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = PROJECT_ROOT / "Config" / "control_platform" / "control_module_registry.json"
DEFAULT_PROFILE_CATALOG = PROJECT_ROOT / "Config" / "profiles" / "catalog.json"
DEFAULT_RUN_ROOT = PROJECT_ROOT / "Results" / "ui_platform" / "orchestrator_runs"

ORCHESTRATOR_COMMANDS = frozenset(
    {
        "validate_experiment_profile",
        "prepare_run",
        "start_run",
        "stop_run",
        "reset_run",
        "apply_injection",
        "restore_injection",
        "prepare_display_session",
        "attach_display",
        "detach_display",
        "capture_display_evidence",
        "get_run_state",
        "get_telemetry",
        "get_result_packet",
        "open_model_context",
    }
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def _portable_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _resolve_project_path(path: str) -> Path | None:
    candidate = Path(path)
    candidate = candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
    resolved = candidate.resolve()
    return resolved if resolved.is_relative_to(PROJECT_ROOT) else None


class RuntimeBackend(Protocol):
    backend_id: str

    def start(self, manifest: dict[str, Any]) -> dict[str, Any]: ...

    def stop(self, manifest: dict[str, Any]) -> dict[str, Any]: ...

    def reset(self, manifest: dict[str, Any]) -> dict[str, Any]: ...

    def apply_injection(self, manifest: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class MoSimOrchestrator:
    run_root: Path = DEFAULT_RUN_ROOT
    registry_path: Path = DEFAULT_REGISTRY
    profile_catalog_path: Path = DEFAULT_PROFILE_CATALOG
    backend: RuntimeBackend | None = None
    active_run_id: str = ""
    manifests: dict[str, dict[str, Any]] = field(default_factory=dict)
    display_sessions: dict[str, dict[str, Any]] = field(default_factory=dict)

    def _response(self, request_id: str, accepted: bool, reason_code: str, **extra: Any) -> dict[str, Any]:
        run_id = extra.pop("run_id", self.active_run_id)
        profile_hash = extra.pop("profile_hash", "")
        if not profile_hash and run_id:
            profile_hash = self.manifests.get(run_id, {}).get("experiment_profile_hash", "")
        response = {
            "schema": "mosim.orchestrator.response.v1",
            "request_id": request_id or f"req-{uuid.uuid4().hex}",
            "accepted": accepted,
            "reason_code": reason_code,
            "run_id": run_id,
            "profile_hash": profile_hash,
            "timestamp": time.time(),
        }
        response.update(extra)
        return response

    def _module(self, controller_id: str) -> dict[str, Any] | None:
        registry = _read_json(self.registry_path)
        return next((item for item in registry.get("modules", []) if item.get("module_id") == controller_id), None)

    def validate_experiment_profile(
        self,
        *,
        request_id: str,
        profile_path: str,
        controller_id: str,
        vehicle_count: int,
    ) -> dict[str, Any]:
        path = _resolve_project_path(profile_path)
        if path is None:
            return self._response(request_id, False, "profile_path_outside_project")
        if not path.is_file():
            return self._response(request_id, False, "profile_not_found", profile_path=str(path))
        try:
            profile = _read_json(path)
        except (OSError, ValueError) as exc:
            return self._response(request_id, False, "profile_invalid_json", detail=str(exc))

        module = self._module(controller_id)
        if module is None:
            return self._response(request_id, False, "controller_not_registered")
        if module.get("status") != "accepted" or module.get("selectable") is not True:
            return self._response(
                request_id,
                False,
                "controller_runtime_gate_pending",
                controller_status=module.get("status"),
                claim_ceiling=module.get("claim_ceiling", ""),
            )
        if vehicle_count not in {1, 3}:
            return self._response(request_id, False, "vehicle_scale_gate_pending", vehicle_count=vehicle_count)

        experiment = profile.get("experiment_profile")
        if not isinstance(experiment, dict):
            return self._response(request_id, False, "experiment_profile_missing")
        expected_controller = module.get("profile_id", "")
        if experiment.get("controller_profile") != expected_controller:
            return self._response(
                request_id,
                False,
                "profile_controller_mismatch",
                selected_controller_profile=expected_controller,
                profile_controller_profile=experiment.get("controller_profile", ""),
            )

        scenario_id = experiment.get("scenario_profile", "")
        scenario_path_value = experiment.get("scenario_path")
        declared_vehicle_count = experiment.get("vehicle_count")
        if scenario_path_value is not None:
            scenario_path = _resolve_project_path(str(scenario_path_value))
            if scenario_path is None or not scenario_path.is_file():
                return self._response(request_id, False, "scenario_path_invalid", scenario_path=scenario_path_value)
            if not isinstance(declared_vehicle_count, int):
                return self._response(request_id, False, "profile_vehicle_count_missing")
        else:
            catalog = _read_json(self.profile_catalog_path)
            scenario = catalog.get("scenario_profiles", {}).get(scenario_id)
            if not isinstance(scenario, dict):
                return self._response(request_id, False, "scenario_profile_not_registered", scenario_profile=scenario_id)
            declared_vehicle_count = scenario.get("vehicle_count")
        if declared_vehicle_count != vehicle_count:
            return self._response(
                request_id,
                False,
                "profile_vehicle_count_mismatch",
                profile_vehicle_count=declared_vehicle_count,
                selected_vehicle_count=vehicle_count,
            )

        profile_hash = _canonical_hash(profile)
        return self._response(
            request_id,
            True,
            "profile_valid",
            profile_path=str(path.relative_to(PROJECT_ROOT)),
            profile_hash=profile_hash,
            experiment_profile_id=experiment.get("id", ""),
            controller_id=controller_id,
            controller_profile_id=module.get("profile_id", ""),
            vehicle_count=vehicle_count,
        )

    def prepare_run(
        self,
        *,
        request_id: str,
        profile_path: str,
        controller_id: str,
        vehicle_count: int,
        parameter_set: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        validation = self.validate_experiment_profile(
            request_id=request_id,
            profile_path=profile_path,
            controller_id=controller_id,
            vehicle_count=vehicle_count,
        )
        if not validation["accepted"]:
            return validation

        run_id = f"run-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        parameters = parameter_set or {}
        manifest = {
            "schema": "mosim.orchestrator.run_manifest.v1",
            "run_id": run_id,
            "lifecycle_state": "ready",
            "runtime_started": False,
            "runtime_backend": getattr(self.backend, "backend_id", "unconfigured"),
            "profile_path": validation["profile_path"],
            "experiment_profile_id": validation["experiment_profile_id"],
            "experiment_profile_hash": validation["profile_hash"],
            "controller_id": controller_id,
            "controller_profile_id": validation["controller_profile_id"],
            "parameter_set": parameters,
            "parameter_set_hash": _canonical_hash(parameters),
            "vehicle_count": vehicle_count,
            "created_at": time.time(),
            "updated_at": time.time(),
            "display_sessions": [],
            "injections": [],
            "events": [],
            "evidence_paths": {},
        }
        self.manifests[run_id] = manifest
        self.active_run_id = run_id
        self._save(manifest)
        return self._response(request_id, True, "run_prepared", run_id=run_id, manifest=manifest)

    def _get_manifest(self, run_id: str) -> dict[str, Any] | None:
        if run_id in self.manifests:
            return self.manifests[run_id]
        path = self.run_root / run_id / "RUN_MANIFEST.json"
        if path.is_file():
            self.manifests[run_id] = _read_json(path)
            return self.manifests[run_id]
        return None

    def _save(self, manifest: dict[str, Any]) -> None:
        manifest["updated_at"] = time.time()
        _write_json(self.run_root / manifest["run_id"] / "RUN_MANIFEST.json", manifest)

    def _event(self, manifest: dict[str, Any], event_type: str, **payload: Any) -> None:
        event = {"timestamp": time.time(), "event_type": event_type, **payload}
        manifest["events"].append(event)
        path = self.run_root / manifest["run_id"] / "events.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")

    def start_run(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        if manifest["lifecycle_state"] != "ready":
            return self._response(request_id, False, "run_not_ready", run_id=run_id)
        if self.backend is None:
            return self._response(request_id, False, "runtime_backend_unconfigured", run_id=run_id)

        result = self.backend.start(manifest)
        if not result.get("accepted"):
            manifest["lifecycle_state"] = "blocked"
            self._event(manifest, "runtime_start_rejected", backend_result=result)
            self._save(manifest)
            return self._response(request_id, False, result.get("reason_code", "runtime_start_failed"), run_id=run_id)
        lifecycle_state = result.get("lifecycle_state", "running")
        if lifecycle_state not in {"starting", "running"}:
            lifecycle_state = "starting"
        manifest["lifecycle_state"] = lifecycle_state
        manifest["runtime_started"] = True
        self._event(manifest, "runtime_started", backend_result=result)
        self._save(manifest)
        reason_code = "run_started" if lifecycle_state == "running" else "run_starting"
        return self._response(request_id, True, reason_code, run_id=run_id, backend_result=result)

    def stop_run(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        if manifest["lifecycle_state"] not in {"starting", "running"} or self.backend is None:
            return self._response(request_id, False, "run_not_active", run_id=run_id)
        result = self.backend.stop(manifest)
        if not result.get("accepted"):
            return self._response(request_id, False, result.get("reason_code", "runtime_stop_failed"), run_id=run_id)
        manifest["lifecycle_state"] = "completed"
        manifest["runtime_started"] = False
        self._event(manifest, "runtime_stopped", backend_result=result)
        self._save(manifest)
        return self._response(request_id, True, "run_stopped", run_id=run_id)

    def reset_run(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        if manifest["lifecycle_state"] in {"starting", "running"}:
            return self._response(request_id, False, "stop_required_before_reset", run_id=run_id)
        if self.backend is not None:
            result = self.backend.reset(manifest)
            if not result.get("accepted"):
                return self._response(request_id, False, result.get("reason_code", "runtime_reset_failed"), run_id=run_id)
        manifest["lifecycle_state"] = "ready"
        manifest["runtime_started"] = False
        manifest["injections"] = []
        self._event(manifest, "run_reset")
        self._save(manifest)
        return self._response(request_id, True, "run_reset", run_id=run_id)

    def apply_injection(self, *, request_id: str, run_id: str, command: dict[str, Any]) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        if manifest["lifecycle_state"] != "running" or self.backend is None:
            return self._response(request_id, False, "run_not_active", run_id=run_id)
        result = self.backend.apply_injection(manifest, command)
        record = {"request": command, "backend_result": result, "timestamp": time.time()}
        manifest["injections"].append(record)
        self._event(manifest, "injection_result", record=record)
        self._save(manifest)
        return self._response(
            request_id,
            bool(result.get("accepted")),
            result.get("reason_code", "injection_result"),
            run_id=run_id,
            requested_value=command.get("value"),
            applied_value=result.get("applied_value"),
        )

    def restore_injection(self, *, request_id: str, run_id: str, command: dict[str, Any]) -> dict[str, Any]:
        payload = dict(command)
        payload["apply_mode"] = "restore"
        return self.apply_injection(request_id=request_id, run_id=run_id, command=payload)

    def prepare_display_session(self, *, request_id: str, run_id: str, displays: list[str]) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        supported = {"rviz_pointcloud", "rviz_gridmap", "unreal", "mworks_result"}
        unknown = sorted(set(displays) - supported)
        if unknown:
            return self._response(request_id, False, "unsupported_display", run_id=run_id, unknown=unknown)
        session_id = f"display-{uuid.uuid4().hex[:10]}"
        session = {"session_id": session_id, "run_id": run_id, "displays": displays, "state": "prepared"}
        self.display_sessions[session_id] = session
        manifest["display_sessions"].append(session_id)
        self._event(manifest, "display_session_prepared", session=session)
        self._save(manifest)
        return self._response(request_id, True, "display_session_prepared", run_id=run_id, session=session)

    def attach_display(self, *, request_id: str, session_id: str) -> dict[str, Any]:
        session = self.display_sessions.get(session_id)
        if session is None:
            return self._response(request_id, False, "display_session_not_found")
        session["state"] = "attached"
        return self._response(request_id, True, "display_attached", run_id=session["run_id"], session=session)

    def detach_display(self, *, request_id: str, session_id: str) -> dict[str, Any]:
        session = self.display_sessions.get(session_id)
        if session is None:
            return self._response(request_id, False, "display_session_not_found")
        session["state"] = "detached"
        return self._response(request_id, True, "display_detached", run_id=session["run_id"], session=session)

    def capture_display_evidence(
        self, *, request_id: str, run_id: str, session_id: str, evidence_path: str
    ) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        session = self.display_sessions.get(session_id)
        path = _resolve_project_path(evidence_path)
        if manifest is None or session is None or session.get("run_id") != run_id:
            return self._response(request_id, False, "display_session_not_found", run_id=run_id)
        if path is None:
            return self._response(request_id, False, "display_evidence_outside_project", run_id=run_id)
        if not path.is_file():
            return self._response(request_id, False, "display_evidence_not_found", run_id=run_id)
        manifest["evidence_paths"].setdefault("display", []).append(evidence_path)
        self._event(manifest, "display_evidence_captured", path=evidence_path)
        self._save(manifest)
        return self._response(request_id, True, "display_evidence_recorded", run_id=run_id)

    def get_run_state(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        poll = getattr(self.backend, "poll", None)
        if manifest["lifecycle_state"] in {"starting", "running"} and callable(poll):
            backend_state = poll(manifest)
            next_state = backend_state.get("lifecycle_state")
            if next_state in {"running", "completed", "blocked", "failed"}:
                manifest["lifecycle_state"] = next_state
                if next_state in {"completed", "blocked", "failed"}:
                    manifest["runtime_started"] = False
                self._event(manifest, "runtime_state_changed", backend_result=backend_state)
                self._save(manifest)
        return self._response(request_id, True, "run_state_ready", run_id=run_id, manifest=manifest)

    def get_telemetry(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        telemetry_path = self.run_root / run_id / "telemetry.json"
        if not telemetry_path.is_file():
            return self._response(request_id, False, "telemetry_not_available", run_id=run_id)
        return self._response(request_id, True, "telemetry_ready", run_id=run_id, telemetry=_read_json(telemetry_path))

    def get_result_packet(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        packet_path = self.run_root / run_id / "RESULT_PACKET.json"
        if not packet_path.is_file():
            return self._response(request_id, False, "result_packet_not_available", run_id=run_id)
        return self._response(request_id, True, "result_packet_ready", run_id=run_id, packet=_read_json(packet_path))

    def open_model_context(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        request_path = self.run_root / run_id / "OPEN_MODEL_CONTEXT_REQUEST.json"
        payload = {
            "schema": "mosim.open_model_context.request.v1",
            "run_id": run_id,
            "profile_path": manifest["profile_path"],
            "controller_id": manifest["controller_id"],
            "created_at": time.time(),
            "status": "requested",
        }
        _write_json(request_path, payload)
        return self._response(
            request_id,
            True,
            "model_context_requested",
            run_id=run_id,
            request_path=_portable_path(request_path),
        )
