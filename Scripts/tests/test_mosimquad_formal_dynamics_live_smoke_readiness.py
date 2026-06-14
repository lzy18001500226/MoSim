#!/usr/bin/env python3
"""Tests for the formal Dynamics live-smoke readiness guard."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "check_mosimquad_formal_dynamics_live_smoke_readiness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_mosimquad_formal_dynamics_live_smoke_readiness", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsLiveSmokeReadinessTest(unittest.TestCase):
    def test_summary_is_ready_but_blocked_by_gui(self) -> None:
        module = load_module()
        summary = module.build_summary(
            module.SCENARIO_DIR,
            module.SCENARIO_CHECK,
            module.BATCH_MANIFEST,
            module.LIVE_PREFLIGHT_BLOCKER,
        )

        self.assertEqual(summary["status"], "ready_but_blocked_by_gui")
        self.assertEqual(summary["live_gate_state"], "blocked_by_current_gui_surface")
        self.assertFalse(summary["live_mworks_touched"])
        self.assertEqual(summary["scenario_count"], 7)
        self.assertEqual(summary["findings"], [])
        self.assertEqual(summary["current_gui_classifier"]["error_kind"], "gui_blocked")
        self.assertEqual(summary["current_gui_classifier"]["license_state_hint"], "upgrade_model_surface_blocked")

        output_paths = [path for scenario in summary["scenarios"] for path in scenario["output_paths"]]
        self.assertEqual(len(output_paths), len(set(output_paths)))
        self.assertTrue(any("rotor_effectiveness" in scenario["scenario"] for scenario in summary["scenarios"]))
        for scenario in summary["scenarios"]:
            self.assertEqual(scenario["missing_extra_variable_mappings"], [])

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "readiness.json"
            returncode = module.main(["--output", str(output)])
            self.assertEqual(returncode, 0)
            self.assertTrue(output.exists())
            self.assertTrue(output.with_suffix(".md").exists())


if __name__ == "__main__":
    unittest.main()
