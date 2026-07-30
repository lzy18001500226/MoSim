#!/usr/bin/env python3
"""Static regression tests for long-duration sensitivity profile handling."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "control_platform" / "run_seven_scenario_batch.py"
PROFILE_PATHS = {
    "motor_efficiency_fault": ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_sensitivity_motor_v1.json",
    "wind_disturbance": ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_sensitivity_wind_v1.json",
    "parameter_mismatch": ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_sensitivity_param_v1.json",
}


def load_runner():
    spec = importlib.util.spec_from_file_location("sensitivity_batch_runner_test", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SensitivityProfileBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    def test_long_duration_profiles_parse_and_keep_four_gradient_points(self) -> None:
        expected = {
            "motor_efficiency_fault": [0.85, 0.75, 0.65, 0.55],
            "wind_disturbance": [0.2, 0.4, 0.6, 0.8],
            "parameter_mismatch": [1.1, 1.2, 1.3, 1.4],
        }
        for scenario, path in PROFILE_PATHS.items():
            document, _ = self.runner.read_profiles(path)
            self.assertEqual(len(document["profiles"]), 4)
            self.assertEqual({profile["scenario_id"] for profile in document["profiles"]}, {scenario})
            self.assertEqual(self.runner.expected_profile_strengths(document), expected[scenario])
            self.assertNotIn("time_varying_rotor_effectiveness", json.dumps(document))

    def test_four_profile_document_generates_eight_cases_in_dry_run(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "Results") as temporary:
            output = Path(temporary) / "motor"
            completed = subprocess.run(
                [
                    sys.executable, str(RUNNER),
                    "--profile", str(PROFILE_PATHS["motor_efficiency_fault"]),
                    "--controllers", "px4ctrl", "official_pid",
                    "--output", str(output),
                    "--dry-run",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            plan = json.loads((output / "SENSITIVITY_BATCH_PLAN.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["case_count"], 8)
            self.assertTrue((output / "px4ctrl" / "sensitivity_motor_efficiency_085_v1" / "RUN_CONFIG.json").is_file())

    def test_raw_result_export_reconciles_native_msr_only_failure(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "Results") as temporary:
            case_dir = Path(temporary) / "px4ctrl" / "sample"
            raw = case_dir / "raw" / "result.csv"
            metrics = case_dir / "metrics" / "METRICS.json"
            raw.parent.mkdir(parents=True)
            metrics.parent.mkdir(parents=True)
            raw.write_text("time,position[1]\n0,0\n", encoding="utf-8")
            metrics.write_text("{}\n", encoding="utf-8")
            requested_native = case_dir / "native_result" / "Result.msr"
            record_path = case_dir / "SENSITIVITY_RUN_RECORD.json"
            record_path.write_text(json.dumps({
                "status": "failed",
                "failure_reasons": ["native Result.msr is missing"],
                "session_result": {"result": {"native_result": str(requested_native.relative_to(ROOT))}},
                "artifacts": {
                    "raw_csv": str(raw.relative_to(ROOT)),
                    "metrics_json": str(metrics.relative_to(ROOT)),
                    "native_result": None,
                },
            }), encoding="utf-8")

            reconciled = self.runner.reconcile_existing_record(record_path)
            persisted = json.loads(record_path.read_text(encoding="utf-8"))

            self.assertTrue(reconciled["changed"])
            self.assertEqual(persisted["status"], "passed")
            self.assertEqual(persisted["failure_reasons"], [])
            self.assertEqual(
                persisted["result_binding"]["status"],
                "native_msr_not_materialized_raw_result_api_exported",
            )

    def test_check_model_status_can_be_recovered_from_mcp_log(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "Results") as temporary:
            log_path = Path(temporary) / "sysplorer_mcp.jsonl"
            model_name = "SensitivityOfficialPid_Sample"
            entries = [
                {
                    "direction": "request",
                    "id": 7,
                    "params": {
                        "name": "check_model",
                        "arguments": {"model_name": model_name, "stop_on_error": True},
                    },
                },
                {
                    "direction": "response",
                    "id": 7,
                    "result": {"content": [{"type": "text", "text": json.dumps({"ok": True})}]},
                },
            ]
            log_path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")

            self.assertEqual(self.runner.infer_check_model_status(log_path, model_name), "passed")

    def test_window_capture_command_is_bound_to_the_batch_mworks_pid(self) -> None:
        command = self.runner.build_capture_command(
            Path("Results/control_platform/sensitivity_wind_v1/preflight"),
            maximize=True,
            mworks_pid=4242,
        )

        self.assertIn("-ProcessId", command)
        self.assertEqual(command[command.index("-ProcessId") + 1], "4242")
        self.assertIn("-MinimizeAfter", command)

    def test_result_window_selection_requires_the_current_runner_title(self) -> None:
        capture = {
            "exit_code": 0,
            "manifest": "Results/example/capture_manifest.json",
            "command": ["powershell.exe"],
            "captured_windows": [
                {
                    "title": "OtherRunner - 结果查看器",
                    "path": "Results/example/other.png",
                    "helper_window": False,
                },
                {
                    "title": "CurrentRunner - Sysplorer [教育版]",
                    "path": "Results/example/main.png",
                    "helper_window": False,
                },
                {
                    "title": "CurrentRunner - 结果查看器",
                    "path": "Results/example/result.png",
                    "helper_window": False,
                },
            ],
        }

        selected = self.runner.select_result_window(capture, model_name="CurrentRunner")

        self.assertEqual(selected["capture_kind"], "model_bound_result_window")
        self.assertEqual(selected["selected_result_window"]["path"], "Results/example/result.png")
        self.assertEqual(len(selected["captured_windows"]), 3)


if __name__ == "__main__":
    unittest.main()
