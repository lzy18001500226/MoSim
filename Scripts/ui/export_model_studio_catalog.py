#!/usr/bin/env python3
"""Export Registry/Profile data in a Syslab-friendly tab-separated format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"
PROFILE_CATALOG = ROOT / "Config" / "profiles" / "catalog.json"
RUNTIME_CATALOG = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
EXPERIMENT_DIR = ROOT / "Config" / "profiles" / "experiments"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_catalog() -> dict[str, Any]:
    registry = _read(REGISTRY)
    profile_catalog = _read(PROFILE_CATALOG)
    runtime_catalog = _read(RUNTIME_CATALOG)
    modules = {
        module["profile_id"]: module
        for module in registry.get("modules", [])
        if module.get("kind") == "nominal_controller"
    }
    runtime_keys = {
        (profile_id, controller_id, vehicle_count)
        for entry in runtime_catalog.get("runtime_profiles", [])
        for profile_id in entry.get("experiment_profile_ids", [])
        for controller_id in entry.get("controller_ids", [])
        for vehicle_count in entry.get("vehicle_counts", [])
    }
    profiles = []
    for path in sorted(EXPERIMENT_DIR.glob("*.json")):
        experiment = _read(path).get("experiment_profile", {})
        module = modules.get(experiment.get("controller_profile"))
        scenario = profile_catalog.get("scenario_profiles", {}).get(experiment.get("scenario_profile"), {})
        vehicle_count = experiment.get("vehicle_count", scenario.get("vehicle_count"))
        controller_id = module.get("module_id", "") if module else ""
        enabled = bool(
            module
            and module.get("status") == "accepted"
            and module.get("selectable") is True
            and vehicle_count in {1, 3}
        )
        if not module:
            reason = "controller_not_registered"
        elif module.get("status") != "accepted" or module.get("selectable") is not True:
            reason = "controller_runtime_gate_pending"
        elif vehicle_count not in {1, 3}:
            reason = "vehicle_scale_gate_pending"
        else:
            reason = "enabled"
        profile_id = experiment.get("id", path.stem)
        profiles.append(
            {
                "profile_id": profile_id,
                "profile_path": path.relative_to(ROOT).as_posix(),
                "controller_id": controller_id,
                "vehicle_count": vehicle_count,
                "enabled": enabled,
                "reason_code": reason,
                "runtime_ready": (profile_id, controller_id, vehicle_count) in runtime_keys,
                "description": experiment.get("description", ""),
            }
        )
    controllers = [
        {
            "controller_id": module.get("module_id", ""),
            "profile_id": module.get("profile_id", ""),
            "family": module.get("family", ""),
            "enabled": module.get("status") == "accepted" and module.get("selectable") is True,
            "reason_code": "enabled"
            if module.get("status") == "accepted" and module.get("selectable") is True
            else "runtime_evidence_pending",
        }
        for module in registry.get("modules", [])
        if module.get("kind") == "nominal_controller"
    ]
    available_counts = {profile["vehicle_count"] for profile in profiles if profile["enabled"]}
    vehicles = [
        {
            "vehicle_count": count,
            "enabled": count in available_counts and count in {1, 3},
            "reason_code": "enabled" if count in available_counts and count in {1, 3} else "scale_gate_pending",
        }
        for count in range(1, 10)
    ]
    return {
        "schema": "mosim.model_studio.catalog.v1",
        "profiles": profiles,
        "controllers": controllers,
        "vehicles": vehicles,
    }


def render_tsv(catalog: dict[str, Any]) -> str:
    lines = []
    for profile in catalog["profiles"]:
        lines.append(
            "\t".join(
                [
                    "PROFILE",
                    str(profile["profile_id"]),
                    str(profile["profile_path"]),
                    str(profile["controller_id"]),
                    str(profile["vehicle_count"]),
                    str(profile["enabled"]).lower(),
                    str(profile["reason_code"]),
                    str(profile["runtime_ready"]).lower(),
                ]
            )
        )
    for controller in catalog["controllers"]:
        lines.append(
            "\t".join(
                [
                    "CONTROLLER",
                    str(controller["controller_id"]),
                    str(controller["profile_id"]),
                    str(controller["family"]),
                    str(controller["enabled"]).lower(),
                    str(controller["reason_code"]),
                ]
            )
        )
    for vehicle in catalog["vehicles"]:
        lines.append(
            "\t".join(
                [
                    "VEHICLE",
                    str(vehicle["vehicle_count"]),
                    str(vehicle["enabled"]).lower(),
                    str(vehicle["reason_code"]),
                ]
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("json", "tsv"), default="tsv")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    catalog = build_catalog()
    rendered = (
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else render_tsv(catalog)
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
