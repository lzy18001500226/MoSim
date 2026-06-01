#!/usr/bin/env python3
"""Check ROS/RViz/FAST-LIO runtime environment for UE scene mapping.

This check is non-invasive: it does not install packages, start roscore,
launch RViz, or run FAST-LIO. It reports what must be sourced/fixed before the
native mapping window can be treated as runtime evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"


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


def command_map() -> dict[str, str | None]:
    names = (
        "roscore",
        "roslaunch",
        "rostopic",
        "rosnode",
        "rosparam",
        "rviz",
        "rviz2",
        "catkin_make",
        "catkin",
        "colcon",
        "python3",
    )
    return {name: shutil.which(name) for name in names}


def run_quiet(command: list[str], timeout_s: float = 5.0) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            check=False,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[:4000],
            "stderr": result.stderr.strip()[:4000],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": f"{exc.__class__.__name__}: {exc}"}


def package_query(package_name: str, commands: dict[str, str | None]) -> dict[str, Any]:
    if not commands.get("rospack"):
        # rospack is not in command_map on purpose; resolve lazily so a missing
        # ROS install is reported as a package visibility issue, not a hard
        # Python error.
        rospack = shutil.which("rospack")
    else:
        rospack = commands["rospack"]
    if not rospack:
        return {
            "package": package_name,
            "visible": False,
            "path": None,
            "error": "missing rospack; source ROS1 setup.bash first",
        }
    result = run_quiet([rospack, "find", package_name])
    return {
        "package": package_name,
        "visible": bool(result.get("ok")),
        "path": result.get("stdout") if result.get("ok") else None,
        "error": None if result.get("ok") else result.get("stderr") or result.get("error"),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    commands = command_map()
    commands["rospack"] = shutil.which("rospack")
    ros_distro = os.environ.get("ROS_DISTRO")
    ros_package_path = os.environ.get("ROS_PACKAGE_PATH")
    ros_master_uri = os.environ.get("ROS_MASTER_URI")
    fast_lio_reference = ROOT / "References/Lab/FAST_LIO/package.xml"
    project_rviz_config = ROOT / "Config/rviz/mosim_uav_mapping.rviz"
    bootstrap_script = ROOT / "Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh"
    ros1_command_set = ("roscore", "roslaunch", "rostopic", "rosnode", "rosparam", "rviz", "python3")
    ros1_commands_ready = all(commands.get(name) for name in ros1_command_set)
    catkin_ready = bool(commands.get("catkin_make") or commands.get("catkin"))
    fast_lio_pkg = package_query(args.fast_lio_package, commands)
    ros1_ready = ros1_commands_ready and catkin_ready and fast_lio_pkg["visible"]
    blockers: list[str] = []
    if not ros1_commands_ready:
        missing = [name for name in ros1_command_set if not commands.get(name)]
        blockers.append("missing_ros1_commands:" + ",".join(missing))
    if not catkin_ready:
        blockers.append("missing_catkin_build_tool")
    if not ros_distro:
        blockers.append("ros_environment_not_sourced")
    if not fast_lio_reference.exists():
        blockers.append("missing_fast_lio_reference_repo")
    if not fast_lio_pkg["visible"]:
        blockers.append(f"fast_lio_package_not_visible:{args.fast_lio_package}")
    if not project_rviz_config.exists():
        blockers.append("missing_mosim_rviz_config")

    return {
        "schema": "mosim.ros_mapping_runtime_env.v1",
        "ready_for_native_mapping_runtime": not blockers,
        "blockers": blockers,
        "environment": {
            "ROS_DISTRO": ros_distro,
            "ROS_MASTER_URI": ros_master_uri,
            "ROS_PACKAGE_PATH_set": bool(ros_package_path),
            "ROS_PACKAGE_PATH_preview": ros_package_path[:1000] if ros_package_path else None,
        },
        "commands": commands,
        "packages": {
            args.fast_lio_package: fast_lio_pkg,
        },
        "project_assets": {
            "fast_lio_reference_package_xml": {
                "path": rel(fast_lio_reference),
                "exists": fast_lio_reference.exists(),
            },
            "rviz_config": {
                "path": rel(project_rviz_config),
                "exists": project_rviz_config.exists(),
            },
            "fastlio_workspace_bootstrap": {
                "path": rel(bootstrap_script),
                "exists": bootstrap_script.exists(),
            },
        },
        "recommended_setup_sequence": [
            "Install or open a WSL environment with ROS1 Noetic-compatible tools.",
            "source /opt/ros/noetic/setup.bash",
            "Run Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh to wire References/Lab/FAST_LIO into Results/tmp/fastlio_ros1_ws and build it.",
            "source Results/tmp/fastlio_ros1_ws/devel/setup.bash",
            "Run Scripts/UE5/check_ros_mapping_runtime_env.py --write again.",
            "Run Scripts/UE5/run_fastlio_rviz_replay_ros1.sh <scene>.",
            "Run Scripts/UE5/check_fastlio_ros1_topics.sh during the live run.",
        ],
        "claim_boundary": [
            "This is only an environment preflight; it does not prove mapping runtime evidence.",
            "Runtime evidence still requires live ROS topics, RViz visibility, recording, and FAST-LIO evaluation.",
            "HTML is not an accepted active point-cloud/map review window.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# ROS Mapping Runtime Environment",
        "",
        f"- ready_for_native_mapping_runtime: `{str(report['ready_for_native_mapping_runtime']).lower()}`",
        f"- blockers: {', '.join(f'`{item}`' for item in report['blockers']) or 'none'}",
        f"- ROS_DISTRO: `{report['environment']['ROS_DISTRO']}`",
        f"- ROS_MASTER_URI: `{report['environment']['ROS_MASTER_URI']}`",
        "",
        "Commands:",
    ]
    for name, value in report["commands"].items():
        lines.append(f"- `{name}`: `{value}`")
    lines.extend(["", "Packages:"])
    for name, payload in report["packages"].items():
        lines.append(f"- `{name}`: visible=`{str(payload['visible']).lower()}`, path=`{payload['path']}`")
        if payload.get("error"):
            lines.append(f"  error: `{payload['error']}`")
    lines.extend(["", "Recommended setup sequence:"])
    for item in report["recommended_setup_sequence"]:
        lines.append(f"- {item}")
    lines.extend(["", "Claim boundary:"])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--fast-lio-package", default="fast_lio")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.write:
        output_root = project_path(args.output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / "ROS_MAPPING_RUNTIME_ENV.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_markdown(output_root / "ROS_MAPPING_RUNTIME_ENV.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_blocker and report["blockers"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
