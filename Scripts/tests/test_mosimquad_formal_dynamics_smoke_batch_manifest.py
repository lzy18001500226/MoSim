#!/usr/bin/env python3
"""Tests for the formal Dynamics smoke batch manifest."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "build_mosimquad_formal_dynamics_smoke_batch_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_mosimquad_formal_dynamics_smoke_batch_manifest", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsSmokeBatchManifestTest(unittest.TestCase):
    def test_build_manifest(self) -> None:
        module = load_module()
        manifest = module.build_manifest(module.SCENARIO_CHECK)

        self.assertEqual(manifest["status"], "passed")
        self.assertFalse(manifest["live_mworks_touched"])
        self.assertFalse(manifest["mworks_window_evidence_touched"])
        self.assertEqual(manifest["scenario_count"], 7)
        self.assertEqual(manifest["runner_support_status"], "minimal_dynamics_strategy_consumed")
        self.assertEqual(manifest["findings"], [])

        command_text = " ".join(manifest["future_live_batch_command"])
        self.assertIn("Scripts/mworks/run_mworks_batch.py", command_text.replace("\\", "/"))
        self.assertIn("--no-gui-result-viewer", command_text)
        self.assertIn("--no-gui-open", command_text)
        self.assertIn("mosimquad_dynamics_rotor_effectiveness_smoke.yaml", command_text)

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "formal_dynamics_smoke_batch_manifest.json").exists())
            self.assertTrue((Path(tmp) / "formal_dynamics_smoke_batch_manifest.md").exists())


if __name__ == "__main__":
    unittest.main()
