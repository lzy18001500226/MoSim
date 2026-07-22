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
ALLOWED_KINDS = REQUIRED_SLOTS | {"fault_manager"}
ALLOWED_SECTIONS = {
    "controller_profiles",
    "augmentation_profiles",
    "safety_profiles",
    "inner_controller_profiles",
    "allocator_profiles",
    "adapter_profiles",
    "formation_profiles",
    "fault_profiles",
}
ACTIVE_STATUSES = {"active", "implemented", "accepted"}
COMMAND_VARIANT_ALIASES = {"BODYRATE_THRUST": "BODY_RATE_THRUST"}
SECTION_FAMILY_FIELDS = {
    "controller_profiles": "controller_family",
    "augmentation_profiles": "module_family",
    "safety_profiles": "module_family",
    "inner_controller_profiles": "module_family",
    "allocator_profiles": "module_family",
    "adapter_profiles": "module_family",
    "formation_profiles": "formation_id",
}
SECTION_ALLOWED_KINDS = {
    "controller_profiles": {"nominal_controller", "attitude_rate_inner"},
    "augmentation_profiles": {"augmentation"},
    "safety_profiles": {"safety_filter"},
    "inner_controller_profiles": {"attitude_rate_inner"},
    "allocator_profiles": {"control_allocator"},
    "adapter_profiles": {"command_adapter"},
    "formation_profiles": {"formation_controller"},
    "fault_profiles": {"fault_manager"},
}
FAULT_FAMILY_BY_MODE = {
    "fdi": "fault_detection_and_isolation",
    "passive_ftc": "passive_fault_tolerant_control",
    "active_ftc": "active_fault_tolerant_control",
    "fault_aware_control_allocation": "fault_aware_control_allocation",
    "single_motor_safe_landing": "single_motor_safe_landing",
    "multi_fault_estimation_reconfiguration": "multi_fault_estimation_and_reconstruction",
}
FAULT_OUTPUT_VARIANTS = {"FAULT_EVENT", "ROTOR_COMMAND", "ROTOR_COMMAND_AND_LAND_ACTION"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def canonical_variant(value: Any) -> str:
    variant = str(value)
    return COMMAND_VARIANT_ALIASES.get(variant, variant)


def canonical_variants(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [canonical_variant(value) for value in values]


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
        elif kind not in SECTION_ALLOWED_KINDS[section]:
            add("CMR-MODULE-08", f"{module_id} kind {kind} is invalid for {section}")
        if not str(module.get("claim_ceiling", "")).strip():
            add("CMR-CLAIM-01", f"{module_id} must declare claim_ceiling")

        entry = catalog.get(section, {}).get(profile_id)
        if not isinstance(entry, dict):
            add("CMR-CATALOG-02", f"{module_id} profile not found in {section}: {profile_id}")
            continue
        catalog_status = str(entry.get("implementation_status", "accepted" if profile_id == "none" else ""))
        if status != catalog_status:
            add("CMR-DRIFT-01", f"{module_id} status {status} != catalog status {catalog_status}")
        if section == "fault_profiles":
            expected_family = FAULT_FAMILY_BY_MODE.get(str(entry.get("management_mode", "")), "")
        else:
            expected_family = str(entry.get(SECTION_FAMILY_FIELDS[section], ""))
        if expected_family != str(module.get("family", "")):
            add("CMR-DRIFT-03", f"{module_id} family does not match catalog")
        selectable = module.get("selectable")
        if not isinstance(selectable, bool):
            add("CMR-SELECT-01", f"{module_id} selectable must be boolean")
        elif selectable and status not in ACTIVE_STATUSES:
            add("CMR-SELECT-02", f"{module_id} status {status} cannot be selectable")

        if section in {"controller_profiles", "augmentation_profiles"}:
            variant = canonical_variant(module.get("output_variant", ""))
            if variant not in REQUIRED_VARIANTS:
                add("CMR-MODULE-07", f"{module_id} has unsupported output_variant: {variant}")
            if canonical_variant(entry.get("output_interface", "")) != variant:
                add("CMR-DRIFT-02", f"{module_id} output {variant} != catalog output {entry.get('output_interface')}")
        elif section == "safety_profiles":
            variants = canonical_variants(module.get("supported_variants"))
            catalog_variants = canonical_variants(entry.get("supported_interfaces"))
            if not variants or not set(variants).issubset(REQUIRED_VARIANTS):
                add("CMR-SAFETY-01", f"{module_id} must declare supported_variants")
            if variants != catalog_variants:
                add("CMR-DRIFT-04", f"{module_id} safety variants do not match catalog")
        elif section == "inner_controller_profiles":
            input_variants = canonical_variants(module.get("input_variants"))
            output_variant = canonical_variant(module.get("output_variant", ""))
            if not input_variants or not set(input_variants).issubset(REQUIRED_VARIANTS):
                add("CMR-INNER-01", f"{module_id} must declare valid input_variants")
            if input_variants != canonical_variants(entry.get("input_interfaces")):
                add("CMR-DRIFT-05", f"{module_id} inner-controller inputs do not match catalog")
            if output_variant != canonical_variant(entry.get("output_interface", "")):
                add("CMR-DRIFT-02", f"{module_id} output does not match catalog")
            if module.get("backend_owned") is not True or not str(module.get("backend_owner", "")):
                add("CMR-BACKEND-01", f"{module_id} must explicitly declare backend ownership")
        elif section == "allocator_profiles":
            input_variant = canonical_variant(module.get("input_variant", ""))
            output_variant = canonical_variant(module.get("output_variant", ""))
            if input_variant != canonical_variant(entry.get("input_interface", "")):
                add("CMR-DRIFT-06", f"{module_id} allocator input does not match catalog")
            if output_variant != canonical_variant(entry.get("output_interface", "")):
                add("CMR-DRIFT-02", f"{module_id} output does not match catalog")
            if module.get("backend_owned") is not True or not str(module.get("backend_owner", "")):
                add("CMR-BACKEND-01", f"{module_id} must explicitly declare backend ownership")
        elif section == "adapter_profiles":
            input_variant = canonical_variant(module.get("input_variant", ""))
            if input_variant != canonical_variant(entry.get("input_interface", "")):
                add("CMR-DRIFT-07", f"{module_id} adapter input does not match catalog")
            if str(module.get("backend_output", "")) != str(entry.get("output_backend", "")):
                add("CMR-DRIFT-08", f"{module_id} adapter backend output does not match catalog")
            for field in ("backend_inner_profile", "backend_allocator_profile"):
                if str(module.get(field, "")) != str(entry.get(field, "")):
                    add("CMR-DRIFT-09", f"{module_id} {field} does not match catalog")
        elif section == "formation_profiles":
            if str(module.get("output_variant", "")) != "MULTI_UAV_REFERENCE":
                add("CMR-FORMATION-01", f"{module_id} must output MULTI_UAV_REFERENCE")
        elif section == "fault_profiles":
            if str(module.get("input_variant", "")) != "ROTOR_COMMAND_AND_RESPONSE":
                add("CMR-FAULT-01", f"{module_id} must consume ROTOR_COMMAND_AND_RESPONSE")
            if str(module.get("output_variant", "")) not in FAULT_OUTPUT_VARIANTS:
                add("CMR-FAULT-02", f"{module_id} has unsupported fault-manager output")

    modules_by_profile = {
        str(module.get("profile_id")): module
        for module in modules
        if isinstance(module, dict) and module.get("profile_id")
    }
    for module in modules:
        if not isinstance(module, dict) or module.get("catalog_section") != "adapter_profiles":
            continue
        adapter_id = str(module.get("module_id", ""))
        inner = modules_by_profile.get(str(module.get("backend_inner_profile", "")))
        allocator = modules_by_profile.get(str(module.get("backend_allocator_profile", "")))
        if not inner or inner.get("kind") != "attitude_rate_inner":
            add("CMR-CHAIN-01", f"{adapter_id} does not bind a registered attitude/rate inner controller")
            continue
        if not allocator or allocator.get("kind") != "control_allocator":
            add("CMR-CHAIN-02", f"{adapter_id} does not bind a registered control allocator")
            continue
        adapter_input = canonical_variant(module.get("input_variant", ""))
        if adapter_input not in canonical_variants(inner.get("input_variants")):
            add("CMR-CHAIN-03", f"{adapter_id} input is not accepted by its backend inner controller")
        if canonical_variant(inner.get("output_variant", "")) != canonical_variant(allocator.get("input_variant", "")):
            add("CMR-CHAIN-04", f"{adapter_id} backend inner output does not match allocator input")

    selectable_adapters = [
        module for module in modules
        if isinstance(module, dict)
        and module.get("kind") == "command_adapter"
        and module.get("selectable") is True
    ]
    selectable_safety_filters = [
        module for module in modules
        if isinstance(module, dict)
        and module.get("kind") == "safety_filter"
        and module.get("selectable") is True
    ]
    for module in modules:
        if not isinstance(module, dict) or module.get("kind") != "nominal_controller":
            continue
        if module.get("selectable") is not True:
            continue
        variant = canonical_variant(module.get("output_variant", ""))
        if not any(canonical_variant(adapter.get("input_variant", "")) == variant for adapter in selectable_adapters):
            add("CMR-CHAIN-05", f"{module.get('module_id')} has no selectable adapter for {variant}")
        if not any(variant in canonical_variants(safety.get("supported_variants")) for safety in selectable_safety_filters):
            add("CMR-CHAIN-06", f"{module.get('module_id')} has no selectable safety filter for {variant}")

    catalog_profiles: set[str] = set()
    for section in ALLOWED_SECTIONS:
        catalog_profiles.update(
            profile_id for profile_id in catalog.get(section, {}) if profile_id != "none"
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
