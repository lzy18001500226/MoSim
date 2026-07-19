"""Allowlisted process backend for project-owned MoSim runtime wrappers."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from .core import DEFAULT_RUN_ROOT, PROJECT_ROOT, _portable_path, _write_json
from .runtime_sidecar_contract import atomic_write_json, load_contract, validate_command


DEFAULT_BACKEND_CATALOG = PROJECT_ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
DEFAULT_MODEL_OPERATION_CATALOG = PROJECT_ROOT / "Config" / "control_platform" / "model_operation_catalog.json"
MODEL_OPERATION_WORKER = PROJECT_ROOT / "Scripts" / "ui" / "run_model_studio_operation.py"
LAUNCHER = PROJECT_ROOT / "Scripts" / "ui" / "run_orchestrated_runtime.sh"
STOP_HELPER = PROJECT_ROOT / "Scripts" / "ui" / "stop_orchestrated_runtime.sh"
DISPLAY_HELPER = PROJECT_ROOT / "Scripts" / "ui" / "attach_orchestrated_displays.ps1"
GSTREAMER_BIN = (
    PROJECT_ROOT
    / ".tools"
    / "flight-console"
    / "gstreamer"
    / "gstreamer"
    / "1.0"
    / "msvc_x86_64"
    / "bin"
)
GSTREAMER_LAUNCH = GSTREAMER_BIN / "gst-launch-1.0.exe"
DEFAULT_INJECTION_CONTRACT = PROJECT_ROOT / "Config" / "control_platform" / "factory_injection_contract.json"
RUN_ID_PATTERN = re.compile(r"^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


def _wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{tail}"


def _read_runtime_json(path: Path, *, attempts: int = 10, delay_s: float = 0.05) -> Any:
    """Read a WSL-updated JSON file through brief Windows sharing conflicts."""
    last_error: OSError | ValueError | None = None
    for attempt in range(attempts):
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(delay_s)
    assert last_error is not None
    raise last_error


def _find_visible_window_handle(process_id: int) -> int | None:
    if os.name != "nt" or process_id <= 0:
        return None
    import ctypes
    from ctypes import wintypes

    handles: list[int] = []
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    @enum_proc
    def collect(hwnd, _lparam):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == process_id and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            handles.append(int(hwnd))
        return True

    user32.EnumWindows(collect, 0)
    return handles[0] if handles else None


class CatalogRuntimeBackend:
    backend_id = "catalog_runtime_backend_v1"

    def __init__(
        self,
        *,
        catalog_path: Path = DEFAULT_BACKEND_CATALOG,
        model_operation_catalog_path: Path = DEFAULT_MODEL_OPERATION_CATALOG,
        process_factory: Callable[..., Any] = subprocess.Popen,
        command_runner: Callable[..., Any] = subprocess.run,
        run_root: Path = DEFAULT_RUN_ROOT,
        injection_contract_path: Path = DEFAULT_INJECTION_CONTRACT,
        injection_ack_timeout_s: float = 3.0,
        gstreamer_launch: Path = GSTREAMER_LAUNCH,
        window_handle_resolver: Callable[[int], int | None] | None = None,
    ) -> None:
        self.catalog_path = catalog_path
        self.model_operation_catalog_path = model_operation_catalog_path
        self.process_factory = process_factory
        self.command_runner = command_runner
        self.run_root = run_root
        self.injection_contract_path = injection_contract_path
        self.injection_ack_timeout_s = injection_ack_timeout_s
        self.gstreamer_launch = gstreamer_launch
        self.window_handle_resolver = window_handle_resolver or _find_visible_window_handle
        self.processes: dict[str, Any] = {}
        self.log_streams: dict[str, tuple[Any, Any]] = {}
        self.display_processes: dict[str, Any] = {}
        self.recording_processes: dict[str, Any] = {}
        self.recording_streams: dict[str, tuple[Any, Any]] = {}
        self.recording_paths: dict[str, Path] = {}
        self.model_operation_processes: dict[str, Any] = {}
        self.model_operation_streams: dict[str, tuple[Any, Any]] = {}

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

    def _model_operation_entry(self, manifest: dict[str, Any], action: str) -> dict[str, Any] | None:
        catalog = json.loads(self.model_operation_catalog_path.read_text(encoding="utf-8"))
        return next(
            (
                entry
                for entry in catalog.get("model_profiles", [])
                if manifest.get("experiment_profile_id") in entry.get("experiment_profile_ids", [])
                and manifest.get("controller_id") in entry.get("controller_ids", [])
                and manifest.get("vehicle_count") in entry.get("vehicle_counts", [])
                and entry.get("status") == "enabled"
                and isinstance(entry.get(action), dict)
            ),
            None,
        )

    def start_model_operation(
        self, manifest: dict[str, Any], *, action: str, operation_id: str
    ) -> dict[str, Any]:
        if action not in {"run_mil", "generate_code"}:
            return {"accepted": False, "reason_code": "unsupported_model_operation"}
        entry = self._model_operation_entry(manifest, action)
        if entry is None:
            return {"accepted": False, "reason_code": "model_operation_not_allowlisted"}
        active = self.model_operation_processes.get(operation_id)
        if active is not None and active.poll() is None:
            return {"accepted": True, "reason_code": "model_operation_already_running", "process_id": active.pid}
        command = [
            sys.executable,
            str(MODEL_OPERATION_WORKER),
            "--action", action,
            "--run-id", manifest["run_id"],
            "--operation-id", operation_id,
        ]
        operation_dir = self.run_root / manifest["run_id"] / "mworks" / action
        operation_dir.mkdir(parents=True, exist_ok=True)
        stdout = (operation_dir / "launcher.stdout.log").open("ab")
        stderr = (operation_dir / "launcher.stderr.log").open("ab")
        try:
            process = self.process_factory(command, cwd=PROJECT_ROOT, stdout=stdout, stderr=stderr)
        except OSError as exc:
            stdout.close()
            stderr.close()
            return {"accepted": False, "reason_code": "model_operation_spawn_failed", "detail": str(exc)}
        if process.poll() is not None:
            stdout.close()
            stderr.close()
            return {
                "accepted": False,
                "reason_code": "model_operation_exited_during_start",
                "exit_code": process.returncode,
            }
        self.model_operation_processes[operation_id] = process
        self.model_operation_streams[operation_id] = (stdout, stderr)
        process_record = {
            "schema": "mosim.model_studio.operation_process.v1",
            "run_id": manifest["run_id"],
            "operation_id": operation_id,
            "action": action,
            "model_profile_id": entry["model_profile_id"],
            "windows_process_id": process.pid,
            "started_at": time.time(),
            "command_shape": ["python", "<project-model-operation-worker>", "--action", action],
        }
        _write_json(operation_dir / "MODEL_OPERATION_PROCESS.json", process_record)
        return {
            "accepted": True,
            "reason_code": "model_operation_started",
            "process_id": process.pid,
            "model_profile_id": entry["model_profile_id"],
        }

    def poll_model_operation(
        self, manifest: dict[str, Any], *, action: str, operation_id: str
    ) -> dict[str, Any]:
        entry = self._model_operation_entry(manifest, action)
        if entry is None:
            return {"state": "failed", "reason_code": "model_operation_not_allowlisted"}
        status_path = self.run_root / manifest["run_id"] / "mworks" / action / "OPERATION_STATUS.json"
        if status_path.is_file():
            try:
                status = _read_runtime_json(status_path)
            except (OSError, ValueError) as exc:
                return {"state": "running", "reason_code": "model_operation_status_invalid", "detail": str(exc)}
            if status.get("operation_id") != operation_id:
                return {"state": "failed", "reason_code": "model_operation_status_mismatch"}
            if status.get("status") in {"completed", "failed"}:
                self._close_model_operation_logs(operation_id)
                return {
                    "state": status["status"],
                    "reason_code": status.get("reason_code", "model_operation_finished"),
                    "status": status,
                    "result_gate": status.get("result_gate", ""),
                }
            return {"state": "running", "reason_code": status.get("reason_code", "model_operation_running")}
        process = self.model_operation_processes.get(operation_id)
        if process is None:
            return {"state": "running", "reason_code": "model_operation_status_pending"}
        exit_code = process.poll()
        if exit_code is None:
            return {"state": "running", "reason_code": "model_operation_status_pending", "process_id": process.pid}
        self._close_model_operation_logs(operation_id)
        return {
            "state": "failed",
            "reason_code": "model_operation_exited_without_status",
            "exit_code": exit_code,
        }

    def _close_model_operation_logs(self, operation_id: str) -> None:
        streams = self.model_operation_streams.pop(operation_id, None)
        if streams:
            streams[0].close()
            streams[1].close()

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
                    status = _read_runtime_json(status_path)
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
                    ack = _read_runtime_json(ack_path)
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
        status_path = (
            self.run_root
            / session["run_id"]
            / "displays"
            / session["session_id"]
            / "DISPLAY_STATUS.json"
        )
        if stopped.returncode != 0 and status_path.is_file():
            try:
                status = _read_runtime_json(status_path)
            except (OSError, ValueError):
                status = {}
            if status.get("state") == "detached":
                return {
                    "accepted": True,
                    "reason_code": "display_already_detached",
                    "status_path": _portable_path(status_path),
                }
        if stopped.returncode != 0:
            return {"accepted": False, "reason_code": "display_detach_failed", "detail": stopped.stderr[-2000:]}
        return {
            "accepted": True,
            "reason_code": "display_detached",
            "status_path": _portable_path(status_path),
        }

    def _display_records(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        run_id = manifest["run_id"]
        for session_id in manifest.get("display_sessions", []):
            process_file = self.run_root / run_id / "displays" / session_id / "DISPLAY_PROCESSES.json"
            if not process_file.is_file():
                continue
            try:
                value = _read_runtime_json(process_file)
            except (OSError, ValueError):
                continue
            for record in value if isinstance(value, list) else [value]:
                if isinstance(record, dict):
                    records.append({**record, "session_id": session_id})
        return records

    def close_all_rviz(self, manifest: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        sessions = sorted(
            {
                str(record["session_id"])
                for record in self._display_records(manifest)
                if record.get("kind") in {"rviz_pointcloud", "rviz_gridmap"}
            }
        )
        results: list[dict[str, Any]] = []
        for session_id in sessions:
            command = [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(DISPLAY_HELPER),
                "-RunId",
                run_id,
                "-SessionId",
                session_id,
                "-CloseRvizOnly",
            ]
            try:
                completed = self.command_runner(
                    command, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                return {
                    "accepted": False,
                    "reason_code": "rviz_cleanup_spawn_failed",
                    "detail": str(exc),
                    "sessions": results,
                }
            results.append(
                {
                    "session_id": session_id,
                    "exit_code": completed.returncode,
                    "status_path": _portable_path(
                        self.run_root
                        / run_id
                        / "displays"
                        / session_id
                        / "RVIZ_CLEANUP_STATUS.json"
                    ),
                }
            )
        failed = [result for result in results if result["exit_code"] != 0]
        return {
            "accepted": not failed,
            "reason_code": "rviz_sessions_closed" if not failed else "rviz_cleanup_failed",
            "session_count": len(sessions),
            "sessions": results,
        }

    def start_ue_recording(self, manifest: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        active = self.recording_processes.get(run_id)
        if active is not None and active.poll() is None:
            return {
                "accepted": True,
                "reason_code": "ue_recording_already_active",
                "output_path": _portable_path(self.recording_paths[run_id]),
            }
        if not self.gstreamer_launch.is_file():
            return {"accepted": False, "reason_code": "gstreamer_runtime_missing"}
        unreal_records = [record for record in self._display_records(manifest) if record.get("kind") == "unreal"]
        if not unreal_records:
            return {"accepted": False, "reason_code": "owned_unreal_window_missing"}
        unreal_pid = int(unreal_records[-1].get("pid", 0))
        window_handle = self.window_handle_resolver(unreal_pid)
        if window_handle is None:
            return {"accepted": False, "reason_code": "owned_unreal_window_missing", "process_id": unreal_pid}

        recording_dir = self.run_root / run_id / "recordings"
        recording_dir.mkdir(parents=True, exist_ok=True)
        output_path = recording_dir / f"ue-{time.strftime('%Y%m%d-%H%M%S')}.mp4"
        stdout = (recording_dir / "ue_recording.stdout.log").open("ab")
        stderr = (recording_dir / "ue_recording.stderr.log").open("ab")
        command = [
            str(self.gstreamer_launch),
            "-e",
            "d3d11screencapturesrc",
            "capture-api=wgc",
            f"window-handle={window_handle}",
            "show-cursor=false",
            "!",
            "d3d11convert",
            "!",
            "video/x-raw,format=NV12,framerate=30/1",
            "!",
            "mfh264enc",
            "bitrate=8000",
            "!",
            "h264parse",
            "!",
            "mp4mux",
            "!",
            "filesink",
            f"location={output_path}",
        ]
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        try:
            process = self.process_factory(
                command,
                cwd=PROJECT_ROOT,
                stdout=stdout,
                stderr=stderr,
                creationflags=creationflags,
            )
        except OSError as exc:
            stdout.close()
            stderr.close()
            return {"accepted": False, "reason_code": "ue_recording_spawn_failed", "detail": str(exc)}
        if process.poll() is not None:
            stdout.close()
            stderr.close()
            return {
                "accepted": False,
                "reason_code": "ue_recording_process_exited_during_start",
                "exit_code": process.returncode,
            }
        self.recording_processes[run_id] = process
        self.recording_streams[run_id] = (stdout, stderr)
        self.recording_paths[run_id] = output_path
        return {
            "accepted": True,
            "reason_code": "ue_recording_started",
            "output_path": _portable_path(output_path),
            "process_id": process.pid,
            "window_handle": window_handle,
        }

    def stop_ue_recording(self, manifest: dict[str, Any]) -> dict[str, Any]:
        run_id = manifest["run_id"]
        process = self.recording_processes.get(run_id)
        output_path = self.recording_paths.get(run_id)
        if process is None or process.poll() is not None:
            return {"accepted": False, "reason_code": "ue_recording_process_not_owned"}
        try:
            if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                process.terminate()
            process.wait(timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        for stream in self.recording_streams.pop(run_id, ()):
            stream.close()
        self.recording_processes.pop(run_id, None)
        self.recording_paths.pop(run_id, None)
        if output_path is None or not output_path.is_file() or output_path.stat().st_size == 0:
            return {"accepted": False, "reason_code": "ue_recording_output_missing"}
        return {
            "accepted": True,
            "reason_code": "ue_recording_stopped",
            "output_path": _portable_path(output_path),
            "size_bytes": output_path.stat().st_size,
        }

    def _close_logs(self, run_id: str) -> None:
        streams = self.log_streams.pop(run_id, ())
        for stream in streams:
            stream.close()
