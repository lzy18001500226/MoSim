#!/usr/bin/env python3
"""Check ROS/RViz/FAST-LIO runtime environment for the UE UAV platform.

This check is non-invasive: it does not install packages, start roscore,
launch RViz, or run FAST-LIO. It reports what must be sourced/fixed before the
native mapping window can be treated as runtime evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
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
        "ros2",
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


def ros2_package_query(package_name: str, commands: dict[str, str | None]) -> dict[str, Any]:
    ros2 = commands.get("ros2")
    if not ros2:
        return {
            "package": package_name,
            "visible": False,
            "path": None,
            "error": "missing ros2; source ROS2 setup.bash first",
        }
    result = run_quiet([ros2, "pkg", "prefix", package_name])
    return {
        "package": package_name,
        "visible": bool(result.get("ok")),
        "path": result.get("stdout") if result.get("ok") else None,
        "error": None if result.get("ok") else result.get("stderr") or result.get("error"),
    }


def ros_generation(ros_distro: str | None) -> str:
    if ros_distro in {"humble", "iron", "jazzy", "kilted", "rolling"}:
        return "ros2"
    if ros_distro in {"melodic", "noetic"}:
        return "ros1"
    return "unknown"


def load_fastlio_compatibility_module() -> Any:
    path = ROOT / "Scripts/UE5/check_fastlio_family_compatibility.py"
    spec = importlib.util.spec_from_file_location("check_fastlio_family_compatibility", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    commands = command_map()
    commands["rospack"] = shutil.which("rospack")
    ros_distro = os.environ.get("ROS_DISTRO")
    generation = ros_generation(ros_distro)
    ros_package_path = os.environ.get("ROS_PACKAGE_PATH")
    ros_master_uri = os.environ.get("ROS_MASTER_URI")
    fast_lio_reference = ROOT / "References/Lab/FAST_LIO/package.xml"
    project_rviz_pointcloud_config = ROOT / "Config/rviz/mosim_uav_fastlio_pointcloud.rviz"
    project_rviz2_pointcloud_config = ROOT / "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz"
    bootstrap_script = ROOT / "Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh"
    factory_headless_script = ROOT / "Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh"
    run_launch_ros2_script = ROOT / "Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh"
    launch_package_xml = ROOT / "Scripts/ros/mosim_scene_replay/package.xml"
    launch_file = ROOT / "Scripts/ros/mosim_scene_replay/launch/mosim_scene_replay.launch.py"
    check_fastlio_ros2_script = ROOT / "Scripts/UE5/check_fastlio_ros2_topics.sh"
    mworks_uav_bridge = ROOT / "Scripts/ros/publish_mworks_uav_state_ros2.py"
    ros1_command_set = ("roscore", "roslaunch", "rostopic", "rosnode", "rosparam", "rviz", "python3")
    ros1_commands_ready = all(commands.get(name) for name in ros1_command_set)
    ros2_command_set = ("ros2", "rviz2", "colcon", "python3")
    ros2_commands_ready = all(commands.get(name) for name in ros2_command_set)
    catkin_ready = bool(commands.get("catkin_make") or commands.get("catkin"))
    fast_lio_pkg = package_query(args.fast_lio_package, commands)
    ros2_packages = {
        name: ros2_package_query(name, commands)
        for name in ("rviz2", "sensor_msgs", "nav_msgs", "geometry_msgs", "tf2_ros")
    }
    ros2_packages_ready = all(payload["visible"] for payload in ros2_packages.values())
    fastlio_module = load_fastlio_compatibility_module()
    fastlio_compatibility = fastlio_module.build_report(list(fastlio_module.DEFAULT_CANDIDATES))
    ros1_ready = ros1_commands_ready and catkin_ready and fast_lio_pkg["visible"]
    ros2_replay_ready = ros2_commands_ready and ros2_packages_ready
    blockers: list[str] = []
    degraded: list[str] = []
    if not ros1_commands_ready:
        missing = [name for name in ros1_command_set if not commands.get(name)]
        degraded.append("missing_ros1_commands:" + ",".join(missing))
    if not catkin_ready:
        degraded.append("missing_catkin_build_tool")
    if not ros_distro:
        blockers.append("ros_environment_not_sourced")
    if generation == "ros1":
        blockers.append(f"unsupported_primary_ros_generation_for_ubuntu_2204:{ros_distro}")
    if not ros2_commands_ready:
        missing = [name for name in ros2_command_set if not commands.get(name)]
        blockers.append("missing_ros2_commands:" + ",".join(missing))
    if not ros2_packages_ready:
        missing = [name for name, payload in ros2_packages.items() if not payload["visible"]]
        blockers.append("missing_ros2_packages:" + ",".join(missing))
    if not fast_lio_reference.exists():
        blockers.append("missing_fast_lio_reference_repo")
    if not fast_lio_pkg["visible"]:
        degraded.append(f"fast_lio_ros1_package_not_visible:{args.fast_lio_package}")
    if fastlio_compatibility["ros2_candidate_count"] == 0:
        degraded.append("no_local_ros2_fastlio_family_source")
    elif not fastlio_compatibility["can_claim_fastlio_ros2_runtime"]:
        degraded.append("ros2_fastlio_candidates_not_built_or_not_sourced")
    if not project_rviz_pointcloud_config.exists():
        degraded.append("missing_mosim_rviz_pointcloud_config")
    if not project_rviz2_pointcloud_config.exists():
        blockers.append("missing_mosim_rviz2_pointcloud_config")
    if not factory_headless_script.exists():
        blockers.append("missing_factory_fastlio_mid360_headless_ros2_script")
    if not mworks_uav_bridge.exists():
        blockers.append("missing_mworks_uav_state_ros2_bridge")
    if not run_launch_ros2_script.exists():
        blockers.append("missing_run_mosim_scene_replay_launch_ros2_script")
    if not launch_package_xml.exists():
        blockers.append("missing_mosim_scene_replay_ros2_package")
    if not launch_file.exists():
        blockers.append("missing_mosim_scene_replay_launch_file")
    if not check_fastlio_ros2_script.exists():
        blockers.append("missing_check_fastlio_ros2_topics_script")

    return {
        "schema": "mosim.ros_fastlio_platform_runtime_env.v1",
        "ready_for_native_fastlio_platform_runtime": not blockers,
        "ready_for_native_mapping_runtime": not blockers,
        "blockers": blockers,
        "degraded": degraded,
        "ros_generation": generation,
        "ros2_replay_ready": ros2_replay_ready,
        "fastlio_ros2_runtime_claimable": fastlio_compatibility["can_claim_fastlio_ros2_runtime"],
        "ros1_fastlio_reference_ready": ros1_ready,
        "environment": {
            "ROS_DISTRO": ros_distro,
            "ROS_MASTER_URI": ros_master_uri,
            "ROS_PACKAGE_PATH_set": bool(ros_package_path),
            "ROS_PACKAGE_PATH_preview": ros_package_path[:1000] if ros_package_path else None,
        },
        "commands": commands,
        "packages": {
            args.fast_lio_package: fast_lio_pkg,
            "ros2": ros2_packages,
        },
        "fastlio_family_compatibility": fastlio_compatibility,
        "project_assets": {
            "fast_lio_reference_package_xml": {
                "path": rel(fast_lio_reference),
                "exists": fast_lio_reference.exists(),
            },
            "rviz_fastlio_pointcloud_config": {
                "path": rel(project_rviz_pointcloud_config),
                "exists": project_rviz_pointcloud_config.exists(),
            },
            "rviz2_fastlio_pointcloud_config": {
                "path": rel(project_rviz2_pointcloud_config),
                "exists": project_rviz2_pointcloud_config.exists(),
            },
            "fastlio_workspace_bootstrap": {
                "path": rel(bootstrap_script),
                "exists": bootstrap_script.exists(),
            },
            "factory_fastlio_mid360_headless_ros2": {
                "path": rel(factory_headless_script),
                "exists": factory_headless_script.exists(),
            },
            "mworks_uav_state_ros2_bridge": {
                "path": rel(mworks_uav_bridge),
                "exists": mworks_uav_bridge.exists(),
            },
            "run_mosim_scene_replay_launch_ros2": {
                "path": rel(run_launch_ros2_script),
                "exists": run_launch_ros2_script.exists(),
            },
            "mosim_scene_replay_ros2_package": {
                "path": rel(launch_package_xml),
                "exists": launch_package_xml.exists(),
            },
            "mosim_scene_replay_launch_file": {
                "path": rel(launch_file),
                "exists": launch_file.exists(),
            },
            "check_fastlio_ros2_topics": {
                "path": rel(check_fastlio_ros2_script),
                "exists": check_fastlio_ros2_script.exists(),
            },
        },
        "recommended_setup_sequence": [
            "Use Ubuntu 22.04 with ROS2 Humble as the primary runtime.",
            "source /opt/ros/humble/setup.bash",
            "Run Scripts/UE5/check_ros_mapping_runtime_env.py --write again.",
            "Run python3 Scripts/ros/publish_mworks_uav_state_ros2.py --dry-run with the Factory MWORKS raw CSV and Livox-like frames.",
            "Run DRY_RUN=1 Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh for the Factory FAST-LIO headless gate.",
            "Run Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh factoryenvironmentcollect to validate the package-style ROS2 launch path.",
            "Run Scripts/UE5/check_fastlio_ros2_topics.sh during the live ROS2 run.",
            "Run Scripts/UE5/check_fastlio_family_compatibility.py --write after adding or changing FAST-LIO-family sources.",
            "Treat local References/Lab/FAST_LIO as ROS1-only until a ROS2 FAST-LIO/FAST-LIO2 package is added or a containerized ROS1 bridge route is approved.",
        ],
        "claim_boundary": [
            "This is only an environment preflight; it does not prove FAST-LIO runtime evidence.",
            "Runtime evidence still requires live ROS topics, RViz visibility, recording, and FAST-LIO evaluation.",
            "HTML is not an accepted active point-cloud/map review window.",
            "Keyboard/mouse input is accepted only for UE/RViz view control; it must not drive UAV pose.",
            "On Ubuntu 22.04, ROS2/RViz2 is the primary runtime. ROS1/Catkin FAST-LIO blockers are degraded compatibility blockers, not blockers for ROS2 replay input review.",
            "Do not claim FAST-LIO localization until a real ROS2 FAST-LIO-family package publishes /cloud_registered and /Odometry, or an approved ROS1 bridge route records equivalent outputs.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# ROS FAST-LIO Platform Runtime Environment",
        "",
        f"- ready_for_native_fastlio_platform_runtime: `{str(report['ready_for_native_fastlio_platform_runtime']).lower()}`",
        f"- blockers: {', '.join(f'`{item}`' for item in report['blockers']) or 'none'}",
        f"- degraded: {', '.join(f'`{item}`' for item in report.get('degraded', [])) or 'none'}",
        f"- ros_generation: `{report['ros_generation']}`",
        f"- ros2_replay_ready: `{str(report['ros2_replay_ready']).lower()}`",
        f"- fastlio_ros2_runtime_claimable: `{str(report['fastlio_ros2_runtime_claimable']).lower()}`",
        f"- ROS_DISTRO: `{report['environment']['ROS_DISTRO']}`",
        f"- ROS_MASTER_URI: `{report['environment']['ROS_MASTER_URI']}`",
        "",
        "Commands:",
    ]
    for name, value in report["commands"].items():
        lines.append(f"- `{name}`: `{value}`")
    lines.extend(["", "Packages:"])
    for name, payload in report["packages"].items():
        if name == "ros2":
            for package_name, ros2_payload in payload.items():
                lines.append(
                    f"- `ros2:{package_name}`: visible=`{str(ros2_payload['visible']).lower()}`, "
                    f"path=`{ros2_payload['path']}`"
                )
                if ros2_payload.get("error"):
                    lines.append(f"  error: `{ros2_payload['error']}`")
            continue
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
