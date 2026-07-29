from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_builder():
    path = ROOT / "Scripts" / "quality" / "build_non_frontend_requirement_evidence_matrix.py"
    spec = importlib.util.spec_from_file_location("non_frontend_requirement_matrix", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load requirement matrix builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_authorities_and_claim_boundaries() -> None:
    builder = load_builder()
    matrix = builder.build_matrix()
    assert matrix["controller_matrix_counts"] == {
        "accepted": 27,
        "executed_blocked": 33,
        "not_run": 7,
    }
    assert matrix["final_ab_counts"] == {
        "accepted": 1,
        "executed_blocked": 11,
        "not_run": 2,
    }
    by_id = {row["requirement_id"]: row for row in matrix["rows"]}
    assert by_id["REQ-UI-01..16"]["status"] == "excluded_by_scope"
    assert by_id["REQ-FAULT-01/02/07/08/09"]["status"] == "verified_at_declared_tier_with_scope"
    assert "not-run" in by_id["REQ-FAULT-01/02/07/08/09"]["claim_ceiling"]
    assert "selectable=false" in by_id["REQ-AI-01/02/05/07/08/10/15"]["claim_ceiling"]
