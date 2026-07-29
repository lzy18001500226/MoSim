from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "check_plant_package_split.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_plant_package_split", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vehicle_assembly_contract_is_complete() -> None:
    module = load_module()
    report = module.check_vehicle_contract()
    assert report["status"] == "passed", report["findings"]
    assert len(report["members"]) == 12
    assert all(member["status"] == "passed" for member in report["members"])
    assert all(item["status"] == "passed" for item in report["canonical_assembly"]["runner_sources"])
