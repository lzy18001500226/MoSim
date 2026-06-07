#!/usr/bin/env python3
"""Check Sunray150 component-review path hygiene without launching Blender/UE."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "component_material_reviews" / "sunray150_component_material_reviews_manifest.json"
REQUIRED_COMPONENTS = {"battery", "guard_landing_gear"}


def project_relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def resolve_project_path(path_text: str) -> Path:
    path = Path(path_text.replace("\\", "/"))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    try:
        path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise AssertionError(f"path outside project: {path}") from exc
    return path


def is_absolute_path_text(value: Any) -> bool:
    return isinstance(value, str) and Path(value.replace("\\", "/")).is_absolute()


def image_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing component image: {path}")
    if path.stat().st_size <= 0:
        raise AssertionError(f"empty component image: {path}")
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        extrema = rgb.getextrema()
        non_flat = not all(lo == hi for lo, hi in extrema)
        if not non_flat:
            raise AssertionError(f"flat component image: {path}")
        return {
            "project_relative_path": project_relative(path),
            "bytes": path.stat().st_size,
            "mode": image.mode,
            "dimensions": list(image.size),
            "non_flat": non_flat,
        }


def build_report() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    outputs = manifest.get("outputs", [])
    rows = {row.get("name"): row for row in outputs if row.get("name")}
    missing_required = sorted(REQUIRED_COMPONENTS - rows.keys())
    if missing_required:
        raise AssertionError(f"manifest missing required components: {missing_required}")

    missing_project_relative = sorted(
        row.get("name", "<unnamed>")
        for row in outputs
        if not row.get("project_relative_path")
    )
    if missing_project_relative:
        raise AssertionError(f"manifest rows missing project_relative_path: {missing_project_relative}")

    component_index = []
    legacy_absolute_rows = []
    for row in outputs:
        name = row.get("name")
        rel = row.get("project_relative_path")
        path = resolve_project_path(rel)
        entry = {
            "name": name,
            **image_info(path),
            "manual_review_status": "pending",
        }
        if is_absolute_path_text(row.get("path")):
            legacy_absolute_rows.append(name)
            entry["legacy_absolute_path_quarantined"] = True
        component_index.append(entry)

    return {
        "schema_version": "mosim.sunray150_component_review_path_hygiene.v1",
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source_manifest": project_relative(MANIFEST),
        "path_policy": {
            "future_review_routing_field": "project_relative_path",
            "do_not_use_legacy_path_for_review_routing": True,
            "source_manifest_all_outputs_have_project_relative_path": not missing_project_relative,
            "source_manifest_legacy_absolute_path_field_count": len(legacy_absolute_rows),
            "source_manifest_top_level_source_blend_absolute": is_absolute_path_text(manifest.get("source_blend")),
            "legacy_absolute_fields_status": "quarantined_existing_manifest_only",
        },
        "quality_boundary": {
            "file_level_checks_passed": True,
            "manual_visual_review_required": True,
            "final_material_acceptance": False,
            "ue_import_export_final_acceptance": False,
            "runtime_evidence": False,
        },
        "required_components": {
            "battery_present": "battery" in rows,
            "guard_landing_gear_present": "guard_landing_gear" in rows,
        },
        "component_index": component_index,
        "legacy_absolute_rows": legacy_absolute_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report()
    output = args.output
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(project_relative(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
