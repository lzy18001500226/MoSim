from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_current_model_entry_map.py"
LIBRARY = ROOT / "Scripts" / "quality" / "current_model_entry_map_lib.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_current_model_entry_map", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_library():
    spec = importlib.util.spec_from_file_location("current_model_entry_map_lib", LIBRARY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_model_entry_map_passes() -> None:
    checker = load_module()
    assert checker.validate(checker.load_inputs()) == []


def test_results_cannot_be_promoted_as_current_model() -> None:
    checker = load_module()
    inputs = copy.deepcopy(checker.load_inputs())
    cascade = next(row for row in inputs["current"]["schemes"] if row["scheme_id"] == "cascade_pid")
    cascade["current_model_file"] = "Results/control_platform/invalid.mo"
    codes = {error["code"] for error in checker.validate(inputs)}
    assert "CMEM-STATE-03" in codes
    assert "CMEM-DRIFT-01" in codes


def test_only_px4ctrl_can_be_runtime_baseline() -> None:
    checker = load_module()
    inputs = copy.deepcopy(checker.load_inputs())
    cascade = next(row for row in inputs["current"]["schemes"] if row["scheme_id"] == "cascade_pid")
    cascade["mapping_state"] = "pending_mworks_equivalent_core"
    codes = {error["code"] for error in checker.validate(inputs)}
    assert "CMEM-STATE-04" in codes


def test_import_equivalence_accepts_only_known_sysplorer_whitespace_rewrite() -> None:
    library = load_library()
    expected = "within Example.Package;\n\nmodel Demo\n  Real x;\nend Demo;\n"
    sysplorer_normalized = "within Example.Package;\nmodel Demo\n  Real x;\nend Demo;"
    trailing_whitespace = "within Example.Package;\r\n\r\nmodel Demo \t\r\n  Real x;  \r\nend Demo; \r\n"
    altered_body = "within Example.Package;\nmodel Demo\n  Real y;\nend Demo;"

    assert library.import_equivalence_text(expected) == library.import_equivalence_text(sysplorer_normalized)
    assert library.import_equivalence_text(expected) == library.import_equivalence_text(trailing_whitespace)
    assert library.import_equivalence_text(expected) != library.import_equivalence_text(altered_body)


def test_approved_project_variant_is_exactly_hash_bound() -> None:
    library = load_library()
    catalog = library.read_json(library.CATALOG_PATH)
    inventory = library.read_json(library.INVENTORY_PATH)
    item = next(
        row for row in library.import_plan(catalog, inventory) if row["scheme_id"] == "lqr_baseline"
    )
    target = item["target_file"]
    expected = library.expected_import_text(item)
    variants = library.read_approved_graphical_import_variants()

    assert library.approved_graphical_import_variant(item, target, expected, variants=variants)

    mutated = copy.deepcopy(variants)
    key = library.import_item_identity(item)
    mutated[key]["current_model_sha256"] = "0" * 64
    assert library.approved_graphical_import_variant(item, target, expected, variants=mutated) is None
