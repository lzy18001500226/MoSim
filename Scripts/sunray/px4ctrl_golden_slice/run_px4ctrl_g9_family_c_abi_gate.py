#!/usr/bin/env python3
"""Compile and run the G9 controller-family C ABI consistency gate."""

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
        result_dir = (
            project_root
            / "Results"
            / "g9"
            / "controller_family_attitude_thrust_v1"
            / f"g9_family_c_abi_gate_{time.strftime('%Y%m%d_%H%M%S')}"
        )
    result_dir.mkdir(parents=True, exist_ok=True)
    build_dir = result_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    source_files = [
        script_dir / "px4ctrl_core.h",
        script_dir / "px4ctrl_core.cpp",
        script_dir / "px4ctrl_g9_family_core_c.h",
        script_dir / "px4ctrl_g9_family_core_c.c",
        script_dir / "px4ctrl_g9_family_c_abi_gate.cpp",
        Path(__file__).resolve(),
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

    c_obj = build_dir / "px4ctrl_g9_family_core_c.o"
    cpp_obj = build_dir / "px4ctrl_core.o"
    gate_obj = build_dir / "px4ctrl_g9_family_c_abi_gate.o"
    exe = build_dir / "px4ctrl_g9_family_c_abi_gate"

    steps = [
        {
            "name": "compile_c_g9_family_core",
            "cmd": [
                "gcc",
                "-std=c99",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(script_dir / "px4ctrl_g9_family_core_c.c"),
                "-o",
                windows_path_to_wsl(c_obj),
            ],
        },
        {
            "name": "compile_cpp_core",
            "cmd": [
                "g++",
                "-std=c++11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(script_dir / "px4ctrl_core.cpp"),
                "-o",
                windows_path_to_wsl(cpp_obj),
            ],
        },
        {
            "name": "compile_gate",
            "cmd": [
                "g++",
                "-std=c++11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(script_dir / "px4ctrl_g9_family_c_abi_gate.cpp"),
                "-I",
                windows_path_to_wsl(script_dir),
                "-o",
                windows_path_to_wsl(gate_obj),
            ],
        },
        {
            "name": "link_gate",
            "cmd": [
                "g++",
                windows_path_to_wsl(cpp_obj),
                windows_path_to_wsl(gate_obj),
                windows_path_to_wsl(c_obj),
                "-lm",
                "-o",
                windows_path_to_wsl(exe),
            ],
        },
    ]

    manifest: dict[str, object] = {
        "schema": "mosim.g9_family_c_abi_manifest.v1",
        "status": "unknown",
        "goal": "G9-G10-BDE-FAMILY-C-ABI",
        "controller_profile": "controller_family_attitude_thrust_v1",
        "controller_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "project_root": str(project_root),
        "result_dir": str(result_dir),
        "steps": [],
        "claim_boundary": "This gate proves only C++ core versus pure C ABI equivalence for G9-A..F plus accepted G10-B/D/E minimal enhancements. It is not MWORKS generated-code or Gazebo runtime evidence.",
    }

    for step in steps:
        name = str(step["name"])
        cmd = list(step["cmd"])
        rc = run_wsl(
            cmd,
            project_root,
            result_dir / f"{name}.stdout.txt",
            result_dir / f"{name}.stderr.txt",
        )
        manifest["steps"].append({"name": name, "returncode": rc, "command": cmd})  # type: ignore[index]
        if rc != 0:
            manifest["status"] = "blocked"
            (result_dir / "RUN_MANIFEST.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(result_dir)
            return 1

    run_rc = run_wsl(
        [windows_path_to_wsl(exe)],
        project_root,
        result_dir / "gate_result.json",
        result_dir / "gate.stderr.txt",
    )
    manifest["run_returncode"] = run_rc
    try:
        gate_result = json.loads((result_dir / "gate_result.json").read_text(encoding="utf-8"))
    except Exception as exc:
        gate_result = {"status": "failed", "parse_error": str(exc)}
    manifest["gate_result"] = gate_result
    manifest["status"] = "passed" if run_rc == 0 and gate_result.get("status") == "passed" else "failed"

    (result_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(result_dir)
    return 0 if manifest["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
