#!/usr/bin/env python3
"""Verify PX4 EKF external-vision fusion from a captured ULog."""

import argparse
import json
import math
import sys
from pathlib import Path


REQUIRED_AID_SOURCES = (
    "estimator_aid_src_ev_pos",
    "estimator_aid_src_ev_vel",
    "estimator_aid_src_ev_hgt",
)
REQUIRED_CONTROL_FLAGS = ("cs_ev_pos", "cs_ev_vel", "cs_ev_hgt")
RESET_COUNTERS = (
    "reset_count_vel_ne",
    "reset_count_vel_d",
    "reset_count_pos_ne",
    "reset_count_pod_d",
    "reset_count_quat",
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ulog", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--min-samples", type=int, default=20)
    parser.add_argument("--min-fused-fraction", type=float, default=0.99)
    parser.add_argument("--max-rejected-fraction", type=float, default=0.01)
    parser.add_argument("--max-fused-gap-s", type=float, default=0.50)
    parser.add_argument("--max-sample-delay-s", type=float, default=0.25)
    parser.add_argument("--reset-grace-s", type=float, default=0.50)
    return parser.parse_args()


def percentile(values, fraction):
    finite_values = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not finite_values:
        return None
    index = int(round((len(finite_values) - 1) * fraction))
    return finite_values[max(0, min(index, len(finite_values) - 1))]


def transitions(timestamps, values, origin_us):
    output = []
    previous = None
    for timestamp, value in zip(timestamps, values):
        current = int(value)
        if current != previous:
            output.append({
                "time_s": (int(timestamp) - origin_us) / 1e6,
                "value": current,
            })
            previous = current
    return output


