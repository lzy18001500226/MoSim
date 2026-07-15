#!/usr/bin/env python3
"""Build a source audit packet for the local Swarm-Formation reference tree."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "References" / "Lab" / "Swarm-Formation"


KEY_FILES = {
    "readme": "README.md",
    "normal_hexagon_launch": "src/planner/plan_manage/launch/normal_hexagon.launch",
    "run_in_sim_launch": "src/planner/plan_manage/launch/run_in_sim.launch",
    "advanced_param_xml": "src/planner/plan_manage/launch/advanced_param.xml",
    "simulator_xml": "src/planner/plan_manage/launch/simulator.xml",
    "normal_hexagon_yaml": "src/planner/plan_manage/config/normal_hexagon.yaml",
    "bridge_launch": "src/planner/swarm_bridge/launch/bridge.launch",
    "ego_replan_fsm": "src/planner/plan_manage/src/ego_replan_fsm.cpp",
    "traj_server": "src/planner/plan_manage/src/traj_server.cpp",
    "bridge_node": "src/planner/swarm_bridge/src/bridge_node.cpp",
    "position_command_msg": "src/Utils/quadrotor_msgs/msg/PositionCommand.msg",
    "poly_traj_msg": "src/planner/traj_utils/msg/PolyTraj.msg",
}


def read_rel(path: str) -> str:
    return (SOURCE_ROOT / path).read_text(encoding="utf-8", errors="replace")


def rel_exists(path: str) -> bool:
    return (SOURCE_ROOT / path).exists()


def parse_xml_fragment(path: str) -> ET.Element:
    text = read_rel(path)
    return ET.fromstring(text)


def parse_args_from_xml(path: str) -> list[dict[str, str | None]]:
    root = parse_xml_fragment(path)
    return [
        {"name": node.get("name"), "value": node.get("value"), "default": node.get("default")}
        for node in root.findall(".//arg")
    ]


def parse_nodes_from_xml(path: str) -> list[dict[str, str | None]]:
    root = parse_xml_fragment(path)
    nodes: list[dict[str, str | None]] = []
    for node in root.findall(".//node"):
        nodes.append(
            {
                "pkg": node.get("pkg"),
                "type": node.get("type"),
                "name": node.get("name"),
                "output": node.get("output"),
            }
        )
    return nodes


def parse_remaps_from_xml(path: str) -> list[dict[str, str | None]]:
    root = parse_xml_fragment(path)
    return [
        {"from": node.get("from"), "to": node.get("to")}
        for node in root.findall(".//remap")
    ]


def parse_params_from_xml(path: str) -> list[dict[str, str | None]]:
    root = parse_xml_fragment(path)
    return [
        {"name": node.get("name"), "value": node.get("value"), "type": node.get("type")}
        for node in root.findall(".//param")
    ]


def parse_includes_from_xml(path: str) -> list[dict[str, object]]:
    root = parse_xml_fragment(path)
    includes: list[dict[str, object]] = []
    for inc in root.findall(".//include"):
        includes.append(
            {
                "file": inc.get("file"),
                "args": [
                    {"name": arg.get("name"), "value": arg.get("value")}
                    for arg in inc.findall("./arg")
                ],
            }
        )
    return includes


def find_regex(path: str, pattern: str) -> list[str]:
    text = read_rel(path)
    matches = []
    for match in re.finditer(pattern, text):
        line_no = text.count("\n", 0, match.start()) + 1
        line = text.splitlines()[line_no - 1].strip()
        matches.append(f"{path}:{line_no}: {line}")
    return matches


def parse_position_command_msg() -> list[str]:
    fields: list[str] = []
    for line in read_rel(KEY_FILES["position_command_msg"]).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields.append(line)
    return fields


def parse_polytraj_msg() -> list[str]:
    fields: list[str] = []
    for line in read_rel(KEY_FILES["poly_traj_msg"]).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields.append(line)
    return fields


def build_audit() -> dict[str, object]:
    packages = sorted(
        str(path.parent.relative_to(SOURCE_ROOT / "src")).replace("\\", "/")
        for path in (SOURCE_ROOT / "src").glob("**/package.xml")
    )
    launch_files = sorted(
        str(path.relative_to(SOURCE_ROOT)).replace("\\", "/")
        for path in SOURCE_ROOT.glob("src/**/*.launch")
    )
    msg_files = sorted(
        str(path.relative_to(SOURCE_ROOT)).replace("\\", "/")
        for path in SOURCE_ROOT.glob("src/**/*.msg")
    )
    key_file_status = {
        name: {"path": rel_path, "exists": rel_exists(rel_path)}
        for name, rel_path in KEY_FILES.items()
    }

    normal_launch = KEY_FILES["normal_hexagon_launch"]
    run_launch = KEY_FILES["run_in_sim_launch"]
    advanced_xml = KEY_FILES["advanced_param_xml"]
    simulator_xml = KEY_FILES["simulator_xml"]
    bridge_launch = KEY_FILES["bridge_launch"]

    normal_includes = parse_includes_from_xml(normal_launch)
    drone_includes = [
        inc
        for inc in normal_includes
        if inc["file"] == "$(find ego_planner)/launch/run_in_sim.launch"
    ]
    drone_profiles = []
    for inc in drone_includes:
        args = {arg["name"]: arg["value"] for arg in inc["args"]}  # type: ignore[index]
        drone_profiles.append(
            {
                "drone_id": args.get("drone_id"),
                "init": [args.get("init_x"), args.get("init_y"), args.get("init_z")],
                "target": [args.get("target_x"), args.get("target_y"), args.get("target_z")],
            }
        )

    audit = {
        "schema": "mosim.swarm_formation.d0_source_audit.v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_root": str(SOURCE_ROOT),
        "status": "review_ready",
        "key_files": key_file_status,
        "inventory": {
            "package_count": len(packages),
            "packages": packages,
            "launch_count": len(launch_files),
            "launch_files": launch_files,
            "msg_count": len(msg_files),
            "msg_files": msg_files,
        },
        "upstream_demo": {
            "readme_claim": "Ubuntu 18.04/20.04 with ROS; catkin_make -j1; rviz.launch + normal_hexagon.launch; target via 2D Nav Goal when flight_type=3.",
            "normal_hexagon": {
                "map_size": {"x": "70.0", "y": "30.0", "z": "3.0"},
                "odom_topic_arg": "visual_slam/odom",
                "formation_type_arg": "1",
                "drone_count": len(drone_profiles),
                "drone_profiles": drone_profiles,
                "includes": normal_includes,
                "nodes": parse_nodes_from_xml(normal_launch),
                "params": parse_params_from_xml(normal_launch),
            },
            "run_in_sim": {
                "args": parse_args_from_xml(run_launch),
                "includes": parse_includes_from_xml(run_launch),
                "nodes": parse_nodes_from_xml(run_launch),
                "remaps": parse_remaps_from_xml(run_launch),
            },
            "advanced_param": {
                "nodes": parse_nodes_from_xml(advanced_xml),
                "remaps": parse_remaps_from_xml(advanced_xml),
                "params": parse_params_from_xml(advanced_xml),
            },
            "simulator_xml": {
                "nodes": parse_nodes_from_xml(simulator_xml),
                "remaps": parse_remaps_from_xml(simulator_xml),
                "params": parse_params_from_xml(simulator_xml),
            },
            "swarm_bridge": {
                "nodes": parse_nodes_from_xml(bridge_launch),
                "remaps": parse_remaps_from_xml(bridge_launch),
                "params": parse_params_from_xml(bridge_launch),
            },
        },
        "message_contracts": {
            "position_command_fields": parse_position_command_msg(),
            "polytraj_fields": parse_polytraj_msg(),
        },
        "source_contract_hits": {
            "ego_replan_fsm_topics": find_regex(
                KEY_FILES["ego_replan_fsm"],
                r"(subscribe|advertise)<|subscribe\(|advertise\(|/move_base_simple/goal|/goal|/traj_start_trigger",
            ),
            "traj_server_topics": find_regex(
                KEY_FILES["traj_server"],
                r"(subscribe|advertise)<|subscribe\(|advertise\(|position_cmd|planning/trajectory|planning/start|planning/finish",
            ),
            "bridge_node_topics": find_regex(
                KEY_FILES["bridge_node"],
                r"(subscribe|advertise)<|subscribe\(|advertise\(|/others_odom|broadcast_traj",
            ),
        },
        "mosim_boundary": {
            "classification": "formation_or_cluster_planning_candidate_not_autonomous_exploration",
            "must_feed": "MoSim Planner Adapter / Trajectory Server; not direct MAVROS/PX4 final control commands.",
            "active_runtime_lane": "ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl / RViz",
            "known_gaps_before_mosim_gazebo": [
                "Upstream simulator uses poscmd_2_odom fake drone feedback, not PX4/MAVROS plant.",
                "Upstream obstacle source is random_forest/mockamap/global_cloud, not current MID360/FAST-LIO map.",
                "Upstream starts from seven-drone normal_hexagon; MoSim first proof should reduce to three UAVs.",
                "Upstream bridge uses UDP broadcast trajectory sharing; MoSim adapter must keep namespaces and safety gates explicit.",
            ],
        },
        "recommended_next_gates": [
            "SF-D1 isolated upstream build/launch smoke with bounded wait and no MoSim success claim.",
            "SF-D2 adapter dry-run: remap three MoSim UAV odom/cloud and inspect pos_cmd/trajectory topics without MAVROS commands.",
            "SF-D3 three-UAV Gazebo proof with known target formation transition through current per-UAV trajectory server and px4ctrl.",
        ],
    }
    return audit


def write_summary(audit: dict[str, object], out_dir: Path) -> None:
    upstream = audit["upstream_demo"]  # type: ignore[index]
    normal = upstream["normal_hexagon"]  # type: ignore[index]
    boundary = audit["mosim_boundary"]  # type: ignore[index]
    lines = [
        "# Swarm-Formation SF-D0 Source Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Source",
        "",
        f"- Source root: `{audit['source_root']}`",
        f"- Packages: `{audit['inventory']['package_count']}`",  # type: ignore[index]
        f"- Launch files: `{audit['inventory']['launch_count']}`",  # type: ignore[index]
        f"- Message files: `{audit['inventory']['msg_count']}`",  # type: ignore[index]
        "",
        "## Upstream Contract",
        "",
        f"- Default demo drone count: `{normal['drone_count']}`",
        "- Default demo launch: `ego_planner normal_hexagon.launch`",
        "- Default odom topic suffix: `visual_slam/odom`",
        "- Default goal mode in `run_in_sim.launch`: `flight_type=3`, RViz `/move_base_simple/goal`.",
        "- Published command stream: `drone_<id>_planning/pos_cmd` (`quadrotor_msgs/PositionCommand`).",
        "- Published trajectory stream: `drone_<id>_planning/trajectory` (`traj_utils/PolyTraj`).",
        "- Swarm trajectory exchange: `/broadcast_traj_from_planner` -> UDP bridge -> `/broadcast_traj_to_planner`.",
        "",
        "## MoSim Boundary",
        "",
        f"- Classification: `{boundary['classification']}`",
        f"- Must feed: {boundary['must_feed']}",
        "- Upstream success is not MoSim Gazebo/PX4 proof.",
        "- The first MoSim integration proof should be three UAVs, known-target formation transition, and no direct MAVROS command publication from Swarm-Formation.",
        "",
        "## Key Gaps",
        "",
    ]
    for gap in boundary["known_gaps_before_mosim_gazebo"]:  # type: ignore[index]
        lines.append(f"- {gap}")
    lines.extend(
        [
            "",
            "## Next Gates",
            "",
        ]
    )
    for gate in audit["recommended_next_gates"]:  # type: ignore[index]
        lines.append(f"- {gate}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `SWARM_FORMATION_D0_SOURCE_AUDIT.json`",
        ]
    )
    (out_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.output_dir or (
        REPO_ROOT / "Results" / "sunray_ros1" / f"swarm_formation_d0_source_audit_{timestamp}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = build_audit()
    (out_dir / "SWARM_FORMATION_D0_SOURCE_AUDIT.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_summary(audit, out_dir)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
