from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = ROOT / "Scripts" / "quality" / "evaluate_gazebo_plant_response.py"


def tmp_result_dir() -> Path:
    path = ROOT / "Results" / "tmp" / "test_gazebo_plant_response_eval" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_plant_response_eval_drops_synthetic_paused_prefix() -> None:
    result_dir = tmp_result_dir()
    truth = result_dir / "gazebo_truth_pose.jsonl"
    summary = result_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    controller = result_dir / "controller_output_adapter_node.json"
    fixture = result_dir / "controller_output_fixture.json"
    output = result_dir / "GAZEBO_PLANT_RESPONSE_EVAL.json"

    rows = []
    for index in range(3):
        rows.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": index,
                "time": index * 1e-6,
                "time_source": "synthetic_order",
                "position_m": [0.0, 0.0, 1.2],
            }
        )
    for index in range(30):
        rows.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": 3 + index,
                "time": 10.0 + index * 0.1,
                "time_source": "header_stamp",
                "position_m": [0.0, 0.0, 1.2 + index * 0.01],
            }
        )
    truth.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    summary.write_text(json.dumps({"status": "recorded", "count": len(rows), "model_name": "sunray150", "frame_id": "world"}), encoding="utf-8")
    controller.write_text(json.dumps({"status": "published", "velocity": [440.0] * 4, "input_command": [0.055] * 4}), encoding="utf-8")
    fixture.write_text(json.dumps({"status": "published", "command": [0.055] * 4}), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--truth-pose-jsonl",
            str(truth),
            "--truth-summary-json",
            str(summary),
            "--controller-report-json",
            str(controller),
            "--fixture-report-json",
            str(fixture),
            "--output-json",
            str(output),
            "--min-samples",
            "20",
            "--min-duration-s",
            "2.0",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    truth_recording = report["truth_recording"]
    assert truth_recording["raw_valid_sample_count"] == 33
    assert truth_recording["valid_sample_count"] == 30
    assert truth_recording["sample_policy"]["synthetic_prefix_dropped"] == 3
    assert truth_recording["duration_s"] == 2.9
    assert report["plant_response"]["max_abs_z_delta_m"] > 0.05
