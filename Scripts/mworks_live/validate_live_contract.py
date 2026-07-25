#!/usr/bin/env python3
"""Validate the frozen MWORKS Live ATTITUDE_THRUST contract and candidate profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v3_candidate_200hz.json"
DEFAULT_PROFILES = (
    ROOT / "Config/profiles/candidates/mworks_live_official_pid_hover_candidate_v1.json",
    ROOT / "Config/profiles/candidates/mworks_live_official_pid_awff_hover_candidate_v1.json",
)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate(contract_path: Path, profile_paths: list[Path]) -> dict[str, Any]:
    errors: list[str] = []
    contract = load_object(contract_path)
    if contract.get("schema") != "mosim.mworks_live_contract.v1":
        errors.append("contract schema must be mosim.mworks_live_contract.v1")
    if contract.get("control_boundary") != "ATTITUDE_THRUST":
        errors.append("control boundary must be ATTITUDE_THRUST")
    if contract.get("attitude_inner_owner") != "px4_builtin_attitude_rate_v1":
        errors.append("PX4 must own the attitude/rate inner loop in v1")

    frames = contract.get("frames", {})
    expected_frames = {
        "world": "ENU",
        "body": "FLU",
        "quaternion_order": "xyzw",
        "state_quaternion": "q_enu_from_flu_xyzw",
        "collective_thrust_input_unit": "N",
    }
    for key, expected in expected_frames.items():
        if frames.get(key) != expected:
            errors.append(f"frames.{key} must be {expected}")

    timing = contract.get("timing_candidates", {})
    if timing.get("minimum_sustained_rate_hz", 0) < 50:
        errors.append("minimum sustained rate must be at least 50 Hz")
    if timing.get("rt0_status") != "not_validated":
        errors.append("RT0 must remain not_validated until runtime evidence passes")
    if timing.get("command_stale_ms", 0) > timing.get("failsafe_escalation_ms", 0):
        errors.append("command stale threshold cannot exceed failsafe escalation")

    rt0 = contract.get("rt0_acceptance", {})
    if rt0.get("required_execution_source") != "mworks_sysplorer_realtime":
        errors.append("RT0 must require the real Sysplorer realtime execution source")
    if rt0.get("required_sim_mode") != 2:
        errors.append("RT0 must require Sysplorer sim_mode=2")

    profiles: list[dict[str, Any]] = []
    for path in profile_paths:
        wrapper = load_object(path)
        profile = wrapper.get("experiment_profile")
        if not isinstance(profile, dict):
            errors.append(f"{path}: missing experiment_profile")
            continue
        profiles.append({"path": str(path), "profile": profile})
        if profile.get("controller_backend") != "mworks_live":
            errors.append(f"{path}: controller_backend must be mworks_live")
        if profile.get("live_contract_id") != contract.get("contract_id"):
            errors.append(f"{path}: live_contract_id mismatch")
        if profile.get("attitude_inner_owner") != contract.get("attitude_inner_owner"):
            errors.append(f"{path}: attitude_inner_owner mismatch")
        capability_status = profile.get("capability_status")
        profile_status = profile.get("profile_status")
        if capability_status == "not_validated":
            if profile_status != "blocked":
                errors.append(f"{path}: unvalidated live profile must remain blocked")
        elif capability_status == "rt0_validated":
            if profile_status not in {"active", "accepted"}:
                errors.append(f"{path}: RT0-validated live profile must be active or accepted")
            expected_frequency = {
                "mworks_live_attitude_thrust_v1": "attitude_thrust_50hz_v1",
                "mworks_live_attitude_thrust_v3_candidate_200hz": "attitude_thrust_200hz_candidate_v2",
            }.get(contract.get("contract_id"))
            if expected_frequency is None or profile.get("frequency_profile") != expected_frequency:
                errors.append(f"{path}: RT0 validation frequency does not match the live contract")
            evidence = profile.get("rt0_evidence")
            if not evidence:
                errors.append(f"{path}: RT0-validated live profile must name its evidence")
            elif not (ROOT / str(evidence)).is_file():
                errors.append(f"{path}: RT0 evidence file does not exist")
        else:
            errors.append(f"{path}: unsupported capability_status={capability_status}")

    return {
        "schema": "mosim.mworks_live_contract_validation.v1",
        "ok": not errors,
        "contract_path": str(contract_path),
        "contract_hash": canonical_hash(contract),
        "profiles": [
            {
                "path": item["path"],
                "profile_id": item["profile"].get("id"),
                "profile_hash": canonical_hash(item["profile"]),
            }
            for item in profiles
        ],
        "errors": errors,
        "claim_boundary": "Static validation only; this does not pass RT0 or prove MWORKS Live flight.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--profile", action="append", type=Path, dest="profiles")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = validate(args.contract, args.profiles or list(DEFAULT_PROFILES))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
