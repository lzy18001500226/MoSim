#!/usr/bin/env python3
"""Tests for the static MoSimQuadrotorModel live-gate runner plan."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "mworks" / "build_mosimquad_live_gate_runner_plan.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_mosimquad_live_gate_runner_plan", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MoSimQuadrotorLiveGateRunnerPlanTest(unittest.TestCase):
    def test_generate_static_runner_plan(self) -> None:
        module = load_module()
        temp_parent = module.DEFAULT_OUTPUT_DIR / "_test_tmp"
        temp_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_parent) as tmp:
            output_dir = Path(tmp)
            summary = module.generate(module.DEFAULT_INPUT_DIR, output_dir)

            self.assertEqual(summary["status"], "passed")
            self.assertFalse(summary["live_mworks_touched"])
            self.assertFalse(summary["mworks_window_evidence_touched"])

            plan = json.loads((output_dir / "live_gate_runner_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["status"], "passed_static")
            self.assertEqual(plan["future_check_model_plan"][0]["target"], "MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance")
            self.assertEqual(len(plan["future_check_model_plan"]), 14)
            self.assertEqual(len(plan["future_simulate_model_plan"]), 7)
            self.assertIn(
                "MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke",
                [item["target"] for item in plan["future_simulate_model_plan"]],
            )
            self.assertIn("target_resolution_manifest", plan)

            resolution = json.loads((output_dir / "target_resolution_check.json").read_text(encoding="utf-8"))
            self.assertEqual(resolution["status"], "passed_static")
            self.assertEqual(resolution["target_count"], 14)
            self.assertEqual(resolution["dynamics_target_count"], 13)
            self.assertEqual(resolution["parameter_target_count"], 1)
            self.assertEqual(resolution["findings"], [])

            probes = json.loads((output_dir / "result_variable_probe_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(probes["simulate_probe_count"], 7)
            self.assertEqual(probes["check_only_observability_count"], 6)


if __name__ == "__main__":
    unittest.main()
