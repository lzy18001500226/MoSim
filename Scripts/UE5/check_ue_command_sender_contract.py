#!/usr/bin/env python3
"""Check the source-level UE command sender contract.

This is a static/source-level gate. It proves the UE Bridge exposes a narrow
Blueprint-callable command sender that builds mosim.ue_command.v1 packets and
rejects pose-overwrite command kinds. It does not prove live UE, MWORKS, or
ROS2 runtime acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h"
SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
TYPES = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksTypes.h"
COMMAND_SCHEMA = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"


FORBIDDEN = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}
REQUIRED_ALLOWED = {
    "controller_select",
    "planner_select",
    "wind_profile",
    "motor_fault",
    "sensor_mode",
    "scenario_reset",
    "start_goal_update",
    "recording",
    "scene_switch",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "source-level UE command sender only; no live UE runtime ack is claimed",
    ]
    header = read(HEADER) if HEADER.exists() else ""
    source = read(SOURCE) if SOURCE.exists() else ""
    types = read(TYPES) if TYPES.exists() else ""
    schema = json.loads(COMMAND_SCHEMA.read_text(encoding="utf-8"))

    if not header:
        issues.append(f"missing header: {HEADER.relative_to(ROOT).as_posix()}")
    if not source:
        issues.append(f"missing source: {SOURCE.relative_to(ROOT).as_posix()}")
    if "UQuadrotorMworksUdpCommandSenderComponent" not in header + source:
        issues.append("command sender component class is missing")
    for symbol in ["SendCommand", "BuildCommandPacket"]:
        if symbol not in header:
            issues.append(f"missing Blueprint-callable command surface: {symbol}")
    for symbol in ["FQuadrotorMworksCommandGuard", "FQuadrotorMworksCommandResult"]:
        if symbol not in types:
            issues.append(f"missing command type: {symbol}")
    if "mosim.ue_command.v1" not in source:
        issues.append("source does not emit mosim.ue_command.v1")
    if "require_mworks_ack" not in source or "require_ros2_ack" not in source:
        issues.append("command guard ack fields are not serialized")
    if "SendTo(" not in source or "FUdpSocketBuilder" not in source:
        issues.append("UDP sender path is missing")

    for kind in REQUIRED_ALLOWED:
        if f'TEXT("{kind}")' not in source:
            issues.append(f"allowed command kind missing from C++ sender: {kind}")
    for kind in FORBIDDEN:
        if f'TEXT("{kind}")' not in source:
            issues.append(f"forbidden command kind missing from C++ sender: {kind}")
    if "forbidden_pose_command" not in source:
        issues.append("forbidden pose commands must reject with forbidden_pose_command")
    for blocked in ["SetActorLocation", "SetActorTransform", "TeleportTo", "AddActorWorldOffset"]:
        if blocked in source:
            issues.append(f"command sender must not directly move actors: {blocked}")

    schema_allowed = set(schema["command"]["allowed_kinds"])
    schema_forbidden = set(schema["command"]["forbidden_kinds"])
    if not REQUIRED_ALLOWED <= schema_allowed:
        issues.append("schema allowed command set is missing sender-supported commands")
    if not FORBIDDEN <= schema_forbidden:
        issues.append("schema forbidden command set is missing sender-rejected commands")

    report = {
        "schema": "mosim.ue_command_sender_source_contract.v1",
        "ok": not issues,
        "source": "source_level_static_check",
        "header": HEADER.relative_to(ROOT).as_posix(),
        "source_cpp": SOURCE.relative_to(ROOT).as_posix(),
        "types_header": TYPES.relative_to(ROOT).as_posix(),
        "allowed_kinds": sorted(REQUIRED_ALLOWED),
        "forbidden_kinds": sorted(FORBIDDEN),
        "not_runtime_ue_console": True,
        "runtime_ack_required_before_acceptance": True,
        "no_pose_overwrite_status": "pass" if not issues else "unknown",
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
