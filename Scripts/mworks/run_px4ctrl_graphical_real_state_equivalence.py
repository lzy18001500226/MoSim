"""Run and extract the isolated 7.2c PX4CTRL real-state comparison.

The simulation is executed through the official ModelingPy API.  The CSV and
metrics are derived from the resulting native MWORKS result in the same API
call; they are not an offline substitute for the simulation.
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
    / "Px4CtrlFormalRunnerTransitionHarness.mo"
)
DEFAULT_MODEL_NAME = (
    "MoSimQuadrotorModel.Experiment.Runners.Graphical."
    "Px4CtrlFormalRunnerTransitionHarness"
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
DEFAULT_FORMAL_RUNNER_PATH = (
    PROJECT_ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Experiment"
    / "Runners"
    / "Formal"
    / "Px4CtrlFormalRunner.mo"
)
DEFAULT_LEGACY_RUNNER_PATH = (
    PROJECT_ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Experiment"
    / "Runners"
    / "Formal"
    / "Px4CtrlEquationBridgeFormalRunner.mo"
)
DEFAULT_OUTPUT_ROOT = (
    PROJECT_ROOT
    / "Results"
    / "mworks_live_gate"
    / "px4ctrl_graphical_7_2_019e9868_20260807"
    / "real_state_closed_loop_7_2c"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--package-path", type=Path, default=DEFAULT_PROJECT_PACKAGE_PATH)
    parser.add_argument("--real-state-runner-path", type=Path, default=DEFAULT_REAL_STATE_RUNNER_PATH)
    parser.add_argument("--formal-runner-path", type=Path, default=DEFAULT_FORMAL_RUNNER_PATH)
    parser.add_argument("--legacy-runner-path", type=Path, default=DEFAULT_LEGACY_RUNNER_PATH)
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


def build_signal_groups() -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []

    def add_vector(
        label: str,
        unit: str,
        graphical_base: str,
        equation_base: str,
        delta_base: str,
        count: int,
    ) -> None:
        for index in range(1, count + 1):
            groups.append(
                {
                    "signal": f"{label}[{index}]",
                    "unit": unit,
                    "graphical": f"{graphical_base}[{index}]",
                    "equation": f"{equation_base}[{index}]",
                    "delta": f"{delta_base}[{index}]",
                }
            )

    add_vector(
        "reference_position",
        "m",
        "graphical_reference_position",
        "equation_reference_position",
        "delta_reference_position",
        3,
    )
    add_vector(
        "reference_velocity",
        "m/s",
        "graphical_reference_velocity",
        "equation_reference_velocity",
        "delta_reference_velocity",
        3,
    )
    add_vector(
        "reference_acceleration",
        "m/s^2",
        "graphical_reference_acceleration",
        "equation_reference_acceleration",
        "delta_reference_acceleration",
        3,
    )
    add_vector("position", "m", "graphical_position", "equation_position", "delta_position", 3)
    add_vector(
        "velocity_measured",
        "m/s",
        "graphical_velocity_mea",
        "equation_velocity_mea",
        "delta_velocity_mea",
        3,
    )
    add_vector("attitude", "rad", "graphical_attitude", "equation_attitude", "delta_attitude", 3)
    add_vector(
        "body_rate_measured",
        "rad/s",
        "graphical_body_rate_mea",
        "equation_body_rate_mea",
        "delta_body_rate_mea",
        3,
    )
    add_vector(
        "desired_acceleration",
        "m/s^2",
        "graphical_desired_acc",
        "equation_desired_acc",
        "delta_desired_acc",
        3,
    )
    add_vector(
        "attitude_command",
        "rad",
        "graphical_attitude_command",
        "equation_attitude_command",
        "delta_attitude_command",
        3,
    )
    groups.append(
        {
            "signal": "collective_thrust_delta",
            "unit": "N",
            "graphical": "graphical_collective_thrust_delta",
            "equation": "equation_collective_thrust_delta",
            "delta": "delta_collective_thrust_delta",
        }
    )
    add_vector(
        "rotor_command",
        "rad/s",
        "graphical_rotor_command",
        "equation_rotor_command",
        "delta_rotor_command",
        4,
    )
    return groups


def unique_names(groups: list[dict[str, object]]) -> list[str]:
    names: list[str] = []
    for group in groups:
        for key in ("graphical", "equation", "delta"):
            name = str(group[key])
            if name not in names:
                names.append(name)
    names.extend(
        [
            "equation_velocity_estimate[1]",
            "equation_velocity_estimate[2]",
            "equation_velocity_estimate[3]",
        ]
    )
    return names


def condition_at_peak(
    index: int,
    times: list[float],
    series: dict[str, list[float]],
) -> dict[str, object]:
    def values(prefix: str, count: int) -> list[float]:
        return [series[f"{prefix}[{component}]"][index] for component in range(1, count + 1)]

    return {
        "time_s": times[index],
        "reference_position_m": values("graphical_reference_position", 3),
        "reference_velocity_mps": values("graphical_reference_velocity", 3),
        "reference_acceleration_mps2": values("graphical_reference_acceleration", 3),
        "graphical_position_m": values("graphical_position", 3),
        "equation_position_m": values("equation_position", 3),
        "graphical_velocity_mps": values("graphical_velocity_mea", 3),
        "equation_velocity_mps": values("equation_velocity_mea", 3),
        "equation_velocity_estimate_mps": values("equation_velocity_estimate", 3),
        "graphical_attitude_rad": values("graphical_attitude", 3),
        "equation_attitude_rad": values("equation_attitude", 3),
        "graphical_body_rate_radps": values("graphical_body_rate_mea", 3),
        "equation_body_rate_radps": values("equation_body_rate_mea", 3),
    }


def compare_group(
    group: dict[str, object],
    times: list[float],
    series: dict[str, list[float]],
) -> dict[str, object]:
    graphical_name = str(group["graphical"])
    equation_name = str(group["equation"])
    delta_name = str(group["delta"])
    graphical = series[graphical_name]
    equation = series[equation_name]
    delta = series[delta_name]
    peak_index = max(range(len(times)), key=lambda index: abs(delta[index]))
    peak_abs = abs(delta[peak_index])
    peak_signed = delta[peak_index]
    peak_scale = max(1e-12, abs(graphical[peak_index]), abs(equation[peak_index]))
    return {
        "signal": str(group["signal"]),
        "unit": str(group["unit"]),
        "graphical_variable": graphical_name,
        "equation_variable": equation_name,
        "delta_variable": delta_name,
        "maximum_absolute_deviation": peak_abs,
        "signed_deviation_at_peak": peak_signed,
        "time_s": times[peak_index],
        "graphical_value_at_peak": graphical[peak_index],
        "equation_value_at_peak": equation[peak_index],
        "relative_deviation_at_peak": peak_abs / peak_scale,
        "condition_at_peak": condition_at_peak(peak_index, times, series),
    }


def real_state_source_contract(runner_path: Path) -> dict[str, object]:
    source = runner_path.read_text(encoding="utf-8")
    required = [
        "Modelica.Blocks.Discrete.UnitDelay sampled_position_ref[3]",
        "Modelica.Blocks.Discrete.UnitDelay sampled_velocity_ref[3]",
        "Modelica.Blocks.Discrete.UnitDelay sampled_acceleration_ref[3]",
        "Modelica.Blocks.Discrete.UnitDelay sampled_position[3]",
        "Modelica.Blocks.Discrete.UnitDelay sampled_attitude[3]",
        "connect(reference.position_command, sampled_position_ref.u);",
        "connect(reference.velocity_command, sampled_velocity_ref.u);",
        "connect(reference.acceleration_command, sampled_acceleration_ref.u);",
        "connect(plant.position, sampled_position.u);",
        "sampled_attitude.u = attitude_mea_from_quat;",
        "connect(sampled_attitude[3].y, graphical_outer.yaw_mea);",
        "connect(plant.VelMea[1], graphical_outer.vx);",
        "connect(plant.VelMea[2], graphical_outer.vy);",
        "connect(plant.VelMea[3], graphical_outer.vz);",
        "connect(plant.BodyRateMea, offline_inner_allocator.body_rate_mea);",
        "offline_inner_allocator.attitude_mea = attitude_mea_from_quat;",
        "quat_xyzw = plant.QuatMea;",
    ]
    missing = [line for line in required if line not in source]
    return {
        "runner_source": str(runner_path),
        "required_statements": required,
        "missing_statements": missing,
        "pass": not missing,
    }


def formal_runner_baseline_contract(
    formal_runner_path: Path,
    equation_bridge_runner_path: Path,
    graphical_real_state_runner_path: Path,
) -> dict[str, object]:
    active_source = formal_runner_path.read_text(encoding="utf-8")
    equation_bridge_source = equation_bridge_runner_path.read_text(encoding="utf-8")
    graphical_real_state_source = graphical_real_state_runner_path.read_text(encoding="utf-8")
    active_required = "extends Px4CtrlEquationBridgeFormalRunner;"
    equation_bridge_required = "Px4CtrlEquationBridgeReportBaselineAdapter controller"
    graphical_runner_required = "model Px4CtrlGraphicalRealStateFormalRunner"
    return {
        "active_runner_source": str(formal_runner_path),
        "equation_bridge_runner_source": str(equation_bridge_runner_path),
        "graphical_real_state_runner_source": str(graphical_real_state_runner_path),
        "active_runner_required_statement": active_required,
        "equation_bridge_required_statement": equation_bridge_required,
        "active_runner_is_equation_bridge": active_required in active_source,
        "equation_bridge_preserved": equation_bridge_required in equation_bridge_source,
        "graphical_real_state_runner_is_independent": (
            graphical_runner_required in graphical_real_state_source
            and "extends Px4CtrlFormalRunner;" not in graphical_real_state_source
        ),
        "pass": (
            active_required in active_source
            and equation_bridge_required in equation_bridge_source
            and graphical_runner_required in graphical_real_state_source
            and "extends Px4CtrlFormalRunner;" not in graphical_real_state_source
        ),
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
    metrics_csv = output_root / "metrics" / f"{run_id}.csv"
    run_record = output_root / "logs" / f"{run_id}_run_record.json"
    output_root.mkdir(parents=True, exist_ok=True)
    native_root.mkdir(parents=True, exist_ok=True)

    groups = build_signal_groups()
    names = unique_names(groups)
    record: dict[str, object] = {
        "schema_version": "mosim.px4ctrl.real_state_7_2c_run.v1",
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
        if not model_path.is_file():
            raise FileNotFoundError(model_path)
        if not package_path.is_file():
            raise FileNotFoundError(package_path)
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

        comparison_rows = [compare_group(group, times, series) for group in groups]
        velocity_estimate_rows: list[dict[str, object]] = []
        for component in range(1, 4):
            errors = [
                series[f"graphical_velocity_mea[{component}]"][index]
                - series[f"equation_velocity_estimate[{component}]"][index]
                for index in range(len(times))
            ]
            peak_index = max(range(len(times)), key=lambda index: abs(errors[index]))
            velocity_estimate_rows.append(
                {
                    "signal": f"velocity_input_vs_formal_estimate[{component}]",
                    "unit": "m/s",
                    "graphical_variable": f"graphical_velocity_mea[{component}]",
                    "equation_variable": f"equation_velocity_estimate[{component}]",
                    "maximum_absolute_deviation": abs(errors[peak_index]),
                    "signed_deviation_at_peak": errors[peak_index],
                    "time_s": times[peak_index],
                    "condition_at_peak": condition_at_peak(peak_index, times, series),
                }
            )

        source_contract = real_state_source_contract(args.real_state_runner_path)
        baseline_contract = formal_runner_baseline_contract(
            args.formal_runner_path,
            args.legacy_runner_path,
            args.real_state_runner_path,
        )
        initial_alignment_names = [
            "delta_desired_acc[1]",
            "delta_desired_acc[2]",
            "delta_desired_acc[3]",
            "delta_collective_thrust_delta",
            "delta_rotor_command[1]",
            "delta_rotor_command[2]",
            "delta_rotor_command[3]",
            "delta_rotor_command[4]",
        ]
        initial_alignment = {name: series[name][0] for name in initial_alignment_names}
        initial_alignment_max = max(abs(value) for value in initial_alignment.values())
        full_horizon_pass = (
            args.stop_time >= 50.0
            and times[-1] >= 50.0 - max(args.interval * 1.5, 1e-9)
        )
        real_state_closure = {
            "source_contract": source_contract,
            "initial_alignment": {
                "signals": initial_alignment,
                "maximum_absolute_deviation": initial_alignment_max,
                "threshold": 1e-9,
                "pass": initial_alignment_max <= 1e-9,
            },
            "native_result": {
                "all_series_finite": True,
                "sample_count": len(times),
                "full_50_s_horizon_pass": full_horizon_pass,
            },
            "pass": (
                bool(source_contract["pass"])
                and initial_alignment_max <= 1e-9
                and full_horizon_pass
            ),
        }
        max_absolute = max(row["maximum_absolute_deviation"] for row in comparison_rows)
        comparison = {
            "sample_count": len(times),
            "time_start_s": times[0],
            "time_end_s": times[-1],
            "all_series_finite": True,
            "maximum_absolute_deviation": max_absolute,
            "signals": comparison_rows,
            "velocity_estimate_diagnostic": velocity_estimate_rows,
            "numerically_identical_under_1e-9": max_absolute <= 1e-9,
            "measurement_boundary": {
                "graphical_velocity_input": "Sunray150Assembly.VelMea direct world-frame velocity",
                "formal_velocity_input": "sampled position filtered through FormalRunner.velocity_estimator",
                "numerical_identity_required_for_7_2c": False,
                "reason": "7.2c deliberately replaces the runner-owned velocity estimate with the plant truth port.",
            },
            "transition_gate": {
                "eligible_only_if_7_2c_and_7_2d_are_accepted": True,
                "7_2c_real_state_closure_pass": real_state_closure["pass"],
                "7_2d_status": "not_evaluated_by_7_2c; use the isolated quaternion-order harness",
                "formal_runner_equation_bridge_contract_pass": baseline_contract["pass"],
                "graphical_takeover_performed": False,
                "graphical_takeover_decision": "deferred_pending_separate_7_2d_acceptance",
                "mismatch_policy": "List discrepancies; do not choose which implementation to modify.",
            },
        }
        metrics = {
            "schema_version": "mosim.px4ctrl.real_state_7_2c_metrics.v1",
            "source_label": "MWORKS_DIRECT_API",
            "metric_extractor": "official ModelingPy.GetVarsValues over the current native Result.msr",
            "model_name": args.model_name,
            "project_package_path": str(package_path),
            "result_file": str(result_file),
            "result_sha256": record["native_result_sha256"],
            "harness_sha256": sha256(model_path),
            "execution": {
                "check_model": True,
                "direct_modelingpy_simulate_model": True,
                "simulation_exit_state": "not exposed by the direct runner",
                "simulation_end_time_s": times[-1],
                "result_manager_open_result": True,
                "result_manager_sample_count": len(times),
            },
            "comparison": comparison,
            "real_state_closure": real_state_closure,
            "formal_runner_baseline": baseline_contract,
            "quaternion_order_boundary": "7.2d is deliberately excluded from this 7.2c comparison and requires its own native result bundle.",
            "claim_boundary": "This is MWORKS native 7.2c real-state closed-loop comparison evidence. It does not prove ROS/PX4/Gazebo deployment or flight acceptance.",
        }
        write_json(metrics_json, metrics)
        with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "signal",
                    "unit",
                    "maximum_absolute_deviation",
                    "signed_deviation_at_peak",
                    "time_s",
                    "relative_deviation_at_peak",
                ]
            )
            for row in comparison_rows + velocity_estimate_rows:
                writer.writerow(
                    [
                        row["signal"],
                        row["unit"],
                        row["maximum_absolute_deviation"],
                        row["signed_deviation_at_peak"],
                        row["time_s"],
                        row.get("relative_deviation_at_peak", ""),
                    ]
                )
        record.update(
            {
                "status": "completed",
                "sample_count": len(times),
                "time_start_s": times[0],
                "time_end_s": times[-1],
                "raw_csv": str(raw_csv),
                "metrics_json": str(metrics_json),
                "metrics_csv": str(metrics_csv),
                "real_state_closure_pass": real_state_closure["pass"],
                "formal_runner_equation_bridge_contract_pass": baseline_contract["pass"],
                "comparison_numerically_identical_under_1e-9": max_absolute <= 1e-9,
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
