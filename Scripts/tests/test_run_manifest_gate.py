from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_run_manifest.py"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def base_manifest(tmp_path: Path) -> dict:
    raw = tmp_path / "raw.csv"
    metrics = tmp_path / "metrics.json"
    setpoints = tmp_path / "setpoints.csv"
    command_echo = tmp_path / "ue_command_echo.jsonl"
    for path in [raw, metrics, setpoints, command_echo]:
        path.write_text("ok\n", encoding="utf-8")

    return {
        "schema_version": "mosim.run_manifest.v1",
        "run_id": "test_run",
        "objective": "unit test",
        "scene_id": "factory",
        "map_id": "factory_map",
        "vehicle_id": "sunray150",
        "controller_id": "pid",
        "planner_id": "ego_style",
        "quality_status": "pass",
        "evidence_level": "p0_closed_loop",
        "claim_scope": ["performance", "fast_lio", "planner", "closed_loop", "ue_visual"],
        "blockers": [],
        "sources": {
            "mworks_source": "MWORKS_MCP",
            "ros2_source": "ROS2_REALSTACK",
            "ue_source": "UE_SENSOR_ORACLE",
            "planner_input_source": "LOCAL_SENSED_MAP",
            "replay_source": "MWORKS_MCP",
        },
        "mworks": {
            "model_name": "QuadrotorExperiments.Example",
            "check_model_status": "pass",
            "simulate_status": "pass",
            "raw_csv": str(raw),
            "metrics_json": str(metrics),
            "setpoint_trace_consumption_status": "pass",
            "consumed_setpoint_trace": str(setpoints),
            "trace_consumption_evidence": str(metrics),
        },
        "ros2": {
            "bag_or_summary": "summary.json",
            "imu_rate_hz": 198.8,
            "lidar_rate_hz": 9.9,
            "tf_status": "pass",
            "timestamp_monotonic": True,
            "fast_lio_eval": {
                "status": "pass",
                "position_rmse_m": 0.39,
                "max_error_m": 0.61,
                "aligned_samples": 80,
            },
        },
        "planner": {
            "map_source": "fast_lio_local_3d_map",
            "global_truth_used_as_input": False,
            "setpoint_trace_source": "RUNTIME_20HZ_ADAPTER",
            "setpoint_adapter_status": "pass",
            "setpoint_trace": str(setpoints),
            "setpoint_rate_hz": 20.0,
            "stale_command_timeout_s": 0.15,
        },
        "ue": {
            "scene_registry_ref": "registry.json",
            "sensor_oracle_log": "sensor.jsonl",
            "command_echo_log": str(command_echo),
            "no_pose_overwrite_status": "pass",
        },
        "gate_results": {"required_checks": [], "warnings": [], "failures": []},
    }


def run_checker(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_run_manifest_gate_accepts_complete_p0_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "RUN_MANIFEST.json"
    write_json(manifest, base_manifest(tmp_path))
    completed = run_checker(manifest)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_run_manifest_gate_rejects_global_truth_planner_input(tmp_path: Path) -> None:
    payload = base_manifest(tmp_path)
    payload["sources"]["planner_input_source"] = "UE_GLOBAL_TRUTH"
    payload["planner"]["global_truth_used_as_input"] = True
    manifest = tmp_path / "RUN_MANIFEST.json"
    write_json(manifest, payload)
    completed = run_checker(manifest)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert any("global" in issue for issue in report["issues"])


def test_run_manifest_gate_rejects_slice_evidence_as_full_p0(tmp_path: Path) -> None:
    payload = base_manifest(tmp_path)
    payload["planner"]["setpoint_rate_hz"] = 0
    payload["planner"]["setpoint_trace"] = ""
    payload["ros2"]["fast_lio_eval"]["position_rmse_m"] = 2.0
    manifest = tmp_path / "RUN_MANIFEST.json"
    write_json(manifest, payload)
    completed = run_checker(manifest)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    joined = "\n".join(report["issues"])
    assert "setpoint_rate_hz" in joined
    assert "position_rmse_m" in joined


def test_run_manifest_gate_rejects_offline_handoff_as_runtime_adapter(tmp_path: Path) -> None:
    payload = base_manifest(tmp_path)
    offline_reference = tmp_path / "control_reference.csv"
    offline_reference.write_text("time,x_ref,y_ref,z_ref,yaw_ref\n0,0,0,1,0\n", encoding="utf-8")
    payload["planner"]["map_source"] = "offline_ue_navigation_control_interface_package"
    payload["planner"]["setpoint_trace_source"] = "OFFLINE_UE_NAVIGATION_HANDOFF"
    payload["planner"]["setpoint_adapter_status"] = "not_integrated"
    payload["planner"]["setpoint_trace"] = str(offline_reference)
    payload["planner"]["stale_command_timeout_s"] = 0
    manifest = tmp_path / "RUN_MANIFEST.json"
    write_json(manifest, payload)
    completed = run_checker(manifest)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    joined = "\n".join(report["issues"])
    assert "RUNTIME_20HZ_ADAPTER" in joined
    assert "setpoint_adapter_status" in joined
    assert "stale_command_timeout_s" in joined


def test_run_manifest_gate_rejects_closed_loop_without_same_mworks_trace(tmp_path: Path) -> None:
    payload = base_manifest(tmp_path)
    other_trace = tmp_path / "other_setpoints.csv"
    other_trace.write_text("time,x_ref,y_ref,z_ref,yaw_ref\n0,0,0,1,0\n", encoding="utf-8")
    payload["mworks"]["consumed_setpoint_trace"] = str(other_trace)
    manifest = tmp_path / "RUN_MANIFEST.json"
    write_json(manifest, payload)
    completed = run_checker(manifest)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert any("consumed_setpoint_trace to match" in issue for issue in report["issues"])
