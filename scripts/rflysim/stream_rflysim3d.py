#!/usr/bin/env python3
"""Stream MWORKS raw CSV frames to an installed RflySim3D renderer.

This bridge is render-only. It must not be used as controller, planner,
collision, or metrics evidence. MWORKS/Sysplorer remains the simulation source
of truth.
"""

from __future__ import annotations

import argparse
import csv
import math
import socket
import struct
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RFLYSIM_ROOTS = (
    Path("/mnt/d/PX4PSP"),
    Path("D:/PX4PSP"),
)
REQUIRED_COLUMNS = ("time", "x", "y", "z")
RPY_COLUMNS = ("roll", "pitch", "yaw")
DEFAULT_MOTOR_COLUMNS = ("u1", "u2", "u3", "u4")


def finite(value: float | None, fallback: float = 0.0) -> float:
    if value is None or math.isnan(value) or math.isinf(value):
        return fallback
    return value


def parse_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    return float(value)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, float]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")
        rows: list[dict[str, float]] = []
        for row in reader:
            rows.append({name: parse_float(row.get(name)) for name in reader.fieldnames})
    if not rows:
        raise ValueError(f"CSV has no data rows: {path}")
    return list(reader.fieldnames), rows


def select_rows(
    rows: list[dict[str, float]],
    *,
    start_time: float | None,
    end_time: float | None,
    stride: int,
    max_frames: int | None,
) -> list[dict[str, float]]:
    selected = []
    for row in rows:
        t = finite(row.get("time"))
        if start_time is not None and t < start_time:
            continue
        if end_time is not None and t > end_time:
            continue
        selected.append(row)
    selected = selected[:: max(1, stride)]
    if max_frames is not None:
        selected = selected[:max_frames]
    if not selected:
        raise ValueError("No rows selected; check time range, stride, and max frames")
    return selected


def resolve_rflysim_root(user_root: Path | None) -> Path:
    if user_root:
        root = user_root
        if root.exists():
            return root
        raise FileNotFoundError(f"RflySim root not found: {root}")
    for root in DEFAULT_RFLYSIM_ROOTS:
        if root.exists():
            return root
    raise FileNotFoundError(f"RflySim root not found. Checked: {DEFAULT_RFLYSIM_ROOTS}")


def import_ue4_ctrl_api(rflysim_root: Path) -> Any:
    sdk_ue = rflysim_root / "RflySimAPIs" / "RflySimSDK" / "ue"
    if not sdk_ue.exists():
        raise FileNotFoundError(f"RflySim UE SDK folder not found: {sdk_ue}")
    sys.path.insert(0, str(sdk_ue))
    import UE4CtrlAPI  # type: ignore[import-not-found]

    return UE4CtrlAPI


class DirectRflySim3DClient:
    """Small direct UDP subset of RflySim3D's documented UE4CtrlAPI protocol."""

    def __init__(self, host: str) -> None:
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def close(self) -> None:
        self.sock.close()

    def _window_ports(self, window_id: int) -> list[int]:
        if window_id < 0:
            return [20010, 20011, 20012]
        return [20010 + window_id]

    def send_cmd(self, command: str, window_id: int) -> None:
        data = command.encode("utf-8") if isinstance(command, str) else command
        if len(data) <= 51:
            payload = struct.pack("i52s", 1234567890, data)
        elif len(data) <= 249:
            payload = struct.pack("i252s", 1234567890, data)
        else:
            raise ValueError(f"RflySim3D command too long: {command}")
        for port in self._window_ports(window_id):
            self.sock.sendto(payload, (self.host, port))

    def send_pos_full(
        self,
        *,
        copter_id: int,
        vehicle_type: int,
        motor_rpms: list[float],
        vel_e: list[float],
        pos_e: list[float],
        rate_b: list[float],
        ang_euler: list[float],
        window_id: int,
    ) -> None:
        # UE4CtrlAPI.sendUE4PosFull uses struct SOut2Simulator:
        # checksum, copterID, vehicleType, reserv, VelE[3], AngEuler[3],
        # quaternion[4], MotorRPM[8], AccB[3], RateB[3], runnedTime, PosE[3],
        # PosGPS[3] -> "4i24f7d".
        payload = struct.pack(
            "4i24f7d",
            123456789,
            copter_id,
            vehicle_type,
            0,
            *vel_e[:3],
            *ang_euler[:3],
            0.0,
            0.0,
            0.0,
            0.0,
            *(motor_rpms + [0.0] * 8)[:8],
            0.0,
            0.0,
            0.0,
            *rate_b[:3],
            -1.0,
            *pos_e[:3],
            0.0,
            0.0,
            0.0,
        )
        for port in self._window_ports(window_id):
            self.sock.sendto(payload, (self.host, port))


