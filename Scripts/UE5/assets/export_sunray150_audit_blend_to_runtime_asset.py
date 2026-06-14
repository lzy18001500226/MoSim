#!/usr/bin/env python3
"""Export the accepted Sunray150 audit Blender scene for UE runtime import.

Run with Blender:
  blender --background <audit.blend> --python this_script.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_BLEND = (
    PROJECT_ROOT
    / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend"
)
OUT_DIR = PROJECT_ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150"


def mesh_summary() -> dict[str, object]:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
    return {
        "mesh_object_count": len(meshes),
        "material_count": len(materials),
        "first_mesh_objects": [obj.name for obj in meshes[:30]],
        "first_materials": materials[:40],
    }


def selected_mesh_summary(meshes: list[bpy.types.Object]) -> dict[str, object]:
    materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
    return {
        "mesh_object_count": len(meshes),
        "material_count": len(materials),
        "first_mesh_objects": [obj.name for obj in meshes[:30]],
        "first_materials": materials[:40],
    }


def parse_args() -> argparse.Namespace:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-blend", type=Path, default=SOURCE_BLEND)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--output-stem", default="sunray150_with_mid360_textured")
    parser.add_argument(
        "--merge-runtime-mesh",
        action="store_true",
        help="Join visible mesh objects into one runtime mesh before export.",
    )
    return parser.parse_args(args)


def join_visible_meshes_for_runtime() -> dict[str, object]:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.visible_get()]
    if not meshes:
        raise RuntimeError("No visible mesh objects found in accepted Sunray150 audit Blender scene.")

    before = selected_mesh_summary(meshes)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = "sunray150_with_mid360_textured_runtime"
    joined.data.name = "sunray150_with_mid360_textured_runtime_mesh"
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    return {
        "merge_runtime_mesh": True,
        "joined_object": joined.name,
        "joined_material_slot_count": len(joined.material_slots),
        "source_mesh_summary": before,
    }


def main() -> None:
    start = time.time()
    args = parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    out_fbx = output_dir / f"{args.output_stem}.fbx"
    out_glb = output_dir / f"{args.output_stem}.glb"
    out_manifest = output_dir / f"{args.output_stem}_export_manifest.json"

    summary = mesh_summary()
    if summary["mesh_object_count"] == 0:
        raise RuntimeError("No mesh objects found in accepted Sunray150 audit Blender scene.")

    merge_summary = {"merge_runtime_mesh": False}
    if args.merge_runtime_mesh:
        merge_summary = join_visible_meshes_for_runtime()

    bpy.ops.export_scene.fbx(
        filepath=str(out_fbx),
        use_selection=False,
        add_leaf_bones=False,
        path_mode="COPY",
        embed_textures=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        bake_space_transform=False,
    )
    bpy.ops.export_scene.gltf(filepath=str(out_glb), export_format="GLB")

    payload = {
        "schema": "mosim.sunray150.audit_blend_runtime_export.v1",
        "ok": True,
        "source_blend": str(args.source_blend),
        "source_route": "user_confirmed_005_dae_derived_blender_visual_baseline",
        "outputs": {
            "fbx": str(out_fbx),
            "glb": str(out_glb),
            "manifest": str(out_manifest),
        },
        "elapsed_sec": round(time.time() - start, 3),
        **summary,
        **merge_summary,
        "claim_boundary": [
            "Exports the accepted Blender visual baseline for UE import.",
            "When merge_runtime_mesh=true, the export uses Blender's own material-slot assignments on one joined runtime mesh.",
            "Does not change MWORKS dynamics, controller, mass, inertia, motor, or planner evidence.",
            "Does not by itself prove UE runtime visual acceptance; UE import and screenshot/log review are still required.",
        ],
    }
    out_manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
