#!/usr/bin/env python3
"""Generate MWORKS smoke models from accepted UE navigation/control handoffs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
SOURCE_MODEL = ROOT / "Models/QuadrotorExperiments/Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop.mo"
MODEL_DIR = ROOT / "Models/QuadrotorExperiments"
SCENARIO_DIR = ROOT / "Config/scenarios/planning"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


SCENE_MODEL_NAMES = {
    "factoryenvironmentcollect": "Sunray150UEFactoryLinearMPCSysblockSmoke",
    "derelictcorridormegascans": "Sunray150UEDerelictLinearMPCSysblockSmoke",
}


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


def fmt(value: float) -> str:
    if abs(value) < 5e-13:
        value = 0.0
    return f"{value:.12g}"


def modelica_array(values: list[float], *, per_line: int = 6) -> str:
    chunks = []
    for index in range(0, len(values), per_line):
        chunks.append(", ".join(fmt(float(value)) for value in values[index : index + per_line]))
    if len(chunks) == 1:
        return "{" + chunks[0] + "}"
    return "{\n      " + ",\n      ".join(chunks) + "}"


def replace_one(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"replacement failed for {label}: {count}")
    return new_text


def reference_constructor(name: str, params: dict[str, Any]) -> str:
    return f"""  {name}(
    n_segments = {int(params["n_segments"])},
    p_x = {modelica_array(params["p_x"])},
    p_y = {modelica_array(params["p_y"])},
    p_z = {modelica_array(params["p_z"])},
    segment_duration = {modelica_array(params["segment_duration"])}"""


def display_constructor(params: dict[str, Any]) -> str:
    points = params["unpadded_points_m"]
    x_values = [float(point[0]) for point in points]
    y_values = [float(point[1]) for point in points]
    margin = 8.0
    base = reference_constructor("PlanningNavigationDisplay navigationDisplay", params)
    return f"""{base},
    x_min = {fmt(min(x_values) - margin)},
    x_max = {fmt(max(x_values) + margin)},
    y_min = {fmt(min(y_values) - margin)},
    y_max = {fmt(max(y_values) + margin)},
    boundary_line_diameter_m = 0.0,
    render_boundary_walls = false,
    boundary_wall_height_m = 0.0,
    boundary_wall_thickness_m = 0.0,
    highlight_local_costmap = true,
    local_costmap_radius_m = 6.0,
    local_costmap_fade_radius_m = 9.0,
    local_costmap_front_half_angle_rad = 3.141592653589793,
    local_costmap_update_period_s = 0.05,
    local_costmap_half_cells = 18,
    local_costmap_cell_size_m = 0.5,
    local_sensed_cell_size_m = 0.5,
    local_sensed_half_cells = 18,
    local_plan_horizon_s = 4.0,
    local_plan_point_count = 12,
    local_plan_max_length_m = 4.0,
    render_terrain_blocks = false,
    show_static_map_mesh = false,
    show_static_map_layers = false,
    show_continuous_ground = false,
    max_pillars = 1,
    pillar_count = 0,
    pillar_center = {{{{0.0, 0.0}}}},
    pillar_length = {{0.16}},
    pillar_width = {{0.16}},
    pillar_height = {{1.0}},
    pillar_z_min = {{0.0}},
    max_wall_groups = 1,
    wall_group_count = 0,
    wall_arm1_min = {{{{0.0, 0.0, 0.0}}}},
    wall_arm1_max = {{{{0.0, 0.0, 0.0}}}},
    wall_arm2_min = {{{{0.0, 0.0, 0.0}}}},
    wall_arm2_max = {{{{0.0, 0.0, 0.0}}}})"""


def build_model(scene_id: str, scene_dir: Path, model_name: str) -> dict[str, Any]:
    params = json.loads((scene_dir / "planned_quintic_reference_params.json").read_text(encoding="utf-8"))
    handoff = json.loads((scene_dir / "navigation_control_handoff.json").read_text(encoding="utf-8"))
    source_text = SOURCE_MODEL.read_text(encoding="utf-8")
    source_name = "Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop"
    text = source_text.replace(f"model {source_name}", f"model {model_name}", 1)
    text = text.replace(f"end {source_name};", f"end {model_name};", 1)
    text = replace_one(
        text,
        r'  "Sunray150 single-UAV A\* obstacle-avoidance reference tracked by the LinearMPC-style Sysblock controller"',
        f'  "Sunray150 UE accepted scene smoke reference for {scene_id}; control interface only"',
        "description",
    )
    text = replace_one(
        text,
        r"  PlannedQuinticReference planningReference\([\s\S]*?\);\n  PlanningNavigationDisplay navigationDisplay\([\s\S]*?\);",
        reference_constructor("PlannedQuinticReference planningReference", params)
        + ");\n"
        + display_constructor(params)
        + ";",
        "reference and navigation display",
    )
    start = params["unpadded_points_m"][0]
    text = replace_one(
        text,
        r"body\(color = \{135, 206, 235\}, r_0\(start = \{[^}]+\}, fixed = \{true, true, true\}\)\)",
        f"body(color = {{135, 206, 235}}, r_0(start = {{{fmt(float(start[0]))}, {fmt(float(start[1]))}, {fmt(float(start[2]))}}}, fixed = {{true, true, true}}))",
        "body start",
    )
    text = replace_one(
        text,
        r"annotation\(experiment\(Algorithm = Dassl, StartTime = 0, StopTime = [^,]+, Tolerance = 0.0001, Interval = [^)]+\)\);",
        f"annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = {fmt(float(params['stop_time_s']))}, Tolerance = 0.0001, Interval = 0.05));",
        "experiment annotation",
    )
    output_model = MODEL_DIR / f"{model_name}.mo"
    output_model.write_text(text, encoding="utf-8")

    scenario = SCENARIO_DIR / f"sunray150_ue_{scene_id}_linear_mpc_smoke.yaml"
    scenario.write_text(
        "\n".join([
            f"experiment_id: sunray150_ue_{scene_id}_linear_mpc_smoke",
            f"scene_id: ue_{scene_id}",
            "controller_id: linear_mpc_sysblock",
            "priority: P1",
            "active: false",
            "inactive_reason: Generated controller-interface smoke scenario; use as smoke evidence only, not as a final performance scenario.",
            "evidence_level: real_sysplorer_mcp_ue_scene_control_smoke",
            "",
            "model:",
            "  source_package: QuadrotorExperiments",
            f"  model_name: QuadrotorExperiments.{model_name}",
            f"  model_path_hint: {rel(output_model)}",
            "  base_model_path_hint: References/MWORKS/QuadrotorModel/package.mo",
            "  extra_model_files:",
            "    - Models/QuadrotorExperiments/PlannedQuinticReference.mo",
            "    - Models/QuadrotorExperiments/PlanningNavigationDisplay.mo",
            "",
            "controller:",
            "  params_file: Config/controllers/linear_mpc_sysblock/default.yaml",
            "  replacement_component: controller3_2",
            "  require_baseline_improvement: false",
            "  sysblock_controller_file: Models/QuadrotorControllerBlocks/AWFF_LinearMPCOuterLoopControllerEquation_Sysblock.mo",
            "  graphical_sysblock_model: AWFF_InnovationGraphicalControllers.AWFF_LinearMPCControllerGraphical_Sysblock",
            "  graphical_sysblock_file: Models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
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
            f"  file: {rel(scene_dir / 'control_reference.csv')}",
            f"  navigation_handoff: {rel(scene_dir / 'navigation_control_handoff.json')}",
            f"  modelica_params: {rel(scene_dir / 'planned_quintic_reference_params.json')}",
            "",
            "planning_acceptance:",
            "  require_collision_free: true",
            "  global_truth_available_to_planner: false",
            f"  planner_policy: {handoff['truth_policy']['planner_policy']}",
            f"  local_plan_frames: {handoff['local_plan_frames']['path']}",
            f"  local_known_map_frames: {handoff['local_known_map_frames']['path']}",
            "",
            "result:",
            f"  raw_file: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/raw/sunray150_ue_{scene_id}_linear_mpc_smoke.csv",
            f"  metrics_file: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/metrics/sunray150_ue_{scene_id}_linear_mpc_smoke.json",
            f"  figure_dir: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/figures",
            f"  mcp_log: Results/unreal_scene_mapping/{scene_id}/mworks_smoke/logs/sysplorer_sunray150_ue_{scene_id}_linear_mpc_smoke.jsonl",
            "  variable_overrides:",
            "    x_ref: planningReference.position_command[1]",
            "    y_ref: planningReference.position_command[2]",
            "    z_ref: planningReference.position_command[3]",
            "  extra_variables:",
            "    z_ref_rate: planningReference.z_ref_rate",
            "    yaw_ref: planningReference.yaw_ref",
        ]) + "\n",
        encoding="utf-8",
    )
    return {
        "scene_id": scene_id,
        "model_name": f"QuadrotorExperiments.{model_name}",
        "model_file": rel(output_model),
        "scenario_file": rel(scenario),
        "n_segments": params["n_segments"],
        "stop_time_s": params["stop_time_s"],
    }


def update_package_order(model_names: list[str]) -> None:
    path = MODEL_DIR / "package.order"
    names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    changed = False
    for name in model_names:
        if name not in names:
            names.append(name)
            changed = True
    if changed:
        path.write_text("\n".join(names) + "\n", encoding="utf-8")


def write_status(output_root: Path, reports: list[dict[str, Any]]) -> None:
    lines = [
        "# MWORKS UE Scene Smoke Status",
        "",
        "Generated models consume accepted UE scene navigation references through `PlannedQuinticReference`.",
        "They are controller-interface smoke models, not final performance scenarios.",
        "",
        "| Scene | Model | Segments | Stop Time | MCP Evidence | Quality | Raw / Metrics |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for report in reports:
        scene_dir = output_root / report["scene_id"]
        smoke_dir = scene_dir / "mworks_smoke"
        raw = smoke_dir / "raw" / f"sunray150_ue_{report['scene_id']}_linear_mpc_smoke.csv"
        metrics = smoke_dir / "metrics" / f"sunray150_ue_{report['scene_id']}_linear_mpc_smoke.json"
        log = smoke_dir / "logs" / f"sysplorer_sunray150_ue_{report['scene_id']}_linear_mpc_smoke.jsonl"
        evidence = "check_model+simulate_model passed" if raw.exists() and metrics.exists() and log.exists() else "pending MCP smoke export"
        quality = "pending"
        if metrics.exists():
            try:
                payload = json.loads(metrics.read_text(encoding="utf-8"))
                quality = str(payload.get("quality_status", "unknown"))
            except json.JSONDecodeError:
                quality = "metrics_json_error"
        lines.append(
            f"| `{report['scene_id']}` | `{report['model_name']}` | "
            f"{report['n_segments']} | {fmt(float(report['stop_time_s']))} | "
            f"{evidence} | `{quality}` | "
            f"`{rel(raw)}` / `{rel(metrics)}` |"
        )
    lines.extend([
        "",
        "Use these outputs to verify that each accepted UE scene can drive the MWORKS controller interface.",
        "Do not report them as completed autonomous navigation or FAST-LIO localization evidence.",
    ])
    (output_root / "MWORKS_UE_SCENE_SMOKE_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = project_path(args.output_root)
    scene_ids = args.scene or list(DEFAULT_SCENES)
    reports = []
    for scene_id in scene_ids:
        key = scene_id.lower()
        model_name = SCENE_MODEL_NAMES[key]
        report = build_model(key, output_root / key, model_name)
        reports.append(report)
        print(f"{report['model_name']}: segments={report['n_segments']} stop_time={fmt(float(report['stop_time_s']))}")
    update_package_order([SCENE_MODEL_NAMES[scene_id.lower()] for scene_id in scene_ids])
    write_status(output_root, reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