def mworks_to_rfly_ned(row: dict[str, float]) -> list[float]:
    # Project raw CSV uses x/y in meters and z positive upward. RflySim3D
    # examples use NED, where altitude is negative when flying above ground.
    return [
        finite(row.get("x")),
        finite(row.get("y")),
        -finite(row.get("z")),
    ]


def mworks_rpy_to_rfly(row: dict[str, float]) -> list[float]:
    return [finite(row.get(name)) for name in RPY_COLUMNS]


def estimate_velocity_ned(row: dict[str, float], prev: dict[str, float] | None) -> list[float]:
    if prev is None:
        return [0.0, 0.0, 0.0]
    t = finite(row.get("time"))
    prev_t = finite(prev.get("time"))
    dt = t - prev_t
    if dt <= 1e-9:
        return [0.0, 0.0, 0.0]
    current = mworks_to_rfly_ned(row)
    previous = mworks_to_rfly_ned(prev)
    return [(current[i] - previous[i]) / dt for i in range(3)]


def motor_rpms(
    row: dict[str, float],
    *,
    motor_columns: list[str],
    mode: str,
    constant_rpm: float,
    gain: float,
    min_rpm: float,
    max_rpm: float,
) -> list[float]:
    if mode == "constant":
        rpms = [constant_rpm] * 4
    else:
        values = [finite(row.get(name), 0.0) for name in motor_columns]
        values = (values + [0.0, 0.0, 0.0, 0.0])[:4]
        rpms = [constant_rpm + gain * abs(value) for value in values]
    rpms = [min(max(value, min_rpm), max_rpm) for value in rpms]
    # RflySim vehicle messages reserve 8 rotor slots. Quadrotor uses the first 4.
    return rpms + [0.0, 0.0, 0.0, 0.0]


def send_init_commands(sender: Any, args: argparse.Namespace) -> None:
    def send_cmd(command: str) -> None:
        if isinstance(sender, DirectRflySim3DClient):
            sender.send_cmd(command, args.window_id)
        else:
            sender.sendUE4Cmd(command, args.window_id)

    if args.map_name:
        send_cmd(f"RflyChangeMapbyName {args.map_name}")
    if args.vehicle_model_id is not None:
        send_cmd(f"RflyChange3DModel {args.copter_id} {args.vehicle_model_id}")
    if args.vehicle_size is not None:
        send_cmd(f"RflyChangeVehicleSize {args.copter_id} {args.vehicle_size}")
    if args.max_fps:
        send_cmd(f"t.MaxFPS {args.max_fps}")
    if args.resolution:
        send_cmd(f"r.setres {args.resolution}")


def preview_payload(row: dict[str, float], prev: dict[str, float] | None, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "time": finite(row.get("time")),
        "copter_id": args.copter_id,
        "vehicle_type": args.vehicle_type,
        "pos_e_ned_m": mworks_to_rfly_ned(row),
        "vel_e_ned_mps": estimate_velocity_ned(row, prev),
        "ang_euler_rad": mworks_rpy_to_rfly(row),
        "motor_rpms": motor_rpms(
            row,
            motor_columns=args.motor_columns,
            mode=args.motor_mode,
            constant_rpm=args.constant_rpm,
            gain=args.rpm_gain,
            min_rpm=args.min_rpm,
            max_rpm=args.max_rpm,
        ),
        "render_only": True,
    }


