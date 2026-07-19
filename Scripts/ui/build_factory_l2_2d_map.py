#!/usr/bin/env python3
"""Build the versioned Factory L2 operator map from accepted scene truth."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
DEFAULT_ENVELOPE = ROOT / "Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json"
DEFAULT_FULL_BOUNDS_AUDIT = (
    ROOT
    / "Results/unreal_scene_mapping/factory_l2_flight_envelope_audit_20260703_014306"
    / "FACTORY_L2_FLIGHT_ENVELOPE_AUDIT.json"
)
DEFAULT_MESH_DIR = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import/assets/chunked_stl_clean"
DEFAULT_MESH_MANIFEST = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import/manifests/blender_chunked_stl_conversion_clean.json"
DEFAULT_OUTPUT = ROOT / "apps/flight_console/mosim/custom/maps/factory_l2/v1"

CANVAS_SIZE = (2048, 800)
MARGIN_PX = 32
SLICE_MIN_Z_M = 0.9
SLICE_MAX_Z_M = 1.6
SECTION_Z_M = 1.2
SECTION_QUANTIZATION_M = 0.1
COLORS = {
    "background": "#10151a",
    "map_area": "#20282e",
    "task_area": "#26383a",
    "task_boundary": "#24a8a8",
    "grid": "#334048",
    "boundary": "#d7e0e5",
    "structure": "#aeb9bf",
    "gate": "#24a8a8",
}

STL_DTYPE = np.dtype(
    [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def full_map_bounds(audit: dict[str, Any]) -> dict[str, float]:
    boundary = audit["recommended_exploration_boundary"]
    return {
        key: float(boundary[key])
        for key in ("min_x_m", "max_x_m", "min_y_m", "max_y_m")
    }


def task_bounds(envelope: dict[str, Any]) -> dict[str, float]:
    boundary = envelope["exploration_boundary"]
    return {
        key: float(boundary[key])
        for key in ("min_x_m", "max_x_m", "min_y_m", "max_y_m")
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def matrix_for_bounds(bounds: dict[str, float]) -> tuple[list[list[float]], list[list[float]], float]:
    width_m = bounds["max_x_m"] - bounds["min_x_m"]
    height_m = bounds["max_y_m"] - bounds["min_y_m"]
    scale = min(
        (CANVAS_SIZE[0] - 2 * MARGIN_PX) / width_m,
        (CANVAS_SIZE[1] - 2 * MARGIN_PX) / height_m,
    )
    left = (CANVAS_SIZE[0] - width_m * scale) / 2.0
    top = (CANVAS_SIZE[1] - height_m * scale) / 2.0
    world_to_pixel = [
        [scale, 0.0, left - scale * bounds["min_x_m"]],
        [0.0, -scale, top + scale * bounds["max_y_m"]],
        [0.0, 0.0, 1.0],
    ]
    pixel_to_world = [
        [1.0 / scale, 0.0, bounds["min_x_m"] - left / scale],
        [0.0, -1.0 / scale, bounds["max_y_m"] + top / scale],
        [0.0, 0.0, 1.0],
    ]
    return world_to_pixel, pixel_to_world, scale


def transform(matrix: list[list[float]], x: float, y: float) -> tuple[float, float]:
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2],
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2],
    )


def clipped_gate(proxy: dict[str, Any], bounds: dict[str, float]) -> dict[str, Any] | None:
    if proxy.get("semantic_type") != "gate":
        return None
    min_m = proxy.get("min_m", [])
    max_m = proxy.get("max_m", [])
    if len(min_m) != 3 or len(max_m) != 3:
        return None
    if float(max_m[2]) < SLICE_MIN_Z_M or float(min_m[2]) > SLICE_MAX_Z_M:
        return None
    min_x = max(float(min_m[0]), bounds["min_x_m"])
    max_x = min(float(max_m[0]), bounds["max_x_m"])
    min_y = max(float(min_m[1]), bounds["min_y_m"])
    max_y = min(float(max_m[1]), bounds["max_y_m"])
    if min_x >= max_x or min_y >= max_y:
        return None
    return {
        "id": str(proxy["collision_proxy_id"]),
        "semantic_type": str(proxy["semantic_type"]),
        "source_actor": str(proxy.get("source_actor", "")),
        "source_mesh": str(proxy.get("source_mesh", "")),
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "min_z": float(min_m[2]),
        "max_z": float(max_m[2]),
    }


def stl_triangle_count(path: Path) -> int:
    with path.open("rb") as stream:
        stream.seek(80)
        raw = stream.read(4)
    if len(raw) != 4:
        raise ValueError(f"Invalid binary STL header: {path}")
    count = struct.unpack("<I", raw)[0]
    expected_size = 84 + count * STL_DTYPE.itemsize
    if path.stat().st_size != expected_size:
        raise ValueError(f"Only binary STL is supported: {path}")
    return count


def mesh_section_segments(
    mesh_dir: Path,
    bounds: dict[str, float],
    section_z_m: float = SECTION_Z_M,
    quantization_m: float = SECTION_QUANTIZATION_M,
) -> tuple[np.ndarray, dict[str, int]]:
    all_segments: list[np.ndarray] = []
    total_triangles = 0
    intersecting_triangles = 0
    mesh_paths = sorted(mesh_dir.glob("*.stl"))
    if not mesh_paths:
        raise FileNotFoundError(f"No STL chunks found under {mesh_dir}")

    for path in mesh_paths:
        count = stl_triangle_count(path)
        total_triangles += count
        vertices = np.memmap(path, dtype=STL_DTYPE, mode="r", offset=84, shape=(count,))["vertices"]
        lower = vertices.min(axis=1)
        upper = vertices.max(axis=1)
        selected = (
            (lower[:, 2] <= section_z_m)
            & (upper[:, 2] >= section_z_m)
            & ((upper[:, 2] - lower[:, 2]) > 1e-7)
            & (upper[:, 0] > bounds["min_x_m"])
            & (lower[:, 0] < bounds["max_x_m"])
            & (upper[:, 1] > bounds["min_y_m"])
            & (lower[:, 1] < bounds["max_y_m"])
        )
        triangles = np.asarray(vertices[selected])
        intersecting_triangles += len(triangles)
        if not len(triangles):
            continue

        points = np.full((len(triangles), 3, 2), np.nan, dtype=np.float64)
        valid = np.zeros((len(triangles), 3), dtype=bool)
        for edge_index, (start_index, end_index) in enumerate(((0, 1), (1, 2), (2, 0))):
            start = triangles[:, start_index]
            end = triangles[:, end_index]
            delta_z = end[:, 2] - start[:, 2]
            crosses = (
                (((start[:, 2] <= section_z_m) & (end[:, 2] >= section_z_m))
                 | ((end[:, 2] <= section_z_m) & (start[:, 2] >= section_z_m)))
                & (np.abs(delta_z) > 1e-7)
            )
            interpolation = (section_z_m - start[crosses, 2]) / delta_z[crosses]
            points[crosses, edge_index] = (
                start[crosses, :2]
                + interpolation[:, None] * (end[crosses, :2] - start[crosses, :2])
            )
            valid[crosses, edge_index] = True

        has_segment = valid.sum(axis=1) >= 2
        points = points[has_segment]
        valid = valid[has_segment]
        first_two = np.argsort(~valid, axis=1)[:, :2]
        segments = np.take_along_axis(points, first_two[:, :, None], axis=1)
        segments[:, :, 0] = np.clip(segments[:, :, 0], bounds["min_x_m"], bounds["max_x_m"])
        segments[:, :, 1] = np.clip(segments[:, :, 1], bounds["min_y_m"], bounds["max_y_m"])
        origin = np.array([bounds["min_x_m"], bounds["min_y_m"]])
        segments = np.rint((segments - origin) / quantization_m).astype(np.int32)
        different = np.any(segments[:, 0] != segments[:, 1], axis=1)
        all_segments.append(segments[different])

    combined = np.concatenate(all_segments, axis=0)
    first = combined[:, 0]
    second = combined[:, 1]
    swap = (first[:, 0] > second[:, 0]) | (
        (first[:, 0] == second[:, 0]) & (first[:, 1] > second[:, 1])
    )
    canonical = combined.copy()
    canonical[swap, 0] = second[swap]
    canonical[swap, 1] = first[swap]
    unique = np.unique(canonical.reshape(-1, 4), axis=0).reshape(-1, 2, 2)
    world_segments = unique.astype(np.float64) * quantization_m
    world_segments[:, :, 0] += bounds["min_x_m"]
    world_segments[:, :, 1] += bounds["min_y_m"]
    return world_segments, {
        "mesh_chunk_count": len(mesh_paths),
        "total_triangle_count": total_triangles,
        "section_triangle_count": intersecting_triangles,
        "unique_section_segment_count": len(world_segments),
    }


def polygon(feature: dict[str, Any]) -> list[list[float]]:
    return [
        [feature["min_x"], feature["min_y"]],
        [feature["max_x"], feature["min_y"]],
        [feature["max_x"], feature["max_y"]],
        [feature["min_x"], feature["max_y"]],
        [feature["min_x"], feature["min_y"]],
    ]


def draw_floorplan(
    output: Path,
    bounds: dict[str, float],
    task_area: dict[str, float],
    segments: np.ndarray,
    gates: list[dict[str, Any]],
    world_to_pixel: list[list[float]],
) -> None:
    image = Image.new("RGB", CANVAS_SIZE, COLORS["background"])
    draw = ImageDraw.Draw(image)
    upper_left = transform(world_to_pixel, bounds["min_x_m"], bounds["max_y_m"])
    lower_right = transform(world_to_pixel, bounds["max_x_m"], bounds["min_y_m"])
    draw.rectangle([upper_left, lower_right], fill=COLORS["map_area"])

    task_upper_left = transform(world_to_pixel, task_area["min_x_m"], task_area["max_y_m"])
    task_lower_right = transform(world_to_pixel, task_area["max_x_m"], task_area["min_y_m"])
    draw.rectangle([task_upper_left, task_lower_right], fill=COLORS["task_area"])

    for x in range(math.ceil(bounds["min_x_m"] / 10) * 10, math.floor(bounds["max_x_m"] / 10) * 10 + 1, 10):
        start = transform(world_to_pixel, x, bounds["min_y_m"])
        end = transform(world_to_pixel, x, bounds["max_y_m"])
        draw.line([start, end], fill=COLORS["grid"], width=1)
    for y in range(math.ceil(bounds["min_y_m"] / 10) * 10, math.floor(bounds["max_y_m"] / 10) * 10 + 1, 10):
        start = transform(world_to_pixel, bounds["min_x_m"], y)
        end = transform(world_to_pixel, bounds["max_x_m"], y)
        draw.line([start, end], fill=COLORS["grid"], width=1)

    for segment in segments:
        start = transform(world_to_pixel, float(segment[0, 0]), float(segment[0, 1]))
        end = transform(world_to_pixel, float(segment[1, 0]), float(segment[1, 1]))
        draw.line([start, end], fill=COLORS["structure"], width=2)

    for gate in gates:
        p0 = transform(world_to_pixel, gate["min_x"], gate["max_y"])
        p1 = transform(world_to_pixel, gate["max_x"], gate["min_y"])
        draw.rectangle([p0, p1], outline=COLORS["gate"], width=3)

    draw.rectangle([task_upper_left, task_lower_right], outline=COLORS["task_boundary"], width=3)
    draw.rectangle([upper_left, lower_right], outline=COLORS["boundary"], width=3)
    image.save(output, format="PNG", optimize=True)


def build_map(
    truth_path: Path,
    envelope_path: Path,
    mesh_dir: Path,
    output_dir: Path,
    full_bounds_audit_path: Path = DEFAULT_FULL_BOUNDS_AUDIT,
) -> dict[str, Any]:
    truth = read_json(truth_path)
    envelope = read_json(envelope_path)
    audit = read_json(full_bounds_audit_path)
    bounds = full_map_bounds(audit)
    indoor_task_bounds = task_bounds(envelope)
    world_to_pixel, pixel_to_world, pixels_per_meter = matrix_for_bounds(bounds)
    gates = [
        clipped
        for proxy in truth["collision_proxies"]
        if (clipped := clipped_gate(proxy, bounds)) is not None
    ]
    gates.sort(key=lambda feature: feature["id"])
    segments, mesh_statistics = mesh_section_segments(mesh_dir, bounds)

    output_dir.mkdir(parents=True, exist_ok=True)
    floorplan_path = output_dir / "floorplan.png"
    geojson_path = output_dir / "structure.geojson"
    transform_path = output_dir / "world_to_pixel.json"
    scene_map_path = output_dir / "scene_map.json"

    draw_floorplan(floorplan_path, bounds, indoor_task_bounds, segments, gates, world_to_pixel)
    geojson = {
        "type": "FeatureCollection",
        "name": "factory_l2_flight_slice",
        "features": [{
            "type": "Feature",
            "id": "factory_l2_mesh_section_z_1_2m",
            "properties": {
                "semantic_type": "structure_section",
                "section_z_m": SECTION_Z_M,
                "source": "accepted_factory_l2_chunked_stl_clean",
            },
            "geometry": {
                "type": "MultiLineString",
                "coordinates": segments.tolist(),
            },
        }, {
            "type": "Feature",
            "id": "factory_l2_indoor_task_boundary",
            "properties": {
                "semantic_type": "task_boundary",
                "source": "factory_l2_exploration_envelope",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [indoor_task_bounds["min_x_m"], indoor_task_bounds["min_y_m"]],
                    [indoor_task_bounds["max_x_m"], indoor_task_bounds["min_y_m"]],
                    [indoor_task_bounds["max_x_m"], indoor_task_bounds["max_y_m"]],
                    [indoor_task_bounds["min_x_m"], indoor_task_bounds["max_y_m"]],
                    [indoor_task_bounds["min_x_m"], indoor_task_bounds["min_y_m"]],
                ]],
            },
        }] + [
            {
                "type": "Feature",
                "id": feature["id"],
                "properties": {
                    "semantic_type": feature["semantic_type"],
                    "source_actor": feature["source_actor"],
                    "source_mesh": feature["source_mesh"],
                    "min_z_m": feature["min_z"],
                    "max_z_m": feature["max_z"],
                },
                "geometry": {"type": "Polygon", "coordinates": [polygon(feature)]},
            }
            for feature in gates
        ],
    }
    write_json(geojson_path, geojson)

    transform_payload = {
        "schema": "mosim.world_to_pixel.v1",
        "map_id": "factory_l2",
        "map_version": "v1",
        "world_frame": "mworks_world",
        "world_units": "meters",
        "pixel_origin": "top_left",
        "image_size_px": {"width": CANVAS_SIZE[0], "height": CANVAS_SIZE[1]},
        "bounds_m": bounds,
        "pixels_per_meter": pixels_per_meter,
        "meters_per_pixel": 1.0 / pixels_per_meter,
        "axis_policy": "pixel_u_increases_with_world_x; pixel_v_decreases_with_world_y",
        "world_to_pixel_3x3": world_to_pixel,
        "pixel_to_world_3x3": pixel_to_world,
    }
    write_json(transform_path, transform_payload)

    counts = {
        "mesh_section_segments": len(segments),
        "semantic_gate_overlays": len(gates),
    }
    scene_map = {
        "schema": "mosim.scene_map.v1",
        "map_id": "factory_l2",
        "map_version": "v1",
        "status": "full_factory_operator_map_candidate",
        "map_scope": {
            "asset_scope": "complete_factory_low_floor_boundary",
            "full_factory_floor_bounds_m": bounds,
            "indoor_task_overlay_bounds_m": indoor_task_bounds,
            "publication_rule": "Use the full Factory base map; render the indoor FUEL area only as a task overlay.",
        },
        "coordinate_contract": {
            "world_frame": "mworks_world",
            "gazebo_to_unreal": "UE_X_cm=world_X_m*100; UE_Y_cm=-world_Y_m*100; UE_Z_cm=world_Z_m*100",
            "world_to_pixel": "world_to_pixel.json",
        },
        "flight_slice_m": {
            "mission_band_min_z": SLICE_MIN_Z_M,
            "mission_band_max_z": SLICE_MAX_Z_M,
            "display_section_z": SECTION_Z_M,
            "section_quantization": SECTION_QUANTIZATION_M,
        },
        "feature_counts": counts,
        "mesh_statistics": mesh_statistics,
        "assets": {
            "floorplan": "floorplan.png",
            "structure": "structure.geojson",
            "world_to_pixel": "world_to_pixel.json",
        },
        "source": {
            "scene_truth": str(truth_path.relative_to(ROOT)).replace("\\", "/"),
            "scene_truth_sha256": sha256(truth_path),
            "full_bounds_audit": str(full_bounds_audit_path.relative_to(ROOT)).replace("\\", "/"),
            "full_bounds_audit_sha256": sha256(full_bounds_audit_path),
            "exploration_envelope": str(envelope_path.relative_to(ROOT)).replace("\\", "/"),
            "exploration_envelope_sha256": sha256(envelope_path),
            "l2_mesh_directory": str(mesh_dir.relative_to(ROOT)).replace("\\", "/"),
            "l2_mesh_manifest": str(DEFAULT_MESH_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "l2_mesh_manifest_sha256": sha256(DEFAULT_MESH_MANIFEST),
        },
        "asset_sha256": {
            "floorplan.png": sha256(floorplan_path),
            "structure.geojson": sha256(geojson_path),
            "world_to_pixel.json": sha256(transform_path),
        },
        "qgc_geodetic_anchor": {
            "status": "pending_runtime_confirmation",
            "reason": "No project-local authoritative PX4/QGC global origin was found; mission publication remains gated.",
        },
        "claim_boundary": [
            "This package is a full-boundary operator-map candidate generated from accepted Factory collision truth.",
            "Its 1196 m by 531 m base bounds come from the accepted low-floor audit; the 175.66 m by 64.00 m indoor area is a separate task overlay.",
            "The structure layer is a quantized horizontal section of the accepted L2 Gazebo mesh; semantic overlays come from scene truth.",
            "The display section is not a replacement for the full 3D Gazebo collision mesh or live occupancy map.",
            "Unknown-environment planners must not consume this operator display map.",
            "QGC mission publication requires a confirmed runtime geodetic anchor and a separate round-trip gate.",
        ],
    }
    write_json(scene_map_path, scene_map)
    return scene_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--full-bounds-audit", type=Path, default=DEFAULT_FULL_BOUNDS_AUDIT)
    parser.add_argument("--mesh-dir", type=Path, default=DEFAULT_MESH_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_map(
        args.truth.resolve(),
        args.envelope.resolve(),
        args.mesh_dir.resolve(),
        args.output.resolve(),
        args.full_bounds_audit.resolve(),
    )
    print(json.dumps({"output": str(args.output), "status": result["status"], "feature_counts": result["feature_counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
