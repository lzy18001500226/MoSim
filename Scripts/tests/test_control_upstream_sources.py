from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_control_upstream_sources.py"
SOURCES = ROOT / "Config" / "control_platform" / "upstream_sources.json"


def checker_module():
    spec = importlib.util.spec_from_file_location("check_control_upstream_sources", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_data() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def test_current_sources_are_pinned_and_licensed() -> None:
    assert checker_module().validate(source_data()) == []


def test_unlicensed_selected_source_is_rejected() -> None:
    data = source_data()
    data["selected"][0]["license"] = "NOASSERTION"
    codes = {item["code"] for item in checker_module().validate(data)}
    assert "CUS-LICENSE-01" in codes


def test_reference_only_source_cannot_be_copied() -> None:
    data = source_data()
    data["reference_only"][0]["source_copy_allowed"] = True
    codes = {item["code"] for item in checker_module().validate(data)}
    assert "CUS-REF-02" in codes
