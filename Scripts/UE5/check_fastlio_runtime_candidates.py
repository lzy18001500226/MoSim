#!/usr/bin/env python3
"""Rank local FAST-LIO/Livox runtime candidates for the MoSim Mid360 route."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "unreal_scene_mapping"
DEFAULT_CANDIDATES = (
    ROOT / "Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio",
    ROOT / "References/Lab/localization_slam/FAST_LIO",
    ROOT / "References/Lab/localization_slam/FAST-LIVO2",
    ROOT / "References/Lab/localization_slam/Point-LIO-point-lio-with-grid-map",
    ROOT / "References/Sunray/simulation/gazebo_plugin/livox_laser_simulation",
    ROOT / "References/Sunray/General_Module/sunray_planner_utils",
    ROOT / "Scripts/ros/mosim_dense_lidar_cpp",
)

DEFAULT_EXTERNAL_CANDIDATES = (
    {
        "name": "Ericsii/FAST_LIO_ROS2",
        "url": "https://github.com/Ericsii/FAST_LIO_ROS2/tree/ros2",
        "branch": "ros2",
        "role": "external_ros2_mid360_fastlio_candidate",
        "score": 90,
        "status": "not_imported_or_built_locally",
        "evidence": [
            "package.xml uses ament_cmake and depends on livox_ros_driver2",
            "launch/mapping.launch.py defaults config_file to mid360.yaml",
            "config/mid360.yaml uses /livox/lidar, /livox/imu, lidar_type=1, scan_line=4, scan_rate=10",
        ],
        "recommendation": (
            "import into ignored temp workspace first, build on ROS2 Humble with local "
            "livox_ros_driver2, then run headless Mid360 truth evaluation"
        ),
        "blockers": [
            "network_import_timeout_in_current_probe",
            "not_yet_built_in_mosim_workspace",
            "not_yet_runtime_verified_with_mosim_livox_custommsg",
        ],
    },
)

TEXT_SUFFIXES = {
    ".cpp",
    ".cc",
    ".cxx",
    ".h",
    ".hpp",
    ".py",
    ".xml",
    ".launch",
    ".rviz",
    ".yaml",
    ".yml",
    ".txt",
    ".md",
    ".cmake",
    ".msg",
}


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_text(path: Path, limit: int = 2_000_000) -> str:
    try:
        if path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def parse_package_xml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "name": None, "buildtool_depends": [], "depends": [], "parse_error": None}
    try:
        root = ET.parse(path).getroot()
        name = root.findtext("name")
        buildtools = [node.text.strip() for node in root.findall("buildtool_depend") if node.text]
        depends: list[str] = []
        for tag in ("depend", "build_depend", "build_export_depend", "exec_depend", "run_depend"):
            depends.extend(node.text.strip() for node in root.findall(tag) if node.text)
        return {
            "exists": True,
            "name": name,
            "buildtool_depends": sorted(set(buildtools)),
            "depends": sorted(set(depends)),
            "parse_error": None,
        }
    except ET.ParseError as exc:
        return {"exists": True, "name": None, "buildtool_depends": [], "depends": [], "parse_error": str(exc)}


def iter_text_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    files = []
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.name in {"CMakeLists.txt", "package.xml"} or file_path.suffix in TEXT_SUFFIXES:
            files.append(file_path)
    return files


def limited_hits(files: list[Path], pattern: str, *, limit: int = 8) -> list[str]:
    hits: list[str] = []
    for file_path in files:
        text = read_text(file_path)
        if pattern in text:
            hits.append(rel(file_path))
            if len(hits) >= limit:
                break
    return hits


def regex_hits(files: list[Path], pattern: str, *, limit: int = 8) -> list[str]:
    compiled = re.compile(pattern)
    hits: list[str] = []
    for file_path in files:
        if compiled.search(read_text(file_path)):
            hits.append(rel(file_path))
            if len(hits) >= limit:
                break
    return hits


def ros2_package_query(package_name: str | None) -> dict[str, Any]:
    if not package_name:
        return {"visible": False, "path": None, "error": "missing package name"}
    ros2 = shutil.which("ros2")
    if not ros2:
        return {"visible": False, "path": None, "error": "missing ros2 command"}
    try:
        result = subprocess.run(
            [ros2, "pkg", "prefix", package_name],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"visible": False, "path": None, "error": f"{exc.__class__.__name__}: {exc}"}
    return {
        "visible": result.returncode == 0,
        "path": result.stdout.strip() or None,
        "error": None if result.returncode == 0 else result.stderr.strip() or None,
    }


def detect_generation(package: dict[str, Any], files: list[Path]) -> str:
    deps = set(package["depends"])
    buildtools = set(package["buildtool_depends"])
    has_ament = (
        "ament_cmake" in buildtools
        or "ament_python" in buildtools
        or bool(limited_hits(files, "find_package(ament_cmake", limit=1))
        or bool(limited_hits(files, "ament_package", limit=1))
        or "rclcpp" in deps
    )
    has_catkin = (
        "catkin" in buildtools
        or bool(limited_hits(files, "find_package(catkin", limit=1))
        or "roscpp" in deps
        or "rospy" in deps
    )
    if has_ament and has_catkin:
        return "mixed_ros1_ros2"
    if has_ament:
        return "ros2_ament"
    if has_catkin:
        return "ros1_catkin"
    return "unknown"


def inspect_candidate(path: Path) -> dict[str, Any]:
    package = parse_package_xml(path / "package.xml")
    files = iter_text_files(path)
    all_text = "\n".join(read_text(file_path) for file_path in files)
    deps = set(package["depends"])
    generation = detect_generation(package, files)

    has_livox_ros1_custom = "livox_ros_driver::CustomMsg" in all_text or "livox_ros_driver/CustomMsg" in all_text
    has_livox_ros2_custom = "livox_ros_driver2::CustomMsg" in all_text or "livox_ros_driver2/msg/custom_msg" in all_text
    has_local_custom_msg = "CustomMsg.msg" in [file_path.name for file_path in files] or "livox_laser_simulation::CustomMsg" in all_text
    has_pointcloud2 = "PointCloud2" in all_text
    has_livox_fields = all(field in all_text for field in ("offset_time", "line")) and any(
        field in all_text for field in ("reflectivity", "intensity")
    )
    has_mid360_config = any(
        token in all_text
        for token in ("mapping_mid360", "mid360.yaml", "MID360_config", "mid360-real-centr.csv", "scan_line: 4")
    )
    has_sunray_scan_csv = "mid360-real-centr.csv" in all_text or (path / "scan_mode" / "mid360-real-centr.csv").exists()
    pointcloud2_livox_runtime = has_pointcloud2 and has_livox_fields
    spark_pointcloud2_blocked = "case OUST64:" in all_text and "case VELO16:" in all_text and "case AVIA:" not in all_text
    macro_typo = "LIVOXROS_DRIVER_FOUND" in all_text
    driver_name_mismatch = (
        "find_package(livox_ros_driver QUIET)" in all_text
        and ("livox_ros_driver2::msg::CustomMsg" in all_text or "livox_ros_driver2/msg/custom_msg" in all_text)
    )
    legacy_driver_header = "livox_ros_driver/CustomMsg.h" in all_text

    blockers: list[str] = []
    if not path.exists():
        blockers.append("candidate_path_missing")
    if generation == "unknown":
        blockers.append("missing_ros_package_markers")
    if generation == "ros1_catkin":
        blockers.append("requires_ros1_or_bridge_on_ubuntu_22_04")
    if spark_pointcloud2_blocked:
        blockers.append("pointcloud2_path_rejects_livox_lidar_type")
    if macro_typo:
        blockers.append("livox_custommsg_macro_typo")
    if driver_name_mismatch:
        blockers.append("livox_driver_package_name_mismatch")
    if legacy_driver_header and generation == "ros2_ament":
        blockers.append("ros2_candidate_includes_ros1_livox_header")
    if has_mid360_config and not (has_livox_ros1_custom or has_livox_ros2_custom or has_local_custom_msg or pointcloud2_livox_runtime):
        blockers.append("mid360_marker_without_livox_message_support")

    role = "unknown"
    recommendation = "audit manually before use"
    score = 0
    if path.name == "mosim_dense_lidar_cpp":
        role = "mosim_transport_probe"
        recommendation = "keep as ROS2 PointCloud2 transport/performance probe; not FAST-LIO evidence by itself"
        score = 55
    elif generation == "ros2_ament" and has_livox_ros2_custom and not blockers:
        role = "preferred_ros2_mid360_fastlio_candidate"
        recommendation = "use as preferred native ROS2 Mid360 FAST-LIO candidate after build and runtime truth evaluation"
        score = 95
    elif generation == "ros2_ament" and has_livox_ros2_custom:
        role = "ros2_candidate_needs_patch"
        recommendation = "patch Livox CustomMsg build/subscriber path before any Mid360 runtime claim"
        score = 75
    elif generation == "ros2_ament" and spark_pointcloud2_blocked:
        role = "ros2_standard_lidar_candidate_only"
        recommendation = "use only for Velodyne/Ouster smoke unless Livox CustomMsg support is repaired"
        score = 45
    elif generation == "ros1_catkin" and has_mid360_config and (has_livox_ros1_custom or has_local_custom_msg):
        role = "strong_ros1_mid360_reference"
        recommendation = "reuse config/message semantics; runtime requires ROS1 container/bridge or ROS2 port"
        score = 70
    elif has_sunray_scan_csv or has_local_custom_msg:
        role = "sensor_semantics_reference"
        recommendation = "reuse scan pattern and CustomMsg schema when implementing MoSim UE/ROS2 sensor bridge"
        score = 65
    elif pointcloud2_livox_runtime:
        role = "pointcloud2_conversion_reference"
        recommendation = "reuse conversion fields for planner/RViz path; verify target FAST-LIO accepts this PointCloud2 layout"
        score = 60

    package_name = package["name"]
    runtime_visibility = ros2_package_query(package_name) if generation == "ros2_ament" else {
        "visible": False,
        "path": None,
        "error": "not a ROS2 candidate",
    }

    return {
        "path": rel(path),
        "exists": path.exists(),
        "package": package,
        "generation": generation,
        "role": role,
        "score": score,
        "recommendation": recommendation,
        "blockers": blockers,
        "support": {
            "mid360_markers": has_mid360_config,
            "sunray_scan_csv": has_sunray_scan_csv,
            "pointcloud2": has_pointcloud2,
            "pointcloud2_livox_fields": pointcloud2_livox_runtime,
            "livox_ros_driver_custom_msg": has_livox_ros1_custom,
            "livox_ros_driver2_custom_msg": has_livox_ros2_custom,
            "local_livox_custom_msg": has_local_custom_msg,
            "spark_pointcloud2_livox_blocked": spark_pointcloud2_blocked,
            "livox_custommsg_macro_typo": macro_typo,
            "livox_driver_package_name_mismatch": driver_name_mismatch,
            "ros2_candidate_includes_ros1_livox_header": legacy_driver_header and generation == "ros2_ament",
        },
        "evidence": {
            "custom_msg": sorted(set(
                limited_hits(files, "CustomMsg", limit=8)
                + limited_hits(files, "custom_msg", limit=8)
            ))[:8],
            "mid360": sorted(set(
                regex_hits(files, r"mid360|MID360|mapping_mid360|scan_line:\s*4", limit=8)
            ))[:8],
            "pointcloud2": limited_hits(files, "PointCloud2", limit=8),
        },
        "ros2_runtime_visibility": runtime_visibility,
    }


def build_report(paths: list[Path], external_candidates: tuple[dict[str, Any], ...] = DEFAULT_EXTERNAL_CANDIDATES) -> dict[str, Any]:
    candidates = [inspect_candidate(path) for path in paths]
    ranked = sorted(candidates, key=lambda item: (-item["score"], item["path"]))
    preferred = [item for item in ranked if item["role"] == "preferred_ros2_mid360_fastlio_candidate"]
    patchable = [item for item in ranked if item["role"] == "ros2_candidate_needs_patch"]
    ros1_refs = [item for item in ranked if item["role"] == "strong_ros1_mid360_reference"]
    sensor_refs = [item for item in ranked if item["role"] in {"sensor_semantics_reference", "pointcloud2_conversion_reference"}]
    degraded_only = [item for item in ranked if item["role"] == "ros2_standard_lidar_candidate_only"]
    external_ranked = sorted(external_candidates, key=lambda item: (-int(item["score"]), item["name"]))

    if preferred:
        decision = "use_preferred_ros2_mid360_fastlio_candidate"
        next_action = "build/run the preferred candidate with MoSim dense Mid360 input and truth evaluation"
    elif external_ranked:
        decision = "evaluate_external_ros2_mid360_fastlio_candidate_first"
        next_action = (
            "import the best external ROS2 Mid360 FAST-LIO candidate into ignored temp workspace, "
            "build it with ROS2 Humble and local livox_ros_driver2, then run headless truth evaluation"
        )
    elif patchable:
        decision = "patch_ros2_livox_custommsg_candidate_first"
        next_action = "repair Livox CustomMsg build/subscriber path, then run headless FAST-LIO truth evaluation"
    elif ros1_refs:
        decision = "use_ros1_mid360_reference_or_bridge_until_ros2_candidate_exists"
        next_action = "port ROS1 Mid360 semantics to ROS2 or run an approved ROS1 bridge/container route"
    else:
        decision = "no_mid360_fastlio_runtime_candidate_ready"
        next_action = "bring in a ROS2 Humble FAST-LIO/Livox candidate before localization claims"

    return {
        "schema": "mosim.fastlio_runtime_candidates.v1",
        "decision": decision,
        "next_action": next_action,
        "candidate_count": len(candidates),
        "preferred_ros2_mid360_count": len(preferred),
        "patchable_ros2_livox_count": len(patchable),
        "strong_ros1_mid360_reference_count": len(ros1_refs),
        "sensor_reference_count": len(sensor_refs),
        "degraded_standard_lidar_only_count": len(degraded_only),
        "ranked_candidates": ranked,
        "external_candidate_count": len(external_ranked),
        "external_candidates": external_ranked,
        "claim_boundary": [
            "A candidate is not localization evidence until it publishes FAST-LIO odometry/path/registered cloud at runtime.",
            "Velodyne/Ouster PointCloud2 smoke does not satisfy the MoSim Mid360/Livox evidence contract.",
            "MoSim Mid360 evidence requires coherent LiDAR, IMU, TF timestamps, per-point timing, and truth-error evaluation.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# FAST-LIO Runtime Candidate Decision",
        "",
        f"- decision: `{report['decision']}`",
        f"- next_action: {report['next_action']}",
        f"- candidate_count: `{report['candidate_count']}`",
        f"- preferred_ros2_mid360_count: `{report['preferred_ros2_mid360_count']}`",
        f"- patchable_ros2_livox_count: `{report['patchable_ros2_livox_count']}`",
        f"- strong_ros1_mid360_reference_count: `{report['strong_ros1_mid360_reference_count']}`",
        f"- external_candidate_count: `{report['external_candidate_count']}`",
        "",
        "## Ranked Candidates",
        "",
        "| Score | Path | Generation | Role | Blockers | Recommendation |",
        "|---:|---|---|---|---|---|",
    ]
    for item in report["ranked_candidates"]:
        blockers = ", ".join(f"`{blocker}`" for blocker in item["blockers"]) or "none"
        lines.append(
            f"| {item['score']} | `{item['path']}` | `{item['generation']}` | `{item['role']}` | "
            f"{blockers} | {item['recommendation']} |"
        )
    lines.extend(["", "## External Candidates To Import First", ""])
    lines.append("| Score | Candidate | Branch | Status | Blockers | Recommendation |")
    lines.append("|---:|---|---|---|---|---|")
    for item in report["external_candidates"]:
        blockers = ", ".join(f"`{blocker}`" for blocker in item["blockers"]) or "none"
        lines.append(
            f"| {item['score']} | `{item['name']}` | `{item['branch']}` | `{item['status']}` | "
            f"{blockers} | {item['recommendation']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Critical Finding", ""])
    lines.extend(
        [
            "The current `spark-fast-lio` source is a useful ROS2 FAST-LIO2-family base,",
            "but it is not ready for Mid360 evidence. Its standard `PointCloud2` path",
            "handles Ouster/Kimera/Velodyne-style cases, while the Livox path is guarded",
            "behind CustomMsg support and currently shows driver-name and macro-name",
            "mismatches that must be patched before a Mid360 run can be claimed.",
            "",
            "The next attempt should evaluate the external `Ericsii/FAST_LIO_ROS2`",
            "`ros2` branch before spending more engineering time patching `spark-fast-lio`,",
            "because its visible ROS2 branch already declares `ament_cmake`,",
            "`livox_ros_driver2`, and a Mid360 launch/config path. It is still not",
            "local evidence until it builds and publishes runtime FAST-LIO outputs.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Project-local runtime candidate paths")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail when no preferred ROS2 Mid360 candidate is ready")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [project_path(path) for path in args.paths] if args.paths else list(DEFAULT_CANDIDATES)
    report = build_report(paths)
    if args.write:
        output_root = project_path(args.output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "FASTLIO_RUNTIME_CANDIDATES.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_markdown(output_root / "FASTLIO_RUNTIME_CANDIDATES.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.strict and report["preferred_ros2_mid360_count"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
