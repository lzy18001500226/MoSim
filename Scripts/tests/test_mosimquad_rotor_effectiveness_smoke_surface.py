#!/usr/bin/env python3
"""Tests for canonical RotorEffectivenessSmoke source ownership."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "LegacyDiagnostics" / "RotorEffectivenessSmoke.mo"
FORMAL_DIAGNOSTICS_DIR = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "LegacyDiagnostics"
FORMAL_PACKAGE = FORMAL_DIAGNOSTICS_DIR / "package.mo"
RETIRED_ROOTS = (
    ROOT / "Models" / "QuadrotorExperiments",
    ROOT / "Models" / "QuadrotorControllerBlocks",
    ROOT / "Models" / "MworksLive",
    ROOT / "Models" / "MoSimQuadrotorModel_backup",
)
SCRIPT_PATH = ROOT / "Scripts" / "mworks" / "validate_mosimquad_formal_smoke_surface.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_mosimquad_formal_smoke_surface", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RotorEffectivenessSmokeSurfaceTest(unittest.TestCase):
    def test_formal_source_is_canonical_implementation(self) -> None:
        source = FORMAL_SOURCE.read_text(encoding="utf-8")
        package = FORMAL_PACKAGE.read_text(encoding="utf-8")

        self.assertIn("within MoSimQuadrotorModel.Vehicle.LegacyDiagnostics;", source)
        self.assertIn("model RotorEffectivenessSmoke", source)
        self.assertIn("equation", source)
        self.assertIn("MoSimQuadrotorModel.Vehicle.Dynamics.RotorActuatorCore dynamics(", source)
        self.assertNotIn("QuadrotorExperiments", source)
        self.assertNotIn("Deprecated compatibility alias", source)
        self.assertNotIn("model RotorEffectivenessSmoke", package)
        self.assertTrue(all(not root.exists() for root in RETIRED_ROOTS))

    def test_all_formal_targets_are_canonical_sources(self) -> None:
        module = load_module()
        package = FORMAL_PACKAGE.read_text(encoding="utf-8")

        self.assertNotIn("\n  model ", package)
        for formal_name in module.FORMAL_PACKAGE_ORDER:
            source_path = module.source_dir_for(formal_name) / f"{formal_name}.mo"
            self.assertTrue(source_path.exists(), f"missing {source_path}")
            source = source_path.read_text(encoding="utf-8")
            self.assertIn(f"model {formal_name}", source)
            self.assertIn(
                f"within {module.target_namespace_for(formal_name)};",
                source,
            )
            self.assertNotIn("QuadrotorExperiments", source)
            self.assertNotIn("Deprecated compatibility alias", source)

    def test_formal_smoke_matrix_requires_canonical_source(self) -> None:
        module = load_module()
        matrix, findings = module.build_matrix()
        self.assertEqual(findings, [])
        target = next(
            item
            for item in matrix
            if item["formal_target"]
            == "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.RotorEffectivenessSmoke"
        )
        self.assertTrue(target["dedicated_formal_source_required"])
        self.assertTrue(target["formal_source_present"])
        self.assertEqual(
            target["formal_source_file"],
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/RotorEffectivenessSmoke.mo",
        )
        self.assertEqual(target["implementation_file"], target["formal_source_file"])
        self.assertTrue(all(item["dedicated_formal_source_required"] for item in matrix))
        self.assertTrue(all(item["formal_source_present"] for item in matrix))


if __name__ == "__main__":
    unittest.main()
