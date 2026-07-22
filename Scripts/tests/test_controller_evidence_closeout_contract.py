from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_controller_evidence_closeout_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_controller_evidence_closeout_contract", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_g1_g7_contract_passes() -> None:
    checker = load_module()
    assert checker.validate(checker.load_inputs()) == []


def test_operation_catalog_cannot_be_promoted_to_model_entry_authority() -> None:
    checker = load_module()
    inputs = copy.deepcopy(checker.load_inputs())
    inputs["operation_catalog"]["non_authoritative_for"] = []
    codes = {error["code"] for error in checker.validate(inputs)}
    assert "CCEC-CATALOG-03" in codes


def test_unresolved_current_map_row_cannot_enable_mworks() -> None:
    checker = load_module()
    inputs = copy.deepcopy(checker.load_inputs())
    mu = next(row for row in inputs["current_model_map"]["schemes"] if row["scheme_id"] == "mu_synthesis")
    mu["mworks_run_eligible"] = True
    codes = {error["code"] for error in checker.validate(inputs)}
    assert "CCEC-MAP-09" in codes


def test_stale_current_g9_wording_is_rejected() -> None:
    checker = load_module()
    inputs = copy.deepcopy(checker.load_inputs())
    inputs["active_docs"]["Docs/Workflows/test_stale_goal.md"] = "Status: current G9 path"
    codes = {error["code"] for error in checker.validate(inputs)}
    assert "CCEC-DOC-06" in codes
