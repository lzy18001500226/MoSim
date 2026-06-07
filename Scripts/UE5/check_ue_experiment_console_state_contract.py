#!/usr/bin/env python3
"""Check the UE Experiment Console source-level command state component.

This is a static/fixture smoke gate only. It does not open UE, implement a
runtime echo socket receiver, call MWORKS, publish ROS2 topics, or prove live
runtime acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
SENDER_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp"

REQUIRED_FIELDS = {
    "RunId",
    "RequestId",
    "Seq",
    "CommandKind",
    "UiState",
    "AckAuthority",
    "Reason",
    "Source",
    "QualityStatus",
    "bAcceptedAsRuntimeAck",
    "NoPoseOverwriteStatus",
}
REQUIRED_METHODS = {
    "RecordPendingCommandFromPacketJson",
    "ApplyCommandEchoJson",
    "GetCommandStates",
    "ClearCommandStates",
}
REQUIRED_STRINGS = {
    "mosim.ue_command.v1",
    "mosim.ue_command_echo.v1",
    "pending",
    "accepted",
    "rejected",
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
    "smoke_only",
    "pending_no_runtime_echo",
    "awaiting_matching_echo",
    "accepted_as_runtime_ack",
    "bAcceptedAsRuntimeAck",
    "no_matching_command_request",
    "unsupported_echo_schema",
    "missing_ack_authority",
    "no_pose_overwrite_not_pass",
    "seq_mismatch",
    "command_kind_mismatch",
}
FORBIDDEN_SOURCE_PATTERNS = {
    "SetActorLocation",
    "SetActorTransform",
    "TeleportTo",
    "AddActorWorldOffset",
    "BindAxis",
    "BindAction",
    "InputComponent",
    "EnhancedInput",
    "UInputAction",
}
FORBIDDEN_RUNTIME_RECEIVER_PATTERNS = {
    "RecvFrom(",
    "FUdpSocketReceiver",
    "AsNonBlocking",
}
NON_LIVE_SOURCE_LABELS = {
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "source-level console state component only; no live UE runtime ack is claimed",
        "runtime socket echo receiver is intentionally out of scope",
    ]

    header = read(HEADER)
    source = read(SOURCE)
    sender_header = read(SENDER_HEADER)
    sender_source = read(SENDER_SOURCE)
    combined = header + "\n" + source
    sender_combined = sender_header + "\n" + sender_source

    if not header:
        issues.append(f"missing header: {HEADER.relative_to(ROOT).as_posix()}")
    if not source:
        issues.append(f"missing source: {SOURCE.relative_to(ROOT).as_posix()}")
    if "UQuadrotorMworksExperimentConsoleStateComponent" not in combined:
        issues.append("missing UQuadrotorMworksExperimentConsoleStateComponent")
    if "FQuadrotorMworksExperimentConsoleCommandState" not in combined:
        issues.append("missing FQuadrotorMworksExperimentConsoleCommandState")
    if "UQuadrotorMworksUdpCommandSenderComponent" not in sender_combined:
        issues.append("existing UDP sender component is not available as separate sender-only dependency")
    if "ApplyCommandEchoJson" in sender_combined:
        issues.append("sender component must remain sender-only and not parse echo rows")

    for field in sorted(REQUIRED_FIELDS):
        if field not in header:
            issues.append(f"missing command lifecycle field: {field}")
    for method in sorted(REQUIRED_METHODS):
        if method not in header:
            issues.append(f"missing component method: {method}")
    for text in sorted(REQUIRED_STRINGS):
        if text not in combined:
            issues.append(f"missing contract string or logic: {text}")
    for blocked in sorted(FORBIDDEN_SOURCE_PATTERNS):
        if blocked in combined:
            issues.append(f"console state component must not expose actor/input pose control: {blocked}")
    for blocked in sorted(FORBIDDEN_RUNTIME_RECEIVER_PATTERNS):
        if blocked in combined:
            issues.append(f"runtime socket echo receiver is out of scope: {blocked}")
    non_live_source_coverage = {
        label: f'TEXT("{label}")' in source for label in sorted(NON_LIVE_SOURCE_LABELS)
    }
    for label, covered in non_live_source_coverage.items():
        if not covered:
            issues.append(f"non-live source label is not downgraded to smoke_only: {label}")

    if "RecordPendingCommandFromPacketJson" in source:
        pending_idx = source.find("RecordPendingCommandFromPacketJson")
        accepted_idx = source.find("accepted")
        rejected_idx = source.find("rejected")
        if accepted_idx != -1 and pending_idx != -1 and accepted_idx < pending_idx:
            warnings.append("accepted string appears before pending method due to helper definitions; static order is not semantic")
        if rejected_idx != -1 and pending_idx != -1 and rejected_idx < pending_idx:
            warnings.append("rejected string appears before pending method due to helper definitions; static order is not semantic")
    if "Result.bSent" in source:
        issues.append("console state component must not treat UDP send success as accepted/rejected state")

    report = {
        "schema": "mosim.ue_experiment_console_state_component_source_contract.v1",
        "ok": not issues,
        "source": "source_level_static_check",
        "component_header": HEADER.relative_to(ROOT).as_posix(),
        "component_source": SOURCE.relative_to(ROOT).as_posix(),
        "sender_remains_sender_only": "ApplyCommandEchoJson" not in sender_combined,
        "not_runtime_ue_console": True,
        "runtime_echo_receiver_implemented": False,
        "runtime_ack_required_before_acceptance": True,
        "accepted_rejected_source": "matching mosim.ue_command_echo.v1 only",
        "pending_source": "mosim.ue_command.v1 request only",
        "non_live_source_labels": sorted(NON_LIVE_SOURCE_LABELS),
        "non_live_source_coverage": non_live_source_coverage,
        "non_live_quality_status": "smoke_only",
        "non_live_accepted_as_runtime_ack": False,
        "no_pose_overwrite_status": "pass" if not issues else "unknown",
        "planner_ready": False,
        "closed_loop_ready": False,
        "issues": issues,
        "warnings": warnings,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
