import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "verify_rt1_graphical_deployment_baseline.py"
SPEC = importlib.util.spec_from_file_location("rt1_graphical_deployment_baseline", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_rt1_deployment_baseline_hashes_the_complete_source_closure() -> None:
    result = MODULE.build()

    assert result["source_snapshot_passed"] is True
    assert result["release_ready"] is False
    assert result["runtime_evidence_status"] == "not_run_requires_clean_licensed_mworks_session"
    assert any(
        item["path"].endswith("MworksRt1Px4CtrlGraphicalShadow100Hz.mo")
        and len(item["sha256"]) == 64
        for item in result["files"]
    )
    assert any(
        item["path"].endswith("analyze_rt1_graphical_equivalence.py")
        and not item["missing_tokens"]
        for item in result["files"]
    )
