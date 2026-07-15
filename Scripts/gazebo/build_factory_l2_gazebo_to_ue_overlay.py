#!/usr/bin/env python3
"""Build a UE visual overlay from the Gazebo clean Factory mesh.

The overlay samples points from the Gazebo STL chunks, transforms them back to
UE coordinates using the current MoSim Factory coordinate contract, and writes a
CSV that the UE review GameMode can draw over the original UE scene.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import struct
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE = REPO_ROOT / "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "Results/unreal_scene_mapping"


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def gazebo_to_unreal_cm(point_m: tuple[float, float, float]) -> tuple[float, float, float]:
    x_m, y_m, z_m = point_m
    return (x_m * 100.0, -y_m * 100.0, z_m * 100.0)


def read_binary_stl_triangle_count(path: Path) -> int | None:
    size = path.stat().st_size
    if size < 84:
        return None
    with path.open("rb") as f:
        f.seek(80)
        count = struct.unpack("<I", f.read(4))[0]
    if 84 + count * 50 == size:
        return count
    return None


def sample_binary_stl_centroids(path: Path, max_points: int) -> list[tuple[float, float, float]]:
    triangle_count = read_binary_stl_triangle_count(path)
    if not triangle_count or max_points <= 0:
        return []

    stride = max(1, math.ceil(triangle_count / max_points))
    points: list[tuple[float, float, float]] = []
    with path.open("rb") as f:
        for tri_index in range(0, triangle_count, stride):
            if len(points) >= max_points:
                break
            f.seek(84 + tri_index * 50)
            data = f.read(50)
            if len(data) != 50:
                break
            values = struct.unpack("<12fH", data)
            v1 = values[3:6]
            v2 = values[6:9]
            v3 = values[9:12]
            points.append(
                (
                    (v1[0] + v2[0] + v3[0]) / 3.0,
                    (v1[1] + v2[1] + v3[1]) / 3.0,
                    (v1[2] + v2[2] + v3[2]) / 3.0,
                )
            )
    return points


def load_profile(profile_path: Path) -> dict:
    return json.loads(profile_path.read_text(encoding="utf-8"))


def load_conversion_manifest(profile: dict) -> dict:
    manifest_path = REPO_ROOT / profile["clean_import"]["conversion_manifest"]
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def bounds(points: list[tuple[float, float, float]]) -> dict:
    if not points:
        return {"min": None, "max": None, "size": None}
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return {
        "min": mins,
        "max": maxs,
        "size": [maxs[i] - mins[i] for i in range(3)],
    }


def write_overlay_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "chunk_index",
        "sample_index",
        "gazebo_x_m",
        "gazebo_y_m",
        "gazebo_z_m",
        "unreal_x_cm",
        "unreal_y_cm",
        "unreal_z_cm",
        "rgba_r",
        "rgba_g",
        "rgba_b",
        "rgba_a",
        "point_size",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene-profile", default=str(DEFAULT_PROFILE))
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--max-points", type=int, default=12000)
    parser.add_argument("--point-size", type=float, default=6.0)
    args = parser.parse_args()

    profile_path = Path(args.scene_profile)
    if not profile_path.is_absolute():
        profile_path = REPO_ROOT / profile_path
    profile = load_profile(profile_path)
    manifest = load_conversion_manifest(profile)

    chunks = [chunk for chunk in manifest["chunks"] if chunk.get("ok")]
    per_chunk = max(1, math.ceil(args.max_points / max(1, len(chunks))))

    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = REPO_ROOT / output_dir
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_ROOT / f"factory_l2_gazebo_to_ue_overlay_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    gazebo_points: list[tuple[float, float, float]] = []
    unreal_points: list[tuple[float, float, float]] = []
    chunk_summaries = []
    for chunk in chunks:
        chunk_path = Path(chunk["path"])
        points = sample_binary_stl_centroids(chunk_path, per_chunk)
        chunk_summaries.append(
            {
                "chunk_index": chunk["chunk_index"],
                "path": repo_rel(chunk_path),
                "sampled_points": len(points),
                "object_count": chunk.get("object_count"),
                "mesh_names_sample": chunk.get("mesh_names_sample", []),
            }
        )
        for sample_index, point_m in enumerate(points):
            point_cm = gazebo_to_unreal_cm(point_m)
            gazebo_points.append(point_m)
            unreal_points.append(point_cm)
            rows.append(
                {
                    "chunk_index": chunk["chunk_index"],
                    "sample_index": sample_index,
                    "gazebo_x_m": f"{point_m[0]:.6f}",
                    "gazebo_y_m": f"{point_m[1]:.6f}",
                    "gazebo_z_m": f"{point_m[2]:.6f}",
                    "unreal_x_cm": f"{point_cm[0]:.3f}",
                    "unreal_y_cm": f"{point_cm[1]:.3f}",
                    "unreal_z_cm": f"{point_cm[2]:.3f}",
                    "rgba_r": "0.00",
                    "rgba_g": "0.95",
                    "rgba_b": "1.00",
                    "rgba_a": "1.00",
                    "point_size": f"{args.point_size:.2f}",
                }
            )

    overlay_csv = output_dir / "factory_l2_gazebo_mesh_reprojected_to_ue_points.csv"
    write_overlay_csv(overlay_csv, rows)

    summary = {
        "schema": "mosim.factory_l2_gazebo_to_ue_overlay.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "visual_review_required",
        "purpose": "Overlay Gazebo clean mesh samples back onto the original UE Factory scene to validate map-to-map alignment.",
        "claim_boundary": [
            "This checks static map coordinate alignment only.",
            "This is not ROS/PX4/MAVROS runtime, localization, planner, or controller evidence.",
        ],
        "coordinate_contract": profile["coordinate_contract"],
        "inputs": {
            "scene_profile": repo_rel(profile_path),
            "conversion_manifest": profile["clean_import"]["conversion_manifest"],
            "clean_world": profile["world_path"],
        },
        "outputs": {
            "overlay_csv": repo_rel(overlay_csv),
        },
        "sampled_point_count": len(rows),
        "chunk_count": len(chunks),
        "per_chunk_budget": per_chunk,
        "gazebo_sample_bounds_m": bounds(gazebo_points),
        "unreal_overlay_bounds_cm": bounds(unreal_points),
        "chunk_summaries_sample": chunk_summaries[:10],
        "review_protocol": [
            "Open UE with this overlay CSV over the original Factory scene.",
            "Cyan points are sampled from Gazebo clean STL chunks and transformed back to UE coordinates.",
            "Accept only if cyan points visually lie on the matching UE factory surfaces: floor, walls, pipes, columns, platforms, and equipment.",
            "Reject if the cyan cloud is globally shifted, mirrored, scaled incorrectly, vertically floating, or buried under the floor.",
        ],
    }
    summary_path = output_dir / "FACTORY_L2_GAZEBO_TO_UE_OVERLAY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    readme = output_dir / "SUMMARY.md"
    readme.write_text(
        "\n".join(
            [
                "# Factory L2 Gazebo-to-UE Overlay Review",
                "",
                "- status: `visual_review_required`",
                f"- sampled Gazebo points: `{len(rows)}`",
                f"- overlay csv: `{repo_rel(overlay_csv)}`",
                f"- summary json: `{repo_rel(summary_path)}`",
                "",
                "Cyan overlay points are sampled from the clean Gazebo STL chunks and",
                "transformed back into UE coordinates. This is the primary visual check",
                "for whether the two maps are registered, replacing synthetic calibration",
                "markers as the acceptance surface.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"output_dir": repo_rel(output_dir), "sampled_point_count": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
