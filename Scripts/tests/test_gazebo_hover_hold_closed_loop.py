from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = ROOT / "Scripts" / "quality" / "evaluate_gazebo_hover_hold_closed_loop.py"


def tmp_result_dir() -> Path:
    path = ROOT / "Results" / "tmp" / "test_gazebo_hover_hold_closed_loop" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_hover_hold_fixture(result_dir: Path, *, final_z: float = 1.2) -> dict[str, Path]:
    controller_report = result_dir / "hover_hold_controller.json"
    controller_trace = result_dir / "hover_hold_controller_trace.jsonl"
    adapter_trace = result_dir / "controller_output_adapter_node.trace.jsonl"
    truth_pose = result_dir / "gazebo_truth_pose.jsonl"
    truth_summary = result_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    output = result_dir / "GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json"

    controller_report.write_text(
        json.dumps(
            {
                "schema": "mosim.gazebo_truth_hover_hold_controller.v1",
                "status": "completed",
                "counts": {"published": 30},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    controller_rows = []
    for index in range(30):
        command = 0.05484 + 0.000001 * (index % 4)
        controller_rows.append(
            {
                "schema": "mosim.gazebo_truth_hover_hold_controller_sample.v1",
                "sequence": index + 1,
                "truth_time_s": 10.0 + index * 0.4,
                "truth_time_source": "header_stamp",
                "command": [command, command, command, command],
            }
        )
    controller_trace.write_text("\n".join(json.dumps(row) for row in controller_rows) + "\n", encoding="utf-8")

    adapter_rows = [
        {
            "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
            "status": "published",
            "input_sequence": index + 1,
        }
        for index in range(30)
    ]
    adapter_trace.write_text("\n".join(json.dumps(row) for row in adapter_rows) + "\n", encoding="utf-8")

    truth_rows = []
    for index in range(5):
        truth_rows.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": index,
                "time": index * 1e-6,
                "time_source": "synthetic_order",
                "position_m": [0.0, 0.0, 1.2],
                "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
        )
    for index in range(120):
        fraction = index / 119.0
        z = 1.2 + (final_z - 1.2) * fraction
        truth_rows.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": 5 + index,
                "time": 10.0 + index * 0.1,
                "time_source": "header_stamp",
                "position_m": [0.0, 0.0, z],
                "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
        )
    truth_pose.write_text("\n".join(json.dumps(row) for row in truth_rows) + "\n", encoding="utf-8")
    truth_summary.write_text(
        json.dumps({"status": "recorded", "count": len(truth_rows), "model_name": "sunray150"}),
        encoding="utf-8",
    )

    return {
        "controller_report": controller_report,
        "controller_trace": controller_trace,
        "adapter_trace": adapter_trace,
        "truth_pose": truth_pose,
        "truth_summary": truth_summary,
        "output": output,
    }


def write_hover_hold_fixture_with_post_controller_fall(result_dir: Path) -> dict[str, Path]:
    paths = write_hover_hold_fixture(result_dir, final_z=1.2)
    truth_pose = paths["truth_pose"]
    rows = [json.loads(line) for line in truth_pose.read_text(encoding="utf-8").splitlines() if line.strip()]
    last_seq = max(int(row["seq"]) for row in rows)
    rows.extend(
        {
            "schema": "mosim.gazebo_pose_truth_sample.v1",
            "seq": last_seq + index + 1,
            "time": 22.1 + index * 0.1,
            "time_source": "header_stamp",
            "position_m": [0.0, 0.0, max(0.05, 1.2 - 0.2 * index)],
            "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
        }
        for index in range(8)
    )
    truth_pose.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    paths["truth_summary"].write_text(
        json.dumps({"status": "recorded", "count": len(rows), "model_name": "sunray150"}),
        encoding="utf-8",
    )
    return paths


def run_evaluator(paths: dict[str, Path]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--controller-report-json",
            str(paths["controller_report"]),
            "--controller-trace-jsonl",
            str(paths["controller_trace"]),
            "--adapter-trace-jsonl",
            str(paths["adapter_trace"]),
            "--truth-pose-jsonl",
            str(paths["truth_pose"]),
            "--truth-summary-json",
            str(paths["truth_summary"]),
            "--output-json",
            str(paths["output"]),
            "--target-altitude-m",
            "1.2",
            "--command-min",
            "0.04500",
            "--command-max",
            "0.06500",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_hover_hold_closed_loop_eval_accepts_bounded_fixture() -> None:
    paths = write_hover_hold_fixture(tmp_result_dir())
    completed = run_evaluator(paths)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    assert report["counts"]["controller_samples"] == 30
    assert report["counts"]["adapter_published"] == 30
    assert report["counts"]["raw_truth_samples"] == 125
    assert report["counts"]["truth_samples"] == 117
    assert report["truth_recording"]["sample_policy"]["synthetic_prefix_dropped"] == 5
    assert report["altitude"]["final_abs_z_error_m"] == 0.0
    assert "multi-UAV readiness" in " ".join(report["claim_boundary"])


def test_hover_hold_closed_loop_eval_blocks_large_altitude_error() -> None:
    paths = write_hover_hold_fixture(tmp_result_dir(), final_z=2.1)
    completed = run_evaluator(paths)
    assert completed.returncode == 1
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is False
    assert any(item.startswith("final_abs_z_error_above_max") for item in report["blockers"])


def test_hover_hold_closed_loop_eval_ignores_post_controller_tail() -> None:
    paths = write_hover_hold_fixture_with_post_controller_fall(tmp_result_dir())
    completed = run_evaluator(paths)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(paths["output"].read_text(encoding="utf-8"))
    assert report["gate_passed"] is True
    window = report["truth_recording"]["controller_window_policy"]
    assert window["controller_window_policy"] == "truth_samples_cropped_to_controller_header_stamp_window"
    assert window["truth_samples_after_controller_crop"] < window["truth_samples_before_controller_crop"]
    assert report["altitude"]["final_abs_z_error_m"] == 0.0
