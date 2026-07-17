#!/usr/bin/env python3
"""Collect live Sysplorer MIL evidence for the five classic controllers.

Run inside Sysplorer with ``call_code(mode="run_script")``.  Every accepted
sample comes from the active MWORKS result API; the script deliberately fails
if a model does not actually simulate.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/classic_controller_closeout_20260717/mworks"
MODEL_DIR = RESULT_DIR / "models"
RAW_DIR = RESULT_DIR / "raw"
METRICS_DIR = RESULT_DIR / "metrics"
BRIDGE_NAME = "MoSim_Classic_CFunction_Sysblock"


def load_builder():
    path = ROOT / "Scripts/control_platform/build_classic_controller_mworks_models.py"
    spec = importlib.util.spec_from_file_location("classic_mworks_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def changes(values: list[float], tolerance: float = 1.0e-12) -> bool:
    return any(abs(value - values[0]) > tolerance for value in values[1:])


def behavior_checks(controller: str, columns: dict[str, list[float]]) -> dict[str, bool]:
    common = {
        "status_code_zero": all(value == 0.0 for value in columns["status_code"]),
        "finite_thrust": all(math.isfinite(value) for value in columns["normalized_thrust"]),
    }
    specific = {
        "pole_placement_luenberger": {
            "observer_position_x_evolves": changes(columns["observer_position_x"]),
            "observer_velocity_x_evolves": changes(columns["observer_velocity_x"]),
        },
        "mrac": {
            "reference_model_position_x_evolves": changes(columns["reference_model_position_x"]),
            "adaptive_position_delta_x_evolves": changes(columns["adaptive_position_delta_x"]),
        },
        "ndi": {
            "desired_acceleration_x_nonzero": any(abs(value) > 1.0e-12 for value in columns["desired_acceleration_x"]),
        },
        "fopid": {
            "fractional_integral_x_evolves": changes(columns["fractional_integral_x"]),
            "fractional_derivative_x_evolves": changes(columns["fractional_derivative_x"]),
        },
        "h2_state_feedback": {
            "desired_acceleration_x_nonzero": any(abs(value) > 1.0e-12 for value in columns["desired_acceleration_x"]),
        },
    }
    return {**common, **specific[controller]}


def main() -> dict:
    builder = load_builder()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    bridge_path = MODEL_DIR / f"{BRIDGE_NAME}.mo"
    if not ModelingPy.ClassExist(BRIDGE_NAME):
        if not ModelingPy.OpenModelFile(str(bridge_path)):
            raise RuntimeError(f"OpenModelFile failed for {bridge_path}")

    fixtures: dict[str, dict] = {}
    overall_ok = True
    for controller_id, controller in builder.CONTROLLERS.items():
        model_name = f"MoSim_Classic_{controller.upper()}_MIL"
        model_path = MODEL_DIR / f"{model_name}.mo"
        if not ModelingPy.ClassExist(model_name):
            if not ModelingPy.OpenModelFile(str(model_path)):
                raise RuntimeError(f"OpenModelFile failed for {model_path}")

        check_ok = bool(ModelingPy.CheckModel(model_name))
        if not check_ok:
            raise RuntimeError(f"CheckModel failed for {model_name}: {ModelingPy.GetLastErrors()}")
        simulate_ok = bool(ModelingPy.SimulateModel(model_name))
        if not simulate_ok:
            raise RuntimeError(f"SimulateModel failed for {model_name}: {ModelingPy.GetLastErrors()}")

        times = [float(value) for value in ModelingPy.GetVarTimes()]
        values = [[float(value) for value in column] for column in ModelingPy.GetVarsValues(builder.OUTPUTS)]
        lengths = {len(times), *(len(column) for column in values)}
        if lengths != {4}:
            raise RuntimeError(f"unexpected result lengths for {model_name}: {sorted(lengths)}")
        if not all(math.isfinite(value) for column in values for value in column):
            raise RuntimeError(f"NaN or Inf in {model_name}")
        columns = dict(zip(builder.OUTPUTS, values, strict=True))
        checks = behavior_checks(controller, columns)
        fixture_ok = all(checks.values())
        overall_ok = overall_ok and fixture_ok

        csv_path = RAW_DIR / f"{controller}_mil.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["time_s", *builder.OUTPUTS])
            writer.writerows(zip(times, *values))

        metrics_path = METRICS_DIR / f"{controller}_mil_metrics.json"
        metrics = {
            "schema": "mosim.classic_controller.mworks_mil_metrics.v1",
            "status": "passed" if fixture_ok else "failed",
            "source": "MWORKS_MCP_LIVE",
            "controller_id": controller_id,
            "controller": controller,
            "model_name": model_name,
            "check_model": check_ok,
            "simulate_model": simulate_ok,
            "sample_count": len(times),
            "output_count": len(builder.OUTPUTS),
            "behavior_checks": checks,
            "first_outputs": {name: column[0] for name, column in columns.items()},
            "last_outputs": {name: column[-1] for name, column in columns.items()},
            "raw_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
            "raw_csv_sha256": sha256(csv_path),
        }
        write_json(metrics_path, metrics)
        fixtures[controller] = {
            "status": metrics["status"],
            "model_name": model_name,
            "metrics": str(metrics_path.relative_to(ROOT)).replace("\\", "/"),
            "raw_csv": metrics["raw_csv"],
        }

    manifest = {
        "schema": "mosim.classic_controller.mworks_mil_manifest.v1",
        "status": "passed" if overall_ok else "failed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "MWORKS_MCP_LIVE",
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "bridge_model": BRIDGE_NAME,
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "claim_ceiling": "Real fixed-input graphical Sysblock MIL behavior only; official codegen, SIL, px4ctrl and Gazebo remain separate gates.",
    }
    manifest_path = RESULT_DIR / "MWORKS_MIL_MANIFEST.json"
    write_json(manifest_path, manifest)
    return {"ok": overall_ok, "manifest": str(manifest_path), "fixtures": fixtures}


RUN_SCRIPT_RESULT = main()
