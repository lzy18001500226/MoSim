#!/usr/bin/env python3
"""Open a Model Studio model in the native MWORKS Sysplorer application.

The selected class is loaded with its project package dependencies and opened
in a dedicated Sysplorer session. Offline models are checked before success is
reported. Code-generation mode only opens the selected graphical model for the
user's native MWORKS action. This entry point never simulates the model,
generates code, opens a result, starts a flight task, or changes the solver
lifecycle.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
CURRENT_MODEL_ENTRY_MAP = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
LOG = ROOT / "Results" / "ui_platform" / "model_studio_open_model" / "latest.json"
THREE_MODEL_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Formation" / "FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo"
THREE_MODEL_NAME = "MoSimQuadrotorModel.Guidance.Formation.TriangleFigure8LinearMPC"
LIVE_MODEL_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
LIVE_MODEL_NAME = "MoSimQuadrotorModel.Deployment.RT1OfficialPidShadow50Hz"
PX4CTRL_CODEGEN_MODEL_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "Sysblocks" / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.mo"
PX4CTRL_CODEGEN_MODEL_NAME = "MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock"
MODEL_DECLARATION = re.compile(r"\bmodel\s+([A-Za-z_]\w*)")
MODEL_NAME = re.compile(r"[A-Za-z_]\w*")
DEFAULT_MWORKS_EXE = Path(r"D:\Program Files\MWORKS\Sysplorer 2026a\Bin64\mworks.exe")
DEFAULT_MWORKS_PYTHON = Path(r"D:\Program Files\MWORKS\Sysplorer 2026a\External\python64\python.exe")
WORKER = ROOT / "Scripts" / "ui" / "open_model_studio_model_worker.py"
WORKER_RESULT = LOG.with_name("latest.worker.json")
TASK_CONFIG_SCHEMA = "mosim.model_studio.task_config.v1"
SW_RESTORE = 9
BASE_MODEL_FILES = [
    ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo",
]
RUNNER_MODELS = {
    "ROTOR_COMMAND": (ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "RotorCommandRunner.mo", "MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner"),
    "ATTITUDE_THRUST": (ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "AttitudeThrustRunner.mo", "MoSimQuadrotorModel.Experiment.Runners.AttitudeThrustRunner"),
    "BODY_RATE_THRUST": (ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "BodyRateThrustRunner.mo", "MoSimQuadrotorModel.Experiment.Runners.BodyRateThrustRunner"),
    "WRENCH": (ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "WrenchRunner.mo", "MoSimQuadrotorModel.Experiment.Runners.WrenchRunner"),
}


def model_name_from_file(model_file: Path) -> str:
    declaration = MODEL_DECLARATION.search(model_file.read_text(encoding="utf-8-sig"))
    if declaration is None:
        raise ValueError("model_declaration_not_found")
    return declaration.group(1)


def resolve_offline_model(profile_id: str, vehicle_count: int, output_variant: str) -> tuple[Path, str]:
    if vehicle_count == 3:
        return THREE_MODEL_FILE, THREE_MODEL_NAME
    if not profile_id:
        boundary = output_variant.split("/", 1)[0].strip()
        runner = RUNNER_MODELS.get(boundary)
        if runner is None:
            raise ValueError("unsupported_output_variant")
        return runner
    catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    entries = list(catalog.get("certified_profiles", [])) + list(catalog.get("custom_profile_proofs", []))
    entry = next((item for item in entries if item.get("profile_id") == profile_id), None)
    if entry is None:
        raise ValueError("profile_not_found_or_not_openable")
    record = ROOT / str(entry["certification_record"])
    certification = json.loads(record.read_text(encoding="utf-8-sig"))
    model_file = ROOT / str(certification["artifacts"]["model_source"])
    return model_file, model_name_from_file(model_file)


def resolve_controller_model(controller_id: str) -> tuple[Path, str]:
    if controller_id == "px4ctrl":
        return PX4CTRL_CODEGEN_MODEL_FILE, PX4CTRL_CODEGEN_MODEL_NAME
    entry_map = json.loads(CURRENT_MODEL_ENTRY_MAP.read_text(encoding="utf-8-sig"))
    entry = next(
        (item for item in entry_map.get("schemes", []) if item.get("scheme_id") == controller_id),
        None,
    )
    if entry is None or entry.get("mapping_state") != "resolved_current_model":
        raise ValueError("controller_not_openable")
    model_file = ROOT / str(entry["current_model_file"])
    return model_file, str(entry["current_model_class"])


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_task_config(task_config_path: Path) -> tuple[Path, str, dict[str, object]]:
    resolved_config = task_config_path.resolve()
    if not resolved_config.is_file():
        raise FileNotFoundError(f"task_config_not_found: {resolved_config}")
    document = json.loads(resolved_config.read_text(encoding="utf-8-sig"))
    if not isinstance(document, dict) or document.get("schema") != TASK_CONFIG_SCHEMA:
        raise ValueError("invalid_task_config_schema")
    raw_harness = document.get("harness_file")
    model_name = document.get("model_name")
    if not isinstance(raw_harness, str) or not raw_harness:
        raise ValueError("task_config_harness_file_missing")
    if not isinstance(model_name, str) or not MODEL_NAME.fullmatch(model_name):
        raise ValueError("task_config_model_name_invalid")
    candidate = Path(raw_harness)
    harness_file = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    try:
        harness_file.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("task_config_harness_outside_project_root") from exc
    if not harness_file.is_file():
        raise FileNotFoundError(f"task_config_harness_not_found: {harness_file}")
    expected_hash = document.get("harness_sha256")
    if isinstance(expected_hash, str) and expected_hash and sha256_path(harness_file) != expected_hash:
        raise ValueError("task_config_harness_hash_mismatch")
    return harness_file, model_name, document


def resolve_mworks_executable() -> Path:
    configured = os.environ.get("MWORKS_SYSPLORE_EXE", "").strip()
    executable = Path(configured) if configured else DEFAULT_MWORKS_EXE
    if not executable.is_file():
        raise FileNotFoundError(f"mworks_executable_not_found: {executable}")
    return executable


def resolve_mworks_python() -> Path:
    configured = os.environ.get("MWORKS_SYSPLORE_PYTHON", "").strip()
    executable = Path(configured) if configured else DEFAULT_MWORKS_PYTHON
    if not executable.is_file():
        raise FileNotFoundError(f"mworks_python_not_found: {executable}")
    return executable


def model_load_files(mode: str, model_file: Path) -> list[Path]:
    if mode == "live":
        return [LIVE_MODEL_FILE]
    files = list(BASE_MODEL_FILES)
    packaged_roots = [path.parent.resolve() for path in BASE_MODEL_FILES]
    resolved = model_file.resolve()
    if not any(resolved.is_relative_to(root) for root in packaged_roots):
        files.append(model_file)
    return files


def visible_model_window(model_name: str, timeout_s: float = 15.0) -> tuple[int, str]:
    if os.name != "nt":
        return 0, "non_windows_model_opened"
    user32 = ctypes.windll.user32
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        windows: list[tuple[int, int, str]] = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def collect(hwnd: int, _lparam: int) -> bool:
            process_id = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    try:
                        is_mworks = psutil.Process(process_id.value).name().lower() == "mworks.exe"
                    except (psutil.Error, OSError):
                        is_mworks = False
                    if is_mworks and model_name in buffer.value and "Sysplorer" in buffer.value:
                        windows.append((hwnd, process_id.value, buffer.value))
            return True

        user32.EnumWindows(callback_type(collect), 0)
        if windows:
            hwnd, pid, title = windows[0]
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, SW_RESTORE)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            return pid, title
        time.sleep(0.2)
    return 0, ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("model", "live", "codegen"), required=True)
    parser.add_argument("--controller-id", default="")
    parser.add_argument("--profile-id", default="")
    parser.add_argument("--vehicle-count", type=int, default=1)
    parser.add_argument("--output-variant", default="ROTOR_COMMAND")
    parser.add_argument("--task-config", type=Path)
    args = parser.parse_args()
    if args.task_config is not None and args.mode != "model":
        parser.error("--task-config is only valid for model mode")
    task_config: dict[str, object] | None = None
    if args.mode == "live":
        model_file = LIVE_MODEL_FILE.with_name("RT1OfficialPidShadow50Hz.mo")
        model_name = LIVE_MODEL_NAME
    elif args.mode == "codegen":
        if not args.controller_id:
            parser.error("--controller-id is required for codegen mode")
        model_file, model_name = resolve_controller_model(args.controller_id)
    elif args.task_config is not None:
        model_file, model_name, task_config = resolve_task_config(args.task_config)
        configured_controller = task_config.get("controller_id")
        if args.controller_id and configured_controller != args.controller_id:
            raise ValueError("task_config_controller_mismatch")
    else:
        model_file, model_name = resolve_offline_model(
            args.profile_id, args.vehicle_count, args.output_variant
        )
    if not model_file.is_file():
        raise FileNotFoundError(f"model_file_not_found: {model_file}")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "mosim.model_studio.open_model_result.v1",
        "mode": args.mode,
        "controller_id": args.controller_id,
        "profile_id": args.profile_id,
        "model_file": model_file.relative_to(ROOT).as_posix(),
        "model_name": model_name,
        "opened": False,
        "created_at": time.time(),
    }
    if task_config is not None:
        result["task_config"] = str(args.task_config.resolve())
        result["task_id"] = task_config.get("task_id")
        result["configuration_kind"] = task_config.get("configuration_kind")
    try:
        executable = resolve_mworks_executable()
        python_executable = resolve_mworks_python()
        load_files = model_load_files(args.mode, model_file)
        missing = [path for path in load_files if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"model_dependency_not_found: {missing[0]}")
        if WORKER_RESULT.exists():
            WORKER_RESULT.unlink()
        command = [
            str(python_executable),
            str(WORKER),
            "--mworks-exe", str(executable),
            "--model-name", model_name,
            "--result-path", str(WORKER_RESULT),
        ]
        for path in load_files:
            command.extend(["--model-file", str(path)])
        if args.mode == "model":
            command.append("--check-model")
        worker_stdout = LOG.with_name("latest.worker.stdout.log")
        worker_stderr = LOG.with_name("latest.worker.stderr.log")
        with worker_stdout.open("w", encoding="utf-8", newline="\n") as stdout_handle, worker_stderr.open(
            "w", encoding="utf-8", newline="\n"
        ) as stderr_handle:
            worker = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
        deadline = time.monotonic() + 120.0
        worker_result: dict[str, object] = {}
        while time.monotonic() < deadline:
            if WORKER_RESULT.is_file():
                worker_result = json.loads(WORKER_RESULT.read_text(encoding="utf-8-sig"))
                break
            if worker.poll() is not None:
                break
            time.sleep(0.2)
        if not worker_result:
            if worker.poll() is None:
                worker.terminate()
            raise RuntimeError(f"mworks_model_worker_not_ready: return_code={worker.poll()}")
        result["mworks_executable"] = str(executable)
        result["mworks_python"] = str(python_executable)
        result["dependency_files"] = [path.relative_to(ROOT).as_posix() for path in load_files]
        result["worker_process_id"] = worker.pid
        result["worker_return_code"] = worker.poll()
        result["worker_result"] = worker_result
        pid, title = visible_model_window(model_name)
        result["process_id"] = pid
        result["window_title"] = title
        result["opened"] = "error" not in worker_result and bool(title)
        if not result["opened"]:
            error = worker_result.get("error", "model_window_not_found")
            if worker.poll() is None:
                worker.terminate()
            raise RuntimeError(f"mworks_model_open_failed: {error}")
    finally:
        LOG.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["opened"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
