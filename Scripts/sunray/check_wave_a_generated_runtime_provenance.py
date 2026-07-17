#!/usr/bin/env python3
"""Fail-closed provenance check for the Wave A generated px4ctrl backend."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


CONTROLLERS = {
    "lqr_baseline": (1, "lqr"),
    "lqi_baseline": (2, "lqi"),
    "so3_attitude": (3, "so3"),
    "backstepping_baseline": (4, "backstepping"),
}
SCHEMA = "mosim.wave_a.generated_runtime_provenance.v1"
MODEL = "MoSim_WaveA_CFunction_Sysblock"
BACKEND = "wave_a_attitude_thrust"
BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST"
GENERATED_DIR_CACHE_VAR = "MOSIM_PX4CTRL_WAVE_A_ATTITUDE_THRUST_GENERATED_DIR"
RUNTIME_SYMBOL = f"{MODEL}::Step"
BINARY_SYMBOL = "MosimWaveAStepScalar"
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


def load_json(path: Path, label: str, errors: list[str]) -> dict[str, object]:
    if not path.is_file():
        errors.append(f"missing {label}: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid {label}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def first_existing(paths: tuple[Path, ...]) -> Path:
    return next((path for path in paths if path.is_file()), paths[0])


def inspect_symbol(executable: Path) -> bool:
    result = subprocess.run(
        ["nm", "-C", str(executable)], text=True, capture_output=True, check=False
    )
    return result.returncode == 0 and BINARY_SYMBOL in result.stdout


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
    controller_id, _ = CONTROLLERS[args.controller_profile]

    startup_manifest = load_json(args.px4_startup_manifest, "PX4 RAM dataman rcS manifest", errors)
    if (
        startup_manifest.get("schema") != "mosim.px4.ram_dataman_rcs.v1"
        or startup_manifest.get("status") != "passed"
        or startup_manifest.get("dataman_backend") != "ram"
        or startup_manifest.get("sys_dm_backend") != 1
    ):
        errors.append("PX4 startup manifest does not prove the RAM dataman backend")

    manifest = load_json(args.build_manifest, "Wave A build manifest", errors)
    if manifest.get("schema") != "mosim.wave_a_mworks_model_build.v1" or manifest.get("model_name") != MODEL:
        errors.append("Wave A build manifest is missing or names another model")

    sil_reports: dict[str, str] = {}
    for profile, (_, sil_name) in CONTROLLERS.items():
        sil_path = args.sil_root / sil_name / "sil_equivalence.json"
        sil = load_json(sil_path, f"{profile} generated-C SIL", errors)
        comparison = sil.get("comparison") if isinstance(sil.get("comparison"), dict) else {}
        if sil.get("ok") is not True or comparison.get("pass") is not True or sil.get("model_name") != MODEL:
            errors.append(f"{profile} generated-C SIL is not accepted")
        sil_reports[profile] = str(sil_path.resolve())

    bundle_hash, generated_hashes, missing = generated_bundle(code_dir)
    if missing:
        errors.append("missing generated files: " + ", ".join(missing))

    cache_text = cache_path.read_text(encoding="utf-8", errors="replace") if cache_path.is_file() else ""
    flags_text = flags_path.read_text(encoding="utf-8", errors="replace") if flags_path.is_file() else ""
    cache_backend = cache_value(cache_text, "MOSIM_PX4CTRL_GENERATED_BACKEND")
    cache_code_dir = cache_value(cache_text, GENERATED_DIR_CACHE_VAR)
    if cache_backend != BACKEND:
        errors.append(f"CMake backend is {cache_backend!r}, expected {BACKEND!r}")
    if BACKEND_DEFINITION not in flags_text:
        errors.append(f"build flags missing {BACKEND_DEFINITION}")
    if cache_code_dir and normalized_path(cache_code_dir) != code_dir:
        errors.append("CMake generated directory mismatch")

    symbol_present = False
    if not executable.is_file():
        errors.append(f"missing px4ctrl executable: {executable}")
    else:
        symbol_present = inspect_symbol(executable)
        if not symbol_present:
            errors.append(f"px4ctrl executable lacks generated symbol {BINARY_SYMBOL}")

    runtime_ack = None
    if args.runtime_log:
        log_text = args.runtime_log.read_text(encoding="utf-8", errors="replace") if args.runtime_log.is_file() else ""
        runtime_ack = (
            f"[mosim_generated_runtime] backend=mworks_generated_c "
            f"build_backend={BACKEND} build_backend_definition={BACKEND_DEFINITION} "
            f"generated_model_name={MODEL} generated_source_sha256={bundle_hash} "
            f"runtime_loaded_symbol={RUNTIME_SYMBOL} controller_id={controller_id} "
            f"controller_name={args.controller_profile}"
        )
        if runtime_ack not in log_text:
            errors.append("runtime generated-backend acknowledgement missing or inconsistent")
    elif args.require_runtime_ack:
        errors.append("runtime log is required")

    return {
        "schema": SCHEMA,
        "status": "passed" if not errors else "failed",
        "backend": BACKEND,
        "controller_id": controller_id,
        "controller_name": args.controller_profile,
        "generated_model_name": MODEL,
        "generated_code_path": str(code_dir),
        "generated_code_sha256": bundle_hash,
        "generated_file_sha256": generated_hashes,
        "build_manifest": str(args.build_manifest.resolve()),
        "sil_reports": sil_reports,
        "px4_startup_manifest": str(args.px4_startup_manifest.resolve()),
        "px4_dataman_backend": startup_manifest.get("dataman_backend"),
        "build_backend_definition": BACKEND_DEFINITION if BACKEND_DEFINITION in flags_text else None,
        "cmake_backend": cache_backend,
        "cmake_generated_dir": cache_code_dir,
        "px4ctrl_executable_path": str(executable),
        "px4ctrl_executable_sha256": sha256_file(executable) if executable.is_file() else None,
        "binary_generated_symbol_present": symbol_present,
        "runtime_loaded_symbol": RUNTIME_SYMBOL if runtime_ack and not errors else None,
        "provenance_level": "runtime_acknowledged" if runtime_ack and not errors else "build_only",
        "runtime_ack": runtime_ack,
        "runtime_log": str(args.runtime_log.resolve()) if args.runtime_log else None,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--px4ctrl-workspace", type=Path, required=True)
    parser.add_argument("--generated-code-dir", type=Path, required=True)
    parser.add_argument("--build-manifest", type=Path, required=True)
    parser.add_argument("--sil-root", type=Path, required=True)
    parser.add_argument("--px4-startup-manifest", type=Path, required=True)
    parser.add_argument("--controller-profile", choices=tuple(CONTROLLERS), required=True)
    parser.add_argument("--runtime-log", type=Path)
    parser.add_argument("--require-runtime-ack", action="store_true")
    parser.add_argument("--json-out", type=Path)
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
