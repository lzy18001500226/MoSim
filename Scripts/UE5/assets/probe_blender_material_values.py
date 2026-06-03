#!/usr/bin/env python3
"""Inspect material node values in the current Sunray150 audit blend."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_material_node_probe_20260603.json"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    rows = []
    for mat in bpy.data.materials:
        row = {
            "name": mat.name,
            "diffuse_color": [round(float(v), 4) for v in mat.diffuse_color],
            "use_nodes": mat.use_nodes,
            "bsdf_inputs": {},
        }
        if mat.use_nodes and mat.node_tree:
            bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
            if bsdf:
                for key in ["Base Color", "Alpha", "Metallic", "Roughness"]:
                    if key in bsdf.inputs:
                        val = bsdf.inputs[key].default_value
                        if hasattr(val, "__len__"):
                            row["bsdf_inputs"][key] = [round(float(v), 4) for v in val]
                        else:
                            row["bsdf_inputs"][key] = round(float(val), 4)
        rows.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))


if __name__ == "__main__":
    main()
