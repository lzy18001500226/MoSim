#!/usr/bin/env python3
"""Collect a bounded, read-only health snapshot for the three-UAV formation run.

This deliberately uses ``rostopic echo`` rather than creating a new rospy node.
The launcher has already proven that CLI route in the current WSL/ROS1 runtime,
and a health check must never block the active flight process.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout-s", type=float, default=12.0)
    parser.add_argument(
        "--mission-tracker-partial",
        default="",
        help="Optional same-run EGO_SWARM_METRICS_PARTIAL.json used only for occupancy history.",
    )
    return parser.parse_args()


def write_packet(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def mission_tracker_occupancy_history(path: Path) -> dict[str, Any]:
    """Read same-run task-node grid records without fabricating a live topic sample."""
    payload = read_json(path)
    if not payload:
        return {
            "source_file": str(path),
            "status": "missing_or_unreadable",
            "per_grid": {},
        }

    per_uav = payload.get("per_uav")
    if not isinstance(per_uav, dict):
        return {
            "source_file": str(path),
            "status": "missing_per_uav",
            "per_grid": {},
        }

    per_grid: dict[str, dict[str, Any]] = {}
    for uid in range(1, 4):
        vehicle = per_uav.get(str(uid))
        if not isinstance(vehicle, dict):
            continue
        counts = vehicle.get("counts")
        last_point_counts = vehicle.get("last_point_counts")
        if not isinstance(counts, dict):
            counts = {}
        if not isinstance(last_point_counts, dict):
            last_point_counts = {}
        update_count = nonnegative_int(counts.get("occupancy"))
        last_point_count = nonnegative_int(last_point_counts.get("occupancy"))
        per_grid[f"drone{uid - 1}_occupancy_inflate"] = {
            "uav_id": uid,
            "update_count": update_count,
            "last_point_count": last_point_count,
            "nonempty": update_count > 0 and last_point_count > 0,
        }

    return {
        "source_file": str(path),
        "status": "available",
        "per_grid": per_grid,
    }


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1) if match else default


def capture_topic(topic: str, timeout_s: float) -> tuple[str, str, int, str]:
    # The pipe intentionally stops after the metadata fields used by the probe.
    # A PointCloud2 can otherwise serialize megabytes of binary payload just to
    # prove that its width is nonzero.
    command = f"rostopic echo -n 1 {topic} | head -n 32"
    completed = subprocess.run(
        ["timeout", "--kill-after=1s", f"{timeout_s:.1f}s", "bash", "-lc", command],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return topic, completed.stdout, completed.returncode, completed.stderr.strip()


def pointcloud_sample(topic: str, output: str, returncode: int, stderr: str) -> dict[str, Any]:
    width = int(first_match(r"^width:\s*(\d+)\s*$", output, "0"))
    height = int(first_match(r"^height:\s*(\d+)\s*$", output, "0"))
    return {
        "topic": topic,
        "received": bool(output),
        "frame_id": first_match(r'^\s*frame_id:\s*"?([^"\n]+)', output),
        "width": width,
        "height": height,
        "point_count": width * max(1, height),
        "nonempty": bool(width),
        "rostopic_exit_code": returncode,
        "stderr": stderr,
    }


def state_sample(topic: str, output: str, returncode: int, stderr: str) -> dict[str, Any]:
    connected = first_match(r"^connected:\s*(True|False)\s*$", output)
    armed = first_match(r"^armed:\s*(True|False)\s*$", output)
    return {
        "topic": topic,
        "received": bool(output),
        "connected": connected == "True",
        "armed": armed == "True",
        "mode": first_match(r"^mode:\s*(.*)$", output),
        "rostopic_exit_code": returncode,
        "stderr": stderr,
    }


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    mission_tracker_partial = (
        Path(args.mission_tracker_partial)
        if args.mission_tracker_partial
        else output.with_name("EGO_SWARM_METRICS_PARTIAL.json")
    )
    started = time.time()
    sample_timeout_s = min(6.0, max(1.0, float(args.timeout_s)))

    world_clouds: dict[str, str] = {}
    for uid in range(1, 4):
        world_clouds[f"uav{uid}_livox_world"] = f"/uav{uid}/livox_world"
    occupancy_grids: dict[str, str] = {}
    for drone_id in range(3):
        occupancy_grids[f"drone{drone_id}_occupancy_inflate"] = (
            f"/drone_{drone_id}/ego_planner_node/grid_map/occupancy_inflate"
        )
    expected_clouds = {**world_clouds, **occupancy_grids}
    review_clouds = {
        f"uav{uid}_accumulated_cloud": f"/mosim/swarm_formation/uav{uid}/livox_world_accumulated"
        for uid in range(1, 4)
    }
    expected_states = {f"uav{uid}_mavros_state": f"/uav{uid}/mavros/state" for uid in range(1, 4)}

    topic_jobs = {**expected_clouds, **review_clouds, **expected_states}
    captured: dict[str, tuple[str, int, str]] = {}
    with ThreadPoolExecutor(max_workers=len(topic_jobs)) as executor:
        futures = {
            executor.submit(capture_topic, topic, sample_timeout_s): name
            for name, topic in topic_jobs.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                _topic, text, returncode, stderr = future.result()
                captured[name] = (text, returncode, stderr)
            except Exception as exc:  # pragma: no cover - unexpected subprocess failure
                captured[name] = ("", 2, repr(exc))

    clouds = {
        name: pointcloud_sample(topic, *captured[name]) for name, topic in expected_clouds.items()
    }
    accumulated_clouds = {
        name: pointcloud_sample(topic, *captured[name]) for name, topic in review_clouds.items()
    }
    states = {
        name: state_sample(topic, *captured[name]) for name, topic in expected_states.items()
    }
    history = mission_tracker_occupancy_history(mission_tracker_partial)
    occupancy_readiness: dict[str, dict[str, Any]] = {}
    for name, topic in occupancy_grids.items():
        direct = clouds[name]
        historical = history.get("per_grid", {}).get(name, {})
        historical_nonempty = bool(historical.get("nonempty", False))
        effective_nonempty = bool(direct.get("nonempty", False)) or historical_nonempty
        occupancy_readiness[name] = {
            "topic": topic,
            "live_topic": direct,
            "mission_tracker_history": historical,
            "effective_nonempty": effective_nonempty,
            "effective_source": (
                "live_topic"
                if direct.get("nonempty", False)
                else "mission_tracker_history"
                if historical_nonempty
                else "missing"
            ),
        }
    world_missing = [name for name, sample in clouds.items() if name in world_clouds and not sample.get("nonempty", False)]
    occupancy_missing = [
        name for name, sample in occupancy_readiness.items() if not sample.get("effective_nonempty", False)
    ]
    sensor_missing = world_missing + occupancy_missing
    flight_link_missing = [
        name for name, sample in states.items() if not sample.get("connected", False)
    ]
    review_missing = [
        name for name, sample in accumulated_clouds.items() if not sample.get("nonempty", False)
    ]
    missing = sensor_missing + flight_link_missing
    packet = {
        "schema": "mosim.factory_l2.swarm_formation.runtime_probe.v1",
        "status": "passed" if not missing else "blocked",
        "reason_code": "ok" if not missing else "required_topics_missing_or_empty",
        "created_at_unix_s": started,
        "duration_s": round(time.time() - started, 3),
        "clouds": clouds,
        "mission_tracker_history": history,
        "occupancy_grid_readiness": {
            "status": "passed" if not occupancy_missing else "blocked",
            "missing_or_empty": occupancy_missing,
            "required_grid_count": len(occupancy_readiness),
            "ready_grid_count": len(occupancy_readiness) - len(occupancy_missing),
            "grids": occupancy_readiness,
            "claim_boundary": "A same-run mission tracker may only supplement a missed instantaneous occupancy topic sample. It does not replace live MID360 or MAVROS sampling.",
        },
        "review_accumulated_clouds": accumulated_clouds,
        "mavros_states": states,
        "sensor_grid_readiness": {
            "status": "passed" if not sensor_missing else "blocked",
            "missing_or_empty": sensor_missing,
            "required_topic_count": len(clouds),
            "ready_topic_count": len(clouds) - len(sensor_missing),
        },
        "flight_link_readiness": {
            "status": "passed" if not flight_link_missing else "blocked",
            "missing_or_disconnected": flight_link_missing,
            "required_link_count": len(states),
            "ready_link_count": len(states) - len(flight_link_missing),
        },
        "rviz_map_readiness": {
            "status": "ready" if not review_missing else "not_attached_or_incomplete",
            "missing_or_empty": review_missing,
            "required_topic_count": len(accumulated_clouds),
            "ready_topic_count": len(accumulated_clouds) - len(review_missing),
            "required_for_backend_start": False,
        },
        "missing_or_empty": missing,
        "claim_boundary": "Read-only liveness check. Live MID360 and MAVROS are sampled directly. A same-run mission tracker may only supplement a missed instantaneous occupancy-grid sample. sensor_grid_readiness, flight_link_readiness, and rviz_map_readiness remain independent evidence layers. An RViz map may be ready while MAVROS is degraded, and a connected MAVROS link does not establish tracking quality, obstacle avoidance, or 4-9 UAV scalability.",
    }
    write_packet(output, packet)
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
