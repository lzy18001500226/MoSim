r"""Replay an ESDF path in RflySim3D with UE4CtrlAPI.

Run with RflySim3D open and RflySim's bundled Python:

    D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_esdf_path_playback.py

The input path is in image pixel coordinates `[row, col]`. This script converts
it into a local NED-like visual path and drives a quadrotor actor in RflySim3D.
It is a renderer/control-channel smoke test, not a full PX4/CopterSim closed
loop.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, r"D:\PX4PSP\RflySimAPIs\RflySimSDK")
sys.path.insert(0, r"D:\PX4PSP\RflySimAPIs\RflySimSDK\ue")

import UE4CtrlAPI  # noqa: E402


DEFAULT_PATH = Path(r"C:\Users\HP\Desktop\Quadrotor\results\rflysim\esdf_path_smoke.npy")


def pixel_path_to_visual(path: np.ndarray, resolution_m: float, altitude_m: float) -> np.ndarray:
    start = path[0]
    d_row = path[:, 0] - start[0]
    d_col = path[:, 1] - start[1]
    north = d_col * resolution_m
    east = d_row * resolution_m
    scale = max(np.ptp(north), np.ptp(east), 1.0)
    # Keep the official map path visible in a compact RflySim scene.
    scene_scale = min(1.0, 14.0 / scale)
    x = north * scene_scale
    y = east * scene_scale
    z = np.full_like(x, -altitude_m)
    return np.column_stack((x, y, z))


def yaw_from_delta(delta: np.ndarray, fallback: float) -> float:
    if np.linalg.norm(delta[:2]) < 1e-6:
        return fallback
    return math.atan2(delta[1], delta[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--resolution-m", type=float, default=0.05)
    parser.add_argument("--altitude-m", type=float, default=4.0)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--vehicle-id", type=int, default=21)
    args = parser.parse_args()

    path = np.load(args.path)
    if len(path) < 2:
        raise RuntimeError(f"Path has too few points: {args.path}")

    visual = pixel_path_to_visual(path, args.resolution_m, args.altitude_m)
    ue = UE4CtrlAPI.UE4CtrlAPI()
    for cmd in (
        "t.MaxFPS 60",
        "r.setres 1280x720w",
        "RflyChangeMapbyName MapSmall",
        "RflyCameraPosAng 6 -28 -15 0 -28 14",
        "RflyCameraFovDegrees 82",
        "RflyShowTextTime ESDF_path_playback 10",
    ):
        ue.sendUE4Cmd(cmd, windowID=-1)
        time.sleep(0.25)

    last_yaw = 0.0
    dt = 1.0 / max(args.rate_hz, 1.0)
    for i, pos in enumerate(visual):
        if i + 1 < len(visual):
            yaw = yaw_from_delta(visual[i + 1] - pos, last_yaw)
        else:
            yaw = last_yaw
        last_yaw = yaw
        rpm = 5600.0 + 350.0 * math.sin(i * 0.16)
        ue.sendUE4PosFull(
            args.vehicle_id,
            3,
            [rpm] * 4 + [0] * 4,
            [0, 0, 0],
            pos.tolist(),
            [0, 0, 0],
            [0.0, 0.0, yaw],
            windowID=-1,
        )
        time.sleep(dt)

    ue.sendUE4Cmd("RflyShowTextTime ESDF_path_playback_done 8", windowID=-1)
    print(f"replayed_points={len(visual)} path={args.path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
