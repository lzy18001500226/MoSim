#!/usr/bin/env python3
"""Verify that the restored Sunray150 audit blend has no PBR006 overlays."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLEND = PROJECT_ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "Results/unreal_scene_mapping/sunray150_pbr_whole_aircraft_grey_cad_realism_20260607_006/verify_006_revert_no_pbr006.json"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    pbr006_objects = sorted(
        obj.name for obj in bpy.context.scene.objects if "pbr006" in obj.name.lower()
    )
    pbr006_materials = sorted(
        mat.name for mat in bpy.data.materials if "pbr006" in mat.name.lower()
    )
    result = {
        "schema_version": "mosim.sunray150_pbr006_revert_verify.v1",
        "blend": BLEND.relative_to(PROJECT_ROOT).as_posix(),
        "pbr006_object_count": len(pbr006_objects),
        "pbr006_material_count": len(pbr006_materials),
        "pbr006_objects": pbr006_objects,
        "pbr006_materials": pbr006_materials,
        "ok": not pbr006_objects and not pbr006_materials,
        "note": "Verifies the 006 whole-aircraft review overlays/materials were removed from the restored 005-approved Blender audit asset.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
