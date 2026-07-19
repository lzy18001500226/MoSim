#!/usr/bin/env python3
"""Submit a bounded request to the persistent Orchestrator service."""

from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_DIR = ROOT / "Results" / "ui_platform" / "orchestrator_requests"
RESPONSE_DIR = ROOT / "Results" / "ui_platform" / "orchestrator_responses"
ACTIVE_RUN = ROOT / "Results" / "ui_platform" / "model_studio_active_run.json"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def submit(payload: dict[str, Any], *, timeout_s: float) -> dict[str, Any]:
    request_id = payload.setdefault("request_id", f"req-{uuid.uuid4().hex}")
    request_path = REQUEST_DIR / f"{request_id}.json"
    response_path = RESPONSE_DIR / f"{request_id}.response.json"
    REQUEST_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSE_DIR.mkdir(parents=True, exist_ok=True)
    temporary = request_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(request_path)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if response_path.is_file():
            response = json.loads(response_path.read_text(encoding="utf-8"))
            if response.get("accepted") and response.get("run_id"):
                ACTIVE_RUN.parent.mkdir(parents=True, exist_ok=True)
                ACTIVE_RUN.write_text(
                    json.dumps({"run_id": response["run_id"], "profile_hash": response.get("profile_hash", "")}, indent=2)
                    + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            return response
        time.sleep(0.1)
    return {
        "request_id": request_id,
        "accepted": False,
        "reason_code": "orchestrator_response_pending",
        "run_id": "",
        "profile_hash": "",
        "request_path": _display_path(request_path),
    }


def _active_run() -> dict[str, str]:
    if not ACTIVE_RUN.is_file():
        return {}
    value = json.loads(ACTIVE_RUN.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {"schema": "mosim.orchestrator.request.v1", "action": args.action}
    if getattr(args, "request_id", None):
        payload["request_id"] = args.request_id
    if args.action == "list_controllers":
        return payload
    if args.action == "propose_operator_task":
        if not args.prompt:
            raise ValueError("propose_operator_task requires a prompt")
        payload["prompt"] = args.prompt
        return payload
    if args.action == "preflight_connection":
        if not args.profile_path or not args.controller_id or args.vehicle_count is None:
            raise ValueError("preflight_connection requires profile, controller, and vehicle count")
        payload.update(
            {
                "profile_path": args.profile_path,
                "controller_id": args.controller_id,
                "vehicle_count": args.vehicle_count,
                "target_host": args.target_host,
                "rt1_udp_port": args.rt1_udp_port,
                "ros_master_uri": "" if args.defer_ros_master else args.ros_master_uri,
                "local_advertised_ip": args.local_advertised_ip,
                "requested_rate_hz": args.requested_rate_hz,
                "timeout_s": args.preflight_timeout_s,
                "sample_count": args.preflight_sample_count,
            }
        )
        return payload
    if args.action == "prepare_run":
        if not args.profile_path or not args.controller_id or args.vehicle_count is None:
            raise ValueError("prepare_run requires profile, controller, and vehicle count")
        payload.update(
            {
                "profile_path": args.profile_path,
                "controller_id": args.controller_id,
                "vehicle_count": args.vehicle_count,
                "parameter_set": {
                    "wind_speed_mps": args.wind_speed_mps,
                    "manual_control": bool(args.manual_control),
                },
                "connection_preflight_id": args.connection_preflight_id or "",
            }
        )
        return payload

    active = _active_run()
    if args.action in {"attach_display", "detach_display"}:
        if not args.session_id:
            raise ValueError(f"{args.action} requires a display session")
        payload["session_id"] = args.session_id
        return payload

    run_id = args.run_id or active.get("run_id")
    if not run_id:
        raise ValueError(f"{args.action} requires an active run")
    payload["run_id"] = run_id

    if args.action == "get_operation_progress":
        if not getattr(args, "operation_id", None):
            raise ValueError("get_operation_progress requires an operation id")
        payload["operation_id"] = args.operation_id
        return payload

    if args.action in {"apply_injection", "restore_injection"}:
        if not args.target or args.value is None:
            raise ValueError(f"{args.action} requires target and value")
        command: dict[str, Any] = {
            "command_id": f"inj-{uuid.uuid4().hex}",
            "run_id": run_id,
            "profile_hash": active.get("profile_hash", ""),
            "target": args.target,
            "requested_at": time.time(),
            "apply_mode": "restore" if args.action == "restore_injection" else "set",
            "value": args.value,
            "ramp_s": args.ramp_s,
            "duration_s": args.duration_s,
            "restore_policy": "manual",
            "source": "flight_console",
        }
        if args.rotor_index is not None:
            command["rotor_index"] = args.rotor_index
        if args.vehicle_id is not None:
            command["vehicle_id"] = args.vehicle_id
        payload["command"] = command
    elif args.action == "prepare_display_session":
        payload["displays"] = args.display
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=(
            "prepare_run",
            "preflight_connection",
            "start_run",
            "request_safe_stop",
            "stop_run",
            "reset_run",
            "apply_injection",
            "restore_injection",
            "prepare_display_session",
            "attach_display",
            "detach_display",
            "get_run_state",
            "get_telemetry",
            "open_model_context",
            "get_result_packet",
            "run_mil",
            "generate_code",
            "get_model_gate_state",
            "list_controllers",
            "propose_operator_task",
            "get_operation_progress",
            "close_all_rviz",
            "start_ue_recording",
            "stop_ue_recording",
        ),
    )
    parser.add_argument("--profile-path")
    parser.add_argument("--prompt")
    parser.add_argument("--controller-id")
    parser.add_argument("--vehicle-count", type=int)
    parser.add_argument("--wind-speed-mps", type=float, default=0.0)
    parser.add_argument("--manual-control", choices=("true", "false"), default="false",
                        help="Start the runtime in bounded keyboard-manual mode.")
    parser.add_argument("--run-id")
    parser.add_argument("--session-id")
    parser.add_argument("--operation-id")
    parser.add_argument("--request-id")
    parser.add_argument("--connection-preflight-id")
    parser.add_argument("--target-host", default="127.0.0.1")
    parser.add_argument("--rt1-udp-port", type=int, default=49020)
    parser.add_argument("--ros-master-uri", default="http://127.0.0.1:11311")
    parser.add_argument(
        "--defer-ros-master",
        action="store_true",
        help="Cold-start prepare: validate MWORKS transport now and require ROS readiness after runtime launch.",
    )
    parser.add_argument("--local-advertised-ip", default="auto")
    parser.add_argument("--requested-rate-hz", type=int, choices=(50, 100, 200), default=200)
    parser.add_argument("--preflight-timeout-s", type=float, default=0.35)
    parser.add_argument("--preflight-sample-count", type=int, default=5)
    parser.add_argument("--target", choices=("wind_speed_mps", "wind_direction_deg", "motor_effectiveness"))
    parser.add_argument("--value", type=float)
    parser.add_argument("--rotor-index", type=int, choices=range(1, 5))
    parser.add_argument("--vehicle-id", choices=tuple(f"uav{index}" for index in range(1, 10)))
    parser.add_argument("--ramp-s", type=float, default=0.0)
    parser.add_argument("--duration-s", type=float, default=0.0)
    parser.add_argument(
        "--display",
        action="append",
        default=[],
        choices=("rviz_pointcloud", "rviz_gridmap", "unreal", "mworks_result"),
    )
    parser.add_argument("--timeout-s", type=float, default=5.0)
    parser.add_argument("--format", choices=("json", "tsv"), default="tsv")
    args = parser.parse_args()
    args.manual_control = args.manual_control == "true"
    if not 0.0 <= args.timeout_s <= 5.0:
        parser.error("--timeout-s must be between 0 and 5 seconds")
    try:
        payload = build_payload(args)
    except ValueError as exc:
        parser.error(str(exc))
    response = submit(payload, timeout_s=args.timeout_s)
    if args.format == "json":
        # QProcess parses stdout as UTF-8 on Windows. Keep the transport
        # response ASCII-safe even when a blocker detail contains Chinese text.
        print(json.dumps(response, ensure_ascii=True, indent=2))
    else:
        print(
            "\t".join(
                str(response.get(field, ""))
                for field in ("accepted", "reason_code", "run_id", "profile_hash", "request_id")
            )
        )
    return 0 if response.get("accepted") else 2


if __name__ == "__main__":
    raise SystemExit(main())
