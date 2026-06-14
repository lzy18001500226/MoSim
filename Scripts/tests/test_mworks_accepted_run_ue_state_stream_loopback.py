#!/usr/bin/env python3
"""Tests for accepted MWORKS run UE state stream UDP loopback smoke."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "UE5" / "smoke_mworks_accepted_run_ue_state_stream_loopback.py"


def load_module():
    spec = importlib.util.spec_from_file_location("smoke_mworks_accepted_run_ue_state_stream_loopback", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MworksAcceptedRunUeStateStreamLoopbackTest(unittest.TestCase):
    def test_loopback_receives_replay_frames_without_runtime_claims(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            summary = module.run_loopback(
                bundle_path=module.DEFAULT_BUNDLE,
                output_dir=Path(tmp),
                max_frames=3,
                timeout_s=8.0,
            )
            self.assertTrue(summary["ok"], summary["issues"])
            self.assertEqual(summary["scene_id"], "robust_rotor1_loss15_example1")
            self.assertEqual(summary["map_id"], "local_factoryenvironmentcollect")
            self.assertEqual(summary["received_packets"], 5)
            self.assertEqual(summary["received_frames"], 3)
            self.assertFalse(summary["ue_editor_opened"])
            self.assertFalse(summary["ue_runtime_started"])
            self.assertTrue(summary["not_runtime_ue_ack"])
            self.assertTrue((Path(tmp) / "ue_state_stream_loopback.json").exists())
            self.assertTrue((Path(tmp) / "received_ue_state_packets.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
