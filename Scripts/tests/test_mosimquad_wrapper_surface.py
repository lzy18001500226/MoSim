#!/usr/bin/env python3
"""Tests for WrapperSurface static source-surface validation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "mworks" / "validate_mosimquad_wrapper_surface.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_mosimquad_wrapper_surface", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WrapperSurfaceTest(unittest.TestCase):
    def test_validate_static_surface(self) -> None:
        module = load_module()
        temp_parent = module.DEFAULT_OUTPUT_DIR / "_test_tmp"
        temp_parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=temp_parent) as tmp:
            summary = module.generate(Path(tmp))

            self.assertEqual(summary["status"], "passed")
            self.assertTrue(summary["formal_source_materialized"])
            self.assertFalse(summary["live_mworks_touched"])
            self.assertFalse(summary["mworks_window_evidence_touched"])

            check = json.loads((Path(tmp) / "wrapper_surface_check.json").read_text(encoding="utf-8"))
            self.assertEqual(check["status"], "passed_static")
            self.assertEqual(check["findings"], [])
            self.assertTrue(check["behavior_preservation"]["formal_source_is_extends_only"])
            self.assertFalse(check["behavior_preservation"]["dynamics_equations_changed_by_026"])
            self.assertTrue(all(item["present"] for item in check["wrapper_anchors"]))
            self.assertTrue(all(item["present"] for item in check["underlying_core_anchors"]))
            self.assertTrue(all(item["present"] for item in check["provenance_anchors"]))
            self.assertTrue(all(item["present_in_wrapper_core_and_parameters"] for item in check["rotor_center_anchors"]))


if __name__ == "__main__":
    unittest.main()
