from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/collect_pid_attitude_thrust_mworks_evidence.py"


def test_collector_uses_live_mworks_result_api() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "ModelingPy.CheckModel" in text
    assert "ModelingPy.OpenModelFile" in text
    assert "ModelingPy.SimulateModel" in text
    assert "ModelingPy.GetVarTimes" in text
    assert "ModelingPy.GetVarsValues(builder.OUTPUTS)" in text
    assert "offline" not in text.lower()


def test_collector_builds_full_sil_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'CODEGEN_ROOT = RESULT_DIR / "generated_c_v2"' in text
    assert "normalize_codegen_archive(code_dir)" in text
    assert 'line.rstrip(" \\t")' in text
    assert 'lengths != {21}' in text
    assert 'len(all_rows) == 126' in text
    assert '"input_sequence": input_sequence' in text
    assert 'f"{name}_out"' in text
    assert 'newline="\\n"' in text
