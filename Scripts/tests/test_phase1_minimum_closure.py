from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MWORKS_DIR = ROOT / "Scripts" / "mworks"
if str(MWORKS_DIR) not in sys.path:
    sys.path.insert(0, str(MWORKS_DIR))

import run_phase1_minimum_closure as phase1  # noqa: E402


def test_phase1_matrix_has_exactly_46_unique_routes() -> None:
    matrix = phase1.build_matrix()
    rows = matrix["rows"]
    assert matrix["route_count"] == 46
    assert len(rows) == 46
    assert len({row["scheme_id"] for row in rows}) == 46


def test_phase1_preserves_missing_adapter_as_terminal_failure_not_fake_closure() -> None:
    matrix = phase1.build_matrix()
    rows = {row["scheme_id"]: row for row in matrix["rows"]}
    assert rows["adaptive_backstepping"]["execution_kind"] == "adapter_missing"
    assert "truthfully" in rows["adaptive_backstepping"]["adapter_missing_reason"]


def test_phase1_has_named_runner_and_fixed_integrated_targets() -> None:
    matrix = phase1.build_matrix()
    rows = {row["scheme_id"]: row for row in matrix["rows"]}
    assert rows["official_pid"]["target_boundary"] == "ROTOR_COMMAND"
    assert rows["cascade_pid"]["execution_kind"] == "adapter_backed_whole_aircraft"
    assert rows["fixed_awff_pid"]["execution_kind"] == "fixed_integrated_whole_aircraft"
