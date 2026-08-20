from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_controller_48_refactor_inventory.py"


def load_module():
    spec = importlib.util.spec_from_file_location("controller_48_refactor_inventory", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inventory_covers_the_active_catalog_and_distinguishes_d2_binding() -> None:
    module = load_module()
    inventory = module.build_inventory()
    summary = inventory["summary"]

    assert inventory["schema"] == "mosim.controller_48_refactor_inventory.v1"
    assert len(inventory["routes"]) == 48
    assert summary["active_catalog_count"] == 48
    assert summary["studio_available_count"] == 48
    assert summary["studio_runner_file_exists_count"] == 48
    assert summary["studio_runner_declared_class_matches_count"] == 48
    assert summary["studio_runner_shared_sunray150assembly_source_chain_count"] == 48
    assert summary["studio_runner_or_d2_whole_aircraft_shell_count"] == 48
    assert summary["route_explicit_adapter_file_exists_count"] == 44
    assert summary["route_explicit_adapter_typed_interface_count"] == 0
    assert summary["route_adapter_or_embedded_binding_count"] == 45
    assert summary["d2_canonical_whole_aircraft_harness_count"] == 5
    assert summary["studio_app_reads_authoritative_toml"] is True
    assert summary["task_writer_reads_authoritative_toml"] is True


def test_inventory_is_deterministic(tmp_path: Path) -> None:
    module = load_module()
    inventory = module.build_inventory()
    json_path, report_path = module.write_outputs(inventory, tmp_path)

    assert json_path.is_file()
    assert report_path.is_file()
    assert json_path.read_text(encoding="utf-8") == __import__("json").dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    assert "## 禁止操作" in report_path.read_text(encoding="utf-8")
