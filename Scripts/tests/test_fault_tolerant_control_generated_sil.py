from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "Scripts/control_platform/run_fault_tolerant_control_generated_sil.py").read_text(encoding="utf-8")


def test_sil_compares_all_six_modes_and_official_codegen() -> None:
    assert "range(1, 7)" in SCRIPT
    assert '"MWORKS GenerateModelCode"' in SCRIPT
    assert "fault_tolerant_control_core.c" in SCRIPT
    assert "max_abs_difference" in SCRIPT


def test_generated_harness_runs_persistent_steps() -> None:
    assert "for(step=0;step<80;++step)" in SCRIPT
    assert "P7_GENERATED_SIL_EQUIVALENCE.json" in SCRIPT
