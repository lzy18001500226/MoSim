#!/usr/bin/env python3
"""Focused regression check for the catalog-48 G3 reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "reconcile_g3_catalog_48_status.py"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "G3_CATALOG_48_CURRENT_STATUS.json"
        run([sys.executable, "-B", str(SCRIPT), "--output", str(output)])
        status = json.loads(output.read_text(encoding="utf-8"))
        summary = status["summary"]
        assert status["schema"] == "mosim.phase2_full_48_climbpath.g3_catalog_reconciliation.v1"
        assert summary == {
            "catalog_entry_count": 48,
            "historical_g3_execution_row_count": 48,
            "historical_g3_exact_count": 33,
            "historical_g3_alias_count": 8,
            "historical_g3_mapped_catalog_count": 41,
            "supplemental_current_record_count": 7,
            "post_freeze_current_override_record_count": 2,
            "formal_runner_missing_count": 0,
            "historical_g3_only_count": 7,
            "passed_count": 31,
            "failed_count": 17,
            "not_run_count": 0,
            "inventory_reconciled": True,
            "completed": False,
        }
        rows = {row["scheme_id"]: row for row in status["rows"]}
        assert len(rows) == 48
        assert rows["nmpc_outer"]["status"] == "pass"
        assert rows["smc_boundary_layer"]["status"] == "fail"
        assert rows["pid_awff_linear_eso"]["status"] == "fail"
        assert rows["fixed_awff_l1_residual"]["status"] == "fail"
        assert rows["fixed_awff_l1_indi"]["status"] == "pass"
        assert rows["fixed_linear_mpc_l1_indi"]["status"] == "pass"
        assert rows["fixed_qp_nmpc_l1_indi_cbf"]["status"] == "fail"
        assert rows["fixed_qp_nmpc_l1_indi_cbf"]["check_model_status"] == (
            "formal_runner_passed_mcp_timeout_native_completion_verified"
        )
        assert rows["pole_placement_luenberger"]["evidence_origin"] == "post_freeze_current_override_record"
        assert rows["pole_placement_luenberger"]["failure_class"] == "terminal_position_error_exceeds_5m"
        assert rows["pole_placement_luenberger"]["terminal_position_error_norm_m"] == 402.1409427651827
        assert rows["adaptive_mpc"]["evidence_origin"] == "post_freeze_current_override_record"
        assert rows["adaptive_mpc"]["status"] == "pass"
        assert rows["adaptive_mpc"]["terminal_position_error_norm_m"] == 0.003614672230764729
        assert status["unresolved_catalog_entries"] == []
        assert len(status["historical_g3_only_rows"]) == 7
        run([sys.executable, "-B", str(SCRIPT), "--output", str(output), "--check"])
    print("catalog-48 G3 reconciliation test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
