from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts/control_platform/summarize_controller_family_final_acceptance.py"
SPEC = importlib.util.spec_from_file_location("controller_final", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_current_matrix_is_fail_closed_and_complete() -> None:
    rows = MODULE.build_rows()
    identities = {(row.cohort, row.controller) for row in rows}

    assert len(rows) == 48
    assert len(identities) == len(rows)
    assert {row.status for row in rows} <= {
        "accepted", "executed_blocked", "provenance_missing", "not_run"
    }
    assert all(row.evidence_paths is not None for row in rows)
    assert all(row.implementation_state == "implemented" for row in rows)
    assert all(row.mworks_codegen_state == "passed" for row in rows)
    assert all(row.generated_sil_state == "passed" for row in rows)
    assert all(row.selectable == (row.status == "accepted" and row.cohort != "P9_LEARNING") for row in rows)


def test_g9_is_not_promoted_from_legacy_runtime() -> None:
    rows = MODULE.build_rows()
    g9 = [row for row in rows if row.cohort == "G9_CORE_COMPARISON"]

    assert len(g9) == 6
    assert {row.status for row in g9} <= {
        "accepted", "executed_blocked", "provenance_missing", "not_run"
    }
    assert all(row.status != "accepted" or row.provenance_status == "passed" for row in g9)
    assert all(row.trajectory_status == "not_run" for row in g9)


def test_specialized_layers_use_specialized_contracts() -> None:
    rows = MODULE.build_rows()
    p6 = next(row for row in rows if row.cohort == "P6_SAFETY")
    p7 = next(row for row in rows if row.cohort == "P7_FTC")
    p8 = [row for row in rows if row.cohort == "P8_FORMATION"]

    assert p6.contract == "event_acknowledgement"
    assert p7.contract == "physical_rotor_loss_isolation_takeover_landing"
    assert len(p8) == 9
    assert all(row.contract == "three_uav_generated_formation" for row in p8)


def test_output_bundle_contains_report_figures(tmp_path: Path) -> None:
    payload = MODULE.write_outputs(MODULE.build_rows(), tmp_path)

    assert payload["status"] == "closed_with_blockers"
    assert payload["figures"] == [
        "figures/acceptance_status_counts.png",
        "figures/cohort_status_distribution.png",
        "figures/single_uav_hover_rmse.png",
    ]
    assert all((tmp_path / path).is_file() for path in payload["figures"])
