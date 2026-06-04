#!/usr/bin/env python3
"""Probe Sunray150 DAE component names for material/texturing planning."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROP_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_sunray150_with_mid360_propeller_assembly_audit_scene.py"
OUT = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray150_material_component_probe_20260603.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    prop = load_module(PROP_AUDIT, "sunray_prop_material_probe")
    objs = prop.dae_objects(prop.DAE_PATH)
    patterns = [
        ("carbon_frame", r"MAIN_STRUCTURE|TOP_PANNEL|BOT_PANNEL|ARM_|PANNEL|PLATE"),
        ("protective_ring_landing", r"PROTECTIVE_RING|LAND_GEAR|PROTECT_ARC"),
        ("mid360_or_mount", r"MID360|LIVOX"),
        ("camera", r"CAMERA|D435|REALSENSE|USB|LENS"),
        ("motor", r"MOTOR"),
        ("propeller_or_hub", r"PROPELLER|CIRCPATTERN"),
        ("screw_fastener", r"SCREW|NUT|WASHER|BOLT"),
        ("spacer_standoff", r"SPACER|STAND|COLUMN"),
        ("connector_wire", r"CONNECTOR|WIRE|CABLE|PLUG|USB"),
    ]
    categories: dict[str, list[dict]] = {key: [] for key, _ in patterns}
    categories["other"] = []
    for obj in objs:
        upper = obj.name.upper()
        key = "other"
        for candidate, pattern in patterns:
            if re.search(pattern, upper):
                key = candidate
                break
        size = obj.max_bound - obj.min_bound
        categories[key].append(
            {
                "name": obj.name,
                "center_m": [round(obj.center.x, 6), round(obj.center.y, 6), round(obj.center.z, 6)],
                "size_m": [round(size.x, 6), round(size.y, 6), round(size.z, 6)],
            }
        )
    summary = {
        "source": str(prop.DAE_PATH),
        "total_objects": len(objs),
        "category_counts": {key: len(value) for key, value in categories.items()},
        "categories": categories,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(OUT), "counts": summary["category_counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
