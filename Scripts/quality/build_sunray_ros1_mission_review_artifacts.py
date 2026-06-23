#!/usr/bin/env python3
"""Build review plots for Sunray ROS1 native mission gates."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out = {}
            for k, v in row.items():
                if k == "phase" or v == "":
                    out[k] = v
                else:
                    try:
                        out[k] = float(v)
                    except ValueError:
                        out[k] = v
            rows.append(out)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    result_dir = args.result_dir

    truth = load_csv(result_dir / "gazebo_truth_uav1.csv")
    reference = load_csv(result_dir / "reference_trajectory.csv")
    if not truth:
        raise SystemExit("missing truth csv")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_truth = [r for r in truth if r.get("phase") == "figure8"] or truth
    figures = {}

    fig, ax = plt.subplots(figsize=(7, 7))
    if reference:
        ax.plot([r["x"] for r in reference], [r["y"] for r in reference], "g-", lw=2.0, label="reference")
    ax.plot([r["x"] for r in fig_truth], [r["y"] for r in fig_truth], "r-", lw=1.2, label="Gazebo truth")
    ax.scatter([fig_truth[0]["x"]], [fig_truth[0]["y"]], c="blue", s=35, label="start")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Sunray ROS1 mission XY trajectory")
    ax.axis("equal")
    ax.grid(True)
    ax.legend()
    path = result_dir / "mission_xy_trajectory_review.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures["xy_trajectory"] = str(path)

    t0 = truth[0]["t"]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot([r["t"] - t0 for r in truth], [r["z"] for r in truth], "b-", lw=1.0, label="Gazebo truth z")
    ax.axhline(1.0, color="g", linestyle="--", lw=1.0, label="target z")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("z [m]")
    ax.set_title("Altitude")
    ax.grid(True)
    ax.legend()
    path = result_dir / "mission_altitude_review.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures["altitude"] = str(path)

    gate_path = result_dir / "SUNRAY_ROS1_NATIVE_MISSION_GATE.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {}
    manifest = {
        "schema": "mosim.sunray_ros1_review_artifacts.v1",
        "status": "built",
        "result_dir": str(result_dir),
        "gate_status": gate.get("status"),
        "mission": gate.get("mission"),
        "figures": figures,
    }
    (result_dir / "REVIEW_ARTIFACTS.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
