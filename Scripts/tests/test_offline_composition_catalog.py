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
