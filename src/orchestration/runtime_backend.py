"""Allowlisted process backend for project-owned MoSim runtime wrappers."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

from .core import DEFAULT_RUN_ROOT, PROJECT_ROOT, _portable_path, _write_json
from .runtime_sidecar_contract import atomic_write_json, load_contract, validate_command


DEFAULT_BACKEND_CATALOG = PROJECT_ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
LAUNCHER = PROJECT_ROOT / "Scripts" / "ui" / "run_orchestrated_runtime.sh"
STOP_HELPER = PROJECT_ROOT / "Scripts" / "ui" / "stop_orchestrated_runtime.sh"
DISPLAY_HELPER = PROJECT_ROOT / "Scripts" / "ui" / "attach_orchestrated_displays.ps1"
DEFAULT_INJECTION_CONTRACT = PROJECT_ROOT / "Config" / "control_platform" / "factory_injection_contract.json"
RUN_ID_PATTERN = re.compile(r"^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


def _wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{tail}"


class CatalogRuntimeBackend:
    backend_id = "catalog_runtime_backend_v1"

    def __init__(
        self,
        *,
        catalog_path: Path = DEFAULT_BACKEND_CATALOG,
        process_factory: Callable[..., Any] = subprocess.Popen,
        command_runner: Callable[..., Any] = subprocess.run,
        run_root: Path = DEFAULT_RUN_ROOT,
        injection_contract_path: Path = DEFAULT_INJECTION_CONTRACT,
        injection_ack_timeout_s: float = 3.0,
    ) -> None:
        self.catalog_path = catalog_path
        self.process_factory = process_factory
        self.command_runner = command_runner
        self.run_root = run_root
        self.injection_contract_path = injection_contract_path
        self.injection_ack_timeout_s = injection_ack_timeout_s
        self.processes: dict[str, Any] = {}
        self.log_streams: dict[str, tuple[Any, Any]] = {}
        self.display_processes: dict[str, Any] = {}

    def _catalog(self) -> dict[str, Any]:
        return json.loads(self.catalog_path.read_text(encoding="utf-8"))

    def _entry(self, manifest: dict[str, Any]) -> dict[str, Any] | None:
        entries = self._catalog().get("runtime_profiles", [])
        return next(
            (
                entry
                for entry in entries
                if manifest.get("experiment_profile_id") in entry.get("experiment_profile_ids", [])
                and manifest.get("controller_id") in entry.get("controller_ids", [])
                and manifest.get("vehicle_count") in entry.get("vehicle_counts", [])
            ),
            None,
        )

    def _command(self, entry: dict[str, Any], run_id: str) -> list[str]:
        if not RUN_ID_PATTERN.fullmatch(run_id):
            raise ValueError("invalid_run_id")
        if entry.get("launcher") != "wsl_project_script":
            raise ValueError("unsupported_runtime_launcher")
        distribution = entry.get("wsl_distribution")
        operation_id = entry.get("operation_id")
        if not isinstance(distribution, str) or not isinstance(operation_id, str):
            raise ValueError("invalid_runtime_catalog_entry")
        return [
            "wsl.exe",
            "-d",
            distribution,
            "--",
            "bash",
            _wsl_path(LAUNCHER),
            operation_id,
            run_id,
        ]

    def start(self, manifest: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        if run_id in self.processes and self.processes[run_id].poll() is None:
            return {"accepted": False, "reason_code": "runtime_already_active"}
        entry = self._entry(manifest)
        if entry is None:
            return {"accepted": False, "reason_code": "runtime_profile_not_allowlisted"}
        try:
            command = self._command(entry, run_id)
        except ValueError as exc:
            return {"accepted": False, "reason_code": str(exc)}

        run_dir = self.run_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        stdout = (run_dir / "runtime.stdout.log").open("ab")
        stderr = (run_dir / "runtime.stderr.log").open("ab")
        try:
            process = self.process_factory(command, cwd=PROJECT_ROOT, stdout=stdout, stderr=stderr)
        except OSError as exc:
            stdout.close()
            stderr.close()
            return {"accepted": False, "reason_code": "runtime_process_spawn_failed", "detail": str(exc)}
        if process.poll() is not None:
            stdout.close()
            stderr.close()
            return {
                "accepted": False,
                "reason_code": "runtime_process_exited_during_start",
                "exit_code": process.returncode,
            }

        self.processes[run_id] = process
        self.log_streams[run_id] = (stdout, stderr)
        process_record = {
            "schema": "mosim.orchestrator.runtime_process.v1",
            "run_id": run_id,
            "backend_id": self.backend_id,
            "runtime_profile_id": entry["runtime_profile_id"],
            "operation_id": entry["operation_id"],
            "windows_process_id": process.pid,
            "started_at": time.time(),
            "command_shape": ["wsl.exe", "-d", entry["wsl_distribution"], "--", "bash", "<project-launcher>"],
        }
        _write_json(run_dir / "RUNTIME_PROCESS.json", process_record)
        return {
            "accepted": True,
            "reason_code": "runtime_process_started",
            "lifecycle_state": "starting",
            "runtime_profile_id": entry["runtime_profile_id"],
            "process_id": process.pid,
            "readiness": "process_started_runtime_gate_pending",
        }

    def poll(self, manifest: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        process = self.processes.get(run_id)
        if process is None:
            return {"lifecycle_state": "blocked", "reason_code": "runtime_process_not_owned"}
        exit_code = process.poll()
        if exit_code is None:
            status_path = self.run_root / run_id / "RUNTIME_STATUS.json"
            if status_path.is_file():
                try:
                    status = json.loads(status_path.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    return {
                        "lifecycle_state": "starting",
                        "reason_code": "runtime_status_invalid",
                        "detail": str(exc),
                        "process_id": process.pid,
                    }
                lifecycle_state = status.get("status")
                if lifecycle_state in {"running", "blocked", "failed"}:
                    return {
                        "lifecycle_state": lifecycle_state,
                        "reason_code": status.get("reason_code", "runtime_status_ready"),
                        "readiness": status,
                        "process_id": process.pid,
                    }
            return {
                "lifecycle_state": "starting",
                "reason_code": "runtime_readiness_gate_pending",
                "process_id": process.pid,
            }
        self._close_logs(run_id)
        runtime_manifest = self.run_root / run_id / "runtime" / "RUN_MANIFEST.json"
        result = {
            "schema": "mosim.orchestrator.runtime_result.v1",
            "run_id": run_id,
            "exit_code": exit_code,
            "runtime_manifest": runtime_manifest.relative_to(PROJECT_ROOT).as_posix(),
            "runtime_manifest_present": runtime_manifest.is_file(),
            "completed_at": time.time(),
        }
        result["status"] = "completed" if exit_code == 0 and runtime_manifest.is_file() else "failed"
        _write_json(self.run_root / run_id / "RESULT_PACKET.json", result)
        return {
            "lifecycle_state": result["status"],
            "reason_code": "runtime_gate_completed" if result["status"] == "completed" else "runtime_gate_failed",
            "exit_code": exit_code,
        }

    def stop(self, manifest: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        process = self.processes.get(run_id)
        if process is None:
            return {"accepted": False, "reason_code": "runtime_process_not_owned"}
        entry = self._entry(manifest)
        if entry is None:
            return {"accepted": False, "reason_code": "runtime_profile_not_allowlisted"}
        stop_command = [
            "wsl.exe",
            "-d",
            entry["wsl_distribution"],
            "--",
            "bash",
            _wsl_path(STOP_HELPER),
            run_id,
        ]
        stopped = self.command_runner(stop_command, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=75)
        if stopped.returncode != 0:
            return {
                "accepted": False,
                "reason_code": "runtime_stop_helper_failed",
                "detail": stopped.stderr[-2000:],
            }
        try:
            exit_code = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            return {"accepted": False, "reason_code": "runtime_process_exit_timeout"}
        self._close_logs(run_id)
        return {"accepted": True, "reason_code": "runtime_process_stopped", "exit_code": exit_code}

    def reset(self, manifest: dict[str, Any]) -> dict[str, Any]:
        process = self.processes.get(manifest["run_id"])
        if process is not None and process.poll() is None:
            return {"accepted": False, "reason_code": "runtime_still_active"}
        self._close_logs(manifest["run_id"])
        return {"accepted": True, "reason_code": "runtime_backend_reset"}

    def apply_injection(self, manifest: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        process = self.processes.get(run_id)
        if process is None or process.poll() is not None:
            return {"accepted": False, "reason_code": "runtime_process_not_active", "applied_value": None}
        try:
            normalized = validate_command(
                command,
                manifest=manifest,
                contract=load_contract(self.injection_contract_path),
            )
        except (OSError, ValueError) as exc:
            return {"accepted": False, "reason_code": str(exc), "applied_value": None}

        run_dir = self.run_root / run_id
        command_id = normalized["command_id"]
        command_path = run_dir / "injection_commands" / f"{command_id}.json"
        ack_path = run_dir / "injection_acks" / f"{command_id}.json"
        if command_path.exists() or ack_path.exists():
            return {"accepted": False, "reason_code": "injection_command_id_reused", "applied_value": None}
        atomic_write_json(command_path, normalized)
        deadline = time.monotonic() + self.injection_ack_timeout_s
        while time.monotonic() < deadline:
            if ack_path.is_file():
                try:
                    ack = json.loads(ack_path.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    return {
                        "accepted": False,
                        "reason_code": "injection_ack_invalid",
                        "detail": str(exc),
                        "applied_value": None,
                    }
                return {
                    "accepted": bool(ack.get("accepted")),
                    "reason_code": ack.get("reason_code", "injection_acknowledged"),
                    "applied_value": ack.get("applied_value"),
                    "command_id": command_id,
                    "ack": ack,
                }
            time.sleep(0.05)
        return {
            "accepted": False,
            "reason_code": "injection_ack_timeout",
            "applied_value": None,
            "command_id": command_id,
        }

    def attach_display(self, session: dict[str, Any]) -> dict[str, Any]:
        run_id = session["run_id"]
        session_id = session["session_id"]
        command = [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(DISPLAY_HELPER),
            "-RunId", run_id, "-SessionId", session_id,
        ]
        command.extend(["-DisplayCsv", ",".join(session.get("displays", []))])
        run_dir = self.run_root / run_id
        log_dir = run_dir / "displays" / session_id
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout = (log_dir / "display_helper.stdout.log").open("ab")
        stderr = (log_dir / "display_helper.stderr.log").open("ab")
        try:
            process = self.process_factory(command, cwd=PROJECT_ROOT, stdout=stdout, stderr=stderr)
        except OSError as exc:
            stdout.close()
            stderr.close()
            return {"accepted": False, "reason_code": "display_helper_spawn_failed", "detail": str(exc)}
        self.display_processes[session_id] = (process, stdout, stderr)
        return {
            "accepted": True,
            "reason_code": "display_attach_requested",
            "process_id": process.pid,
            "status_path": _portable_path(log_dir / "DISPLAY_STATUS.json"),
        }

    def detach_display(self, session: dict[str, Any]) -> dict[str, Any]:
        command = [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(DISPLAY_HELPER),
            "-RunId", session["run_id"], "-SessionId", session["session_id"], "-Detach",
        ]
        stopped = self.command_runner(command, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30)
        owned = self.display_processes.pop(session["session_id"], None)
        if owned:
            _, stdout, stderr = owned
            stdout.close()
            stderr.close()
        if stopped.returncode != 0:
            return {"accepted": False, "reason_code": "display_detach_failed", "detail": stopped.stderr[-2000:]}
        return {"accepted": True, "reason_code": "display_detached"}

    def _close_logs(self, run_id: str) -> None:
        streams = self.log_streams.pop(run_id, ())
        for stream in streams:
            stream.close()
