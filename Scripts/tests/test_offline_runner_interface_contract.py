from __future__ import annotations

import copy
import json

from Scripts.quality import check_offline_runner_interface_contract as checker


def contract() -> dict:
    return json.loads(checker.CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def test_current_static_runner_contract_passes() -> None:
    assert checker.validate(contract()) == []


def test_four_boundaries_are_mandatory() -> None:
    changed = copy.deepcopy(contract())
    changed["boundaries"].pop("WRENCH")
    assert "four_explicit_boundaries_required" in checker.validate(changed)


def test_physical_units_cannot_be_claimed_before_verification() -> None:
    changed = copy.deepcopy(contract())
    output = changed["boundaries"]["WRENCH"]["outputs"][0]
    output["unit_semantics"] = "newtons"
    errors = checker.validate(changed)
    assert "unverified_physical_unit_overclaim:WRENCH:body_force" in errors


def test_lifecycle_ports_cannot_be_promoted_by_config_only() -> None:
    changed = copy.deepcopy(contract())
    changed["lifecycle_contract"]["current_model_ports_implemented"] = True
    errors = checker.validate(changed)
    assert "lifecycle_ports_must_remain_blocked_until_model_evidence" in errors
