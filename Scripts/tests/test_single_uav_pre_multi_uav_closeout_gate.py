#!/usr/bin/env python3
"""Tests for single-UAV pre multi-UAV closeout gate."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "build_single_uav_pre_multi_uav_closeout_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_single_uav_pre_multi_uav_closeout_gate", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SingleUavPreMultiUavCloseoutGateTest(unittest.TestCase):
    def test_current_gate_uses_latest_clean_sentinel(self) -> None:
        module = load_module()
        gate = module.build_gate(
            module.DEFAULT_ACCEPTANCE,
            module.DEFAULT_ERROR_PROFILE,
            module.DEFAULT_CANDIDATE_MATRIX,
            module.find_latest_sentinel(),
        )

        self.assertEqual(gate["status"], "single_uav_gate_ready_for_ue_prep")
        self.assertEqual(gate["decision"], "prepare_ue_replay_inputs_directly_when_user_authorized")
        self.assertTrue(gate["live_gate"]["live_mworks_allowed"])
        self.assertEqual(gate["batch_acceptance_summary"]["accepted_result_count"], 11)
        self.assertEqual(gate["batch_acceptance_summary"]["needs_iteration_count"], 2)
        self.assertEqual(gate["rotor1_candidate_summary"]["accepted_candidate_count"], 1)
        self.assertTrue(gate["current_candidate_rerun_evidence"]["accepted_current_rerun"])
        self.assertIn("Prepare a UE replay/render input bundle", "\n".join(gate["required_before_multi_uav"]))

    def test_explicit_blocked_sentinel_blocks_live_gate(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = Path(tmp) / "blocked_sentinel.json"
            sentinel.write_text(
                json.dumps(
                    {
                        "status": "incident_detected",
                        "error_kind": "gui_blocked",
                        "license_state_hint": "upgrade_model_surface_blocked",
                        "blocking_mworks_window_count": 1,
                        "upgrade_model_window_count": 1,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            gate = module.build_gate(
                module.DEFAULT_ACCEPTANCE,
                module.DEFAULT_ERROR_PROFILE,
                module.DEFAULT_CANDIDATE_MATRIX,
                sentinel,
            )
            self.assertEqual(gate["status"], "blocked_by_live_mworks_gate")
            self.assertEqual(gate["decision"], "do_not_enter_multi_uav_yet")
            self.assertFalse(gate["live_gate"]["live_mworks_allowed"])

    def test_clean_sentinel_with_current_candidate_allows_ue_prep_review(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = Path(tmp) / "sentinel.json"
            sentinel.write_text(
                json.dumps(
                    {
                        "created_at": "2026-06-12T02:24:49+08:00",
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
            gate = module.build_gate(
                module.DEFAULT_ACCEPTANCE,
                module.DEFAULT_ERROR_PROFILE,
                module.DEFAULT_CANDIDATE_MATRIX,
                sentinel,
            )
            self.assertEqual(gate["status"], "single_uav_gate_ready_for_ue_prep")
            self.assertEqual(gate["decision"], "prepare_ue_replay_inputs_directly_when_user_authorized")
            self.assertTrue(gate["current_candidate_rerun_evidence"]["accepted_current_rerun"])
            self.assertIn("proceed to UE replay/render input preparation", "\n".join(gate["required_before_multi_uav"]))

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "single_uav_pre_multi_uav_closeout_gate.json").exists())
            self.assertTrue((Path(tmp) / "single_uav_pre_multi_uav_closeout_gate.md").exists())


if __name__ == "__main__":
    unittest.main()
