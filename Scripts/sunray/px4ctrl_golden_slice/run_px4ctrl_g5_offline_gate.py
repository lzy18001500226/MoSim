#!/usr/bin/env python3
"""Compile and run the px4ctrl G5 offline core-extraction consistency gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path, stdout: Path, stderr: Path) -> int:
    with stdout.open("w", encoding="utf-8", newline="\n") as out, stderr.open("w", encoding="utf-8", newline="\n") as err:
        proc = subprocess.run(cmd, cwd=str(cwd), stdout=out, stderr=err, text=True)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default="/mnt/c/Users/HP/Desktop/MoSim")
    parser.add_argument("--result-dir", default="")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    script_dir = project_root / "Scripts" / "sunray" / "px4ctrl_golden_slice"
    if args.result_dir:
        result_dir = Path(args.result_dir).resolve()
    else:
        result_dir = project_root / "Results" / "sunray_ros1" / f"px4ctrl_g5_offline_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir.mkdir(parents=True, exist_ok=True)
    build_dir = result_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    upstream_files = [
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "controller.cpp",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "controller.h",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "PX4CtrlParam.cpp",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "PX4CtrlParam.h",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "input.cpp",
        project_root / "References" / "Lab" / "Fast-Drone-250" / "src" / "realflight_modules" / "px4ctrl" / "src" / "input.h",
    ]
    local_files = [
        script_dir / "px4ctrl_core.h",
        script_dir / "px4ctrl_core.cpp",
        script_dir / "px4ctrl_g5_offline_gate.cpp",
        script_dir / "run_px4ctrl_g5_offline_gate.py",
    ]

    source_hashes = {
        str(path.relative_to(project_root)): sha256(path)
        for path in upstream_files + local_files
    }
    (result_dir / "source_hashes.json").write_text(
        json.dumps(source_hashes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    exe = build_dir / "px4ctrl_g5_offline_gate"
    compile_cmd = [
        "g++",
        "-std=c++11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-pedantic",
        str(script_dir / "px4ctrl_core.cpp"),
        str(script_dir / "px4ctrl_g5_offline_gate.cpp"),
        "-o",
        str(exe),
    ]
    compile_rc = run(
        compile_cmd,
        cwd=project_root,
        stdout=result_dir / "compile.stdout.txt",
        stderr=result_dir / "compile.stderr.txt",
    )

    gate_json = {
        "schema": "mosim.px4ctrl_goal3_g5_run_manifest.v1",
        "status": "blocked" if compile_rc != 0 else "unknown",
        "goal": "G-PX4CTRL-5",
        "project_root": str(project_root),
        "result_dir": str(result_dir),
        "compile_command": compile_cmd,
        "compile_returncode": compile_rc,
        "scope": {
            "controller_under_test": "References/Lab/Fast-Drone-250/src/realflight_modules/px4ctrl",
            "plant_or_runtime": "none; offline source/core consistency only",
            "mworks": "not started; G5 must pass before G6",
            "gazebo": "not started; G7 is gated by G6",
        },
        "claim_boundary": "G5 only proves the extracted platform-independent px4ctrl_core matches a ROS-free transcription of LinearControl::calculateControl for deterministic offline samples.",
    }

    if compile_rc == 0:
        run_rc = run(
            [str(exe)],
            cwd=project_root,
            stdout=result_dir / "gate_result.json",
            stderr=result_dir / "gate.stderr.txt",
        )
        gate_json["run_returncode"] = run_rc
        try:
            gate_result = json.loads((result_dir / "gate_result.json").read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic only
            gate_result = {"status": "failed", "parse_error": str(exc)}
        gate_json["gate_result"] = gate_result
        gate_json["status"] = "passed" if run_rc == 0 and gate_result.get("status") == "passed" else "failed"

    (result_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(gate_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = [
        "# px4ctrl G5 Offline Consistency Gate",
        "",
        f"Status: `{gate_json['status']}`",
        "",
        "## Scope",
        "",
        "- Goal: `G-PX4CTRL-5` only.",
        "- Runtime: none; this is an offline source/core consistency gate.",
        "- MWORKS reconstruction and generated C code are intentionally not started.",
        "- Gazebo A/B alignment is intentionally not started.",
        "",
        "## Compared Objects",
        "",
        "- Reference: ROS-free transcription of `LinearControl::calculateControl` from ZJU/Fast-Drone-250 px4ctrl.",
        "- Extracted core: `Scripts/sunray/px4ctrl_golden_slice/px4ctrl_core.*`.",
        "",
        "## Result Files",
        "",
        "- `RUN_MANIFEST.json`",
        "- `source_hashes.json`",
        "- `gate_result.json`",
        "- `compile.stdout.txt` / `compile.stderr.txt`",
        "- `gate.stderr.txt`",
        "",
    ]
    if "gate_result" in gate_json:
        report.extend(
            [
                "## Metrics",
                "",
                "```json",
                json.dumps(gate_json["gate_result"], ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    (result_dir / "G5_OFFLINE_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    print(result_dir)
    return 0 if gate_json["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
