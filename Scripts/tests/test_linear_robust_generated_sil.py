from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_linear_robust_generated_sil.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p2_generated_sil", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_harness_uses_official_globals_and_all_controllers() -> None:
    module = load_runner()
    public = "extern struct InputTag generatedInput;\nextern struct OutputTag generatedOutput;\n"
    harness = module.generated_harness("", public)
    assert "generatedInput.controller_id_in" in harness
    assert "generatedOutput.normalized_thrust_out" in harness
    assert "print_case(1); print_case(2); print_case(3); print_case(4);" in harness
    assert 'printf("%d,0," +' not in harness


def test_parse_rows_ignores_lifecycle_rows() -> None:
    rows = load_runner().parse_rows("1,0,0.1,0.2\nL,disabled,0,1,0\n")
    assert rows == {1: [0.0, 0.1, 0.2]}
