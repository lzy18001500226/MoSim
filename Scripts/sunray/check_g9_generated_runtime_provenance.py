#!/usr/bin/env python3
"""Fail-closed provenance check for the G9 MWORKS-generated px4ctrl runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import subprocess
import sys


CONTROLLERS = {
    "official_pid": 1,
    "se3_basic": 2,
    "dfbc_basic": 3,
    "smc_boundary_layer": 4,
    "pid_indi": 5,
    "nmpc_outer": 6,
}
MODEL = "G9_Family_CFunction_Sysblock"
BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY"
RUNTIME_SYMBOL = f"{MODEL}::Step"
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


def source_identity(project_root: Path) -> dict[str, object]:
    paths = (
        project_root / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/CMakeLists.txt",
        project_root / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/src/controller.cpp",
        project_root / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/src/controller.h",
    )
    file_hashes = {
        str(path.relative_to(project_root)).replace("\\", "/"): sha256_file(path)
        for path in paths
        if path.is_file()
    }
    git_head = None
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        git_head = result.stdout.strip()
    return {"git_head": git_head, "file_sha256": file_hashes}


def inspect_symbols(executable: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["nm", "-C", str(executable)],
        text=True,
        capture_output=True,
        check=False,
    )
    text = result.stdout + result.stderr
    return result.returncode == 0 and "MosimPx4ctrlG9FamilyCStepScalar" in text, text[-4000:]


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    project_root = normalized_path(args.project_root)
    workspace = normalized_path(args.px4ctrl_workspace)
    code_dir = normalized_path(args.generated_code_dir)
    cache_path = workspace / "build/CMakeCache.txt"
    flags_path = workspace / "build/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make"
    executable = workspace / "devel/lib/px4ctrl/px4ctrl_node"
    errors: list[str] = []

    controller_id = CONTROLLERS.get(args.controller_profile)
    if controller_id is None:
        errors.append(f"unsupported controller profile: {args.controller_profile}")

    codegen_record: dict[str, object] = {}
    if not args.codegen_manifest.is_file():
        errors.append(f"missing codegen manifest: {args.codegen_manifest}")
    else:
        try:
            codegen_record = json.loads(args.codegen_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid codegen manifest: {exc}")
    if codegen_record.get("model_name") != MODEL:
        errors.append("codegen manifest model_name mismatch")
    manifest_code_dir = codegen_record.get("code_dir")
    if manifest_code_dir and normalized_path(str(manifest_code_dir)) != code_dir:
        errors.append("codegen manifest code_dir mismatch")
    if codegen_record.get("generate_model_code") is not True or codegen_record.get("ok") is not True:
        errors.append("codegen manifest does not record successful GenerateModelCode")

    bundle_hash, generated_hashes, missing_generated = generated_bundle(code_dir)
    if missing_generated:
        errors.append("missing generated files: " + ", ".join(missing_generated))

    cache_text = cache_path.read_text(encoding="utf-8", errors="replace") if cache_path.is_file() else ""
    flags_text = flags_path.read_text(encoding="utf-8", errors="replace") if flags_path.is_file() else ""
    cache_backend = cache_value(cache_text, "MOSIM_PX4CTRL_GENERATED_BACKEND")
    cache_code_dir = cache_value(cache_text, "MOSIM_PX4CTRL_G9_FAMILY_GENERATED_DIR")
    if cache_backend != "g9_family":
        errors.append(f"CMake backend is {cache_backend!r}, expected 'g9_family'")
    if BACKEND_DEFINITION not in flags_text:
        errors.append(f"build flags missing {BACKEND_DEFINITION}")
    if cache_code_dir and normalized_path(cache_code_dir) != code_dir:
        errors.append("CMake G9 generated directory mismatch")

    binary_symbol_present = False
    symbol_tail = ""
    if not executable.is_file():
        errors.append(f"missing px4ctrl executable: {executable}")
    else:
        binary_symbol_present, symbol_tail = inspect_symbols(executable)
        if not binary_symbol_present:
            errors.append("px4ctrl executable lacks G9 generated scalar-step symbol")

    runtime_ack = None
    if args.runtime_log:
        log_text = args.runtime_log.read_text(encoding="utf-8", errors="replace") if args.runtime_log.is_file() else ""
        expected = (
            f"[mosim_generated_runtime] backend=mworks_generated_c "
            f"build_backend=g9_family "
            f"build_backend_definition={BACKEND_DEFINITION} "
            f"generated_model_name={MODEL} "
            f"runtime_loaded_symbol={RUNTIME_SYMBOL} "
            f"controller_id={controller_id} controller_name={args.controller_profile}"
        )
        runtime_ack = expected
        if expected not in log_text:
            errors.append("runtime generated-backend acknowledgement missing or inconsistent")
    elif args.require_runtime_ack:
        errors.append("runtime log is required")

    executable_stat = executable.stat() if executable.is_file() else None
    payload: dict[str, object] = {
        "schema": "mosim.g9_mworks_generated_runtime_provenance.v1",
        "status": "passed" if not errors else "failed",
        "backend": "mworks_generated_c" if not errors else None,
        "controller_id": controller_id,
        "controller_name": args.controller_profile,
        "generated_model_name": MODEL,
        "generated_code_path": str(code_dir),
        "generated_code_sha256": bundle_hash,
        "generated_file_sha256": generated_hashes,
        "codegen_manifest": str(args.codegen_manifest.resolve()),
        "runtime_loaded_symbol": RUNTIME_SYMBOL if runtime_ack and not errors else None,
        "build_backend_definition": BACKEND_DEFINITION if BACKEND_DEFINITION in flags_text else None,
        "cmake_backend": cache_backend,
        "cmake_g9_generated_dir": cache_code_dir,
        "px4ctrl_executable_path": str(executable),
        "px4ctrl_executable_sha256": sha256_file(executable) if executable.is_file() else None,
        "build_timestamp_utc": (
            datetime.fromtimestamp(executable_stat.st_mtime, timezone.utc).isoformat()
            if executable_stat else None
        ),
        "binary_generated_symbol_present": binary_symbol_present,
        "runtime_ack": runtime_ack,
        "runtime_log": str(args.runtime_log.resolve()) if args.runtime_log else None,
        "source_commit_or_tree_identity": source_identity(project_root),
        "errors": errors,
    }
    if args.include_symbol_tail:
        payload["nm_tail"] = symbol_tail
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--px4ctrl-workspace", type=Path, required=True)
    parser.add_argument("--generated-code-dir", type=Path, required=True)
    parser.add_argument("--codegen-manifest", type=Path, required=True)
    parser.add_argument("--controller-profile", required=True, choices=tuple(CONTROLLERS))
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
    sys.stdout.write(rendered)
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
