from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MWORKS_DIR = ROOT / "Scripts" / "mworks"
if str(MWORKS_DIR) not in sys.path:
    sys.path.insert(0, str(MWORKS_DIR))

import run_g6_formal_closed_loop_baseline as baseline  # noqa: E402


class G6FormalClosedLoopBaselineContractTests(unittest.TestCase):
    def test_official_pid_binding_is_hash_bound_and_outside_the_frozen_matrix(self) -> None:
        binding = baseline.resolve_formal_binding()

        self.assertEqual(binding["controller_id"], "official_pid")
        self.assertEqual(binding["scenario_id"], "climb_path_50s")
        self.assertEqual(binding["duration_s"], 50.0)
        self.assertEqual(
            binding["target"]["model_class"],
            "MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner",
        )
        self.assertEqual(binding["formal_adapter"]["output_boundary"], "ROTOR_COMMAND")
        self.assertTrue(all(source["expected_sha256"] for source in binding["source_bindings"]))
        self.assertNotIn("sensors1_1", baseline.FORMAL_VARIABLES.values())
        self.assertEqual(baseline.FORMAL_VARIABLES["x"], "position[1]")
        self.assertEqual(baseline.FORMAL_VARIABLES["u4"], "rotor_command[4]")
        self.assertTrue(
            {role for role, _ in baseline.SHARED_CLOSURE_SOURCES}.issubset(
                {source["role"] for source in binding["source_bindings"]}
            )
        )
        self.assertEqual(
            set(baseline.RESULT_VIEWER_VARIABLES),
            {"time", "x", "y", "z", "x_ref", "y_ref", "z_ref"},
        )


if __name__ == "__main__":
    unittest.main()
