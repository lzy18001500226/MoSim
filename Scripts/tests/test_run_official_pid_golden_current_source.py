from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_runner_binds_one_existing_port_and_preserves_the_two_references() -> None:
    source = (ROOT / "Scripts/mworks/run_official_pid_golden_current_source.py").read_text(encoding="utf-8")

    assert "ModelingPy.ConnectSysplorer(port=port)" in source
    assert "OfficialPidSingleUavGoldenRunner" in source
    assert "OfficialPidFormalRunner" in source
    assert "ModelingPy.CheckModel(model_name)" in source
    assert "ModelingPy.SimulateModel(" in source
    assert "stopTime=stop_time_s" in source
    assert "run_comparison(" in source
    assert "source_hash_drift" in source
