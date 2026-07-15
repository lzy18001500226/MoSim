#!/usr/bin/env python3
"""Compile and run the px4ctrl G7A static ROS/Sunray adapter gate."""

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
    parser.add_argument("--code-dir", required=True)
    parser.add_argument("--result-dir", default="")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    script_dir = project_root / "Scripts" / "sunray" / "px4ctrl_golden_slice"
    code_dir = (project_root / args.code_dir).resolve()
    if args.result_dir:
        result_dir = Path(args.result_dir).resolve()
    else:
        result_dir = project_root / "Results" / "sunray_ros1" / f"px4ctrl_g7a_ros_sunray_adapter_gate_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir.mkdir(parents=True, exist_ok=True)
    build_dir = result_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    required_generated_files = [
        code_dir / "PX4CTRL_Core_CFunction_Sysblock.c",
        code_dir / "PX4CTRL_Core_CFunction_Sysblock.h",
        code_dir / "PX4CTRL_Core_CFunction_Sysblock_data.c",
        code_dir / "PX4CTRL_Core_CFunction_Sysblock_private.h",
        code_dir / "extern_inc" / "momodel_extern_ince1.c",
    ]
    missing = [str(path) for path in required_generated_files if not path.exists()]

    source_files = [
        script_dir / "px4ctrl_core.h",
        script_dir / "px4ctrl_core.cpp",
        script_dir / "px4ctrl_g7a_ros_sunray_adapter_gate.cpp",
        Path(__file__).resolve(),
        *required_generated_files,
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

    manifest: dict[str, object] = {
        "schema": "mosim.px4ctrl_g7a_ros_sunray_adapter_manifest.v1",
        "status": "unknown",
        "goal": "G-PX4CTRL-7A",
        "project_root": str(project_root),
        "code_dir": str(code_dir),
        "result_dir": str(result_dir),
        "required_generated_files_present": {
            str(path.relative_to(code_dir)): path.exists() for path in required_generated_files
        },
        "steps": [],
        "claim_boundary": "Static ROS/Sunray adapter gate only. No ROS, Gazebo, PX4, MAVROS, RViz, or MWORKS GUI/runtime is executed.",
        "next_gate": "G-PX4CTRL-7B Gazebo A/B run with original px4ctrl versus MWORKS-generated core under the frozen Sunray runtime baseline.",
    }
    if missing:
        manifest["status"] = "blocked"
        manifest["missing_files"] = missing
        (result_dir / "RUN_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(result_dir)
        return 1

    compile_steps = [
        (
            "generated_model",
            [
                "gcc",
                "-std=c99",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(code_dir / "PX4CTRL_Core_CFunction_Sysblock.c"),
                "-I",
                windows_path_to_wsl(code_dir),
                "-o",
                windows_path_to_wsl(build_dir / "generated_model.o"),
            ],
        ),
        (
            "generated_data",
            [
                "gcc",
                "-std=c99",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(code_dir / "PX4CTRL_Core_CFunction_Sysblock_data.c"),
                "-I",
                windows_path_to_wsl(code_dir),
                "-o",
                windows_path_to_wsl(build_dir / "generated_data.o"),
            ],
        ),
        (
            "generated_extern",
            [
                "gcc",
                "-std=c99",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(code_dir / "extern_inc" / "momodel_extern_ince1.c"),
                "-I",
                windows_path_to_wsl(code_dir),
                "-o",
                windows_path_to_wsl(build_dir / "generated_extern.o"),
            ],
        ),
        (
            "cpp_core",
            [
                "g++",
                "-std=c++11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(script_dir / "px4ctrl_core.cpp"),
                "-I",
                windows_path_to_wsl(script_dir),
                "-o",
                windows_path_to_wsl(build_dir / "cpp_core.o"),
            ],
        ),
        (
            "adapter_gate",
            [
                "g++",
                "-std=c++11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(script_dir / "px4ctrl_g7a_ros_sunray_adapter_gate.cpp"),
                "-I",
                windows_path_to_wsl(script_dir),
                "-I",
                windows_path_to_wsl(code_dir),
                "-o",
                windows_path_to_wsl(build_dir / "adapter_gate.o"),
            ],
        ),
    ]
    exe = build_dir / "px4ctrl_g7a_ros_sunray_adapter_gate"
    link_cmd = [
        "g++",
        windows_path_to_wsl(build_dir / "adapter_gate.o"),
        windows_path_to_wsl(build_dir / "cpp_core.o"),
        windows_path_to_wsl(build_dir / "generated_model.o"),
        windows_path_to_wsl(build_dir / "generated_data.o"),
        windows_path_to_wsl(build_dir / "generated_extern.o"),
        "-lm",
        "-o",
        windows_path_to_wsl(exe),
    ]

    for name, cmd in compile_steps + [("link", link_cmd)]:
        rc = run_wsl(cmd, project_root, result_dir / f"{name}.stdout.txt", result_dir / f"{name}.stderr.txt")
        manifest["steps"].append({"name": name, "returncode": rc, "command": cmd})  # type: ignore[index]
        if rc != 0:
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
