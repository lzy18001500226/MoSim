"""Audited lifecycle core shared by Model Studio and Flight Console."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = PROJECT_ROOT / "Config" / "control_platform" / "control_module_registry.json"
DEFAULT_PROFILE_CATALOG = PROJECT_ROOT / "Config" / "profiles" / "catalog.json"
DEFAULT_RUN_ROOT = PROJECT_ROOT / "Results" / "ui_platform" / "orchestrator_runs"
MWORKS_LIVE_PREFLIGHT = PROJECT_ROOT / "Scripts" / "mworks_live" / "preflight_connection.py"

ORCHESTRATOR_COMMANDS = frozenset(
    {
        "validate_experiment_profile",
        "preflight_connection",
        "prepare_run",
        "start_run",
        "request_safe_stop",
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
        "run_mil",
        "generate_code",
        "get_model_gate_state",
        "list_controllers",
        "propose_operator_task",
        "get_operation_progress",
        "close_all_rviz",
        "start_ue_recording",
        "stop_ue_recording",
    }
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    operations: dict[str, dict[str, Any]] = field(default_factory=dict)
    connection_preflight_runner: Callable[..., dict[str, Any]] | None = None

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

    def list_controllers(self, *, request_id: str) -> dict[str, Any]:
        registry = _read_json(self.registry_path)
        controllers = []
        for module in registry.get("modules", []):
            if module.get("kind") != "nominal_controller":
                continue
            module_id = str(module.get("module_id", ""))
            status = str(module.get("status", "unknown"))
            selectable = module.get("selectable") is True
            enabled = status == "accepted" and selectable
            disabled_reason = ""
            if not enabled:
                disabled_reason = str(module.get("disabled_reason") or "")
                if not disabled_reason:
                    disabled_reason = (
                        f"controller_status_{status}" if status != "accepted" else "controller_not_selectable"
                    )
            controllers.append(
                {
                    "module_id": module_id,
                    "label": module_id.replace("_", " "),
                    "family": module.get("family", ""),
                    "kind": module.get("kind", ""),
                    "profile_id": module.get("profile_id", ""),
                    "status": status,
                    "selectable": selectable,
                    "enabled": enabled,
                    "disabled_reason": disabled_reason,
                    "claim_ceiling": module.get("claim_ceiling", ""),
                    "output_variant": module.get("output_variant", ""),
                }
            )
        controllers.sort(key=lambda item: (not item["enabled"], str(item["family"]), item["module_id"]))
        return self._response(
            request_id,
            True,
            "controller_catalog_ready",
            controllers=controllers,
            registry_hash=_canonical_hash(registry),
        )

    def propose_operator_task(self, *, request_id: str, prompt: str) -> dict[str, Any]:
        text = str(prompt).strip()
        if not text:
            return self._response(request_id, False, "agent_prompt_empty")
        if len(text) > 1000:
            return self._response(request_id, False, "agent_prompt_too_long")

        normalized = text.casefold()
        tasks = (
            {
                "profile_id": "cascade_pid_figure8_generated_c_v1",
                "profile_path": "Config/profiles/experiments/cascade_pid_figure8_generated_c_v1.json",
                "controller_id": "cascade_pid",
                "vehicle_count": 1,
                "label": "生成代码控制器8字飞行",
                "keywords": ("生成代码", "generated c", "codegen"),
                "manual_control": False,
            },
            {
                "profile_id": "factory_l2_fuel_fixed64_exploration_v1",
                "profile_path": "Config/profiles/experiments/factory_l2_fuel_fixed64_exploration_v1.json",
                "controller_id": "px4ctrl",
                "vehicle_count": 1,
                "label": "FUEL单机自主探索",
                "keywords": ("fuel", "自主探索", "探索"),
                "manual_control": False,
            },
            {
                "profile_id": "factory_l2_three_uav_swarm_formation_v1",
                "profile_path": "Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json",
                "controller_id": "px4ctrl",
                "vehicle_count": 3,
                "label": "三机固定编队避障",
                "keywords": ("三机", "编队", "formation", "swarm"),
                "manual_control": False,
            },
            {
                "profile_id": "px4ctrl_figure8_baseline_v1",
                "profile_path": "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json",
                "controller_id": "px4ctrl",
                "vehicle_count": 1,
                "label": "单机8字飞行",
                "keywords": ("8字", "八字", "figure eight", "figure8"),
                "manual_control": False,
            },
            {
                "profile_id": "px4ctrl_ground_standby_v1",
                "profile_path": "Config/profiles/experiments/px4ctrl_ground_standby_v1.json",
                "controller_id": "px4ctrl",
                "vehicle_count": 1,
                "label": "单机定点操纵",
                "keywords": ("定点", "手动", "wasd", "悬停"),
                "manual_control": True,
            },
        )
        task = next(
            (candidate for candidate in tasks if any(keyword in normalized for keyword in candidate["keywords"])),
            None,
        )
        if task is None:
            return self._response(
                request_id,
                False,
                "agent_intent_not_recognized",
                supported_intents=[candidate["label"] for candidate in tasks],
            )

        profile_path = PROJECT_ROOT / str(task["profile_path"])
        if not profile_path.is_file():
            return self._response(request_id, False, "agent_profile_missing", profile_path=str(task["profile_path"]))
        proposal = {key: value for key, value in task.items() if key != "keywords"}
        proposal.update(
            {
                "requires_user_confirmation": True,
                "may_start_flight": False,
                "next_action": "confirm_then_prepare_run",
                "source": "bounded_local_intent_router_v1",
            }
        )
        return self._response(request_id, True, "agent_proposal_ready", proposal=proposal)

    def _operation_path(self, run_id: str, operation_id: str) -> Path:
        return self.run_root / run_id / "operations" / f"{operation_id}.json"

    def _create_operation(
        self,
        *,
        request_id: str,
        run_id: str,
        action: str,
        stage_id: str,
        stage_label: str,
        max_attempts: int = 1,
        cancellable: bool = False,
        safe_stop_only: bool = False,
    ) -> dict[str, Any]:
        digest = hashlib.sha256(f"{request_id}:{action}:{run_id}".encode("utf-8")).hexdigest()[:16]
        operation_id = f"op-{digest}"
        existing = self.operations.get(operation_id)
        if existing is None:
            path = self._operation_path(run_id, operation_id)
            if path.is_file():
                existing = _read_json(path)
        if existing is not None:
            self.operations[operation_id] = existing
            return existing
        now = time.time()
        operation = {
            "schema": "mosim.operation_progress.v1",
            "operation_id": operation_id,
            "request_id": request_id,
            "run_id": run_id,
            "action": action,
            "state": "running",
            "stage_id": stage_id,
            "stage_label": stage_label,
            "progress_mode": "indeterminate",
            "progress_percent": None,
            "attempt": 1,
            "max_attempts": max_attempts,
            "cancellable": cancellable,
            "safe_stop_only": safe_stop_only,
            "reason_code": "operation_started",
            "started_at": now,
            "updated_at": now,
        }
        self.operations[operation_id] = operation
        manifest = self._get_manifest(run_id)
        if manifest is not None and operation_id not in manifest.setdefault("operations", []):
            manifest["operations"].append(operation_id)
            self._save(manifest)
        self._save_operation(operation)
        return operation

    def _save_operation(self, operation: dict[str, Any]) -> None:
        operation["updated_at"] = time.time()
        self.operations[operation["operation_id"]] = operation
        _write_json(self._operation_path(operation["run_id"], operation["operation_id"]), operation)

    def _finish_operation(
        self,
        operation: dict[str, Any],
        *,
        accepted: bool,
        reason_code: str,
        stage_id: str,
        stage_label: str,
    ) -> None:
        operation.update(
            {
                "state": "completed" if accepted else "failed",
                "stage_id": stage_id,
                "stage_label": stage_label,
                "progress_mode": "determinate" if accepted else "indeterminate",
                "progress_percent": 100 if accepted else None,
                "reason_code": reason_code,
            }
        )
        self._save_operation(operation)

    def _load_operation(self, run_id: str, operation_id: str) -> dict[str, Any] | None:
        operation = self.operations.get(operation_id)
        if operation is not None and operation.get("run_id") == run_id:
            return operation
        path = self._operation_path(run_id, operation_id)
        if not path.is_file():
            return None
        operation = _read_json(path)
        self.operations[operation_id] = operation
        return operation

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

        experiment = profile.get("experiment_profile")
        if not isinstance(experiment, dict):
            return self._response(request_id, False, "experiment_profile_missing")
        is_mworks_live = experiment.get("controller_backend") == "mworks_live"
        if is_mworks_live:
            rt0_evidence = _resolve_project_path(str(experiment.get("rt0_evidence", "")))
            if (
                experiment.get("profile_status") not in {"active", "accepted"}
                or experiment.get("capability_status") != "rt0_validated"
                or rt0_evidence is None
                or not rt0_evidence.is_file()
            ):
                return self._response(request_id, False, "mworks_live_rt0_gate_pending")

        module = self._module(controller_id)
        if module is None:
            return self._response(request_id, False, "controller_not_registered")
        allowed_statuses = {"accepted", "implemented"} if is_mworks_live else {"accepted"}
        if module.get("status") not in allowed_statuses or module.get("selectable") is not True:
            return self._response(
                request_id,
                False,
                "controller_runtime_gate_pending",
                controller_status=module.get("status"),
                claim_ceiling=module.get("claim_ceiling", ""),
            )
        if vehicle_count not in {1, 3}:
            return self._response(request_id, False, "vehicle_scale_gate_pending", vehicle_count=vehicle_count)

        expected_controller = module.get("profile_id", "")
        selected_controller_profile = str(experiment.get("controller_profile", ""))
        if is_mworks_live:
            catalog = _read_json(self.profile_catalog_path)
            controller_profile = catalog.get("controller_profiles", {}).get(selected_controller_profile)
            profile_matches = (
                isinstance(controller_profile, dict)
                and controller_profile.get("controller_id") == controller_id
                and controller_profile.get("output_interface") == "ATTITUDE_THRUST"
            )
        else:
            profile_matches = selected_controller_profile == expected_controller
        if not profile_matches:
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
        scenario_snapshot: dict[str, Any]
        scenario_path_relative = ""
        if scenario_path_value is not None:
            scenario_path = _resolve_project_path(str(scenario_path_value))
            if scenario_path is None or not scenario_path.is_file():
                return self._response(request_id, False, "scenario_path_invalid", scenario_path=scenario_path_value)
            try:
                scenario_snapshot = _read_json(scenario_path)
            except (OSError, ValueError, json.JSONDecodeError):
                return self._response(request_id, False, "scenario_payload_invalid", scenario_path=scenario_path_value)
            if not isinstance(scenario_snapshot, dict):
                return self._response(request_id, False, "scenario_payload_invalid", scenario_path=scenario_path_value)
            scenario_path_relative = str(scenario_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            if not isinstance(declared_vehicle_count, int):
                return self._response(request_id, False, "profile_vehicle_count_missing")
        else:
            catalog = _read_json(self.profile_catalog_path)
            scenario = catalog.get("scenario_profiles", {}).get(scenario_id)
            if not isinstance(scenario, dict):
                return self._response(request_id, False, "scenario_profile_not_registered", scenario_profile=scenario_id)
            scenario_snapshot = scenario
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
            selected_controller_profile_id=selected_controller_profile,
            controller_backend=experiment.get("controller_backend", "generated_c"),
            capability_status=experiment.get("capability_status", ""),
            rt0_evidence=experiment.get("rt0_evidence", ""),
            requested_rate_hz=(
                _read_json(self.profile_catalog_path)
                .get("frequency_profiles", {})
                .get(experiment.get("frequency_profile", ""), {})
                .get("controller_rate_hz")
            ),
            scenario_profile_id=scenario_id,
            scenario_path=scenario_path_relative,
            scenario_hash=_canonical_hash(scenario_snapshot),
            scenario_snapshot=scenario_snapshot,
            vehicle_count=vehicle_count,
        )

    def _invoke_connection_preflight(self, **endpoint: Any) -> dict[str, Any]:
        if self.connection_preflight_runner is not None:
            return self.connection_preflight_runner(**endpoint)
        spec = importlib.util.spec_from_file_location("mosim_mworks_live_preflight", MWORKS_LIVE_PREFLIGHT)
        if spec is None or spec.loader is None:
            raise RuntimeError("connection_preflight_backend_unavailable")
        module_dir = str(MWORKS_LIVE_PREFLIGHT.parent)
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        value = module.Endpoint(
            endpoint["target_host"],
            endpoint["rt1_udp_port"],
            endpoint["ros_master_uri"],
            endpoint["local_advertised_ip"],
            endpoint["requested_rate_hz"],
        )
        return module.run_preflight(value, timeout_s=endpoint["timeout_s"], sample_count=endpoint["sample_count"])

    def preflight_connection(
        self,
        *,
        request_id: str,
        profile_path: str,
        controller_id: str,
        vehicle_count: int,
        target_host: str,
        rt1_udp_port: int,
        ros_master_uri: str,
        local_advertised_ip: str = "auto",
        requested_rate_hz: int = 200,
        timeout_s: float = 0.35,
        sample_count: int = 5,
    ) -> dict[str, Any]:
        validation = self.validate_experiment_profile(
            request_id=request_id,
            profile_path=profile_path,
            controller_id=controller_id,
            vehicle_count=vehicle_count,
        )
        if not validation["accepted"]:
            return validation
        if validation.get("controller_backend") != "mworks_live":
            return self._response(request_id, False, "connection_preflight_not_required")
        if requested_rate_hz not in {50, 100, 200}:
            return self._response(request_id, False, "requested_rate_unsupported")

        endpoint = {
            "target_host": target_host,
            "rt1_udp_port": rt1_udp_port,
            "ros_master_uri": ros_master_uri,
            "local_advertised_ip": local_advertised_ip,
            "requested_rate_hz": requested_rate_hz,
            "timeout_s": timeout_s,
            "sample_count": sample_count,
        }
        try:
            transport = self._invoke_connection_preflight(**endpoint)
        except (OSError, RuntimeError, ValueError) as exc:
            return self._response(
                request_id, False, "connection_preflight_backend_failed", detail=str(exc), endpoint=endpoint
            )

        profile_rate = validation.get("requested_rate_hz")
        rate_validated = (
            requested_rate_hz == profile_rate
            and validation.get("capability_status") == "rt0_validated"
            and bool(validation.get("rt0_evidence"))
        )
        transport_ok = bool(transport.get("accepted"))
        accepted = transport_ok and rate_validated
        reason_code = (
            "connection_preflight_passed"
            if accepted
            else "requested_rate_unvalidated"
            if transport_ok
            else str(transport.get("reason_code", "connection_preflight_failed"))
        )
        preflight_id = f"preflight-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        packet = {
            "schema": "mosim.orchestrator.connection_preflight.v1",
            "preflight_id": preflight_id,
            "accepted": accepted,
            "transport_ok": transport_ok,
            "rate_validated": rate_validated,
            "reason_code": reason_code,
            "profile_path": validation["profile_path"],
            "profile_id": validation["experiment_profile_id"],
            "profile_hash": validation["profile_hash"],
            "controller_id": controller_id,
            "vehicle_count": vehicle_count,
            "endpoint": {key: value for key, value in endpoint.items() if key not in {"timeout_s", "sample_count"}},
            "transport": transport,
            "created_at": time.time(),
        }
        packet["preflight_result_hash"] = _canonical_hash(packet)
        _write_json(self.run_root / "_preflight" / f"{preflight_id}.json", packet)
        return self._response(
            request_id,
            accepted,
            reason_code,
            profile_hash=validation["profile_hash"],
            preflight=packet,
        )

    def prepare_run(
        self,
        *,
        request_id: str,
        profile_path: str,
        controller_id: str,
        vehicle_count: int,
        parameter_set: dict[str, Any] | None = None,
        connection_preflight_id: str = "",
    ) -> dict[str, Any]:
        if self.active_run_id:
            active_manifest = self._get_manifest(self.active_run_id)
            if active_manifest is not None:
                self._refresh_runtime_state(active_manifest)
                if active_manifest.get("lifecycle_state") in {"starting", "running"}:
                    return self._response(
                        request_id,
                        False,
                        "active_run_must_stop_before_prepare",
                        run_id=self.active_run_id,
                        manifest=active_manifest,
                    )

        validation = self.validate_experiment_profile(
            request_id=request_id,
            profile_path=profile_path,
            controller_id=controller_id,
            vehicle_count=vehicle_count,
        )
        if not validation["accepted"]:
            return validation

        connection = None
        if validation.get("controller_backend") == "mworks_live":
            preflight_path = self.run_root / "_preflight" / f"{connection_preflight_id}.json"
            if not connection_preflight_id or not preflight_path.is_file():
                return self._response(request_id, False, "connection_preflight_required")
            connection = _read_json(preflight_path)
            if connection.get("accepted") is not True:
                return self._response(request_id, False, "connection_preflight_not_accepted")
            if (
                connection.get("profile_hash") != validation["profile_hash"]
                or connection.get("controller_id") != controller_id
                or connection.get("vehicle_count") != vehicle_count
                or connection.get("preflight_result_hash")
                != _canonical_hash({key: value for key, value in connection.items() if key != "preflight_result_hash"})
            ):
                return self._response(request_id, False, "connection_preflight_identity_mismatch")

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
            "selected_controller_profile_id": validation.get("selected_controller_profile_id", ""),
            "parameter_set": parameters,
            "parameter_set_hash": _canonical_hash(parameters),
            "vehicle_count": vehicle_count,
            "scenario_profile_id": validation.get("scenario_profile_id", ""),
            "scenario_path": validation.get("scenario_path", ""),
            "scenario_hash": validation.get("scenario_hash", ""),
            "scenario_snapshot": validation.get("scenario_snapshot", {}),
            "created_at": time.time(),
            "updated_at": time.time(),
            "display_sessions": [],
            "operations": [],
            "recording": {"active": False, "state": "idle", "output_path": ""},
            "injections": [],
            "events": [],
            "evidence_paths": {},
        }
        if connection is not None:
            endpoint = connection["endpoint"]
            manifest["mworks_live_connection"] = {
                "connection_contract_id": "mworks_live_connection_preflight_v1",
                "target_host": endpoint["target_host"],
                "resolved_target_addresses": connection.get("transport", {}).get("resolved_target_addresses", []),
                "rt1_udp_port": endpoint["rt1_udp_port"],
                "ros_master_uri": endpoint["ros_master_uri"],
                "local_advertised_ip": endpoint["local_advertised_ip"],
                "requested_rate_hz": endpoint["requested_rate_hz"],
                "selected_rate_hz": endpoint["requested_rate_hz"],
                "protocol_version": connection.get("transport", {}).get("rt1", {}).get("protocol_version", 1),
                "preflight_id": connection["preflight_id"],
                "preflight_result_hash": connection["preflight_result_hash"],
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

    def _refresh_runtime_state(self, manifest: dict[str, Any]) -> dict[str, Any] | None:
        poll = getattr(self.backend, "poll", None)
        if manifest["lifecycle_state"] not in {"starting", "running"} or not callable(poll):
            return None
        backend_state = poll(manifest)
        next_state = backend_state.get("lifecycle_state")
        if next_state in {"running", "completed", "blocked", "failed"}:
            state_changed = next_state != manifest["lifecycle_state"]
            manifest["lifecycle_state"] = next_state
            if next_state in {"completed", "blocked", "failed"}:
                manifest["runtime_started"] = False
            if state_changed:
                self._event(manifest, "runtime_state_changed", backend_result=backend_state)
            self._save(manifest)
        return backend_state

    def start_run(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        operation = self._create_operation(
            request_id=request_id,
            run_id=run_id,
            action="start_run",
            stage_id="runtime_spawn",
            stage_label="Starting runtime process",
            max_attempts=2,
            cancellable=True,
        )
        if manifest["lifecycle_state"] != "ready":
            self._finish_operation(operation, accepted=False, reason_code="run_not_ready", stage_id="failed", stage_label="Run not ready")
            return self._response(request_id, False, "run_not_ready", run_id=run_id, operation=operation)
        if self.backend is None:
            self._finish_operation(operation, accepted=False, reason_code="runtime_backend_unconfigured", stage_id="failed", stage_label="Runtime backend unavailable")
            return self._response(request_id, False, "runtime_backend_unconfigured", run_id=run_id, operation=operation)

        result = self.backend.start(manifest)
        if not result.get("accepted") and result.get("reason_code") == "runtime_process_spawn_failed":
            operation["attempt"] = 2
            operation["reason_code"] = "retrying_runtime_spawn"
            self._save_operation(operation)
            result = self.backend.start(manifest)
        if not result.get("accepted"):
            manifest["lifecycle_state"] = "blocked"
            self._event(manifest, "runtime_start_rejected", backend_result=result)
            self._save(manifest)
            reason = result.get("reason_code", "runtime_start_failed")
            self._finish_operation(operation, accepted=False, reason_code=reason, stage_id="failed", stage_label="Runtime start failed")
            return self._response(request_id, False, reason, run_id=run_id, operation=operation)
        lifecycle_state = result.get("lifecycle_state", "running")
        if lifecycle_state not in {"starting", "running"}:
            lifecycle_state = "starting"
        manifest["lifecycle_state"] = lifecycle_state
        manifest["runtime_started"] = True
        self._event(manifest, "runtime_started", backend_result=result)
        self._save(manifest)
        reason_code = "run_started" if lifecycle_state == "running" else "run_starting"
        if lifecycle_state == "running":
            self._finish_operation(operation, accepted=True, reason_code=reason_code, stage_id="ready", stage_label="Runtime ready")
        else:
            operation.update(
                {
                    "state": "running",
                    "stage_id": "runtime_readiness",
                    "stage_label": "Waiting for runtime readiness",
                    "reason_code": reason_code,
                }
            )
            self._save_operation(operation)
        return self._response(request_id, True, reason_code, run_id=run_id, backend_result=result, operation=operation)

    def _start_model_operation(self, *, request_id: str, run_id: str, action: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        operation = self._create_operation(
            request_id=request_id,
            run_id=run_id,
            action=action,
            stage_id="mworks_request",
            stage_label="Starting MWORKS MIL" if action == "run_mil" else "Starting MWORKS code generation",
            max_attempts=1,
            cancellable=False,
        )
        if operation.get("state") != "running" or operation.get("reason_code") != "operation_started":
            return self._response(
                request_id,
                operation.get("state") != "failed",
                "model_operation_reused",
                run_id=run_id,
                operation=operation,
            )
        if manifest.get("lifecycle_state") != "ready":
            self._finish_operation(
                operation,
                accepted=False,
                reason_code="model_operation_requires_ready_run",
                stage_id="manual_confirmation_required",
                stage_label="Stop or reset runtime before model operation",
            )
            return self._response(
                request_id, False, "model_operation_requires_ready_run", run_id=run_id, operation=operation
            )
        for candidate_id in manifest.get("operations", []):
            if candidate_id == operation["operation_id"]:
                continue
            candidate = self._load_operation(run_id, str(candidate_id))
            if candidate and candidate.get("state") == "running" and candidate.get("action") in {"run_mil", "generate_code"}:
                self._finish_operation(
                    operation,
                    accepted=False,
                    reason_code="model_operation_conflict",
                    stage_id="manual_confirmation_required",
                    stage_label="Another MWORKS operation is active",
                )
                return self._response(
                    request_id, False, "model_operation_conflict", run_id=run_id, operation=operation
                )
        start = getattr(self.backend, "start_model_operation", None)
        if not callable(start):
            self._finish_operation(
                operation,
                accepted=False,
                reason_code="model_operation_backend_unavailable",
                stage_id="manual_confirmation_required",
                stage_label="MWORKS operation backend unavailable",
            )
            return self._response(
                request_id, False, "model_operation_backend_unavailable", run_id=run_id, operation=operation
            )
        result = start(manifest, action=action, operation_id=operation["operation_id"])
        if not result.get("accepted"):
            reason = result.get("reason_code", "model_operation_start_failed")
            self._finish_operation(
                operation,
                accepted=False,
                reason_code=reason,
                stage_id="manual_confirmation_required",
                stage_label="MWORKS operation requires review",
            )
            self._event(manifest, "model_operation_rejected", action=action, backend_result=result)
            self._save(manifest)
            return self._response(request_id, False, reason, run_id=run_id, operation=operation)
        operation.update(
            {
                "stage_id": "mworks_running",
                "stage_label": "MWORKS MIL running" if action == "run_mil" else "MWORKS code generation running",
                "reason_code": result.get("reason_code", "model_operation_started"),
                "backend_result": result,
            }
        )
        self._save_operation(operation)
        self._event(manifest, "model_operation_started", action=action, operation_id=operation["operation_id"])
        self._save(manifest)
        return self._response(
            request_id, True, "model_operation_started", run_id=run_id, operation=operation
        )

    def run_mil(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        return self._start_model_operation(request_id=request_id, run_id=run_id, action="run_mil")

    def generate_code(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        return self._start_model_operation(request_id=request_id, run_id=run_id, action="generate_code")

    def stop_run(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        if manifest["lifecycle_state"] not in {"starting", "running"} or self.backend is None:
            return self._response(request_id, False, "run_not_active", run_id=run_id)
        stop_evidence = self._runtime_stop_evidence(manifest)
        if not stop_evidence["accepted"]:
            return self._response(
                request_id,
                False,
                stop_evidence["reason_code"],
                run_id=run_id,
                stop_evidence=stop_evidence,
            )
        result = self.backend.stop(manifest)
        if not result.get("accepted"):
            return self._response(request_id, False, result.get("reason_code", "runtime_stop_failed"), run_id=run_id)
        manifest["lifecycle_state"] = "completed"
        manifest["runtime_started"] = False
        self._event(manifest, "runtime_stopped", backend_result=result, stop_evidence=stop_evidence)
        self._save(manifest)
        return self._response(
            request_id,
            True,
            "run_stopped",
            run_id=run_id,
            stop_evidence=stop_evidence,
        )

    def _runtime_stop_evidence(self, manifest: dict[str, Any]) -> dict[str, Any]:
        """Require run-scoped landing evidence before terminating flight processes."""
        run_id = str(manifest["run_id"])
        safe_stop = manifest.get("safe_stop") or {}
        if safe_stop.get("stage") == "completed" and safe_stop.get("accepted") is True:
            ack_path = self.run_root / run_id / "safe_stop" / "ack.json"
            try:
                ack = _read_json(ack_path)
            except (OSError, ValueError, json.JSONDecodeError):
                ack = {}
            if (
                ack.get("schema") == "mosim.safe_stop.ack.v1"
                and ack.get("run_id") == run_id
                and ack.get("operation_id") == safe_stop.get("operation_id")
                and ack.get("stage") == "completed"
                and ack.get("terminal") is True
                and ack.get("accepted") is True
            ):
                return {
                    "accepted": True,
                    "reason_code": "safe_stop_disarm_confirmed",
                    "source": "mission_adapter_ack",
                    "operation_id": safe_stop.get("operation_id"),
                }

        telemetry_path = self.run_root / run_id / "telemetry.json"
        try:
            telemetry = _read_json(telemetry_path)
        except (OSError, ValueError, json.JSONDecodeError):
            return {
                "accepted": False,
                "reason_code": "runtime_stop_requires_fresh_disarm_evidence",
                "source": "runtime_sidecar",
            }
        timestamp = float(telemetry.get("timestamp", 0.0) or 0.0)
        if telemetry.get("run_id") != run_id or time.time() - timestamp > 2.5:
            return {
                "accepted": False,
                "reason_code": "runtime_stop_telemetry_stale",
                "source": "runtime_sidecar",
            }
        vehicles = telemetry.get("vehicles")
        expected = int(manifest.get("vehicle_count", 0) or 0)
        if not isinstance(vehicles, list) or len(vehicles) != expected:
            return {
                "accepted": False,
                "reason_code": "runtime_stop_vehicle_state_incomplete",
                "source": "runtime_sidecar",
                "expected_vehicle_count": expected,
            }
        states = [vehicle.get("state") or {} for vehicle in vehicles if isinstance(vehicle, dict)]
        if len(states) != expected or not all(state.get("connected") is True for state in states):
            return {
                "accepted": False,
                "reason_code": "runtime_stop_vehicle_state_incomplete",
                "source": "runtime_sidecar",
                "expected_vehicle_count": expected,
            }
        armed = [bool(state.get("armed")) for state in states]
        if any(armed):
            return {
                "accepted": False,
                "reason_code": "runtime_stop_rejected_vehicle_armed",
                "source": "runtime_sidecar",
                "armed_vehicle_count": sum(armed),
                "vehicle_count": expected,
            }
        return {
            "accepted": True,
            "reason_code": "runtime_sidecar_disarm_confirmed",
            "source": "runtime_sidecar",
            "vehicle_count": expected,
        }

    def request_safe_stop(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        if manifest.get("lifecycle_state") not in {"starting", "running"} or self.backend is None:
            return self._response(request_id, False, "run_not_active", run_id=run_id)

        supported_profiles = {
            "px4ctrl_figure8_baseline_v1",
            "cascade_pid_figure8_generated_c_v1",
            "factory_l2_fuel_fixed64_exploration_v1",
            "factory_l2_three_uav_swarm_formation_v1",
        }
        if manifest.get("experiment_profile_id") not in supported_profiles:
            return self._response(request_id, False, "safe_stop_adapter_not_supported", run_id=run_id)

        for operation_id in reversed(manifest.get("operations", [])):
            existing = self._load_operation(run_id, operation_id)
            if existing and existing.get("action") == "request_safe_stop" and existing.get("state") in {
                "running",
                "completed",
            }:
                return self._response(
                    request_id,
                    True,
                    "safe_stop_request_reused",
                    run_id=run_id,
                    operation=existing,
                )

        operation = self._create_operation(
            request_id=request_id,
            run_id=run_id,
            action="request_safe_stop",
            stage_id="requested",
            stage_label="Safe stop requested",
            cancellable=False,
            safe_stop_only=True,
        )
        operation["progress_mode"] = "determinate"
        operation["progress_percent"] = 5
        operation["reason_code"] = "safe_stop_requested"
        self._save_operation(operation)
        request = {
            "schema": "mosim.safe_stop.request.v1",
            "run_id": run_id,
            "request_id": request_id,
            "operation_id": operation["operation_id"],
            "requested_at": time.time(),
            "source": "flight_console",
        }
        _write_json(self.run_root / run_id / "safe_stop" / "request.json", request)
        manifest["safe_stop"] = {
            "operation_id": operation["operation_id"],
            "stage": "requested",
            "requested_at": request["requested_at"],
        }
        self._event(manifest, "safe_stop_requested", operation_id=operation["operation_id"])
        self._save(manifest)
        return self._response(
            request_id,
            True,
            "safe_stop_requested",
            run_id=run_id,
            operation=operation,
        )

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
        if manifest["lifecycle_state"] == "starting" and self.backend is not None:
            self._refresh_runtime_state(manifest)
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
        normalized_displays = sorted(set(displays))
        for existing in self._manifest_display_sessions(manifest):
            if (
                existing.get("state") in {"prepared", "attached"}
                and sorted(existing.get("displays", [])) == normalized_displays
            ):
                return self._response(
                    request_id,
                    True,
                    "display_session_reused",
                    run_id=run_id,
                    session=existing,
                )
            if existing.get("state") in {"prepared", "attached", "detach_failed"}:
                return self._response(
                    request_id,
                    False,
                    "display_session_conflict",
                    run_id=run_id,
                    session=existing,
                    requested_displays=normalized_displays,
                )
        session_id = f"display-{uuid.uuid4().hex[:10]}"
        session = {"session_id": session_id, "run_id": run_id, "displays": normalized_displays, "state": "prepared"}
        self.display_sessions[session_id] = session
        manifest["display_sessions"].append(session_id)
        self._save_display_session(session)
        self._event(manifest, "display_session_prepared", session=session)
        self._save(manifest)
        return self._response(request_id, True, "display_session_prepared", run_id=run_id, session=session)

    def _display_session_path(self, session: dict[str, Any]) -> Path:
        return self.run_root / session["run_id"] / "displays" / session["session_id"] / "DISPLAY_SESSION.json"

    def _save_display_session(self, session: dict[str, Any]) -> None:
        self.display_sessions[session["session_id"]] = session
        _write_json(self._display_session_path(session), session)

    def _refresh_display_session_from_status(self, session: dict[str, Any]) -> dict[str, Any]:
        status_path = self._display_session_path(session).with_name("DISPLAY_STATUS.json")
        if not status_path.is_file():
            return session
        try:
            status = _read_json(status_path)
        except (OSError, ValueError, json.JSONDecodeError):
            return session
        state = str(status.get("state", ""))
        if state in {"attached", "detached", "blocked"} and state != session.get("state"):
            session["state"] = state
            session["status"] = status
            self._save_display_session(session)
        return session

    def _get_display_session(self, session_id: str) -> dict[str, Any] | None:
        session = self.display_sessions.get(session_id)
        if session is not None:
            return session
        for path in self.run_root.glob(f"run-*/displays/{session_id}/DISPLAY_SESSION.json"):
            session = _read_json(path)
            if session.get("session_id") == session_id:
                self.display_sessions[session_id] = session
                return session
        return None

    def _manifest_display_sessions(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        indexed_ids = [str(value) for value in manifest.get("display_sessions", [])]
        sessions: list[dict[str, Any]] = []
        valid_ids: list[str] = []
        for session_id in indexed_ids:
            session = self._get_display_session(session_id)
            if session is None:
                continue
            session = self._refresh_display_session_from_status(session)
            sessions.append(session)
            valid_ids.append(session_id)
        if valid_ids != indexed_ids:
            manifest["display_sessions"] = valid_ids
            self._event(
                manifest,
                "display_session_index_reconciled",
                removed_session_ids=[value for value in indexed_ids if value not in valid_ids],
            )
            self._save(manifest)
        return sessions

    def attach_display(self, *, request_id: str, session_id: str) -> dict[str, Any]:
        session = self._get_display_session(session_id)
        if session is None:
            return self._response(request_id, False, "display_session_not_found")
        if session.get("state") == "attached":
            return self._response(
                request_id, True, "display_already_attached", run_id=session["run_id"], session=session
            )
        operation = self._create_operation(
            request_id=request_id,
            run_id=session["run_id"],
            action="attach_display",
            stage_id="display_spawn",
            stage_label="Starting display session",
            max_attempts=2,
            cancellable=True,
        )
        operation["session_id"] = session["session_id"]
        self._save_operation(operation)
        attach = getattr(self.backend, "attach_display", None)
        if callable(attach):
            result = attach(session)
            if not result.get("accepted") and result.get("reason_code") == "display_helper_spawn_failed":
                operation["attempt"] = 2
                operation["reason_code"] = "retrying_display_spawn"
                self._save_operation(operation)
                result = attach(session)
            if not result.get("accepted"):
                session["state"] = "blocked"
                session["backend_result"] = result
                self._save_display_session(session)
                reason = result.get("reason_code", "display_attach_failed")
                self._finish_operation(operation, accepted=False, reason_code=reason, stage_id="failed", stage_label="Display attach failed")
                return self._response(
                    request_id, False, reason,
                    run_id=session["run_id"], session=session, operation=operation,
                )
            session["backend_result"] = result
        session["state"] = "attached"
        self._save_display_session(session)
        manifest = self._get_manifest(session["run_id"])
        if manifest is not None:
            self._event(manifest, "display_session_attached", session=session)
            self._save(manifest)
        if session.get("backend_result", {}).get("status_path"):
            operation.update(
                {
                    "stage_id": "display_readiness",
                    "stage_label": "Waiting for display readiness",
                    "reason_code": "display_attach_requested",
                }
            )
            self._save_operation(operation)
        else:
            self._finish_operation(operation, accepted=True, reason_code="display_attached", stage_id="ready", stage_label="Displays ready")
        return self._response(
            request_id, True, "display_attached", run_id=session["run_id"], session=session, operation=operation
        )

    def get_operation_progress(
        self, *, request_id: str, run_id: str, operation_id: str
    ) -> dict[str, Any]:
        operation = self._load_operation(run_id, operation_id)
        if operation is None:
            return self._response(request_id, False, "operation_not_found", run_id=run_id)
        manifest = self._get_manifest(run_id)
        if operation["state"] == "running" and manifest is not None:
            if operation["action"] == "start_run":
                backend_state = self._refresh_runtime_state(manifest)
                state = manifest.get("lifecycle_state")
                if state == "running":
                    self._finish_operation(operation, accepted=True, reason_code="runtime_ready", stage_id="ready", stage_label="Runtime ready")
                elif state in {"blocked", "failed"}:
                    reason = (backend_state or {}).get("reason_code", f"runtime_{state}")
                    self._finish_operation(operation, accepted=False, reason_code=reason, stage_id="failed", stage_label="Runtime readiness failed")
                else:
                    operation["reason_code"] = (backend_state or {}).get("reason_code", "runtime_readiness_gate_pending")
                    self._save_operation(operation)
            elif operation["action"] == "attach_display":
                session_id = str(operation.get("session_id", ""))
                session = self.display_sessions.get(session_id)
                status_path = _resolve_project_path(str((session or {}).get("backend_result", {}).get("status_path", "")))
                if status_path is not None and status_path.is_file():
                    status = _read_json(status_path)
                    if status.get("state") == "attached":
                        self._finish_operation(operation, accepted=True, reason_code="display_ready", stage_id="ready", stage_label="Displays ready")
                    elif status.get("state") == "blocked":
                        self._finish_operation(operation, accepted=False, reason_code="display_readiness_failed", stage_id="failed", stage_label="Display readiness failed")
            elif operation["action"] in {"run_mil", "generate_code"}:
                poll = getattr(self.backend, "poll_model_operation", None)
                if callable(poll):
                    backend_state = poll(
                        manifest,
                        action=operation["action"],
                        operation_id=operation["operation_id"],
                    )
                    if backend_state.get("state") == "completed":
                        operation["result_gate"] = backend_state.get("result_gate", "")
                        self._finish_operation(
                            operation,
                            accepted=True,
                            reason_code=backend_state.get("reason_code", "model_operation_completed"),
                            stage_id="completed",
                            stage_label="MWORKS operation complete",
                        )
                        self._event(
                            manifest,
                            "model_operation_completed",
                            action=operation["action"],
                            operation_id=operation["operation_id"],
                            result_gate=operation.get("result_gate", ""),
                        )
                        self._save(manifest)
                        self._write_model_gate_packet(manifest)
                    elif backend_state.get("state") == "failed":
                        self._finish_operation(
                            operation,
                            accepted=False,
                            reason_code=backend_state.get("reason_code", "model_operation_failed"),
                            stage_id="manual_confirmation_required",
                            stage_label="MWORKS operation failed; review required",
                        )
                        self._event(
                            manifest,
                            "model_operation_failed",
                            action=operation["action"],
                            operation_id=operation["operation_id"],
                            backend_result=backend_state,
                        )
                        self._save(manifest)
                        self._write_model_gate_packet(manifest)
                    else:
                        operation["reason_code"] = backend_state.get("reason_code", "model_operation_running")
                        self._save_operation(operation)
            elif operation["action"] == "request_safe_stop":
                ack_path = self.run_root / run_id / "safe_stop" / "ack.json"
                if ack_path.is_file():
                    try:
                        ack = _read_json(ack_path)
                    except (OSError, ValueError, json.JSONDecodeError):
                        ack = {}
                    if (
                        ack.get("schema") == "mosim.safe_stop.ack.v1"
                        and ack.get("run_id") == run_id
                        and ack.get("operation_id") == operation_id
                        and ack.get("request_id") == operation.get("request_id")
                    ):
                        stage = str(ack.get("stage", "requested"))
                        labels = {
                            "requested": "Safe stop requested",
                            "quiescing": "Quiescing planner commands",
                            "hovering": "Holding position",
                            "landing": "Landing",
                            "disarmed": "Disarmed",
                            "completed": "Safe stop complete",
                            "failed": "Safe stop failed",
                        }
                        operation.update(
                            {
                                "stage_id": stage,
                                "stage_label": labels.get(stage, stage),
                                "progress_mode": "determinate",
                                "progress_percent": int(ack.get("progress_percent", 5)),
                                "reason_code": ack.get("reason_code", f"safe_stop_{stage}"),
                                "safe_stop_ack": ack,
                            }
                        )
                        if ack.get("terminal"):
                            accepted = bool(ack.get("accepted")) and stage == "completed"
                            self._finish_operation(
                                operation,
                                accepted=accepted,
                                reason_code=operation["reason_code"],
                                stage_id=stage,
                                stage_label=labels.get(stage, stage),
                            )
                            manifest["safe_stop"] = {
                                "operation_id": operation_id,
                                "stage": stage,
                                "completed_at": ack.get("updated_at"),
                                "accepted": accepted,
                            }
                            self._event(manifest, "safe_stop_completed" if accepted else "safe_stop_failed", ack=ack)
                            self._save(manifest)
                        else:
                            self._save_operation(operation)
        return self._response(
            request_id,
            True,
            "operation_progress_ready",
            run_id=run_id,
            operation=operation,
        )

    def _write_model_gate_packet(self, manifest: dict[str, Any]) -> Path:
        rows = []
        for operation_id in manifest.get("operations", []):
            operation = self._load_operation(manifest["run_id"], str(operation_id))
            if operation and operation.get("action") in {"run_mil", "generate_code"}:
                rows.append(operation)
        required = {"run_mil", "generate_code"}
        passed = {row["action"] for row in rows if row.get("state") == "completed"}
        failed = [row for row in rows if row.get("state") == "failed"]
        packet = {
            "schema": "mosim.model_studio.gate_packet.v1",
            "run_id": manifest["run_id"],
            "profile_hash": manifest["experiment_profile_hash"],
            "controller_id": manifest["controller_id"],
            "status": "passed" if required <= passed else "failed" if failed else "pending",
            "required_actions": sorted(required),
            "passed_actions": sorted(passed),
            "operations": rows,
            "updated_at": time.time(),
            "claim_boundary": "Model Studio MWORKS MIL and code-generation gates only; runtime and controller-performance acceptance are separate.",
        }
        path = self.run_root / manifest["run_id"] / "MODEL_GATE_PACKET.json"
        _write_json(path, packet)
        return path

    def get_model_gate_state(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        latest: dict[str, dict[str, Any]] = {}
        for operation_id in manifest.get("operations", []):
            operation = self._load_operation(run_id, str(operation_id))
            if operation is None or operation.get("action") not in {"run_mil", "generate_code"}:
                continue
            if operation.get("state") == "running":
                self.get_operation_progress(
                    request_id=f"{request_id}-poll-{operation['action']}",
                    run_id=run_id,
                    operation_id=operation["operation_id"],
                )
                operation = self._load_operation(run_id, operation["operation_id"]) or operation
            latest[operation["action"]] = operation
        packet_path = self._write_model_gate_packet(manifest)
        packet = _read_json(packet_path)
        return self._response(
            request_id,
            True,
            "model_gate_state_ready",
            run_id=run_id,
            gate_state=latest,
            packet=packet,
            packet_path=_portable_path(packet_path),
        )

    def close_all_rviz(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        operation = self._create_operation(
            request_id=request_id,
            run_id=run_id,
            action="close_all_rviz",
            stage_id="rviz_cleanup",
            stage_label="Closing MoSim RViz sessions",
            max_attempts=2,
        )
        close = getattr(self.backend, "close_all_rviz", None)
        if not callable(close):
            self._finish_operation(operation, accepted=False, reason_code="rviz_cleanup_backend_unavailable", stage_id="failed", stage_label="RViz cleanup unavailable")
            return self._response(request_id, False, "rviz_cleanup_backend_unavailable", run_id=run_id, operation=operation)
        result = close(manifest)
        if not result.get("accepted") and result.get("reason_code") == "rviz_cleanup_spawn_failed":
            operation["attempt"] = 2
            self._save_operation(operation)
            result = close(manifest)
        reason = result.get("reason_code", "rviz_cleanup_failed")
        self._finish_operation(operation, accepted=bool(result.get("accepted")), reason_code=reason, stage_id="completed" if result.get("accepted") else "failed", stage_label="RViz cleanup complete" if result.get("accepted") else "RViz cleanup failed")
        return self._response(request_id, bool(result.get("accepted")), reason, run_id=run_id, operation=operation, cleanup=result)

    def start_ue_recording(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        return self._set_ue_recording(request_id=request_id, run_id=run_id, start=True)

    def stop_ue_recording(self, *, request_id: str, run_id: str) -> dict[str, Any]:
        return self._set_ue_recording(request_id=request_id, run_id=run_id, start=False)

    def _set_ue_recording(self, *, request_id: str, run_id: str, start: bool) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        action = "start_ue_recording" if start else "stop_ue_recording"
        if manifest is None:
            return self._response(request_id, False, "run_not_found", run_id=run_id)
        operation = self._create_operation(
            request_id=request_id,
            run_id=run_id,
            action=action,
            stage_id="recording_start" if start else "recording_flush",
            stage_label="Starting UE recording" if start else "Flushing UE recording",
            max_attempts=2 if start else 1,
        )
        current = manifest.setdefault("recording", {"active": False, "state": "idle", "output_path": ""})
        if start and current.get("active"):
            self._finish_operation(operation, accepted=True, reason_code="ue_recording_already_active", stage_id="ready", stage_label="UE recording active")
            return self._response(request_id, True, "ue_recording_already_active", run_id=run_id, operation=operation, recording=current)
        if not start and not current.get("active"):
            self._finish_operation(operation, accepted=True, reason_code="ue_recording_already_stopped", stage_id="completed", stage_label="UE recording stopped")
            return self._response(request_id, True, "ue_recording_already_stopped", run_id=run_id, operation=operation, recording=current)
        method = getattr(self.backend, action, None)
        if not callable(method):
            reason = "ue_recording_backend_unavailable"
            self._finish_operation(operation, accepted=False, reason_code=reason, stage_id="failed", stage_label="UE recording unavailable")
            return self._response(request_id, False, reason, run_id=run_id, operation=operation)
        result = method(manifest)
        if start and not result.get("accepted") and result.get("reason_code") == "ue_recording_spawn_failed":
            operation["attempt"] = 2
            self._save_operation(operation)
            result = method(manifest)
        accepted = bool(result.get("accepted"))
        reason = result.get("reason_code", "ue_recording_failed")
        if accepted:
            current.update(
                {
                    "active": start,
                    "state": "recording" if start else "stopped",
                    "output_path": result.get("output_path", current.get("output_path", "")),
                    "updated_at": time.time(),
                }
            )
            self._event(manifest, "ue_recording_started" if start else "ue_recording_stopped", backend_result=result)
            self._save(manifest)
        self._finish_operation(operation, accepted=accepted, reason_code=reason, stage_id="ready" if start and accepted else "completed" if accepted else "failed", stage_label="UE recording active" if start and accepted else "UE recording stopped" if accepted else "UE recording failed")
        return self._response(request_id, accepted, reason, run_id=run_id, operation=operation, recording=current, backend_result=result)

    def detach_display(self, *, request_id: str, session_id: str) -> dict[str, Any]:
        session = self._get_display_session(session_id)
        if session is None:
            return self._response(request_id, False, "display_session_not_found")
        if session.get("state") == "detached":
            return self._response(
                request_id, True, "display_already_detached", run_id=session["run_id"], session=session
            )
        detach = getattr(self.backend, "detach_display", None)
        if callable(detach):
            result = detach(session)
            if not result.get("accepted") and result.get("reason_code") == "display_detach_failed":
                result = detach(session)
            if not result.get("accepted"):
                session["state"] = "detach_failed"
                session["backend_result"] = result
                self._save_display_session(session)
                return self._response(
                    request_id, False, result.get("reason_code", "display_detach_failed"),
                    run_id=session["run_id"], session=session,
                )
            session["backend_result"] = result
        session["state"] = "detached"
        self._save_display_session(session)
        manifest = self._get_manifest(session["run_id"])
        if manifest is not None:
            self._event(manifest, "display_session_detached", session=session)
            self._save(manifest)
        return self._response(request_id, True, "display_detached", run_id=session["run_id"], session=session)

    def capture_display_evidence(
        self, *, request_id: str, run_id: str, session_id: str, evidence_path: str
    ) -> dict[str, Any]:
        manifest = self._get_manifest(run_id)
        session = self._get_display_session(session_id)
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
        self._refresh_runtime_state(manifest)
        active_session = None
        for session in reversed(self._manifest_display_sessions(manifest)):
            if session.get("state") in {"prepared", "attached", "detach_failed"}:
                active_session = session
                break
        return self._response(
            request_id,
            True,
            "run_state_ready",
            run_id=run_id,
            manifest=manifest,
            session=active_session or {},
        )

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
            packet_path = self.run_root / run_id / "MODEL_GATE_PACKET.json"
        if not packet_path.is_file():
            return self._response(request_id, False, "result_packet_not_available", run_id=run_id)
        return self._response(
            request_id,
            True,
            "result_packet_ready",
            run_id=run_id,
            packet=_read_json(packet_path),
            packet_path=_portable_path(packet_path),
        )

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
