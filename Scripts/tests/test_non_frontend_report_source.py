from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_builder():
    path = ROOT / "Scripts" / "quality" / "build_non_frontend_report_source.py"
    spec = importlib.util.spec_from_file_location("non_frontend_report_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load report source builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_report_source_preserves_authority_rows() -> None:
    builder = load_builder()
    source = builder.build()
    assert source["controller_summary"]["counts"] == {
        "accepted": 27,
        "executed_blocked": 33,
        "not_run": 7,
    }
    assert source["final_ab_summary"]["counts"] == {
        "accepted": 1,
        "executed_blocked": 11,
        "not_run": 2,
    }
    assert len(source["final_ab_summary"]["rows"]) == 14
    assert source["specialized_summary"]["learning_status"] == "closed_with_performance_blocker"
