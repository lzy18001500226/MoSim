#!/usr/bin/env python3
"""Build a hash-bound, MWORKS-only RT1 graphical bridge source baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SOURCE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "Models/MoSimQuadrotorModel/package.mo": ("package MoSimQuadrotorModel",),
    "Models/MoSimQuadrotorModel/package.order": ("RealTime",),
    "Models/MoSimQuadrotorModel/Control/package.mo": ("package Control",),
    "Models/MoSimQuadrotorModel/Control/package.order": ("PID", "Px4Ctrl"),
    "Models/MoSimQuadrotorModel/Control/PID/package.mo": ("package PID",),
    "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.mo": ("package Px4Ctrl",),
    "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.order": (
        "Px4CtrlOuterLoopGraphicalSysblock",
        "Px4CtrlAttitudeThrustSysblockAdapter",
    ),
    "Models/MoSimQuadrotorModel/RealTime/package.mo": ("package RealTime",),
    "Models/MoSimQuadrotorModel/RealTime/package.order": (
        "MworksRt1Px4CtrlGraphicalShadow100Hz",
    ),
    "Models/MoSimQuadrotorModel/Parameters/Sunray150Parameters.mo": (
        "record Sunray150Parameters",
    ),
    "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlOuterLoopGraphicalSysblock.mo": (
        "extends ModelWorkspace;",
        "SysblockVersion=\"1.0\"",
    ),
    "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlAttitudeThrustSysblockAdapter.mo": (
        "Px4CtrlOuterLoopGraphicalSysblock outer_loop",
        "desired_acceleration[1] = graphical_desired_acceleration[1];",
    ),
    "Models/MoSimQuadrotorModel/RealTime/MworksRt1Px4CtrlGraphicalShadow100Hz.mo": (
        "mosim_mworks_rt1_graphical_exchange",
        "pendingCommand := pre(graphicalStateTicks) >= 1;",
    ),
    "Models/MoSimQuadrotorModel/RealTime/Resources/Include/mosim_mworks_live_rt1_bridge.h": (
        "mosim_mworks_live_rt1_receive",
        "mosim_mworks_live_rt1_send",
    ),
    "Models/MoSimQuadrotorModel/RealTime/Resources/Include/mosim_mworks_rt1_graphical_exchange.h": (
        "mosim_mworks_rt1_graphical_exchange",
    ),
    "Scripts/mworks/check_rt1_graphical_bridge.py": (
        "adapter_uses_graphical_output_only",
        "graphical_core_startup_gate",
    ),
    "Scripts/mworks/run_rt1_graphical_loopback_mcp.py": (
        "BATCH_SIM_MODE = 2",
        "rt2_outer_loop_excitation",
    ),
    "Scripts/mworks_live/rt1_contract.py": ("class StateReferenceFrame", "class CommandFrame"),
    "Scripts/mworks_live/run_rt1_mworks_graphical_loopback.py": (
        "rt2_outer_loop_excitation",
        "sent_frames",
    ),
    "Scripts/mworks_live/analyze_rt1_graphical_equivalence.py": (
        "analysis_of_mworks_local_udp_loopback_fixture",
        "rt2_requires_identity_attitude",
    ),
}


def source_record(relative_path: str, required_tokens: tuple[str, ...]) -> dict[str, Any]:
    path = ROOT / relative_path
    record: dict[str, Any] = {
        "path": relative_path,
        "exists": path.is_file(),
        "required_tokens": list(required_tokens),
    }
    if not path.is_file():
        record["missing_tokens"] = list(required_tokens)
        return record
    data = path.read_bytes()
    text = data.decode("utf-8")
    record.update(
        {
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "missing_tokens": [token for token in required_tokens if token not in text],
        }
    )
    return record


def git_state(relative_paths: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "status", "--short", "--", *relative_paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "available": completed.returncode == 0,
        "entries": completed.stdout.splitlines(),
        "error": completed.stderr.strip() or None,
        "clean_for_release": completed.returncode == 0 and not completed.stdout.strip(),
    }


def build() -> dict[str, Any]:
    records = [
        source_record(relative_path, required_tokens)
        for relative_path, required_tokens in SOURCE_REQUIREMENTS.items()
    ]
    failures = [
        {
            "path": record["path"],
            "reason_code": "missing_source" if not record["exists"] else "missing_required_token",
            "missing_tokens": record["missing_tokens"],
        }
        for record in records
        if not record["exists"] or record["missing_tokens"]
    ]
    git = git_state(list(SOURCE_REQUIREMENTS))
    source_snapshot_passed = not failures
    return {
        "schema": "mosim.mworks_rt1_graphical_deployment_baseline.v1",
        "source": "static_hash_bound_source_closure",
        "working_directory": str(ROOT),
        "model_name": "MoSimQuadrotorModel.RealTime.MworksRt1Px4CtrlGraphicalShadow100Hz",
        "source_snapshot_passed": source_snapshot_passed,
        "release_ready": False,
        "files": records,
        "git_state": git,
        "failures": failures,
        "reproduction": {
            "static_check": "python Scripts/mworks/check_rt1_graphical_bridge.py",
            "static_tests": "python -m pytest Scripts/tests/test_rt1_graphical_bridge_static.py Scripts/tests/test_rt1_graphical_equivalence.py -q",
            "mworks_check": "python Scripts/mworks/check_rt1_graphical_bridge_mcp.py --sysplorer-api-port <existing-port>",
            "rt1_loopback": "python Scripts/mworks/run_rt1_graphical_loopback_mcp.py --sysplorer-api-port <existing-port> --simulation-duration-s 2 --minimum-responses 20",
            "rt2_loopback": "python Scripts/mworks/run_rt1_graphical_loopback_mcp.py --sysplorer-api-port <existing-port> --fixture-profile rt2_outer_loop_excitation --simulation-duration-s 2 --minimum-responses 20",
            "rt2_analysis": "python Scripts/mworks_live/analyze_rt1_graphical_equivalence.py <RT2_LOCAL_UDP_LOOPBACK.json> --output <RT2_GRAPHICAL_EQUIVALENCE.json>",
        },
        "runtime_evidence_status": "not_run_requires_clean_licensed_mworks_session",
        "claim_boundary": [
            "This is a hash-bound source closure, not a live MWORKS runtime result.",
            "release_ready remains false until source ownership is integrated and live MWORKS evidence passes.",
            "No Gazebo, ROS, PX4, MAVROS, planner, localization, closed-loop, or flight claim is made.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/RT1_DEPLOYMENT_BASELINE.json",
    )
    args = parser.parse_args()
    output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    output.parent.mkdir(parents=True, exist_ok=True)
    result = build()
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_snapshot_passed": result["source_snapshot_passed"],
        "release_ready": result["release_ready"],
        "json_output": str(output),
    }, ensure_ascii=False))
    return 0 if result["source_snapshot_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
