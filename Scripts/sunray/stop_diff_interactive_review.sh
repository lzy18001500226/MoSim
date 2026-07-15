#!/usr/bin/env bash
# Stop the current Sunray ROS1 Goal4/Diff interactive-review process family.
#
# This intentionally uses /proc/cmdline matching instead of pkill -f from the
# caller shell, because broad pkill patterns can match and terminate the
# cleanup command itself.

set -euo pipefail

python3 - <<'PY'
import os
import signal
import time

PATTERNS = [
    "run_px4ctrl_ego_single_gate.sh",
    "start_diff_interactive_review.ps1",
    "review_diff_interactive_guard_",
    "diff_interactive_no_truncate_100hz_",
    "diff_single_auto123_",
    "px4ctrl_ego_single_mission_node.py",
    "external_fusion_node",
    "goal4_path_hold_from_csv.py",
    "goal4_pointcloud_to_world_node.py",
    "goal4_clicked_goal_adapter.py",
    "accumulate_pointcloud_review.py",
    "goal4_position_cmd_safety_adapter.py",
    "px4ctrl_mosim.launch",
    "diff_planner_single_px4ctrl_goal4.launch",
    "sunray_sim_uav_planning.launch",
    "sunray_ros1_goal4_diff_pointcloud_review.rviz",
    "sunray_ros1_goal4_diff_grid3d_review.rviz",
    "sunray_ros1_ego_grid_trajectory_review.rviz",
    "gzserver",
    "gzclient",
    "px4_sitl_default/bin/px4",
    "mavros_node",
    "diff_planner_node",
    "traj_server",
    "rosmaster --core -p 11311",
]


def select_processes():
    current = {os.getpid(), os.getppid()}
    selected = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid in current:
            continue
        try:
            raw = (
                open(f"/proc/{pid}/cmdline", "rb")
                .read()
                .replace(b"\0", b" ")
                .decode("utf-8", "ignore")
            )
        except OSError:
            continue
        if raw and any(pattern in raw for pattern in PATTERNS):
            selected.append((pid, raw[:260]))
    return selected


for sig, label, delay_s in (
    (signal.SIGTERM, "SIGTERM", 3.0),
    (signal.SIGKILL, "SIGKILL", 1.0),
):
    selected = select_processes()
    print(f"{label} selected_pids={len(selected)}")
    for pid, cmd in selected:
        print(f"{pid} {cmd}")
        try:
            os.kill(pid, sig)
        except OSError as exc:
            print(f"kill_error {pid} {exc}")
    time.sleep(delay_s)

remaining = select_processes()
print(f"remaining_after={len(remaining)}")
for pid, cmd in remaining:
    print(f"{pid} {cmd}")

raise SystemExit(1 if remaining else 0)
PY
