"""Minimal RflySim3D smoke test.
Run with Windows Python while RflySim3D is open.
"""
import math
import sys
import time

sys.path.insert(0, r"D:\PX4PSP\RflySimAPIs\RflySimSDK")
sys.path.insert(0, r"D:\PX4PSP\RflySimAPIs\RflySimSDK\ue")
import UE4CtrlAPI  # noqa: E402

ue = UE4CtrlAPI.UE4CtrlAPI()
commands = [
    "t.MaxFPS 60",
    "r.setres 1280x720w",
    "RflyShowTextTime Windows_RflySim_SDK_smoke 10",
    "RflyChangeMapbyName MapSmall",
    "RflyCameraPosAng 0 -35 -18 0 -25 0",
    "RflyCameraFovDegrees 80",
]
for cmd in commands:
    print("cmd", cmd, flush=True)
    ue.sendUE4Cmd(cmd, windowID=-1)
    time.sleep(0.5)

# Official example style: create/update a quadrotor with vehicleType=3.
for copter_id, x in [(1, 0), (10, 6), (1000, -6)]:
    print("create", copter_id, flush=True)
    ue.sendUE4Pos(copterID=copter_id, vehicleType=3, MotorRPMSMean=5600, PosE=[x, 0, -6], AngEuler=[0, 0, 0], windowID=-1)
    ue.sendUE4LabelID(copter_id, f"Copter {copter_id}", fontSize=30, RGB=[0, 255, 255], windowID=-1)
    time.sleep(0.6)

for k in range(450):
    t = k / 30.0
    x = 6.0 * math.sin(0.55 * t)
    y = 3.0 * math.sin(1.10 * t)
    z = -6.0 - 0.5 * math.sin(0.25 * t)
    yaw = 0.8 * math.sin(0.55 * t)
    roll = 0.20 * math.sin(1.10 * t)
    pitch = 0.18 * math.cos(0.55 * t)
    rpm = 5600 + 700 * math.sin(3.0 * t)
    ue.sendUE4PosFull(1, 3, [rpm] * 4 + [0] * 4, [0, 0, 0], [x, y, z], [0, 0, 0], [roll, pitch, yaw], windowID=-1)
    time.sleep(1 / 30)
ue.sendUE4Cmd("RflyShowTextTime Windows_RflySim_SDK_smoke_done 8", windowID=-1)
print("done", flush=True)
