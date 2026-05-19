r"""Minimal Mid360 point-cloud smoke test for RflySim3D.
Run with D:\PX4PSP\Python38\python.exe while RflySim3D is open.
It requests a Mid360 sensor and prints point-cloud summaries; it does not open RViz/Open3D.
"""
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
ue = UE4CtrlAPI.UE4CtrlAPI()
ue.sendUE4Cmd("RflyShowTextTime Mid360_smoke_request 8", windowID=-1)
ue.sendUE4Cmd("RflyChangeMapbyName SLAMScene", windowID=-1)
time.sleep(2)
ue.sendUE4PosNew(copterID=1, vehicleType=3, PosE=[2, 0, -2], AngEuler=[0, 0, 0], PWMs=[5600] * 4 + [0] * 4, windowID=-1)
time.sleep(1)

vis = VisionCaptureApi.VisionCaptureApi()
vis.jsonLoad(jsonPath=str(BASE / "Config_udp.json"))
ok = vis.sendReqToUE4()
print(f"sendReqToUE4={ok}", flush=True)
vis.startImgCap()

samples = 0
start = time.time()
while time.time() - start < 8:
    t = time.time() - start
    pos = ue.circle_traj(t, (1, 0), 1, 10)
    ue.sendUE4PosNew(copterID=1, vehicleType=3, PosE=pos + [-2], AngEuler=[0, 0, 0], PWMs=[5600] * 4 + [0] * 4, windowID=-1)
    if vis.hasData and vis.hasData[0]:
        cloud = np.asarray(vis.Img[0])
        samples += 1
        if cloud.size:
            flat = cloud.reshape(-1, cloud.shape[-1]) if cloud.ndim == 3 else cloud.reshape(-1, cloud.shape[-1])
            finite = flat[np.isfinite(flat).all(axis=1)]
            xyz = finite[:, :3] if finite.shape[1] >= 3 else finite
            mins = xyz.min(axis=0)[:3] if len(xyz) else [float('nan')] * 3
            maxs = xyz.max(axis=0)[:3] if len(xyz) else [float('nan')] * 3
            if samples == 1 or samples % 10 == 0:
                print(f"sample={samples} shape={cloud.shape} points={len(xyz)} min={mins} max={maxs}", flush=True)
        vis.hasData[0] = False
    time.sleep(0.03)
print(f"samples={samples}", flush=True)
ue.sendUE4Cmd("RflyShowTextTime Mid360_smoke_done 8", windowID=-1)
time.sleep(0.2)

# VisionCaptureApi starts background receiver threads that keep Python alive.
# RflySim's official examples also terminate the process explicitly after demos.
os._exit(0)
