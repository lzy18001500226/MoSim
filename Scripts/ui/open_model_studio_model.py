#!/usr/bin/env python3
"""Open a Model Studio model in the native MWORKS Sysplorer application.

The selected class is loaded with its project package dependencies and opened
in a dedicated Sysplorer session. Offline models are checked before success is
reported. This entry point never simulates the model, opens a result, starts a
flight task, or changes the solver lifecycle.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import subprocess
import time
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
LOG = ROOT / "Results" / "ui_platform" / "model_studio_open_model" / "latest.json"
THREE_MODEL_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Formation" / "FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo"
THREE_MODEL_NAME = "MoSimQuadrotorModel.Guidance.Formation.TriangleFigure8LinearMPC"
LIVE_MODEL_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
LIVE_MODEL_NAME = "MoSimQuadrotorModel.Deployment.RT1OfficialPidShadow50Hz"
MODEL_DECLARATION = re.compile(r"\bmodel\s+([A-Za-z_]\w*)")
DEFAULT_MWORKS_EXE = Path(r"D:\Program Files\MWORKS\Sysplorer 2026a\Bin64\mworks.exe")
DEFAULT_MWORKS_PYTHON = Path(r"D:\Program Files\MWORKS\Sysplorer 2026a\External\python64\python.exe")
WORKER = ROOT / "Scripts" / "ui" / "open_model_studio_model_worker.py"
WORKER_RESULT = LOG.with_name("latest.worker.json")
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
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            return pid, title
        time.sleep(0.2)
    return 0, ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("model", "live"), required=True)
    parser.add_argument("--profile-id", default="")
    parser.add_argument("--vehicle-count", type=int, default=1)
    parser.add_argument("--output-variant", default="ROTOR_COMMAND")
    args = parser.parse_args()
    if args.mode == "live":
        model_file = LIVE_MODEL_FILE.with_name("RT1OfficialPidShadow50Hz.mo")
        model_name = LIVE_MODEL_NAME
    else:
        model_file, model_name = resolve_offline_model(args.profile_id, args.vehicle_count, args.output_variant)
    if not model_file.is_file():
        raise FileNotFoundError(f"model_file_not_found: {model_file}")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "mosim.model_studio.open_model_result.v1",
        "mode": args.mode,
        "profile_id": args.profile_id,
        "model_file": model_file.relative_to(ROOT).as_posix(),
        "model_name": model_name,
        "opened": False,
        "created_at": time.time(),
    }
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
