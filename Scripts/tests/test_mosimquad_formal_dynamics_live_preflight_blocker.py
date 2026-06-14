#!/usr/bin/env python3
"""Tests for the formal Dynamics live-preflight blocker checker."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "check_mosimquad_formal_dynamics_live_preflight_blocker.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_mosimquad_formal_dynamics_live_preflight_blocker", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsLivePreflightBlockerTest(unittest.TestCase):
    def test_summary_preserves_blocker_and_minimal_strategy(self) -> None:
        module = load_module()
        summary = module.build_summary()

        self.assertEqual(summary["status"], "blocked_by_upgrade_model_surface")
        self.assertEqual(summary["current_live_gate_result"], "blocked")
        self.assertEqual(summary["blocking_surface"], "upgrade_model_modal_or_progress_window")
        self.assertEqual(summary["next_load_strategy"]["name"], "minimal_dynamics_only")
        self.assertEqual(summary["scenario_count"], 7)
        self.assertEqual(summary["findings"], [])
        self.assertTrue(all(item["live_load_strategy"] == "minimal_dynamics_only" for item in summary["scenarios"]))

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "live_preflight_blocker_summary.json").exists())
            self.assertTrue((Path(tmp) / "live_preflight_blocker_summary.md").exists())


if __name__ == "__main__":
    unittest.main()
