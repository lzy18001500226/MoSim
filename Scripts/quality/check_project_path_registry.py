#!/usr/bin/env python3
"""Validate the explicit MoSim component-path registry without starting a runtime."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


VALID_STATES = {"legacy_active", "copied_pending_activation", "canonical_active"}
LEGACY_PREFIXES = ("References/", "apps/flight_console/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(os.environ.get("MOSIM_PROJECT_ROOT", Path(__file__).resolve().parents[2])),
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("Config/project_paths.json"),
    )
    parser.add_argument(
        "--require-canonical-active",
        action="store_true",
        help="fail unless every registered component uses its canonical path",
    )
    return parser.parse_args()


def normalized_relative_path(value: Any, field: str, component_id: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value:
        errors.append(f"{component_id}.{field}: missing string")
        return ""
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        errors.append(f"{component_id}.{field}: must be a repository-relative POSIX path")
    return value.rstrip("/")


def validate_component(
    project_root: Path,
    component_id: str,
    component: Any,
    require_canonical_active: bool,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(component, dict):
        return [f"{component_id}: component must be an object"], {}

    canonical = normalized_relative_path(component.get("canonical_relpath"), "canonical_relpath", component_id, errors)
    legacy = normalized_relative_path(component.get("legacy_relpath"), "legacy_relpath", component_id, errors)
    active = normalized_relative_path(component.get("active_relpath"), "active_relpath", component_id, errors)
    state = component.get("migration_state")

    if not canonical.startswith("src/"):
        errors.append(f"{component_id}.canonical_relpath: must live under src/")
    if not legacy.startswith(LEGACY_PREFIXES):
        errors.append(f"{component_id}.legacy_relpath: must be an approved retained legacy root")
    if active not in {canonical, legacy}:
        errors.append(f"{component_id}.active_relpath: must equal canonical_relpath or legacy_relpath")
    if state not in VALID_STATES:
        errors.append(f"{component_id}.migration_state: unsupported value {state!r}")

    expected_active = {
        "legacy_active": legacy,
        "copied_pending_activation": legacy,
        "canonical_active": canonical,
    }.get(state)
    if expected_active and active != expected_active:
        errors.append(f"{component_id}: state {state} requires active_relpath={expected_active}")

    legacy_exists = bool(legacy) and (project_root / legacy).is_dir()
    canonical_exists = bool(canonical) and (project_root / canonical).is_dir()
    if not legacy_exists:
        errors.append(f"{component_id}: retained legacy path is missing: {legacy}")
    if active and not (project_root / active).is_dir():
        errors.append(f"{component_id}: active path is missing: {active}")
    if state == "copied_pending_activation" and not canonical_exists:
        errors.append(f"{component_id}: copied_pending_activation requires canonical path: {canonical}")
    if state == "canonical_active" and not canonical_exists:
        errors.append(f"{component_id}: canonical_active requires canonical path: {canonical}")
    if require_canonical_active and state != "canonical_active":
        errors.append(f"{component_id}: canonical activation is required but state is {state}")

    return errors, {
        "component_id": component_id,
        "migration_state": state,
        "legacy_exists": legacy_exists,
        "canonical_exists": canonical_exists,
        "active_relpath": active,
    }


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    registry_path = args.registry if args.registry.is_absolute() else project_root / args.registry
    errors: list[str] = []
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [f"registry_read_failed: {exc}"]}, indent=2))
        return 2

    components = registry.get("components") if isinstance(registry, dict) else None
    if not isinstance(components, dict) or not components:
        print(json.dumps({"valid": False, "errors": ["components: non-empty object required"]}, indent=2))
        return 2

    records: list[dict[str, Any]] = []
    for component_id, component in components.items():
        component_errors, record = validate_component(
            project_root, component_id, component, args.require_canonical_active
        )
        errors.extend(component_errors)
        records.append(record)

    states = Counter(record.get("migration_state") for record in records)
    payload = {
        "catalog_id": registry.get("catalog_id"),
        "project_root": str(project_root),
        "registry": str(registry_path),
        "valid": not errors,
        "component_count": len(records),
        "states": dict(sorted(states.items())),
        "components": records,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
