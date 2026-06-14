#!/usr/bin/env python3
"""Tests for formal Dynamics smoke scenario bindings."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "check_mosimquad_formal_dynamics_smoke_scenarios.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_mosimquad_formal_dynamics_smoke_scenarios", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsSmokeScenarioTest(unittest.TestCase):
    def test_validate_formal_dynamics_smoke_scenarios(self) -> None:
        module = load_module()
        summary = module.validate(module.SCENARIO_DIR, module.PROBE_PLAN)

        self.assertEqual(summary["status"], "passed")
        self.assertFalse(summary["live_mworks_touched"])
        self.assertFalse(summary["mworks_window_evidence_touched"])
        self.assertEqual(summary["expected_simulate_target_count"], 7)
        self.assertEqual(summary["scenario_target_count"], 7)
        self.assertEqual(summary["findings"], [])
        self.assertEqual(summary["runner_support_status"], "minimal_dynamics_strategy_consumed")

        targets = {item["target"] for item in summary["bindings"]}
        self.assertIn("MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke", targets)
        for binding in summary["bindings"]:
            self.assertEqual(binding["live_load_strategy"], "minimal_dynamics_only")
            command_text = " ".join(binding["dry_run_command"])
            self.assertIn("--no-gui-result-viewer", command_text)
            self.assertIn("--no-gui-open", command_text)
            command_text_normalized = command_text.replace("\\", "/")
            self.assertIn("Results/generated_mworks/minimal_dynamics_only/QuadrotorExperiments/package.mo", command_text_normalized)
            self.assertIn("Results/generated_mworks/minimal_dynamics_only/MoSimQuadrotorModel/package.mo", command_text_normalized)
            self.assertNotIn("Models/MoSimQuadrotorModel/package.mo", command_text_normalized)
            self.assertFalse(binding["missing_extra_variable_mappings"])

    def test_cli_writes_summary(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            returncode = module.main(["--output", str(output)])
            self.assertEqual(returncode, 0)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
