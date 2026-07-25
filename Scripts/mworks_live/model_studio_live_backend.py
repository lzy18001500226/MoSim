#!/usr/bin/env python3
"""Fail-closed backend for the Model Studio MWORKS Live UI section."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts/mworks_live"))

from preflight_connection import Endpoint, run_preflight

CONTRACT = ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v1.json"
RT0_DIR = ROOT / "Results/control_platform/mworks_live_full_loop_20260719/rt0_accepted_50hz_v1"
RT0_ANALYSIS = RT0_DIR / "rt0_analysis.json"
RT0_INVOCATION = RT0_DIR / "rt0_invocation.json"
RT0_MODEL_ROOT = ROOT / "Models/MoSimQuadrotorModel/LiveIntegration"
CATALOG = ROOT / "Config/profiles/catalog.json"
PROFILES = {
    "official_pid": ROOT / "Config/profiles/experiments/mworks_live_official_pid_hover_50hz_v2.json",
    "official_pid_200hz": ROOT / "Config/profiles/experiments/mworks_live_official_pid_hover_200hz_v1.json",
    "official_pid_awff": ROOT / "Config/profiles/experiments/mworks_live_official_pid_awff_hover_50hz_v2.json",
}
PROFILE_CAPABILITIES = {
    "official_pid": {
        "contract": CONTRACT,
        "rt0_dir": RT0_DIR,
        "rate_hz": 50,
    },
    "official_pid_200hz": {
        "contract": ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v3_candidate_200hz.json",
        "rt0_dir": ROOT / "Results/control_platform/mworks_live_full_loop_20260719/rt0_200hz_v3_run6",
        "rate_hz": 200,
    },
    "official_pid_awff": {
        "contract": CONTRACT,
        "rt0_dir": RT0_DIR,
        "rate_hz": 50,
    },
}
FIELDS = (
    "accepted",
    "connection_ok",
    "reason_code",
    "profile_id",
    "profile_hash",
    "rt0_status",
    "output_rate_hz",
    "latency_p99_ms",
    "requested_rate_hz",
    "target_host",
    "rt1_udp_port",
    "ros_master_reachable",
    "rt1_reachable",
    "rtt_p95_ms",
    "payload_bytes_per_s",
    "wire_bytes_per_s",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_source_hashes(model_name: str) -> dict[str, str]:
    files = [
        RT0_MODEL_ROOT / "package.mo",
        RT0_MODEL_ROOT / "package.order",
        RT0_MODEL_ROOT / "RT0RealtimeProbe.mo",
        RT0_MODEL_ROOT / "Resources/Include/mosim_mworks_live_rt0_bridge.h",
    ]
    if model_name.endswith("50Hz"):
        files.append(RT0_MODEL_ROOT / "RT0RealtimeProbe50Hz.mo")
    if model_name.endswith("200Hz"):
        files.extend([
            RT0_MODEL_ROOT / "RT0RealtimeProbe200Hz.mo",
            RT0_MODEL_ROOT / "Resources/Include/mosim_mworks_live_rt0_timer_resolution.h",
        ])
    return {path.relative_to(ROOT).as_posix(): sha256(path) for path in files}


def rt0_authoritative_hashes(values: dict[str, str]) -> dict[str, str]:
    # package.order is a discoverability index. Adding a later RT1 model must
    # not invalidate unchanged RT0 executable sources and bridge code.
    return {path: digest for path, digest in values.items() if not path.endswith("/package.order")}


def capability(profile_key: str) -> dict[str, Any]:
    profile_path = PROFILES[profile_key]
    capability_config = PROFILE_CAPABILITIES[profile_key]
    contract_path = Path(capability_config["contract"])
    rt0_dir = Path(capability_config["rt0_dir"])
    rt0_analysis = rt0_dir / "rt0_analysis.json"
    rt0_invocation = rt0_dir / "rt0_invocation.json"
    accepted_rate_hz = int(capability_config["rate_hz"])
    wrapper = load_json(profile_path)
    profile = wrapper["experiment_profile"]
    result = {
        "accepted": False,
        "connection_ok": False,
        "reason_code": "rt0_not_validated",
        "profile_id": profile.get("id", ""),
        "profile_hash": canonical_hash(profile),
        "rt0_status": "not_validated",
        "output_rate_hz": "",
        "latency_p99_ms": "",
        "requested_rate_hz": accepted_rate_hz,
        "target_host": "",
        "rt1_udp_port": "",
        "ros_master_reachable": "",
        "rt1_reachable": "",
        "rtt_p95_ms": "",
        "payload_bytes_per_s": "",
        "wire_bytes_per_s": "",
    }
    if not rt0_analysis.is_file() or not rt0_invocation.is_file():
        return result
    analysis = load_json(rt0_analysis)
    invocation = load_json(rt0_invocation)
    metrics = analysis.get("metrics") if isinstance(analysis.get("metrics"), dict) else {}
    result["rt0_status"] = "passed" if analysis.get("ok") is True else "failed"
    result["output_rate_hz"] = metrics.get("output_rate_hz", "")
    result["latency_p99_ms"] = metrics.get("latency_p99_ms", "")
    if analysis.get("ok") is not True:
        result["reason_code"] = "rt0_failed"
        return result
    if (
        invocation.get("status") != "passed"
        or invocation.get("sim_mode") != 2
        or invocation.get("execution_source") != "mworks_sysplorer_realtime"
        or invocation.get("contract_sha256") != sha256(contract_path)
    ):
        result["accepted"] = False
        result["rt0_status"] = "failed"
        result["reason_code"] = "rt0_provenance_mismatch"
        return result
    current_source_hashes = model_source_hashes(str(invocation.get("model_name", "")))
    recorded_source_hashes = invocation.get("model_source_hashes")
    frequency = load_json(CATALOG).get("frequency_profiles", {}).get(profile.get("frequency_profile"))
    if (
        not isinstance(recorded_source_hashes, dict)
        or invocation.get("model_bundle_sha256") != canonical_hash(recorded_source_hashes)
        or rt0_authoritative_hashes(recorded_source_hashes) != rt0_authoritative_hashes(current_source_hashes)
        or not isinstance(frequency, dict)
        or invocation.get("frequency_profile_id") != profile.get("frequency_profile")
        or invocation.get("frequency_profile_hash") != canonical_hash(frequency)
    ):
        result["rt0_status"] = "failed"
        result["reason_code"] = "rt0_provenance_mismatch"
        return result
    if profile.get("profile_status") not in {"active", "accepted"}:
        result["reason_code"] = "live_profile_not_published"
        return result
    if profile.get("capability_status") != "rt0_validated":
        result["reason_code"] = "rt0_not_validated"
        return result
    result["accepted"] = True
    result["reason_code"] = "mworks_live_capability_ready"
    return result


def connection_preflight(
    *,
    host: str,
    port: int,
    ros_master_uri: str,
    local_advertised_ip: str,
    requested_rate_hz: int,
) -> dict[str, Any]:
    probe = run_preflight(
        Endpoint(host, port, ros_master_uri, local_advertised_ip, requested_rate_hz),
        timeout_s=0.35,
        sample_count=5,
    )
    ros = probe.get("ros_master") if isinstance(probe.get("ros_master"), dict) else {}
    rt1 = probe.get("rt1") if isinstance(probe.get("rt1"), dict) else {}
    return {
        "accepted": bool(probe.get("accepted")),
        "connection_ok": bool(probe.get("accepted")),
        "reason_code": str(probe.get("reason_code", "connection_preflight_failed")),
        "profile_id": "",
        "profile_hash": "",
        "rt0_status": "not_checked",
        "output_rate_hz": "",
        "latency_p99_ms": "",
        "requested_rate_hz": requested_rate_hz,
        "target_host": host,
        "rt1_udp_port": port,
        "ros_master_reachable": ros.get("reachable", ""),
        "rt1_reachable": rt1.get("reachable", ""),
        "rtt_p95_ms": rt1.get("rtt_p95_ms", ""),
        "payload_bytes_per_s": rt1.get("measured_payload_bytes_per_s", ""),
        "wire_bytes_per_s": rt1.get("estimated_ip_udp_wire_bytes_per_s", ""),
        "preflight": probe,
    }


def prepare_with_connection(
    profile_key: str,
    *,
    host: str,
    port: int,
    ros_master_uri: str,
    local_advertised_ip: str,
    requested_rate_hz: int,
) -> dict[str, Any]:
    accepted_rate_hz = int(PROFILE_CAPABILITIES[profile_key]["rate_hz"])
    if requested_rate_hz != accepted_rate_hz:
        result = capability(profile_key)
        result.update(
            {
                "accepted": False,
                "requested_rate_hz": requested_rate_hz,
                "target_host": host,
                "rt1_udp_port": port,
                "reason_code": "prepare_blocked:requested_rate_unvalidated",
            }
        )
        return result
    result = capability(profile_key)
    if not result["accepted"]:
        result["reason_code"] = f"prepare_blocked:{result['reason_code']}"
        return result
    connection = connection_preflight(
        host=host,
        port=port,
        ros_master_uri=ros_master_uri,
        local_advertised_ip=local_advertised_ip,
        requested_rate_hz=requested_rate_hz,
    )
    identity = {key: result[key] for key in ("profile_id", "profile_hash", "rt0_status", "output_rate_hz", "latency_p99_ms")}
    connection.update(identity)
    if not connection["accepted"]:
        connection["reason_code"] = f"prepare_blocked:{connection['reason_code']}"
    else:
        connection["reason_code"] = "prepare_connection_gate_passed"
    return connection


def validate_profile(profile_key: str) -> dict[str, Any]:
    import validate_live_contract

    profile_path = PROFILES[profile_key]
    validation = validate_live_contract.validate(Path(PROFILE_CAPABILITIES[profile_key]["contract"]), [profile_path])
    result = capability(profile_key)
    if not validation.get("ok"):
        result["accepted"] = False
        result["reason_code"] = "live_profile_contract_invalid"
    elif result["reason_code"] == "rt0_not_validated":
        result["reason_code"] = "profile_valid_rt0_pending"
    return result


def render_tsv(result: dict[str, Any]) -> str:
    values = []
    for field in FIELDS:
        value = result.get(field, "")
        if isinstance(value, bool):
            value = "true" if value else "false"
        values.append(str(value).replace("\t", " ").replace("\r", " ").replace("\n", " "))
    return "\t".join(values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "validate", "connection-test", "prepare"))
    parser.add_argument("--profile", choices=tuple(PROFILES), default="official_pid_200hz")
    parser.add_argument("--format", choices=("json", "tsv"), default="tsv")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49020)
    parser.add_argument("--ros-master-uri", default="http://127.0.0.1:11311")
    parser.add_argument("--local-advertised-ip", default="auto")
    parser.add_argument("--rate-hz", type=int, choices=(50, 100, 200), default=200)
    args = parser.parse_args()
    if args.action == "validate":
        result = validate_profile(args.profile)
    elif args.action == "connection-test":
        result = connection_preflight(
            host=args.host,
            port=args.port,
            ros_master_uri=args.ros_master_uri,
            local_advertised_ip=args.local_advertised_ip,
            requested_rate_hz=args.rate_hz,
        )
    elif args.action == "prepare":
        result = prepare_with_connection(
            args.profile,
            host=args.host,
            port=args.port,
            ros_master_uri=args.ros_master_uri,
            local_advertised_ip=args.local_advertised_ip,
            requested_rate_hz=args.rate_hz,
        )
    else:
        result = capability(args.profile)
    print(json.dumps(result, ensure_ascii=True, indent=2) if args.format == "json" else render_tsv(result))
    # The APP must always receive the structured blocker instead of losing it
    # through a process exception. accepted remains the authoritative field.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
