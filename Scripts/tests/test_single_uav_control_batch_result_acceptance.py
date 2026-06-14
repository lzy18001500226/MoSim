#!/usr/bin/env python3
"""Tests for the single-UAV control batch result acceptance checker."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "check_single_uav_control_batch_result_acceptance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_single_uav_control_batch_result_acceptance", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SingleUavControlBatchResultAcceptanceTest(unittest.TestCase):
    def test_current_workspace_preserves_rotor_loss_iteration_targets(self) -> None:
        module = load_module()
        summary = module.build_summary(module.SCENARIO_PATHS)

        self.assertEqual(summary["status"], "needs_iteration")
        self.assertEqual(summary["scenario_count"], 13)
        self.assertEqual(summary["present_result_count"], 13)
        self.assertEqual(summary["accepted_result_count"], 11)
        self.assertEqual(summary["needs_iteration_count"], 2)
        self.assertEqual(summary["pending_result_count"], 0)
        self.assertEqual(summary["findings"], [])

        targets = {item["scenario"] for item in summary["iteration_targets"]}
        self.assertIn("Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml", targets)
        self.assertIn("Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml", targets)

    def test_missing_artifacts_fail_in_temp_scenario(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            scenario = Path(tmp) / "missing_result.yaml"
            scenario.write_text(
                "\n".join(
                    [
                        "experiment_id: tmp_missing",
                        "scene_id: official_example1",
                        "controller_id: pid_baseline",
                        "result:",
                        "  raw_file: missing/raw.csv",
                        "  metrics_file: missing/metrics.json",
                        "  mcp_log: missing/log.jsonl",
                    ]
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            summary = module.build_summary([str(scenario)])
            self.assertEqual(summary["status"], "failed")
            codes = {item["code"] for item in summary["findings"]}
            self.assertTrue({"raw_missing", "metrics_missing", "mcp_log_missing"}.issubset(codes))

    def test_temp_pass_scenario_is_accepted(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw.csv"
            metrics = root / "metrics.json"
            log = root / "run.jsonl"
            scenario = root / "scenario.yaml"
            raw.write_text(
                "time,x,y,z,x_ref,y_ref,z_ref\n"
                + "\n".join(f"{i},0,0,1,0,0,1" for i in range(11))
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            metrics.write_text(
                json.dumps(
                    {
                        "source": "MWORKS_MCP",
                        "evidence_level": "real_sysplorer_mcp_full_baseline",
                        "valid": True,
                        "quality_status": "pass",
                        "quality_pass": True,
                        "position_rmse_m": 0.1,
                        "max_position_error_m": 0.2,
                        "total_health_score": 80.0,
                        "nan_count": 0,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            log.write_text("{}\n", encoding="utf-8")
            scenario.write_text(
                "\n".join(
                    [
                        "experiment_id: tmp_pass",
                        "scene_id: official_example1",
                        "controller_id: pid_baseline",
                        "result:",
                        f"  raw_file: {str(raw).replace(chr(92), '/')}",
                        f"  metrics_file: {str(metrics).replace(chr(92), '/')}",
                        f"  mcp_log: {str(log).replace(chr(92), '/')}",
                    ]
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            summary = module.build_summary([str(scenario)])
            self.assertEqual(summary["status"], "passed")
            self.assertEqual(summary["accepted_result_count"], 1)
            self.assertEqual(summary["findings"], [])

    def test_cli_writes_outputs(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "acceptance.json"
            returncode = module.main(["--output", str(output)])
            self.assertEqual(returncode, 0)
            self.assertTrue(output.exists())
            self.assertTrue(output.with_suffix(".md").exists())


if __name__ == "__main__":
    unittest.main()
