#!/usr/bin/env python3
"""Build a static storyboard plan for the final demo video.

The plan maps candidate evidence rows to a conservative video outline. It does
not record, render, encode, or accept the demo video.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATE_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)
DEFAULT_FIGURE_READINESS = (
    ROOT
    / "Results"
    / "static_audits"
    / "candidate_figure_readiness_20260610"
    / "candidate_figure_readiness_inventory.json"
)
DEFAULT_FINAL_ARTIFACT_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_artifacts_20260610"
    / "final_submission_artifact_manifest_check.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "demo_video_storyboard_plan_20260610"

SCENE_BLUEPRINTS = [
    {
        "scene_id": "S0-boundary-title",
        "title": "Scope and evidence boundary",
        "claim_families": [],
        "duration_s": 20,
        "allowed_narration": [
            "This demo is planned from static candidate evidence only.",
            "Final video recording and PMO acceptance are still pending.",
        ],
    },
    {
        "scene_id": "S1-official-pid-baseline",
        "title": "Official PID baseline across required scenes",
        "claim_families": ["official_baseline"],
        "duration_s": 45,
        "allowed_narration": [
            "Show baseline PID behavior for step, helix, and figure-8 scenes.",
            "Use saved raw data, metrics, replay, and figures as candidate evidence.",
        ],
    },
    {
        "scene_id": "S2-optimized-controller-comparison",
        "title": "Optimized controller comparison",
        "claim_families": ["optimized_controller"],
        "duration_s": 55,
        "allowed_narration": [
            "Compare optimized Sysblock controller candidates against official PID baseline.",
            "Discuss tracking RMSE and health-score changes from saved metrics only.",
        ],
    },
    {
        "scene_id": "S3-robustness-fault-safety",
        "title": "Robustness, fault tolerance, and safety filter",
        "claim_families": ["robustness", "fault_tolerance", "safety_filter"],
        "duration_s": 60,
        "allowed_narration": [
            "Show mass perturbation, wind gust, rotor degradation, and safety-filter candidate evidence.",
            "Keep boundary cases separate from completed pass cases.",
        ],
    },
    {
        "scene_id": "S4-formation-control",
        "title": "Leader-follower multi-UAV formation",
        "claim_families": ["multi_uav_formation"],
        "duration_s": 40,
        "allowed_narration": [
            "Show the triangle figure-8 formation candidate and its formation score.",
            "Describe this as saved Sysplorer/MWORKS candidate evidence, not live closed-loop acceptance.",
        ],
    },
    {
        "scene_id": "S5-visual-trajectory-review",
        "title": "Visual trajectory review assets",
        "claim_families": ["visual_trajectory_review"],
        "duration_s": 35,
        "allowed_narration": [
            "Show planar and helical figure-8 visual-review trajectory candidates.",
            "Do not claim UE build, runtime, editor, or final visual acceptance from these rows.",
        ],
    },
    {
        "scene_id": "S6-final-packaging-gates",
        "title": "Final packaging gates",
        "claim_families": [],
        "duration_s": 25,
        "allowed_narration": [
            "List remaining final artifacts: PDFs, demo video, and PMO acceptance packet.",
            "State that final submission readiness remains blocked until those artifacts exist and are reviewed.",
        ],
    },
]

FORBIDDEN_VIDEO_CLAIMS = [
    "final PMO acceptance",
    "final submission ready",
    "planner_ready",
    "closed_loop",
    "ROS2 controller handoff",
    "UE build/runtime/editor success",
    "native Syslab complete report generation",
    "live MWORKS no-start attach success",
    "final visual acceptance",
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def candidate_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("claim_slot", "")), str(row.get("experiment_id", ""))


def build_figure_lookup(figure_readiness: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in figure_readiness.get("candidate_rows", []):
        if isinstance(row, dict):
            lookup[candidate_key(row)] = row
    return lookup


def compact_row(row: dict[str, Any], figure_row: dict[str, Any] | None) -> dict[str, Any]:
    core_figures = figure_row.get("core_figures", {}) if isinstance(figure_row, dict) else {}
    primary_figures: list[str] = []
    if isinstance(core_figures, dict):
        for figure_kind in ("trajectory_xy", "position_error", "metrics_summary", "altitude_tracking"):
            values = core_figures.get(figure_kind, [])
            if isinstance(values, list) and values:
                primary_figures.append(str(values[0]))
    replay_files = figure_row.get("replay_files", []) if isinstance(figure_row, dict) else []
    log_files = figure_row.get("log_files", []) if isinstance(figure_row, dict) else []
    return {
        "claim_slot": row.get("claim_slot", ""),
        "experiment_id": row.get("experiment_id", ""),
        "scene_id": row.get("scene_id", ""),
        "controller_id": row.get("controller_id", ""),
        "claim_family": row.get("claim_family", ""),
        "quality_status": row.get("quality_status", ""),
        "position_rmse_m": row.get("position_rmse_m", ""),
        "total_health_score": row.get("total_health_score", ""),
        "formation_score": row.get("formation_score", ""),
        "metrics_file": row.get("metrics_file", ""),
        "raw_file": row.get("raw_file", ""),
        "primary_figures": primary_figures,
        "replay_files": replay_files if isinstance(replay_files, list) else [],
        "log_files": log_files if isinstance(log_files, list) else [],
        "claim_ceiling": row.get("claim_ceiling", ""),
    }


def build_storyboard(
    candidate_manifest_path: Path,
    figure_readiness_path: Path,
    final_artifact_manifest_path: Path,
) -> dict[str, Any]:
    candidate_manifest = read_json(candidate_manifest_path)
    figure_readiness = read_json(figure_readiness_path)
    final_artifact_manifest = read_json(final_artifact_manifest_path)

    candidates = [
        row for row in candidate_manifest.get("candidate_rows", [])
        if isinstance(row, dict)
    ]
    figure_lookup = build_figure_lookup(figure_readiness)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_figure_links: list[str] = []
    for row in candidates:
        key = candidate_key(row)
        figure_row = figure_lookup.get(key)
        if figure_row is None:
            missing_figure_links.append(str(row.get("claim_slot", "")))
        by_family[str(row.get("claim_family", ""))].append(compact_row(row, figure_row))

    scenes: list[dict[str, Any]] = []
    for index, blueprint in enumerate(SCENE_BLUEPRINTS, start=1):
        rows: list[dict[str, Any]] = []
        for family in blueprint["claim_families"]:
            rows.extend(by_family.get(family, []))
        scenes.append(
            {
                "order": index,
                "scene_id": blueprint["scene_id"],
                "title": blueprint["title"],
                "duration_s": blueprint["duration_s"],
                "claim_families": blueprint["claim_families"],
                "candidate_row_count": len(rows),
                "candidate_rows": rows,
                "allowed_narration": blueprint["allowed_narration"],
                "forbidden_claims": FORBIDDEN_VIDEO_CLAIMS,
                "recording_status": "not_recorded",
                "claim_boundary": "storyboard_only_not_demo_video_acceptance",
            }
        )

    demo_artifact = final_artifact_manifest.get("artifacts", {}).get("demo_video", {})
    demo_video_exists = bool(demo_artifact.get("exists"))
    storyboard_ready_for_review = (
        candidate_manifest.get("status") == "review_candidate_not_final_acceptance"
        and figure_readiness.get("status") == "static_figure_inventory_not_final_report_acceptance"
        and not missing_figure_links
        and len(candidates) > 0
    )

    return {
        "plan_id": "demo_video_storyboard_plan_20260610",
        "status": "storyboard_plan_not_demo_video_acceptance",
        "inputs": {
            "candidate_submission_evidence_manifest": rel(candidate_manifest_path),
            "candidate_figure_readiness_inventory": rel(figure_readiness_path),
            "final_submission_artifact_manifest": rel(final_artifact_manifest_path),
        },
        "summary": {
            "candidate_row_count": len(candidates),
            "scene_count": len(scenes),
            "storyboard_duration_s": sum(scene["duration_s"] for scene in scenes),
            "missing_figure_link_count": len(missing_figure_links),
            "storyboard_ready_for_review": storyboard_ready_for_review,
            "demo_video_exists": demo_video_exists,
            "safe_to_record_demo_video_now": False,
            "records_or_renders_video_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "scenes": scenes,
        "missing_figure_links": missing_figure_links,
        "forbidden_video_claims": FORBIDDEN_VIDEO_CLAIMS,
        "blockers": [
            {
                "blocker_id": "demo_video_not_recorded",
                "reason": "Results/submission/demo_video.mp4 is missing",
                "needed_action": "record or render the reviewed storyboard only after approval",
            },
            {
                "blocker_id": "manual_storyboard_review_required",
                "reason": "storyboard content must be reviewed before recording",
                "needed_action": "confirm scenes, wording, and evidence boundaries before producing video",
            },
        ],
        "claim_boundary": [
            "This artifact is a storyboard and recording checklist only.",
            "It does not record, render, encode, or create demo_video.mp4.",
            "It does not claim final PMO acceptance or final submission readiness.",
            "It does not prove ROS2 planner_ready, closed_loop, or UE runtime success.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Demo Video Storyboard Plan, 2026-06-10",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Summary",
        "",
        f"- Candidate rows: `{summary['candidate_row_count']}`",
        f"- Scenes: `{summary['scene_count']}`",
        f"- Planned duration: `{summary['storyboard_duration_s']} s`",
        f"- Missing figure links: `{summary['missing_figure_link_count']}`",
        f"- Storyboard ready for review: `{summary['storyboard_ready_for_review']}`",
        f"- Demo video exists: `{summary['demo_video_exists']}`",
        f"- Safe to record demo video now: `{summary['safe_to_record_demo_video_now']}`",
        f"- Records or renders video now: `{summary['records_or_renders_video_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Scenes", ""])
    for scene in plan["scenes"]:
        lines.extend(
            [
                f"### {scene['order']}. {scene['title']}",
                "",
                f"- Scene ID: `{scene['scene_id']}`",
                f"- Duration: `{scene['duration_s']} s`",
                f"- Candidate rows: `{scene['candidate_row_count']}`",
                f"- Recording status: `{scene['recording_status']}`",
                "- Allowed narration:",
            ]
        )
        for item in scene["allowed_narration"]:
            lines.append(f"  - {item}")
        if scene["candidate_rows"]:
            lines.append("- Evidence rows:")
            for row in scene["candidate_rows"]:
                metric = row["position_rmse_m"]
                score = row["total_health_score"]
                formation = row["formation_score"]
                details = f"rmse={metric}, health={score}"
                if formation != "":
                    details += f", formation={formation}"
                lines.append(
                    f"  - `{row['claim_slot']}` / `{row['experiment_id']}` ({details})"
                )
        lines.append("")
    lines.extend(["## Forbidden Video Claims", ""])
    for item in plan["forbidden_video_claims"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Blockers", ""])
    for blocker in plan["blockers"]:
        lines.append(
            f"- `{blocker['blocker_id']}`: {blocker['reason']} Needed action: {blocker['needed_action']}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-manifest", default=str(DEFAULT_CANDIDATE_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--figure-readiness", default=str(DEFAULT_FIGURE_READINESS.relative_to(ROOT)))
    parser.add_argument("--artifact-manifest", default=str(DEFAULT_FINAL_ARTIFACT_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_storyboard(
        repo_path(args.candidate_manifest),
        repo_path(args.figure_readiness),
        repo_path(args.artifact_manifest),
    )
    json_path = output_dir / "demo_video_storyboard_plan.json"
    md_path = output_dir / "demo_video_storyboard_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "plan_json": rel(json_path),
                "plan_markdown": rel(md_path),
                "storyboard_ready_for_review": plan["summary"]["storyboard_ready_for_review"],
                "safe_to_record_demo_video_now": plan["summary"]["safe_to_record_demo_video_now"],
                "records_or_renders_video_now": plan["summary"]["records_or_renders_video_now"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
