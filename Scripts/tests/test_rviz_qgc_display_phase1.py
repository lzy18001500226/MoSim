from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from Scripts.sunray.rviz_qgc_display_phase1 import (
    ADAPTER_SCHEMA,
    MANUAL_TEST_SCHEMA,
    build_manual_test_packet,
    build_phase1_acceptance,
)


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1.json"


def _metrics() -> dict:
    return {
        "status": "passed",
        "run_terminal_status": "interactive_passed",
        "blockers": [],
        "forwarded_goal_count": 1,
        "counts": {"polytraj": 2, "planner_position_cmd": 4},
        "interactive_goal_handoffs": [{"goal_seq": 1}],
        "interactive_final_hover": {"reached": True},
    }


def _adapter() -> dict:
    return {
        "schema": ADAPTER_SCHEMA,
        "nav_goal_topic": "/move_base_simple/goal",
        "output_goal_topic": "/goal_with_id",
        "nav_goal_count": 1,
        "published_goal_count": 1,
        "last_goal": {"source": "nav_goal", "x": 3.0, "y": 4.0, "z": 1.0},
    }


def _telemetry(run_id: str) -> dict:
    return {
        "run_id": run_id,
        "map_state": {
            "run_id": run_id,
            "map": {"coordinate_contract_status": "verified"},
            "map_data_status": {"state": "accepted"},
            "task_paths": {
                "expected": {"status": "available", "points": [{}, {}]},
                "future": {"status": "available", "points": [{}, {}]},
            },
            "actual_tracks": {"uav1": {"status": "available", "points": [{}, {}]}},
        },
    }


def test_phase1_automated_evidence_requires_a_recorded_rviz_goal_and_manual_qgc_observation() -> None:
    result = build_phase1_acceptance(
        run_id="rviz-qgc-phase1-test",
        metrics=_metrics(),
        adapter=_adapter(),
        telemetry=_telemetry("rviz-qgc-phase1-test"),
    )

    assert result["status"] == "automated_evidence_ready"
    assert result["blockers"] == []
    assert result["manual_observation"] == {
        "required": True,
        "status": "pending",
        "surface": "QGC",
        "requirement": "A human must observe the same run's future path and actual track in QGC.",
    }


def test_phase1_rejects_a_run_without_an_rviz_nav_goal() -> None:
    adapter = _adapter()
    adapter["nav_goal_count"] = 0

    result = build_phase1_acceptance(
        run_id="rviz-qgc-phase1-test",
        metrics=_metrics(),
        adapter=adapter,
        telemetry=_telemetry("rviz-qgc-phase1-test"),
    )

    assert result["status"] == "blocked"
    assert "rviz_nav_goal_missing" in result["blockers"]


def test_manual_packet_keeps_qgc_plan_goal_out_of_phase1() -> None:
    packet = build_manual_test_packet(
        run_id="rviz-qgc-phase1-test",
        profile_id="px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1",
        runtime_profile_id="sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1",
        rviz_config="Config/rviz/sunray_ros1_goal4_diff_pointcloud_review.rviz",
        result_directory="Results/sunray_ros1/rviz-qgc-phase1-test",
        operator_run_directory="Results/runs/rviz-qgc-phase1-test",
    )

    assert packet["schema"] == MANUAL_TEST_SCHEMA
    assert packet["status"] == "awaiting_rviz_goal"
    assert packet["entrypoints"]["rviz_tool"] == "2D Nav Goal"
    assert "Do not select QGC Plan Goal in Phase 1." in packet["must_not_do"]


def test_phase1_profile_passes_static_contract_validation() -> None:
    completed = subprocess.run(
        [sys.executable, "Scripts/quality/check_experiment_profile.py", str(PROFILE)],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_phase1_wrapper_opens_the_rviz_goal_surface_and_writes_the_manual_packet() -> None:
    wrapper = (ROOT / "Scripts" / "sunray" / "run_qgc_diff_realtime_goal_gate.sh").read_text(encoding="utf-8")

    assert "rviz_qgc_display_phase1)" in wrapper
    assert "COMMAND_SCHEMA=mosim.rviz_qgc_display_phase1_command.v1" in wrapper
    assert "OPEN_RVIZ_FOR_PHASE=true" in wrapper
    assert "DIFF_OPEN_SPLIT_RVIZ_FOR_PHASE=true" in wrapper
    assert "RVIZ_CONFIG_RELATIVE=Config/rviz/sunray_ros1_goal4_diff_pointcloud_review.rviz" in wrapper
    assert "DIFF_GRID3D_RVIZ_CONFIG=\"$PROJECT_ROOT/Config/rviz/sunray_ros1_goal4_diff_grid3d_review.rviz\"" in wrapper
    assert "write_phase1_manual_test_packet" in wrapper
    assert "verify_rviz_qgc_display_phase1_acceptance" in wrapper
    assert "qgc_plan_goal=disabled_for_phase_1" in wrapper


def test_phase1_standalone_launcher_prepares_the_same_published_run_contract() -> None:
    launcher = (ROOT / "Scripts" / "sunray" / "start_factory_l2_rviz_qgc_phase1.sh").read_text(encoding="utf-8")

    assert '--profile-id "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1"' in launcher
    assert '--runtime-profile-id "sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1"' in launcher
    assert '--prepared-by "terminal_rviz_qgc_display_phase1"' in launcher
    assert "--print-run-id" in launcher
    assert "MOSIM_OPERATOR_RUN_ID" in launcher
    assert "MOSIM_OPERATOR_RUN_DIR" in launcher
    assert "MOSIM_OPERATOR_RUN_MANIFEST" in launcher
    assert 'run_qgc_diff_realtime_goal_gate.sh" rviz_qgc_display_phase1' in launcher
