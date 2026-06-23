#!/usr/bin/env python3
"""Create a Goal5 Gazebo Classic world with UAV models preloaded.

Gazebo Classic can load multiple Livox sensor plugins during initial world
load, but the current Sunray dynamic spawn path only loads the first Livox
SensorPlugin reliably.  This helper keeps the Sunray SDF/Jinja model and PX4
port convention intact while inserting uav1/uav2/uav3 models directly into the
world before gzserver starts.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def render_model(
    sunray_ws: Path,
    vehicle: str,
    uid: int,
    x: float,
    y: float,
    z: float,
    yaw: float,
) -> str:
    simulator = sunray_ws / "simulation/sunray_simulator"
    template = simulator / f"models/drone_models/{vehicle}/{vehicle}.sdf.jinja"
    if not template.exists():
        raise FileNotFoundError(template)

    instance = uid - 1
    cmd = [
        "python3",
        str(simulator / "scripts/jinja_gen.py"),
        "--stdout",
        f"--mavlink_id={uid}",
        f"--mavlink_udp_port={14560 + instance}",
        f"--mavlink_tcp_port={4560 + instance}",
        f"--gst_udp_port={5600 + instance}",
        f"--video_uri={5600 + instance}",
        f"--mavlink_cam_udp_port={14530 + instance}",
        str(template),
        str(simulator),
    ]
    rendered = subprocess.check_output(cmd, text=True)
    match = re.search(r"<model\b[^>]*>.*</model>", rendered, re.DOTALL)
    if not match:
        raise RuntimeError(f"no <model> block in rendered SDF for uav{uid}")
    model = match.group(0)
    model = re.sub(r"<model\s+name=(['\"])[^'\"]+\1>", f"<model name='uav{uid}'>", model, count=1)
    model = model.replace(
        f"<model name='uav{uid}'>",
        f"<model name='uav{uid}'>\n    <pose>{x:.6f} {y:.6f} {z:.6f} 0 0 {yaw:.6f}</pose>",
        1,
    )
    return "\n".join("    " + line if line.strip() else line for line in model.splitlines())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sunray-ws", required=True, type=Path)
    parser.add_argument("--base-world", required=True, type=Path)
    parser.add_argument("--output-world", required=True, type=Path)
    parser.add_argument("--vehicle", default="sunray150_with_mid360")
    parser.add_argument("--uav-num", type=int, choices=[2, 3], default=2)
    parser.add_argument("--uav1", nargs=4, type=float, metavar=("X", "Y", "Z", "YAW"), default=[0.0, -1.0, 0.2, 0.0])
    parser.add_argument("--uav2", nargs=4, type=float, metavar=("X", "Y", "Z", "YAW"), default=[0.0, 1.0, 0.2, 0.0])
    parser.add_argument("--uav3", nargs=4, type=float, metavar=("X", "Y", "Z", "YAW"), default=[-1.5, 0.0, 0.2, 0.0])
    args = parser.parse_args()

    text = args.base_world.read_text(encoding="utf-8")
    insert_at = text.rfind("</world>")
    if insert_at < 0:
        raise RuntimeError(f"base world has no </world>: {args.base_world}")

    poses = {1: args.uav1, 2: args.uav2, 3: args.uav3}
    models = []
    for uid in range(1, args.uav_num + 1):
        models.append(render_model(args.sunray_ws, args.vehicle, uid, *poses[uid]))

    insertion = "\n\n    <!-- MoSim Goal5 preloaded PX4/Gazebo UAV models. -->\n" + "\n\n".join(models) + "\n"
    out = text[:insert_at] + insertion + text[insert_at:]
    args.output_world.parent.mkdir(parents=True, exist_ok=True)
    args.output_world.write_text(out, encoding="utf-8")
    print(args.output_world)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
