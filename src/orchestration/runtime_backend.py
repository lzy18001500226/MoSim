"""Allowlisted process backend for project-owned MoSim runtime wrappers."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

from .core import DEFAULT_RUN_ROOT, PROJECT_ROOT, _write_json


DEFAULT_BACKEND_CATALOG = PROJECT_ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
LAUNCHER = PROJECT_ROOT / "Scripts" / "ui" / "run_orchestrated_runtime.sh"
STOP_HELPER = PROJECT_ROOT / "Scripts" / "ui" / "stop_orchestrated_runtime.sh"
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
    ) -> None:
        self.catalog_path = catalog_path
        self.process_factory = process_factory
        self.command_runner = command_runner
        self.processes: dict[str, Any] = {}
        self.log_streams: dict[str, tuple[Any, Any]] = {}

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

        run_dir = DEFAULT_RUN_ROOT / run_id
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
            return {
                "lifecycle_state": "starting",
                "reason_code": "runtime_readiness_gate_pending",
                "process_id": process.pid,
            }
        self._close_logs(run_id)
        runtime_manifest = DEFAULT_RUN_ROOT / run_id / "runtime" / "RUN_MANIFEST.json"
        result = {
            "schema": "mosim.orchestrator.runtime_result.v1",
            "run_id": run_id,
            "exit_code": exit_code,
            "runtime_manifest": runtime_manifest.relative_to(PROJECT_ROOT).as_posix(),
            "runtime_manifest_present": runtime_manifest.is_file(),
            "completed_at": time.time(),
        }
        result["status"] = "completed" if exit_code == 0 and runtime_manifest.is_file() else "failed"
        _write_json(DEFAULT_RUN_ROOT / run_id / "RESULT_PACKET.json", result)
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
        return {"accepted": False, "reason_code": "runtime_injection_adapter_pending", "applied_value": None}

    def _close_logs(self, run_id: str) -> None:
        streams = self.log_streams.pop(run_id, ())
        for stream in streams:
            stream.close()
