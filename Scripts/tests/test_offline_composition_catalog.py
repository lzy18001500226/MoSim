from __future__ import annotations

import copy
import json

from Scripts.quality import check_offline_composition_catalog as checker


def authority() -> tuple[dict, dict]:
    catalog = json.loads(checker.CATALOG_PATH.read_text(encoding="utf-8-sig"))
    inventory = json.loads(checker.INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    return catalog, inventory


def test_current_catalog_module_mappings_pass() -> None:
    catalog, inventory = authority()
    assert checker.validate_module_mappings(catalog, inventory) == []


def test_unknown_registry_mapping_fails_closed() -> None:
    catalog, inventory = authority()
    changed = copy.deepcopy(catalog)
    changed["modules"]["official_pid"]["registry_module_ids"] = ["not_registered"]
    errors = checker.validate_module_mappings(changed, inventory)
    assert any(error.startswith("unknown_registry_module_ids:official_pid") for error in errors)


def test_resolved_mapping_must_match_declared_composition() -> None:
    catalog, inventory = authority()
    changed = copy.deepcopy(catalog)
    changed["modules"]["awff"]["layered_composition"]["augmentations"] = []
    errors = checker.validate_module_mappings(changed, inventory)
    assert "resolved_mapping_ids_mismatch:awff" in errors


def test_unresolved_alias_requires_a_blocker() -> None:
    catalog, inventory = authority()
    changed = copy.deepcopy(catalog)
    changed["modules"]["linear_mpc"].pop("mapping_blocker")
    errors = checker.validate_module_mappings(changed, inventory)
    assert "unresolved_mapping_blocker_missing:linear_mpc" in errors


def test_resolved_native_boundary_must_match_frozen_inventory() -> None:
    catalog, inventory = authority()
    changed = copy.deepcopy(catalog)
    changed["modules"]["official_pid"]["native_output_variant"] = "ROTOR_COMMAND"
    errors = checker.validate_module_mappings(changed, inventory)
    assert "resolved_native_output_variant_mismatch:official_pid" in errors


def test_cross_boundary_mapping_must_be_explicit_and_offline_only() -> None:
    catalog, inventory = authority()
    changed = copy.deepcopy(catalog)
    changed["modules"]["awff"].pop("boundary_conversion_state")
    errors = checker.validate_module_mappings(changed, inventory)
    assert "cross_boundary_conversion_not_declared:awff" in errors


def test_unresolved_alias_cannot_guess_native_boundary() -> None:
    catalog, inventory = authority()
    changed = copy.deepcopy(catalog)
    changed["modules"]["l1_awff"]["native_output_variant"] = "ATTITUDE_THRUST"
    errors = checker.validate_module_mappings(changed, inventory)
    assert "unresolved_native_output_variant_must_be_null:l1_awff" in errors
