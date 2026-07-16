#!/usr/bin/env python3
"""Validate the allowlisted runtime backend catalog without launching runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"


def check(catalog_path: Path) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    identifiers: set[str] = set()
    for entry in catalog.get("runtime_profiles", []):
        identifier = entry.get("runtime_profile_id", "")
        if not identifier or identifier in identifiers:
            errors.append(f"duplicate_or_missing_runtime_profile_id:{identifier}")
        identifiers.add(identifier)
        if entry.get("launcher") != "wsl_project_script":
            errors.append(f"unsupported_launcher:{identifier}")
        if "command" in entry or "arguments" in entry:
            errors.append(f"arbitrary_command_surface_forbidden:{identifier}")
        script = ROOT / entry.get("project_script", "")
        if not script.is_file() or not script.resolve().is_relative_to(ROOT):
            errors.append(f"project_script_missing_or_external:{identifier}")
        if not entry.get("experiment_profile_ids") or not entry.get("controller_ids"):
            errors.append(f"profile_or_controller_allowlist_missing:{identifier}")
        if not set(entry.get("vehicle_counts", [])) <= {1, 3}:
            errors.append(f"unaccepted_vehicle_scale:{identifier}")
    for helper in ("Scripts/ui/run_orchestrated_runtime.sh", "Scripts/ui/stop_orchestrated_runtime.sh"):
        if not (ROOT / helper).is_file():
            errors.append(f"helper_missing:{helper}")
    return {
        "schema": "mosim.orchestrator.runtime_backend_source_gate.v1",
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "runtime_profile_count": len(identifiers),
        "shared_gazebo_px4_touched": False,
        "actual_end_to_end_runtime_accepted": False,
        "claim_ceiling": "Runtime catalog and fixed project launcher source only; live startup, readiness, stop, and residue gates remain pending.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.catalog)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
