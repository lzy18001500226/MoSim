#!/usr/bin/env python3
"""Build a sparse Factory L2 Gazebo-to-UE frame overlay.

This source/static helper creates a readable UE review surface for checking
whether the clean Gazebo Factory map is registered to the original UE Factory
scene. It intentionally avoids dense point overlays. The output is a small set
of structure bounding boxes and reference frames transformed through the same
Gazebo/MWORKS -> UE coordinate contract used by the clean Factory scene.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_PROFILE = ROOT / "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json"
DEFAULT_COORDINATE_AUDIT = (
    ROOT
    / "Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/FACTORY_L2_COORDINATE_AUDIT.json"
)
DEFAULT_SCENE_TRUTH = (
    ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
)
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"


COLORS = {
    "global": (1.0, 0.82, 0.05, 1.0),
    "ue_truth": (1.0, 0.0, 0.85, 1.0),
    "gazebo_projected": (0.0, 0.95, 1.0, 1.0),
    "near": (0.0, 0.9, 1.0, 1.0),
    "indoor": (1.0, 0.18, 0.92, 1.0),
    "pillar": (0.1, 1.0, 0.15, 1.0),
    "warning": (1.0, 0.45, 0.03, 1.0),
    "white": (1.0, 1.0, 1.0, 1.0),
}


SELECTED_ACTORS = [
    # Around the current review camera / outdoor Factory area.
    ("near_hangar_y120", "SM_Background2_Hangar3", "near"),
    ("near_box_tower_y125", "SM_Background2_BoxBuildingTower10", "near"),
    ("near_pipe_bridge_y147", "SM_Background2_Pipe13", "near"),
    ("near_tall_tower_y119", "SM_background1_15", "warning"),
    ("near_antenna_y136", "SM_Background1_AntennaTower4", "warning"),
    # Indoor/low-altitude recognizable obstacles used by planner review later.
    ("indoor_concrete_pillar_a", "SM_ConcretePillar25", "pillar"),
    ("indoor_concrete_pillar_b", "SM_ConcretePillar29", "pillar"),
    ("indoor_stair_platform", "SM_Stair_01", "indoor"),
    ("indoor_truck_tank", "SM_Truck_cabin_11", "indoor"),
    ("indoor_assembly_line", "SM_AssemblyLine4", "indoor"),
    ("indoor_metal_wall", "SM_MetalWall_6", "indoor"),
    ("indoor_air_platform", "SM_AirConditioningPlatform_01", "indoor"),
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def gazebo_to_unreal_cm(xyz_m: list[float] | tuple[float, float, float]) -> list[float]:
    x_m, y_m, z_m = xyz_m
    return [x_m * 100.0, -y_m * 100.0, z_m * 100.0]


def box_corners(min_m: list[float], max_m: list[float]) -> list[list[float]]:
    x0, y0, z0 = min_m
    x1, y1, z1 = max_m
    return [
        [x0, y0, z0],
        [x1, y0, z0],
        [x1, y1, z0],
        [x0, y1, z0],
        [x0, y0, z1],
        [x1, y0, z1],
        [x1, y1, z1],
        [x0, y1, z1],
    ]


def lerp(a: list[float], b: list[float], t: float) -> list[float]:
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]


def offset_z(point_m: list[float], z_offset_m: float) -> list[float]:
    return [point_m[0], point_m[1], point_m[2] + z_offset_m]


def append_segment_row(
    rows: list[dict[str, Any]],
    segment_id: str,
    plane: str,
    start_m: list[float],
    end_m: list[float],
    color: tuple[float, float, float, float],
) -> None:
    start_cm = gazebo_to_unreal_cm(start_m)
    end_cm = gazebo_to_unreal_cm(end_m)
    r, g, b, a = color
    rows.append(
        {
            "id": segment_id,
            "plane": plane,
            "axis_color": "box",
            "start_gazebo_x_m": f"{start_m[0]:.6f}",
            "start_gazebo_y_m": f"{start_m[1]:.6f}",
            "start_gazebo_z_m": f"{start_m[2]:.6f}",
            "end_gazebo_x_m": f"{end_m[0]:.6f}",
            "end_gazebo_y_m": f"{end_m[1]:.6f}",
            "end_gazebo_z_m": f"{end_m[2]:.6f}",
            "start_unreal_x_cm": f"{start_cm[0]:.3f}",
            "start_unreal_y_cm": f"{start_cm[1]:.3f}",
            "start_unreal_z_cm": f"{start_cm[2]:.3f}",
            "end_unreal_x_cm": f"{end_cm[0]:.3f}",
            "end_unreal_y_cm": f"{end_cm[1]:.3f}",
            "end_unreal_z_cm": f"{end_cm[2]:.3f}",
            "rgba_r": f"{r:.3f}",
            "rgba_g": f"{g:.3f}",
            "rgba_b": f"{b:.3f}",
            "rgba_a": f"{a:.3f}",
        }
    )


def add_box_segments(
    rows: list[dict[str, Any]],
    box_id: str,
    min_m: list[float],
    max_m: list[float],
    color: tuple[float, float, float, float],
    *,
    dashed: bool = False,
    visual_z_offset_m: float = 0.0,
) -> None:
    corners = box_corners(min_m, max_m)
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]
    for edge_index, (start_i, end_i) in enumerate(edges):
        start_m = offset_z(corners[start_i], visual_z_offset_m)
        end_m = offset_z(corners[end_i], visual_z_offset_m)
        if not dashed:
            append_segment_row(rows, f"{box_id}_edge_{edge_index:02d}", box_id, start_m, end_m, color)
            continue

        dash_count = 8
        for dash_index in range(dash_count):
            if dash_index % 2 == 1:
                continue
            dash_start = lerp(start_m, end_m, dash_index / dash_count)
            dash_end = lerp(start_m, end_m, (dash_index + 1) / dash_count)
            append_segment_row(
                rows,
                f"{box_id}_edge_{edge_index:02d}_dash_{dash_index:02d}",
                box_id,
                dash_start,
                dash_end,
                color,
            )


def write_segments(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "id",
        "plane",
        "axis_color",
        "start_gazebo_x_m",
        "start_gazebo_y_m",
        "start_gazebo_z_m",
        "end_gazebo_x_m",
        "end_gazebo_y_m",
        "end_gazebo_z_m",
        "start_unreal_x_cm",
        "start_unreal_y_cm",
        "start_unreal_z_cm",
        "end_unreal_x_cm",
        "end_unreal_y_cm",
        "end_unreal_z_cm",
        "rgba_r",
        "rgba_g",
        "rgba_b",
        "rgba_a",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markers(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "id",
        "label",
        "shape",
        "offset_x_m",
        "offset_y_m",
        "offset_z_m",
        "gazebo_x_m",
        "gazebo_y_m",
        "gazebo_z_m",
        "unreal_x_cm",
        "unreal_y_cm",
        "unreal_z_cm",
        "size_x_m",
        "size_y_m",
        "size_z_m",
        "rgba_r",
        "rgba_g",
        "rgba_b",
        "rgba_a",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def proxy_by_actor(scene_truth: dict[str, Any]) -> dict[str, dict[str, Any]]:
    proxies: dict[str, dict[str, Any]] = {}
    for proxy in scene_truth.get("collision_proxies", []):
        actor = proxy.get("source_actor")
        if isinstance(actor, str) and actor not in proxies:
            proxies[actor] = proxy
    return proxies


def marker_from_proxy(marker_id: str, proxy: dict[str, Any], color_key: str) -> dict[str, Any]:
    center_m = proxy["center_m"]
    size_m = proxy["size_m"]
    center_cm = gazebo_to_unreal_cm(center_m)
    r, g, b, a = COLORS[color_key]
    return {
        "id": marker_id,
        "label": f"{marker_id}: {proxy['source_actor']}",
        "shape": "box",
        "offset_x_m": "0.000",
        "offset_y_m": "0.000",
        "offset_z_m": "0.000",
        "gazebo_x_m": f"{center_m[0]:.6f}",
        "gazebo_y_m": f"{center_m[1]:.6f}",
        "gazebo_z_m": f"{center_m[2]:.6f}",
        "unreal_x_cm": f"{center_cm[0]:.3f}",
        "unreal_y_cm": f"{center_cm[1]:.3f}",
        "unreal_z_cm": f"{center_cm[2]:.3f}",
        "size_x_m": f"{size_m[0]:.6f}",
        "size_y_m": f"{size_m[1]:.6f}",
        "size_z_m": f"{size_m[2]:.6f}",
        "rgba_r": f"{r:.3f}",
        "rgba_g": f"{g:.3f}",
        "rgba_b": f"{b:.3f}",
        "rgba_a": f"{a:.3f}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene-profile", default=str(DEFAULT_SCENE_PROFILE))
    parser.add_argument("--coordinate-audit", default=str(DEFAULT_COORDINATE_AUDIT))
    parser.add_argument("--scene-truth", default=str(DEFAULT_SCENE_TRUTH))
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    scene_profile = project_path(args.scene_profile)
    coordinate_audit = project_path(args.coordinate_audit)
    scene_truth_path = project_path(args.scene_truth)

    profile = read_json(scene_profile)
    audit = read_json(coordinate_audit)
    truth = read_json(scene_truth_path)
    proxies = proxy_by_actor(truth)

    if args.output_dir:
        output_dir = project_path(args.output_dir)
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_ROOT / f"factory_l2_gazebo_to_ue_frame_overlay_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    segment_rows: list[dict[str, Any]] = []
    marker_rows: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    missing: list[str] = []

    gazebo_bounds = audit["gazebo_chunks"]["bounds"]
    add_box_segments(
        segment_rows,
        "clean_gazebo_global_bounds",
        gazebo_bounds["min_m"],
        gazebo_bounds["max_m"],
        COLORS["global"],
    )

    for marker_id, actor, color_key in SELECTED_ACTORS:
        proxy = proxies.get(actor)
        if not proxy:
            missing.append(actor)
            continue
        add_box_segments(
            segment_rows,
            f"ue_truth_solid_{marker_id}",
            proxy["min_m"],
            proxy["max_m"],
            COLORS["ue_truth"],
        )
        add_box_segments(
            segment_rows,
            f"gazebo_projected_dashed_{marker_id}",
            proxy["min_m"],
            proxy["max_m"],
            COLORS["gazebo_projected"],
            dashed=True,
            visual_z_offset_m=0.0,
        )
        selected.append(
            {
                "id": marker_id,
                "source_actor": actor,
                "semantic_type": proxy.get("semantic_type"),
                "center_m": proxy["center_m"],
                "size_m": proxy["size_m"],
                "source_mesh": proxy.get("source_mesh"),
                "color_key": color_key,
            }
        )

    segments_csv = output_dir / "factory_l2_gazebo_structure_frame_segments.csv"
    markers_csv = output_dir / "factory_l2_gazebo_structure_frame_markers.csv"
    write_segments(segments_csv, segment_rows)
    write_markers(markers_csv, marker_rows)

    summary = {
        "schema": "mosim.factory_l2_gazebo_to_ue_frame_overlay.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "visual_review_required",
        "purpose": "Readable sparse frame overlay for checking whether Gazebo/MWORKS Factory coordinates align with the original UE Factory scene.",
        "claim_boundary": [
            "This is a static map registration review surface only.",
            "It does not prove ROS/PX4/MAVROS/RViz runtime, localization, planning, controller performance, or UE feedback authority.",
            "User visual acceptance is still required; source bounds alone are not final acceptance.",
        ],
        "coordinate_contract": profile["coordinate_contract"],
        "inputs": {
            "scene_profile": rel(scene_profile),
            "coordinate_audit": rel(coordinate_audit),
            "scene_truth": rel(scene_truth_path),
        },
        "outputs": {
            "segments_csv": rel(segments_csv),
            "markers_csv": rel(markers_csv),
        },
        "global_bounds_source": "clean Gazebo chunk bounds from coordinate audit",
        "selected_structure_count": len(selected),
        "segment_count": len(segment_rows),
        "marker_count": len(marker_rows),
        "missing_selected_actors": missing,
        "selected_structures": selected,
        "review_protocol": [
            "Open UE with the frame overlay command.",
            "Yellow frame is the clean Gazebo global map bounds.",
            "Solid magenta boxes are UE scene-truth structure frames.",
            "Dashed cyan boxes are the Gazebo/MWORKS structure frames reprojected back into UE coordinates.",
            "Accept only if solid and dashed frames visually coincide with each other and sit on the matching UE structures, with no global shift, mirror, scale error, or vertical offset.",
            "Reject if dashed frames drift away from the solid UE frames or both frame layers miss the visible UE structures.",
        ],
    }
    summary_path = output_dir / "FACTORY_L2_GAZEBO_TO_UE_FRAME_OVERLAY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    (output_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Factory L2 Gazebo-to-UE Frame Overlay",
                "",
                "- status: `visual_review_required`",
                f"- selected structures: `{len(selected)}`",
                f"- frame segments: `{len(segment_rows)}`",
                f"- marker boxes: `{len(marker_rows)}`",
                f"- segments csv: `{rel(segments_csv)}`",
                f"- markers csv: `{rel(markers_csv)}`",
                f"- summary json: `{rel(summary_path)}`",
                "",
                "Use this packet for visual map-registration review. The overlay uses",
                "solid magenta UE truth frames plus dashed cyan Gazebo-projected frames instead of",
                "dense point samples, so the operator can check whether the two map",
                "coordinate surfaces coincide on readable Factory structures.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "output_dir": rel(output_dir),
                "segments_csv": rel(segments_csv),
                "markers_csv": rel(markers_csv),
                "selected_structure_count": len(selected),
                "missing_selected_actors": missing,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
