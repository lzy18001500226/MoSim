#!/usr/bin/env python3
"""Static validator for future ROS2 B1 live evidence bundles.

This checker is file-only. It does not import ROS libraries, source ROS setup,
execute ros2, start RViz2/FAST-LIO, or inspect a live graph. It validates
whether a future bounded live bundle contains enough same-run evidence to keep
FAST-LIO output review, TF grounding, and controller handoff claims separate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


FORBIDDEN_TOPICS = {
    "/position_cmd",
    "/mosim/planner/position_cmd",
    "/mosim/planner/setpoint",
    "/mosim/planner/setpoint_adapter_status",
    "/planning/bspline",
}

FORBIDDEN_CLAIM_MARKERS = {
    "true_sensor_capture",
    "fast_lio_success",
    "fastlio_success",
    "tf_rviz_readiness",
    "final_tf_rviz_readiness",
    "planner_ready",
    "controller_performance",
    "runtime_ack",
    "mission_success",
    "closed_loop",
    "localization_quality",
    "local_map_quality",
}

FAKE_ROUTE_MARKERS = {
    "fake_point_cloud",
    "fake_pointcloud",
    "fake_map",
    "fake_odom",
    "fake_tf",
    "fake_transform",
    "keyboard_pose",
    "ue_truth_shortcut",
    "arbitrary_camera_init_to_map",
    "arbitrary_camera_init_to_world",
    "header_frame_rename",
}


def load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def get_path(data: dict[str, Any], dotted: str, default: Any = None) -> Any:
    value: Any = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def rate_near(value: Any, target: float, tolerance_fraction: float) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return abs(numeric - target) <= abs(target) * tolerance_fraction


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def claims_text(bundle: dict[str, Any]) -> str:
    claims = as_list(bundle.get("claims")) + as_list(bundle.get("claim_boundary"))
    classifications = [
        bundle.get("classification"),
        get_path(bundle, "result.classification"),
        get_path(bundle, "status.classification"),
        get_path(bundle, "controller_handoff.status"),
    ]
    return json.dumps(claims + classifications, ensure_ascii=False).lower()


def validate_no_forbidden_claims(bundle: dict[str, Any]) -> list[str]:
    text = claims_text(bundle)
    return [
        f"forbidden readiness or quality claim marker present: {marker}"
        for marker in sorted(FORBIDDEN_CLAIM_MARKERS)
        if marker in text
    ]


def validate_no_fake_routes(bundle: dict[str, Any]) -> list[str]:
    text = json.dumps(
        [
            bundle.get("fake_data_routes"),
            bundle.get("forbidden_routes_observed"),
            bundle.get("route_flags"),
            bundle.get("claims"),
        ],
        ensure_ascii=False,
    ).lower()
    if "reject" in text or "rejected" in text:
        return []
    return [
        f"fake-data route is present without rejection: {marker}"
        for marker in sorted(FAKE_ROUTE_MARKERS)
        if marker in text
    ]


def validate_probe_budget(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    count = get_path(bundle, "probe_budget.live_probe_count_after")
    limit = get_path(bundle, "probe_budget.live_probe_limit", 1)
    require(errors, count is not None, "probe_budget.live_probe_count_after is required")
    require(errors, limit == 1, "probe_budget.live_probe_limit must be 1")
    if isinstance(count, int):
        require(errors, count <= 1, "live_probe_count_after must be <= 1")
    else:
        errors.append("live_probe_count_after must be an integer")
    require(errors, get_path(bundle, "probe_budget.rerun_attempted") is False, "probe_budget.rerun_attempted must be false")
    return errors


def validate_lidar(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lidar = get_path(bundle, "source_topics.lidar", {})
    require(errors, lidar.get("topic") == "/mosim/livox/lidar", "LiDAR topic must be /mosim/livox/lidar")
    require(errors, lidar.get("frame_id") == "base/mid360_link", "LiDAR frame must be base/mid360_link")
    require(errors, int(lidar.get("count", 0) or 0) > 0, "LiDAR count must be nonzero")
    require(errors, lidar.get("monotonic") is True, "LiDAR stamps must be monotonic")
    require(errors, int(lidar.get("regression_count", 1) or 0) == 0, "LiDAR regression_count must be zero")
    require(errors, rate_near(lidar.get("rate_hz"), 20.0, 0.10), "LiDAR rate_hz must be near replay-time 20 Hz")
    classification = str(lidar.get("classification", "")).lower()
    require(errors, "true_sensor_capture" not in classification, "LiDAR classification must not claim true sensor capture")
    require(errors, "replay" in classification or "adapt" in classification, "LiDAR classification must preserve replay/adapt provenance")
    return errors


def validate_imu(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    imu = get_path(bundle, "source_topics.imu", {})
    require(errors, imu.get("topic") == "/mosim/forward/imu", "IMU topic must be /mosim/forward/imu")
    require(errors, imu.get("frame_id") == "base/forward_imu_optical_frame", "IMU frame must be base/forward_imu_optical_frame")
    require(errors, int(imu.get("count", 0) or 0) > 0, "IMU count must be nonzero")
    require(errors, imu.get("monotonic") is True, "IMU stamps must be monotonic")
    require(errors, int(imu.get("regression_count", 1) or 0) == 0, "IMU regression_count must be zero")
    require(errors, rate_near(imu.get("rate_hz"), 200.0, 0.05), "IMU rate_hz must be near 200 Hz")
    return errors


def validate_fastlio(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fastlio = bundle.get("fastlio") or {}
    require(errors, int(fastlio.get("callback_loopback_total", 1) or 0) == 0, "FAST-LIO callback_loopback_total must be zero")
    outputs = fastlio.get("outputs") or {}
    for topic in ("/Odometry", "/cloud_registered"):
        evidence = outputs.get(topic) or {}
        require(errors, int(evidence.get("count", 0) or 0) > 0, f"{topic} count must be nonzero")
        require(errors, evidence.get("frame_id") == "camera_init", f"{topic} frame_id must be camera_init")
        require(errors, evidence.get("monotonic") is True, f"{topic} stamps must be monotonic")
        require(errors, int(evidence.get("regression_count", 1) or 0) == 0, f"{topic} regression_count must be zero")
    path = outputs.get("/path") or {}
    if path:
        require(errors, path.get("frame_id") == "camera_init", "/path frame_id must be camera_init when present")
    return errors


def validate_tf(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tf = bundle.get("tf") or {}
    dynamic_edges = tf.get("dynamic_edges")
    static_edges = tf.get("static_edges")
    require(errors, isinstance(dynamic_edges, list), "tf.dynamic_edges must be an explicit list")
    require(errors, isinstance(static_edges, list), "tf.static_edges must be an explicit list, even when empty")
    if isinstance(dynamic_edges, list):
        require(errors, "camera_init->body" in dynamic_edges, "tf.dynamic_edges must include camera_init->body")
    grounding = tf.get("camera_init_map_world_grounding")
    if grounding is not None:
        status = str(grounding.get("status", "")).lower() if isinstance(grounding, dict) else str(grounding).lower()
        require(
            errors,
            status in {"absent", "blocked_absent", "real_same_run_evidence"},
            "camera_init_map_world_grounding status must be absent, blocked_absent, or real_same_run_evidence",
        )
        if status == "real_same_run_evidence":
            basis = str(grounding.get("basis", "")).lower()
            require(errors, "fake" not in basis and "arbitrary" not in basis and "rename" not in basis, "real grounding basis must not be fake/arbitrary/header rename")
            require(errors, bool(grounding.get("evidence_path")), "real grounding requires evidence_path")
    return errors


def validate_forbidden_topics(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    absence = bundle.get("forbidden_topic_absence") or {}
    observed = set(absence.get("observed_present_topics") or [])
    allowed = set(absence.get("authorized_present_topics") or [])
    unauthorized = sorted((observed & FORBIDDEN_TOPICS) - allowed)
    require(errors, absence.get("checked") is True, "forbidden_topic_absence.checked must be true")
    require(errors, not unauthorized, f"forbidden topics observed without authorization: {unauthorized}")
    require(errors, absence.get("published_goal_or_setpoint") is False, "published_goal_or_setpoint must be false before handoff authorization")
    return errors


def validate_cleanup(bundle: dict[str, Any]) -> list[str]:
    cleanup = bundle.get("cleanup") or {}
    errors: list[str] = []
    require(errors, cleanup.get("residue") in (False, "none", []), "cleanup residue must be false, none, or empty")
    require(errors, cleanup.get("kill_non_task_processes") is False, "cleanup must not kill non-task processes")
    return errors


def validate_controller_handoff(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    handoff = bundle.get("controller_handoff") or {}
    status = str(handoff.get("status", "")).lower()
    require(errors, status in {"blocked_no_map_world_grounding", "not_authorized", "authorized_with_real_grounding"}, "controller_handoff.status must be explicit")
    if status == "authorized_with_real_grounding":
        grounding = get_path(bundle, "tf.camera_init_map_world_grounding", {})
        require(errors, isinstance(grounding, dict) and grounding.get("status") == "real_same_run_evidence", "controller handoff authorization requires real same-run camera_init map/world grounding")
    else:
        require(errors, handoff.get("published_setpoints") is False, "blocked or not_authorized handoff must not publish setpoints")
    return errors


def validate_bundle(bundle: dict[str, Any], strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(validate_probe_budget(bundle))
    errors.extend(validate_lidar(bundle))
    errors.extend(validate_imu(bundle))
    errors.extend(validate_fastlio(bundle))
    errors.extend(validate_tf(bundle))
    errors.extend(validate_forbidden_topics(bundle))
    errors.extend(validate_cleanup(bundle))
    errors.extend(validate_controller_handoff(bundle))
    errors.extend(validate_no_forbidden_claims(bundle))
    errors.extend(validate_no_fake_routes(bundle))

    mode = str(bundle.get("mode", "")).lower()
    if "future" not in mode and "live" not in mode:
        warnings.append("mode does not explicitly say future/live evidence bundle")
        if strict:
            errors.append("strict mode requires mode to include future/live evidence bundle")

    accepted = not errors
    handoff_status = str(get_path(bundle, "controller_handoff.status", "")).lower()
    if accepted and handoff_status != "authorized_with_real_grounding":
        classification = "accepted_for_future_fastlio_output_review_controller_handoff_blocked"
    elif accepted:
        classification = "accepted_for_future_controller_handoff_with_real_grounding"
    else:
        classification = "rejected_or_blocked_future_live_evidence_bundle"

    return {
        "schema": "mosim.ros2_runtime.live_evidence_bundle_validation_summary_073.v1",
        "ok": accepted,
        "classification": classification,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": [
            "This validator is static/file-only and does not run ROS2, FAST-LIO, RViz2, planner, adapter, UE, or MWORKS.",
            "A passing validation means a future evidence bundle preserves required claim boundaries; it is not live TF/RViz readiness or planner/controller success.",
            "Controller handoff remains blocked unless real same-run camera_init-to-map/world grounding is present and explicitly authorized.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path, help="Path to future live evidence bundle JSON.")
    parser.add_argument("--output", type=Path, help="Optional path for validation summary JSON.")
    parser.add_argument("--strict", action="store_true", help="Require mode to name future/live evidence semantics.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    bundle = load_json_object(args.bundle)
    summary = validate_bundle(bundle, strict=args.strict)
    text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if summary["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
