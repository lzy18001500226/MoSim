r"""Minimal Mid360 point-cloud smoke test for RflySim3D.

Run with D:\PX4PSP\Python38\python.exe while RflySim3D is open.
By default it prints point-cloud summaries only. Pass --show-open3d to use the
official Open3DShow point-cloud viewer.
"""
import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

RFY = Path(r"D:\PX4PSP\RflySimAPIs")
SDK = RFY / "RflySimSDK"
sys.path[:0] = [
    str(SDK),
    str(SDK / "ue"),
    str(SDK / "vision"),
    str(RFY / "8.RflySimVision" / "0.ApiExps" / "10.Mid360Demo"),
]

import UE4CtrlAPI  # noqa: E402
import VisionCaptureApi  # noqa: E402

BASE = RFY / "8.RflySimVision" / "0.ApiExps" / "10.Mid360Demo"


def cloud_stats(cloud: np.ndarray) -> tuple[int, np.ndarray, np.ndarray]:
    flat = cloud.reshape(-1, cloud.shape[-1]) if cloud.ndim >= 2 else cloud.reshape(-1, 1)
    finite = flat[np.isfinite(flat).all(axis=1)]
    xyz = finite[:, :3] if finite.shape[1] >= 3 else finite
    mins = xyz.min(axis=0)[:3] if len(xyz) else np.array([float("nan")] * 3)
    maxs = xyz.max(axis=0)[:3] if len(xyz) else np.array([float("nan")] * 3)
    return len(xyz), mins, maxs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=20.0)
    parser.add_argument("--map", default="SLAMScene")
    parser.add_argument("--vehicle-id", type=int, default=1)
    parser.add_argument("--x", type=float, default=2.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--altitude-m", type=float, default=2.0)
    parser.add_argument("--static", action="store_true", help="Keep the aircraft fixed while requesting Mid360 frames.")
    parser.add_argument("--show-open3d", action="store_true")
    args = parser.parse_args()

    show3d = None
    if args.show_open3d:
        try:
            import Open3DShow  # noqa: WPS433

            show3d = Open3DShow.Open3DShow()
            show3d.CreatShow(0)
        except Exception as exc:
            print(f"open3d_unavailable={exc!r}", flush=True)
            show3d = None

    ue = UE4CtrlAPI.UE4CtrlAPI()
    ue.sendUE4Cmd("RflyShowTextTime Mid360_smoke_request 8", windowID=-1)
    ue.sendUE4Cmd(f"RflyChangeMapbyName {args.map}", windowID=-1)
    ue.sendUE4Cmd("r.setres 1280x720w", windowID=-1)
    ue.sendUE4Cmd("t.MaxFPS 30", windowID=-1)
    time.sleep(2)
    ue.sendUE4PosNew(
        copterID=args.vehicle_id,
        vehicleType=3,
        PosE=[args.x, args.y, -abs(args.altitude_m)],
        AngEuler=[0, 0, 0],
        PWMs=[5600] * 4 + [0] * 4,
        windowID=-1,
    )
    time.sleep(1)

    vis = VisionCaptureApi.VisionCaptureApi()
    vis.jsonLoad(jsonPath=str(BASE / "Config_udp.json"))
    ok = vis.sendReqToUE4()
    print(f"sendReqToUE4={ok}", flush=True)
    vis.startImgCap()

    samples = 0
    start = time.time()
    while time.time() - start < args.duration_s:
        t = time.time() - start
        if args.static:
            pos = [args.x, args.y]
        else:
            pos = ue.circle_traj(t, (args.x, args.y), 1, 10)
        ue.sendUE4PosNew(
            copterID=args.vehicle_id,
            vehicleType=3,
            PosE=pos + [-abs(args.altitude_m)],
            AngEuler=[0, 0, 0],
            PWMs=[5600] * 4 + [0] * 4,
            windowID=-1,
        )
        if vis.hasData and vis.hasData[0]:
            cloud = np.asarray(vis.Img[0])
            samples += 1
            points, mins, maxs = cloud_stats(cloud)
            if show3d is not None:
                show3d.UpdateShow(cloud)
            if samples == 1 or samples % 10 == 0:
                print(f"sample={samples} shape={cloud.shape} points={points} min={mins} max={maxs}", flush=True)
            vis.hasData[0] = False
        time.sleep(0.03)
    print(f"samples={samples}", flush=True)
    ue.sendUE4Cmd("RflyShowTextTime Mid360_smoke_done 8", windowID=-1)
    time.sleep(0.2)

    # VisionCaptureApi starts background receiver threads that keep Python alive.
    # RflySim's official examples also terminate the process explicitly after demos.
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
