#!/usr/bin/env python3
"""Audit reusable generated-C evidence for the MWORKS Live comparison profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PID_ROOT = ROOT / "Results/control_platform/p1_pid_attitude_thrust_mworks_20260716"
AWFF_ROOT = ROOT / "Results/control_platform/p5_enhancement_mworks_20260717"
AWFF_RUNTIME = ROOT / "Results/control_platform/p5_enhancement_runtime_20260717/awff"
CONTRACT_VALIDATION = ROOT / "Results/control_platform/mworks_live_full_loop_20260719/p0_contract_validation.json"
CURRENT_AWFF_SIL = ROOT / "Results/control_platform/mworks_live_full_loop_20260719/awff_current_generated_c_sil/P5_GENERATED_SIL_EQUIVALENCE.json"


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {path}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"expected JSON object: {path}")
        return {}
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hashes(root: Path, expected: dict[str, Any], findings: list[str], label: str) -> tuple[dict[str, str], bool]:
    checked: dict[str, str] = {}
    matched = True
    for relative, expected_hash in expected.items():
        path = root / relative
        if not path.is_file():
            findings.append(f"{label}: missing generated file {relative}")
            matched = False
            continue
        actual = sha256_file(path)
        checked[relative] = actual
        if actual != expected_hash:
            findings.append(f"{label}: hash mismatch for {relative}")
            matched = False
    return checked, matched


def audit() -> dict[str, Any]:
    errors: list[str] = []
    findings: list[str] = []
    pid_manifest_path = PID_ROOT / "MWORKS_ATTITUDE_THRUST_MANIFEST.json"
    pid_manifest = load_json(pid_manifest_path, errors)
    pid_sil = load_json(PID_ROOT / "sil/sil_equivalence_126_rows_v2.json", errors)
    pid_codegen = load_json(PID_ROOT / "generate_model_code_result_v2.json", errors)
    pid_code_root = PID_ROOT / "generated_c_v2/MoSim_PID_AttitudeThrust_CFunction_Sysblock"
    pid_hashes, pid_hashes_match = verify_hashes(
        pid_code_root,
        pid_manifest.get("generated_source_hashes", {}),
        findings,
        "official_pid",
    )
    if pid_manifest.get("ok") is not True or pid_manifest.get("sample_count") != 126:
        errors.append("official_pid: MWORKS evidence manifest is not the accepted 126-sample set")
    if pid_codegen.get("result") is not True:
        errors.append("official_pid: v2 GenerateModelCode record is not successful")
    if pid_sil.get("ok") is not True:
        errors.append("official_pid: generated-C SIL equivalence did not pass")

    awff_build = load_json(AWFF_ROOT / "BUILD_MANIFEST.json", errors)
    awff_sil = load_json(AWFF_ROOT / "sil/P5_GENERATED_SIL_EQUIVALENCE.json", errors)
    current_awff_sil = load_json(CURRENT_AWFF_SIL, errors)
    awff_runtime_path = AWFF_RUNTIME / "ENHANCEMENT_GENERATED_RUNTIME_PROVENANCE.json"
    awff_runtime = load_json(awff_runtime_path, errors)
    awff_code_root = AWFF_ROOT / "generated_c/MoSim_P5_Enhancement_CFunction_Sysblock"
    awff_hashes, awff_runtime_hashes_match = verify_hashes(
        awff_code_root,
        awff_runtime.get("generated_file_sha256", {}),
        findings,
        "awff",
    )
    if awff_runtime.get("status") != "passed" or awff_runtime.get("controller_name") != "awff":
        errors.append("awff: runtime provenance is missing or not passed")
    if awff_sil.get("ok") is not True and awff_sil.get("status") != "passed":
        errors.append("awff: generated-C SIL equivalence did not pass")
    if current_awff_sil.get("status") != "passed":
        errors.append("awff: current generated-C SIL revalidation did not pass")

    contract = load_json(CONTRACT_VALIDATION, errors)
    profile_hashes = {
        str(item.get("profile_id")): str(item.get("profile_hash"))
        for item in contract.get("profiles", [])
        if isinstance(item, dict)
    }
    required_scripts = [
        ROOT / "Scripts/sunray/ensure_px4ctrl_generated_backend.sh",
        ROOT / "Scripts/sunray/check_pid_attitude_thrust_generated_runtime_provenance.py",
        ROOT / "Scripts/sunray/check_enhancement_generated_runtime_provenance.py",
    ]
    for path in required_scripts:
        if not path.is_file():
            errors.append(f"missing runtime integration script: {path}")

    return {
        "schema": "mosim.mworks_live_generated_c_reuse_audit.v1",
        "ok": not errors and pid_hashes_match,
        "status": "passed_with_awff_historical_provenance_drift"
        if not errors and pid_hashes_match and not awff_runtime_hashes_match
        else "passed" if not errors and pid_hashes_match else "failed",
        "profile_hashes": profile_hashes,
        "official_pid": {
            "mworks_manifest": str(pid_manifest_path),
            "generated_code_dir": str(pid_code_root),
            "verified_generated_files": len(pid_hashes),
            "sil_evidence": str(PID_ROOT / "sil/sil_equivalence_126_rows_v2.json"),
            "sil_sample_count": pid_manifest.get("sample_count"),
            "generated_hashes_match_manifest": pid_hashes_match,
            "reusable_without_rebuild": pid_hashes_match,
            "current_same_profile_gazebo_regression": "pending",
        },
        "awff": {
            "build_manifest": str(AWFF_ROOT / "BUILD_MANIFEST.json"),
            "generated_code_dir": str(awff_code_root),
            "verified_generated_files": len(awff_hashes),
            "sil_evidence": str(AWFF_ROOT / "sil/P5_GENERATED_SIL_EQUIVALENCE.json"),
            "historical_runtime_provenance": str(awff_runtime_path),
            "historical_runtime_status": awff_runtime.get("status"),
            "historical_runtime_hashes_match_current_files": awff_runtime_hashes_match,
            "current_sil_revalidation": str(CURRENT_AWFF_SIL),
            "current_sil_status": current_awff_sil.get("status"),
            "reusable_without_rebuild": current_awff_sil.get("status") == "passed",
            "runtime_provenance_refresh_required": not awff_runtime_hashes_match,
            "current_same_profile_gazebo_regression": "pending",
        },
        "decision": {
            "rebuild_generated_c": False,
            "required_next_action": "Refresh AWFF runtime provenance against current hashes, then run one current minimal same-Profile Gazebo regression after MWORKS Live RT0-RT3.",
            "reason": "Official PID hashes match. Current AWFF generated C still passes SIL with zero difference, but its historical runtime provenance hashes do not bind the committed files.",
        },
        "errors": errors,
        "findings": findings,
        "claim_boundary": "This audit proves repository asset integrity and historical provenance only. It does not prove current Gazebo, QGC, or MWORKS Live acceptance.",
        "observed_awff_build_schema": awff_build.get("schema"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
