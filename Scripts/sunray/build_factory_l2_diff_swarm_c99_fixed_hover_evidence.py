#!/usr/bin/env python3
"""Build a reproducible evidence packet for a Factory L2 Diff-Swarm run.

This tool only reads an existing result directory. It does not start ROS,
Gazebo, PX4, MAVROS, RViz, or any GUI process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "sunray_ros1"
SOURCE_FILES = (
    ROOT / "Scripts" / "sunray" / "run_c99_multiuav_planner_gate.sh",
    ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_swarm_gate.sh",
    ROOT / "Scripts" / "sunray" / "px4ctrl_ego_swarm_mission_node.py",
)
REQUIRED_ARTIFACTS = (
    "EGO_SWARM_METRICS.json",
    "RUN_INPUTS.json",
    "RUN_MANIFEST.json",
    "STARTUP_ATTEMPT_SUMMARY.json",
    "planner_runtime_log_audit.json",
    "c99_diff_target_coordinate_contract.json",
    "c99_multiuav_contract.env",
    "goal5_preloaded_3uav.world",
    "inter_uav_separation.csv",
    "planner_swarm_px4ctrl_goal5.log",
)
PER_UAV_ARTIFACTS = (
    "uav{uid}_raw_position_cmd.csv",
    "uav{uid}_position_cmd.csv",
    "uav{uid}_bspline_summary.csv",
    "uav{uid}_truth.csv",
    "uav{uid}_pointcloud_diagnostics.json",
)
REPRODUCTION_ENV_KEYS = (
    "PLANNER_VARIANT",
    "UAV_NUM",
    "TARGET1_X",
    "TARGET1_Y",
    "TARGET1_Z",
    "TARGET2_X",
    "TARGET2_Y",
    "TARGET2_Z",
    "TARGET3_X",
    "TARGET3_Y",
    "TARGET3_Z",
    "C99_DIFF_TARGET_COORDINATE_FRAME",
    "C99_DIFF_MAVROS_ODOM_FRAME",
    "DIFF_GOAL5_COMMON_WORLD_FRAME",
    "SEQUENTIAL_SPAWN",
    "STAGGERED_SPAWN",
    "STAGGERED_SPAWN_INTERVAL_S",
    "PRELOAD_GAZEBO_MODELS",
    "PX4CTRL_CORE_PROFILE",
    "PX4CTRL_EXPECTED_BUILD_BACKEND",
    "PX4CTRL_HOVER_PERCENTAGE",
    "EGO_GATE_TAKEOFF_HEIGHT",
    "EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF",
    "EGO_GATE_TARGET_HOLD_S",
)


def workspace_path(value: Path) -> Path:
    path = value if value.is_absolute() else ROOT / value
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path outside MoSim workspace: {value}")
    return resolved


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int:
    with path.open(encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def artifact_record(path: Path) -> dict[str, Any]:
    return {
        "path": relative_path(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def numeric(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric, got {value!r}") from exc


def targets_match(expected: list[Any], actual: Any, tolerance: float = 1e-6) -> bool:
    if not isinstance(actual, (list, tuple)) or len(actual) != 3:
        return False
    return all(abs(numeric(left, "target") - numeric(right, "target")) <= tolerance for left, right in zip(expected, actual))


def run_artifacts(run_dir: Path) -> list[Path]:
    paths = [run_dir / name for name in REQUIRED_ARTIFACTS]
    for uid in (1, 2, 3):
        paths.extend(run_dir / pattern.format(uid=uid) for pattern in PER_UAV_ARTIFACTS)
    missing = [relative_path(path) for path in paths if not path.is_file()]
    if missing:
        raise ValueError("missing required runtime artifacts: " + ", ".join(missing))
    return paths


def add_check(checks: list[dict[str, Any]], blockers: list[str], check_id: str, passed: bool, details: dict[str, Any]) -> None:
    checks.append({"id": check_id, "passed": passed, "details": details})
    if not passed:
        blockers.append(check_id)


def startup_ready(startup: dict[str, Any], uid: int) -> tuple[bool, dict[str, Any]]:
    attempts = startup.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        return False, {"reason": "attempts_missing"}

    latest = attempts[-1]
    if not isinstance(latest, dict):
        return False, {"reason": "latest_attempt_invalid"}
    topics = latest.get("topics")
    if not isinstance(topics, dict):
        return False, {"reason": "topics_missing"}
    item = topics.get(f"uav{uid}")
    if not isinstance(item, dict):
        return False, {"reason": "uav_topics_missing"}

    state = item.get("mavros_state") if isinstance(item.get("mavros_state"), dict) else {}
    state_data = state.get("data") if isinstance(state.get("data"), dict) else {}
    odom = item.get("odom") if isinstance(item.get("odom"), dict) else {}
    lidar = item.get("raw_lidar") if isinstance(item.get("raw_lidar"), dict) else {}
    details = {
        "mavros_state_received": state.get("received") is True,
        "mavros_connected": state_data.get("connected") is True,
        "odom_received": odom.get("received") is True,
        "raw_lidar_received": lidar.get("received") is True,
        "startup_exit_code": latest.get("exit_code"),
        "mission_status": latest.get("mission_status"),
    }
    return (
        all(
            (
                details["mavros_state_received"],
                details["mavros_connected"],
                details["odom_received"],
                details["raw_lidar_received"],
                details["startup_exit_code"] == 0,
                details["mission_status"] == "passed",
            )
        ),
        details,
    )


def per_uav_summary(
    metrics: dict[str, Any],
    contract: dict[str, Any],
    run_dir: Path,
    min_target_hold_s: float,
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> list[dict[str, Any]]:
    per_uav = metrics.get("per_uav")
    source_targets = contract.get("source_targets")
    mission_targets = contract.get("mission_targets")
    planner_targets = contract.get("planner_targets")
    if not isinstance(per_uav, dict) or not isinstance(source_targets, dict):
        raise ValueError("per-UAV metrics or target contract is missing")

    summaries: list[dict[str, Any]] = []
    for uid in (1, 2, 3):
        key = str(uid)
        uav = per_uav.get(key)
        expected = source_targets.get(key)
        if not isinstance(uav, dict) or not isinstance(expected, list):
            raise ValueError(f"uav{uid} metrics or target is missing")
        target = uav.get("target")
        actual_target = [target.get("x"), target.get("y"), target.get("z")] if isinstance(target, dict) else target
        hold = uav.get("target_hold") if isinstance(uav.get("target_hold"), dict) else {}
        hold_reached = hold.get("reached") is True
        required_s = numeric(hold.get("required_s"), f"uav{uid}.target_hold.required_s")
        duration_s = numeric(hold.get("duration_s"), f"uav{uid}.target_hold.duration_s")
        hold_passed = hold_reached and required_s >= min_target_hold_s and duration_s >= required_s
        add_check(
            checks,
            blockers,
            f"uav{uid}_strict_target_hold",
            hold_passed,
            {
                "reached": hold_reached,
                "reached_by": hold.get("reached_by"),
                "required_s": required_s,
                "duration_s": duration_s,
                "minimum_required_s": min_target_hold_s,
                "end_error_m": (hold.get("end_snapshot") or {}).get("error_xyz_m"),
            },
        )
        coordinate_passed = (
            targets_match(expected, actual_target)
            and targets_match(expected, mission_targets.get(key) if isinstance(mission_targets, dict) else None)
            and targets_match(expected, planner_targets.get(key) if isinstance(planner_targets, dict) else None)
        )
        add_check(
            checks,
            blockers,
            f"uav{uid}_coordinate_contract",
            coordinate_passed,
            {
                "source_target": expected,
                "metric_target": actual_target,
                "mission_target": mission_targets.get(key) if isinstance(mission_targets, dict) else None,
                "planner_target": planner_targets.get(key) if isinstance(planner_targets, dict) else None,
            },
        )
        raw_samples = max(0, line_count(run_dir / f"uav{uid}_raw_position_cmd.csv") - 1)
        trajectory_samples = max(0, line_count(run_dir / f"uav{uid}_bspline_summary.csv") - 1)
        add_check(
            checks,
            blockers,
            f"uav{uid}_planner_output",
            raw_samples >= 10 and trajectory_samples >= 1,
            {"raw_position_cmd_samples": raw_samples, "planner_trajectory_samples": trajectory_samples},
        )
        summaries.append(
            {
                "uav": uid,
                "target_world_m": actual_target,
                "target_hold": {
                    "reached": hold_reached,
                    "reached_by": hold.get("reached_by"),
                    "required_s": required_s,
                    "duration_s": duration_s,
                    "end_error_m": (hold.get("end_snapshot") or {}).get("error_xyz_m"),
                    "end_speed_mps": (hold.get("end_snapshot") or {}).get("speed_mps"),
                    "end_abs_vz_mps": (hold.get("end_snapshot") or {}).get("abs_vz_mps"),
                },
                "planner_output": {
                    "raw_position_cmd_samples": raw_samples,
                    "planner_trajectory_samples": trajectory_samples,
                },
            }
        )
    return summaries


def reproduction_command(values: dict[str, str]) -> str:
    exports = ["RUN_ID=<new_run_id>", "RESULT_DIR=/mnt/c/Users/HP/Desktop/MoSim/Results/sunray_ros1/<new_run_id>"]
    exports.extend(f"{key}={shlex.quote(values[key])}" for key in REPRODUCTION_ENV_KEYS if values.get(key))
    command = " ".join(exports) + " bash Scripts/sunray/run_c99_multiuav_planner_gate.sh"
    return "wsl.exe -d Ubuntu-20.04 --exec bash -lc " + shlex.quote(
        "cd /mnt/c/Users/HP/Desktop/MoSim && " + command
    )


def build_packet(
    run_dir: Path,
    output_dir: Path,
    min_target_hold_s: float,
    min_inter_uav_distance_m: float,
) -> dict[str, Any]:
    artifacts = run_artifacts(run_dir)
    metrics = load_json(run_dir / "EGO_SWARM_METRICS.json")
    inputs = load_json(run_dir / "RUN_INPUTS.json")
    manifest = load_json(run_dir / "RUN_MANIFEST.json")
    startup = load_json(run_dir / "STARTUP_ATTEMPT_SUMMARY.json")
    audit = load_json(run_dir / "planner_runtime_log_audit.json")
    contract = load_json(run_dir / "c99_diff_target_coordinate_contract.json")
    contract_env = load_env(run_dir / "c99_multiuav_contract.env")

    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    add_check(
        checks,
        blockers,
        "mission_exit",
        metrics.get("status") == "passed"
        and not metrics.get("blockers")
        and manifest.get("mission_exit_code") == 0,
        {
            "metrics_status": metrics.get("status"),
            "metrics_blockers": metrics.get("blockers"),
            "mission_exit_code": manifest.get("mission_exit_code"),
        },
    )
    add_check(
        checks,
        blockers,
        "factory_world",
        "factoryenvironmentcollect_l2_static_review_clean" in str(inputs.get("world_file", ""))
        and bool(inputs.get("factory_l2_model_path_active")),
        {
            "world_file": inputs.get("world_file"),
            "factory_l2_model_path_active": inputs.get("factory_l2_model_path_active"),
        },
    )
    add_check(
        checks,
        blockers,
        "diff_planner_c99_profile",
        inputs.get("planner_variant") == "diff_planner"
        and manifest.get("controller_core_profile") == "graphical_c99"
        and contract_env.get("PX4CTRL_BUILD_BACKEND") == "graphical_px4ctrl_c99",
        {
            "planner_variant": inputs.get("planner_variant"),
            "controller_core_profile": manifest.get("controller_core_profile"),
            "build_backend": contract_env.get("PX4CTRL_BUILD_BACKEND"),
        },
    )
    add_check(
        checks,
        blockers,
        "target_coordinate_contract",
        contract.get("status") == "passed"
        and contract.get("source_frame") == "world"
        and contract.get("mavros_frame") == "common_world"
        and contract.get("mission_frame") == "common_world"
        and contract.get("planner_frame") == "common_world",
        {
            "status": contract.get("status"),
            "source_frame": contract.get("source_frame"),
            "mavros_frame": contract.get("mavros_frame"),
            "mission_frame": contract.get("mission_frame"),
            "planner_frame": contract.get("planner_frame"),
        },
    )
    add_check(
        checks,
        blockers,
        "planner_runtime_log",
        audit.get("status") == "passed"
        and not audit.get("blockers")
        and numeric(audit.get("fatal_event_count"), "fatal_event_count") == 0,
        {
            "status": audit.get("status"),
            "blockers": audit.get("blockers"),
            "fatal_event_count": audit.get("fatal_event_count"),
        },
    )

    readiness: list[dict[str, Any]] = []
    for uid in (1, 2, 3):
        passed, details = startup_ready(startup, uid)
        add_check(checks, blockers, f"uav{uid}_startup_readiness", passed, details)
        readiness.append({"uav": uid, **details})

    uavs = per_uav_summary(metrics, contract, run_dir, min_target_hold_s, checks, blockers)
    observed_separation = numeric(metrics.get("min_inter_uav_distance_m"), "min_inter_uav_distance_m")
    emergency = metrics.get("inter_uav_emergency_hold") if isinstance(metrics.get("inter_uav_emergency_hold"), dict) else {}
    add_check(
        checks,
        blockers,
        "inter_uav_separation",
        observed_separation >= min_inter_uav_distance_m and not emergency.get("events"),
        {
            "observed_min_distance_m": observed_separation,
            "required_min_distance_m": min_inter_uav_distance_m,
            "closest_pair": metrics.get("min_inter_uav_pair"),
            "emergency_events": emergency.get("events"),
        },
    )
    landing = metrics.get("landing") if isinstance(metrics.get("landing"), dict) else {}
    add_check(
        checks,
        blockers,
        "controlled_landing",
        landing.get("completed") is True and landing.get("exit_reason") == "all_uavs_landed_and_disarmed",
        {"completed": landing.get("completed"), "exit_reason": landing.get("exit_reason")},
    )

    source_records = [artifact_record(path) for path in SOURCE_FILES]
    packet = {
        "schema": "mosim.sunray_ros1.factory_l2_diff_swarm_c99_fixed_hover_evidence.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "passed" if not blockers else "blocked",
        "blockers": blockers,
        "source_run": {
            "run_id": inputs.get("run_id"),
            "result_dir": relative_path(run_dir),
            "world_file": inputs.get("world_file"),
            "planner_variant": inputs.get("planner_variant"),
            "controller_core_profile": manifest.get("controller_core_profile"),
            "px4ctrl_hover_percentage": contract_env.get("PX4CTRL_HOVER_PERCENTAGE"),
            "target_hold_s": contract_env.get("EGO_GATE_TARGET_HOLD_S"),
            "target_contract": relative_path(run_dir / "c99_diff_target_coordinate_contract.json"),
        },
        "checks": checks,
        "readiness": readiness,
        "per_uav": uavs,
        "separation": {
            "observed_min_distance_m": observed_separation,
            "required_min_distance_m": min_inter_uav_distance_m,
            "closest_pair": metrics.get("min_inter_uav_pair"),
            "emergency_events": emergency.get("events", []),
        },
        "reproduction": {
            "runtime_command": reproduction_command(contract_env),
            "contract_environment": {key: contract_env.get(key) for key in REPRODUCTION_ENV_KEYS},
            "static_checks": [
                "python -m pytest Scripts/tests/test_c99_planner_core_contract.py Scripts/tests/test_diff_swarm_core_fixture_contract.py Scripts/tests/test_px4ctrl_graphical_c99_runtime_contract.py Scripts/tests/test_build_factory_l2_diff_swarm_c99_fixed_hover_evidence.py",
                "wsl.exe -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash -n Scripts/sunray/run_c99_multiuav_planner_gate.sh Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh'",
                "wsl.exe -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && python3 -m py_compile Scripts/sunray/px4ctrl_ego_swarm_mission_node.py Scripts/sunray/build_factory_l2_diff_swarm_c99_fixed_hover_evidence.py'",
            ],
        },
        "integrity": {
            "runtime_artifacts": [artifact_record(path) for path in artifacts],
            "source_files_at_packet_build": source_records,
        },
        "claim_boundary": {
            "proves": [
                "One Factory L2 three-UAV ROS1/Gazebo/PX4/MAVROS/px4ctrl Diff-Planner fixed-target mission completed with the recorded contract.",
                "Each UAV passed the configured strict fixed-target dwell, and the recorded minimum inter-UAV separation exceeded the configured gate.",
                "The run completed controlled landing and disarm for all three aircraft.",
            ],
            "does_not_prove": [
                "Autonomous coverage or frontier exploration.",
                "FAST-LIO localization accuracy or a visual RViz acceptance review.",
                "A generalized multi-UAV safety guarantee beyond this fixed-target scenario and configured separation gate.",
                "Formal MWORKS controller acceptance or hardware flight performance.",
            ],
        },
    }
    return packet


def write_summary(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Factory L2 Diff-Swarm C99 Fixed-Hover Evidence",
        "",
        f"status: `{packet['status']}`",
        f"source_run: `{packet['source_run']['result_dir']}`",
        "",
        "## Runtime Gates",
        "",
        "| UAV | Target (world m) | Strict hold | End error (m) | Raw commands | Planner trajectories |",
        "|---|---|---|---:|---:|---:|",
    ]
    for item in packet["per_uav"]:
        hold = item["target_hold"]
        lines.append(
            "| uav{uav} | {target} | {duration:.3f}/{required:.3f} s | {error:.6f} | {raw} | {trajectory} |".format(
                uav=item["uav"],
                target=item["target_world_m"],
                duration=hold["duration_s"],
                required=hold["required_s"],
                error=numeric(hold["end_error_m"], "end_error_m"),
                raw=item["planner_output"]["raw_position_cmd_samples"],
                trajectory=item["planner_output"]["planner_trajectory_samples"],
            )
        )
    separation = packet["separation"]
    lines.extend(
        [
            "",
            "## Separation",
            "",
            f"- observed minimum: `{separation['observed_min_distance_m']:.6f} m`",
            f"- configured gate: `{separation['required_min_distance_m']:.6f} m`",
            f"- closest pair: `{separation['closest_pair']}`",
            "",
            "## Reproduction",
            "",
            "```powershell",
            packet["reproduction"]["runtime_command"],
            "```",
            "",
            "## Claim Boundary",
            "",
            "This packet is runtime evidence for one fixed-target Factory L2 scenario. It is not visual RViz acceptance, autonomous coverage, a generalized swarm-safety claim, formal MWORKS acceptance, or hardware-flight evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_packet(output_dir: Path, packet: dict[str, Any], force: bool) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "FACTORY_L2_DIFF_SWARM_C99_FIXED_HOVER_EVIDENCE.json"
    summary_path = output_dir / "SUMMARY.md"
    if not force and (json_path.exists() or summary_path.exists()):
        raise ValueError(f"packet output already exists: {output_dir}; use --force to overwrite")
    json_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    write_summary(summary_path, packet)
    return json_path, summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path, help="Existing Results/sunray_ros1 run directory")
    parser.add_argument("--output-dir", type=Path, help="Packet directory under the MoSim workspace")
    parser.add_argument("--min-target-hold-s", type=float, default=5.0)
    parser.add_argument("--min-inter-uav-distance-m", type=float, default=0.45)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = workspace_path(args.run_dir)
    if not run_dir.is_dir():
        raise SystemExit(f"run directory missing: {run_dir}")
    output_dir = (
        workspace_path(args.output_dir)
        if args.output_dir
        else DEFAULT_OUTPUT_ROOT / f"{run_dir.name}_evidence"
    )
    packet = build_packet(
        run_dir,
        output_dir,
        args.min_target_hold_s,
        args.min_inter_uav_distance_m,
    )
    json_path, _ = write_packet(output_dir, packet, args.force)
    print(relative_path(json_path))
    print(packet["status"])
    return 0 if packet["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
