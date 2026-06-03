#!/usr/bin/env python3
"""Regression checks for the real UAV stack minimum-loop gate."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "check_realstack_miniloop_gate.py"
    spec = importlib.util.spec_from_file_location("check_realstack_miniloop_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_realstack_miniloop_gate"] = module
    spec.loader.exec_module(module)
    return module


def args_for(module, **overrides):
    values = {
        "mworks_raw_csv": module.DEFAULT_MWORKS_RAW,
        "livox_frames": module.DEFAULT_LIVOX_FRAMES,
        "fastlio_contract": module.DEFAULT_FASTLIO_CONTRACT,
        "runtime_recording": module.DEFAULT_RUNTIME_RECORDING,
        "runtime_evaluation": module.DEFAULT_RUNTIME_EVALUATION,
        "rviz_pointcloud": module.DEFAULT_RVIZ_POINTCLOUD,
        "rviz_map": module.DEFAULT_RVIZ_MAP,
        "sample_frames": 5,
        "truth_rate_hz": 20.0,
        "imu_rate_hz": 200.0,
        "lidar_rate_hz": 10.0,
        "controller_rate_hz": 20.0,
        "rate_tolerance_hz": 0.1,
        "max_continuous_step_m": 0.25,
        "min_lidar_points_per_frame": 15000,
    }
    values.update(overrides)
    return type("Args", (), values)()


def test_gate_defaults_to_formal_fastlio_runtime_ready() -> None:
    module = load_module()
    report = module.evaluate(args_for(module))
    if report["schema"] != "mosim.realstack_miniloop_gate.v1":
        raise AssertionError(report)
    if report["status"] != "ready_for_manual_rviz_ue_review":
        raise AssertionError(report)
    if report["mworks_state"]["nominal_hz"] != 20.0:
        raise AssertionError(report["mworks_state"])
    if report["lidar"]["points_per_frame_min"] < 15000:
        raise AssertionError(report["lidar"])
    if report["fastlio_input_contract_status"] != "claimable_input_ready":
        raise AssertionError(report["fastlio_input_contract_status"])
    counts = report["fastlio_runtime_counts"]
    for key in ("odometry", "path", "registered_cloud"):
        if int(counts.get(key, 0)) <= 0:
            raise AssertionError(counts)
    evaluation = report["fastlio_runtime_evaluation"]
    if evaluation["status"] not in {"pass", "passed", "ok"}:
        raise AssertionError(evaluation)
    if not report["rviz2"]["pointcloud"]["uses_mosim_lidar_points"]:
        raise AssertionError(report["rviz2"]["pointcloud"])
    if not report["rviz2"]["pointcloud"]["uses_fastlio_odometry"]:
        raise AssertionError(report["rviz2"]["pointcloud"])
    if not report["rviz2"]["map"]["uses_3d_local_voxels"]:
        raise AssertionError(report["rviz2"]["map"])


def test_gate_passes_with_fixture_runtime_and_claimable_contract() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "realstack_miniloop_gate_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        contract_path = temp_root / "fastlio_input_contract.json"
        runtime_path = temp_root / "FASTLIO_RUNTIME_RECORDING.json"
        evaluation_path = temp_root / "FASTLIO_RUNTIME_EVALUATION.json"
        contract_path.write_text(
            json.dumps({"status": "claimable_input_ready"}, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        runtime_path.write_text(
            json.dumps(
                {
                    "counts": {
                        "odometry": 12,
                        "path": 12,
                        "registered_cloud": 12,
                    }
                },
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        evaluation_path.write_text(
            json.dumps(
                {
                    "status": "passed",
                    "metrics": {
                        "position_rmse_m": 0.1,
                        "max_position_error_m": 0.2,
                    },
                },
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        report = module.evaluate(
            args_for(
                module,
                fastlio_contract=contract_path,
                runtime_recording=runtime_path,
                runtime_evaluation=evaluation_path,
            )
        )
        if report["status"] != "ready_for_manual_rviz_ue_review":
            raise AssertionError(report)
        md_path = temp_root / "REALSTACK_GATE.md"
        module.write_markdown(md_path, report)
        text = md_path.read_text(encoding="utf-8")
        if "ready_for_manual_rviz_ue_review" not in text:
            raise AssertionError(text)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_gate_blocks_failed_truth_evaluation() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "realstack_miniloop_gate_failed_eval_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        contract_path = temp_root / "fastlio_input_contract.json"
        runtime_path = temp_root / "FASTLIO_RUNTIME_RECORDING.json"
        evaluation_path = temp_root / "FASTLIO_RUNTIME_EVALUATION.json"
        contract_path.write_text(json.dumps({"status": "claimable_input_ready"}) + "\n", encoding="utf-8")
        runtime_path.write_text(
            json.dumps({"counts": {"odometry": 12, "path": 12, "registered_cloud": 12}}) + "\n",
            encoding="utf-8",
        )
        evaluation_path.write_text(
            json.dumps(
                {
                    "status": "failed_error_threshold",
                    "metrics": {"position_rmse_m": 9.5, "max_position_error_m": 17.9},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report = module.evaluate(
            args_for(
                module,
                fastlio_contract=contract_path,
                runtime_recording=runtime_path,
                runtime_evaluation=evaluation_path,
            )
        )
        if report["status"] != "blocked_before_manual_review":
            raise AssertionError(report)
        details = "\n".join(finding["detail"] for finding in report["findings"])
        if "failed_error_threshold" not in details:
            raise AssertionError(report["findings"])
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def test_gate_blocks_zero_runtime_outputs() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "realstack_miniloop_gate_zero_runtime_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        contract_path = temp_root / "fastlio_input_contract.json"
        runtime_path = temp_root / "FASTLIO_RUNTIME_RECORDING.json"
        evaluation_path = temp_root / "FASTLIO_RUNTIME_EVALUATION.json"
        contract_path.write_text(json.dumps({"status": "claimable_input_ready"}) + "\n", encoding="utf-8")
        runtime_path.write_text(
            json.dumps({"counts": {"odometry": 0, "path": 0, "registered_cloud": 0}}) + "\n",
            encoding="utf-8",
        )
        evaluation_path.write_text(
            json.dumps({"status": "pass", "metrics": {"position_rmse_m": 0.1, "max_position_error_m": 0.2}})
            + "\n",
            encoding="utf-8",
        )
        report = module.evaluate(
            args_for(
                module,
                fastlio_contract=contract_path,
                runtime_recording=runtime_path,
                runtime_evaluation=evaluation_path,
            )
        )
        if report["status"] != "blocked_before_manual_review":
            raise AssertionError(report)
        details = "\n".join(finding["detail"] for finding in report["findings"])
        for phrase in (
            "/odometry recorded zero samples",
            "/path recorded zero samples",
            "/cloud_registered recorded zero samples",
        ):
            if phrase not in details:
                raise AssertionError((phrase, details))
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_gate_defaults_to_formal_fastlio_runtime_ready()
    test_gate_passes_with_fixture_runtime_and_claimable_contract()
    test_gate_blocks_failed_truth_evaluation()
    test_gate_blocks_zero_runtime_outputs()
    print("[OK] real UAV stack minimum-loop gate regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
