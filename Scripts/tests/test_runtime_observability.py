from __future__ import annotations

from collections import namedtuple
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts/runtime/collect_runtime_observability.py"
SPEC = importlib.util.spec_from_file_location("collect_runtime_observability", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_200hz_observability_contract_matches_promoted_rt0_timing() -> None:
    contract = json.loads(
        (ROOT / "Config/control_platform/runtime_observability_contract_v1.json").read_text(encoding="utf-8")
    )
    scan = contract["control_rate_capability_scan"]
    timing = contract["diagnostic_thresholds"]["control_200hz"]
    assert scan["target_rate_hz"] == 200
    assert scan["target_status"] == "rt0_validated_rt1_pending"
    assert timing["nominal_period_ms"] == 5.0
    assert timing["soft_deadline_warning_ms"] == 5.0
    assert timing["deadline_ms"] == 10.0


def test_counter_rates_are_nonnegative_and_time_normalized() -> None:
    Counter = namedtuple("Counter", "bytes_sent bytes_recv")
    assert MODULE.counter_rates(Counter(1200, 2400), Counter(1000, 2000), 2.0, ("bytes_sent", "bytes_recv")) == {
        "bytes_sent_per_s": 100.0,
        "bytes_recv_per_s": 200.0,
    }


def test_process_groups_only_match_runtime_authorities() -> None:
    assert "wsl.exe" not in MODULE.PROCESS_GROUPS["wsl_vm"]
    assert "wslhost.exe" not in MODULE.PROCESS_GROUPS["wsl_vm"]
    assert "vmmemwsl" in MODULE.PROCESS_GROUPS["wsl_vm"]
    assert "mwsolver.exe" in MODULE.PROCESS_GROUPS["mworks_solver"]


def test_process_sampler_derives_cpu_percent_from_cumulative_time() -> None:
    sampler = MODULE.AsyncProcessGroupSampler()
    sampler._consume(
        100.0,
        {"mworks_solver": {"process_count": 1, "cpu_time_s": 10.0, "resident_memory_bytes": 20}},
    )
    sampler._consume(
        102.0,
        {"mworks_solver": {"process_count": 1, "cpu_time_s": 11.0, "resident_memory_bytes": 30}},
    )
    assert sampler._latest["mworks_solver"] == {
        "process_count": 1,
        "cpu_percent": 50.0,
        "resident_memory_bytes": 30,
    }


def test_summary_reports_mean_p95_and_max() -> None:
    samples = [{"host": {"cpu_total_percent": value}} for value in (10.0, 20.0, 30.0)]
    summary = MODULE.summarize(samples)["cpu_total_percent"]
    assert summary == {"mean": 20.0, "p95": 30.0, "max": 30.0}


def test_summary_prioritizes_control_rate_before_gazebo_and_display_findings() -> None:
    sample = {
        "host": {"cpu_total_percent": 95.0, "memory_percent": 20.0},
        "components": {
            "mworks_ros_control": {
                "state": "available",
                "metrics": {"transport": {"command_receive_rate_hz": 190.0, "estimated_command_drop_rate": 0.01}},
            },
            "ros1_topics": {
                "state": "available",
                "metrics": {"gazebo": {"clock_derived_real_time_factor": 0.8}},
            },
            "gazebo_ue_receiver": {
                "state": "available",
                "metrics": {"receiver_drop_rate": 0.02},
            },
            "ue_frame_timing": {"state": "available", "metrics": {"ue_fps": 40.0}},
            "qgc_telemetry": {
                "state": "available",
                "metrics": {"vehicle_counters": {"mavlink_loss_percent": 1.0}},
            },
        },
    }
    findings = MODULE.diagnostic_findings(sample, MODULE.summarize([sample]), 200.0)
    assert [finding["priority"] for finding in findings] == sorted(finding["priority"] for finding in findings)
    assert findings[0]["component"] == "mworks_ros_control"
    assert {finding["code"] for finding in findings} >= {
        "control_rate_below_target",
        "control_command_loss_observed",
        "gazebo_real_time_factor_low",
        "ue_receiver_sequence_loss_observed",
        "ue_fps_low",
        "qgc_mavlink_loss_observed",
        "host_cpu_saturation",
    }


def test_component_metric_fails_closed_for_wrong_run_id(tmp_path: Path) -> None:
    metric = tmp_path / "metric.json"
    metric.write_text('{"run_id":"run-other","updated_at_unix":1}', encoding="utf-8")
    result = MODULE.read_component_metric(metric, "run-expected", 5.0)
    assert result["state"] == "invalid"
    assert result["reason"] == "run_id_mismatch"


def test_first_component_metric_reports_all_missing_candidates(tmp_path: Path) -> None:
    result = MODULE.read_first_component_metric(
        (tmp_path / "one.json", tmp_path / "two.json"), "run-expected", 5.0
    )
    assert result["state"] == "unavailable"
    assert len(result["paths"]) == 2


def test_qgc_metric_is_bound_to_the_same_run(tmp_path: Path) -> None:
    metric = tmp_path / "mavlink_qgc.json"
    metric.write_text('{"run_id":"run-expected","updated_at_unix":9999999999}', encoding="utf-8")
    result = MODULE.read_component_metric(metric, "run-expected", 5.0)
    assert result["state"] == "available"
    assert result["metrics"]["run_id"] == "run-expected"


def test_qgc_observability_source_keeps_unmeasured_rtt_and_ui_fps_unavailable() -> None:
    source = (ROOT / "apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.cc").read_text(
        encoding="utf-8"
    )
    assert "mavlink_qgc.json" in source
    assert "no_correlated_qgc_ping_measurement" in source
    assert "qt_quick_render_instrumentation_not_attached" in source
    assert "Transport byte counters include MAVLink framing but not inferred UDP/IP overhead." in source


def test_ros1_collector_keeps_zero_samples_explicitly_unavailable() -> None:
    ros_module_path = ROOT / "Scripts/runtime/collect_ros1_observability.py"
    spec = importlib.util.spec_from_file_location("collect_ros1_observability", ros_module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    snapshot = module.TopicWindow(5.0).snapshot()
    assert snapshot["state"] == "no_samples"
    assert snapshot["sample_count"] == 0


def test_collector_publishes_summary_before_process_exit(tmp_path: Path) -> None:
    run_id = "run-observability-live-summary"
    manifest = {
        "run_id": run_id,
        "mworks_live_connection": {"selected_rate_hz": 200},
    }
    (tmp_path / "RUN_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    summary_path = tmp_path / "observability" / "RUNTIME_OBSERVABILITY_SUMMARY.json"
    process = subprocess.Popen(
        [
            sys.executable,
            str(MODULE_PATH),
            "--run-id",
            run_id,
            "--run-dir",
            str(tmp_path),
            "--interval-s",
            "0.2",
            "--duration-s",
            "1.5",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 1.2
        observed_while_running = False
        while time.monotonic() < deadline and process.poll() is None:
            if summary_path.exists():
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                if summary.get("sample_count", 0) >= 1:
                    observed_while_running = True
                    assert summary["run_id"] == run_id
                    assert summary["target_control_rate_hz"] == 200.0
                    break
            time.sleep(0.05)
        assert observed_while_running
        stdout, stderr = process.communicate(timeout=4.0)
        assert process.returncode == 0, stderr or stdout
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=2.0)
