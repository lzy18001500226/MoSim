from __future__ import annotations

import importlib.util
import json
import locale
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
REPORT_SCRIPT_DIR = ROOT / "Scripts" / "report"
MODULE_PATH = REPORT_SCRIPT_DIR / "prepare_mathtype_formula_manifest.py"


def load_module():
    sys.path.insert(0, str(REPORT_SCRIPT_DIR))
    try:
        spec = importlib.util.spec_from_file_location(
            "prepare_mathtype_formula_manifest", MODULE_PATH
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(REPORT_SCRIPT_DIR))


def test_report_formula_manifest_covers_all_display_equations():
    module = load_module()
    manifest = module.build_manifest(
        module.DEFAULT_SOURCE,
        module.DEFAULT_GOLDEN,
        module.find_pandoc(),
    )

    assert manifest["source"]["display_formula_count"] == 104
    assert manifest["source"]["inline_formula_count"] == 142
    assert len(manifest["formulas"]) == 104
    assert manifest["conversion"]["pandoc_warnings"] == []
    assert manifest["conversion"]["word_or_mathtype_invoked"] is False

    numbers = [item["expected_number"] for item in manifest["formulas"]]
    assert numbers[0] == "2-1"
    assert numbers[-1] == "14-1"
    assert len(numbers) == len(set(numbers))
    assert "3-4a" in numbers
    assert "3-5b" in numbers
    assert "6-36a" in numbers
    assert "6-39a" in numbers
    assert "8-5a" in numbers
    assert manifest["numbering_contract"]["chapters"]["3"][
        "source_order_monotonic"
    ] is False
    assert manifest["numbering_contract"]["chapters"]["3"][
        "requires_explicit_sequence_reset"
    ] is True
    assert manifest["numbering_contract"]["chapters"]["8"][
        "source_order_monotonic"
    ] is True
    assert manifest["numbering_contract"]["chapters"]["8"][
        "requires_explicit_sequence_reset"
    ] is True
    inferred = manifest["numbering_contract"]["inferred_numbering"]
    assert [item["formula_id"] for item in inferred] == [69, 73]
    assert [item["expected_number"] for item in inferred] == ["6-36a", "6-39a"]
    assert all("for review" in item["reason"] for item in inferred)


def test_problematic_formulas_have_structured_presentation_mathml():
    module = load_module()
    manifest = module.build_manifest(
        module.DEFAULT_SOURCE,
        module.DEFAULT_GOLDEN,
        module.find_pandoc(),
    )
    by_id = {item["formula_id"]: item for item in manifest["formulas"]}

    formula_2 = by_id[2]
    formula_102 = by_id[102]
    assert formula_2["mathml_structure"]["mtable"] >= 2
    assert "𝟙" in formula_2["mathml"]
    assert formula_102["mathml_structure"]["msqrt"] == 1
    assert "∥" in formula_102["mathml"]

    for formula in (formula_2, formula_102):
        root = etree.fromstring(formula["mathml"].encode("utf-8"))
        assert etree.QName(root).localname == "math"
        assert root.get("display") == "block"


def test_golden_layout_contract_matches_manual_sample():
    module = load_module()
    layout = module.inspect_golden_layout(module.DEFAULT_GOLDEN)

    assert layout["table_rows"] == 1
    assert layout["table_columns"] == 2
    assert layout["table_width_twips"] == 8832
    assert layout["column_widths_twips"] == [7655, 1177]
    assert set(layout["borders"].values()) == {"none"}
    assert layout["cell_vertical_alignment"] == ["center", "center"]
    assert layout["paragraph_alignment"] == ["center", "center"]
    assert layout["field_instructions"] == [
        r"SEQ Chapter \c",
        r"SEQ Equation \* ARABIC",
    ]
    assert layout["cached_number_text"] == "(2-1)"
    assert layout["mathtype_progid"] == "Equation.DSMT4"


def test_mathml_ole_pilot_dry_run_reads_utf8_manifest(tmp_path: Path):
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        pytest.skip("Windows PowerShell is unavailable")

    script = ROOT / "Scripts" / "report" / "invoke_mathtype_mathml_ole_pilot.ps1"
    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-OutputPath",
            str(tmp_path / "mathml_ole_dryrun.docx"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    output = result.stdout.decode(locale.getpreferredencoding(False))
    plan = json.loads(output)

    assert plan["mode"] == "dry_run"
    assert plan["formula_id"] == 102
    assert plan["expected_number"] == "13-1"
    assert plan["manifest_sha256"]
    assert plan["golden_pilot_sha256"]
