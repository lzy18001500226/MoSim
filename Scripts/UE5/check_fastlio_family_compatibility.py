#!/usr/bin/env python3
"""Inspect local FAST-LIO-family sources for ROS2 compatibility evidence.

This script is intentionally non-invasive. It does not build packages, launch
ROS, download sources, or open RViz. It turns local package metadata into an
auditable answer for the current Ubuntu 22.04 / ROS2 Humble route.
"""

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
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_CANDIDATES = (
    ROOT / "References/Lab/localization_slam/FAST_LIO",
    ROOT / "References/Lab/localization_slam/FAST-LIVO2",
    ROOT / "References/Lab/localization_slam/Point-LIO-point-lio-with-grid-map",
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
}
TOPIC_PATTERN = re.compile(
    r"(/(?:cloud_registered|Odometry|path|velodyne_points|imu/data|livox/lidar|livox/imu|Laser_map))"
)


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


def read_text(path: Path, limit: int = 1_000_000) -> str:
    try:
        if path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def parse_package_xml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "name": None,
            "buildtool_depends": [],
            "depends": [],
            "parse_error": None,
        }
    try:
        root = ET.parse(path).getroot()
        name = root.findtext("name")
        buildtool_depends = [node.text.strip() for node in root.findall("buildtool_depend") if node.text]
        depend_tags = [
            "depend",
            "build_depend",
            "build_export_depend",
            "exec_depend",
            "run_depend",
        ]
        depends: list[str] = []
        for tag in depend_tags:
            depends.extend(node.text.strip() for node in root.findall(tag) if node.text)
        return {
            "exists": True,
            "name": name,
            "buildtool_depends": sorted(set(buildtool_depends)),
            "depends": sorted(set(depends)),
            "parse_error": None,
        }
    except ET.ParseError as exc:
        return {
            "exists": True,
            "name": None,
            "buildtool_depends": [],
            "depends": [],
            "parse_error": str(exc),
        }


def list_files(path: Path) -> dict[str, list[str]]:
    launch_xml: list[str] = []
    launch_py: list[str] = []
    rviz: list[str] = []
    cmake: list[str] = []
    package_xml: list[str] = []
    if not path.exists():
        return {
            "package_xml": [],
            "cmake": [],
            "launch_xml": [],
            "launch_py": [],
            "rviz": [],
        }
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
        name = file_path.name
        if name == "package.xml":
            package_xml.append(rel(file_path))
        elif name == "CMakeLists.txt" or name.endswith(".cmake"):
            cmake.append(rel(file_path))
        elif name.endswith(".launch.py"):
            launch_py.append(rel(file_path))
        elif name.endswith(".launch"):
            launch_xml.append(rel(file_path))
        elif name.endswith(".rviz"):
            rviz.append(rel(file_path))
    return {
        "package_xml": sorted(package_xml),
        "cmake": sorted(cmake),
        "launch_xml": sorted(launch_xml),
        "launch_py": sorted(launch_py),
        "rviz": sorted(rviz),
    }


def scan_text_evidence(path: Path) -> dict[str, Any]:
    evidence = {
        "find_package_catkin": [],
        "find_package_ament_cmake": [],
        "ament_package": [],
        "roscpp_include_or_depend": [],
        "rclcpp_include_or_depend": [],
        "topics": {},
    }
    if not path.exists():
        return evidence
    topic_hits: dict[str, list[str]] = {}
    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.name != "CMakeLists.txt" and file_path.suffix not in TEXT_SUFFIXES:
            continue
        text = read_text(file_path)
        if not text:
            continue
        rel_path = rel(file_path)
        if "find_package(catkin" in text:
            evidence["find_package_catkin"].append(rel_path)
        if "find_package(ament_cmake" in text:
            evidence["find_package_ament_cmake"].append(rel_path)
        if "ament_package(" in text or "ament_package()" in text:
            evidence["ament_package"].append(rel_path)
        if "roscpp" in text or "#include <ros/" in text:
            evidence["roscpp_include_or_depend"].append(rel_path)
        if "rclcpp" in text or "#include <rclcpp/" in text:
            evidence["rclcpp_include_or_depend"].append(rel_path)
        for topic in TOPIC_PATTERN.findall(text):
            topic_hits.setdefault(topic, []).append(rel_path)
    evidence["topics"] = {topic: sorted(set(paths))[:8] for topic, paths in sorted(topic_hits.items())}
    for key in (
        "find_package_catkin",
        "find_package_ament_cmake",
        "ament_package",
        "roscpp_include_or_depend",
        "rclcpp_include_or_depend",
    ):
        evidence[key] = sorted(set(evidence[key]))[:12]
    return evidence


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


