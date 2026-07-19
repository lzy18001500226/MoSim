#!/usr/bin/env python3
"""Validate the allowlisted runtime backend catalog without launching runtime."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
DEFAULT_RUNNER = ROOT / "Scripts" / "ui" / "run_orchestrated_runtime.sh"
DEFAULT_QML = ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src" / "FlyViewCustomLayer.qml"
PROFILE_PATTERN = re.compile(
    r'\{\s*id:\s*"(?P<id>[^"]+)".*?path:\s*"(?P<path>[^"]+)"'
    r'.*?controller:\s*"(?P<controller>[^"]+)".*?count:\s*(?P<count>\d+)'
    r'.*?enabled:\s*(?P<enabled>true|false)',
)
RUNNER_OPERATION_PATTERN = re.compile(r"^  ([a-z][a-z0-9_]*)\)$", re.MULTILINE)


def check(catalog_path: Path, runner_path: Path = DEFAULT_RUNNER, qml_path: Path = DEFAULT_QML) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    identifiers: set[str] = set()
    operation_ids: set[str] = set()
    runtime_keys: set[tuple[str, str, int]] = set()
    runner_text = runner_path.read_text(encoding="utf-8") if runner_path.is_file() else ""
    runner_operations = set(RUNNER_OPERATION_PATTERN.findall(runner_text))
    for entry in catalog.get("runtime_profiles", []):
        identifier = entry.get("runtime_profile_id", "")
        if not identifier or identifier in identifiers:
            errors.append(f"duplicate_or_missing_runtime_profile_id:{identifier}")
        identifiers.add(identifier)
        operation_id = entry.get("operation_id", "")
        if not operation_id or operation_id in operation_ids:
            errors.append(f"duplicate_or_missing_operation_id:{operation_id}")
        operation_ids.add(operation_id)
        if operation_id not in runner_operations:
            errors.append(f"runner_operation_missing:{identifier}:{operation_id}")
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
        for profile_id in entry.get("experiment_profile_ids", []):
            profile_path = ROOT / "Config" / "profiles" / "experiments" / f"{profile_id}.json"
            if not profile_path.is_file():
                errors.append(f"experiment_profile_missing:{identifier}:{profile_id}")
                continue
            profile = json.loads(profile_path.read_text(encoding="utf-8")).get("experiment_profile", {})
            if profile.get("id") != profile_id:
                errors.append(f"experiment_profile_id_mismatch:{identifier}:{profile_id}")
            declared_count = int(profile.get("vehicle_count", 1))
            if declared_count not in entry.get("vehicle_counts", []):
                errors.append(f"experiment_vehicle_count_mismatch:{identifier}:{profile_id}:{declared_count}")
            for controller_id in entry.get("controller_ids", []):
                key = (profile_id, controller_id, declared_count)
                if key in runtime_keys:
                    errors.append(f"duplicate_runtime_selection:{profile_id}:{controller_id}:{declared_count}")
                runtime_keys.add(key)
    for operation_id in sorted(runner_operations - operation_ids):
        errors.append(f"runner_operation_not_catalogued:{operation_id}")

    qml_profiles: list[dict[str, object]] = []
    qml_text = qml_path.read_text(encoding="utf-8") if qml_path.is_file() else ""
    for match in PROFILE_PATTERN.finditer(qml_text):
        item = {
            "id": match.group("id"),
            "path": match.group("path"),
            "controller": match.group("controller"),
            "count": int(match.group("count")),
            "enabled": match.group("enabled") == "true",
        }
        qml_profiles.append(item)
        profile_path = ROOT / str(item["path"])
        if not profile_path.is_file():
            errors.append(f"qgc_profile_path_missing:{item['id']}:{item['path']}")
            continue
        profile = json.loads(profile_path.read_text(encoding="utf-8")).get("experiment_profile", {})
        if profile.get("id") != item["id"]:
            errors.append(f"qgc_profile_id_mismatch:{item['id']}:{profile.get('id', '')}")
        selection = (str(item["id"]), str(item["controller"]), int(item["count"]))
        if selection not in runtime_keys:
            errors.append(f"qgc_runtime_selection_missing:{':'.join(map(str, selection))}")
    if not qml_profiles:
        errors.append("qgc_profile_catalog_missing")
    for helper in ("Scripts/ui/run_orchestrated_runtime.sh", "Scripts/ui/stop_orchestrated_runtime.sh"):
        if not (ROOT / helper).is_file():
            errors.append(f"helper_missing:{helper}")
    return {
        "schema": "mosim.orchestrator.runtime_backend_source_gate.v1",
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "runtime_profile_count": len(identifiers),
        "runner_operation_count": len(runner_operations),
        "qgc_profile_count": len(qml_profiles),
        "shared_gazebo_px4_touched": False,
        "actual_end_to_end_runtime_accepted": False,
        "claim_ceiling": "Runtime catalog and fixed project launcher source only; live startup, readiness, stop, and residue gates remain pending.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--qml", type=Path, default=DEFAULT_QML)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.catalog, args.runner, args.qml)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
