#!/usr/bin/env python3
"""Dump all mesh object bounds/materials for Sunray150 audit blend."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_all_object_bounds_20260604.json"


def bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    rows = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        mn, mx = bounds(obj)
        size = mx - mn
        rows.append(
            {
                "name": obj.name,
                "min": [round(mn.x, 6), round(mn.y, 6), round(mn.z, 6)],
                "max": [round(mx.x, 6), round(mx.y, 6), round(mx.z, 6)],
                "center": [round((mn.x + mx.x) / 2, 6), round((mn.y + mx.y) / 2, 6), round((mn.z + mx.z) / 2, 6)],
                "size": [round(size.x, 6), round(size.y, 6), round(size.z, 6)],
                "materials": [mat.name if mat else None for mat in obj.data.materials],
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))


if __name__ == "__main__":
    main()
