#!/usr/bin/env python3
"""Tests for rotor1 loss15 iteration plan builder."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "build_rotor1_loss15_iteration_plan.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_rotor1_loss15_iteration_plan", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Rotor1Loss15IterationPlanTest(unittest.TestCase):
    def test_current_workspace_is_blocked_by_upgrade_model_surface(self) -> None:
        module = load_module()
        plan = module.build_plan(module.BLOCKER_SENTINEL)

        self.assertEqual(plan["status"], "blocked_by_mworks_gui")
        self.assertEqual(plan["live_gate"]["license_state_hint"], "upgrade_model_surface_blocked")
        self.assertFalse(plan["live_gate"]["live_run_allowed_now"])
        self.assertEqual(plan["scenario_count"], 2)
        self.assertTrue(all(row["current_quality_status"] == "needs_iteration" for row in plan["scenarios"]))
        command = " ".join(str(item) for item in plan["future_live_rerun_command"])
        self.assertIn("--allow-needs-iteration", command)
        self.assertIn("example1_rotor1_loss15_pid_baseline.yaml", command)
        self.assertIn("example1_rotor1_loss15_awff_sysblock.yaml", command)
        self.assertNotIn("formation", command.lower())

    def test_clean_sentinel_allows_bounded_live_rerun_plan(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = Path(tmp) / "sentinel.json"
            sentinel.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "error_kind": "",
                        "license_state_hint": "clean",
                        "blocking_mworks_window_count": 0,
                        "upgrade_model_window_count": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            plan = module.build_plan(sentinel)
            self.assertEqual(plan["status"], "ready_for_bounded_live_rerun")
            self.assertTrue(plan["live_gate"]["live_run_allowed_now"])

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "rotor1_loss15_iteration_plan.json").exists())
            self.assertTrue((Path(tmp) / "rotor1_loss15_iteration_plan.md").exists())


if __name__ == "__main__":
    unittest.main()
