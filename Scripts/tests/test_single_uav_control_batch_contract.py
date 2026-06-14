#!/usr/bin/env python3
"""Tests for the single-UAV control batch contract."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "build_single_uav_control_batch_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_single_uav_control_batch_contract", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SingleUavControlBatchContractTest(unittest.TestCase):
    def test_curated_batch_passes_and_excludes_formation(self) -> None:
        module = load_module()
        contract = module.build_contract(module.SCENARIO_PATHS)

        self.assertEqual(contract["status"], "passed")
        self.assertFalse(contract["live_mworks_touched"])
        self.assertEqual(contract["scope"], "single_uav_control_before_multi_uav")
        self.assertEqual(contract["scenario_count"], 13)
        self.assertEqual(contract["findings"], [])
        self.assertTrue(all(contract["coverage"].values()))
        self.assertTrue(contract["coverage"]["formation_excluded"])

        controllers = {item["controller_id"] for item in contract["scenarios"]}
        self.assertIn("pid_baseline", controllers)
        self.assertIn("awff_sysblock", controllers)
        self.assertIn("awff_indi_sysblock", controllers)
        self.assertIn("improved_pid", controllers)
        self.assertIn("linear_mpc_sysblock", controllers)

        command_text = " ".join(str(item) for item in contract["future_live_batch_command"])
        self.assertIn("Scripts/mworks/run_mworks_batch.py", command_text.replace("\\", "/"))
        self.assertIn("--no-gui-result-viewer", command_text)
        self.assertIn("--no-gui-open", command_text)
        self.assertIn("example3_linear_mpc_sysblock.yaml", command_text)

    def test_optimized_scenarios_have_batch_baselines(self) -> None:
        module = load_module()
        contract = module.build_contract(module.SCENARIO_PATHS)
        experiment_ids = {item["experiment_id"] for item in contract["scenarios"]}

        for item in contract["scenarios"]:
            if item["controller_id"] == "pid_baseline":
                self.assertEqual(item["baseline_experiment"], "")
            else:
                self.assertIn(item["baseline_experiment"], experiment_ids)
                self.assertTrue(item["result"]["metrics_file"])
                self.assertIn(item["baseline_source"], {"declared", "inferred_same_scene_pid"})

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "single_uav_control_batch_contract.json").exists())
            self.assertTrue((Path(tmp) / "single_uav_control_batch_contract.md").exists())


if __name__ == "__main__":
    unittest.main()
