#!/usr/bin/env python3
"""Tests for rotor1 loss15 command semantics profile."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "profile_rotor1_loss15_command_semantics.py"


def load_module():
    spec = importlib.util.spec_from_file_location("profile_rotor1_loss15_command_semantics", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Rotor1Loss15CommandSemanticsTest(unittest.TestCase):
    def test_current_profile_confirms_source_topology_is_hover_mapped(self) -> None:
        module = load_module()
        profile = module.build_profile(module.SCENARIOS)

        self.assertEqual(profile["status"], "diagnostic_profile_ready")
        self.assertTrue(profile["static_read_only"])
        self.assertFalse(profile["live_mworks_touched"])
        self.assertEqual(profile["scenario_count"], 7)
        self.assertEqual(profile["direct_delta_mismatch_count"], 0)
        self.assertEqual(profile["hover_mapped_count"], 7)
        controllers = {item["controller_id"]: item for item in profile["profiles"]}
        self.assertEqual(
            controllers["l1_fault_allocation_sysblock"]["inferred_command_semantics"],
            "controller_outputs_delta_commands_mapped_to_hover_actuator_domain",
        )
        self.assertEqual(
            controllers["linear_mpc_sysblock"]["inferred_command_semantics"],
            "controller_outputs_delta_commands_mapped_to_hover_actuator_domain",
        )

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "rotor1_loss15_command_semantics.json").exists())
            self.assertTrue((Path(tmp) / "rotor1_loss15_command_semantics.md").exists())


if __name__ == "__main__":
    unittest.main()