def stream_rows(args: argparse.Namespace) -> int:
    _, rows = read_rows(args.raw_csv)
    rows = select_rows(
        rows,
        start_time=args.start_time,
        end_time=args.end_time,
        stride=args.stride,
        max_frames=args.max_frames,
    )
    interval_override = 1.0 / args.fps if args.fps and args.fps > 0 else None

    sender: Any = None
    if not args.dry_run:
        if args.transport == "sdk":
            rflysim_root = resolve_rflysim_root(args.rflysim_root)
            UE4CtrlAPI = import_ue4_ctrl_api(rflysim_root)
            sender = UE4CtrlAPI.UE4CtrlAPI(ip=args.host)
        else:
            sender = DirectRflySim3DClient(args.host)
        send_init_commands(sender, args)

    prev: dict[str, float] | None = None
    previous_t = finite(rows[0].get("time"))
    start_wall = time.monotonic()
    for seq, row in enumerate(rows):
        payload = preview_payload(row, prev, args)
        if args.dry_run:
            print(payload)
        else:
            assert sender is not None
            if seq > 0 and not args.no_sleep:
                current_t = finite(row.get("time"), previous_t)
                dt = interval_override if interval_override is not None else max(0.0, current_t - previous_t)
                time.sleep(max(0.0, dt / args.replay_speed))
                previous_t = current_t
            if isinstance(sender, DirectRflySim3DClient):
                sender.send_pos_full(
                    copter_id=args.copter_id,
                    vehicle_type=args.vehicle_type,
                    motor_rpms=payload["motor_rpms"],
                    vel_e=payload["vel_e_ned_mps"],
                    pos_e=payload["pos_e_ned_m"],
                    rate_b=[0.0, 0.0, 0.0],
                    ang_euler=payload["ang_euler_rad"],
                    window_id=args.window_id,
                )
            else:
                sender.sendUE4PosFull(
                    args.copter_id,
                    args.vehicle_type,
                    MotorRPMS=payload["motor_rpms"],
                    VelE=payload["vel_e_ned_mps"],
                    PosE=payload["pos_e_ned_m"],
                    RateB=[0.0, 0.0, 0.0],
                    AngEuler=payload["ang_euler_rad"],
                    windowID=args.window_id,
                )
        if args.print_every and seq % args.print_every == 0:
            elapsed = time.monotonic() - start_wall
            print(
                f"streamed seq={seq} t={payload['time']:.3f}s "
                f"pos={payload['pos_e_ned_m']} elapsed={elapsed:.2f}s",
                file=sys.stderr,
            )
        prev = row
    print(
        f"RflySim3D stream complete: frames={len(rows)} raw={args.raw_csv} "
        f"dry_run={args.dry_run}"
    )
    if isinstance(sender, DirectRflySim3DClient):
        sender.close()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path, help="Standard MWORKS raw CSV")
    parser.add_argument("--transport", choices=("direct", "sdk"), default="direct")
    parser.add_argument("--rflysim-root", type=Path, default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--window-id", type=int, default=0)
    parser.add_argument("--copter-id", type=int, default=1)
    parser.add_argument("--vehicle-type", type=int, default=3)
    parser.add_argument("--vehicle-model-id", type=int, default=None)
    parser.add_argument("--vehicle-size", type=float, default=None)
    parser.add_argument("--map-name", default=None)
    parser.add_argument("--resolution", default=None, help="Example: 1280x720w")
    parser.add_argument("--max-fps", type=float, default=None)
    parser.add_argument("--start-time", type=float, default=None)
    parser.add_argument("--end-time", type=float, default=None)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--fps", type=float, default=None, help="Override CSV spacing with a fixed send FPS")
    parser.add_argument("--replay-speed", type=float, default=1.0)
    parser.add_argument("--no-sleep", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-every", type=int, default=0)
    parser.add_argument("--motor-columns", nargs="+", default=list(DEFAULT_MOTOR_COLUMNS))
    parser.add_argument("--motor-mode", choices=("constant", "command_magnitude"), default="constant")
    parser.add_argument("--constant-rpm", type=float, default=2200.0)
    parser.add_argument("--rpm-gain", type=float, default=300.0)
    parser.add_argument("--min-rpm", type=float, default=0.0)
    parser.add_argument("--max-rpm", type=float, default=8000.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.replay_speed <= 0:
        raise ValueError("--replay-speed must be positive")
    if len(args.motor_columns) > 4:
        raise ValueError("--motor-columns accepts at most four columns for a quadrotor")
    if not args.raw_csv.exists():
        raise FileNotFoundError(args.raw_csv)
    return stream_rows(args)


if __name__ == "__main__":
    raise SystemExit(main())
