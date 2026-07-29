#!/usr/bin/env python3
"""Fail-closed runtime provenance for the P10 generated-C Gazebo routes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path


CONFIG = {
    "l1_awff_minimal": {
        "backend": "p10_l1_awff",
        "definition": "MOSIM_PX4CTRL_GENERATED_BACKEND_P10_L1_AWFF",
        "cache_var": "MOSIM_PX4CTRL_P10_L1_AWFF_GENERATED_DIR",
        "model": "MoSim_P10_G10_BDE_CFunction_Sysblock",
        "symbol": "MosimPx4ctrlG9FamilyCStepScalar",
        "controller_id": 7,
        "closeout": "Results/control_platform/p10_mworks_gap_closeout_20260718/l1_awff_minimal/P10_L1_AWFF_MWORKS_CLOSEOUT.json",
        "bodyrate": False,
        "dob": False,
    },
    "hinf_hover_wrench": {
        "backend": "p10_hinf_wrench",
        "definition": "MOSIM_PX4CTRL_GENERATED_BACKEND_P10_HINF_WRENCH",
        "cache_var": "MOSIM_PX4CTRL_P10_HINF_WRENCH_GENERATED_DIR",
        "model": "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock",
        "symbol": "MosimP10HinfWrenchAdapterStepScalar",
        "controller_id": 1,
        "closeout": "Results/control_platform/p10_mworks_gap_closeout_20260718/hinf_hover_wrench/P10_HINF_MWORKS_MANIFEST.json",
        "bodyrate": False,
        "dob": False,
    },
}

for name, controller_id, bodyrate, dob in (
    ("dfbc_high_order_attitude", 10, False, False),
    ("dfbc_high_order_bodyrate", 10, True, False),
    ("dfbc_smooth_robust_attitude", 11, False, False),
    ("dfbc_smooth_robust_bodyrate", 11, True, False),
    ("dfbc_dob_eso_disabled", 11, False, False),
    ("dfbc_dob_eso", 11, False, True),
):
    CONFIG[name] = {
        "backend": "p10_dfbc_family",
        "definition": "MOSIM_PX4CTRL_GENERATED_BACKEND_P10_DFBC_FAMILY",
        "cache_var": "MOSIM_PX4CTRL_P10_DFBC_FAMILY_GENERATED_DIR",
        "model": "MoSim_P10_DFBC_Family_CFunction_Sysblock",
        "symbol": "MosimPx4ctrlG9FamilyCStepScalar",
        "controller_id": controller_id,
        "closeout": f"Results/control_platform/p10_mworks_gap_closeout_20260718/dfbc_family/closeout/{name}_closeout.json",
        "bodyrate": bodyrate,
        "dob": dob,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_path(raw: str | Path) -> Path:
    text = str(raw).replace("\\", "/")
    drive = re.match(r"^([A-Za-z]):/(.*)$", text)
    if drive and os.name == "posix" and Path("/mnt").is_dir():
        text = f"/mnt/{drive.group(1).lower()}/{drive.group(2)}"
    return Path(os.path.normpath(text)).resolve()


def generated_bundle(code_dir: Path, model: str) -> tuple[str, dict[str, str], list[str]]:
    files = (f"{model}.c", f"{model}.h", f"{model}_data.c", f"{model}_private.h", "extern_inc/momodel_extern_ince1.c")
    digest = hashlib.sha256()
    hashes: dict[str, str] = {}
    missing: list[str] = []
    for relative in files:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--px4ctrl-workspace", type=Path, required=True)
    parser.add_argument("--generated-code-dir", type=Path, required=True)
    parser.add_argument("--controller-profile", choices=tuple(CONFIG), required=True)
    parser.add_argument("--runtime-log", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    cfg = CONFIG[args.controller_profile]
    root = normalized_path(args.project_root)
    workspace = normalized_path(args.px4ctrl_workspace)
    code_dir = normalized_path(args.generated_code_dir)
    errors: list[str] = []

    closeout_path = root / str(cfg["closeout"])
    try:
        closeout = json.loads(closeout_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        closeout = {}
        errors.append(f"invalid MWORKS closeout: {exc}")
    ladder = closeout.get("evidence_ladder", {})
    if closeout.get("status") != "passed" or any(
        ladder.get(key) != "passed" for key in (
            "graphical_sysblock_fixture", "check_model", "simulate_model",
            "result_variables_and_metrics", "official_generate_model_code", "generated_c_sil",
        )
    ):
        errors.append("MWORKS closeout is not passed through generated-C SIL")

    model = str(cfg["model"])
    bundle_hash, file_hashes, missing = generated_bundle(code_dir, model)
    if missing:
        errors.append("missing generated files: " + ", ".join(missing))
    cache_path = workspace / "build/CMakeCache.txt"
    flags_path = workspace / "build/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make"
    binary = workspace / "devel/lib/px4ctrl/px4ctrl_node"
    cache_text = cache_path.read_text(encoding="utf-8", errors="replace") if cache_path.is_file() else ""
    flags_text = flags_path.read_text(encoding="utf-8", errors="replace") if flags_path.is_file() else ""
    backend = cache_value(cache_text, "MOSIM_PX4CTRL_GENERATED_BACKEND")
    cache_dir = cache_value(cache_text, str(cfg["cache_var"]))
    if backend != cfg["backend"]:
        errors.append(f"CMake backend is {backend!r}, expected {cfg['backend']!r}")
    if cfg["definition"] not in flags_text:
        errors.append(f"build flags missing {cfg['definition']}")
    if cache_dir and normalized_path(cache_dir) != code_dir:
        errors.append("CMake generated directory mismatch")
    symbol_present = False
    if binary.is_file():
        nm = subprocess.run(["nm", "-C", str(binary)], text=True, capture_output=True, check=False)
        symbol_present = nm.returncode == 0 and str(cfg["symbol"]) in nm.stdout
    if not symbol_present:
        errors.append(f"px4ctrl binary lacks {cfg['symbol']}")

    log_text = args.runtime_log.read_text(encoding="utf-8", errors="replace") if args.runtime_log.is_file() else ""
    required_ack = (
        "[mosim_generated_runtime] backend=mworks_generated_c",
        f"build_backend={cfg['backend']}",
        f"build_backend_definition={cfg['definition']}",
        f"generated_model_name={model}",
        f"generated_source_sha256={bundle_hash}",
        f"runtime_loaded_symbol={model}::Step",
        f"controller_id={cfg['controller_id']}",
        f"controller_name={args.controller_profile}",
    )
    missing_ack = [fragment for fragment in required_ack if fragment not in log_text]
    if missing_ack:
        errors.append("runtime acknowledgement missing: " + ", ".join(missing_ack))
    if args.controller_profile.startswith("dfbc_"):
        expected_interface = "BODY_RATE_THRUST" if cfg["bodyrate"] else "ATTITUDE_THRUST"
        expected_dob = "enabled" if cfg["dob"] else "disabled"
        if f"output_interface={expected_interface}" not in log_text:
            errors.append("runtime output-interface acknowledgement mismatch")
        if f"disturbance_observer={expected_dob}" not in log_text:
            errors.append("runtime disturbance-observer acknowledgement mismatch")

    payload = {
        "schema": "mosim.p10.generated_runtime_provenance.v1",
        "status": "passed" if not errors else "failed",
        "controller": args.controller_profile,
        "backend": cfg["backend"],
        "controller_id": cfg["controller_id"],
        "output_interface": "BODY_RATE_THRUST" if cfg["bodyrate"] else "ATTITUDE_THRUST",
        "disturbance_observer": "enabled" if cfg["dob"] else "disabled",
        "generated_model_name": model,
        "generated_code_path": str(code_dir),
        "generated_code_sha256": bundle_hash,
        "generated_file_sha256": file_hashes,
        "mworks_closeout": str(closeout_path),
        "cmake_backend": backend,
        "cmake_generated_dir": cache_dir,
        "build_backend_definition": cfg["definition"] if cfg["definition"] in flags_text else None,
        "px4ctrl_executable": str(binary),
        "px4ctrl_executable_sha256": sha256_file(binary) if binary.is_file() else None,
        "binary_generated_symbol_present": symbol_present,
        "runtime_loaded_symbol": f"{model}::Step" if not missing_ack else None,
        "provenance_level": "runtime_acknowledged" if not errors else "build_only",
        "runtime_log": str(args.runtime_log.resolve()),
        "errors": errors,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
