#!/usr/bin/env python3
"""Tests for Dynamics Batch A canonical source-ownership validation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "mworks" / "validate_mosimquad_dynamics_batch_a_source_migration.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_mosimquad_dynamics_batch_a_source_migration", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DynamicsBatchASourceMigrationTest(unittest.TestCase):
    def test_validate_batch_a_source_surface(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            summary = module.generate(Path(tmp))

            self.assertEqual(summary["status"], "passed")
            self.assertTrue(summary["static_only"])
            self.assertFalse(summary["live_mworks_touched"])
            self.assertFalse(summary["mworks_window_evidence_touched"])
            self.assertEqual(
                summary["batch_scope"],
                [
                    "MoSimQuadrotorModel.Vehicle.Dynamics.RotorActuatorCore",
                    "MoSimQuadrotorModel.Vehicle.Dynamics.WrapperSurface",
                ],
            )
            self.assertIn("MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.HoverSmoke", summary["deferred_targets"])

            matrix = json.loads((Path(tmp) / "batch_a_source_migration_matrix.json").read_text(encoding="utf-8"))
            self.assertEqual(matrix["status"], "passed_static")
            self.assertEqual(matrix["findings"], [])
            self.assertEqual(len(matrix["targets"]), 2)
            self.assertTrue(matrix["source_surface_policy"]["formal_sources_are_canonical_implementations"])
            self.assertTrue(matrix["source_surface_policy"]["retired_roots_absent"])
            self.assertFalse(matrix["source_surface_policy"]["dynamics_equations_changed_by_namespace_consolidation"])
            self.assertFalse(matrix["source_surface_policy"]["numeric_parameters_changed_by_namespace_consolidation"])
            self.assertTrue(all(item["canonical_source_owns_implementation"] for item in matrix["targets"]))
            self.assertTrue(all(item["retired_roots_absent"] for item in matrix["targets"]))
            self.assertTrue(all(item["migration_state"] == "canonical_single_root" for item in matrix["targets"]))


if __name__ == "__main__":
    unittest.main()
