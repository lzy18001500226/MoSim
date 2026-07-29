#!/usr/bin/env python3
"""Bind an accepted RT0 trace to the actual dedicated Sysplorer invocation."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = ROOT / "Results/control_platform/mworks_live_full_loop_20260719/rt0"
MODEL_ROOT = ROOT / "Models/MoSimQuadrotorModel/LiveIntegration"
DEFAULT_CONTRACT = ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v1.json"
CATALOG = ROOT / "Config/profiles/catalog.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def model_source_hashes(model_name: str) -> dict[str, str]:
    files = [
        MODEL_ROOT / "package.mo",
        MODEL_ROOT / "package.order",
        MODEL_ROOT / "RT0RealtimeProbe.mo",
        MODEL_ROOT / "Resources/Include/mosim_mworks_live_rt0_bridge.h",
    ]
    if model_name.endswith("50Hz"):
        files.append(MODEL_ROOT / "RT0RealtimeProbe50Hz.mo")
    if model_name.endswith("200Hz"):
        files.extend([
            MODEL_ROOT / "RT0RealtimeProbe200Hz.mo",
            MODEL_ROOT / "Resources/Include/mosim_mworks_live_rt0_timer_resolution.h",
        ])
    return {path.relative_to(ROOT).as_posix(): sha256(path) for path in files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--sysplorer-port", type=int, required=True)
    parser.add_argument("--processed-frames", type=int, required=True)
    parser.add_argument("--model-name", default="MoSimQuadrotorModel.Deployment.RT0RealtimeProbe")
    parser.add_argument("--frequency-profile", default="attitude_thrust_100hz_v1")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    analysis = load(args.output_dir / "rt0_analysis.json")
    capture = load(args.output_dir / "rt0_capture.json")
    if analysis.get("ok") is not True:
        raise SystemExit("RT0 analysis did not pass")
    if int(capture.get("response_count", 0)) < 1000:
        raise SystemExit("RT0 capture has fewer than 1000 responses")
    if args.processed_frames < 1000:
        raise SystemExit("Sysplorer result reports fewer than 1000 processed frames")
    frequency = load(CATALOG).get("frequency_profiles", {}).get(args.frequency_profile)
    if not isinstance(frequency, dict):
        raise SystemExit(f"Unknown frequency profile: {args.frequency_profile}")
    source_hashes = model_source_hashes(args.model_name)
    invocation = {
        "schema": "mosim.mworks_live_rt0_invocation.v1",
        "status": "passed",
        "execution_source": "mworks_sysplorer_realtime",
        "api": "Sysplorer SimulateModel",
        "sim_mode": 2,
        "dedicated_sysplorer_port": args.sysplorer_port,
        "model_name": args.model_name,
        "model_source_hashes": source_hashes,
        "model_bundle_sha256": canonical_hash(source_hashes),
        "contract_path": args.contract.resolve().relative_to(ROOT).as_posix(),
        "contract_sha256": sha256(args.contract),
        "frequency_profile_id": args.frequency_profile,
        "frequency_profile_hash": canonical_hash(frequency),
        "processed_frames_result": args.processed_frames,
        "capture_response_count": capture["response_count"],
        "analysis_path": (args.output_dir / "rt0_analysis.json").resolve().relative_to(ROOT).as_posix(),
        "captured_at_unix": time.time(),
        "claim_boundary": "RT0 transport/timing capability only; no Gazebo or flight-control claim.",
    }
    output = args.output_dir / "rt0_invocation.json"
    if output.exists():
        runtime_output = args.output_dir / "rt0_runtime_invocation.json"
        runtime_output.write_bytes(output.read_bytes())
    output.write_text(json.dumps(invocation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(invocation, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
