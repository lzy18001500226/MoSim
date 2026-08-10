from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "report" / "run_mathtype_report_mathml_backend.ps1"
LEGACY = ROOT / "Scripts" / "report" / "run_mathtype_report_review_copy.py"
SOURCE = ROOT / "Docs" / "报告" / "MoSim_仿真分析报告.docx"
MANIFEST = ROOT / "Results" / "report_word_layout_20260804" / "MATHTYPE_FORMULA_MANIFEST.json"


def powershell_exe() -> str:
    executable = shutil.which("powershell.exe")
    if executable is None:
        pytest.skip("Windows PowerShell is unavailable")
    return executable


def test_backend_dry_run_declares_noninteractive_engine(tmp_path: Path):
    result = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-Source",
            str(SOURCE),
            "-Manifest",
            str(MANIFEST),
            "-Output",
            str(tmp_path / "review.docx"),
            "-Audit",
            str(tmp_path / "audit.json"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    plan = json.loads(result.stdout)

    assert plan["mode"] == "dry_run"
    assert plan["engine"] == "Equation.DSMT4_OLE_IDataObject_MathML"
    assert plan["requested_formula_count"] == 104
    assert plan["requested_formula_ids"][0] == 1
    assert plan["requested_formula_ids"][-1] == 104
    assert plan["foreground_interaction"] is False
    assert plan["selection_or_activation_used"] is False
    assert plan["clipboard_used"] is False
    assert plan["legacy_tex_toggle_used"] is False
    assert not (tmp_path / "review.docx").exists()
    assert not (tmp_path / "audit.json").exists()


def test_backend_source_has_no_foreground_entry_or_clipboard_route():
    source = SCRIPT.read_text(encoding="utf-8")

    assert "MathTypeCommands.UILib.MTCommand_TeXToggle" not in source
    assert ".Select()" not in source
    assert ".Activate()" not in source
    assert "Range.Copy" not in source
    assert ".Paste(" not in source
    assert ".FormattedText" in source
    assert "SetPresentationMathML" in source
    assert "CloseWithoutSave" in source


def test_legacy_execute_requires_an_explicit_foreground_opt_in(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(LEGACY),
            "--execute",
            "--output",
            str(tmp_path / "review.docx"),
            "--evidence",
            str(tmp_path / "evidence.json"),
            "--checkpoint",
            str(tmp_path / "checkpoint.jsonl"),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode != 0
    assert "Foreground MathType TeX-toggle execution is disabled" in result.stderr
    assert not (tmp_path / "review.docx").exists()


def test_mathml_helper_uses_the_document_element_and_explicit_close():
    helper = (ROOT / "Scripts" / "report" / "MathTypeOleData.cs").read_text(
        encoding="utf-8"
    )

    assert "return value;" in helper
    assert "<html>" not in helper
    assert "public static void CloseWithoutSave" in helper
