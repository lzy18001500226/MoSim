"""Validate the static source surface for the AWFF PID + linear ESO route."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/AWFF_PidLinearEsoControllerEquation_Sysblock.mo"
ADAPTER = ROOT / "Models/MoSimQuadrotorModel/Control/Adapters/PidAwffLinearEsoRotorAdapter.mo"
RUNNER = ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/PidAwffLinearEsoFormalRunner.mo"
CORE_ORDER = CORE.parent / "package.order"
ADAPTER_ORDER = ADAPTER.parent / "package.order"
RUNNER_ORDER = RUNNER.parent / "package.order"
BASELINE = ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/AWFF_FullControllerEquation_Sysblock.mo"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_order(order_path: Path, entry: str) -> int:
    return sum(line.strip() == entry for line in order_path.read_text(encoding="utf-8").splitlines())


def validate() -> dict[str, Any]:
    errors: list[str] = []
    files = (CORE, ADAPTER, RUNNER, CORE_ORDER, ADAPTER_ORDER, RUNNER_ORDER, BASELINE)
    for path in files:
        if not path.is_file():
            errors.append(f"missing file: {path.relative_to(ROOT)}")

    core_text = CORE.read_text(encoding="utf-8") if CORE.is_file() else ""
    adapter_text = ADAPTER.read_text(encoding="utf-8") if ADAPTER.is_file() else ""
    runner_text = RUNNER.read_text(encoding="utf-8") if RUNNER.is_file() else ""
    baseline_text = BASELINE.read_text(encoding="utf-8") if BASELINE.is_file() else ""

    required_core = (
        "within MoSimQuadrotorModel.Control.Implementations.Sysblocks;",
        "model AWFF_PidLinearEsoControllerEquation_Sysblock",
        "PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),",
        "Right(y,y1,y2,y3))",
        "parameter Real eso_bandwidth_xy",
        "parameter Real eso_bandwidth_z",
        "der(eso_x1)",
        "der(eso_x2)",
        "der(eso_x3)",
        "der(eso_y1)",
        "der(eso_y2)",
        "der(eso_y3)",
        "der(eso_z1)",
        "der(eso_z2)",
        "der(eso_z3)",
        "eso_x3 / eso_b0_xy",
        "eso_y3 / eso_b0_xy",
        "eso_z3 / eso_b0_z",
        "pitch_ref_raw = x_command_nominal - eso_x_comp",
        "roll_ref_raw = y_command_nominal - eso_y_comp",
        "thrust_ref_raw = z_command_nominal - eso_z_comp",
        "end AWFF_PidLinearEsoControllerEquation_Sysblock;",
    )
    for needle in required_core:
        if needle not in core_text:
            errors.append(f"core missing: {needle}")

    required_adapter = (
        "within MoSimQuadrotorModel.Control.Adapters;",
        "model PidAwffLinearEsoRotorAdapter",
        "extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;",
        "AWFF_PidLinearEsoControllerEquation_Sysblock core",
        "rotor_command = {hover_speed + command_scale * core.y,",
        "-hover_speed + command_scale * core.y1",
        "hover_speed + command_scale * core.y2",
        "-hover_speed + command_scale * core.y3",
        "end PidAwffLinearEsoRotorAdapter;",
    )
    for needle in required_adapter:
        if needle not in adapter_text:
            errors.append(f"adapter missing: {needle}")

    required_runner = (
        "within MoSimQuadrotorModel.Experiment.Runners.Formal;",
        "model PidAwffLinearEsoFormalRunner",
        "FormalRotorCommandRunnerBase",
        "MoSimQuadrotorModel.Control.Adapters.PidAwffLinearEsoRotorAdapter",
        "end PidAwffLinearEsoFormalRunner;",
    )
    for needle in required_runner:
        if needle not in runner_text:
            errors.append(f"runner missing: {needle}")

    if CORE_ORDER.is_file() and count_order(CORE_ORDER, CORE.stem) != 1:
        errors.append("core package.order must contain exactly one formal core entry")
    if ADAPTER_ORDER.is_file() and count_order(ADAPTER_ORDER, ADAPTER.stem) != 1:
        errors.append("adapter package.order must contain exactly one adapter entry")
    if RUNNER_ORDER.is_file() and count_order(RUNNER_ORDER, RUNNER.stem) != 1:
        errors.append("runner package.order must contain exactly one formal runner entry")

    if BASELINE.is_file() and "model AWFF_FullControllerEquation_Sysblock" not in baseline_text:
        errors.append("AWFF baseline source no longer has its expected class declaration")

    relative_files = [path.relative_to(ROOT).as_posix() for path in files if path.is_file()]
    return {
        "schema": "mosim.pid_awff_linear_eso_static_surface.v1",
        "status": "passed" if not errors else "failed",
        "source": "offline_script",
        "controller": "pid_awff_linear_eso",
        "claim_boundary": "static source surface only; no MWORKS CheckModel or simulation claim",
        "files": {path: sha256(ROOT / path) for path in relative_files},
        "checks": {
            "formal_core_surface": not any(error.startswith("core ") for error in errors),
            "adapter_surface": not any(error.startswith("adapter ") for error in errors),
            "runner_surface": not any(error.startswith("runner ") for error in errors),
            "package_order_entries": not any("package.order" in error for error in errors),
            "baseline_class_preserved": not any("baseline source" in error for error in errors),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate()
    rendered = json.dumps(result, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
