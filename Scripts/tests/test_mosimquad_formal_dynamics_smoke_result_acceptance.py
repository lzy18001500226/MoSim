#!/usr/bin/env python3
"""Tests for formal Dynamics smoke result acceptance checker."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "quality" / "check_mosimquad_formal_dynamics_smoke_result_acceptance.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_mosimquad_formal_dynamics_smoke_result_acceptance", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormalDynamicsSmokeResultAcceptanceTest(unittest.TestCase):
    def test_current_workspace_has_accepted_live_smoke_results(self) -> None:
        module = load_module()
        summary = module.build_summary(module.SCENARIO_DIR)
        self.assertEqual(summary["status"], "passed")
        self.assertEqual(summary["present_result_count"], 7)
        self.assertEqual(summary["scenario_count"], 7)
        self.assertEqual(summary["missing_result_count"], 0)
        self.assertEqual(summary["findings"], [])

    def test_empty_temp_scenario_dir_is_pending_live_results(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            summary = module.build_summary(Path(tmp))
        self.assertEqual(summary["status"], "pending_live_results")
        self.assertEqual(summary["present_result_count"], 0)
        self.assertEqual(summary["scenario_count"], 0)
        self.assertEqual(summary["findings"], [])

    def test_complete_temp_result_passes_without_tracking_claims(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            scenario_dir = tmp_root / "scenarios"
            result_root = tmp_root / "results"
            scenario_dir.mkdir()
            source = ROOT / "Config" / "scenarios" / "diagnostics" / "mosimquad_dynamics_rotor_effectiveness_smoke.yaml"
            target = scenario_dir / source.name
            text = source.read_text(encoding="utf-8")
            raw = result_root / "raw.csv"
            metrics = result_root / "metrics.json"
            text = text.replace(
                "Results/diagnostics/mosimquad_formal_dynamics_smoke/mosimquad_dynamics_rotor_effectiveness_smoke/raw/mosimquad_dynamics_rotor_effectiveness_smoke.csv",
                str(raw).replace("\\", "/"),
            )
            text = text.replace(
                "Results/diagnostics/mosimquad_formal_dynamics_smoke/mosimquad_dynamics_rotor_effectiveness_smoke/metrics/mosimquad_dynamics_rotor_effectiveness_smoke.json",
                str(metrics).replace("\\", "/"),
            )
            target.write_text(text, encoding="utf-8", newline="\n")
            headers = [
                "time",
                "dynamics_rotor2_thrust_effectiveness",
                "dynamics_minimum_thrust_effectiveness",
                "total_thrust_loss",
                "roll_moment_imbalance",
                "pitch_moment_imbalance",
                "yaw_moment_imbalance",
            ]
            raw.parent.mkdir(parents=True)
            raw.write_text(
                ",".join(headers) + "\n" + "\n".join(
                    f"{index * 0.025:.3f},0.85,0.85,{index * 0.01:.3f},0.1,0.2,0.3"
                    for index in range(11)
                ) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            metrics.write_text(
                json.dumps(
                    {
                        "metrics_profile": "diagnostics_smoke",
                        "claim_role": "dynamics_smoke_only",
                        "valid": True,
                        "row_count": 11,
                        "nan_count": 0,
                    },
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )

            # The checker accepts partial scenario sets for unit testing a single
            # completed diagnostics result.
            summary = module.build_summary(scenario_dir)
            self.assertEqual(summary["status"], "passed")
            self.assertEqual(summary["present_result_count"], 1)
            self.assertEqual(summary["findings"], [])

    def test_tracking_metric_leak_fails(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            scenario_dir = tmp_root / "scenarios"
            scenario_dir.mkdir()
            source = ROOT / "Config" / "scenarios" / "diagnostics" / "mosimquad_dynamics_rotor_effectiveness_smoke.yaml"
            target = scenario_dir / source.name
            shutil.copy2(source, target)
            config = module.read_yaml(target)
            raw = tmp_root / "raw.csv"
            metrics = tmp_root / "metrics.json"
            config["result"]["raw_file"] = str(raw)
            config["result"]["metrics_file"] = str(metrics)
            target.write_text(
                "\n".join(
                    [
                        f"experiment_id: {config['experiment_id']}",
                        f"scene_id: {config['scene_id']}",
                        f"controller_id: {config['controller_id']}",
                        "evidence_level: future_live_mworks_formal_dynamics_smoke_contract",
                        "postprocess_profile: diagnostics_smoke",
                        "model:",
                        "  live_load_strategy: minimal_dynamics_only",
                        "  model_name: MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke",
                        "simulation:",
                        "  stop_time_s: 0.25",
                        "result:",
                        f"  raw_file: {str(raw).replace(chr(92), '/')}",
                        f"  metrics_file: {str(metrics).replace(chr(92), '/')}",
                        "  extra_variables:",
                        "    total_thrust_loss: total_thrust_loss",
                    ]
                ) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            raw.write_text("time,total_thrust_loss\n" + "\n".join(f"{i},1" for i in range(11)) + "\n", encoding="utf-8")
            metrics.write_text(
                '{"metrics_profile":"diagnostics_smoke","claim_role":"dynamics_smoke_only","valid":true,"position_rmse_m":0.1}\n',
                encoding="utf-8",
            )
            summary = module.build_summary(scenario_dir)
            self.assertEqual(summary["status"], "failed")
            self.assertTrue(any(item["code"] == "tracking_or_quality_claim_leak" for item in summary["findings"]))


if __name__ == "__main__":
    unittest.main()
