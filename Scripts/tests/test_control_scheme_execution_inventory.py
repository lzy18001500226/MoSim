from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_control_scheme_execution_inventory.py"
CHECKER = ROOT / "Scripts" / "quality" / "check_control_scheme_execution_inventory.py"
CATALOG = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
MATRIX = ROOT / "Results" / "control_platform" / "classic_controller_closeout_20260717" / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"
DOCUMENT_INVENTORY = ROOT / "Results" / "control_platform" / "controller_document_evidence_20260720" / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authorities() -> tuple[dict, dict, dict, dict]:
    return tuple(json.loads(path.read_text(encoding="utf-8")) for path in (CATALOG, MATRIX, REGISTRY, DOCUMENT_INVENTORY))


def test_g1_inventory_covers_exactly_the_frozen_49_schemes() -> None:
    builder = load_module(BUILDER, "build_control_scheme_execution_inventory")
    checker = load_module(CHECKER, "check_control_scheme_execution_inventory")
    catalog, matrix, registry, document_inventory = authorities()
    inventory = builder.build_inventory()
    assert inventory["summary"]["top_level_scheme_count"] == 49
    assert inventory["summary"]["mworks_run_eligible_count"] == 0
    assert checker.validate(inventory, catalog, matrix, registry, document_inventory) == []


def test_unresolved_source_candidate_cannot_enable_mworks() -> None:
    builder = load_module(BUILDER, "build_control_scheme_execution_inventory")
    checker = load_module(CHECKER, "check_control_scheme_execution_inventory")
    catalog, matrix, registry, document_inventory = authorities()
    inventory = builder.build_inventory()
    inventory = copy.deepcopy(inventory)
    cascade = next(row for row in inventory["schemes"] if row["scheme_id"] == "cascade_pid")
    cascade["mworks_run_eligible"] = True
    codes = {item["code"] for item in checker.validate(inventory, catalog, matrix, registry, document_inventory)}
    assert "CSE-RUN-02" in codes
    assert "CSE-RUN-03" in codes


def test_px4ctrl_cannot_be_promoted_to_a_graphical_mworks_scheme() -> None:
    builder = load_module(BUILDER, "build_control_scheme_execution_inventory")
    checker = load_module(CHECKER, "check_control_scheme_execution_inventory")
    catalog, matrix, registry, document_inventory = authorities()
    inventory = builder.build_inventory()
    inventory = copy.deepcopy(inventory)
    px4ctrl = next(row for row in inventory["schemes"] if row["scheme_id"] == "px4ctrl")
    px4ctrl["mworks_run_eligible"] = True
    px4ctrl["model_entry"]["mapping_state"] = "resolved_current_model"
    codes = {item["code"] for item in checker.validate(inventory, catalog, matrix, registry, document_inventory)}
    assert "CSE-PX4CTRL-02" in codes
