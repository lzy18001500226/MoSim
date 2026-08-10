"""Run and extract the isolated 7.2d PX4CTRL quaternion-order validation.

This uses the official ModelingPy API directly so a wrapper return-value
failure cannot be mistaken for a model/result failure. The generated native
result, raw CSV, metrics, and run record are dedicated to quaternion order;
they are not part of the 7.2c signal-for-signal comparison.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import mworks.sysplorer as ModelingPy


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT_PACKAGE_PATH = PROJECT_ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
DEFAULT_MODEL_PATH = (
    PROJECT_ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Experiment"
    / "Runners"
    / "Graphical"
    / "Px4CtrlGraphicalQuaternionOrderValidationHarness.mo"
)
DEFAULT_MODEL_NAME = (
    "MoSimQuadrotorModel.Experiment.Runners.Graphical."
    "Px4CtrlGraphicalQuaternionOrderValidationHarness"
)
DEFAULT_REAL_STATE_RUNNER_PATH = (
    PROJECT_ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Experiment"
    / "Runners"
    / "Formal"
    / "Px4CtrlGraphicalRealStateFormalRunner.mo"
)
DEFAULT_SENSOR_PATH = PROJECT_ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Sensors" / "package.mo"
DEFAULT_GRAPHICAL_SYSBLOCK_PATH = (
    PROJECT_ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Control"
    / "Implementations"
    / "Sysblocks"
    / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.mo"
)
DEFAULT_OUTPUT_ROOT = (
    PROJECT_ROOT
    / "Results"
    / "mworks_live_gate"
    / "px4ctrl_graphical_7_2_019e9868_20260807"
    / "quaternion_order_7_2d"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--package-path", type=Path, default=DEFAULT_PROJECT_PACKAGE_PATH)
    parser.add_argument("--real-state-runner-path", type=Path, default=DEFAULT_REAL_STATE_RUNNER_PATH)
    parser.add_argument("--sensor-path", type=Path, default=DEFAULT_SENSOR_PATH)
    parser.add_argument("--graphical-sysblock-path", type=Path, default=DEFAULT_GRAPHICAL_SYSBLOCK_PATH)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--stop-time", type=float, default=50.0)
    parser.add_argument("--interval", type=float, default=0.01)
    return parser.parse_args()


def last_errors() -> str:
    try:
        return str(ModelingPy.GetLastErrors())
    except Exception as exc:  # pragma: no cover - only used for API failures
        return f"GetLastErrors failed: {exc!r}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def newest_result_file(root: Path) -> Path:
    candidates = [path for path in root.rglob("Result.msr") if path.is_file()]
    if not candidates:
        raise RuntimeError(f"No native Result.msr found below {root}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def finite_series(values: Iterable[object]) -> list[float]:
    series = [float(value) for value in values]
    if not all(math.isfinite(value) for value in series):
        raise RuntimeError("result contains NaN or Inf")
    return series


def names_for(prefix: str, count: int) -> list[str]:
    return [f"{prefix}[{index}]" for index in range(1, count + 1)]


def result_variables() -> list[str]:
    names: list[str] = []
    for prefix, count in (
        ("quat_xyzw", 4),
        ("quat_wxyz", 4),
        ("reorder_identity_error", 4),
        ("attitude_from_reordered_quat", 3),
        ("legacy_angle_mea", 3),
        ("quat_to_euler_error", 3),
    ):
        names.extend(names_for(prefix, count))
    names.extend(
        [
            "quaternion_norm",
            "quaternion_norm_error",
            "yaw_before_sample",
            "yaw_to_graphical_sysblock",
        ]
    )
    return names


def component_peak(
    variable: str,
    times: list[float],
    series: dict[str, list[float]],
) -> dict[str, object]:
    values = series[variable]
    index = max(range(len(times)), key=lambda item: abs(values[item]))
    return {
        "variable": variable,
        "maximum_absolute_value": abs(values[index]),
        "signed_value_at_peak": values[index],
        "time_s": times[index],
        "quat_xyzw_at_peak": [series[name][index] for name in names_for("quat_xyzw", 4)],
        "quat_wxyz_at_peak": [series[name][index] for name in names_for("quat_wxyz", 4)],
        "attitude_from_reordered_quat_rad_at_peak": [
            series[name][index] for name in names_for("attitude_from_reordered_quat", 3)
        ],
        "legacy_angle_mea_rad_at_peak": [
            series[name][index] for name in names_for("legacy_angle_mea", 3)
        ],
    }


def source_contract(
    model_path: Path,
    real_state_runner_path: Path,
    sensor_path: Path,
    graphical_sysblock_path: Path,
) -> dict[str, object]:
    harness = model_path.read_text(encoding="utf-8")
    runner = real_state_runner_path.read_text(encoding="utf-8")
    sensors = sensor_path.read_text(encoding="utf-8")
    graphical_sysblock = graphical_sysblock_path.read_text(encoding="utf-8")
    required = {
        "sensor_to_q": "QuatMea = Modelica.Mechanics.MultiBody.Frames.to_Q(frame_a.R);",
        "modelica_order": "{x, y, z, w}",
        "explicit_reorder": "quat_wxyz = {quat_xyzw[4], quat_xyzw[1], quat_xyzw[2], quat_xyzw[3]};",
        "sampled_yaw_boundary": "connect(sampled_attitude[3].y, graphical_outer.yaw_mea);",
        "graphical_scalar_yaw_port": "SysplorerEmbeddedCoder.Port.Inport yaw_mea",
        "isolated_harness": "Px4CtrlGraphicalRealStateFormalRunner graphical_formal",
        "no_equation_bridge_in_harness": "Px4CtrlEquationBridgeFormalRunner",
    }
    checks = {
        "sensor_to_q": required["sensor_to_q"] in sensors,
        "modelica_order": required["modelica_order"] in sensors,
        "explicit_reorder": required["explicit_reorder"] in runner,
        "sampled_yaw_boundary": required["sampled_yaw_boundary"] in runner,
        "graphical_scalar_yaw_port": required["graphical_scalar_yaw_port"] in graphical_sysblock,
        "isolated_harness": required["isolated_harness"] in harness,
        "no_equation_bridge_in_harness": required["no_equation_bridge_in_harness"] not in harness,
    }
    return {
        "harness_source": str(model_path),
        "real_state_runner_source": str(real_state_runner_path),
        "sensor_source": str(sensor_path),
        "graphical_sysblock_source": str(graphical_sysblock_path),
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    args = parse_args()
    if args.stop_time <= 0 or args.interval <= 0:
        raise ValueError("stop time and interval must be positive")
    model_path = args.model_path.resolve()
    package_path = args.package_path.resolve()
    output_root = args.output_root.resolve()
    run_id = datetime.now(timezone.utc).strftime("directapi_%Y%m%d_%H%M%S")
    native_root = output_root / "native_results" / run_id
    raw_csv = output_root / "raw" / f"{run_id}.csv"
    metrics_json = output_root / "metrics" / f"{run_id}.json"
    run_record = output_root / "logs" / f"{run_id}_run_record.json"
    output_root.mkdir(parents=True, exist_ok=True)
    native_root.mkdir(parents=True, exist_ok=True)

    names = result_variables()
    record: dict[str, object] = {
        "schema_version": "mosim.px4ctrl.quaternion_order_7_2d_run.v1",
        "source_label": "MWORKS_DIRECT_API",
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "model_name": args.model_name,
        "harness_path": str(model_path),
        "project_package_path": str(package_path),
        "stop_time_s": args.stop_time,
        "interval_s": args.interval,
        "run_id": run_id,
        "status": "started",
    }
    write_json(run_record, record)

    try:
        for path in (
            model_path,
            package_path,
            args.real_state_runner_path.resolve(),
            args.sensor_path.resolve(),
            args.graphical_sysblock_path.resolve(),
        ):
            if not path.is_file():
                raise FileNotFoundError(path)
        if not ModelingPy.OpenModelFile(str(package_path)):
            raise RuntimeError(f"OpenModelFile(project package) failed: {last_errors()}")
        record["open_project_package"] = True
        check_ok = bool(ModelingPy.CheckModel(args.model_name))
        record["check_model"] = check_ok
        record["check_model_last_errors"] = last_errors()
        if not check_ok:
            raise RuntimeError(f"CheckModel failed: {record['check_model_last_errors']}")
        simulation_ok = bool(
            ModelingPy.SimulateModel(
                args.model_name,
                startTime=0.0,
                stopTime=args.stop_time,
                interval=args.interval,
                simMode=0,
                path=str(native_root),
            )
        )
        record["simulate_model"] = simulation_ok
        record["simulate_model_last_errors"] = last_errors()
        if not simulation_ok:
            raise RuntimeError(f"SimulateModel failed: {record['simulate_model_last_errors']}")

        result_file = newest_result_file(native_root)
        record["native_result_file"] = str(result_file)
        record["native_result_sha256"] = sha256(result_file)
        if not ModelingPy.OpenResult(str(result_file)):
            raise RuntimeError(f"OpenResult failed: {last_errors()}")
        record["open_result"] = True
        times = finite_series(ModelingPy.GetVarTimes())
        values = ModelingPy.GetVarsValues(names)
        if len(values) != len(names):
            raise RuntimeError(f"GetVarsValues returned {len(values)} columns for {len(names)} names")
        series = {name: finite_series(column) for name, column in zip(names, values)}
        if not times or len(times) <= 10 or any(len(column) != len(times) for column in series.values()):
            raise RuntimeError("native result has an invalid or undersized time series")
        if abs(times[-1] - args.stop_time) > max(args.interval * 1.5, 1e-9):
            raise RuntimeError(f"simulation ended at {times[-1]:.12g}s, expected {args.stop_time:.12g}s")

        raw_csv.parent.mkdir(parents=True, exist_ok=True)
        with raw_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["time"] + names)
            for index, time_value in enumerate(times):
                writer.writerow([time_value] + [series[name][index] for name in names])

        reorder_peaks = [component_peak(name, times, series) for name in names_for("reorder_identity_error", 4)]
        euler_peaks = [component_peak(name, times, series) for name in names_for("quat_to_euler_error", 3)]
        norm_peak = component_peak("quaternion_norm_error", times, series)
        yaw_sample_error = [
            series["yaw_to_graphical_sysblock"][index] - series["yaw_before_sample"][index]
            for index in range(len(times))
        ]
        yaw_sample_index = max(range(len(times)), key=lambda item: abs(yaw_sample_error[item]))
        contract = source_contract(
            model_path,
            args.real_state_runner_path.resolve(),
            args.sensor_path.resolve(),
            args.graphical_sysblock_path.resolve(),
        )
        full_horizon_pass = (
            args.stop_time >= 50.0
            and times[-1] >= 50.0 - max(args.interval * 1.5, 1e-9)
        )
        reorder_max = max(float(row["maximum_absolute_value"]) for row in reorder_peaks)
        euler_max = max(float(row["maximum_absolute_value"]) for row in euler_peaks)
        norm_max = float(norm_peak["maximum_absolute_value"])
        validation = {
            "modelica_sensor_order": "{x,y,z,w}",
            "graphical_sysblock_input_contract": "scalar yaw_mea; no PX4-style quaternion bus enters the graphical Sysblock",
            "explicit_boundary_mapping": "wxyz = {xyzw[4], xyzw[1], xyzw[2], xyzw[3]}",
            "source_contract": contract,
            "reorder_identity": {
                "threshold": 1e-12,
                "maximum_absolute_value": reorder_max,
                "components": reorder_peaks,
                "pass": reorder_max <= 1e-12,
            },
            "angle_reconstruction": {
                "threshold_rad": 1e-6,
                "maximum_absolute_value": euler_max,
                "components": euler_peaks,
                "pass": euler_max <= 1e-6,
            },
            "quaternion_norm": {
                "threshold": 1e-6,
                "maximum_absolute_value": norm_max,
                "peak": norm_peak,
                "pass": norm_max <= 1e-6,
            },
            "sampled_yaw_diagnostic": {
                "maximum_absolute_delay_effect_rad": abs(yaw_sample_error[yaw_sample_index]),
                "time_s": times[yaw_sample_index],
                "before_sample_rad": series["yaw_before_sample"][yaw_sample_index],
                "to_graphical_sysblock_rad": series["yaw_to_graphical_sysblock"][yaw_sample_index],
                "acceptance_role": "diagnostic_only; the controller sample delay is intentional",
            },
            "native_result": {
                "sample_count": len(times),
                "all_series_finite": True,
                "full_50_s_horizon_pass": full_horizon_pass,
            },
        }
        validation["pass"] = (
            bool(contract["pass"])
            and bool(validation["reorder_identity"]["pass"])
            and bool(validation["angle_reconstruction"]["pass"])
            and bool(validation["quaternion_norm"]["pass"])
            and full_horizon_pass
        )
        metrics = {
            "schema_version": "mosim.px4ctrl.quaternion_order_7_2d_metrics.v1",
            "source_label": "MWORKS_DIRECT_API",
            "metric_extractor": "official ModelingPy.GetVarsValues over the isolated 7.2d native Result.msr",
            "model_name": args.model_name,
            "project_package_path": str(package_path),
            "result_file": str(result_file),
            "result_sha256": record["native_result_sha256"],
            "harness_sha256": sha256(model_path),
            "execution": {
                "check_model": True,
                "direct_modelingpy_simulate_model": True,
                "simulation_end_time_s": times[-1],
                "result_manager_open_result": True,
                "result_manager_sample_count": len(times),
            },
            "quaternion_order_validation": validation,
            "claim_boundary": "This is isolated MWORKS 7.2d quaternion-order evidence. It does not establish 7.2c signal equivalence, 7.3 takeover, ROS/PX4/Gazebo deployment, or flight acceptance.",
        }
        write_json(metrics_json, metrics)
        record.update(
            {
                "status": "completed",
                "sample_count": len(times),
                "time_start_s": times[0],
                "time_end_s": times[-1],
                "raw_csv": str(raw_csv),
                "metrics_json": str(metrics_json),
                "quaternion_order_pass": validation["pass"],
            }
        )
        write_json(run_record, record)
        print(json.dumps(record, ensure_ascii=True))
        return 0
    except Exception as exc:
        record.update(
            {
                "status": "failed",
                "error": repr(exc),
                "last_errors": last_errors(),
            }
        )
        write_json(run_record, record)
        raise


if __name__ == "__main__":
    sys.exit(main())
