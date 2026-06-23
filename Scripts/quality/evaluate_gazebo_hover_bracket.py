#!/usr/bin/env python3
"""Aggregate Gazebo single-UAV open-loop hover command bracket samples.

This evaluates thrust-scale samples only. It does not tune a controller or
prove hover/closed-loop behavior.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    yaml = None
    YAML_IMPORT_ERROR = exc
else:
    YAML_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = ROOT / "Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError(f"PyYAML unavailable: {YAML_IMPORT_ERROR}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def bracket_cfg(scenario: dict[str, Any]) -> dict[str, Any]:
    ros2 = scenario.get("ros2") if isinstance(scenario.get("ros2"), dict) else {}
    cfg = ros2.get("single_uav_hover_command_bracket")
    return cfg if isinstance(cfg, dict) else {}


def command_dir_name(command: float) -> str:
    return f"cmd_{command:.6f}".replace(".", "p")


def sample_dir_candidates(result_root: Path, command: float) -> list[Path]:
    return [
        result_root / command_dir_name(command),
        result_root / f"cmd_{command:.3f}".replace(".", "p"),
    ]


def parse_commands(raw: list[str] | None, cfg: dict[str, Any]) -> list[float]:
    if raw:
        values = [float(item) for item in raw]
    else:
        cfg_values = cfg.get("commands", [])
        values = [float(item) for item in cfg_values] if isinstance(cfg_values, list) else []
    if not values:
        raise SystemExit("no bracket commands supplied")
    for value in values:
        if not math.isfinite(value) or value < 0.0 or value > 1.0:
            raise SystemExit(f"invalid normalized command: {value}")
    return values


def float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def classify_sample(sample: dict[str, Any], cls: dict[str, Any]) -> str:
    z_delta = float_or_none(sample.get("z_delta_m"))
    max_z_delta = float_or_none(sample.get("max_abs_z_delta_m"))
    if max_z_delta is None:
        max_z_delta = float_or_none(sample.get("max_z_delta_m"))
    max_3d_delta = float_or_none(sample.get("max_3d_delta_m"))
    if not sample.get("evidence_valid"):
        return "invalid_evidence"

    grounded_max = float(cls.get("grounded_max_z_delta_m", 0.05))
    near_abs = float(cls.get("near_hover_abs_z_delta_m", 0.5))
    near_max_z = float(cls.get("near_hover_max_z_excursion_m", 1.0))
    near_max_3d = float(cls.get("near_hover_max_3d_excursion_m", 2.0))
    over_delta = float(cls.get("over_climb_z_delta_m", 1.0))
    over_max_z = float(cls.get("over_climb_max_z_m", 2.0))

    if z_delta is None or max_z_delta is None or max_3d_delta is None:
        return "invalid_metrics"
    if z_delta >= over_delta or max_z_delta >= over_max_z:
        return "over_climb"
    if max_z_delta <= grounded_max and abs(z_delta) <= grounded_max:
        return "grounded_or_under_thrust"
    if abs(z_delta) <= near_abs and max_z_delta <= near_max_z and max_3d_delta <= near_max_3d:
        return "near_hover_candidate"
    if z_delta < -near_abs:
        return "descending_or_under_thrust"
    return "transient_or_unclassified"


def load_sample(result_root: Path, command: float) -> dict[str, Any]:
    candidates = sample_dir_candidates(result_root, command)
    sample_dir = next((path for path in candidates if path.exists()), candidates[0])
    runtime_status = read_json(sample_dir / "RUNTIME_STATUS.json")
    plant_eval = read_json(sample_dir / "GAZEBO_PLANT_RESPONSE_EVAL.json")
    fixture = read_json(sample_dir / "controller_output_fixture.json")
    adapter = read_json(sample_dir / "controller_output_adapter_node.json")

    plant = plant_eval.get("plant_response", {}) if isinstance(plant_eval.get("plant_response"), dict) else {}
    truth = plant_eval.get("truth_recording", {}) if isinstance(plant_eval.get("truth_recording"), dict) else {}
    truth_sample_count = truth.get("valid_sample_count") or truth.get("summary_count") or 0
    try:
        truth_sample_count_int = int(truth_sample_count)
    except (TypeError, ValueError):
        truth_sample_count_int = 0
    runtime_plant = (
        runtime_status.get("plant_response_pre_acceptance", {})
        if isinstance(runtime_status.get("plant_response_pre_acceptance"), dict)
        else {}
    )
    actuator = (
        runtime_status.get("actuator_command", {})
        if isinstance(runtime_status.get("actuator_command"), dict)
        else {}
    )
    ros_echo = actuator.get("ros_echo", {}) if isinstance(actuator.get("ros_echo"), dict) else {}
    gz_echo = actuator.get("gz_echo", {}) if isinstance(actuator.get("gz_echo"), dict) else {}

    command_values = fixture.get("command") if isinstance(fixture.get("command"), list) else []
    adapter_velocity = adapter.get("velocity") if isinstance(adapter.get("velocity"), list) else []
    runtime_blockers = runtime_status.get("blockers") if isinstance(runtime_status.get("blockers"), list) else []
    plant_blockers = plant_eval.get("blockers") if isinstance(plant_eval.get("blockers"), list) else []
    plant_gate_passed = bool(plant_eval.get("gate_passed"))

    evidence_valid = (
        fixture.get("status") == "published"
        and adapter.get("status") == "published"
        and bool(runtime_plant.get("truth_recording_recorded"))
        and bool(runtime_plant.get("eval_recorded"))
        and truth_sample_count_int > 0
        and plant.get("z_delta_m") is not None
        and plant.get("max_3d_delta_m") is not None
        and bool(ros_echo.get("sample_recorded"))
        and bool(gz_echo.get("sample_recorded"))
        and bool(actuator.get("ros_velocity_matches_expected"))
        and bool(actuator.get("gz_velocity_matches_expected"))
    )

    return {
        "command": command,
        "sample_dir": rel(sample_dir),
        "runtime_status": runtime_status.get("status"),
        "runtime_gate_passed": bool(runtime_status.get("gate_passed")),
        "runtime_blockers": runtime_blockers,
        "plant_eval_status": plant_eval.get("status"),
        "plant_gate_passed": plant_gate_passed,
        "plant_blockers": plant_blockers,
        "evidence_valid": evidence_valid,
        "fixture_status": fixture.get("status"),
        "adapter_status": adapter.get("status"),
        "fixture_command": command_values,
        "adapter_velocity": adapter_velocity,
        "truth_sample_count": truth_sample_count_int,
        "truth_duration_s": truth.get("duration_s"),
        "z_delta_m": plant.get("z_delta_m"),
        "max_z_delta_m": plant.get("max_z_delta_m"),
        "min_z_delta_m": plant.get("min_z_delta_m"),
        "max_abs_z_delta_m": plant.get("max_abs_z_delta_m"),
        "max_3d_delta_m": plant.get("max_3d_delta_m"),
        "xy_delta_m": plant.get("xy_delta_m"),
        "early_z_range_m": plant.get("early_z_range_m"),
        "ros_velocity_matches_expected": actuator.get("ros_velocity_matches_expected"),
        "gz_velocity_matches_expected": actuator.get("gz_velocity_matches_expected"),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    scenario_path = repo_path(args.scenario)
    scenario = read_yaml(scenario_path)
    cfg = bracket_cfg(scenario)
    classification_cfg = (
        cfg.get("classification") if isinstance(cfg.get("classification"), dict) else {}
    )
    commands = parse_commands(args.commands, cfg)
    result_root = repo_path(args.result_root or cfg.get("result_dir", "Results/gazebo_ros2/sunray150_gazebo_ros2_single_uav_hover_command_bracket"))
    output_json = repo_path(
        args.output_json or result_root / str(cfg.get("output_json", "GAZEBO_HOVER_COMMAND_BRACKET_EVAL.json"))
    )

    samples = [load_sample(result_root, command) for command in commands]
    for sample in samples:
        sample["classification"] = classify_sample(sample, classification_cfg)

    valid_samples = [sample for sample in samples if sample.get("evidence_valid")]
    near_candidates = [
        sample for sample in valid_samples if sample.get("classification") == "near_hover_candidate"
    ]
    over_samples = [sample for sample in valid_samples if sample.get("classification") == "over_climb"]
    under_samples = [
        sample
        for sample in valid_samples
        if sample.get("classification") in {"grounded_or_under_thrust", "descending_or_under_thrust"}
    ]
    min_valid_samples = int(classification_cfg.get("min_valid_samples", 3))
    blockers: list[str] = []
    warnings: list[str] = []
    if len(valid_samples) < min_valid_samples:
        blockers.append(f"valid_bracket_samples_below_min:{len(valid_samples)}<{min_valid_samples}")
    if not near_candidates:
        warnings.append("no_near_hover_candidate_found_in_current_bracket")
    if not over_samples:
        warnings.append("no_over_climb_sample_found_in_current_bracket")
    if not under_samples:
        warnings.append("no_under_thrust_sample_found_in_current_bracket")
    for sample in samples:
        if not sample.get("evidence_valid"):
            blockers.append(f"invalid_sample_evidence:{sample['command']:.3f}")

    chosen = None
    if near_candidates:
        chosen = min(
            near_candidates,
            key=lambda item: abs(float_or_none(item.get("z_delta_m")) or 0.0),
        )

    report = {
        "schema": "mosim.gazebo_hover_command_bracket_eval.v1",
        "status": "passed" if not blockers else "blocked",
        "gate_passed": not blockers,
        "scenario": rel(scenario_path),
        "result_root": rel(result_root),
        "output_json": rel(output_json),
        "commands": commands,
        "classification_thresholds": classification_cfg,
        "theoretical_hover_estimate": cfg.get("theoretical_hover_estimate", {}),
        "valid_sample_count": len(valid_samples),
        "class_counts": {
            "near_hover_candidate": len(near_candidates),
            "over_climb": len(over_samples),
            "under_thrust": len(under_samples),
            "invalid": len([sample for sample in samples if not sample.get("evidence_valid")]),
        },
        "selected_near_hover_candidate": chosen,
        "samples": samples,
        "blockers": blockers,
        "warnings": warnings,
        "next_gate_decision": (
            "near_hover_candidate_available_for_next_bounded_closed_loop_pre_acceptance"
            if chosen and not blockers
            else "adjust_bracket_or_fix_gazebo_plant_scaling_before_closed_loop"
        ),
        "claim_boundary": [
            "This is an open-loop Gazebo thrust-scale bracket for one Sunray150 plant.",
            "Low-motion samples can be valid under-thrust evidence even when a per-sample plant-response threshold blocks.",
            "It does not prove hover success, trajectory tracking, controller performance, planner_ready, final closed_loop acceptance, or multi-UAV readiness.",
        ],
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default=str(DEFAULT_SCENARIO))
    parser.add_argument("--result-root")
    parser.add_argument("--output-json")
    parser.add_argument("--commands", nargs="*")
    args = parser.parse_args()
    report = build_report(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
