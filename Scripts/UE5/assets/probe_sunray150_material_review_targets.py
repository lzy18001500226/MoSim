#!/usr/bin/env python3
"""Locate material-review targets in the Sunray150 audit blend."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_material_review_targets_20260603.json"


def bounds(objs: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mn.x, mn.y, mn.z = min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)
            mx.x, mx.y, mx.z = max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)
    return mn, mx


def row_for(name: str, predicate) -> dict:
    objs = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and predicate(obj)]
    if not objs:
        return {"target": name, "count": 0}
    mn, mx = bounds(objs)
    center = (mn + mx) * 0.5
    return {
        "target": name,
        "count": len(objs),
        "center_m": [round(center.x, 6), round(center.y, 6), round(center.z, 6)],
        "bbox_min_m": [round(mn.x, 6), round(mn.y, 6), round(mn.z, 6)],
        "bbox_max_m": [round(mx.x, 6), round(mx.y, 6), round(mx.z, 6)],
        "objects": [obj.name for obj in objs[:80]],
    }


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    rows = [
        row_for("front_camera", lambda obj: "FRONT_CAMERA" in obj.name.upper() or obj.name.startswith("front_usb_camera_lens")),
        row_for("bottom_camera", lambda obj: "BOTTOM_CAMERA" in obj.name.upper() or obj.name.startswith("bottom_usb_camera_lens")),
        row_for("motors", lambda obj: "MOTOR" in obj.name.upper() or obj.name.startswith("decal_motor")),
        row_for("tri_blade_propellers", lambda obj: obj.name.startswith("TriBlade_")),
        row_for("mid360", lambda obj: obj.name.startswith("AUDIT_STANDALONE_MID360")),
        row_for("carbon_frame", lambda obj: any(token in obj.name.upper() for token in ("MAIN_STRUCTURE", "TOP_PANNEL", "FILL.1"))),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
