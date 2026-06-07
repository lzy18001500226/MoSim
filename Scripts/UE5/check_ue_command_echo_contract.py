#!/usr/bin/env python3
"""Validate the UE Experiment Console command/echo contract.

The current UE surface is allowed to be a smoke-only placeholder, but it must
not be overclaimed as a runtime command channel. Runtime echo evidence requires
JSONL acknowledgements from MWORKS/ROS2 authority, not direct UE pose changes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_KINDS = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}
ALLOWED_RUNTIME_STATUS = {"accepted", "rejected"}
ALLOWED_ACK_AUTHORITIES = {"MWORKS", "ROS2", "MWORKS_ROS2"}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number}: JSONL row must be an object")
            payload["_line_number"] = line_number
            rows.append(payload)
    if not rows:
        raise ValueError(f"empty command echo log: {path}")
    return rows


def command_kind(row: dict[str, Any]) -> str:
    command = row.get("command")
    if isinstance(command, dict):
        return str(command.get("kind") or "")
    return str(row.get("command_kind") or row.get("kind") or "")


def validate_rows(rows: list[dict[str, Any]], *, require_runtime_ack: bool) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    runtime_rows = 0
    placeholder_rows = 0

    for row in rows:
        line = int(row.get("_line_number", 0))
        schema = str(row.get("schema") or "")
        status = str(row.get("status") or "")
        no_pose = str(row.get("no_pose_overwrite_status") or "")
        kind = command_kind(row)

        rejected_forbidden_pose = (
            schema == "mosim.ue_command_echo.v1"
            and status == "rejected"
            and str(row.get("reason") or "") in {"forbidden_pose_command", "pose_override_not_allowed"}
        )
        if kind in FORBIDDEN_KINDS and not rejected_forbidden_pose:
            issues.append(f"line {line}: forbidden UE command kind {kind!r}")
        if row.get("pose_override") is True or row.get("teleport") is True:
            issues.append(f"line {line}: UE command echo must not contain pose_override/teleport=true")

        if schema == "mosim.ue_command_echo.placeholder.v1":
            placeholder_rows += 1
            if no_pose != "pass":
                issues.append(f"line {line}: placeholder no_pose_overwrite_status must be pass")
            continue

        if schema != "mosim.ue_command_echo.v1":
            issues.append(f"line {line}: unsupported command echo schema {schema!r}")
            continue
        if status not in ALLOWED_RUNTIME_STATUS:
            issues.append(f"line {line}: runtime echo status must be accepted/rejected, got {status!r}")
        if no_pose != "pass":
            issues.append(f"line {line}: runtime no_pose_overwrite_status must be pass")

        authority = str(row.get("ack_authority") or "")
        if authority not in ALLOWED_ACK_AUTHORITIES:
            issues.append(f"line {line}: ack_authority must be one of {sorted(ALLOWED_ACK_AUTHORITIES)}, got {authority!r}")
        if not str(row.get("run_id") or ""):
            issues.append(f"line {line}: missing run_id")
        if not str(row.get("request_id") or ""):
            issues.append(f"line {line}: missing request_id")
        runtime_rows += 1

    if placeholder_rows:
        warnings.append("UE command echo is placeholder-only or includes placeholder rows; this is smoke-only evidence")
    if require_runtime_ack and runtime_rows == 0:
        issues.append("runtime UE command echo evidence requires at least one accepted/rejected mosim.ue_command_echo.v1 row")

    return {
        "ok": not issues,
        "issues": issues,
        "warnings": warnings,
        "rows": len(rows),
        "runtime_ack_rows": runtime_rows,
        "placeholder_rows": placeholder_rows,
        "require_runtime_ack": require_runtime_ack,
        "no_pose_overwrite_status": "pass" if not issues else "invalid",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("echo_jsonl", help="UE command echo JSONL path")
    parser.add_argument("--require-runtime-ack", action="store_true")
    parser.add_argument("--output-json", help="Optional report path")
    args = parser.parse_args()

    echo_path = repo_path(args.echo_jsonl)
    try:
        rows = read_jsonl(echo_path)
        report = validate_rows(rows, require_runtime_ack=args.require_runtime_ack)
    except Exception as exc:
        report = {
            "ok": False,
            "issues": [str(exc)],
            "warnings": [],
            "rows": 0,
            "runtime_ack_rows": 0,
            "placeholder_rows": 0,
            "require_runtime_ack": args.require_runtime_ack,
            "no_pose_overwrite_status": "invalid",
        }
    report["echo_jsonl"] = str(args.echo_jsonl)
    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
