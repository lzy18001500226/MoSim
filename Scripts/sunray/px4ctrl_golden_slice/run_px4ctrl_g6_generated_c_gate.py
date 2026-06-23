#!/usr/bin/env python3
"""Run G6 four-way offline consistency against MWORKS generated C Step()."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import time
from pathlib import Path


def windows_path_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return resolved.as_posix()
    tail = resolved.relative_to(resolved.anchor).as_posix()
    return f"/mnt/{drive}/{tail}"


def run_wsl(command: list[str], cwd: Path, stdout: Path, stderr: Path) -> int:
    shell_command = " ".join(shlex.quote(item) for item in command)
    wrapped = ["wsl", "bash", "-lc", f"cd {shlex.quote(windows_path_to_wsl(cwd))} && {shell_command}"]
    with stdout.open("w", encoding="utf-8", newline="\n") as out, stderr.open("w", encoding="utf-8", newline="\n") as err:
        proc = subprocess.run(wrapped, cwd=str(cwd), stdout=out, stderr=err, text=True)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default="C:/Users/HP/Desktop/MoSim")
    parser.add_argument("--code-dir", default="Results/sunray_ros1/px4ctrl_g6_codegen_20260622_001/px4ctrl_core_cfunction_codegen_strict/PX4CTRL_Core_CFunction_Sysblock")
    parser.add_argument("--result-dir", default="")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    script_dir = project_root / "Scripts" / "sunray" / "px4ctrl_golden_slice"
    code_dir = (project_root / args.code_dir).resolve()
    if args.result_dir:
        result_dir = Path(args.result_dir).resolve()
    else:
        result_dir = project_root / "Results" / "sunray_ros1" / f"px4ctrl_g6_generated_c_gate_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir.mkdir(parents=True, exist_ok=True)
    build_dir = result_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    compile_steps = [
        ("generated_model", ["gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic", "-c", windows_path_to_wsl(code_dir / "PX4CTRL_Core_CFunction_Sysblock.c"), "-I", windows_path_to_wsl(code_dir), "-o", windows_path_to_wsl(build_dir / "generated_model.o")]),
        ("generated_data", ["gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic", "-c", windows_path_to_wsl(code_dir / "PX4CTRL_Core_CFunction_Sysblock_data.c"), "-I", windows_path_to_wsl(code_dir), "-o", windows_path_to_wsl(build_dir / "generated_data.o")]),
        ("generated_extern", ["gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic", "-c", windows_path_to_wsl(code_dir / "extern_inc" / "momodel_extern_ince1.c"), "-I", windows_path_to_wsl(code_dir), "-o", windows_path_to_wsl(build_dir / "generated_extern.o")]),
        ("cpp_core", ["g++", "-std=c++11", "-O2", "-Wall", "-Wextra", "-pedantic", "-c", windows_path_to_wsl(script_dir / "px4ctrl_core.cpp"), "-I", windows_path_to_wsl(script_dir), "-o", windows_path_to_wsl(build_dir / "cpp_core.o")]),
        ("gate", ["g++", "-std=c++11", "-O2", "-Wall", "-Wextra", "-pedantic", "-c", windows_path_to_wsl(script_dir / "px4ctrl_g6_generated_c_gate.cpp"), "-I", windows_path_to_wsl(script_dir), "-I", windows_path_to_wsl(code_dir), "-o", windows_path_to_wsl(build_dir / "gate.o")]),
    ]
    exe = build_dir / "px4ctrl_g6_generated_c_gate"
    link_cmd = [
        "g++",
        windows_path_to_wsl(build_dir / "gate.o"),
        windows_path_to_wsl(build_dir / "cpp_core.o"),
        windows_path_to_wsl(build_dir / "generated_model.o"),
        windows_path_to_wsl(build_dir / "generated_data.o"),
        windows_path_to_wsl(build_dir / "generated_extern.o"),
        "-lm",
        "-o",
        windows_path_to_wsl(exe),
    ]

    manifest: dict[str, object] = {
        "schema": "mosim.px4ctrl_g6_generated_c_manifest.v1",
        "status": "unknown",
        "project_root": str(project_root),
        "code_dir": str(code_dir),
        "result_dir": str(result_dir),
        "steps": [],
        "claim_boundary": "Offline four-way consistency only. No Gazebo runtime is executed.",
    }

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
