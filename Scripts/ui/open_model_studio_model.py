#!/usr/bin/env python3
"""Open a Model Studio model in the native MWORKS Sysplorer application.

This entry point only launches a selected model file. It never checks or
simulates the model, opens a result, starts a flight task, or changes the solver
lifecycle.
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

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
LOG = ROOT / "Results" / "ui_platform" / "model_studio_open_model" / "latest.json"
THREE_MODEL_FILE = ROOT / "Models" / "QuadrotorExperiments" / "FormationScenarios" / "FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo"
THREE_MODEL_NAME = "QuadrotorExperiments.FormationScenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop"
LIVE_MODEL_FILE = ROOT / "Models" / "MworksLive" / "package.mo"
LIVE_MODEL_NAME = "MworksLive.RT1OfficialPidShadow50Hz"
MODEL_DECLARATION = re.compile(r"\bmodel\s+([A-Za-z_]\w*)")
DEFAULT_MWORKS_EXE = Path(r"D:\Program Files\MWORKS\Sysplorer 2026a\Bin64\mworks.exe")
RUNNER_MODELS = {
    "ROTOR_COMMAND": ROOT / "Models" / "MoSimQuadrotorModel" / "ExperimentRunner" / "Runners" / "RotorCommandRunner.mo",
    "ATTITUDE_THRUST": ROOT / "Models" / "MoSimQuadrotorModel" / "ExperimentRunner" / "Runners" / "AttitudeThrustRunner.mo",
    "BODY_RATE_THRUST": ROOT / "Models" / "MoSimQuadrotorModel" / "ExperimentRunner" / "Runners" / "BodyRateThrustRunner.mo",
    "WRENCH": ROOT / "Models" / "MoSimQuadrotorModel" / "ExperimentRunner" / "Runners" / "WrenchRunner.mo",
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
        model_file = RUNNER_MODELS.get(boundary)
        if model_file is None:
            raise ValueError("unsupported_output_variant")
        return model_file, model_name_from_file(model_file)
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


def visible_window_title(pid: int, timeout_s: float = 10.0) -> str:
    if os.name != "nt":
        return "non_windows_process_started"
    user32 = ctypes.windll.user32
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        titles: list[str] = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def collect(hwnd: int, _lparam: int) -> bool:
            process_id = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            if process_id.value == pid and user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    titles.append(buffer.value)
            return True

        user32.EnumWindows(callback_type(collect), 0)
        if titles:
            return titles[0]
        time.sleep(0.2)
    return ""


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
        process = subprocess.Popen([str(executable), str(model_file)], cwd=ROOT)
        result["mworks_executable"] = str(executable)
        result["process_id"] = process.pid
        result["window_title"] = visible_window_title(process.pid)
        result["opened"] = bool(result["window_title"])
        if not result["opened"]:
            return_code = process.poll()
            raise RuntimeError(f"mworks_visible_window_not_found: return_code={return_code}")
    finally:
        LOG.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["opened"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
