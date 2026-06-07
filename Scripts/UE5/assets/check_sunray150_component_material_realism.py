#!/usr/bin/env python3
"""Check Sunray150 component material review images and build a contact sheet.

This is a file-level audit helper. It does not launch Blender or Unreal and it
does not assert final material acceptance.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REVIEW_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "component_material_reviews"
MANIFEST = REVIEW_DIR / "sunray150_component_material_reviews_manifest.json"
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_pbr_electronics_camera_realism_20260606_005"

TARGET_COMPONENTS = [
    "front_camera",
    "pcb_boards",
    "n150_stack_boards",
    "n150_internal_pcb_audit",
    "n150_ports",
    "n150_cooling_storage",
    "esc_board",
    "electronics_connectors",
    "connector_shells",
    "cables_wires",
    "battery",
    "guard_landing_gear",
]

PBR_TARGETS = {"Base Color", "Roughness", "Bump"}


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.resolve().relative_to(PROJECT_ROOT.resolve())
    return path


def image_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing image: {path}")
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        extrema = rgb.getextrema()
        non_flat = not all(lo == hi for lo, hi in extrema)
        sample = rgb.resize((64, 48))
        colors = sample.getcolors(maxcolors=64 * 48)
        return {
            "path": project_relative(path),
            "bytes": path.stat().st_size,
            "mode": image.mode,
            "dimensions": list(image.size),
            "non_flat": non_flat,
            "rgb_extrema": extrema,
            "sample_unique_color_count": len(colors or []),
        }


def pbr_maps_for_row(row: dict[str, Any]) -> list[dict[str, Any]]:
    maps = row.get("isolation", {}).get("override_texture_maps", [])
    return [item for item in maps if item.get("target") in PBR_TARGETS]


def validate_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST)
    rows = {row.get("name"): row for row in manifest.get("outputs", [])}
    missing = [name for name in TARGET_COMPONENTS if name not in rows]
    if missing:
        raise AssertionError(f"missing component rows: {missing}")

    components = []
    for name in TARGET_COMPONENTS:
        row = rows[name]
        image_path = resolve_project_path(row.get("project_relative_path", f"{REVIEW_DIR.name}/{name}.png"))
        info = image_info(image_path)
        if not info["non_flat"]:
            raise AssertionError(f"flat image: {name}")
        maps = pbr_maps_for_row(row)
        targets = {item.get("target") for item in maps}
        missing_targets = sorted(PBR_TARGETS - targets)
        if missing_targets:
            raise AssertionError(f"{name} missing PBR map targets: {missing_targets}")
        components.append(
            {
                "name": name,
                "image": info,
                "target_object_count": row.get("isolation", {}).get("target_object_count"),
                "override_material": row.get("isolation", {}).get("override_material"),
                "pbr_targets": sorted(targets),
                "pbr_maps": maps,
                "manual_review_status": "pending",
            }
        )
    return {
        "schema_version": "mosim.sunray150_component_material_realism_check.v1",
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "source_manifest": project_relative(MANIFEST),
        "target_components": TARGET_COMPONENTS,
        "quality_boundary": {
            "file_level_checks_passed": True,
            "manual_visual_review_required": True,
            "final_material_acceptance": False,
            "ue_import_export_final_acceptance": False,
            "runtime_evidence": False,
        },
        "component_index": components,
        "known_limits": [
            "File-level checks verify image readability, non-flat pixels, and connected PBR map targets only.",
            "Mixed electronics components still need human review for per-subcomponent material realism.",
        ],
    }


def build_contact_sheet(report: dict[str, Any], output: Path) -> None:
    thumb_w, thumb_h = 360, 270
    label_h = 42
    cols = 3
    rows = (len(report["component_index"]) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (28, 30, 32))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for idx, component in enumerate(report["component_index"]):
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        with Image.open(PROJECT_ROOT / component["image"]["path"]) as image:
            thumb = image.convert("RGB")
            thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            px = x + (thumb_w - thumb.width) // 2
            py = y + (thumb_h - thumb.height) // 2
            sheet.paste(thumb, (px, py))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(18, 20, 22))
        draw.text((x + 10, y + thumb_h + 10), component["name"], fill=(235, 238, 240), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    args = parser.parse_args()
    evidence_dir = resolve_project_path(args.evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    report = validate_manifest()
    contact_sheet = evidence_dir / "sunray150_electronics_camera_realism_contact_sheet.png"
    build_contact_sheet(report, contact_sheet)
    report["contact_sheet"] = project_relative(contact_sheet)
    evidence_json = evidence_dir / "material_realism_evidence.json"
    evidence_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(project_relative(evidence_json))
    print(project_relative(contact_sheet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
