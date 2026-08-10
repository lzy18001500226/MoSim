from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "report" / "pilot_mathtype_mathml_clipboard_paste.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mathtype_mathml_clipboard", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def test_build_mathml_presentation_payload_wraps_one_math_root():
    module = load_module()

    payload = module.build_mathml_presentation_payload(
        '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi></math>'
    )

    assert payload.startswith("<?xml version='1.0' encoding='UTF-8'?><html><math")
    assert payload.endswith("</math></html>")


def test_dry_run_does_not_create_pilot_artifacts(tmp_path: Path):
    output = tmp_path / "clipboard_pilot.docx"
    evidence = tmp_path / "clipboard_pilot.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--formula-id",
            "43",
            "--output",
            str(output),
            "--evidence",
            str(evidence),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    plan = json.loads(result.stdout)

    assert plan["mode"] == "dry_run"
    assert plan["formula_id"] == 43
    assert plan["clipboard"]["format"] == "MathML Presentation"
    assert plan["clipboard"]["restore_original_ole_clipboard"] is True
    assert plan["output"] == output.as_posix()
    assert plan["evidence"] == evidence.as_posix()
    assert not output.exists()
    assert not evidence.exists()
