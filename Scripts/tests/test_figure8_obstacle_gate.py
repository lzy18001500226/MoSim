from __future__ import annotations

import json
import math
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = ROOT / "Scripts" / "quality" / "evaluate_figure8_obstacle_gate.py"
FIGURE8_RUNNER = ROOT / "Scripts" / "gazebo" / "run_sunray150_figure8_obstacle_gate.sh"
ANIMATION_REVIEW_RUNNER = ROOT / "Scripts" / "gazebo" / "run_sunray150_figure8_animation_review.sh"
RVIZ_REVIEW_PATHS = ROOT / "Scripts" / "ros" / "publish_gazebo_review_paths.py"
CAMERA_FOLLOW = ROOT / "Scripts" / "gazebo" / "set_gazebo_camera_follow.py"
CAMERA_ORBIT = ROOT / "Scripts" / "gazebo" / "orbit_gazebo_camera_follow.py"
GAZEBO_GUI_CONFIG = ROOT / "Config" / "gazebo" / "gui" / "sunray150_visual_review_gui.config"


def tmp_result_dir() -> Path:
    path = ROOT / "Results" / "tmp" / "test_figure8_obstacle_gate" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_fixture(result_dir: Path, *, add_tail: bool = False) -> dict[str, Path]:
    reference_report = result_dir / "figure8_position_command.json"
    reference_trace = result_dir / "figure8_position_command.trace.jsonl"
    tracker_report = result_dir / "figure8_setpoint_tracker.json"
    tracker_trace = result_dir / "figure8_setpoint_tracker.trace.jsonl"
    adapter_trace = result_dir / "controller_output_adapter_node.trace.jsonl"
    truth_pose = result_dir / "gazebo_truth_pose.jsonl"
    truth_summary = result_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    output = result_dir / "FIGURE8_STATIC_OBSTACLE_GATE.json"

    reference_report.write_text(
        json.dumps({"status": "passed", "gate_passed": True}, ensure_ascii=False),
        encoding="utf-8",
    )
    tracker_report.write_text(
        json.dumps({"status": "completed", "counts": {"published": 80}}, ensure_ascii=False),
        encoding="utf-8",
    )
    ref_rows = []
    tracker_rows = []
    adapter_rows = []
    truth_rows = []
    for index in range(120):
        t = index * 0.1
        row = {
            "schema": "mosim.figure8_position_command_sample.v1",
            "elapsed_s": t,
            "position_m": [0.5, 0.5, 1.2],
        }
        ref_rows.append(row)
        truth_rows.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": index,
                "time": t + 10.0,
                "time_source": "header_stamp",
                "position_m": [0.5, 0.5, 1.2],
                "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
        )
        if index < 80:
            tracker_rows.append(
                {
                    "schema": "mosim.gazebo_truth_planner_setpoint_tracker_sample.v1",
                    "sequence": index + 1,
                    "truth_time_s": t + 10.0,
                    "position_m": [0.5, 0.5, 1.2],
                    "reference_xy_error_m": 0.0,
                    "z_error_m": 0.0,
                    "control_phase": "xy_track",
                    "target_position_m": [0.5, 0.5, 1.2],
                    "command": [0.055, 0.055, 0.055, 0.055],
                }
            )
            adapter_rows.append(
                {
                    "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
                    "status": "published",
                    "input_sequence": index + 1,
                }
            )

    if add_tail:
        for index in range(20):
            truth_rows.append(
                {
                    "schema": "mosim.gazebo_pose_truth_sample.v1",
                    "seq": 120 + index,
                    "time": 22.0 + index * 0.1,
                    "time_source": "header_stamp",
                    "position_m": [8.0, 8.0, 0.05],
                    "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
                }
            )

    reference_trace.write_text("\n".join(json.dumps(row) for row in ref_rows) + "\n", encoding="utf-8")
    tracker_trace.write_text("\n".join(json.dumps(row) for row in tracker_rows) + "\n", encoding="utf-8")
    adapter_trace.write_text("\n".join(json.dumps(row) for row in adapter_rows) + "\n", encoding="utf-8")
    truth_pose.write_text("\n".join(json.dumps(row) for row in truth_rows) + "\n", encoding="utf-8")
    truth_summary.write_text(
        json.dumps({"status": "recorded", "count": len(truth_rows)}, ensure_ascii=False),
        encoding="utf-8",
    )
    return {
        "reference_report": reference_report,
        "reference_trace": reference_trace,
        "tracker_report": tracker_report,
        "tracker_trace": tracker_trace,
        "adapter_trace": adapter_trace,
        "truth_pose": truth_pose,
        "truth_summary": truth_summary,
        "output": output,
    }


