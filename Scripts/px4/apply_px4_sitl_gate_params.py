#!/usr/bin/env python3
"""Apply per-run PX4 SITL parameters for MoSim evidence gates."""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from datetime import datetime, timezone
from typing import Any

from pymavlink import mavutil


DEFAULT_PARAMS: dict[str, float | int] = {
    # Keep simulator safety checks deterministic for long Offboard evidence gates.
    "CBRK_SUPPLY_CHK": 894281,
    "COM_LOW_BAT_ACT": 0,
    "COM_FLT_TIME_MAX": -1,
    "NAV_DLL_ACT": 0,
    "NAV_RCL_ACT": 0,
    "COM_DL_LOSS_T": 30,
    "COM_OF_LOSS_T": 5.0,
    # Keep thresholds below simulated battery levels so long 8-shaped gates do not RTL.
    "BAT_LOW_THR": 0.05,
    "BAT_CRIT_THR": 0.03,
    "BAT_EMERGEN_THR": 0.02,
}


FASTLIO_EXTERNAL_VISION_PARAMS: dict[str, float | int] = {
    # Fuse FAST-LIO as external vision position/height/velocity, but keep yaw
    # out of the first guarded gate until the frame convention is separately
    # accepted from plots and RViz.
    "EKF2_EV_CTRL": 7,
    "EKF2_HGT_REF": 3,
    "EKF2_EV_DELAY": 0.0,
    "EKF2_EV_NOISE_MD": 0,
    "EKF2_EV_POS_X": 0.035,
    "EKF2_EV_POS_Y": 0.0,
    "EKF2_EV_POS_Z": 0.08,
    "EKF2_EVP_NOISE": 0.05,
    "EKF2_EVV_NOISE": 0.1,
}


def _coerce_param_value(value: float | int) -> tuple[float, int]:
    if isinstance(value, int):
        return float(value), mavutil.mavlink.MAV_PARAM_TYPE_INT32
    return float(value), mavutil.mavlink.MAV_PARAM_TYPE_REAL32


def apply_params(endpoint: str, params: dict[str, float | int], timeout_s: float, require_ack: bool) -> dict[str, Any]:
    connection = mavutil.mavlink_connection(endpoint, source_system=254, source_component=191)
    try:
        connection.wait_heartbeat(timeout=timeout_s)
    except Exception:
        if require_ack:
            raise
        connection.target_system = 1
        connection.target_component = 1
    applied: list[dict[str, Any]] = []
    deadline = time.monotonic() + timeout_s

    for name, value in params.items():
        param_value, param_type = _coerce_param_value(value)
        connection.mav.param_set_send(
            connection.target_system,
            connection.target_component,
            name.encode("ascii"),
            param_value,
            param_type,
        )
        ack_value = None
        if require_ack:
            while time.monotonic() < deadline:
                message = connection.recv_match(type="PARAM_VALUE", blocking=True, timeout=1.0)
                if message is None:
                    continue
                if message.param_id.strip("\x00") != name:
                    continue
                ack_value = float(message.param_value)
                break
        applied.append(
            {
                "name": name,
                "requested": value,
                "ack_value": ack_value,
                "acked": ack_value is not None,
                "param_type": param_type,
            }
        )

    return {
        "schema": "mosim.px4_sitl_gate_params.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "require_ack": require_ack,
        "params": applied,
        "all_acked": all(item["acked"] for item in applied),
        "sent_all": len(applied) == len(params),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="udpout:127.0.0.1:18570")
    parser.add_argument("--timeout-s", type=float, default=20.0)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--require-ack", action="store_true")
    parser.add_argument("--fastlio-external-vision", action="store_true")
    parser.add_argument("--param", action="append", default=[], help="Extra NAME=VALUE override")
    args = parser.parse_args()

    params: dict[str, float | int] = dict(DEFAULT_PARAMS)
    if args.fastlio_external_vision:
        params.update(FASTLIO_EXTERNAL_VISION_PARAMS)
    for item in args.param:
        name, raw_value = item.split("=", 1)
        try:
            if "." in raw_value:
                params[name] = float(raw_value)
            else:
                params[name] = int(raw_value)
        except ValueError:
            params[name] = float(raw_value)

    payload = apply_params(args.endpoint, params, args.timeout_s, args.require_ack)
    output = pathlib.Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["sent_all"] and (payload["all_acked"] or not args.require_ack) else 2


if __name__ == "__main__":
    raise SystemExit(main())
