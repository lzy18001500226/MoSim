#!/usr/bin/env python3
"""Fail-closed provenance check for the P1 PID MWORKS-generated px4ctrl backend."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


CONTROLLERS = {
    "cascade_pid": 1,
    "gain_scheduled_pid": 2,
    "fuzzy_pid": 3,
    "neural_pid": 4,
    "anti_windup": 5,
    "feedforward_profile": 6,
}
MODEL = "MoSim_PID_AttitudeThrust_CFunction_Sysblock"
BACKEND = "pid_attitude_thrust"
BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST"
RUNTIME_SYMBOL = f"{MODEL}::Step"
BINARY_SYMBOL = "MosimPidAttitudeThrustStepScalar"
REQUIRED_GENERATED_FILES = (
    f"{MODEL}.c",
    f"{MODEL}.h",
    f"{MODEL}_data.c",
    f"{MODEL}_private.h",
    "extern_inc/momodel_extern_ince1.c",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generated_bundle(code_dir: Path) -> tuple[str, dict[str, str], list[str]]:
    digest = hashlib.sha256()
    hashes: dict[str, str] = {}
    missing: list[str] = []
    for relative in REQUIRED_GENERATED_FILES:
        path = code_dir / relative
        if not path.is_file():
            missing.append(relative)
            continue
        file_hash = sha256_file(path)
        hashes[relative] = file_hash
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), hashes, missing


def cache_value(text: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:[^=]+=(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def normalized_path(raw: str | Path) -> Path:
    text = str(raw).replace("\\", "/")
    drive = re.match(r"^([A-Za-z]):/(.*)$", text)
    if drive and os.name == "posix" and Path("/mnt").is_dir():
        text = f"/mnt/{drive.group(1).lower()}/{drive.group(2)}"
    return Path(os.path.normpath(text)).resolve()


def first_existing(paths: tuple[Path, ...]) -> Path:
    return next((path for path in paths if path.is_file()), paths[0])


def inspect_symbol(executable: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["nm", "-C", str(executable)], text=True, capture_output=True, check=False
    )
    text = result.stdout + result.stderr
    return result.returncode == 0 and BINARY_SYMBOL in text, text[-4000:]


def load_json(path: Path, label: str, errors: list[str]) -> dict[str, object]:
    if not path.is_file():
        errors.append(f"missing {label}: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid {label}: {exc}")
        return {}


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    workspace = normalized_path(args.px4ctrl_workspace)
    code_dir = normalized_path(args.generated_code_dir)
    cache_path = workspace / "build/CMakeCache.txt"
    flags_path = first_existing((
        workspace / "build/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make",
        workspace / "build/realflight_modules/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make",
    ))
    executable = workspace / "devel/lib/px4ctrl/px4ctrl_node"
    errors: list[str] = []
    controller_id = CONTROLLERS[args.controller_profile]

    generation = load_json(args.codegen_manifest, "codegen manifest", errors)
    runtime_check = load_json(args.runtime_check, "generated runtime check", errors)
    if generation.get("model_name") != MODEL or generation.get("result") is not True:
        errors.append("codegen manifest does not record successful v2 GenerateModelCode")
    if not str(generation.get("output_root", "")).replace("\\", "/").endswith("generated_c_v2"):
        errors.append("codegen manifest does not identify generated_c_v2")
    if runtime_check.get("model_name") != MODEL or runtime_check.get("ok") is not True:
        errors.append("generated runtime check is missing or failed")
    runtime_code_dir = runtime_check.get("code_dir")
    if runtime_code_dir and normalized_path(str(runtime_code_dir)) != code_dir:
        errors.append("generated runtime check code_dir mismatch")

    bundle_hash, generated_hashes, missing_generated = generated_bundle(code_dir)
    if missing_generated:
        errors.append("missing generated files: " + ", ".join(missing_generated))

    cache_text = cache_path.read_text(encoding="utf-8", errors="replace") if cache_path.is_file() else ""
    flags_text = flags_path.read_text(encoding="utf-8", errors="replace") if flags_path.is_file() else ""
    cache_backend = cache_value(cache_text, "MOSIM_PX4CTRL_GENERATED_BACKEND")
    cache_code_dir = cache_value(cache_text, "MOSIM_PX4CTRL_PID_ATTITUDE_THRUST_GENERATED_DIR")
    if cache_backend != BACKEND:
        errors.append(f"CMake backend is {cache_backend!r}, expected {BACKEND!r}")
    if BACKEND_DEFINITION not in flags_text:
        errors.append(f"build flags missing {BACKEND_DEFINITION}")
    if cache_code_dir and normalized_path(cache_code_dir) != code_dir:
        errors.append("CMake PID generated directory mismatch")

    binary_symbol_present = False
    symbol_tail = ""
    if not executable.is_file():
        errors.append(f"missing px4ctrl executable: {executable}")
    else:
        binary_symbol_present, symbol_tail = inspect_symbol(executable)
        if not binary_symbol_present:
            errors.append(f"px4ctrl executable lacks generated symbol {BINARY_SYMBOL}")

    runtime_ack = None
    if args.runtime_log:
        log_text = args.runtime_log.read_text(encoding="utf-8", errors="replace") if args.runtime_log.is_file() else ""
        runtime_ack = (
            f"[mosim_generated_runtime] backend=mworks_generated_c "
            f"build_backend={BACKEND} "
            f"build_backend_definition={BACKEND_DEFINITION} "
            f"generated_model_name={MODEL} "
            f"runtime_loaded_symbol={RUNTIME_SYMBOL} "
            f"controller_id={controller_id} controller_name={args.controller_profile} "
            f"neural_residual_source=zero_untrained"
        )
        if runtime_ack not in log_text:
            errors.append("runtime generated-backend acknowledgement missing or inconsistent")
    elif args.require_runtime_ack:
        errors.append("runtime log is required")

    payload: dict[str, object] = {
        "schema": "mosim.pid_attitude_thrust_generated_runtime_provenance.v1",
        "status": "passed" if not errors else "failed",
        "backend": BACKEND if not errors else None,
        "controller_id": controller_id,
        "controller_name": args.controller_profile,
        "generated_model_name": MODEL,
        "generated_code_path": str(code_dir),
        "generated_code_sha256": bundle_hash,
        "generated_file_sha256": generated_hashes,
        "codegen_manifest": str(args.codegen_manifest.resolve()),
        "runtime_check": str(args.runtime_check.resolve()),
        "runtime_loaded_symbol": RUNTIME_SYMBOL if runtime_ack and not errors else None,
        "provenance_level": "runtime_acknowledged" if runtime_ack and not errors else "build_only",
        "build_backend_definition": BACKEND_DEFINITION if BACKEND_DEFINITION in flags_text else None,
        "cmake_backend": cache_backend,
        "cmake_pid_generated_dir": cache_code_dir,
        "px4ctrl_executable_path": str(executable),
        "px4ctrl_executable_sha256": sha256_file(executable) if executable.is_file() else None,
        "binary_generated_symbol_present": binary_symbol_present,
        "runtime_ack": runtime_ack,
        "runtime_log": str(args.runtime_log.resolve()) if args.runtime_log else None,
        "neural_residual_source": "zero_untrained",
        "errors": errors,
    }
    if args.include_symbol_tail:
        payload["nm_tail"] = symbol_tail
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--px4ctrl-workspace", type=Path, required=True)
    parser.add_argument("--generated-code-dir", type=Path, required=True)
    parser.add_argument("--codegen-manifest", type=Path, required=True)
    parser.add_argument("--runtime-check", type=Path, required=True)
    parser.add_argument("--controller-profile", choices=tuple(CONTROLLERS), required=True)
    parser.add_argument("--runtime-log", type=Path)
    parser.add_argument("--require-runtime-ack", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--include-symbol-tail", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