def inspect_candidate(path: Path) -> dict[str, Any]:
    package_xml = parse_package_xml(path / "package.xml")
    files = list_files(path)
    text_evidence = scan_text_evidence(path)
    deps = set(package_xml["depends"])
    buildtools = set(package_xml["buildtool_depends"])
    has_catkin = (
        "catkin" in buildtools
        or bool(text_evidence["find_package_catkin"])
        or "roscpp" in deps
        or "rospy" in deps
    )
    has_ament = (
        "ament_cmake" in buildtools
        or "ament_python" in buildtools
        or bool(text_evidence["find_package_ament_cmake"])
        or bool(text_evidence["ament_package"])
    )
    has_rclcpp = "rclcpp" in deps or bool(text_evidence["rclcpp_include_or_depend"])
    has_ros2_launch = bool(files["launch_py"])
    has_ros1_launch = bool(files["launch_xml"])

    if has_ament or has_rclcpp or has_ros2_launch:
        if has_catkin and not has_ament:
            verdict = "mixed_needs_manual_review"
        else:
            verdict = "ros2_candidate"
    elif has_catkin or has_ros1_launch:
        verdict = "ros1_catkin_only"
    elif path.exists():
        verdict = "unknown_no_ros_metadata"
    else:
        verdict = "missing"

    blockers: list[str] = []
    if verdict == "ros1_catkin_only":
        blockers.extend(["catkin_buildtool", "roscpp_rospy_tf_dependencies", "ros1_launch_files"])
    elif verdict == "mixed_needs_manual_review":
        blockers.append("mixed_ros1_ros2_markers")
    elif verdict == "unknown_no_ros_metadata":
        blockers.append("missing_recognized_ros_package_markers")
    elif verdict == "missing":
        blockers.append("candidate_path_missing")

    package_name = package_xml["name"]
    runtime_visibility = ros2_package_query(package_name) if verdict == "ros2_candidate" else {
        "visible": False,
        "path": None,
        "error": "not a ROS2 candidate",
    }
    return {
        "path": rel(path),
        "exists": path.exists(),
        "package": package_xml,
        "files": files,
        "markers": {
            "has_catkin": has_catkin,
            "has_ament": has_ament,
            "has_rclcpp": has_rclcpp,
            "has_ros1_launch_xml": has_ros1_launch,
            "has_ros2_launch_py": has_ros2_launch,
        },
        "topics_found": text_evidence["topics"],
        "text_evidence": {
            key: value
            for key, value in text_evidence.items()
            if key != "topics"
        },
        "verdict": verdict,
        "blockers": blockers,
        "ros2_runtime_visibility": runtime_visibility,
    }


def build_report(paths: list[Path]) -> dict[str, Any]:
    candidates = [inspect_candidate(path) for path in paths]
    ros2_candidates = [item for item in candidates if item["verdict"] == "ros2_candidate"]
    ros1_only = [item for item in candidates if item["verdict"] == "ros1_catkin_only"]
    mixed = [item for item in candidates if item["verdict"] == "mixed_needs_manual_review"]
    runtime_visible = [
        item
        for item in ros2_candidates
        if item["ros2_runtime_visibility"].get("visible")
    ]
    no_ros2_local_candidate = not ros2_candidates
    degradation = []
    if no_ros2_local_candidate:
        degradation.append("no_local_ros2_fastlio_family_source")
    if ros1_only:
        degradation.append("local_fastlio_family_sources_are_ros1_catkin")
    if mixed:
        degradation.append("mixed_fastlio_family_sources_need_manual_review")
    if ros2_candidates and not runtime_visible:
        degradation.append("ros2_fastlio_candidates_not_built_or_not_sourced")

    return {
        "schema": "mosim.fastlio_family_compatibility.v1",
        "can_claim_fastlio_ros2_runtime": bool(runtime_visible),
        "ros2_candidate_count": len(ros2_candidates),
        "ros1_catkin_only_count": len(ros1_only),
        "mixed_candidate_count": len(mixed),
        "degradation": degradation,
        "candidates": candidates,
        "claim_boundary": [
            "This scan only inspects local source metadata and ROS2 package visibility.",
            "It does not build FAST-LIO, launch ROS, record topics, or evaluate localization.",
            "FAST-LIO localization remains unclaimed until a real runtime publishes /cloud_registered and /Odometry and is recorded/evaluated.",
        ],
        "recommended_next_actions": [
            "Keep ROS2/RViz2 replay as the primary Ubuntu 22.04 map-review route.",
            "Add or review a ROS2 Humble FAST-LIO-family package before enabling START_FASTLIO=1 in the ROS2 wrapper.",
            "If using the current local ROS1/Catkin sources, use an explicitly approved ROS1 bridge/container route and record equivalent output topics.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# FAST-LIO Family Compatibility",
        "",
        f"- can_claim_fastlio_ros2_runtime: `{str(report['can_claim_fastlio_ros2_runtime']).lower()}`",
        f"- ros2_candidate_count: `{report['ros2_candidate_count']}`",
        f"- ros1_catkin_only_count: `{report['ros1_catkin_only_count']}`",
        f"- mixed_candidate_count: `{report['mixed_candidate_count']}`",
        f"- degradation: {', '.join(f'`{item}`' for item in report['degradation']) or 'none'}",
        "",
        "## Candidates",
        "",
        "| Path | Package | Verdict | Key Markers | Topics Found |",
        "|---|---|---|---|---|",
    ]
    for item in report["candidates"]:
        markers = [
            name
            for name, enabled in item["markers"].items()
            if enabled
        ]
        topics = ", ".join(sorted(item["topics_found"])) or "none"
        lines.append(
            f"| `{item['path']}` | `{item['package']['name']}` | `{item['verdict']}` | "
            f"{', '.join(markers) or 'none'} | {topics} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Recommended Next Actions", ""])
    for item in report["recommended_next_actions"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Project-local FAST-LIO-family source paths")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-if-no-ros2-candidate", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [project_path(path) for path in args.paths] if args.paths else list(DEFAULT_CANDIDATES)
    report = build_report(paths)
    if args.write:
        output_root = project_path(args.output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "FASTLIO_FAMILY_COMPATIBILITY.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_markdown(output_root / "FASTLIO_FAMILY_COMPATIBILITY.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_if_no_ros2_candidate and report["ros2_candidate_count"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
