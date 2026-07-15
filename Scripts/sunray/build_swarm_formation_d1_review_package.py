#!/usr/bin/env python3
"""Build a Swarm-Formation SF-D1 review package from an isolated ROS1 workspace.

This script indexes already-created build and launch-parse evidence only. It
does not start ROS, Gazebo, PX4, MAVROS, RViz, or any GUI process.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "sunray_ros1"
REQUIRED_EXECUTABLES = {
    "ego_planner_node": "devel/lib/ego_planner/ego_planner_node",
    "traj_server": "devel/lib/ego_planner/traj_server",
    "bridge_node": "devel/lib/swarm_bridge/bridge_node",
    "random_forest": "devel/lib/map_generator/random_forest",
    "poscmd_2_odom": "devel/lib/poscmd_2_odom/poscmd_2_odom",
    "pcl_render_node": "devel/lib/local_sensing_node/pcl_render_node",
}
REQUIRED_PACKAGES = [
    "ego_planner",
    "swarm_bridge",
    "traj_utils",
    "traj_opt",
    "plan_env",
    "path_searching",
    "swarm_graph",
    "quadrotor_msgs",
    "pose_utils",
    "map_generator",
    "local_sensing_node",
    "poscmd_2_odom",
    "odom_visualization",
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path outside MoSim workspace: {value}")
    return resolved


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]


def executable_status(workspace: Path) -> dict[str, dict[str, Any]]:
    status: dict[str, dict[str, Any]] = {}
    for name, rel_path in REQUIRED_EXECUTABLES.items():
        path = workspace / rel_path
        status[name] = {
            "path": rel(path),
            "exists": path.is_file(),
            "size_bytes": path.stat().st_size if path.is_file() else None,
        }
    return status


def package_status(workspace: Path) -> dict[str, dict[str, Any]]:
    package_xml_by_name: dict[str, Path] = {}
    for package_xml in (workspace / "src").glob("**/package.xml"):
        try:
            root = ET.fromstring(package_xml.read_text(encoding="utf-8", errors="replace"))
        except ET.ParseError:
            continue
        name = root.findtext("name")
        if name:
            package_xml_by_name[name.strip()] = package_xml

    status: dict[str, dict[str, Any]] = {}
    for package in REQUIRED_PACKAGES:
        package_xml = package_xml_by_name.get(package)
        status[package] = {
            "present": package_xml is not None,
            "package_xml": rel(package_xml) if package_xml else "",
        }
    return status


def classify_catkin_log(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"present": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "present": True,
        "line_count": len(text.splitlines()),
        "contains_timeout_termination": "Terminated" in text,
        "contains_compiler_error": " error:" in text.lower() or "undefined reference" in text.lower(),
        "tail": text.splitlines()[-40:],
    }


def build_packet(workspace: Path) -> dict[str, Any]:
    normal_nodes = read_lines(workspace / "normal_hexagon_nodes.txt")
    run_nodes = read_lines(workspace / "run_in_sim_nodes.txt")
    executables = executable_status(workspace)
    packages = package_status(workspace)
    missing_executables = [name for name, item in executables.items() if not item["exists"]]
    missing_packages = [name for name, item in packages.items() if not item["present"]]
    status = "review_ready" if not missing_executables and not missing_packages and normal_nodes and run_nodes else "incomplete"
    return {
        "schema": "mosim.swarm_formation.d1_upstream_smoke_review.v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "workspace": rel(workspace),
        "scope": "isolated upstream ROS1 build and roslaunch --nodes parse only",
        "claims": {
            "proves": [
                "Required Swarm-Formation planner-side ROS1 packages are present in the isolated workspace.",
                "Required planner/simulator helper executables exist after segmented build recovery.",
                "normal_hexagon.launch and run_in_sim.launch can be resolved by roslaunch --nodes in the isolated workspace.",
            ],
            "does_not_prove": [
                "No ROS/Gazebo/PX4/MAVROS/RViz runtime success is claimed.",
                "No MoSim three-UAV formation flight success is claimed.",
                "No autonomous exploration or full-map coverage claim is made.",
            ],
        },
        "build": {
            "catkin_make_log": rel(workspace / "catkin_make.log"),
            "catkin_make_log_classification": classify_catkin_log(workspace / "catkin_make.log"),
            "segmented_recovery_note": (
                "The seed catkin_make may time out on Windows-mounted workspaces; "
                "SF-D1 acceptance is based on required target executables plus launch parse."
            ),
        },
        "packages": packages,
        "missing_packages": missing_packages,
        "executables": executables,
        "missing_executables": missing_executables,
        "launch_parse": {
            "normal_hexagon_nodes_file": rel(workspace / "normal_hexagon_nodes.txt"),
            "normal_hexagon_nodes": normal_nodes,
            "normal_hexagon_node_count": len(normal_nodes),
            "run_in_sim_nodes_file": rel(workspace / "run_in_sim_nodes.txt"),
            "run_in_sim_nodes": run_nodes,
            "run_in_sim_node_count": len(run_nodes),
        },
        "next_gate": {
            "id": "SF-D2",
            "summary": (
                "MoSim adapter dry-run for uav1/uav2/uav3 known-target formation; "
                "remap MoSim-like odom/cloud into Swarm-Formation inputs, inspect "
                "per-UAV trajectory/pos_cmd outputs, and forbid MAVROS command publication."
            ),
        },
    }


def write_summary(packet: dict[str, Any], out_dir: Path) -> None:
    lines = [
        "# Swarm-Formation SF-D1 Upstream Smoke Review",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Scope",
        "",
        f"- Workspace: `{packet['workspace']}`",
        f"- Evidence scope: `{packet['scope']}`",
        "- This is build/launch-parse evidence only.",
        "",
        "## Build Evidence",
        "",
        f"- Catkin log: `{packet['build']['catkin_make_log']}`",
        f"- Required executables missing: `{packet['missing_executables']}`",
        f"- Required packages missing: `{packet['missing_packages']}`",
        "- The seed `catkin_make` can time out on the Windows-mounted workspace; required targets were recovered through segmented target builds.",
        "",
        "## Launch Parse Evidence",
        "",
        f"- `normal_hexagon.launch --nodes`: `{packet['launch_parse']['normal_hexagon_node_count']}` nodes.",
        f"- `run_in_sim.launch --nodes`: `{packet['launch_parse']['run_in_sim_node_count']}` nodes.",
        "- `normal_hexagon.launch` resolves the upstream seven-UAV demo nodes plus `random_forest` and `swarm_bridge`.",
        "- `run_in_sim.launch` resolves one per-UAV planner/traj_server/fake-drone/local-sensing stack.",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in packet["claims"]["does_not_prove"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            f"- `{packet['next_gate']['id']}`: {packet['next_gate']['summary']}",
            "",
            "## Artifacts",
            "",
            "- `SWARM_FORMATION_D1_UPSTREAM_SMOKE_REVIEW.json`",
            "- `SUMMARY.md`",
        ]
    )
    (out_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    workspace = repo_path(args.workspace)
    if not workspace.is_dir():
        raise SystemExit(f"workspace missing: {workspace}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = repo_path(args.output_dir) if args.output_dir else (
        DEFAULT_OUTPUT_ROOT / f"swarm_formation_d1_upstream_smoke_{timestamp}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    packet = build_packet(workspace)
    (out_dir / "SWARM_FORMATION_D1_UPSTREAM_SMOKE_REVIEW.json").write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_summary(packet, out_dir)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
