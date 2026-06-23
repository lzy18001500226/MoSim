#!/usr/bin/env python3
"""Validate UE scene-truth, replay, and accepted-run handoff contracts.

This is a static/file evidence gate. It does not start Unreal, MWORKS, ROS2,
Gazebo, RViz, FAST-LIO, sockets, or GUI actions.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPING_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")
DEFAULT_ACCEPTED_RUN_DIR = (
    ROOT
    / "Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation"
)


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {rel(path)}")
    return payload


def non_empty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def csv_headers(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        return next(reader, [])


def jsonl_lines(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row must be an object: {rel(path)}")
        rows.append(value)
    return rows


def resolve_artifact(value: Any) -> Path:
    if not isinstance(value, str) or not value:
        return ROOT / "__missing_artifact__"
    return repo_path(value)


def add_missing_file_issue(issues: list[str], label: str, path: Path) -> None:
    if not non_empty(path):
        issues.append(f"missing_or_empty:{label}:{rel(path)}")


def validate_readiness(mapping_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    path = mapping_root / "UE_SCENE_RUNTIME_READINESS.json"
    data = read_json(path)
    if data.get("schema") != "mosim.unreal_scene_runtime_readiness.v1":
        issues.append("runtime_readiness_schema_mismatch")
    overall = data.get("overall") if isinstance(data.get("overall"), dict) else {}
    policy = data.get("window_policy") if isinstance(data.get("window_policy"), dict) else {}
    if overall.get("file_loop_ready") is not True:
        issues.append("runtime_readiness_file_loop_not_ready")
    if policy.get("html_allowed_as_active_pointcloud_window") is not False:
        issues.append("runtime_readiness_html_pointcloud_must_be_false")
    if policy.get("global_truth_used_by_planner") is not False:
        issues.append("runtime_readiness_global_truth_used_by_planner")
    if overall.get("runtime_ready") is True:
        warnings.append("runtime_ready_true_requires_live_evidence_review")
    boundary = "\n".join(str(item) for item in data.get("claim_boundary", []))
    for required in [
        "preflight report",
        "not a new simulation result",
        "FAST-LIO localization remains unclaimed",
    ]:
        if required not in boundary:
            issues.append(f"runtime_readiness_missing_boundary:{required}")
    return data, issues, warnings


def validate_scene(mapping_root: Path, scene_id: str) -> dict[str, Any]:
    scene_dir = mapping_root / scene_id
    issues: list[str] = []
    warnings: list[str] = []

    planner_path = scene_dir / "planner_summary.json"
    occupancy_path = scene_dir / "occupancy_grid.json"
    runtime_bundle_path = scene_dir / "runtime_review_bundle.json"
    collision_path = scene_dir / "mworks_smoke/collision/mworks_scene_truth_collision.json"

    for label, path in [
        ("planner_summary", planner_path),
        ("occupancy_grid", occupancy_path),
        ("runtime_review_bundle", runtime_bundle_path),
        ("mworks_scene_truth_collision", collision_path),
    ]:
        add_missing_file_issue(issues, label, path)
    if issues:
        return {"scene_id": scene_id, "ok": False, "issues": issues, "warnings": warnings}

    planner = read_json(planner_path)
    occupancy = read_json(occupancy_path)
    runtime_bundle = read_json(runtime_bundle_path)
    collision = read_json(collision_path)

    if planner.get("schema") != "mosim.ue_scene_mapping_summary.v1":
        issues.append("planner_summary_schema_mismatch")
    if planner.get("scene_id") != scene_id:
        issues.append("planner_summary_scene_id_mismatch")
    if planner.get("global_truth_available_to_planner") is not False:
        issues.append("planner_global_truth_must_be_false")
    if planner.get("collision_free_against_truth") is not True:
        issues.append("planner_collision_free_against_truth_not_true")
    if planner.get("buffered_collision_free_against_truth") is not True:
        issues.append("planner_buffered_collision_free_not_true")
    path_cells = int(planner.get("path_cells") or 0)
    if path_cells <= 0:
        issues.append("planner_path_cells_not_positive")
    if int(planner.get("merged_lidar_point_count") or 0) <= 0:
        issues.append("planner_lidar_points_not_positive")

    if occupancy.get("schema") != "mosim.ue_scene_occupancy.v1":
        issues.append("occupancy_schema_mismatch")
    if occupancy.get("scene_id") != scene_id:
        issues.append("occupancy_scene_id_mismatch")
    grid = occupancy.get("grid") if isinstance(occupancy.get("grid"), dict) else {}
    occupied = grid.get("occupied_cells_xy") if isinstance(grid.get("occupied_cells_xy"), list) else []
    summary = occupancy.get("summary") if isinstance(occupancy.get("summary"), dict) else {}
    if summary.get("occupied_cell_count") != len(occupied):
        issues.append("occupancy_count_mismatch")
    if str(occupancy.get("frame", "")) != "mworks_world":
        issues.append("occupancy_frame_must_be_mworks_world")

    outputs = planner.get("outputs") if isinstance(planner.get("outputs"), dict) else {}
    artifacts = {
        "render_replay_csv": resolve_artifact(outputs.get("render_replay_csv")),
        "local_known_map_jsonl": resolve_artifact(outputs.get("local_known_map_jsonl")),
        "local_plan_jsonl": resolve_artifact(outputs.get("local_plan_jsonl")),
        "lidar_point_frames_jsonl": resolve_artifact(outputs.get("lidar_point_frames_jsonl")),
        "merged_pointcloud_ply": resolve_artifact(outputs.get("merged_pointcloud_ply")),
    }
    for label, path in artifacts.items():
        add_missing_file_issue(issues, label, path)

    fastlio_replay = scene_dir / "fastlio_replay_dataset.jsonl"
    add_missing_file_issue(issues, "fastlio_replay_dataset_jsonl", fastlio_replay)

    if non_empty(artifacts["render_replay_csv"]):
        required_columns = {
            "time",
            "x",
            "y",
            "z",
            "x_ref",
            "y_ref",
            "z_ref",
            "roll",
            "pitch",
            "yaw",
            "u1",
            "u2",
            "u3",
            "u4",
        }
        headers = set(csv_headers(artifacts["render_replay_csv"]))
        if not required_columns <= headers:
            issues.append("render_replay_missing_required_columns")
        if count_csv_rows(artifacts["render_replay_csv"]) != path_cells:
            issues.append("render_replay_row_count_mismatch")

    frame_counts: dict[str, int] = {}
    for label in ["local_known_map_jsonl", "local_plan_jsonl", "lidar_point_frames_jsonl"]:
        path = artifacts[label]
        if not non_empty(path):
            continue
        frames = jsonl_lines(path)
        frame_counts[label] = len(frames)
        if len(frames) != path_cells:
            issues.append(f"{label}_count_mismatch")
        if not frames:
            issues.append(f"{label}_empty")
            continue
        first = frames[0]
        if first.get("evidence_backed") is not True:
            issues.append(f"{label}_first_frame_not_evidence_backed")
        if first.get("render_only") is not False:
            issues.append(f"{label}_first_frame_render_only_not_false")
        if label == "local_plan_jsonl" and first.get("global_truth_available_to_planner") is not False:
            issues.append("local_plan_global_truth_must_be_false")
        if label == "lidar_point_frames_jsonl" and not first.get("points_m"):
            issues.append("lidar_point_frame_missing_points")

    if runtime_bundle.get("schema") != "mosim.ue_scene_runtime_bundle.v1":
        issues.append("runtime_bundle_schema_mismatch")
    policy = runtime_bundle.get("window_policy") if isinstance(runtime_bundle.get("window_policy"), dict) else {}
    if policy.get("html_allowed_as_active_pointcloud_window") is not False:
        issues.append("runtime_bundle_html_pointcloud_must_be_false")
    if policy.get("global_truth_used_by_planner") is not False:
        issues.append("runtime_bundle_global_truth_used_by_planner")
    rb_counts = runtime_bundle.get("counts") if isinstance(runtime_bundle.get("counts"), dict) else {}
    for key in ["render_replay_frames", "local_known_map_frames", "local_plan_frames", "lidar_point_frames"]:
        if int(rb_counts.get(key) or -1) != path_cells:
            issues.append(f"runtime_bundle_count_mismatch:{key}")
    bundle_boundary = "\n".join(str(item) for item in runtime_bundle.get("claim_boundary", []))
    if "not proof that runtime already ran" not in bundle_boundary:
        issues.append("runtime_bundle_missing_runtime_not_proof_boundary")
    if "FAST-LIO localization remains unclaimed" not in bundle_boundary:
        issues.append("runtime_bundle_missing_fastlio_unclaimed_boundary")

    if collision.get("schema") != "mosim.mworks_ue_scene_truth_collision_check.v1":
        issues.append("collision_schema_mismatch")
    if collision.get("pass") is not True:
        issues.append("mworks_scene_truth_collision_not_pass")
    actual = collision.get("actual") if isinstance(collision.get("actual"), dict) else {}
    reference = collision.get("reference") if isinstance(collision.get("reference"), dict) else {}
    if actual.get("collision_free_against_truth") is not True:
        issues.append("actual_collision_free_not_true")
    if reference.get("collision_free_against_truth") is not True:
        issues.append("reference_collision_free_not_true")

    return {
        "scene_id": scene_id,
        "ok": not issues,
        "status": "ue_truth_replay_static_contract_ready" if not issues else "ue_truth_replay_contract_failed",
        "issues": issues,
        "warnings": warnings,
        "counts": {
            "path_cells": path_cells,
            "lidar_points": int(planner.get("merged_lidar_point_count") or 0),
            **frame_counts,
        },
        "artifacts": {
            "planner_summary": rel(planner_path),
            "occupancy_grid": rel(occupancy_path),
            "runtime_review_bundle": rel(runtime_bundle_path),
            "mworks_scene_truth_collision": rel(collision_path),
            "render_replay_csv": rel(artifacts["render_replay_csv"]),
            "local_known_map_jsonl": rel(artifacts["local_known_map_jsonl"]),
            "local_plan_jsonl": rel(artifacts["local_plan_jsonl"]),
            "lidar_point_frames_jsonl": rel(artifacts["lidar_point_frames_jsonl"]),
            "pointcloud_merged_ply": rel(artifacts["merged_pointcloud_ply"]),
            "fastlio_replay_dataset_jsonl": rel(fastlio_replay),
        },
    }


def validate_accepted_run(accepted_run_dir: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    bundle_path = accepted_run_dir / "ue_replay_input_bundle.json"
    loopback_path = accepted_run_dir / "ue_state_stream_loopback.json"
    runtime_probe_path = accepted_run_dir / "ue_runtime_probe_20260612_1105/ue_runtime_replay_probe_summary.json"
    for label, path in [
        ("ue_replay_input_bundle", bundle_path),
        ("ue_state_stream_loopback", loopback_path),
    ]:
        add_missing_file_issue(issues, label, path)
    if issues:
        return {"ok": False, "issues": issues, "warnings": warnings}

    bundle = read_json(bundle_path)
    loopback = read_json(loopback_path)
    if bundle.get("schema") != "mosim.ue_replay_input_bundle.v1":
        issues.append("accepted_bundle_schema_mismatch")
    if bundle.get("status") != "ready_for_source_static_ue_replay_input":
        issues.append("accepted_bundle_status_not_ready")
    for flag in ["source_static_only"]:
        if bundle.get(flag) is not True:
            issues.append(f"accepted_bundle_{flag}_must_be_true")
    for flag in ["ue_editor_opened", "ue_runtime_started", "udp_sent"]:
        if bundle.get(flag) is not False:
            issues.append(f"accepted_bundle_{flag}_must_be_false")
    candidate = bundle.get("accepted_candidate") if isinstance(bundle.get("accepted_candidate"), dict) else {}
    if candidate.get("quality_status") != "pass":
        issues.append("accepted_candidate_quality_not_pass")
    scene_binding = bundle.get("scene_binding") if isinstance(bundle.get("scene_binding"), dict) else {}
    if scene_binding.get("map_id") != "local_factoryenvironmentcollect":
        issues.append("accepted_bundle_map_id_mismatch")
    raw = bundle.get("artifacts", {}).get("raw", {}) if isinstance(bundle.get("artifacts"), dict) else {}
    if int(raw.get("row_count") or 0) <= 0:
        issues.append("accepted_bundle_raw_row_count_not_positive")
    forbidden = "\n".join(str(item) for item in bundle.get("forbidden_claims", []))
    for term in ["UE runtime success", "planner_ready", "multi-UAV formation readiness"]:
        if term not in forbidden:
            issues.append(f"accepted_bundle_missing_forbidden_claim:{term}")

    if loopback.get("schema") != "mosim.mworks_accepted_run_ue_state_stream_loopback.v1":
        issues.append("loopback_schema_mismatch")
    if loopback.get("ok") is not True:
        issues.append("loopback_not_ok")
    if loopback.get("not_runtime_ue_ack") is not True:
        issues.append("loopback_must_not_be_runtime_ack")
    for flag in ["ue_editor_opened", "ue_runtime_started", "mworks_started", "ros2_started"]:
        if loopback.get(flag) is not False:
            issues.append(f"loopback_{flag}_must_be_false")
    if int(loopback.get("received_frames") or 0) <= 0:
        issues.append("loopback_received_frames_not_positive")

    runtime_probe: dict[str, Any] | None = None
    if runtime_probe_path.exists():
        runtime_probe = read_json(runtime_probe_path)
        if runtime_probe.get("schema") != "mosim.ue_runtime_replay_probe_summary.v1":
            issues.append("runtime_probe_schema_mismatch")
        if runtime_probe.get("status") != "runtime_ingest_and_visual_uav_visible_pass":
            issues.append("runtime_probe_status_not_visible_pass")
        log = runtime_probe.get("ue_log_evidence") if isinstance(runtime_probe.get("ue_log_evidence"), dict) else {}
        for flag in [
            "factory_scene_visible",
            "udp_first_frame_received",
            "sunray_first_frame_applied",
            "sunray_visible",
            "sunray_bounds_nonzero",
        ]:
            if log.get(flag) is not True:
                issues.append(f"runtime_probe_log_{flag}_not_true")
        if log.get("sunray_hidden_in_game") is not False:
            issues.append("runtime_probe_sunray_hidden_in_game_not_false")
        boundary = "\n".join(str(item) for item in runtime_probe.get("claim_boundary", []))
        for term in ["does not prove authoritative UE command echo ack", "FAST-LIO", "multi-UAV"]:
            if term not in boundary:
                issues.append(f"runtime_probe_missing_boundary:{term}")
    else:
        warnings.append(f"runtime_probe_summary_absent:{rel(runtime_probe_path)}")

    return {
        "ok": not issues,
        "status": "accepted_mworks_run_replay_contract_ready" if not issues else "accepted_run_contract_failed",
        "issues": issues,
        "warnings": warnings,
        "bundle": rel(bundle_path),
        "loopback": rel(loopback_path),
        "runtime_probe": rel(runtime_probe_path) if runtime_probe is not None else "",
        "accepted_candidate": {
            "scenario": candidate.get("scenario"),
            "controller_id": candidate.get("controller_id"),
            "position_rmse_m": candidate.get("position_rmse_m"),
            "total_health_score": candidate.get("total_health_score"),
        },
    }


def validate(mapping_root: Path, scenes: list[str], accepted_run_dir: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    readiness, readiness_issues, readiness_warnings = validate_readiness(mapping_root)
    issues.extend(readiness_issues)
    warnings.extend(readiness_warnings)
    scene_reports = [validate_scene(mapping_root, scene_id) for scene_id in scenes]
    accepted_run = validate_accepted_run(accepted_run_dir)
    for report in scene_reports:
        issues.extend(f"{report['scene_id']}:{issue}" for issue in report.get("issues", []))
        warnings.extend(f"{report['scene_id']}:{warning}" for warning in report.get("warnings", []))
    issues.extend(f"accepted_run:{issue}" for issue in accepted_run.get("issues", []))
    warnings.extend(f"accepted_run:{warning}" for warning in accepted_run.get("warnings", []))

    runtime_ready = bool(readiness.get("overall", {}).get("runtime_ready"))
    runtime_blockers = list(readiness.get("overall", {}).get("runtime_blockers", []))
    status = "ue_truth_replay_contract_failed"
    if not issues:
        status = "ue_truth_replay_contract_ready"
        if not runtime_ready:
            status = "ue_truth_replay_static_ready_runtime_blocked_or_degraded"

    return {
        "schema": "mosim.ue_truth_replay_contract_check.v1",
        "ok": not issues,
        "status": status,
        "mapping_root": rel(mapping_root),
        "scenes": scene_reports,
        "accepted_run": accepted_run,
        "runtime_ready": runtime_ready,
        "runtime_blockers": runtime_blockers,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker validates file-level UE truth/replay and accepted-run handoff contracts.",
            "It does not start UE, MWORKS, ROS2, Gazebo, RViz, FAST-LIO, sockets, or GUI actions.",
            "Static readiness does not prove planner_ready, closed_loop, FAST-LIO localization, Gazebo runtime success, final material acceptance, controller performance from UE, or multi-UAV readiness.",
            "MWORKS metrics remain the controller-performance source for the accepted single-UAV run.",
        ],
        "next_allowed_actions": [
            "Use the accepted run replay bundle for bounded UE render/replay work when that live scope is authorized.",
            "Use the scene truth artifacts as validation oracle and ROS2/Gazebo prep inputs, not as planner global-map input.",
            "Resolve ROS2/Gazebo runtime dependencies before claiming PointCloud2, local voxel/grid, or Gazebo runtime evidence.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# UE Truth Replay Contract Check",
        "",
        f"- status: `{report['status']}`",
        f"- ok: `{str(report['ok']).lower()}`",
        f"- runtime_ready: `{str(report['runtime_ready']).lower()}`",
        f"- runtime_blockers: {', '.join(f'`{item}`' for item in report['runtime_blockers']) or 'none'}",
        "",
        "## Scenes",
        "",
        "| Scene | OK | Path Cells | LiDAR Points | Status |",
        "|---|---:|---:|---:|---|",
    ]
    for scene in report["scenes"]:
        counts = scene.get("counts", {})
        lines.append(
            f"| `{scene['scene_id']}` | `{str(scene['ok']).lower()}` | "
            f"{counts.get('path_cells', 0)} | {counts.get('lidar_points', 0)} | "
            f"`{scene.get('status', '')}` |"
        )
    accepted = report["accepted_run"]
    candidate = accepted.get("accepted_candidate", {})
    lines.extend(
        [
            "",
            "## Accepted MWORKS Run",
            "",
            f"- status: `{accepted.get('status', '')}`",
            f"- controller: `{candidate.get('controller_id', '')}`",
            f"- scenario: `{candidate.get('scenario', '')}`",
            f"- position_rmse_m: `{candidate.get('position_rmse_m', '')}`",
            f"- total_health_score: `{candidate.get('total_health_score', '')}`",
            "",
            "## Boundary",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["claim_boundary"])
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- `{item}`" for item in report["issues"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- `{item}`" for item in report["warnings"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping-root", type=Path, default=DEFAULT_MAPPING_ROOT)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--accepted-run-dir", type=Path, default=DEFAULT_ACCEPTED_RUN_DIR)
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()

    try:
        report = validate(
            repo_path(args.mapping_root),
            [scene.lower() for scene in (args.scene or list(DEFAULT_SCENES))],
            repo_path(args.accepted_run_dir),
        )
    except Exception as exc:
        report = {
            "schema": "mosim.ue_truth_replay_contract_check.v1",
            "ok": False,
            "status": "ue_truth_replay_contract_exception",
            "mapping_root": rel(repo_path(args.mapping_root)),
            "scenes": [],
            "accepted_run": {},
            "runtime_ready": False,
            "runtime_blockers": [],
            "issues": [f"{exc.__class__.__name__}: {exc}"],
            "warnings": [],
            "claim_boundary": [],
            "next_allowed_actions": [],
        }

    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        write_markdown(repo_path(args.output_md), report)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
