#!/usr/bin/env python3
"""Tests for accepted MWORKS run to UE replay input bundle."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "UE5" / "build_mworks_accepted_run_ue_replay_input_bundle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_mworks_accepted_run_ue_replay_input_bundle", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MworksAcceptedRunUeReplayInputBundleTest(unittest.TestCase):
    def test_current_bundle_is_source_static_and_ue_prep_ready(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = module.build_bundle(
                module.DEFAULT_CLOSEOUT,
                Path(tmp),
                "robust_rotor1_loss15_example1",
                "local_factoryenvironmentcollect",
            )
            self.assertEqual(bundle["status"], "ready_for_source_static_ue_replay_input")
            self.assertTrue(bundle["source_static_only"])
            self.assertFalse(bundle["ue_editor_opened"])
            self.assertFalse(bundle["ue_runtime_started"])
            self.assertFalse(bundle["udp_sent"])
            self.assertEqual(bundle["accepted_candidate"]["controller_id"], "linear_mpc_online_fault_allocation_sysblock")
            self.assertEqual(bundle["artifacts"]["raw"]["row_count"], 25001)
            self.assertEqual(bundle["stream_contract_dry_run"]["frame_scene_id"], "robust_rotor1_loss15_example1")
            self.assertEqual(bundle["stream_contract_dry_run"]["frame_map_id"], "local_factoryenvironmentcollect")
            self.assertEqual(bundle["scene_binding"]["map_id_role"], "registry_scene_source_id_for_AQuadrotorMworksMapActor.ResolveSceneSourceId")
            self.assertIn("frame", bundle["stream_contract_dry_run"]["packet_types"])
            self.assertIn("UE runtime success", bundle["forbidden_claims"])
            self.assertTrue((Path(tmp) / "ue_replay_input_bundle.json").exists())
            self.assertTrue((Path(tmp) / "ue_replay_input_bundle.md").exists())


if __name__ == "__main__":
    unittest.main()
