from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_control_scheme_catalog.py"
CATALOG = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
MATRIX = (
    ROOT
    / "Results"
    / "control_platform"
    / "classic_controller_closeout_20260717"
    / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
)
REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_control_scheme_catalog", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_authorities() -> tuple[dict, dict, dict]:
    return (
        json.loads(CATALOG.read_text(encoding="utf-8")),
        json.loads(MATRIX.read_text(encoding="utf-8")),
        json.loads(REGISTRY.read_text(encoding="utf-8")),
    )


def error_codes(catalog: dict, matrix: dict, registry: dict) -> set[str]:
    checker = load_checker()
    return {error["code"] for error in checker.validate(catalog, matrix, registry)}


def test_current_catalog_is_frozen_at_48_and_matches_authorities() -> None:
    catalog, matrix, registry = load_authorities()
    checker = load_checker()
    assert catalog["frozen_scheme_count"] == 48
    assert catalog["count_summary"]["mworks_control_profiles"] == 47
    assert catalog["count_summary"]["current_mworks_routes"] == 46
    assert checker.validate(catalog, matrix, registry) == []


def test_graphical_core_matrix_mapping_cannot_drift() -> None:
    catalog, matrix, registry = load_authorities()
    catalog = copy.deepcopy(catalog)
    graphical = next(item for item in catalog["schemes"] if item["scheme_id"] == "fuzzy_pid")
    graphical["evidence_matrix_controller"] = "cascade_pid"
    assert "CSC-GRAPHICAL-03" in error_codes(catalog, matrix, registry)


def test_frozen_count_cannot_drift() -> None:
    catalog, matrix, registry = load_authorities()
    catalog = copy.deepcopy(catalog)
    catalog["frozen_scheme_count"] = 50
    assert "CSC-COUNT-01" in error_codes(catalog, matrix, registry)


def test_full_profile_must_match_its_source_controller_id() -> None:
    catalog, matrix, registry = load_authorities()
    catalog = copy.deepcopy(catalog)
    awff_indi = next(item for item in catalog["schemes"] if item["scheme_id"] == "awff_l1_indi")
    awff_indi["source_controller_id"] = "wrong_controller"
    codes = error_codes(catalog, matrix, registry)
    assert "CSC-FULL-02" in codes
    assert "CSC-FULL-04" in codes


def test_standard_ui_cannot_reopen_generic_augmentation_multiselect() -> None:
    catalog, matrix, registry = load_authorities()
    catalog = copy.deepcopy(catalog)
    catalog["selection_contract"]["generic_augmentation_selector"] = "multi_select"
    assert "CSC-POLICY-03" in error_codes(catalog, matrix, registry)


def test_research_basis_must_remain_a_valid_frozen_list() -> None:
    catalog, matrix, registry = load_authorities()
    catalog = copy.deepcopy(catalog)
    catalog["research_basis"] = {}
    assert "CSC-RESEARCH-01" in error_codes(catalog, matrix, registry)
