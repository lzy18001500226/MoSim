#!/usr/bin/env python3
"""Tests for rotor1 loss15 error profile builder."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "profile_rotor1_loss15_error.py"


def load_module():
    spec = importlib.util.spec_from_file_location("profile_rotor1_loss15_error", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Rotor1Loss15ErrorProfileTest(unittest.TestCase):
    def test_current_profiles_are_read_only_iteration_diagnostics(self) -> None:
        module = load_module()
        profile = module.build_profile(module.SCENARIOS)

        self.assertEqual(profile["status"], "diagnostic_profile_ready")
        self.assertTrue(profile["static_read_only"])
        self.assertFalse(profile["live_mworks_touched"])
        self.assertEqual(profile["scenario_count"], 2)
        self.assertTrue(all(item["quality_status"] == "needs_iteration" for item in profile["profiles"]))
        self.assertTrue(profile["comparison"]["available"])
        self.assertGreater(profile["comparison"]["rmse_improvement_pct"], 0.0)
        self.assertIn("single_uav", profile["scope"])
        self.assertNotIn("formation", profile["scope"])

    def test_phase_profiles_cover_expected_windows(self) -> None:
        module = load_module()
        profile = module.build_profile(module.SCENARIOS)

        expected = {name for name, _, _ in module.PHASES}
        for item in profile["profiles"]:
            phases = {phase["phase"] for phase in item["phase_profiles"]}
            self.assertEqual(phases, expected)
            self.assertTrue(all(phase["row_count"] > 0 for phase in item["phase_profiles"]))
            self.assertIn(item["worst_phase"], expected)
            self.assertIn(item["dominant_axis_overall"], {"x", "y", "z"})

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "rotor1_loss15_error_profile.json").exists())
            self.assertTrue((Path(tmp) / "rotor1_loss15_error_profile.md").exists())


if __name__ == "__main__":
    unittest.main()
