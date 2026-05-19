"""Static RflySim3D scene survey helper.

This script is intentionally simple: it switches to one built-in RflySim map,
places one stationary quadrotor, and sets a fixed overview camera. It does not
spawn artificial obstacle boxes, request sensors, or run navigation. Use it to
choose sane scene/start/goal coordinates before enabling Mid360 and planning.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

RFY = Path(r"D:\PX4PSP\RflySimAPIs")
SDK = RFY / "RflySimSDK"
sys.path[:0] = [
    str(SDK),
    str(SDK / "ue"),
]

import UE4CtrlAPI  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="OldFactory")
    parser.add_argument("--vehicle-id", type=int, default=1)
    parser.add_argument("--vehicle-type", type=int, default=3)
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--altitude-m", type=float, default=3.0)
    parser.add_argument("--yaw-deg", type=float, default=0.0)
    parser.add_argument("--duration-s", type=float, default=120.0)
    parser.add_argument("--camera-x", type=float, default=-12.0)
    parser.add_argument("--camera-y", type=float, default=-18.0)
    parser.add_argument("--camera-z", type=float, default=-16.0)
    parser.add_argument("--camera-roll-deg", type=float, default=0.0)
    parser.add_argument("--camera-pitch-deg", type=float, default=-38.0)
    parser.add_argument("--camera-yaw-deg", type=float, default=42.0)
    args = parser.parse_args()

    ue = UE4CtrlAPI.UE4CtrlAPI()
    for cmd in (
        "r.setres 1280x720w",
        "t.MaxFPS 30",
        f"RflyChangeMapbyName {args.map}",
        "RflyCameraFovDegrees 85",
    ):
        ue.sendUE4Cmd(cmd, windowID=-1)
        time.sleep(0.4)

    pos = [args.x, args.y, -abs(args.altitude_m)]
    yaw = math.radians(args.yaw_deg)
    ue.sendUE4PosNew(
        copterID=args.vehicle_id,
        vehicleType=args.vehicle_type,
        PosE=pos,
        AngEuler=[0.0, 0.0, yaw],
        PWMs=[5600] * 4 + [0] * 4,
        windowID=-1,
    )
    ue.sendUE4LabelID(
        args.vehicle_id,
        f"{args.map} start ({args.x:.1f},{args.y:.1f},{args.altitude_m:.1f}m)",
        fontSize=30,
        RGB=[0, 255, 255],
        windowID=-1,
    )
    ue.sendUE4Cmd(
        "RflyCameraPosAng "
        f"{args.camera_x} {args.camera_y} {args.camera_z} "
        f"{args.camera_roll_deg} {args.camera_pitch_deg} {args.camera_yaw_deg}",
        windowID=-1,
    )
    ue.sendUE4Cmd(f"RflyShowTextTime SceneSurvey_{args.map}_static 10", windowID=-1)

    print(
        "scene_survey map={} vehicle_id={} pos={} yaw_deg={} duration_s={}".format(
            args.map,
            args.vehicle_id,
            pos,
            args.yaw_deg,
            args.duration_s,
        ),
        flush=True,
    )
    deadline = time.time() + args.duration_s
    while time.time() < deadline:
        ue.sendUE4PosNew(
            copterID=args.vehicle_id,
            vehicleType=args.vehicle_type,
            PosE=pos,
            AngEuler=[0.0, 0.0, yaw],
            PWMs=[5600] * 4 + [0] * 4,
            windowID=-1,
        )
        time.sleep(0.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