def figure8_xy(t: float, *, x_amp: float = 0.6, y_amp: float = 0.6, y_offset: float = 0.8, z: float = 1.0) -> list[float]:
    phase = 2.0 * math.pi * t / 20.0
    s = math.sin(phase)
    c = math.cos(phase)
    return [x_amp * s, y_offset + y_amp * s * c, z]


def write_shape_fixture(
    result_dir: Path,
    *,
    collapsed_truth: bool = False,
    omit_landing_phase: bool = False,
    truth_final_altitude: float = 0.05,
    figure8_truth_x_bias_m: float = 0.0,
    post_land_xy_drift_m: float = 0.0,
) -> dict[str, Path]:
    paths = write_fixture(result_dir)
    ref_rows = []
    truth_rows = []
    tracker_rows = []
    adapter_rows = []
    for index in range(600):
        t = index * 0.1
        if t < 2.0:
            phase = "pre_takeoff_hold"
            ref_position = [0.0, 0.8, 0.05]
        elif t < 8.0:
            phase = "takeoff"
            ref_position = [0.0, 0.8, 0.05 + (t - 2.0) / 6.0 * 0.95]
        elif t < 10.0:
            phase = "pre_figure8_hold"
            ref_position = [0.0, 0.8, 1.0]
        elif t < 50.0:
            phase = "figure8"
            ref_position = figure8_xy(t - 10.0)
        elif t < 52.0:
            phase = "post_figure8_hold"
            ref_position = figure8_xy(40.0)
        elif t < 58.0:
            phase = "land"
            ref_position = [0.0, 0.8, 1.0 - (t - 52.0) / 6.0 * 0.95]
        else:
            phase = "post_land_hold"
            ref_position = [0.0, 0.8, 0.05]
        if omit_landing_phase and phase in {"land", "post_land_hold"}:
            phase = "figure8"
            ref_position = figure8_xy(min(39.9, max(0.0, t - 10.0)))
        truth_position = [0.12 * math.sin(t), 0.8 + 0.08 * math.cos(t), 1.0] if collapsed_truth else list(ref_position)
        if phase == "figure8" and not collapsed_truth:
            truth_position[0] += figure8_truth_x_bias_m
        if phase in {"land", "post_land_hold"} and not collapsed_truth:
            truth_position[2] = truth_final_altitude if phase == "post_land_hold" else ref_position[2]
        if phase == "post_land_hold" and post_land_xy_drift_m > 0.0:
            drift_fraction = min(1.0, max(0.0, (t - 58.0) / 1.9))
            truth_position[0] += post_land_xy_drift_m * drift_fraction
        ref_rows.append(
            {
                "schema": "mosim.figure8_position_command_sample.v1",
                "elapsed_s": t,
                "mission_phase": phase,
                "trajectory_time_s": max(0.0, min(40.0, t - 10.0)),
                "position_m": ref_position,
            }
        )
        truth_rows.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": index,
                "time": t + 10.0,
                "time_source": "header_stamp",
                "position_m": truth_position,
                "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
        )
        if index < 600:
            tracker_rows.append(
                {
                    "schema": "mosim.gazebo_truth_planner_setpoint_tracker_sample.v1",
                    "sequence": index + 1,
                    "truth_time_s": t + 10.0,
                    "position_m": truth_position,
                    "reference_xy_error_m": math.hypot(truth_position[0] - ref_position[0], truth_position[1] - ref_position[1]),
                    "z_error_m": ref_position[2] - truth_position[2],
                    "control_phase": "xy_track" if phase == "figure8" else "takeoff_altitude_hold",
                    "target_position_m": ref_position,
                    "command": [0.055, 0.055, 0.055, 0.055],
                }
            )
            adapter_rows.append(
                {
                    "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
                    "status": "published",
                    "input_sequence": index + 1,
                }
            )

    paths["reference_report"].write_text(
        json.dumps({"status": "passed", "gate_passed": True}, ensure_ascii=False),
        encoding="utf-8",
    )
    paths["tracker_report"].write_text(
        json.dumps({"status": "completed", "counts": {"published": len(tracker_rows)}}, ensure_ascii=False),
        encoding="utf-8",
    )
    paths["reference_trace"].write_text("\n".join(json.dumps(row) for row in ref_rows) + "\n", encoding="utf-8")
    paths["tracker_trace"].write_text("\n".join(json.dumps(row) for row in tracker_rows) + "\n", encoding="utf-8")
    paths["adapter_trace"].write_text("\n".join(json.dumps(row) for row in adapter_rows) + "\n", encoding="utf-8")
    paths["truth_pose"].write_text("\n".join(json.dumps(row) for row in truth_rows) + "\n", encoding="utf-8")
    paths["truth_summary"].write_text(
        json.dumps({"status": "recorded", "count": len(truth_rows)}, ensure_ascii=False),
        encoding="utf-8",
    )
    return paths


