#!/usr/bin/env python3
"""Validate offline Runner/module/Profile compatibility declarations."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
INVENTORY_PATH = ROOT / "Config" / "control_platform" / "offline_expansion_inventory.json"
ALLOWED_VARIANTS = {"ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"}
MAPPING_STATES = {"RESOLVED_REGISTRY_MAPPING", "UNRESOLVED_LEGACY_ALIAS", "NOT_APPLICABLE"}


def validate_module_mappings(catalog: dict, inventory: dict) -> list[str]:
    registry_ids = {module["module_id"] for module in inventory["modules"]}
    errors: list[str] = []
    for module_id, module in catalog.get("modules", {}).items():
        mapping_state = module.get("mapping_state")
        mapped_ids = module.get("registry_module_ids")
        if module.get("entry_kind") not in {"boundary_fixture", "legacy_bundle", "layered_adapter"}:
            errors.append(f"invalid_entry_kind:{module_id}")
        if mapping_state not in MAPPING_STATES:
            errors.append(f"invalid_mapping_state:{module_id}")
        if not isinstance(mapped_ids, list) or len(mapped_ids) != len(set(mapped_ids)):
            errors.append(f"invalid_registry_module_ids:{module_id}")
            continue
        unknown = sorted(set(mapped_ids) - registry_ids)
        if unknown:
            errors.append(f"unknown_registry_module_ids:{module_id}:{unknown}")
        if mapping_state == "RESOLVED_REGISTRY_MAPPING":
            composition = module.get("layered_composition")
            if not mapped_ids or not isinstance(composition, dict):
                errors.append(f"resolved_mapping_incomplete:{module_id}")
            else:
                composition_ids = {
                    value
                    for key, value in composition.items()
                    if key != "augmentations" and isinstance(value, str)
                }
                composition_ids.update(composition.get("augmentations", []))
                if composition_ids != set(mapped_ids):
                    errors.append(f"resolved_mapping_ids_mismatch:{module_id}")
        elif mapping_state == "UNRESOLVED_LEGACY_ALIAS" and not module.get("mapping_blocker"):
            errors.append(f"unresolved_mapping_blocker_missing:{module_id}")
        elif mapping_state == "NOT_APPLICABLE" and module.get("entry_kind") != "boundary_fixture":
            errors.append(f"not_applicable_mapping_not_fixture:{module_id}")
    return errors


def main() -> int:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    errors = validate_module_mappings(catalog, inventory)
    if set(catalog.get("runners", {})) != ALLOWED_VARIANTS:
        errors.append("four_explicit_runners_required")
    modules = catalog.get("modules", {})
    profiles = catalog.get("certified_profiles", [])
    single = [profile for profile in profiles if profile.get("vehicle_count") == 1]
    multi = [profile for profile in profiles if profile.get("vehicle_count") == 3]
    if len(single) != 8:
        errors.append(f"eight_single_uav_profiles_required:{len(single)}")
    if len(multi) != 1:
        errors.append(f"one_three_uav_profile_required:{len(multi)}")
    profile_ids: set[str] = set()
    for profile in profiles:
        profile_id = profile.get("profile_id")
        if not profile_id or profile_id in profile_ids:
            errors.append(f"duplicate_or_missing_profile_id:{profile_id}")
        profile_ids.add(profile_id)
        module = modules.get(profile.get("controller_id"))
        if not module:
            errors.append(f"unknown_controller:{profile_id}")
        elif module.get("status") not in {"available", "fixture"}:
            errors.append(f"certified_profile_controller_not_available:{profile_id}")
        elif profile.get("output_variant") != module.get("output_variant"):
            errors.append(f"output_variant_mismatch:{profile_id}")
        if profile.get("vehicle_count") == 1 and profile.get("output_variant") not in catalog["runners"]:
            errors.append(f"runner_missing:{profile_id}")
        if profile.get("execution_kind") == "direct_model" and not profile.get("direct_model"):
            errors.append(f"direct_model_missing:{profile_id}")
        if profile.get("vehicle_count") == 3 and not profile.get("direct_model"):
            errors.append(f"multi_uav_direct_model_missing:{profile_id}")
        if profile.get("execution_kind") == "direct_model":
            source_value = profile.get("direct_model_file")
            if not isinstance(source_value, str) or not (ROOT / source_value).is_file():
                errors.append(f"direct_model_source_missing:{profile_id}")
        if profile.get("certification_state") == "accepted":
            record_value = profile.get("certification_record")
            record_path = ROOT / record_value if isinstance(record_value, str) else None
            if record_path is None or not record_path.is_file():
                errors.append(f"accepted_certification_record_missing:{profile_id}")
            else:
                record = json.loads(record_path.read_text(encoding="utf-8-sig"))
                if record.get("profile_id") != profile_id or record.get("status") != "accepted":
                    errors.append(f"accepted_certification_record_mismatch:{profile_id}")
                if record.get("run_id") != profile.get("certification_run_id"):
                    errors.append(f"accepted_certification_run_mismatch:{profile_id}")
    for profile in catalog.get("disabled_profiles", []):
        module = modules.get(profile.get("controller_id"))
        if not module:
            errors.append(f"disabled_profile_unknown_controller:{profile.get('profile_id')}")
        elif module.get("status") in {"available", "fixture"}:
            errors.append(f"disabled_profile_controller_still_available:{profile.get('profile_id')}")
        if not profile.get("disabled_reason"):
            errors.append(f"disabled_profile_reason_missing:{profile.get('profile_id')}")
    custom_proofs = catalog.get("custom_profile_proofs", [])
    if len(custom_proofs) < 2:
        errors.append(f"two_custom_profile_proofs_required:{len(custom_proofs)}")
    for proof in custom_proofs:
        record_value = proof.get("certification_record")
        record_path = ROOT / record_value if isinstance(record_value, str) else None
        if record_path is None or not record_path.is_file():
            errors.append(f"custom_profile_record_missing:{proof.get('profile_id')}")
            continue
        record = json.loads(record_path.read_text(encoding="utf-8-sig"))
        if record.get("profile_kind") != "custom" or record.get("status") != "accepted":
            errors.append(f"custom_profile_record_not_accepted:{proof.get('profile_id')}")
        if record.get("profile_id") != proof.get("profile_id") or record.get("run_id") != proof.get("run_id"):
            errors.append(f"custom_profile_record_mismatch:{proof.get('profile_id')}")
    root = catalog.get("generated_wrapper_root", "")
    if root != "Results/mworks_generated_profiles":
        errors.append("generated_wrapper_root_must_be_results_local")
    result = {"ok": not errors, "errors": errors, "single_uav_profiles": len(single), "three_uav_profiles": len(multi)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
