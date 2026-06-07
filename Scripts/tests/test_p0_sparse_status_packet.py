#!/usr/bin/env python3
"""Regression test for the sparse P0 PMO status packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_p0_sparse_status_packet.py"
OUTPUT = ROOT / "Results" / "tmp" / "test_p0_sparse_status_packet.json"


def test_sparse_status_packet_does_not_claim_notification_or_closure() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--output-json",
            str(OUTPUT),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    packet = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert packet["template_type"] == "blocker_notification"
    assert packet["class"] == "manual_review_required"
    assert packet["task_id"] == "RFLY-MOSIM-P0-10H-20260606"
    assert packet["canonical_status"] == "blocked"
    assert packet["origin_thread_id"] == "019e9868-83ea-70f0-92c5-a3a408bd78c6"
    assert "P0 planner/closed_loop claim remains blocked" in packet["blocked_surface"]
    assert packet["schema_version"] == "mosim.pmo_sparse_status_packet.v1"
    assert packet["status"] == "progress_mworks_016_bridge_ros2_019_odom_cloud_restore_blocked"
    assert packet["quality_status"] == "smoke_only"
    assert packet["closed_loop_ready"] is False
    assert packet["planner_ready"] is False
    assert packet["wechat"]["send_attempted"] is False
    assert packet["wechat"]["packet_shape"] == "blocker_notification/manual_review_required"
    assert "ret=-2" in packet["wechat"]["reason"]
    assert packet["wechat"]["ops_incident"] == "WEIXIN-GATEWAY-INCIDENT-B0-MANIFEST-20260606-0459"
    assert any(path.endswith("P0_CLOSED_LOOP_GAP_MATRIX.json") for path in packet["evidence"])
    assert any(path.endswith("RUNTIME-DISABLED-SMOKE-20260606-017.json") for path in packet["evidence"])
    assert any(path.endswith("SENSOR-BUS-RECONNECT-20260606-015.json") for path in packet["evidence"])
    assert any(path.endswith("POSITION-BRIDGE-20260606-016.json") for path in packet["evidence"])
    assert any(path.endswith("REAL-PLANNER-INPUT-GATE-20260606-018.json") for path in packet["evidence"])
    assert any(path.endswith("ODOM-CLOUD-RESTORE-20260606-019.json") for path in packet["evidence"])
    assert any(path.endswith("odom_cloud_restore_summary.json") for path in packet["evidence"])
    assert any(item["id"] == "mworks_same_trace_consumption" for item in packet["current_blockers"])
    assert any(item["id"] == "mworks_sensor_bus_reconnect" for item in packet["current_blockers"])
    assert any(item["id"] == "mworks_position_bridge" for item in packet["current_blockers"])
    assert any(item["id"] == "ros2_real_planner_runtime" for item in packet["current_blockers"])
    assert any(item["id"] == "ros2_real_planner_input_gate" for item in packet["current_blockers"])
    assert any(item["id"] == "ros2_odom_cloud_restore" for item in packet["current_blockers"])
    assert any(item["id"] == "ros2_planner_dependency_surfaces" for item in packet["current_blockers"])
    waiting = {item["path"]: item["exists"] for item in packet["waiting_for_packets"]}
    assert not any(path.endswith("RATE-FEEDBACK-ISOLATION-20260606-014.json") for path in waiting)
    assert not any(path.endswith("YAW-RATE-DECOUPLING-20260606-013.json") for path in waiting)
    assert not any(path.endswith("PITCH-DECOUPLING-20260606-012.json") for path in waiting)
    assert not any(path.endswith("RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json") for path in waiting)
    assert not any(path.endswith("RUNTIME-DISABLED-SMOKE-20260606-017.json") for path in waiting)
    assert not any(path.endswith("RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json") for path in waiting)
    assert not any(path.endswith("PLANMANAGE-LINK-PREFLIGHT-20260606-014.json") for path in waiting)


if __name__ == "__main__":
    test_sparse_status_packet_does_not_claim_notification_or_closure()
    print("[OK] P0 sparse status packet")
