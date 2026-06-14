#!/usr/bin/env python3
"""Tests for formal Dynamics static equation invariants."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "check_mosimquad_formal_dynamics_static_equation_invariants.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_mosimquad_formal_dynamics_static_equation_invariants", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsStaticEquationInvariantsTest(unittest.TestCase):
    def test_summary_passes_current_sources(self) -> None:
        module = load_module()
        summary = module.build_summary(module.READINESS)

        self.assertEqual(summary["status"], "passed")
        self.assertFalse(summary["live_mworks_touched"])
        self.assertEqual(summary["findings"], [])
        self.assertEqual(len(summary["anchor_groups"]), 4)
        self.assertEqual(len(summary["model_sources"]), 7)
        for group in summary["anchor_groups"]:
            self.assertEqual(group["missing_anchors"], [])
        for source in summary["model_sources"]:
            self.assertEqual(source["missing_instance_anchors"], [])
            self.assertTrue(source["dependency_anchor_groups"])

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "invariants.json"
            returncode = module.main(["--output", str(output)])
            self.assertEqual(returncode, 0)
            self.assertTrue(output.exists())
            self.assertTrue(output.with_suffix(".md").exists())


if __name__ == "__main__":
    unittest.main()
