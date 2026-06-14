#!/usr/bin/env python3
"""Tests for rotor1 loss15 candidate matrix builder."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "build_rotor1_loss15_candidate_matrix.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_rotor1_loss15_candidate_matrix", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Rotor1Loss15CandidateMatrixTest(unittest.TestCase):
    def test_current_matrix_has_one_accepted_current_candidate(self) -> None:
        module = load_module()
        matrix = module.build_matrix(module.SCENARIOS)

        self.assertEqual(matrix["status"], "ready_with_accepted_candidates")
        self.assertTrue(matrix["static_read_only"])
        self.assertFalse(matrix["live_mworks_touched"])
        self.assertEqual(matrix["scenario_count"], 11)
        self.assertEqual(matrix["accepted_candidate_count"], 1)
        self.assertEqual(matrix["needs_iteration_or_unverified_count"], 10)
        controllers = {row["controller_id"]: row for row in matrix["rows"]}
        self.assertEqual(controllers["pid_baseline"]["candidate_state"], "needs_iteration_or_unverified")
        self.assertEqual(controllers["awff_sysblock"]["candidate_state"], "needs_iteration_or_unverified")
        self.assertEqual(controllers["l1_fault_allocation_sysblock"]["candidate_state"], "needs_iteration_or_unverified")
        self.assertEqual(controllers["l1_online_fault_allocation_sysblock"]["candidate_state"], "needs_iteration_or_unverified")
        self.assertEqual(
            controllers["linear_mpc_online_fault_allocation_sysblock"]["candidate_state"],
            "accepted_candidate",
        )
        self.assertIn("Use accepted rotor1_loss15", "\n".join(matrix["recommended_next_steps"]))

    def test_best_candidate_is_current_linear_mpc_online_fault_allocation(self) -> None:
        module = load_module()
        matrix = module.build_matrix(module.SCENARIOS)

        best = matrix["best_rmse_candidate"]
        self.assertIsNotNone(best)
        self.assertEqual(best["controller_id"], "linear_mpc_online_fault_allocation_sysblock")
        self.assertEqual(best["quality_status"], "pass")

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "rotor1_loss15_candidate_matrix.json").exists())
            self.assertTrue((Path(tmp) / "rotor1_loss15_candidate_matrix.md").exists())


if __name__ == "__main__":
    unittest.main()
