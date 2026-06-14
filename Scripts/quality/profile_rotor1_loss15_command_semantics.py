#!/usr/bin/env python3
"""Profile rotor1_loss15 controller command semantics.

This read-only diagnostic compares scenario model topology, controller output
limits, and existing raw command traces. It does not run MWORKS, Sysplorer,
MCP, check_model, SimulateModel, ROS2, UE, or GUI/window tools.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260612_rotor1_loss15_command_semantics"
SCENARIOS = [
    "Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_residual_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_fault_allocation_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_online_fault_allocation_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_multi_fault_isolation_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml",
]
COMMAND_COLUMNS = ["u1", "u2", "u3", "u4"]

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_scenario import read_yaml  # noqa: E402


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {value!r}")
    return number


def resolve_model_file(config: dict[str, Any]) -> Path:
    model = config.get("model", {})
    if not isinstance(model, dict):
        model = {}
    hint = model.get("model_path_hint")
    if hint:
        hinted = repo_path(hint)
        if hinted.exists():
            return hinted

    model_name = str(model.get("model_name", ""))
    class_name = model_name.rsplit(".", 1)[-1]
    if class_name:
        candidates = sorted((ROOT / "Models").glob(f"**/{class_name}.mo"))
        if candidates:
            return candidates[0]
    return repo_path(hint or "")


def controller_output_limit(controller_file: Path) -> float | None:
    if not controller_file.exists():
        return None
    text = controller_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"parameter\s+Real\s+output_limit\s*=\s*([0-9.+\-eE]+)", text)
    if not match:
        return None
    return float(match.group(1))


def classify_topology(model_file: Path) -> dict[str, Any]:
    if not model_file.exists():
        return {
            "model_file": rel(model_file),
            "topology": "missing_model_file",
            "has_hover_mapper": False,
            "has_direct_actuator_connect": False,
        }
    text = model_file.read_text(encoding="utf-8", errors="ignore")
    has_hover_mapper = all(token in text for token in ["hover_motor_speed_cmd", "motor_command_scale", "motor1_hover_sum"])
    has_direct = bool(re.search(r"connect\s*\(\s*controller3_2\.y\s*,\s*actuator1_1\.u\s*\)", text))
    if has_hover_mapper:
        topology = "delta_to_hover_command_mapper"
    elif has_direct:
        topology = "direct_controller_to_actuator"
    else:
        topology = "unknown_or_custom"
    return {
        "model_file": rel(model_file),
        "topology": topology,
        "has_hover_mapper": has_hover_mapper,
        "has_direct_actuator_connect": has_direct,
    }


def command_stats(raw_file: Path) -> dict[str, Any]:
    if not raw_file.exists():
        return {"raw_file": rel(raw_file), "raw_present": False}
    rows: list[dict[str, float]] = []
    with raw_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(set(COMMAND_COLUMNS + ["time", "z", "z_ref"]) - set(reader.fieldnames or []))
        if missing:
            return {"raw_file": rel(raw_file), "raw_present": True, "missing_columns": missing}
        for row in reader:
            item = {key: finite_float(row[key]) for key in COMMAND_COLUMNS + ["time", "z", "z_ref"]}
            rows.append(item)
    if not rows:
        return {"raw_file": rel(raw_file), "raw_present": True, "row_count": 0}

    command_values = [value for row in rows for value in (row[key] for key in COMMAND_COLUMNS)]
    abs_values = [abs(value) for value in command_values]
    final = rows[-1]
    early = [row for row in rows if row["time"] <= 2.0]
    late = [row for row in rows if row["time"] >= max(0.0, final["time"] - 5.0)]
    return {
        "raw_file": rel(raw_file),
        "raw_present": True,
        "row_count": len(rows),
        "time_start_s": rows[0]["time"],
        "time_end_s": final["time"],
        "command_abs_max": max(abs_values),
        "command_abs_mean": sum(abs_values) / len(abs_values),
        "command_min": min(command_values),
        "command_max": max(command_values),
        "early_0_2s_command_abs_mean": sum(abs(row[key]) for row in early for key in COMMAND_COLUMNS) / max(1, len(early) * 4),
        "late_5s_command_abs_mean": sum(abs(row[key]) for row in late for key in COMMAND_COLUMNS) / max(1, len(late) * 4),
        "final_z_m": final["z"],
        "final_z_ref_m": final["z_ref"],
        "final_z_error_m": final["z"] - final["z_ref"],
    }


def infer_semantics(topology: str, stats: dict[str, Any], output_limit: float | None) -> str:
    command_abs_max = stats.get("command_abs_max")
    if topology == "delta_to_hover_command_mapper":
        return "controller_outputs_delta_commands_mapped_to_hover_actuator_domain"
    if (
        topology == "direct_controller_to_actuator"
        and isinstance(command_abs_max, (int, float))
        and output_limit is not None
        and command_abs_max <= output_limit * 1.05
    ):
        return "controller_outputs_look_like_delta_commands_but_are_wired_directly_to_actuators"
    if topology == "direct_controller_to_actuator":
        return "controller_outputs_may_be_direct_actuator_commands"
    return "unknown"


def scenario_profile(path_text: str) -> dict[str, Any]:
    scenario_path = repo_path(path_text)
    config = read_yaml(scenario_path)
    result = config.get("result", {})
    if not isinstance(result, dict):
        result = {}
    controller = config.get("controller", {})
    if not isinstance(controller, dict):
        controller = {}
    raw_file = repo_path(result.get("raw_file", ""))
    metrics_file = repo_path(result.get("metrics_file", ""))
    controller_file = repo_path(controller.get("sysblock_controller_file", ""))
    model_file = resolve_model_file(config)
    topology = classify_topology(model_file)
    stats = command_stats(raw_file)
    output_limit = controller_output_limit(controller_file)
    metrics = read_json(metrics_file) if metrics_file.exists() else {}
    semantics = infer_semantics(topology["topology"], stats, output_limit)
    return {
        "scenario": rel(scenario_path),
        "experiment_id": config.get("experiment_id"),
        "controller_id": config.get("controller_id"),
        "model_name": (config.get("model", {}) or {}).get("model_name") if isinstance(config.get("model", {}), dict) else "",
        "controller_file": rel(controller_file),
        "controller_output_limit": output_limit,
        "topology": topology,
        "command_stats": stats,
        "quality_status": metrics.get("quality_status"),
        "quality_pass": metrics.get("quality_pass"),
        "position_rmse_m": metrics.get("position_rmse_m"),
        "total_health_score": metrics.get("total_health_score"),
        "inferred_command_semantics": semantics,
        "candidate_action": "restore_or_standardize_hover_command_mapper"
        if semantics == "controller_outputs_look_like_delta_commands_but_are_wired_directly_to_actuators"
        else "retain_current_topology_for_controller_tuning",
    }


def build_profile(paths: list[str]) -> dict[str, Any]:
    profiles = [scenario_profile(path) for path in paths]
    direct_delta = [
        item
        for item in profiles
        if item["inferred_command_semantics"] == "controller_outputs_look_like_delta_commands_but_are_wired_directly_to_actuators"
    ]
    hover_mapped = [
        item
        for item in profiles
        if item["inferred_command_semantics"] == "controller_outputs_delta_commands_mapped_to_hover_actuator_domain"
    ]
    return {
        "schema": "mosim.mworks.rotor1_loss15_command_semantics.v1",
        "status": "diagnostic_profile_ready",
        "static_read_only": True,
        "live_mworks_touched": False,
        "scenario_count": len(profiles),
        "direct_delta_mismatch_count": len(direct_delta),
        "hover_mapped_count": len(hover_mapped),
        "profiles": profiles,
        "recommended_next_steps": [
            "Treat Sysblock y/y1/y2/y3 outputs with output_limit around +/-20 as delta-like motor commands unless a controller proves otherwise.",
            "For direct-controller-to-actuator rotor-loss P1-B models with delta-like command traces, restore or standardize a hover command mapper before retuning gains.",
            "After each topology change, run a short smoke simulation first, then the 50 s scenario, then refresh candidate matrix and closeout gate.",
            "Do not enter UE replay/rendering until a current accepted rotor1_loss15 candidate exists.",
        ],
        "claim_boundary": [
            "This profile reads source and existing raw/metrics only.",
            "It does not prove a new live MWORKS run.",
            "It is diagnostic evidence for choosing the next single-UAV iteration, not controller acceptance.",
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, profile: dict[str, Any]) -> None:
    lines = [
        "# Rotor1 Loss15 Command Semantics Profile",
        "",
        f"Status: `{profile['status']}`",
        f"Direct/delta mismatch count: `{profile['direct_delta_mismatch_count']}`",
        f"Hover-mapped count: `{profile['hover_mapped_count']}`",
        "",
        "Read-only diagnostic profile. It does not run MWORKS.",
        "",
        "## Scenario Profiles",
        "",
        "| Controller | Topology | Inferred Semantics | Abs Cmd Max | Final Z Error | Quality | Action |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for item in profile["profiles"]:
        stats = item["command_stats"]
        lines.append(
            "| {controller} | {topology} | {semantics} | {absmax} | {zerr} | {quality} | {action} |".format(
                controller=item["controller_id"],
                topology=item["topology"]["topology"],
                semantics=item["inferred_command_semantics"],
                absmax="" if stats.get("command_abs_max") is None else f"{float(stats['command_abs_max']):.3f}",
                zerr="" if stats.get("final_z_error_m") is None else f"{float(stats['final_z_error_m']):.3f}",
                quality=item["quality_status"],
                action=item["candidate_action"],
            )
        )
    lines.extend(["", "## Recommended Next Steps", ""])
    lines.extend(f"- {item}" for item in profile["recommended_next_steps"])
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in profile["claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenarios", nargs="*", default=SCENARIOS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    profile = build_profile(args.scenarios)
    write_json(output_dir / "rotor1_loss15_command_semantics.json", profile)
    write_markdown(output_dir / "rotor1_loss15_command_semantics.md", profile)
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
