from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "Scripts/control_platform/run_enhancement_generated_sil.py").read_text(encoding="utf-8")


def test_sil_compares_six_controllers_and_official_codegen() -> None:
    assert 'range(1, 7)' in SCRIPT
    assert '"MWORKS GenerateModelCode"' in SCRIPT
    assert '"compared_columns_per_controller"' in SCRIPT
    assert '"mosim.control_platform.p5_generated_sil.v1"' in SCRIPT
