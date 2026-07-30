#!/usr/bin/env python3
"""Static regression tests for sensitivity result classification."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "Scripts" / "analysis" / "analyze_sensitivity_results.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("sensitivity_analysis_test", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def motor_record(*, controller: str, efficiency: float, status: str, raw: str | None, terminal: float | None, reasons: list[str]):
    return {
        "controller_id": controller,
        "scenario_id": "motor_efficiency_fault",
        "profile_id": f"motor_{efficiency}",
        "status": status,
        "failure_reasons": reasons,
        "profile": {"runner_parameter_overrides": {"fault_rotor_effectiveness": efficiency}},
        "numerical_closure": {"terminal_time_s": terminal} if terminal is not None else {},
        "artifacts": {"raw_csv": raw, "metrics_json": None},
    }


class SensitivityAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_timeout_without_raw_result_is_not_a_threshold_failure(self) -> None:
        records = [
            motor_record(
                controller="official_pid",
                efficiency=0.85,
                status="failed",
                raw=None,
                terminal=None,
                reasons=["TimeoutError: Timeout waiting for MCP method tools/call"],
            ),
            motor_record(
                controller="px4ctrl",
                efficiency=0.85,
                status="passed",
                raw="Results/raw.csv",
                terminal=50.0,
                reasons=[],
            ),
            motor_record(
                controller="px4ctrl",
                efficiency=0.75,
                status="failed",
                raw="Results/raw.csv",
                terminal=20.0,
                reasons=["simulation ended at 20s before 50s"],
            ),
        ]

        rows, thresholds = self.analyzer.summarize(records)
        threshold_by_controller = {item["controller_id"]: item for item in thresholds}

        self.assertEqual(rows[0]["status"], "incomplete_timeout")
        self.assertEqual(threshold_by_controller["official_pid"]["threshold_status"], "incomplete")
        self.assertEqual(threshold_by_controller["px4ctrl"]["threshold_status"], "observed_grid_boundary")
        self.assertIn("15%", threshold_by_controller["px4ctrl"]["critical_threshold_description"])


if __name__ == "__main__":
    unittest.main()
