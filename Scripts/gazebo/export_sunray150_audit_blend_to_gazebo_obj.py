#!/usr/bin/env python3
"""Export the accepted Sunray150 audit Blender scene to a Gazebo OBJ visual.

Run with Blender 5:
  blender --background --python Scripts/gazebo/export_sunray150_audit_blend_to_gazebo_obj.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_BLEND = (
    PROJECT_ROOT
    / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend"
)
OUT_DIR = PROJECT_ROOT / "Config/gazebo/models/sunray150_assembled/meshes"
DEFAULT_STEM = "sunray150_dae_mid360_realistic_material_audit_gazebo_visual"

FORBIDDEN_SOURCE_TOKENS = (
    "Sunray150_Mid360BaseSupplement",
    "Sunray150_Mid360DomeSupplement",
    "sunray150_with_mid360_tri_blade_prop_",
)
EXPECTED_SOURCE_TOKENS = (
    "AUDIT_STANDALONE_MID360_",
    "TriBlade_flipped_around_screw_axis_",
)

GAZEBO_MTL_OVERRIDES = {
    "MID360_Texture_Black_Base": {
        "Ns": "72.000000",
        "Ka": "0.060000 0.065000 0.065000",
        "Kd": "0.055000 0.060000 0.060000",
        "Ks": "0.110000 0.110000 0.110000",
        "d": "1.000000",
        "illum": "2",
    },
    "MID360_Texture_Black_M12_Connector": {
        "Ns": "80.000000",
        "Ka": "0.045000 0.045000 0.043000",
        "Kd": "0.035000 0.035000 0.033000",
        "Ks": "0.080000 0.080000 0.080000",
        "d": "1.000000",
        "illum": "2",
    },
    "MID360_Texture_Black_Mount_Inserts": {
        "Ns": "64.000000",
        "Ka": "0.050000 0.050000 0.048000",
        "Kd": "0.040000 0.040000 0.038000",
        "Ks": "0.080000 0.080000 0.080000",
        "d": "1.000000",
        "illum": "2",
    },
    "MID360_Texture_Dark_Blue_Mirror_Coated_Optical_Dome": {
        "Ns": "180.000000",
        "Ka": "0.080000 0.140000 0.220000",
        "Kd": "0.020000 0.170000 0.360000",
        "Ks": "0.500000 0.650000 0.800000",
        "d": "1.000000",
        "illum": "3",
    },
    "MID360_Texture_Satin_Black_Protection_Frame": {
        "Ns": "90.000000",
        "Ka": "0.055000 0.060000 0.060000",
        "Kd": "0.050000 0.055000 0.055000",
        "Ks": "0.160000 0.160000 0.160000",
        "d": "1.000000",
        "illum": "3",
        "map_Kd": None,
    },
    "MID360_Texture_Satin_Silver_Grey_Coated_Metal_Housing": {
        "Ns": "120.000000",
        "Ka": "0.310000 0.320000 0.320000",
        "Kd": "0.520000 0.550000 0.540000",
        "Ks": "0.380000 0.390000 0.390000",
        "d": "1.000000",
        "illum": "3",
        "map_Kd": None,
    },
    "Sunray150_Texture_Clear_Liuli_Glass_Prop_Guard": {
        "Ka": "0.520000 0.650000 0.660000",
        "Kd": "0.420000 0.560000 0.580000",
        "Ks": "0.080000 0.090000 0.090000",
        "d": "1.000000",
        "illum": "2",
    },
    "Sunray150_Texture_Clear_Liuli_Glass_Propeller": {
        "Ka": "0.580000 0.700000 0.720000",
        "Kd": "0.520000 0.660000 0.700000",
        "Ks": "0.080000 0.090000 0.090000",
        "d": "1.000000",
        "illum": "2",
    },
}


def append_missing_material_overrides(
    patched_lines: list[str],
    current_material: str | None,
    seen_keys: set[str],
    applied: list[dict[str, str]],
) -> None:
    overrides = GAZEBO_MTL_OVERRIDES.get(current_material or "")
    if not overrides:
        return
    for key in ("Ns", "Ka", "Kd", "Ks", "d", "illum"):
        if key in seen_keys or key not in overrides:
            continue
        value = overrides[key]
        if value is None:
            continue
        patched_lines.append(f"{key} {value}")
        applied.append(
            {
                "material": current_material or "",
                "key": key,
                "value": value,
                "action": "insert_missing",
            }
        )


def parse_args() -> argparse.Namespace:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-blend", type=Path, default=SOURCE_BLEND)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--output-stem", default=DEFAULT_STEM)
    parser.add_argument(
        "--join",
        action="store_true",
        help="Join selected visible meshes before export. Off by default to preserve audit object names.",
    )
    return parser.parse_args(args)


def resolved(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def visible_meshes() -> list[bpy.types.Object]:
    meshes: list[bpy.types.Object] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if obj.visible_get():
            meshes.append(obj)
    return meshes


def bounds_for(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    mins = Vector((float("inf"), float("inf"), float("inf")))
    maxs = Vector((float("-inf"), float("-inf"), float("-inf")))
    for obj in objects:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            mins.x = min(mins.x, world.x)
            mins.y = min(mins.y, world.y)
            mins.z = min(mins.z, world.z)
            maxs.x = max(maxs.x, world.x)
            maxs.y = max(maxs.y, world.y)
            maxs.z = max(maxs.z, world.z)
    return {
        "min": [round(v, 6) for v in mins],
        "max": [round(v, 6) for v in maxs],
    }


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def maybe_join(objects: list[bpy.types.Object]) -> list[bpy.types.Object]:
    if len(objects) <= 1:
        return objects
    select_only(objects)
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = "sunray150_audit_gazebo_visual"
    joined.data.name = "sunray150_audit_gazebo_visual_mesh"
    return [joined]


def export_obj(out_obj: Path) -> None:
    bpy.ops.wm.obj_export(
        filepath=str(out_obj),
        check_existing=False,
        export_selected_objects=True,
        export_uv=True,
        export_normals=True,
        export_materials=True,
        path_mode="AUTO",
        apply_modifiers=True,
        apply_transform=True,
        export_triangulated_mesh=True,
        export_object_groups=True,
        export_material_groups=True,
    )


def apply_gazebo_mtl_overrides(out_mtl: Path) -> list[dict[str, str]]:
    if not out_mtl.exists():
        raise FileNotFoundError(out_mtl)

    lines = out_mtl.read_text(encoding="utf-8", errors="ignore").splitlines()
    current_material: str | None = None
    patched_lines: list[str] = []
    applied: list[dict[str, str]] = []
    seen_keys: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("newmtl "):
            append_missing_material_overrides(patched_lines, current_material, seen_keys, applied)
            current_material = stripped.split(maxsplit=1)[1]
            seen_keys = set()

        key = stripped.split(maxsplit=1)[0] if stripped else ""
        if current_material and key:
            seen_keys.add(key)
        overrides = GAZEBO_MTL_OVERRIDES.get(current_material or "")
        if overrides and key in overrides:
            value = overrides[key]
            if value is None:
                applied.append(
                    {
                        "material": current_material or "",
                        "key": key,
                        "value": "",
                        "action": "remove",
                    }
                )
                continue
            patched_lines.append(f"{key} {value}")
            applied.append(
                {
                    "material": current_material or "",
                    "key": key,
                    "value": value,
                    "action": "replace",
                }
            )
        else:
            patched_lines.append(line)

    append_missing_material_overrides(patched_lines, current_material, seen_keys, applied)
    out_mtl.write_text("\n".join(patched_lines) + "\n", encoding="utf-8")
    return applied


def text_contains(path: Path, token: str) -> bool:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if token in line:
                return True
    return False


def main() -> None:
    start = time.time()
    args = parse_args()
    source_blend = resolved(args.source_blend)
    output_dir = resolved(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_obj = output_dir / f"{args.output_stem}.obj"
    out_mtl = output_dir / f"{args.output_stem}.mtl"
    out_manifest = output_dir / f"{args.output_stem}_manifest.json"

    if not source_blend.exists():
        raise FileNotFoundError(source_blend)

    bpy.ops.wm.open_mainfile(filepath=str(source_blend))
    meshes = visible_meshes()
    if not meshes:
        raise RuntimeError("No visible mesh objects found in the accepted audit blend.")

    materials = sorted(
        {slot.material.name for obj in meshes for slot in obj.material_slots if slot.material}
    )
    source_names = [obj.name for obj in meshes]
    export_objects = maybe_join(meshes) if args.join else meshes
    select_only(export_objects)
    export_obj(out_obj)
    mtl_overrides_applied = apply_gazebo_mtl_overrides(out_mtl)

    validation = {
        "expected_tokens": {token: text_contains(out_obj, token) for token in EXPECTED_SOURCE_TOKENS},
        "forbidden_tokens": {token: text_contains(out_obj, token) for token in FORBIDDEN_SOURCE_TOKENS},
    }
    ok = all(validation["expected_tokens"].values()) and not any(
        validation["forbidden_tokens"].values()
    )
    if args.join:
        # Joined export cannot preserve source object names in OBJ, so validate
        # source scene names instead.
        joined_expected = {token: any(token in name for name in source_names) for token in EXPECTED_SOURCE_TOKENS}
        validation["expected_tokens_in_source_scene"] = joined_expected
        ok = all(joined_expected.values()) and not any(validation["forbidden_tokens"].values())

    payload = {
        "schema": "mosim.sunray150.audit_blend_gazebo_obj_export.v1",
        "ok": ok,
        "source_route": "user_confirmed_005_dae_derived_blender_visual_baseline",
        "source_blend": str(source_blend),
        "outputs": {
            "obj": str(out_obj),
            "mtl": str(out_mtl),
            "manifest": str(out_manifest),
        },
        "visible_mesh_count": len(meshes),
        "export_object_count": len(export_objects),
        "material_count": len(materials),
        "first_visible_mesh_objects": source_names[:40],
        "first_materials": materials[:40],
        "source_bounds_m": bounds_for(meshes),
        "joined": bool(args.join),
        "validation": validation,
        "gazebo_mtl_overrides_applied": mtl_overrides_applied,
        "claim_boundary": [
            "Exports only the accepted Blender audit visual baseline for Gazebo visual review.",
            "Applies Gazebo-only material overrides so MID360 radar, frame/guard, and propeller visuals remain visible in Gazebo.",
            "Does not change dynamics, collision, sensors, controller, ROS2 topics, or runtime evidence.",
            "Does not prove final visual acceptance until the user reviews the Gazebo window/screenshot.",
        ],
        "elapsed_sec": round(time.time() - start, 3),
    }
    out_manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if not ok:
        raise RuntimeError(f"Gazebo OBJ export validation failed; see {out_manifest}")


if __name__ == "__main__":
    main()
