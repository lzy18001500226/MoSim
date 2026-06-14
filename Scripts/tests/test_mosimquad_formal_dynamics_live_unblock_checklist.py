#!/usr/bin/env python3
"""Tests for the formal Dynamics live-unblock checklist."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "build_mosimquad_formal_dynamics_live_unblock_checklist.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_mosimquad_formal_dynamics_live_unblock_checklist", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsLiveUnblockChecklistTest(unittest.TestCase):
    def test_current_state_requires_user_or_pmo_ui_decision(self) -> None:
        module = load_module()
        checklist = module.build_checklist(module.PREFLIGHT_BLOCKER, module.SMOKE_READINESS, module.RESULT_ACCEPTANCE)

        self.assertEqual(checklist["status"], "blocked_needs_user_or_pmo_ui_decision")
        self.assertEqual(checklist["unblock_state"], "blocked_needs_user_or_pmo_ui_decision")
        self.assertTrue(checklist["required_user_or_pmo_decision"])
        self.assertFalse(checklist["live_mworks_touched"])
        self.assertFalse(checklist["mworks_window_action_touched"])
        self.assertEqual(checklist["findings"], [])
        self.assertIn("升级模型", " ".join(checklist["allowed_next_action_when_clean"]["stop_before_command_on"]))

    def test_clean_classifier_allows_bounded_live_smoke_preflight(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            preflight = json.loads(module.PREFLIGHT_BLOCKER.read_text(encoding="utf-8"))
            clean_preflight = copy.deepcopy(preflight)
            clean_preflight["current_upgrade_classifier"] = {
                "status": "clean",
                "error_kind": "none",
                "license_state_hint": "clean",
                "upgrade_model_window_count": 0,
                "all_window_license_gate": "clean",
            }
            clean_preflight_path = tmp_path / "preflight_clean.json"
            clean_preflight_path.write_text(json.dumps(clean_preflight, ensure_ascii=False), encoding="utf-8")

            checklist = module.build_checklist(clean_preflight_path, module.SMOKE_READINESS, module.RESULT_ACCEPTANCE)

            self.assertEqual(checklist["status"], "ready_for_bounded_live_smoke_preflight")
            self.assertEqual(checklist["unblock_state"], "preflight_surface_clean")
            self.assertFalse(checklist["required_user_or_pmo_decision"])
            command_text = " ".join(str(item) for item in checklist["allowed_next_action_when_clean"]["command"])
            self.assertIn("Scripts/mworks/run_mworks_batch.py", command_text.replace("\\", "/"))
            self.assertIn("--no-gui-result-viewer", command_text)
            self.assertIn("--no-gui-open", command_text)

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            returncode = module.main(["--output-dir", tmp])
            self.assertEqual(returncode, 0)
            self.assertTrue((Path(tmp) / "live_unblock_checklist.json").exists())
            self.assertTrue((Path(tmp) / "live_unblock_checklist.md").exists())


if __name__ == "__main__":
    unittest.main()