def run_evaluator(paths: dict[str, Path]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--reference-report-json",
            str(paths["reference_report"]),
            "--reference-trace-jsonl",
            str(paths["reference_trace"]),
            "--tracker-report-json",
            str(paths["tracker_report"]),
            "--tracker-trace-jsonl",
            str(paths["tracker_trace"]),
            "--adapter-trace-jsonl",
            str(paths["adapter_trace"]),
            "--truth-pose-jsonl",
            str(paths["truth_pose"]),
            "--truth-summary-json",
            str(paths["truth_summary"]),
            "--output-json",
            str(paths["output"]),
            "--obstacle=3.0,3.0,0.35",
            "--min-reference-samples",
            "100",
            "--min-truth-samples",
            "70",
            "--min-tracker-samples",
            "20",
            "--min-xy-track-samples",
            "20",
            "--min-adapter-samples",
            "20",
            "--min-duration-s",
            "50.0",
            "--max-xy-rmse-m",
            "0.5",
            "--max-xy-error-m",
            "1.0",
            "--max-z-error-m",
            "0.5",
            "--max-xy-track-rmse-m",
            "0.12",
            "--max-xy-track-error-m",
            "0.25",
            "--min-figure8-phase-samples",
            "100",
            "--max-figure8-phase-xy-rmse-m",
            "0.20",
            "--max-figure8-phase-xy-error-m",
            "0.45",
            "--max-figure8-phase-z-error-m",
            "0.55",
            "--min-reference-obstacle-clearance-m",
            "0.35",
            "--min-truth-obstacle-clearance-m",
            "0.0",
            "--min-truth-span-x-m",
            "0.9",
            "--min-truth-span-y-m",
            "0.45",
            "--min-truth-path-length-ratio",
            "0.8",
            "--min-lobe-fraction",
            "0.18",
            "--min-center-crossings-x",
            "2",
            "--min-figure8-trajectory-time-span-s",
            "35.0",
            "--center-revisit-radius-m",
            "0.02",
            "--min-center-revisit-entries",
            "2",
            "--max-final-altitude-m",
            "0.20",
            "--max-landing-window-altitude-m",
            "0.25",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_figure8_eval_rejects_stationary_control_window_fixture() -> None:
    paths = write_fixture(tmp_result_dir())
    completed = run_evaluator(paths)
    assert completed.returncode != 0
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert any("truth_span_x_below_min" in item for item in report["blockers"])


def test_figure8_eval_ignores_post_tracker_tail() -> None:
    paths = write_shape_fixture(tmp_result_dir())
    with paths["truth_pose"].open("a", encoding="utf-8") as handle:
        for index in range(20):
            row = {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": 580 + index,
                "time": 70.0 + index * 0.1,
                "time_source": "header_stamp",
                "position_m": [8.0, 8.0, 0.05],
                "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
            handle.write(json.dumps(row) + "\n")
    completed = run_evaluator(paths)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    window = report["truth_recording"]["tracker_window_policy"]
    assert window["tracker_window_policy"] == "truth_samples_cropped_to_tracker_truth_time_window"
    assert window["truth_samples_after_tracker_crop"] < window["truth_samples_before_tracker_crop"]


def test_figure8_shape_gate_accepts_full_shape_fixture() -> None:
    paths = write_shape_fixture(tmp_result_dir())
    completed = run_evaluator(paths)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["figure8_shape"]["truth"]["center_crossings_x"] >= 2


def test_figure8_shape_gate_rejects_collapsed_truth_fixture() -> None:
    paths = write_shape_fixture(tmp_result_dir(), collapsed_truth=True)
    completed = run_evaluator(paths)
    assert completed.returncode != 0
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert any("truth_span_x_below_min" in item for item in report["blockers"])


def test_figure8_phase_gate_rejects_biased_but_full_shape_fixture() -> None:
    paths = write_shape_fixture(tmp_result_dir(), figure8_truth_x_bias_m=0.35)
    completed = run_evaluator(paths)
    assert completed.returncode != 0
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert report["tracking"]["figure8_phase"]["rmse_xy_m"] >= 0.20
    assert any("figure8_phase_xy_rmse_above_max" in item for item in report["blockers"])


def test_figure8_gate_rejects_missing_landing_phase_fixture() -> None:
    paths = write_shape_fixture(tmp_result_dir(), omit_landing_phase=True)
    completed = run_evaluator(paths)
    assert completed.returncode != 0
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert any("reference_phase_land_samples_below_min" in item for item in report["blockers"])


def test_figure8_gate_rejects_truth_that_does_not_land() -> None:
    paths = write_shape_fixture(tmp_result_dir(), truth_final_altitude=1.0)
    completed = run_evaluator(paths)
    assert completed.returncode != 0
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert any("truth_final_altitude_above_max" in item for item in report["blockers"])


def test_figure8_gate_rejects_post_landing_xy_sliding() -> None:
    paths = write_shape_fixture(tmp_result_dir(), post_land_xy_drift_m=0.12)
    completed = run_evaluator(paths)
    assert completed.returncode != 0
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert any("truth_landing_window_xy_displacement_above_max" in item for item in report["blockers"])


def test_rviz_review_paths_contract_filters_named_gazebo_entity() -> None:
    source = RVIZ_REVIEW_PATHS.read_text(encoding="utf-8")
    assert "--gz-truth-topic" in source
    assert "--model-name" in source
    assert "parse_truth_samples" in source
    assert "Actual path is filtered by Gazebo entity name" in source
    assert "import PoseArray" not in source


def test_figure8_runner_does_not_bridge_unnamed_posearray_for_rviz_paths() -> None:
    source = FIGURE8_RUNNER.read_text(encoding="utf-8")
    assert '--gz-truth-topic "${GAZEBO_TRUTH_TOPIC}"' in source
    assert '--model-name "${GAZEBO_TRUTH_MODEL_NAME}"' in source
    assert '--truth-pose-topic "${ROS_GAZEBO_TRUTH_POSE_TOPIC}"' not in source

    bridge_line = '${ROS_GAZEBO_TRUTH_POSE_TOPIC}@geometry_msgs/msg/PoseArray@gz.msgs.Pose_V'
    assert (
        'if [[ "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1" ]]; then\n'
        f'  bridge_args+=("{bridge_line}")'
    ) not in source


def test_gazebo_review_camera_defaults_are_left_rear_up_body_frame() -> None:
    runner = FIGURE8_RUNNER.read_text(encoding="utf-8")
    animation_runner = ANIMATION_REVIEW_RUNNER.read_text(encoding="utf-8")
    gui_config = GAZEBO_GUI_CONFIG.read_text(encoding="utf-8")
    camera_follow = CAMERA_FOLLOW.read_text(encoding="utf-8")

    for source in (runner, animation_runner):
        assert 'GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M:--0.233}"' in source
        assert 'GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M:--0.933}"' in source
        assert 'GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M:-0.467}"' in source
    assert "<camera_pose>-0.667 -1.667 1.34 0 0.42 1.33</camera_pose>" in gui_config
    assert "<follow_offset>-0.233 -0.933 0.467</follow_offset>" in gui_config
    assert "KeyPublisher" in gui_config
    assert "back:left:up = 4:1:2" in camera_follow
    assert "--allow-service-fallback" in runner


def test_gazebo_review_camera_orbit_is_gui_only_and_preserves_radius_contract() -> None:
    source = CAMERA_ORBIT.read_text(encoding="utf-8")
    runner = FIGURE8_RUNNER.read_text(encoding="utf-8")

    assert "--left-key" in source
    assert "16777234" in source
    assert "16777235" in source
    assert "16777236" in source
    assert "16777237" in source
    assert "radius_preserved" in source
    assert "/gui/follow/offset" in source
    assert "never publishes UAV control" in source
    assert "topic\", \"-e\", \"-t\", args.keyboard_topic" in source
    assert "topic\", \"-t\"" not in source
    assert "/cmd_vel" not in source
    assert "/mosim/planner" not in source
    assert "/model/" not in source
    assert "/actuator" not in source
    assert "GAZEBO_GUI_CAMERA_ORBIT" in runner
    assert "gazebo_camera_orbit_request.json" in runner
