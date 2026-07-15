#!/usr/bin/env python3
"""Compile and run the G9.6 smooth robust DFBC static controller gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import time
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def windows_path_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return resolved.as_posix()
    tail = resolved.relative_to(resolved.anchor).as_posix()
    return f"/mnt/{drive}/{tail}"


def run_wsl(command: list[str], cwd: Path, stdout: Path, stderr: Path) -> int:
    shell_command = " ".join(shlex.quote(item) for item in command)
    wrapped = [
        "wsl",
        "-d",
        "Ubuntu-20.04",
        "bash",
        "-lc",
        f"cd {shlex.quote(windows_path_to_wsl(cwd))} && {shell_command}",
    ]
    with stdout.open("w", encoding="utf-8", newline="\n") as out, stderr.open("w", encoding="utf-8", newline="\n") as err:
        proc = subprocess.run(wrapped, cwd=str(cwd), stdout=out, stderr=err, text=True)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default="C:/Users/HP/Desktop/MoSim")
    parser.add_argument("--result-dir", default="")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    script_dir = project_root / "Scripts" / "sunray" / "px4ctrl_golden_slice"
    if args.result_dir:
        result_dir = Path(args.result_dir).resolve()
    else:
        result_dir = project_root / "Results" / "g9" / "dfbc_smooth_robust_attitude_thrust_v1" / f"g96_static_gate_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir.mkdir(parents=True, exist_ok=True)
    build_dir = result_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    source_files = [
        script_dir / "px4ctrl_core.h",
        script_dir / "px4ctrl_core.cpp",
        script_dir / "px4ctrl_g96_dfbc_smooth_robust_gate.cpp",
        Path(__file__).resolve(),
        project_root / "Docs" / "Design" / "需求.md",
        project_root / "Docs" / "Design" / "架构.md",
        project_root / "Docs" / "Design" / "架构" / "00_架构与任务" / "任务路线图.md",
        project_root / "Docs" / "Design" / "架构" / "01_控制器平台" / "controllers" / "DFBC.md",
        project_root / "Docs" / "Design" / "架构" / "01_控制器平台" / "控制增强与容错.md",
        project_root / "Docs" / "Paper" / "Quadrotor Trajectory Tracking Under Unknown Wind Disturbances via Differential Flatness and Smooth Bounded Robust Control.pdf",
        project_root / "References" / "Lab" / "Diff-Planner" / "src" / "diff_planner" / "plan_manage" / "src" / "traj_server.cpp",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "controller.cpp",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "controller.h",
    ]
    source_hashes = {
        str(path.relative_to(project_root)): sha256(path)
        for path in source_files
        if path.exists() and path.is_file()
    }
    (result_dir / "source_hashes.json").write_text(
        json.dumps(source_hashes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    exe = build_dir / "px4ctrl_g96_dfbc_smooth_robust_gate"
    compile_cmd = [
        "g++",
        "-std=c++11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-pedantic",
        windows_path_to_wsl(script_dir / "px4ctrl_core.cpp"),
        windows_path_to_wsl(script_dir / "px4ctrl_g96_dfbc_smooth_robust_gate.cpp"),
        "-I",
        windows_path_to_wsl(script_dir),
        "-o",
        windows_path_to_wsl(exe),
    ]

    manifest: dict[str, object] = {
        "schema": "mosim.g96_dfbc_smooth_robust_static_gate_manifest.v1",
        "status": "unknown",
        "goal": "G9.6",
        "controller_profile": "dfbc_smooth_robust_attitude_thrust_v1",
        "runtime_core_profile": "dfbc_smooth_robust",
        "project_root": str(project_root),
        "result_dir": str(result_dir),
        "compile_command": compile_cmd,
        "claim_boundary": "Static smooth robust DFBC core gate only. No ROS, Gazebo, PX4, MAVROS, RViz, MWORKS GUI, wind-runtime benchmark, body-rate publish switch, or PX4-native deployment is started.",
    }

    compile_rc = run_wsl(compile_cmd, project_root, result_dir / "compile.stdout.txt", result_dir / "compile.stderr.txt")
    manifest["compile_returncode"] = compile_rc
    if compile_rc != 0:
        manifest["status"] = "blocked"
        (result_dir / "RUN_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(result_dir)
        return 1

    run_rc = run_wsl([windows_path_to_wsl(exe)], project_root, result_dir / "gate_result.json", result_dir / "gate.stderr.txt")
    manifest["run_returncode"] = run_rc
    try:
        gate_result = json.loads((result_dir / "gate_result.json").read_text(encoding="utf-8"))
    except Exception as exc:
        gate_result = {"status": "failed", "parse_error": str(exc)}
    manifest["gate_result"] = gate_result
    manifest["status"] = "passed" if run_rc == 0 and gate_result.get("status") == "passed" else "failed"
    (result_dir / "RUN_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result_dir)
    return 0 if manifest["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
