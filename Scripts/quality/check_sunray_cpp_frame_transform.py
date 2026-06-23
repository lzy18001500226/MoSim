#!/usr/bin/env python3
"""Compile-check the Sunray FAST-LIO frame-transform C++ helper."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap


ROOT = Path(__file__).resolve().parents[2]
HEADER_DIR = ROOT / "Scripts" / "sunray" / "cpp" / "mosim_sunray_runtime_adapters" / "include"
HEADER = HEADER_DIR / "mosim_sunray_runtime_adapters" / "fastlio_frame_transform.hpp"
OUTPUT_DIR = ROOT / "Results" / "refactor" / "runtime_tiers"
BUILD_DIR = OUTPUT_DIR / "cpp_frame_transform_check"


def to_wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix()[3:]
    return f"/mnt/{drive}/{tail}"


def compiler_command(source: Path, output: Path) -> tuple[list[str], list[str]]:
    if shutil.which("g++"):
        compile_cmd = [
            "g++",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-pedantic",
            "-I",
            str(HEADER_DIR),
            str(source),
            "-o",
            str(output),
        ]
        run_cmd = [str(output)]
        return compile_cmd, run_cmd

    if shutil.which("wsl"):
        output_wsl = to_wsl_path(output)
        compile_cmd = [
            "wsl",
            "-d",
            "Ubuntu-20.04",
            "--",
            "g++",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-pedantic",
            "-I",
            to_wsl_path(HEADER_DIR),
            to_wsl_path(source),
            "-o",
            output_wsl,
        ]
        run_cmd = ["wsl", "-d", "Ubuntu-20.04", "--", output_wsl]
        return compile_cmd, run_cmd

    raise RuntimeError("no g++ compiler found on Windows PATH and no wsl command found")


def write_check_source(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            r'''
            #include <cmath>
            #include <iostream>

            #include "mosim_sunray_runtime_adapters/fastlio_frame_transform.hpp"

            namespace rt = mosim_sunray_runtime_adapters;

            bool near(double a, double b, double tol = 1.0e-9) {
              return std::fabs(a - b) <= tol;
            }

            int main() {
              const rt::Quat identity = rt::quat_from_rpy(0.0, 0.0, 0.0);
              if (!near(identity.x, 0.0) || !near(identity.y, 0.0) ||
                  !near(identity.z, 0.0) || !near(identity.w, 1.0)) {
                std::cerr << "identity quaternion failed\n";
                return 2;
              }

              const double yaw = 1.2;
              const rt::Quat yaw_q = rt::quat_from_rpy(0.0, 0.0, yaw);
              if (!near(rt::yaw_from_quat(yaw_q), yaw)) {
                std::cerr << "yaw extraction failed\n";
                return 3;
              }

              const rt::Vec3 rotated = rt::transform_velocity(
                  rt::quat_from_rpy(0.0, 0.0, 1.5707963267948966),
                  rt::Vec3{1.0, 0.0, 0.0});
              if (!near(rotated.x, 0.0, 1.0e-8) || !near(rotated.y, 1.0, 1.0e-8) ||
                  !near(rotated.z, 0.0, 1.0e-8)) {
                std::cerr << "velocity rotation failed\n";
                return 4;
              }

              const rt::Pose3 pose{rt::Vec3{1.0, -2.0, 0.4}, rt::quat_from_rpy(0.1, -0.2, 0.3)};
              const rt::Pose3 roundtrip = rt::pose_mul(pose, rt::pose_inv(pose));
              if (!near(roundtrip.p.x, 0.0, 1.0e-8) || !near(roundtrip.p.y, 0.0, 1.0e-8) ||
                  !near(roundtrip.p.z, 0.0, 1.0e-8) || !near(roundtrip.q.x, 0.0, 1.0e-8) ||
                  !near(roundtrip.q.y, 0.0, 1.0e-8) || !near(roundtrip.q.z, 0.0, 1.0e-8) ||
                  !near(roundtrip.q.w, 1.0, 1.0e-8)) {
                std::cerr << "pose inverse roundtrip failed\n";
                return 5;
              }

              std::cout << "{\"status\":\"passed\"}\n";
              return 0;
            }
            '''
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    source = BUILD_DIR / "frame_transform_check.cpp"
    output = BUILD_DIR / "frame_transform_check"
    write_check_source(source)

    payload: dict[str, object] = {
        "schema": "mosim.sunray_cpp_frame_transform_check.v1",
        "header": HEADER.relative_to(ROOT).as_posix(),
        "source": source.relative_to(ROOT).as_posix(),
        "claim_boundary": [
            "Static compile/unit check only: no ROS, Gazebo, PX4, RViz, MWORKS, or FAST-LIO node was started.",
            "This proves only the pure C++ transform helper compiles and passes deterministic math checks.",
        ],
    }

    try:
        compile_cmd, run_cmd = compiler_command(source, output)
        compile_result = subprocess.run(compile_cmd, cwd=ROOT, text=True, capture_output=True, check=False)
        run_result = subprocess.run(run_cmd, cwd=ROOT, text=True, capture_output=True, check=False) if compile_result.returncode == 0 else None
        payload.update(
            {
                "status": "passed" if compile_result.returncode == 0 and run_result and run_result.returncode == 0 else "failed",
                "compile_returncode": compile_result.returncode,
                "compile_stdout": compile_result.stdout,
                "compile_stderr": compile_result.stderr,
                "run_returncode": None if run_result is None else run_result.returncode,
                "run_stdout": None if run_result is None else run_result.stdout,
                "run_stderr": None if run_result is None else run_result.stderr,
            }
        )
    except Exception as exc:  # pragma: no cover - diagnostic payload path
        payload.update({"status": "blocked", "error": str(exc)})

    out_path = OUTPUT_DIR / "sunray_cpp_frame_transform_check.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
