#!/usr/bin/env python3
"""Build the 006 review contact sheet and image-level check report."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = PROJECT_ROOT / "Results/unreal_scene_mapping/sunray150_pbr_whole_aircraft_grey_cad_realism_20260607_006"
COMPONENT_DIR = PROJECT_ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews"

REVIEW_ITEMS = [
    ("whole_aircraft_iso", EVIDENCE_DIR / "whole_aircraft_iso.png"),
    ("top_electronics_mid360", EVIDENCE_DIR / "top_electronics_mid360.png"),
    ("front_camera_tfmini_electronics", EVIDENCE_DIR / "front_camera_tfmini_electronics.png"),
    ("transparent_guard_propeller_check", EVIDENCE_DIR / "transparent_guard_propeller_check.png"),
    ("mid360_component_closeup", COMPONENT_DIR / "mid360_sensor.png"),
    ("front_camera_component_closeup", COMPONENT_DIR / "front_camera.png"),
    ("bottom_camera_component_closeup", COMPONENT_DIR / "bottom_camera.png"),
    ("tfmini_component_closeup", COMPONENT_DIR / "tfmini_laser_rangefinder.png"),
    ("pcb_n150_component_closeup", COMPONENT_DIR / "n150_ports.png"),
    ("battery_component_closeup", COMPONENT_DIR / "battery.png"),
    ("cables_component_closeup", COMPONENT_DIR / "cables_wires.png"),
    ("guard_component_closeup", COMPONENT_DIR / "guard_landing_gear.png"),
]


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def image_check(path: Path) -> dict:
    if not path.exists():
        return {"path": project_relative(path), "exists": False}
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        stat = ImageStat.Stat(rgb)
        extrema = rgb.getextrema()
        thumb = rgb.resize((96, 72))
        colors = thumb.getcolors(maxcolors=96 * 72)
        return {
            "path": project_relative(path),
            "exists": True,
            "bytes": path.stat().st_size,
            "mode": image.mode,
            "size": list(image.size),
            "mean_rgb": [round(value, 2) for value in stat.mean],
            "stddev_rgb": [round(value, 2) for value in stat.stddev],
            "rgb_extrema": extrema,
            "non_flat": any(lo != hi for lo, hi in extrema),
            "sample_unique_color_count": len(colors or []),
        }


def build_sheet(checks: list[dict], output: Path) -> None:
    thumb_w, thumb_h = 420, 315
    label_h = 46
    cols = 3
    rows = (len(REVIEW_ITEMS) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (24, 26, 28))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for idx, (label, path) in enumerate(REVIEW_ITEMS):
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        draw.rectangle((x, y, x + thumb_w - 1, y + thumb_h + label_h - 1), outline=(58, 63, 68))
        if path.exists():
            with Image.open(path) as image:
                thumb = image.convert("RGB")
                thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                px = x + (thumb_w - thumb.width) // 2
                py = y + (thumb_h - thumb.height) // 2
                sheet.paste(thumb, (px, py))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(15, 17, 19))
        draw.text((x + 10, y + thumb_h + 12), label, fill=(235, 238, 240), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    checks = [image_check(path) | {"name": name} for name, path in REVIEW_ITEMS]
    missing = [row["name"] for row in checks if not row["exists"]]
    flat = [row["name"] for row in checks if row["exists"] and not row["non_flat"]]
    contact_sheet = EVIDENCE_DIR / "sunray150_pbr_006_whole_aircraft_review_contact_sheet.png"
    build_sheet(checks, contact_sheet)
    report = {
        "schema_version": "mosim.sunray150_pbr_006_review_image_check.v1",
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "request_id": "RFLY-MOSIM-SUNRAY150-PBR-WHOLE-AIRCRAFT-GREY-CAD-REALISM-20260607-006",
        "contact_sheet": project_relative(contact_sheet),
        "manual_review_required": True,
        "final_material_acceptance": False,
        "missing_images": missing,
        "flat_images": flat,
        "checks": checks,
    }
    report_path = EVIDENCE_DIR / "sunray150_pbr_006_image_check.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if missing or flat:
        print(json.dumps({"ok": False, "missing": missing, "flat": flat}, ensure_ascii=False))
        return 1
    print(project_relative(report_path))
    print(project_relative(contact_sheet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
