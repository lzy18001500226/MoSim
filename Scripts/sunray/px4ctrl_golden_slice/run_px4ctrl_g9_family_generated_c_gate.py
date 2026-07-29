#!/usr/bin/env python3
"""Compile and run G9 family C++ core against MWORKS generated C Step()."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def detect_generated_globals(header_path: Path) -> tuple[str, str]:
    text = header_path.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(r"extern\s+struct\s+\w+\s+(\w+)\s*;", text)
    if len(matches) < 2:
        raise ValueError(f"cannot detect generated input/output globals from {header_path}")
    return matches[0], matches[1]


def detect_g10_bde_inputs(header_paths: list[Path]) -> bool:
    header_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in header_paths
        if path.is_file()
    )
    return all(
        field in header_text
        for field in (
            "l1_model_decay_in",
            "safety_accel_limit_x_in",
            "fault_rotor_efficiency_4_in",
        )
    )


def detect_p10_dfbc_inputs(header_paths: list[Path]) -> bool:
    header_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in header_paths
        if path.is_file()
    )
    return all(
        field in header_text
        for field in (
            "high_order_body_rate_limit_x_in",
            "smooth_feedback_bound_x_in",
            "disturbance_compensation_limit_z_in",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default="C:/Users/HP/Desktop/MoSim")
    parser.add_argument(
        "--code-dir",
        default=(
            "Results/g9/controller_family_attitude_thrust_v1/"
            "g9_family_mworks_codegen_20260630_work/"
            "g9_family_cfunction_codegen_strict/"
            "G9_Family_CFunction_Sysblock"
        ),
    )
    parser.add_argument("--model-name", default="G9_Family_CFunction_Sysblock")
    parser.add_argument("--result-dir", default="")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    script_dir = project_root / "Scripts" / "sunray" / "px4ctrl_golden_slice"
    code_dir = (project_root / args.code_dir).resolve()
    if args.result_dir:
        result_dir = Path(args.result_dir).resolve()
    else:
        result_dir = (
            project_root
            / "Results"
            / "g9"
            / "controller_family_attitude_thrust_v1"
            / f"g9_family_generated_c_gate_{time.strftime('%Y%m%d_%H%M%S')}"
        )
    result_dir.mkdir(parents=True, exist_ok=True)
    build_dir = result_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    model_name = args.model_name
    generated_headers = [
        code_dir / f"{model_name}.h",
        code_dir / f"{model_name}_private.h",
    ]
    has_g10_bde_inputs = detect_g10_bde_inputs(generated_headers)
    has_p10_dfbc_inputs = detect_p10_dfbc_inputs(generated_headers)
    controller_ids = list(range(1, 12 if has_p10_dfbc_inputs else (10 if has_g10_bde_inputs else 7)))
    required = [
        code_dir / f"{model_name}.c",
        code_dir / f"{model_name}_data.c",
        code_dir / f"{model_name}_private.h",
        code_dir / f"{model_name}.h",
        code_dir / "mwb_runtime.h",
        code_dir / "mwb_types.h",
        code_dir / "extern_inc" / "momodel_extern_ince1.c",
        script_dir / "px4ctrl_core.h",
        script_dir / "px4ctrl_core.cpp",
        script_dir / "px4ctrl_g9_family_generated_c_gate.cpp",
        Path(__file__).resolve(),
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        manifest = {
            "schema": "mosim.g9_family_mworks_generated_c_manifest.v1",
            "status": "blocked",
            "missing": missing,
            "project_root": str(project_root),
            "code_dir": str(code_dir),
            "result_dir": str(result_dir),
        }
        (result_dir / "RUN_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(result_dir)
        return 1

    try:
        input_global, output_global = detect_generated_globals(code_dir / f"{model_name}.h")
    except Exception as exc:
        manifest = {
            "schema": "mosim.g9_family_mworks_generated_c_manifest.v1",
            "status": "blocked",
            "error": str(exc),
            "project_root": str(project_root),
            "code_dir": str(code_dir),
            "result_dir": str(result_dir),
        }
        (result_dir / "RUN_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(result_dir)
        return 1

    source_hashes = {rel(path, project_root): sha256(path) for path in required if path.is_file()}
    (result_dir / "source_hashes.json").write_text(
        json.dumps(source_hashes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    generated_model_obj = build_dir / "generated_model.o"
    generated_data_obj = build_dir / "generated_data.o"
    generated_extern_obj = build_dir / "generated_extern.o"
    cpp_core_obj = build_dir / "px4ctrl_core.o"
    gate_obj = build_dir / "px4ctrl_g9_family_generated_c_gate.o"
    exe = build_dir / "px4ctrl_g9_family_generated_c_gate"

    steps = [
        {
            "name": "compile_generated_model",
            "cmd": [
                "gcc",
                "-std=c99",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(code_dir / f"{model_name}.c"),
                "-I",
                windows_path_to_wsl(code_dir),
                "-o",
                windows_path_to_wsl(generated_model_obj),
            ],
        },
        {
            "name": "compile_generated_data",
            "cmd": [
                "gcc",
                "-std=c99",
                "-O2",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-c",
                windows_path_to_wsl(code_dir / f"{model_name}_data.c"),
                "-I",
                windows_path_to_wsl(code_dir),
                "-o",
                windows_path_to_wsl(generated_data_obj),
            ],
        },
        {
            "name": "compile_generated_extern",
            "cmd": [
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
                windows_path_to_wsl(generated_extern_obj),
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
                "-I",
                windows_path_to_wsl(script_dir),
                "-o",
                windows_path_to_wsl(cpp_core_obj),
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
                windows_path_to_wsl(script_dir / "px4ctrl_g9_family_generated_c_gate.cpp"),
                "-I",
                windows_path_to_wsl(script_dir),
                "-I",
                windows_path_to_wsl(code_dir),
                f'-DGENERATED_MODEL_PRIVATE_HEADER="{model_name}_private.h"',
                f"-DGENERATED_MODEL_INPUT_GLOBAL={input_global}",
                f"-DGENERATED_MODEL_OUTPUT_GLOBAL={output_global}",
                f"-DGENERATED_MODEL_HAS_G10_BDE_INPUTS={1 if has_g10_bde_inputs else 0}",
                f"-DGENERATED_MODEL_HAS_P10_DFBC_INPUTS={1 if has_p10_dfbc_inputs else 0}",
                "-o",
                windows_path_to_wsl(gate_obj),
            ],
        },
        {
            "name": "link_gate",
            "cmd": [
                "g++",
                windows_path_to_wsl(gate_obj),
                windows_path_to_wsl(cpp_core_obj),
                windows_path_to_wsl(generated_model_obj),
                windows_path_to_wsl(generated_data_obj),
                windows_path_to_wsl(generated_extern_obj),
                "-lm",
                "-o",
                windows_path_to_wsl(exe),
            ],
        },
    ]

    manifest: dict[str, object] = {
        "schema": "mosim.g9_family_mworks_generated_c_manifest.v1",
        "status": "unknown",
        "goal": "G9-G10-P10-FAMILY-MWORKS-GENERATED-C" if has_p10_dfbc_inputs else ("G9-G10-BDE-FAMILY-MWORKS-GENERATED-C" if has_g10_bde_inputs else "G9-FAMILY-MWORKS-GENERATED-C"),
        "controller_profile": "controller_family_attitude_thrust_v1",
        "controller_ids": controller_ids,
        "model_name": model_name,
        "generated_input_global": input_global,
        "generated_output_global": output_global,
        "project_root": str(project_root),
        "code_dir": str(code_dir),
        "result_dir": str(result_dir),
        "steps": [],
        "claim_boundary": ("Offline generated-code equivalence for G9-A..F, G10-B/D/E, and P10 DFBC high-order/smooth-robust routes only. No ROS, Gazebo, RViz, or flight runtime is executed." if has_p10_dfbc_inputs else ("Offline generated-code equivalence for G9-A..F plus accepted G10-B/D/E minimal enhancements only. No ROS, Gazebo, RViz, or flight runtime is executed." if has_g10_bde_inputs else "Offline generated-code equivalence for G9-A..F only. No ROS, Gazebo, RViz, or flight runtime is executed.")),
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