def main():
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    blockers = []
    result = {
        "schema": "mosim.px4_ev_fusion_ulog_gate.v1",
        "status": "blocked",
        "blockers": blockers,
        "ulog": str(Path(args.ulog)),
        "thresholds": {
            "min_samples": args.min_samples,
            "min_fused_fraction": args.min_fused_fraction,
            "max_rejected_fraction": args.max_rejected_fraction,
            "max_fused_gap_s": args.max_fused_gap_s,
            "max_sample_delay_s": args.max_sample_delay_s,
            "reset_grace_s": args.reset_grace_s,
        },
    }

    project_root = Path(args.project_root)
    pyulog_root = project_root / "References" / "Log" / "pyulog"
    sys.path.insert(0, str(pyulog_root))
    try:
        from pyulog import ULog
    except Exception as exc:
        blockers.append("pyulog_import_failed")
        result["error"] = repr(exc)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 18

    ulog_path = Path(args.ulog)
    if not ulog_path.is_file() or ulog_path.stat().st_size == 0:
        blockers.append("missing_px4_ulog")
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 18

    try:
        ulog = ULog(str(ulog_path))
    except Exception as exc:
        blockers.append("px4_ulog_parse_failed")
        result["error"] = repr(exc)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 18

    datasets = {(dataset.name, dataset.multi_id): dataset.data for dataset in ulog.data_list}

    def get_dataset(name):
        data = datasets.get((name, 0))
        if data is None:
            blockers.append("missing_" + name)
        return data

    timestamp_starts = [
        int(data["timestamp"][0])
        for data in datasets.values()
        if "timestamp" in data and len(data["timestamp"])
    ]
    origin_us = min(timestamp_starts) if timestamp_starts else 0
    result["ulog_origin_us"] = origin_us
    aid_summary = {}
    first_fusion_timestamp_us = None

    for name in REQUIRED_AID_SOURCES:
        data = get_dataset(name)
        if data is None:
            continue
        timestamps = [int(value) for value in data["timestamp"]]
        fused = [int(value) for value in data["fused"]]
        rejected = [int(value) for value in data["innovation_rejected"]]
        sample_count = len(timestamps)
        fused_count = sum(fused)
        rejected_count = sum(rejected)
        fused_fraction = fused_count / sample_count if sample_count else 0.0
        rejected_fraction = rejected_count / sample_count if sample_count else 1.0
        fused_timestamps = [timestamp for timestamp, state in zip(timestamps, fused) if state]
        fused_gaps = [
            (right - left) / 1e6
            for left, right in zip(fused_timestamps, fused_timestamps[1:])
        ]
        max_fused_gap_s = max(fused_gaps) if fused_gaps else None
        test_ratios = []
        for key, values in data.items():
            if key.startswith("test_ratio"):
                test_ratios.extend(float(value) for value in values)
        if fused_timestamps:
            first = min(fused_timestamps)
            first_fusion_timestamp_us = first if first_fusion_timestamp_us is None else min(first_fusion_timestamp_us, first)

        aid_summary[name] = {
            "samples": sample_count,
            "fused_count": fused_count,
            "fused_fraction": fused_fraction,
            "innovation_rejected_count": rejected_count,
            "innovation_rejected_fraction": rejected_fraction,
            "max_fused_sample_gap_s": max_fused_gap_s,
            "test_ratio_max": max(test_ratios) if test_ratios else None,
            "test_ratio_p95": percentile(test_ratios, 0.95),
            "test_ratio_over_1_count": sum(value > 1.0 for value in test_ratios),
        }
        if sample_count < args.min_samples:
            blockers.append(name + "_insufficient_samples")
        if fused_fraction < args.min_fused_fraction:
            blockers.append(name + "_fused_fraction_below_limit")
        if rejected_fraction > args.max_rejected_fraction:
            blockers.append(name + "_rejected_fraction_exceeds_limit")
        if max_fused_gap_s is None or max_fused_gap_s > args.max_fused_gap_s:
            blockers.append(name + "_fused_gap_exceeds_limit")

    result["aid_sources"] = aid_summary

    status_flags = get_dataset("estimator_status_flags")
    control_summary = {}
    if status_flags is not None:
        timestamps = [int(value) for value in status_flags["timestamp"]]
        for key in REQUIRED_CONTROL_FLAGS:
            values = [int(value) for value in status_flags[key]]
            key_transitions = transitions(timestamps, values, origin_us)
            first_true_index = next((index for index, value in enumerate(values) if value), None)
            dropped_after_start = (
                first_true_index is not None and any(value == 0 for value in values[first_true_index + 1 :])
            )
            control_summary[key] = {
                "transitions": key_transitions,
                "became_active": first_true_index is not None,
                "dropped_after_start": dropped_after_start,
            }
            if first_true_index is None:
                blockers.append(key + "_never_active")
            elif dropped_after_start:
                blockers.append(key + "_dropped_after_start")
    result["control_flags"] = control_summary

    event_flags = get_dataset("estimator_event_flags")
    if event_flags is not None:
        vision_data_stopped_count = sum(int(value) for value in event_flags["vision_data_stopped"])
        result["vision_data_stopped_count"] = vision_data_stopped_count
        if vision_data_stopped_count:
            blockers.append("vision_data_stopped")

    estimator_status = get_dataset("estimator_status")
    reset_summary = {}
    if estimator_status is not None and first_fusion_timestamp_us is not None:
        timestamps = [int(value) for value in estimator_status["timestamp"]]
        cutoff_us = first_fusion_timestamp_us + int(args.reset_grace_s * 1e6)
        for key in RESET_COUNTERS:
            values = [int(value) for value in estimator_status[key]]
            after = [value for timestamp, value in zip(timestamps, values) if timestamp >= cutoff_us]
            delta = max(after) - min(after) if after else 0
            reset_summary[key] = {"post_fusion_delta": delta}
            if delta:
                blockers.append(key + "_changed_after_fusion")
    result["reset_counters"] = reset_summary

    visual_odometry = get_dataset("vehicle_visual_odometry")
    if visual_odometry is not None:
        delays = [
            (int(timestamp) - int(sample_timestamp)) / 1e6
            for timestamp, sample_timestamp in zip(
                visual_odometry["timestamp"], visual_odometry["timestamp_sample"]
            )
        ]
        sample_count = len(delays)
        max_delay_s = max(delays) if delays else None
        result["vehicle_visual_odometry"] = {
            "samples": sample_count,
            "timestamp_minus_sample_s": {
                "min": min(delays) if delays else None,
                "mean": sum(delays) / sample_count if delays else None,
                "p95": percentile(delays, 0.95),
                "max": max_delay_s,
            },
            "quality_values": sorted(set(int(value) for value in visual_odometry["quality"])),
        }
        if sample_count < args.min_samples:
            blockers.append("vehicle_visual_odometry_insufficient_samples")
        if max_delay_s is None or max_delay_s > args.max_sample_delay_s:
            blockers.append("vehicle_visual_odometry_sample_delay_exceeds_limit")

    result["status"] = "passed" if not blockers else "blocked"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if not blockers else 18


if __name__ == "__main__":
    raise SystemExit(main())
