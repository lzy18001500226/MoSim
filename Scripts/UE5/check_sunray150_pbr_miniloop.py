#!/usr/bin/env python3
"""Validate the Sunray150 carbon/propeller PBR minimum-loop evidence.

This check is intentionally file-level. It does not launch Blender or Unreal.
It verifies that the generated texture maps, component-render manifest, review
images, and geometry guard documentation still support the current manual audit
gate.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEXTURE_MANIFEST = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures" / "sunray150_texture_manifest.json"
REVIEW_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "component_material_reviews"
REVIEW_MANIFEST = REVIEW_DIR / "sunray150_component_material_reviews_manifest.json"
EVIDENCE_DOC = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md"
SKILL_DOC = PROJECT_ROOT / "Docs" / "Skills" / "Unreal" / "sunray-pbr-material-workflow" / "SKILL.md"

TEXTURE_REQUIREMENTS = {
    "carbon_fiber": {
        "base_color": "sunray150_carbon_fiber_base.png",
        "roughness": "sunray150_carbon_fiber_roughness.png",
        "bump": "sunray150_carbon_fiber_bump.png",
    },
    "smoked_propeller": {
        "base_color": "sunray150_smoked_propeller_base.png",
        "roughness": "sunray150_smoked_propeller_roughness.png",
        "bump": "sunray150_smoked_propeller_bump.png",
    },
}

COMPONENT_REQUIREMENTS = {
    "carbon_frame": {
        "image": "carbon_frame.png",
        "material": "Sunray150_ComponentReview_Dark_Woven_Carbon_PBR_Map_Audit",
        "texture_paths": {
            "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_carbon_fiber_base.png",
            "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_carbon_fiber_roughness.png",
            "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_carbon_fiber_bump.png",
        },
    },
    "tri_blade_propeller": {
        "image": "tri_blade_propeller.png",
        "material": "Sunray150_ComponentReview_Smoked_Translucent_Plastic_Propeller_PBR_Map_Audit",
        "texture_paths": {
            "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_smoked_propeller_base.png",
            "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_smoked_propeller_roughness.png",
            "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_smoked_propeller_bump.png",
        },
    },
}

GEOMETRY_GUARDS = [
    "0.833527",
    "sunray_cw.stl",
    "flipped_around_screw_axis",
    "-0.014052",
    "does not export to UE",
]


def load_json(path: Path) -> Any:
    if not path.exists():
        raise AssertionError(f"missing json file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def assert_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    try:
        path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise AssertionError(f"path outside project: {path}") from exc
    return path


def check_image(path: Path, *, expected_mode: str | None = None) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing image: {path}")
    with Image.open(path) as im:
        if expected_mode and im.mode != expected_mode:
            raise AssertionError(f"{path} mode {im.mode} != {expected_mode}")
        if im.size != (1024, 1024) and path.name.endswith(".png") and "Textures" in path.parts:
            raise AssertionError(f"{path} size {im.size} != (1024, 1024)")
        rgb = im.convert("RGB")
        extrema = rgb.getextrema()
        if all(lo == hi for lo, hi in extrema):
            raise AssertionError(f"flat image with no variation: {path}")
        return {"mode": im.mode, "size": im.size, "extrema": extrema, "bytes": path.stat().st_size}


def check_texture_manifest() -> dict[str, Any]:
    manifest = load_json(TEXTURE_MANIFEST)
    result: dict[str, Any] = {}
    for material_key, maps in TEXTURE_REQUIREMENTS.items():
        if material_key not in manifest:
            raise AssertionError(f"texture manifest missing key: {material_key}")
        result[material_key] = {}
        for channel, filename in maps.items():
            actual = Path(manifest[material_key].get(channel, ""))
            if actual.name != filename:
                raise AssertionError(f"{material_key}.{channel} expected {filename}, got {actual}")
            path = assert_project_path(str(actual))
            expected_mode = "RGB" if channel == "base_color" else "L"
            result[material_key][channel] = check_image(path, expected_mode=expected_mode)
    return result


def check_review_manifest() -> dict[str, Any]:
    manifest = load_json(REVIEW_MANIFEST)
    rows = {row.get("name"): row for row in manifest.get("outputs", [])}
    result: dict[str, Any] = {}
    for component, requirement in COMPONENT_REQUIREMENTS.items():
        row = rows.get(component)
        if row is None:
            raise AssertionError(f"review manifest missing component: {component}")
        isolation = row.get("isolation", {})
        if isolation.get("target_object_count", 0) <= 0:
            raise AssertionError(f"{component} has no target objects")
        if isolation.get("override_material") != requirement["material"]:
            raise AssertionError(f"{component} override material mismatch: {isolation.get('override_material')}")
        maps = isolation.get("override_texture_maps", [])
        targets = {item.get("target") for item in maps}
        if not {"Base Color", "Roughness", "Bump"} <= targets:
            raise AssertionError(f"{component} missing texture targets: {sorted({'Base Color', 'Roughness', 'Bump'} - targets)}")
        paths = {item.get("project_relative_path") for item in maps}
        missing_paths = requirement["texture_paths"] - paths
        if missing_paths:
            raise AssertionError(f"{component} missing texture paths: {sorted(missing_paths)}")
        image_path = REVIEW_DIR / requirement["image"]
        image_info = check_image(image_path)
        result[component] = {
            "target_object_count": isolation["target_object_count"],
            "override_material": isolation["override_material"],
            "texture_targets": sorted(targets),
            "image": image_info,
        }
    return result


def check_docs() -> dict[str, Any]:
    evidence = EVIDENCE_DOC.read_text(encoding="utf-8")
    skill = SKILL_DOC.read_text(encoding="utf-8")
    missing = [token for token in GEOMETRY_GUARDS if token not in evidence and token not in skill]
    if missing:
        raise AssertionError(f"missing geometry guard tokens in docs: {missing}")
    if "smoked translucent plastic" not in evidence or "smoked translucent plastic" not in skill:
        raise AssertionError("smoked translucent plastic material target is not documented in both docs")
    if "opaque black" not in evidence or "opaque black" not in skill:
        raise AssertionError("opaque-black rejection is not documented in both docs")
    return {
        "evidence_doc": str(EVIDENCE_DOC.relative_to(PROJECT_ROOT)),
        "skill_doc": str(SKILL_DOC.relative_to(PROJECT_ROOT)),
        "geometry_guards": GEOMETRY_GUARDS,
    }


def main() -> int:
    result = {
        "texture_manifest": check_texture_manifest(),
        "review_manifest": check_review_manifest(),
        "docs": check_docs(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
