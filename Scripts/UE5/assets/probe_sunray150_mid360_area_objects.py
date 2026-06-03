#!/usr/bin/env python3
"""List visible mesh objects around the MID-360 audit area."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_mid360_area_objects_20260603.json"


def object_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for corner in obj.bound_box:
        w = obj.matrix_world @ Vector(corner)
        mn.x, mn.y, mn.z = min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)
        mx.x, mx.y, mx.z = max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)
    return mn, mx


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    rows = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        mn, mx = object_bounds(obj)
        center = (mn + mx) * 0.5
        size = mx - mn
        if -0.09 <= center.x <= 0.09 and -0.04 <= center.y <= 0.09 and 0.035 <= center.z <= 0.145:
            rows.append(
                {
                    "name": obj.name,
                    "center_m": [round(center.x, 5), round(center.y, 5), round(center.z, 5)],
                    "size_m": [round(size.x, 5), round(size.y, 5), round(size.z, 5)],
                    "materials": [slot.material.name for slot in obj.material_slots if slot.material],
                }
            )
    rows.sort(key=lambda row: (-(row["size_m"][0] * row["size_m"][1]), row["name"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))


if __name__ == "__main__":
    main()
