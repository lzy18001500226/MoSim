from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORDER = ROOT / "Scripts" / "gazebo" / "record_gazebo_pose_truth.py"
EVALUATOR = ROOT / "Scripts" / "quality" / "evaluate_fastlio_truth_error.py"


def mosim_tmp_dir(name: str) -> Path:
    test_dir = ROOT / "Results" / "tmp" / "fastlio_truth_error_eval_tests" / name
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


def test_gazebo_pose_truth_recorder_extracts_named_model() -> None:
    test_dir = mosim_tmp_dir("gazebo_pose_truth_recorder")
    stdout = test_dir / "gazebo_truth_pose.jsonl"
    summary = test_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    sample = """
header {
  stamp {
    sec: 1
    nsec: 500000000
  }
}
pose {
  name: "sunray150"
  position {
    x: 1.0
    y: 2.0
    z: 3.0
  }
  orientation {
    w: 1
  }
}
---
"""
    completed = subprocess.run(
        [
            sys.executable,
            str(RECORDER),
            "--output-jsonl",
            str(stdout),
            "--summary-json",
            str(summary),
            "--topic",
            "/world/mosim_factory_minimal/dynamic_pose/info",
        ],
        input=sample,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    rows = [json.loads(line) for line in stdout.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["time"] == 1.5
    assert rows[0]["model_name"] == "sunray150"
    assert rows[0]["position_m"] == [1.0, 2.0, 3.0]
    report = json.loads(summary.read_text(encoding="utf-8"))
    assert report["count"] == 1


def test_gazebo_pose_truth_recorder_splits_unseparated_ign_stream() -> None:
    test_dir = mosim_tmp_dir("gazebo_pose_truth_unseparated_stream")
    stdout = test_dir / "gazebo_truth_pose.jsonl"
    summary = test_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    sample = """
header {
  stamp {
    sec: 1
    nsec: 0
  }
}
pose {
  name: "sunray150"
  position {
    x: 1.0
  }
  orientation {
    w: 1
  }
}
header {
  stamp {
    sec: 2
    nsec: 250000000
  }
}
pose {
  name: "sunray150"
  position {
    x: 2.0
  }
  orientation {
    w: 1
  }
}
"""
    completed = subprocess.run(
        [
            sys.executable,
            str(RECORDER),
            "--output-jsonl",
            str(stdout),
            "--summary-json",
            str(summary),
            "--topic",
            "/world/mosim_factory_minimal/dynamic_pose/info",
        ],
        input=sample,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    rows = [json.loads(line) for line in stdout.read_text(encoding="utf-8").splitlines()]
    assert [row["time"] for row in rows] == [1.0, 2.25]
    assert [row["position_m"][0] for row in rows] == [1.0, 2.0]
    report = json.loads(summary.read_text(encoding="utf-8"))
    assert report["count"] == 2


def test_gazebo_pose_truth_recorder_marks_missing_header_time_as_synthetic() -> None:
    test_dir = mosim_tmp_dir("gazebo_pose_truth_synthetic_time")
    stdout = test_dir / "gazebo_truth_pose.jsonl"
    summary = test_dir / "GAZEBO_TRUTH_POSE_RECORDING.json"
    sample = """
pose {
  name: "sunray150"
  position {
    z: 1.2
  }
  orientation {
    w: 1
  }
}
---
header {
  stamp {
    sec: 2
    nsec: 500000000
  }
}
pose {
  name: "sunray150"
  position {
    z: 1.1
  }
  orientation {
    w: 1
  }
}
"""
    completed = subprocess.run(
        [
            sys.executable,
            str(RECORDER),
            "--output-jsonl",
            str(stdout),
            "--summary-json",
            str(summary),
            "--topic",
            "/world/mosim_factory_minimal/dynamic_pose/info",
        ],
        input=sample,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    rows = [json.loads(line) for line in stdout.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["time_source"] == "synthetic_order"
    assert rows[1]["time_source"] == "header_stamp"
    assert rows[1]["time"] == 2.5
    report = json.loads(summary.read_text(encoding="utf-8"))
    assert report["time_sources"] == {"header_stamp": 1, "synthetic_order": 1}


def test_fastlio_truth_error_eval_passes_origin_aligned_stationary_smoke() -> None:
    test_dir = mosim_tmp_dir("fastlio_truth_error_eval")
    spark = test_dir / "fastlio_odometry.jsonl"
    truth = test_dir / "gazebo_truth_pose.jsonl"
    output = test_dir / "FASTLIO_TRUTH_ERROR_EVAL.json"
    spark_rows = []
    truth_rows = []
    for index in range(35):
        t = float(index) * 0.05
        truth_rows.append({"time": t, "frame_id": "world", "position_m": [0.0, 0.0, 0.04]})
        spark_rows.append({"time": t + 0.01, "frame_id": "map", "position_m": [1.0, -2.0, 0.54]})
    spark.write_text("\n".join(json.dumps(row) for row in spark_rows) + "\n", encoding="utf-8")
    truth.write_text("\n".join(json.dumps(row) for row in truth_rows) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(EVALUATOR),
            "--spark-odometry-jsonl",
            str(spark),
            "--truth-pose-jsonl",
            str(truth),
            "--output-json",
            str(output),
            "--max-time-delta-s",
            "0.05",
            "--min-matched-samples",
            "30",
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
    assert report["gate_passed"] is True
    assert report["alignment"]["matched_count"] == 35
    assert report["metrics"]["direct"]["rmse_3d_m"] > 0.0
    assert report["metrics"]["origin_aligned"]["rmse_3d_m"] == 0.0
    assert "closed_loop" in " ".join(report["claim_boundary"])
