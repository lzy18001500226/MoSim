#!/usr/bin/env python3
"""Write the Sunray150 material audit package from current manifests."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
TEXTURE_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures"
RESULT_DIR = PROJECT_ROOT / "Results" / "unreal_scene_mapping"
OUT_MD = RESULT_DIR / "SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md"
OUT_JSON = RESULT_DIR / "sunray150_mid360_material_audit_package_20260603.json"


COMPONENT_PLAN = [
    {
        "component": "carbon frame plates / top panel / main structure",
        "source_names": ["MAIN_STRUCTURE", "TOP_PANNEL", "BOT_PANNEL", "Fill"],
        "material": "dark graphite woven carbon fiber",
        "texture_maps": [
            "sunray150_carbon_fiber_base.png",
            "sunray150_carbon_fiber_roughness.png",
            "sunray150_carbon_fiber_bump.png",
        ],
        "evidence": "Local DAE part names and Sunray/CUAV visual references show dark carbon composite frame plates, not white plastic.",
    },
    {
        "component": "MID-360 protection structure",
        "source_names": ["PROTECTIVE_RING", "MID360_PROTECT_ARC*", "MID360_PROTECT_ARC_CONNECTOR*"],
        "material": "matte black / dark grey low-reflection plastic or composite",
        "texture_maps": ["sunray150_black_rubber_base.png", "sunray150_black_rubber_roughness.png", "sunray150_black_rubber_bump.png"],
        "evidence": "YunDrone MID-360 protection cover references and local DAE names indicate a dark protective structure; previous white/blue broad coloring was rejected.",
    },
    {
        "component": "Livox MID-360 visual sensor",
        "source_names": ["AUDIT_STANDALONE_MID360_013/014/015/016/017"],
        "material": "satin silver-grey housing, blue optical window, black M12 connector/base",
        "texture_maps": ["mid360_silver_grey_aluminum_base.png", "mid360_silver_grey_aluminum_roughness.png", "mid360_silver_grey_aluminum_bump.png"],
        "evidence": "Livox MID-360 product references show blue optical dome/window with grey housing and black connector/base.",
    },
    {
        "component": "propellers",
        "source_names": ["sunray_cw.stl fitted to DAE M2 screw pairs"],
        "material": "dark smoked composite propeller",
        "texture_maps": ["sunray150_smoked_translucent_guard_base.png", "sunray150_smoked_translucent_guard_roughness.png"],
        "evidence": "User accepted three-blade geometry from local Sunray source; material remains dark composite until physical photo audit refines it.",
    },
    {
        "component": "motors and screws",
        "source_names": ["MOTOR", "STATOR WIRE", "SCREW", "NUT", "WASHER"],
        "material": "black motor bell, copper winding hints, brushed/dark steel screws",
        "texture_maps": ["sunray150_dark_anodized_metal_base.png", "sunray150_dark_anodized_metal_roughness.png"],
        "evidence": "DAE object names expose motor, stator wire, and screw families; material assignment separates metal, copper, and plastic roles.",
    },
    {
        "component": "electronics, cameras, connectors, cables",
        "source_names": ["N150", "PCBModel", "FRONT_CAMERA", "BOTTOM_CAMERA", "USB", "HDMI", "CABLE"],
        "material": "black PCB/camera bodies, nickel connector shells, colored cable hints",
        "texture_maps": ["sunray150_pcb_black_base.png", "sunray150_black_rubber_base.png"],
        "evidence": "Local DAE object hierarchy exposes N150/USB/HDMI/camera/cable groups; overlays mark cable and camera-lens intent without changing geometry.",
    },
]


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    assembly_manifest = load_json(AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit_manifest.json")
    texture_manifest = load_json(TEXTURE_DIR / "sunray150_texture_manifest.json")
    closeup_manifest = load_json(AUDIT_DIR / "material_closeups" / "sunray150_material_closeups_manifest.json")

    invariants = {
        "mid360_uniform_scale": assembly_manifest.get("mid360", {}).get("hole_fit", {}).get("uniform_scale"),
        "propeller_source": assembly_manifest.get("propellers", {}).get("source"),
        "propeller_orientation": assembly_manifest.get("propellers", {}).get("orientation_mode"),
        "propeller_z_rule": assembly_manifest.get("propellers", {}).get("z_rule"),
        "ue_export_allowed": False,
        "status": "manual_blender_material_audit_pending",
    }
    closeups = []
    for item in closeup_manifest.get("outputs", []):
        path = Path(item["path"])
        if path.is_absolute() and str(path).startswith(str(PROJECT_ROOT)):
            item_path = rel(path)
        else:
            item_path = item.get("project_relative_path") or str(path)
        closeups.append({**item, "project_relative_path": item_path})

    package = {
        "status": "manual_blender_material_audit_pending",
        "do_not_export_to_ue_until_manual_acceptance": True,
        "component_plan": COMPONENT_PLAN,
        "geometry_invariants": invariants,
        "texture_manifest": texture_manifest,
        "closeups": closeups,
        "audit_blend": rel(AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"),
    }
    OUT_JSON.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Sunray150 + MID-360 Material Audit Package",
        "",
        "Status: manual Blender material audit pending. Do not export or import this material candidate into UE until manual acceptance.",
        "",
        "## Geometry Invariants",
        "",
        f"- MID-360 four-hole uniform scale: `{invariants['mid360_uniform_scale']}`",
        f"- Propeller source: `{invariants['propeller_source']}`",
        f"- Propeller orientation: `{invariants['propeller_orientation']}`",
        f"- Propeller Z rule: `{invariants['propeller_z_rule']}`",
        "",
        "## Component-Material-Texture Plan",
        "",
    ]
    for item in COMPONENT_PLAN:
        lines.extend(
            [
                f"### {item['component']}",
                "",
                f"- Source names: `{', '.join(item['source_names'])}`",
                f"- Material: {item['material']}",
                f"- Texture maps: `{', '.join(item['texture_maps'])}`",
                f"- Evidence: {item['evidence']}",
                "",
            ]
        )
    lines.extend(["## Audit Outputs", ""])
    lines.append(f"- Audit blend: `{package['audit_blend']}`")
    for item in closeups:
        lines.append(f"- {item['name']}: `{item['project_relative_path']}`")
    lines.extend(["", "## Next Gate", "", "Manual review must accept MID-360 housing/window/connector, carbon frame, USB camera/electronics, motor/propeller, and overall material realism before any UE export."])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
