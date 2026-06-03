#!/usr/bin/env python3
"""Write the complete close-up manifest without re-rendering images."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
BLEND = AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT_DIR = AUDIT_DIR / "material_closeups"
MANIFEST = OUT_DIR / "sunray150_material_closeups_manifest.json"

VIEWS = [
    ("mid360_housing_window_connector", (0.0, 0.032, 0.086), (0.030, -0.115, 0.030), 0.105, "MID-360 silver housing, blue optical window, black connector, screw details, and protection arc."),
    ("front_usb_camera_battery", (0.0, 0.072, 0.019), (0.018, -0.120, 0.020), 0.115, "Front USB camera, battery pack area, connector holes, and black camera/glass material."),
    ("pcb_connectors_cables", (0.030, 0.052, 0.017), (0.085, -0.080, 0.035), 0.085, "N150/ESC PCB stack, USB/HDMI connector metal, and colored cable hints."),
    ("carbon_frame_gold_standoffs", (0.0, 0.006, 0.020), (0.090, -0.105, 0.055), 0.135, "Carbon fiber plates, gold aluminum standoffs, screws, and stack separation."),
    ("motor_prop_guard", (0.055, 0.055, -0.012), (0.055, -0.070, 0.040), 0.080, "Motor bell, copper windings, propeller material, screws, and smoked guard."),
]


def main() -> None:
    outputs = []
    for name, center, camera_offset, ortho_scale, purpose in VIEWS:
        path = OUT_DIR / f"{name}.png"
        if not path.exists():
            continue
        outputs.append(
            {
                "name": name,
                "path": str(path),
                "project_relative_path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "center_m": list(center),
                "camera_offset_m": list(camera_offset),
                "ortho_scale": ortho_scale,
                "purpose": purpose,
            }
        )
    MANIFEST.write_text(
        json.dumps(
            {
                "source_blend": str(BLEND),
                "source_blend_project_relative": str(BLEND.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "outputs": outputs,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(str(MANIFEST))


if __name__ == "__main__":
    main()
