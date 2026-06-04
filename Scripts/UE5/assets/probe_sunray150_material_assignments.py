#!/usr/bin/env python3
"""Probe material assignments inside the Sunray150 material audit blend."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_material_assignment_probe_20260604.json"


def bsdf_snapshot(mat: bpy.types.Material | None) -> dict:
    if mat is None:
        return {"material": None}
    out = {
        "material": mat.name,
        "diffuse_color": [round(float(v), 6) for v in mat.diffuse_color],
        "image_nodes": [],
        "bsdf": {},
    }
    if not mat.use_nodes:
        return out
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and getattr(node, "image", None):
            out["image_nodes"].append(
                {
                    "name": node.name,
                    "image": node.image.name,
                    "filepath": bpy.path.abspath(node.image.filepath),
                    "colorspace": node.image.colorspace_settings.name,
                }
            )
        if node.type == "BSDF_PRINCIPLED":
            for key in ("Base Color", "Metallic", "Roughness", "Alpha", "Specular IOR Level", "Specular"):
                if key in node.inputs:
                    value = node.inputs[key].default_value
                    if hasattr(value, "__iter__") and not isinstance(value, str):
                        value = [round(float(v), 6) for v in value]
                    else:
                        value = round(float(value), 6)
                    out["bsdf"][key] = value
                    out["bsdf"][f"{key}_linked"] = bool(node.inputs[key].is_linked)
    return out


def object_bounds(obj: bpy.types.Object) -> dict:
    pts = [obj.matrix_world @ Vector(obj.bound_box[i]) for i in range(8)]
    return {
        "min": [round(min(p[j] for p in pts), 6) for j in range(3)],
        "max": [round(max(p[j] for p in pts), 6) for j in range(3)],
    }


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    keys = (
        "MAIN_STRUCTURE",
        "TOP_PANNEL",
        "PROTECTIVE_RING",
        "MID360_PROTECT_ARC",
        "TriBlade",
        "AUDIT_STANDALONE_MID360_013",
        "AUDIT_STANDALONE_MID360_014",
        "AUDIT_STANDALONE_MID360_015",
        "MID-360_4_ASM",
        "FRONT_CAMERA",
        "N150_AllCATPart",
    )
    rows = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if any(key in obj.name for key in keys):
            rows.append(
                {
                    "object": obj.name,
                    "bounds": object_bounds(obj),
                    "materials": [bsdf_snapshot(mat) for mat in obj.data.materials],
                }
            )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))


if __name__ == "__main__":
    main()
