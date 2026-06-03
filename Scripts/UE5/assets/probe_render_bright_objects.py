#!/usr/bin/env python3
"""Find visible objects that render with unexpectedly bright materials."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_bright_object_probe_20260603.json"


def color_luma(color) -> float:
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    rows = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        mats = [slot.material for slot in obj.material_slots if slot.material]
        if not mats:
            rows.append({"object": obj.name, "material": None, "luma": 1.0})
            continue
        for mat in mats:
            rows.append({"object": obj.name, "material": mat.name, "diffuse": [float(v) for v in mat.diffuse_color], "luma": color_luma(mat.diffuse_color)})
    rows.sort(key=lambda row: row["luma"], reverse=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows[:120], ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))


if __name__ == "__main__":
    main()
