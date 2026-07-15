#!/usr/bin/env python3
"""Build the RACER-D0 source/interface/dependency audit package.

This is a read-only source audit. It does not start ROS, Gazebo, PX4, MAVROS,
RViz, RACER, FUEL, or any GUI process.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "References/Lab/exploration_coverage/RACER"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/sunray_ros1"


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def strip_xml_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def line_hits(path: Path, pattern: str, limit: int = 20) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    rx = re.compile(pattern)
    if not path.is_file():
        return hits
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if rx.search(line):
            hits.append({"file": rel(path), "line": idx, "text": line.strip()})
            if len(hits) >= limit:
                break
    return hits


def collect_files(source: Path, pattern: str) -> list[str]:
    return sorted(rel(path) for path in source.rglob(pattern) if path.is_file())


def extract_arg_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    text = strip_xml_comments(read_text(path))
    cut_points = [pos for token in ("<include", "<node") if (pos := text.find(token)) >= 0]
    if cut_points:
        text = text[: min(cut_points)]
    for name, value in re.findall(r'<arg\s+name="([^"]+)"\s+(?:default|value)="([^"]*)"', text):
        values.setdefault(name, value)
    return values


def extract_remaps(path: Path) -> list[dict[str, str]]:
    remaps: list[dict[str, str]] = []
    text = strip_xml_comments(read_text(path))
    for old, new in re.findall(r'<remap\s+from\s*=\s*"([^"]+)"\s+to\s*=\s*"([^"]+)"', text):
        remaps.append({"from": old, "to": new})
    for old, new in re.findall(r'<remap\s+from="([^"]+)"\s+to="([^"]+)"', text):
        item = {"from": old, "to": new}
        if item not in remaps:
            remaps.append(item)
    return remaps


def extract_params(path: Path, prefix_allowlist: tuple[str, ...]) -> dict[str, str]:
    params: dict[str, str] = {}
    text = strip_xml_comments(read_text(path))
    for name, value in re.findall(r'<param\s+name="([^"]+)"\s+value="([^"]*)"', text):
        if any(name.startswith(prefix) for prefix in prefix_allowlist):
            params[name] = value
    return params


def extract_launch_includes(path: Path) -> list[dict[str, str]]:
    includes: list[dict[str, str]] = []
    text = strip_xml_comments(read_text(path))
    for file_value in re.findall(r'<include\s+file="([^"]+)"', text):
        includes.append({"file": file_value})
    return includes


def extract_nodes(path: Path) -> list[dict[str, str]]:
    nodes: list[dict[str, str]] = []
    text = strip_xml_comments(read_text(path))
    for pkg, name, node_type in re.findall(
        r'<node\s+pkg\s*=\s*"([^"]+)"\s+name\s*=\s*"([^"]+)"\s+type\s*=\s*"([^"]+)"',
        text,
    ):
        nodes.append({"pkg": pkg, "name": name, "type": node_type})
    for pkg, name, node_type in re.findall(
        r'<node\s+pkg="([^"]+)"\s+name="([^"]+)"\s+type="([^"]+)"',
        text,
    ):
        item = {"pkg": pkg, "name": name, "type": node_type}
        if item not in nodes:
            nodes.append(item)
    return nodes


def parse_msg(path: Path) -> list[str]:
    fields: list[str] = []
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line == "---":
            continue
        fields.append(line)
    return fields


def collect_package_names(source: Path) -> list[str]:
    names: set[str] = set()
    for package in source.rglob("package.xml"):
        text = read_text(package)
        match = re.search(r"<name>([^<]+)</name>", text)
        if match:
            names.add(match.group(1).strip())
    return sorted(names)


def collect_dependency_hints(source: Path) -> dict[str, Any]:
    readme = source / "README.md"
    bspline_cmake = source / "swarm_exploration/bspline_opt/CMakeLists.txt"
    local_sensing_cmake = source / "uav_simulator/local_sensing/CMakeLists.txt"
    hints = {
        "readme_dependencies": {
            "nlopt": line_hits(readme, r"nlopt|NLopt", 10),
            "armadillo": line_hits(readme, r"armadillo|Armadillo", 10),
            "lkh": line_hits(readme, r"LKH", 10),
            "supported_ubuntu_ros": line_hits(readme, r"Ubuntu|ROS Melodic|ROS Noetic", 5),
        },
        "hardcoded_paths": {
            "nlopt": line_hits(bspline_cmake, r"/usr/local/(include|lib/libnlopt\.so)", 10),
            "local_sensing_cuda_or_eigen": line_hits(local_sensing_cmake, r"ENABLE_CUDA|CUDA|Eigen|OpenCV|PCL", 20),
        },
        "package_names": collect_package_names(source),
    }
    return hints


def collect_interface(source: Path) -> dict[str, Any]:
    launch_root = source / "swarm_exploration/exploration_manager/launch"
    swarm_launch = launch_root / "swarm_exploration.launch"
    single_exploration = launch_root / "single_drone_exploration.xml"
    single_planner = launch_root / "single_drone_planner.xml"
    tsp_server = launch_root / "tsp_server.launch"
    traj_server = source / "swarm_exploration/plan_manage/src/traj_server.cpp"
    fsm = source / "swarm_exploration/exploration_manager/src/fast_exploration_fsm.cpp"
    map_ros = source / "swarm_exploration/plan_env/src/map_ros.cpp"
    multi_map = source / "swarm_exploration/plan_env/src/multi_map_manager.cpp"
    return {
        "launch_files": {
            "swarm_exploration": {
                "path": rel(swarm_launch),
                "args": extract_arg_values(swarm_launch),
                "nodes": extract_nodes(swarm_launch),
                "includes": extract_launch_includes(swarm_launch),
            },
            "single_drone_exploration": {
                "path": rel(single_exploration),
                "args": extract_arg_values(single_exploration),
                "remaps": extract_remaps(single_exploration),
                "nodes": extract_nodes(single_exploration),
            },
            "single_drone_planner": {
                "path": rel(single_planner),
                "args": extract_arg_values(single_planner),
                "remaps": extract_remaps(single_planner),
                "params": extract_params(
                    single_planner,
                    (
                        "sdf_map/",
                        "map_ros/",
                        "fsm/",
                        "partitioning/",
                        "exploration/",
                        "frontier/",
                        "manager/",
                        "search/",
                        "optimization/",
                        "bspline/",
                    ),
                ),
                "nodes": extract_nodes(single_planner),
            },
            "tsp_server": {
                "path": rel(tsp_server),
                "nodes": extract_nodes(tsp_server),
                "params": extract_params(tsp_server, ("exploration/",)),
            },
        },
        "code_topics": {
            "fast_exploration_fsm": {
                "path": rel(fsm),
                "timers": line_hits(fsm, r"createTimer", 20),
                "pub_sub": line_hits(fsm, r"subscribe\(|advertise<", 40),
                "trigger": line_hits(fsm, r"/move_base_simple/goal|triggerCallback|WAIT_TRIGGER", 20),
                "odom_fields": line_hits(fsm, r"odom_pos_|odom_vel_|odom_orient_|odom_yaw_", 25),
            },
            "map_ros": {
                "path": rel(map_ros),
                "sync_and_inputs": line_hits(map_ros, r"message_filters|/map_ros/(depth|cloud|pose)|depthPoseCallback|cloudPoseCallback", 35),
                "map_outputs": line_hits(map_ros, r"advertise<.*(/sdf_map|depth_cloud)|publishMap(All|Local)|publishDepth", 30),
            },
            "multi_map_manager": {
                "path": rel(multi_map),
                "timers": line_hits(multi_map, r"createTimer", 10),
                "pub_sub": line_hits(multi_map, r"/multi_map_manager/(chunk_stamps|chunk_data).*_(send|recv)|advertise<|subscribe", 30),
            },
            "traj_server": {
                "path": rel(traj_server),
                "bspline_input": line_hits(traj_server, r"bsplineCallback|bspline::Bspline|/planning/bspline", 25),
                "pos_cmd_output": line_hits(traj_server, r"PositionCommand|pos_cmd_pub|/position_cmd|cmd\.position|cmd\.velocity|cmd\.acceleration|cmd\.yaw", 35),
            },
        },
    }


def collect_messages(source: Path) -> dict[str, list[str]]:
    message_paths = [
        source / "swarm_exploration/bspline/msg/Bspline.msg",
        source / "swarm_exploration/exploration_manager/msg/DroneState.msg",
        source / "swarm_exploration/exploration_manager/msg/PairOpt.msg",
        source / "swarm_exploration/exploration_manager/msg/PairOptResponse.msg",
        source / "swarm_exploration/exploration_manager/msg/GridTour.msg",
        source / "swarm_exploration/exploration_manager/msg/HGrid.msg",
        source / "swarm_exploration/plan_env/msg/IdxList.msg",
        source / "swarm_exploration/plan_env/msg/ChunkStamps.msg",
        source / "swarm_exploration/plan_env/msg/ChunkData.msg",
        source / "swarm_exploration/utils/lkh_tsp_solver/srv/SolveTSP.srv",
        source / "swarm_exploration/utils/lkh_mtsp_solver/srv/SolveMTSP.srv",
    ]
    return {rel(path): parse_msg(path) for path in message_paths}


def derive_findings(source: Path, interface: dict[str, Any], deps: dict[str, Any]) -> list[dict[str, str]]:
    findings = [
        {
            "id": "RACER_D0_001",
            "severity": "info",
            "claim": "RACER upstream is ROS Melodic/Noetic compatible and is a valid local source candidate for the current Ubuntu-20.04/ROS1 lane.",
            "evidence": "README reports Ubuntu 18.04/20.04 and ROS Melodic/Noetic support.",
        },
        {
            "id": "RACER_D0_002",
            "severity": "risk",
            "claim": "Default launch is an upstream PCD/render demo, not MoSim Gazebo proof.",
            "evidence": "swarm_exploration.launch starts map_generator map_pub with pillar.pcd and simulator_light.xml can start upstream simulator nodes.",
        },
        {
            "id": "RACER_D0_003",
            "severity": "risk",
            "claim": "D1 build must patch or inject NLopt paths because bspline_opt hard-codes /usr/local include/libnlopt.so.",
            "evidence": "bspline_opt/CMakeLists.txt sets NLOPT_INCLUDE_DIR and NLOPT_LIBRARY under /usr/local.",
        },
        {
            "id": "RACER_D0_004",
            "severity": "risk",
            "claim": "D1 build requires LKH/TSP services and probably both lkh_tsp_solver and lkh_mtsp_solver resources for each drone.",
            "evidence": "tsp_server.launch starts tsp_node and mtsp_node for drone ids 1-3; exploration_manager reads exploration/tsp_dir and mtsp_dir.",
        },
        {
            "id": "RACER_D0_005",
            "severity": "info",
            "claim": "RACER already exposes per-UAV B-spline and pos_cmd topics through drone_id remaps.",
            "evidence": "single_drone_planner.xml remaps /planning/bspline, /planning/replan, /planning/new, /position_cmd and visualization/map topics to suffixed per-drone names.",
        },
        {
            "id": "RACER_D0_006",
            "severity": "requirement",
            "claim": "MoSim D2 must bridge sensor pose plus either cloud or depth; cloud alone is not enough because RACER synchronizes /map_ros/cloud with /map_ros/pose.",
            "evidence": "MapROS creates message_filters synchronizers for depth+pose and cloud+pose.",
        },
        {
            "id": "RACER_D0_007",
            "severity": "requirement",
            "claim": "MoSim D2 must keep RACER away from direct MAVROS/PX4 publication; use RACER B-spline/pos_cmd as planner outputs only.",
            "evidence": "traj_server publishes quadrotor_msgs/PositionCommand; any MAVROS bridge must remain MoSim-owned and reversible.",
        },
        {
            "id": "RACER_D0_008",
            "severity": "requirement",
            "claim": "Three-UAV target should override upstream drone_num=5 and launch only uav1/uav2/uav3 for the first MoSim gate.",
            "evidence": "swarm_exploration.launch has drone_num=5 while active MoSim requirement is uav1/uav2/uav3.",
        },
        {
            "id": "RACER_D0_009",
            "severity": "risk",
            "claim": "RACER uses shared non-namespaced swarm/map channels by design; adapter dry-run must prove self-message filtering and per-drone output isolation.",
            "evidence": "single_drone_planner.xml remaps send/recv topics to shared /swarm_expl/* and /multi_map_manager/* topics.",
        },
        {
            "id": "RACER_D0_010",
            "severity": "risk",
            "claim": "The upstream local_sensing package currently disables CUDA but still uses a PCD renderer; MoSim proof should prefer online Sunray/Gazebo sensor topics or a clearly marked sensor renderer boundary.",
            "evidence": "local_sensing/CMakeLists.txt has ENABLE_CUDA false and builds pcl_render_node from pointcloud_render_node.cpp.",
        },
    ]
    return findings


def build_summary(audit: dict[str, Any]) -> str:
    evidence_dir = audit["evidence_dir"]
    findings = audit["findings"]
    risks = [f for f in findings if f["severity"] == "risk"]
    requirements = [f for f in findings if f["severity"] == "requirement"]
    lines = [
        "# RACER-D0 Source Audit",
        "",
        f"Status: `{audit['status']}`",
        f"Generated: `{audit['generated_at']}`",
        f"Source: `{audit['source_root']}`",
        "",
        "## Conclusion",
        "",
        "RACER is a viable local source candidate for three-UAV autonomous exploration,",
        "but D0 only proves source/interface readiness. It does not prove a RACER",
        "build, upstream smoke, MoSim adapter dry-run, or Gazebo multi-UAV closed loop.",
        "",
        "The next gate is RACER-D1 only after NLopt/LKH/package dependency handling is",
        "made explicit, followed by RACER-D2 namespace adapter dry-run.",
        "",
        "## Key Findings",
        "",
    ]
    for item in findings:
        lines.append(f"- `{item['id']}` `{item['severity']}`: {item['claim']}")
    lines.extend(
        [
            "",
            "## D1 Build Risks",
            "",
        ]
    )
    for item in risks:
        lines.append(f"- `{item['id']}`: {item['evidence']}")
    lines.extend(
        [
            "",
            "## D2 Adapter Requirements",
            "",
        ]
    )
    for item in requirements:
        lines.append(f"- `{item['id']}`: {item['claim']}")
    lines.extend(
        [
            "",
            "## Evidence Files",
            "",
            f"- `{evidence_dir}/RACER_D0_SOURCE_AUDIT.json`",
            f"- `{evidence_dir}/SUMMARY.md`",
            "",
            "## Claim Boundary",
            "",
            "This package is source/static evidence only. It does not start or validate",
            "ROS, Gazebo, PX4, MAVROS, RViz, RACER runtime, or multi-UAV exploration.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="RACER source root")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="directory for audit output")
    parser.add_argument("--stamp", default=None, help="optional output timestamp")
    args = parser.parse_args()

    source = repo_path(args.source)
    output_root = repo_path(args.output_root)
    if not source.is_dir():
        raise SystemExit(f"missing RACER source root: {source}")
    stamp = args.stamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = output_root / f"racer_d0_source_audit_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    interface = collect_interface(source)
    deps = collect_dependency_hints(source)
    audit: dict[str, Any] = {
        "status": "review_ready",
        "gate": "RACER-D0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_root": rel(source),
        "evidence_dir": rel(out_dir),
        "claim_boundary": [
            "source/interface/dependency audit only",
            "no ROS/Gazebo/PX4/MAVROS/RViz runtime started",
            "no build, smoke, adapter dry-run, or multi-UAV exploration success claimed",
        ],
        "source_inventory": {
            "launch_files": collect_files(source, "*.launch") + collect_files(source, "*.xml"),
            "message_files": collect_files(source, "*.msg"),
            "service_files": collect_files(source, "*.srv"),
            "package_files": collect_files(source, "package.xml"),
            "cmake_files": collect_files(source, "CMakeLists.txt"),
        },
        "dependencies": deps,
        "interface": interface,
        "messages": collect_messages(source),
    }
    audit["findings"] = derive_findings(source, interface, deps)
    audit_path = out_dir / "RACER_D0_SOURCE_AUDIT.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = build_summary(audit)
    (out_dir / "SUMMARY.md").write_text(summary, encoding="utf-8")
    print(json.dumps({"status": "review_ready", "evidence_dir": rel(out_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
