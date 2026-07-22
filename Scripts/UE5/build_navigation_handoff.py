#!/usr/bin/env python3
"""Build a navigation/control handoff from accepted UE scene mapping outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")
MODEL_POINT_CAPACITY = 91
MODEL_SEGMENT_CAPACITY = 90
DEFAULT_REFERENCE_VELOCITY_M_S = 0.8
DEFAULT_MIN_SEGMENT_DURATION_S = 0.9
DEFAULT_REFERENCE_SAMPLE_DT_S = 0.05


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def fmt(value: float) -> str:
    if abs(value) < 5e-13:
        value = 0.0
    return f"{value:.12g}"


def modelica_array(values: list[float], *, per_line: int = 6) -> str:
    chunks = []
    for index in range(0, len(values), per_line):
        chunks.append(", ".join(fmt(value) for value in values[index : index + per_line]))
    if len(chunks) == 1:
        return "{" + chunks[0] + "}"
    return "{\n      " + ",\n      ".join(chunks) + "}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((b[axis] - a[axis]) ** 2 for axis in range(3)))


def heading(a: list[float], b: list[float], default: float = 0.0) -> float:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if abs(dx) + abs(dy) < 1e-9:
        return default
    return math.atan2(dy, dx)


def smoothstep(ratio: float) -> float:
    r = min(1.0, max(0.0, ratio))
    return 10.0 * r**3 - 15.0 * r**4 + 6.0 * r**5


def smoothstep_derivative(ratio: float, duration: float) -> float:
    r = min(1.0, max(0.0, ratio))
    return (30.0 * r**2 - 60.0 * r**3 + 30.0 * r**4) / max(duration, 1e-9)


def padded(values: list[float], capacity: int, pad_value: float) -> list[float]:
    if len(values) > capacity:
        raise ValueError(f"too many values for capacity {capacity}: {len(values)}")
    return values + [pad_value] * (capacity - len(values))


def build_reference_params(
    waypoints: list[dict[str, Any]],
    *,
    velocity_m_s: float = DEFAULT_REFERENCE_VELOCITY_M_S,
    min_segment_duration_s: float = DEFAULT_MIN_SEGMENT_DURATION_S,
) -> dict[str, Any]:
    points = [[float(value) for value in item["position_m"]] for item in waypoints]
    if len(points) < 2:
        raise ValueError("navigation handoff requires at least two waypoints")
    n_segments = len(points) - 1
    if n_segments > MODEL_SEGMENT_CAPACITY:
        raise ValueError(f"n_segments={n_segments} exceeds PlannedQuinticReference capacity {MODEL_SEGMENT_CAPACITY}")
    durations = [
        max(distance(a, b) / max(velocity_m_s, 1e-9), min_segment_duration_s)
        for a, b in zip(points[:-1], points[1:])
    ]
    return {
        "schema": "mosim.planned_quintic_reference_params.v1",
        "n_segments": n_segments,
        "point_count": len(points),
        "reference_velocity_m_s": velocity_m_s,
        "min_segment_duration_s": min_segment_duration_s,
        "stop_time_s": sum(durations),
        "p_x": padded([point[0] for point in points], MODEL_POINT_CAPACITY, points[-1][0]),
        "p_y": padded([point[1] for point in points], MODEL_POINT_CAPACITY, points[-1][1]),
        "p_z": padded([point[2] for point in points], MODEL_POINT_CAPACITY, points[-1][2]),
        "segment_duration": padded(durations, MODEL_SEGMENT_CAPACITY, 1.0),
        "unpadded_points_m": points,
        "unpadded_segment_duration_s": durations,
    }


def reference_samples(params: dict[str, Any], sample_dt_s: float) -> list[dict[str, Any]]:
    points = params["unpadded_points_m"]
    durations = params["unpadded_segment_duration_s"]
    rows: list[dict[str, Any]] = []
    elapsed = 0.0
    last_yaw = heading(points[0], points[1])
    for segment_index, (a, b, duration) in enumerate(zip(points[:-1], points[1:], durations)):
        yaw = heading(a, b, last_yaw)
        last_yaw = yaw
        sample_count = max(1, int(math.ceil(duration / sample_dt_s)))
        for sample_index in range(sample_count + 1):
            if segment_index > 0 and sample_index == 0:
                continue
            tau = min(duration, sample_index * sample_dt_s)
            ratio = tau / max(duration, 1e-9)
            alpha = smoothstep(ratio)
            rate = smoothstep_derivative(ratio, duration)
            position = [a[axis] + (b[axis] - a[axis]) * alpha for axis in range(3)]
            velocity = [(b[axis] - a[axis]) * rate for axis in range(3)]
            rows.append({
                "time": fmt(elapsed + tau),
                "x_ref": fmt(position[0]),
                "y_ref": fmt(position[1]),
                "z_ref": fmt(position[2]),
                "vx_ref": fmt(velocity[0]),
                "vy_ref": fmt(velocity[1]),
                "vz_ref": fmt(velocity[2]),
                "yaw_ref": fmt(yaw),
                "segment_index": segment_index,
            })
        elapsed += duration
    return rows


def write_control_interface_package(scene_dir: Path, handoff: dict[str, Any]) -> dict[str, Any]:
    params = build_reference_params(handoff["waypoints"])
    params_path = scene_dir / "planned_quintic_reference_params.json"
    reference_csv = scene_dir / "control_reference.csv"
    snippet_path = scene_dir / "planned_quintic_reference_constructor.mo.txt"
    scenario_path = scene_dir / "scenario_draft.yaml"
    package_path = scene_dir / "control_interface_package.json"

    params_path.write_text(json.dumps(params, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(
        reference_csv,
        ["time", "x_ref", "y_ref", "z_ref", "vx_ref", "vy_ref", "vz_ref", "yaw_ref", "segment_index"],
        reference_samples(params, DEFAULT_REFERENCE_SAMPLE_DT_S),
    )
    snippet_path.write_text(
        "PlannedQuinticReference planningReference(\n"
        f"    n_segments = {params['n_segments']},\n"
        f"    p_x = {modelica_array(params['p_x'])},\n"
        f"    p_y = {modelica_array(params['p_y'])},\n"
        f"    p_z = {modelica_array(params['p_z'])},\n"
        f"    segment_duration = {modelica_array(params['segment_duration'])});\n",
        encoding="utf-8",
    )

    scene_id = handoff["scene_id"]
    scenario_path.write_text(
        "\n".join([
            f"experiment_id: sunray150_ue_{scene_id}_linear_mpc_interface",
            f"scene_id: ue_{scene_id}",
            "controller_id: linear_mpc_sysblock",
            "priority: P1",
            "active: false",
            "inactive_reason: UE navigation/control interface package only; not yet integrated into a Sysplorer executable model.",
            "evidence_level: offline_ue_navigation_control_interface_package",
            "",
            "model:",
            "  source_package: MoSimQuadrotorModel",
            "  model_name: TBD.UEAcceptedSceneLinearMPCClosedLoop",
            "  base_model_path_hint: References/MWORKS/QuadrotorModel/package.mo",
            "  extra_model_files:",
            "    - Models/MoSimQuadrotorModel/Planning/Scenarios/PlannedQuinticReference.mo",
            "",
            "controller:",
            "  params_file: Config/controllers/linear_mpc_sysblock/default.yaml",
            "  replacement_component: controller3_2",
            "  require_baseline_improvement: false",
            "",
            "simulation:",
            "  start_time_s: 0.0",
            f"  stop_time_s: {fmt(float(params['stop_time_s']))}",
            "  step_size_s: 0.05",
            "  solver: Dassl",
            "  tolerance: 0.0001",
            "",
            "reference:",
            "  type: ue_scene_truth_planned_quintic",
            f"  navigation_handoff: {rel(scene_dir / 'navigation_control_handoff.json')}",
            f"  file: {rel(reference_csv)}",
            f"  modelica_params: {rel(params_path)}",
            f"  modelica_constructor: {rel(snippet_path)}",
            "",
            "planning_acceptance:",
            "  require_collision_free: true",
            "  global_truth_available_to_planner: false",
            f"  planner_policy: {handoff['truth_policy']['planner_policy']}",
            f"  local_plan_frames: {handoff['local_plan_frames']['path']}",
            f"  local_known_map_frames: {handoff['local_known_map_frames']['path']}",
            "",
            "result:",
            f"  raw_file: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/raw/sunray150_ue_{scene_id}_linear_mpc_interface.csv",
            f"  metrics_file: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/metrics/sunray150_ue_{scene_id}_linear_mpc_interface.json",
            f"  mcp_log: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/logs/sysplorer_sunray150_ue_{scene_id}_linear_mpc_interface.jsonl",
        ]) + "\n",
        encoding="utf-8",
    )

    package = {
        "schema": "mosim.control_interface_package.v1",
        "scene_id": scene_id,
        "status": "ready_for_mworks_reference_model_integration",
        "claim_boundary": [
            "This package converts accepted UE navigation output into controller-reference inputs.",
            "It is not a Sysplorer/MWORKS dynamics simulation result.",
            "The generated scenario is inactive until a concrete Sysplorer model consumes the PlannedQuinticReference parameters and passes MCP check/simulate gates.",
        ],
        "generated_outputs": {
            "control_reference_csv": rel(reference_csv),
            "planned_quintic_reference_params_json": rel(params_path),
            "planned_quintic_reference_constructor": rel(snippet_path),
            "scenario_draft_yaml": rel(scenario_path),
            "control_interface_package_json": rel(package_path),
        },
        "planned_quintic_reference": {
            "n_segments": params["n_segments"],
            "point_count": params["point_count"],
            "stop_time_s": params["stop_time_s"],
            "reference_velocity_m_s": params["reference_velocity_m_s"],
            "model_capacity": {
                "points": MODEL_POINT_CAPACITY,
                "segments": MODEL_SEGMENT_CAPACITY,
            },
        },
    }
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return package


def build_scene_handoff(scene_dir: Path) -> dict[str, Any]:
    planner = read_json(scene_dir / "planner_summary.json")
    trajectory = read_csv(scene_dir / "trajectory.csv")
    render_replay = read_csv(scene_dir / "render_replay.csv")
    local_plan_frames = read_jsonl(scene_dir / "local_plan_frames.jsonl")
    local_known_frames = read_jsonl(scene_dir / "local_known_map_frames.jsonl")
    fastlio_manifest = read_json(scene_dir / "fastlio_adapter_manifest.json")

    if planner.get("global_truth_available_to_planner") is not False:
        raise ValueError(f"planner truth policy violated: {scene_dir}")
    if planner.get("collision_free_against_truth") is not True:
        raise ValueError(f"planner collision validation failed: {scene_dir}")
    if planner.get("buffered_collision_free_against_truth") is not True:
        raise ValueError(f"planner buffered collision validation failed: {scene_dir}")
    if len(trajectory) != planner.get("path_cells"):
        raise ValueError(f"trajectory/planner length mismatch: {scene_dir}")
    if len(local_plan_frames) != len(trajectory):
        raise ValueError(f"local plan/trajectory length mismatch: {scene_dir}")

    waypoints = [
        {
            "index": int(row["index"]),
            "position_m": [float(row["x_m"]), float(row["y_m"]), float(row["z_m"])],
            "cell_xy": [int(row["cell_x"]), int(row["cell_y"])],
        }
        for row in trajectory
    ]
    replay_samples = [
        {
            "time_s": float(row["time"]),
            "position_m": [float(row["x"]), float(row["y"]), float(row["z"])],
            "reference_m": [float(row["x_ref"]), float(row["y_ref"]), float(row["z_ref"])],
            "yaw_rad": float(row["yaw"]),
        }
        for row in render_replay
    ]
    handoff = {
        "schema": "mosim.navigation_control_handoff.v1",
        "scene_id": planner["scene_id"],
        "status": "ready_for_mworks_controller_interface_smoke",
        "truth_policy": {
            "global_truth_available_to_planner": planner["global_truth_available_to_planner"],
            "collision_free_against_truth": planner["collision_free_against_truth"],
            "buffered_collision_free_against_truth": planner["buffered_collision_free_against_truth"],
            "control_tracking_buffer_cells": planner["control_tracking_buffer_cells"],
            "planner_policy": planner["planner_policy"],
        },
        "start_m": planner["start_m"],
        "goal_m": planner["goal_m"],
        "waypoints": waypoints,
        "render_replay_samples": replay_samples,
        "local_plan_frames": {
            "path": rel(scene_dir / "local_plan_frames.jsonl"),
            "count": len(local_plan_frames),
            "first_frame_source": local_plan_frames[0].get("source"),
        },
        "local_known_map_frames": {
            "path": rel(scene_dir / "local_known_map_frames.jsonl"),
            "count": len(local_known_frames),
        },
        "fastlio_adapter": {
            "path": rel(scene_dir / "fastlio_adapter_manifest.json"),
            "status": fastlio_manifest.get("status"),
            "ros1_ready": fastlio_manifest.get("ros_environment", {}).get("ros1_ready"),
        },
        "controller_interface_notes": [
            "This handoff is a navigation/planning interface artifact, not a dynamics-controller simulation result.",
            "MWORKS/Sysplorer control integration should consume waypoints/reference samples through a scenario-specific bridge and then produce native simulation evidence.",
            "The global occupancy grid must remain validation truth; do not feed it directly into an online planner/controller.",
            "The generated path must also pass buffered collision validation before MWORKS smoke integration.",
        ],
    }
    handoff["control_interface"] = write_control_interface_package(scene_dir, handoff)
    output = scene_dir / "navigation_control_handoff.json"
    output.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return handoff


def write_summary(output_root: Path, handoffs: list[dict[str, Any]]) -> None:
    lines = [
        "# Navigation Control Handoff Status",
        "",
        "| Scene | Status | Waypoints | Planner Truth | Control Buffer | FAST-LIO Adapter |",
        "|---|---|---:|---|---:|---|",
    ]
    for handoff in handoffs:
        truth = handoff["truth_policy"]
        lines.append(
            f"| `{handoff['scene_id']}` | `{handoff['status']}` | {len(handoff['waypoints'])} | "
            f"`global_truth_available_to_planner={str(truth['global_truth_available_to_planner']).lower()}`, "
            f"`collision_free_against_truth={str(truth['collision_free_against_truth']).lower()}`, "
            f"`buffered_collision_free_against_truth={str(truth['buffered_collision_free_against_truth']).lower()}` | "
            f"{truth['control_tracking_buffer_cells']} | "
            f"`{handoff['fastlio_adapter']['status']}` |"
        )
    lines.extend([
        "",
        "These files prepare controller-interface smoke work only. They are not MWORKS dynamics simulation evidence.",
        "Each scene directory also contains an inactive scenario draft plus PlannedQuinticReference parameters for later Sysplorer model integration.",
    ])
    (output_root / "NAVIGATION_HANDOFF_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = project_path(args.output_root)
    scene_ids = args.scene or list(DEFAULT_SCENES)
    handoffs = []
    for scene_id in scene_ids:
        handoff = build_scene_handoff(output_root / scene_id.lower())
        handoffs.append(handoff)
        print(f"{scene_id}: {handoff['status']} waypoints={len(handoff['waypoints'])}")
    write_summary(output_root, handoffs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
