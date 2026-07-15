"""Validate the MoSim control-module registry against the Profile catalog.

This is a static contract gate. It does not prove MWORKS, generated-C, or
Gazebo/PX4 runtime success.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"
REQUIRED_SCHEMA = "mosim.control_module_registry.v2"
REQUIRED_VARIANTS = {"ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"}
REQUIRED_FRAMES = {
    "FrameHeader", "StateFrame", "ReferenceFrame", "CommandFrame",
    "ModuleDiagnostics", "LifecycleContext", "ParameterSet",
}
REQUIRED_SLOTS = {
    "formation_controller", "reference_governor", "nominal_controller",
    "augmentation", "safety_filter", "attitude_rate_inner",
    "control_allocator", "command_adapter",
}
ALLOWED_KINDS = REQUIRED_SLOTS
ALLOWED_SECTIONS = {"controller_profiles", "augmentation_profiles"}
ACTIVE_STATUSES = {"active", "implemented", "accepted"}
COMMAND_VARIANT_ALIASES = {"BODYRATE_THRUST": "BODY_RATE_THRUST"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def canonical_variant(value: Any) -> str:
    variant = str(value)
    return COMMAND_VARIANT_ALIASES.get(variant, variant)


def validate(registry: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    if registry.get("schema") != REQUIRED_SCHEMA or registry.get("version") != 2:
        add("CMR-SCHEMA-01", "registry must use mosim.control_module_registry.v2 version 2")

    variants = set(registry.get("command_variants", []))
    if variants != REQUIRED_VARIANTS:
        add("CMR-CMD-01", f"command_variants must equal {sorted(REQUIRED_VARIANTS)}")

    frames = set(registry.get("frames", []))
    missing_frames = sorted(REQUIRED_FRAMES - frames)
    if missing_frames:
        add("CMR-FRAME-01", f"missing required frames: {missing_frames}")

    composition = registry.get("composition", {})
    missing_slots = sorted(REQUIRED_SLOTS - set(composition))
    if missing_slots:
        add("CMR-COMP-01", f"missing composition slots: {missing_slots}")
    for slot in ("nominal_controller", "safety_filter", "attitude_rate_inner", "command_adapter"):
        rule = composition.get(slot, {})
        if rule.get("min") != 1 or rule.get("max") != 1:
            add("CMR-COMP-02", f"{slot} must have cardinality exactly one")

    catalog_path = resolve(str(registry.get("profile_catalog", "")))
    if not catalog_path.is_file():
        add("CMR-CATALOG-01", f"profile catalog not found: {catalog_path}")
        return errors
    catalog = load_json(catalog_path)

    modules = registry.get("modules")
    if not isinstance(modules, list) or not modules:
        add("CMR-MODULE-01", "modules must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    seen_profiles: set[str] = set()
    for index, module in enumerate(modules):
        prefix = f"modules[{index}]"
        if not isinstance(module, dict):
            add("CMR-MODULE-02", f"{prefix} must be an object")
            continue
        module_id = str(module.get("module_id", ""))
        profile_id = str(module.get("profile_id", ""))
        section = str(module.get("catalog_section", ""))
        kind = str(module.get("kind", ""))
        status = str(module.get("status", ""))
        variant = str(module.get("output_variant", ""))

        if not module_id or module_id in seen_ids:
            add("CMR-MODULE-03", f"{prefix} has missing or duplicate module_id: {module_id}")
        seen_ids.add(module_id)
        if not profile_id or profile_id in seen_profiles:
            add("CMR-MODULE-04", f"{prefix} has missing or duplicate profile_id: {profile_id}")
        seen_profiles.add(profile_id)
        if section not in ALLOWED_SECTIONS:
            add("CMR-MODULE-05", f"{module_id} has unsupported catalog_section: {section}")
            continue
        if kind not in ALLOWED_KINDS:
            add("CMR-MODULE-06", f"{module_id} has unsupported kind: {kind}")
        if variant not in REQUIRED_VARIANTS:
            add("CMR-MODULE-07", f"{module_id} has unsupported output_variant: {variant}")
        if not str(module.get("claim_ceiling", "")).strip():
            add("CMR-CLAIM-01", f"{module_id} must declare claim_ceiling")

        entry = catalog.get(section, {}).get(profile_id)
        if not isinstance(entry, dict):
            add("CMR-CATALOG-02", f"{module_id} profile not found in {section}: {profile_id}")
            continue
        catalog_status = str(entry.get("implementation_status", "accepted" if profile_id == "none" else ""))
        if status != catalog_status:
            add("CMR-DRIFT-01", f"{module_id} status {status} != catalog status {catalog_status}")
        if canonical_variant(entry.get("output_interface", "")) != variant:
            add("CMR-DRIFT-02", f"{module_id} output {variant} != catalog output {entry.get('output_interface')}")
        family_field = "controller_family" if section == "controller_profiles" else "module_family"
        if str(entry.get(family_field, "")) != str(module.get("family", "")):
            add("CMR-DRIFT-03", f"{module_id} family does not match catalog")
        selectable = module.get("selectable")
        if not isinstance(selectable, bool):
            add("CMR-SELECT-01", f"{module_id} selectable must be boolean")
        elif selectable and status not in ACTIVE_STATUSES:
            add("CMR-SELECT-02", f"{module_id} status {status} cannot be selectable")

    catalog_profiles = set(catalog.get("controller_profiles", {}))
    catalog_profiles.update(
        profile_id for profile_id in catalog.get("augmentation_profiles", {}) if profile_id != "none"
    )
    missing_profiles = sorted(catalog_profiles - seen_profiles)
    if missing_profiles:
        add("CMR-COVERAGE-01", f"catalog modules missing from registry: {missing_profiles}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output-json")
    args = parser.parse_args()
    registry_path = resolve(args.registry)
    try:
        errors = validate(load_json(registry_path))
    except Exception as exc:
        errors = [{"code": "CMR-READ-01", "message": str(exc)}]
    report = {
        "ok": not errors,
        "registry": str(registry_path),
        "error_count": len(errors),
        "errors": errors,
    }
    if args.output_json:
        output = resolve(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
