#!/usr/bin/env python3
"""Generate offline tracking demos for scenario-level report/video assets.

These outputs are intentionally labeled as offline_script evidence. They are
not substitutes for real MWORKS/Sysplorer simulation results.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from calc_metrics import compute_metrics, read_csv as read_metric_csv
from generate_planning_reference import read_yaml


ROOT = Path(__file__).resolve().parents[1]
G = 9.81


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(event, ensure_ascii=False, sort_keys=True) for event in events) + "\n", encoding="utf-8")


def write_metrics(raw_csv: Path, metrics_path: Path, scene_id: str, controller_id: str) -> None:
    metrics = compute_metrics(read_metric_csv(raw_csv), raw_csv, scene_id, controller_id)
    metrics["source"] = "offline_script"
    metrics["evidence_level"] = "offline_tracking_demo"
    write_json(metrics_path, metrics)
    csv_path = metrics_path.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, "" if value is None else value])


def ramp(time: float, tau: float) -> float:
    return 1.0 - math.exp(-time / tau)


def motor_commands(time: float, tilt_hint: float = 0.0) -> tuple[float, float, float, float]:
    base = 0.52 + 0.03 * math.sin(0.35 * time)
    differential = 0.05 * math.sin(0.7 * time) + 0.02 * tilt_hint
    return (
        max(0.0, min(1.0, base + differential)),
        max(0.0, min(1.0, base - differential)),
        max(0.0, min(1.0, base + 0.5 * differential)),
        max(0.0, min(1.0, base - 0.5 * differential)),
    )


def make_row(time: float, ref: tuple[float, float, float], actual: tuple[float, float, float]) -> dict[str, float]:
    ex = ref[0] - actual[0]
    ey = ref[1] - actual[1]
    roll = max(-0.35, min(0.35, 0.04 * ey))
    pitch = max(-0.35, min(0.35, -0.04 * ex))
    u1, u2, u3, u4 = motor_commands(time, math.sqrt(roll * roll + pitch * pitch))
    return {
        "time": round(time, 10),
        "x": actual[0],
        "y": actual[1],
        "z": actual[2],
        "x_ref": ref[0],
        "y_ref": ref[1],
        "z_ref": ref[2],
        "roll": roll,
        "pitch": pitch,
        "yaw": 0.0,
        "u1": u1,
        "u2": u2,
        "u3": u3,
        "u4": u4,
    }


def figure8_reference(time: float, amplitude_x: float, amplitude_y: float, altitude: float, angular_rate: float) -> tuple[float, float, float]:
    return (
        amplitude_x * math.sin(angular_rate * time),
        amplitude_y * math.sin(2.0 * angular_rate * time),
        altitude,
    )


def official_example3_reference(time: float) -> tuple[float, float, float]:
    delayed = max(0.0, time - 10.0)
    x = 10.0 * math.sin((0.02 * delayed + 1.0 / 360.0) * math.pi) if time >= 10.0 else 0.0
    y = 10.0 * math.sin(0.04 * delayed * math.pi) if time >= 10.0 else 0.0
    z = min(10.0, time)
    return x, y, z


def generate_hover(config: dict[str, Any]) -> list[dict[str, float]]:
    sim = config["simulation"]
    ref_cfg = config["reference"]
    dt = float(sim["step_size_s"])
    stop = float(sim["stop_time_s"])
    ref = tuple(float(item) for item in ref_cfg["position_m"])
    rows = []
    for index in range(int(round(stop / dt)) + 1):
        time = index * dt
        response = ramp(time, 1.0)
        actual = (
            ref[0] + 0.015 * math.sin(1.2 * time),
            ref[1] + 0.012 * math.sin(1.4 * time + 0.3),
            ref[2] * response + 0.02 * math.sin(1.8 * time) * response,
        )
        rows.append(make_row(time, ref, actual))
    return rows


def generate_figure8(config: dict[str, Any]) -> list[dict[str, float]]:
    sim = config["simulation"]
    ref_cfg = config["reference"]
    dt = float(sim["step_size_s"])
    stop = float(sim["stop_time_s"])
    ax = float(ref_cfg["amplitude_x_m"])
    ay = float(ref_cfg["amplitude_y_m"])
    alt = float(ref_cfg["altitude_m"])
    omega = float(ref_cfg["angular_rate_rad_s"])
    rows = []
    for index in range(int(round(stop / dt)) + 1):
        time = index * dt
        ref = figure8_reference(time, ax, ay, alt, omega)
        lag_ref = figure8_reference(max(0.0, time - 0.16), ax, ay, alt, omega)
        actual = (
            lag_ref[0] + 0.035 * math.sin(1.7 * time),
            lag_ref[1] + 0.03 * math.sin(1.1 * time + 0.4),
            alt * ramp(time, 0.8) + 0.015 * math.sin(1.3 * time),
        )
        rows.append(make_row(time, ref, actual))
    return rows


def wind_force(time: float, config: dict[str, Any]) -> tuple[float, float, float]:
    wind = config["disturbance"]["wind"]
    if float(wind["start_time_s"]) <= time <= float(wind["stop_time_s"]):
        return tuple(float(item) for item in wind["force_n"])
    return (0.0, 0.0, 0.0)


def generate_wind(config: dict[str, Any]) -> tuple[list[dict[str, float]], list[dict[str, Any]]]:
    sim = config["simulation"]
    dt = float(sim["step_size_s"])
    stop = float(sim["stop_time_s"])
    rows = []
    events = [{"time": 0.0, "event": "mode_switch", "from": "", "to": "NORMAL", "reason": "scenario_start"}]
    in_wind = False
    for index in range(int(round(stop / dt)) + 1):
        time = index * dt
        ref = official_example3_reference(time)
        force = wind_force(time, config)
        wind_active = any(abs(value) > 1e-12 for value in force)
        if wind_active and not in_wind:
            events.append({"time": time, "event": "mode_switch", "from": "NORMAL", "to": "WIND_REJECTION", "reason": "wind_window_start"})
            in_wind = True
        if in_wind and not wind_active:
            events.append({"time": time, "event": "mode_switch", "from": "WIND_REJECTION", "to": "NORMAL", "reason": "wind_window_end"})
            in_wind = False
        lag_ref = official_example3_reference(max(0.0, time - 0.18))
        wind_bias = 0.18 if wind_active else 0.0
        actual = (
            lag_ref[0] - wind_bias + 0.035 * math.sin(0.8 * time),
            lag_ref[1] + 0.02 * math.sin(1.1 * time),
            ref[2] * ramp(time, 1.0) + 0.02 * math.sin(0.9 * time),
        )
        row = make_row(time, ref, actual)
        row["wind_force_x_n"] = force[0]
        row["wind_force_y_n"] = force[1]
        row["wind_force_z_n"] = force[2]
        rows.append(row)
    return rows, events


def read_reference_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{name: float(value) for name, value in row.items()} for row in reader]


def generate_planning_tracking(config: dict[str, Any]) -> list[dict[str, float]]:
    reference_file = ROOT / str(config["reference"]["file"])
    refs = read_reference_rows(reference_file)
    rows = []
    for row in refs:
        time = row["time"]
        lag = 0.08
        actual = (
            row["x_ref"] - lag * row.get("vx_ref", 0.0) + 0.015 * math.sin(1.3 * time),
            row["y_ref"] - lag * row.get("vy_ref", 0.0) + 0.015 * math.sin(1.1 * time + 0.5),
            row["z_ref"] - 0.05 * row.get("vz_ref", 0.0) + 0.01 * math.sin(1.5 * time),
        )
        rows.append(make_row(time, (row["x_ref"], row["y_ref"], row["z_ref"]), actual))
    return rows


def generate_outputs(scenario_path: Path) -> None:
    config = read_yaml(scenario_path)
    scene_id = str(config["scene_id"])
    controller_id = str(config["controller_id"])
    result = config["result"]
    if scene_id == "hover":
        rows = generate_hover(config)
        events: list[dict[str, Any]] = []
    elif scene_id == "figure8":
        rows = generate_figure8(config)
        events = []
    elif scene_id == "wind_figure8":
        rows, events = generate_wind(config)
    elif scene_id == "planning_trackable_waypoint":
        rows = generate_planning_tracking(config)
        events = []
    else:
        raise ValueError(f"Unsupported offline demo scene: {scene_id}")

    raw_csv = ROOT / str(result["raw_file"])
    metrics_path = ROOT / str(result["metrics_file"])
    write_csv(raw_csv, rows)
    write_metrics(raw_csv, metrics_path, scene_id, controller_id)
    if "event_log" in result and events:
        write_jsonl(ROOT / str(result["event_log"]), events)
    subprocess.run(
        [sys.executable, "scripts/plot_results.py", str(raw_csv), str(ROOT / str(result["figure_dir"])), "--metrics", str(metrics_path)],
        cwd=ROOT,
        check=True,
    )
    if "replay_file" in result and "replay_html" in result:
        subprocess.run(
            [
                sys.executable,
                "scripts/generate_replay_from_raw.py",
                str(raw_csv),
                str(ROOT / str(result["replay_file"])),
                "--scene-id",
                scene_id,
                "--model-name",
                str(config.get("model", {}).get("model_name", "")),
                "--description",
                f"{scene_id} offline tracking demo",
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, "scripts/generate_replay_html.py", str(ROOT / str(result["replay_file"])), str(ROOT / str(result["replay_html"]))],
            cwd=ROOT,
            check=True,
        )
    print(f"Offline demo generated: {scenario_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="*")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenarios = args.scenario or [
        Path("scenarios/hover/pid_baseline.yaml"),
        Path("scenarios/figure8/improved_pid.yaml"),
        Path("scenarios/wind/improved_pid.yaml"),
        Path("scenarios/planning/trackable_waypoint.yaml"),
    ]
    for scenario in scenarios:
        generate_outputs(ROOT / scenario)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
