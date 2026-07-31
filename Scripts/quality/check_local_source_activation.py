#!/usr/bin/env python3
"""Check that the nine migrated components resolve only through project src."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMPONENT_IDS = (
    "sunray_planner_utils",
    "sunray_tutorial",
    "fuel",
    "falcon",
    "racer",
    "diff_planner",
    "ego_planner_swarm",
    "fixed_formation",
    "qgroundcontrol",
)
ACTIVE_CONSUMERS = (
    "Config/profiles/runtime_bindings.json",
    "Config/runtime/ros1_local_source_manifest.v1.json",
    "Scripts/sunray/check_fuel_ros1_preflight.sh",
    "Scripts/sunray/build_fuel_ros1_upstream_smoke.sh",
    "Scripts/sunray/check_falcon_ros1_preflight.sh",
    "Scripts/sunray/build_falcon_f1_minimal_build_probe.sh",
    "Scripts/sunray/build_racer_ros1_upstream_smoke.sh",
    "Scripts/sunray/build_swarm_formation_ros1_upstream_smoke.sh",
    "Scripts/sunray/setup_goal4_diff_planner_overlay.sh",
    "Scripts/sunray/setup_goal4_ego_overlay.sh",
    "Scripts/sunray/run_px4ctrl_ego_single_gate.sh",
    "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh",
    "Scripts/sunray/setup_sunray_livox_gazebo_plugin.sh",
    "Scripts/ui/build_flight_console.ps1",
    "Scripts/ui/materialize_qgc_custom_overlay.py",
    "Scripts/ui/generate_qgc_vendor_manifest.py",
    "src/planning/falcon/falcon_planner/exploration_utils/resource/coverage_path.par",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def entrypoint_path(value: str) -> str:
    return value.split("#", 1)[0]


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    registry_path = root / "Config/project_paths.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    components: dict[str, Any] = registry["components"]
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    legacy_tokens: list[str] = []

    for component_id in COMPONENT_IDS:
        component = components.get(component_id)
        if not isinstance(component, dict):
            errors.append(f"missing_component:{component_id}")
            continue
        canonical = component.get("canonical_relpath")
        active = component.get("active_relpath")
        legacy = component.get("legacy_relpath")
        state = component.get("migration_state")
        entrypoints = component.get("entrypoints", [])
        if state != "canonical_active" or active != canonical:
            errors.append(f"not_canonical_active:{component_id}")
        if not isinstance(canonical, str) or not (root / canonical).is_dir():
            errors.append(f"missing_canonical_path:{component_id}:{canonical}")
        missing_entrypoints = [
            value for value in entrypoints if not (root / entrypoint_path(value)).exists()
        ]
        if missing_entrypoints:
            errors.extend(f"missing_entrypoint:{component_id}:{value}" for value in missing_entrypoints)
        if isinstance(legacy, str):
            legacy_tokens.append(legacy)
        records.append(
            {
                "component_id": component_id,
                "canonical_relpath": canonical,
                "active_relpath": active,
                "entrypoints": entrypoints,
                "missing_entrypoints": missing_entrypoints,
            }
        )

    direct_legacy_hits: list[dict[str, str]] = []
    for consumer_relpath in ACTIVE_CONSUMERS:
        consumer = root / consumer_relpath
        if not consumer.is_file():
            errors.append(f"missing_active_consumer:{consumer_relpath}")
            continue
        text = consumer.read_text(encoding="utf-8", errors="replace")
        for token in legacy_tokens:
            if token in text:
                direct_legacy_hits.append({"file": consumer_relpath, "legacy_path": token})
    errors.extend(f"direct_legacy_reference:{hit['file']}:{hit['legacy_path']}" for hit in direct_legacy_hits)

    payload = {
        "schema": "mosim.local_source_activation_check.v1",
        "project_root": str(root),
        "component_count": len(records),
        "components": records,
        "active_consumer_count": len(ACTIVE_CONSUMERS),
        "direct_legacy_hits": direct_legacy_hits,
        "valid": not errors,
        "errors": errors,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        report = args.report if args.report.is_absolute() else root / args.report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
