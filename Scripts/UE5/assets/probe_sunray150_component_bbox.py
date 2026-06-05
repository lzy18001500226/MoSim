#!/usr/bin/env python3
"""Probe Sunray150 audit component bounding boxes from Blender."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
BLEND = AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"


def object_matches(obj: bpy.types.Object, keys: tuple[str, ...], excludes: tuple[str, ...]) -> bool:
    if obj.type != "MESH":
        return False
    if any(key in obj.name for key in excludes):
        return False
    return any(key in obj.name for key in keys)


def bbox_for(obj: bpy.types.Object) -> dict:
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector((min(p.x for p in coords), min(p.y for p in coords), min(p.z for p in coords)))
    maxs = Vector((max(p.x for p in coords), max(p.y for p in coords), max(p.z for p in coords)))
    center = (mins + maxs) * 0.5
    size = maxs - mins
    return {
        "name": obj.name,
        "min": [mins.x, mins.y, mins.z],
        "max": [maxs.x, maxs.y, maxs.z],
        "center": [center.x, center.y, center.z],
        "size": [size.x, size.y, size.z],
        "materials": [mat.name if mat else None for mat in obj.data.materials],
    }


def main() -> None:
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1 :]
    else:
        args = []
    keys = tuple(args[0].split(",")) if args else ("front_usb_camera_lens_glass_overlay", "DAE_FULL_FRONT_CAMERA_PartBody", "DAE_FULL_FRONT_CAMERA_CONNECTOR.1")
    excludes = tuple(args[1].split(",")) if len(args) > 1 and args[1] else ("CABLE_FRONT_CAMERA", "CABLE_BOTTOM_CAMERA")
    output_path = Path(args[2]) if len(args) > 2 and args[2] else None

    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    rows = [bbox_for(obj) for obj in bpy.context.scene.objects if object_matches(obj, keys, excludes)]
    coords: list[Vector] = []
    for row in rows:
        coords.append(Vector(row["min"]))
        coords.append(Vector(row["max"]))
    summary = {"keys": keys, "excludes": excludes, "count": len(rows), "objects": rows}
    if coords:
        mins = Vector((min(p.x for p in coords), min(p.y for p in coords), min(p.z for p in coords)))
        maxs = Vector((max(p.x for p in coords), max(p.y for p in coords), max(p.z for p in coords)))
        summary["combined"] = {
            "min": [mins.x, mins.y, mins.z],
            "max": [maxs.x, maxs.y, maxs.z],
            "center": [((mins + maxs) * 0.5).x, ((mins + maxs) * 0.5).y, ((mins + maxs) * 0.5).z],
            "size": [(maxs - mins).x, (maxs - mins).y, (maxs - mins).z],
        }
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
