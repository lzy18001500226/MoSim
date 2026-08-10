from __future__ import annotations

import json
import locale
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "report" / "probe_mathtype_mathml_ole_formats.ps1"
HELPER = ROOT / "Scripts" / "report" / "MathTypeOleData.cs"


def powershell_exe() -> str:
    executable = shutil.which("powershell.exe")
    if executable is None:
        pytest.skip("Windows PowerShell is unavailable")
    return executable


def test_read_only_format_probe_dry_run_has_all_mathml_variants(tmp_path: Path):
    result = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-EvidencePath",
            str(tmp_path / "format_probe.json"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    plan = json.loads(result.stdout.decode(locale.getpreferredencoding(False)))

    assert plan["mode"] == "dry_run"
    assert plan["probe_contract"]["enumeration_direction"] == "DATADIR_GET,DATADIR_SET"
    assert plan["probe_contract"]["ole_activation"] == (
        "OLEFormat.DoVerb(2) / documented RunForConversion verb"
    )
    assert plan["probe_contract"]["requested_mathml_clipboard_formats"] == [
        "MathML Presentation",
        "MathML",
        "application/mathml+xml",
    ]
    assert plan["probe_contract"]["set_data_invoked"] is False
    assert plan["probe_contract"]["get_data_invoked"] is False
    assert not (tmp_path / "format_probe.json").exists()


def test_ole_helper_compiles_and_exposes_read_only_probe():
    helper_text = HELPER.read_text(encoding="utf-8")
    assert 'RegisteredClipboardFormat("MathML Presentation")' in helper_text

    command = (
        "Add-Type -Path '"
        + str(HELPER).replace("'", "''")
        + "'; "
        "if ($null -eq [MathTypeOleData].GetMethod('ProbeMathMLFormats')) "
        "{ throw 'ProbeMathMLFormats is missing' }; "
        "[MathTypeOleData].GetMethod('ProbeMathMLFormats').Name"
    )
    result = subprocess.run(
        [
            powershell_exe(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    assert result.stdout.decode(locale.getpreferredencoding(False)).strip() == (
        "ProbeMathMLFormats"
    )
