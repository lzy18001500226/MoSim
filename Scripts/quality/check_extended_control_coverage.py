#!/usr/bin/env python3
"""Report exact Registry coverage for every expanded control algorithm id."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCOPE = ROOT / "Config" / "control_platform" / "extended_control_scope_catalog.json"
DEFAULT_REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"


def build_report(scope: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    modules = {
        str(module.get("algorithm_id", module.get("module_id", ""))): module
        for module in registry.get("modules", [])
        if isinstance(module, dict)
    }
    rows: list[dict[str, Any]] = []
    for family in scope.get("families", []):
        for algorithm_id in family.get("required_algorithm_ids", []):
            module = modules.get(algorithm_id)
            rows.append({
                "family_id": family.get("family_id"),
                "algorithm_id": algorithm_id,
                "registry_module_id": module.get("module_id") if module else None,
                "status": module.get("status", "unregistered") if module else "unregistered",
                "selectable": module.get("selectable", False) if module else False,
                "claim_ceiling": module.get("claim_ceiling", "none") if module else "none",
            })
    counts = Counter(row["status"] for row in rows)
    return {
        "schema": "mosim.control_platform.extended_coverage_report.v1",
        "algorithm_count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "registered_count": sum(row["status"] != "unregistered" for row in rows),
        "selectable_count": sum(bool(row["selectable"]) for row in rows),
        "accepted_count": sum(row["status"] == "accepted" for row in rows),
        "complete": all(row["status"] == "accepted" for row in rows),
        "algorithms": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    report = build_report(
        json.loads(args.scope.read_text(encoding="utf-8")),
        json.loads(args.registry.read_text(encoding="utf-8")),
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
