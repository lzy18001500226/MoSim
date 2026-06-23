#!/usr/bin/env python3
"""Evaluate Gazebo takeoff-hover-land plant sanity evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            data = json.loads(line)
            if isinstance(data, dict):
                rows.append(data)
    return rows


def row_position(row: dict[str, Any]) -> list[float] | None:
    value = row.get("position_m")
    if not (isinstance(value, list) and len(value) == 3):
        return None
    try:
        pos = [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None
    return pos if all(math.isfinite(item) for item in pos) else None


def row_tilt(row: dict[str, Any]) -> float | None:
    value = row.get("euler_rpy_rad")
    if not (isinstance(value, list) and len(value) >= 2):
        return None
    try:
        roll = float(value[0])
        pitch = float(value[1])
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(roll) and math.isfinite(pitch)):
        return None
    return math.hypot(roll, pitch)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    controller_report_path = project_path(args.controller_report_json)
    controller_trace_path = project_path(args.controller_trace_jsonl)
    adapter_trace_path = project_path(args.adapter_trace_jsonl)
    truth_path = project_path(args.truth_pose_jsonl)
    truth_summary_path = project_path(args.truth_summary_json)

    controller = read_json(controller_report_path)
    trace = read_jsonl(controller_trace_path)
    adapter = read_jsonl(adapter_trace_path)
    truth_summary = read_json(truth_summary_path)
    blockers: list[str] = []
    warnings: list[str] = []
    if controller.get("status") != "completed":
        blockers.append(f"controller_not_completed:{controller.get('status')}")
    if len(trace) < args.min_controller_samples:
        blockers.append(f"controller_samples_below_min:{len(trace)}<{args.min_controller_samples}")
    adapter_published = len([row for row in adapter if row.get("status") == "published"])
    if adapter_published < args.min_adapter_samples:
        blockers.append(f"adapter_published_below_min:{adapter_published}<{args.min_adapter_samples}")

    phase_rows: dict[str, list[dict[str, Any]]] = {"takeoff": [], "hover": [], "land": [], "settle": []}
    for row in trace:
        phase = str(row.get("phase", ""))
        if phase in phase_rows:
            phase_rows[phase].append(row)
    for phase in ["takeoff", "hover", "land"]:
        if len(phase_rows[phase]) < args.min_phase_samples:
            blockers.append(f"{phase}_samples_below_min:{len(phase_rows[phase])}<{args.min_phase_samples}")

    positions: list[list[float]] = []
    valid_rows: list[tuple[dict[str, Any], list[float]]] = []
    for row in trace:
        pos = row_position(row)
        if pos is not None:
            positions.append(pos)
            valid_rows.append((row, pos))
    if not positions:
        blockers.append("positions_missing")
        min_z = max_z = final_z = max_xy = max_tilt = max_airborne_tilt = max_contact_tilt = None
        airborne_tilt_samples = contact_tilt_samples = 0
    else:
        origin = positions[0]
        min_z = min(pos[2] for pos in positions)
        max_z = max(pos[2] for pos in positions)
        final_z = positions[-1][2]
        max_xy = max(math.hypot(pos[0] - origin[0], pos[1] - origin[1]) for pos in positions)
        tilt_rows = [(row, pos, tilt) for row, pos in valid_rows if (tilt := row_tilt(row)) is not None]
        airborne_tilts = [
            tilt
            for row, pos, tilt in tilt_rows
            if str(row.get("phase", "")) in {"takeoff", "hover", "land"} and pos[2] >= args.min_airborne_tilt_z_m
        ]
        contact_tilts = [
            tilt
            for _row, pos, tilt in tilt_rows
            if pos[2] < args.min_airborne_tilt_z_m
        ]
        max_tilt = max((tilt for _row, _pos, tilt in tilt_rows), default=None)
        max_airborne_tilt = max(airborne_tilts, default=None)
        max_contact_tilt = max(contact_tilts, default=None)
        airborne_tilt_samples = len(airborne_tilts)
        contact_tilt_samples = len(contact_tilts)
        if max_z < args.min_takeoff_peak_z_m:
            blockers.append(f"takeoff_peak_z_below_min:{max_z:.6f}<{args.min_takeoff_peak_z_m:.6f}")
        if phase_rows["hover"]:
            hover_z = [float(row["position_m"][2]) for row in phase_rows["hover"] if isinstance(row.get("position_m"), list)]
            hover_error_max = max(abs(z - args.hover_altitude_m) for z in hover_z) if hover_z else None
            hover_error_mean = sum(abs(z - args.hover_altitude_m) for z in hover_z) / len(hover_z) if hover_z else None
            settled_start = min(len(hover_z), int(len(hover_z) * args.hover_settled_fraction))
            settled_hover_z = hover_z[settled_start:] or hover_z
            hover_settled_error_max = max(abs(z - args.hover_altitude_m) for z in settled_hover_z) if settled_hover_z else None
            hover_settled_error_mean = (
                sum(abs(z - args.hover_altitude_m) for z in settled_hover_z) / len(settled_hover_z)
                if settled_hover_z
                else None
            )
            if hover_error_max is None:
                blockers.append("hover_altitude_missing")
            elif hover_settled_error_max is None:
                blockers.append("hover_settled_altitude_missing")
            elif hover_settled_error_max > args.max_hover_abs_z_error_m:
                blockers.append(f"hover_settled_abs_z_error_above_max:{hover_settled_error_max:.6f}>{args.max_hover_abs_z_error_m:.6f}")
        else:
            hover_error_max = hover_error_mean = hover_settled_error_max = hover_settled_error_mean = None
        if final_z > args.max_final_landed_z_m:
            blockers.append(f"final_landed_z_above_max:{final_z:.6f}>{args.max_final_landed_z_m:.6f}")
        if max_xy > args.max_xy_distance_m:
            blockers.append(f"max_xy_distance_above_max:{max_xy:.6f}>{args.max_xy_distance_m:.6f}")
        if max_airborne_tilt is None:
            blockers.append("airborne_tilt_missing")
        elif max_airborne_tilt > args.max_tilt_rad:
            blockers.append(f"max_airborne_tilt_above_max:{max_airborne_tilt:.6f}>{args.max_tilt_rad:.6f}")
        if max_contact_tilt is not None and max_contact_tilt > args.max_contact_tilt_warning_rad:
            warnings.append(f"contact_or_low_altitude_tilt_high:{max_contact_tilt:.6f}>{args.max_contact_tilt_warning_rad:.6f}")

    duration = float(controller.get("duration_s") or 0.0)
    if duration < args.min_duration_s:
        blockers.append(f"duration_below_min:{duration:.3f}<{args.min_duration_s:.3f}")

    gate_passed = not blockers
    return {
        "schema": "mosim.gazebo_takeoff_hover_land_eval.v1",
        "status": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "inputs": {
            "controller_report_json": rel(controller_report_path),
            "controller_trace_jsonl": rel(controller_trace_path),
            "adapter_trace_jsonl": rel(adapter_trace_path),
            "truth_pose_jsonl": rel(truth_path),
            "truth_summary_json": rel(truth_summary_path),
        },
        "counts": {
            "controller_samples": len(trace),
            "adapter_published": adapter_published,
            "truth_summary_count": truth_summary.get("count"),
            "phase_samples": {key: len(value) for key, value in phase_rows.items()},
            "airborne_tilt_samples": airborne_tilt_samples,
            "contact_tilt_samples": contact_tilt_samples,
        },
        "metrics": {
            "duration_s": round(duration, 6),
            "min_z_m": round(min_z, 6) if min_z is not None else None,
            "max_z_m": round(max_z, 6) if max_z is not None else None,
            "final_z_m": round(final_z, 6) if final_z is not None else None,
            "hover_max_abs_z_error_m": round(hover_error_max, 6) if "hover_error_max" in locals() and hover_error_max is not None else None,
            "hover_mean_abs_z_error_m": round(hover_error_mean, 6) if "hover_error_mean" in locals() and hover_error_mean is not None else None,
            "hover_settled_max_abs_z_error_m": round(hover_settled_error_max, 6) if "hover_settled_error_max" in locals() and hover_settled_error_max is not None else None,
            "hover_settled_mean_abs_z_error_m": round(hover_settled_error_mean, 6) if "hover_settled_error_mean" in locals() and hover_settled_error_mean is not None else None,
            "max_xy_distance_m": round(max_xy, 6) if max_xy is not None else None,
            "max_tilt_rad": round(max_tilt, 6) if max_tilt is not None else None,
            "max_airborne_tilt_rad": round(max_airborne_tilt, 6) if max_airborne_tilt is not None else None,
            "max_contact_tilt_rad": round(max_contact_tilt, 6) if max_contact_tilt is not None else None,
        },
        "thresholds": {
            "min_duration_s": args.min_duration_s,
            "min_takeoff_peak_z_m": args.min_takeoff_peak_z_m,
            "hover_altitude_m": args.hover_altitude_m,
            "hover_settled_fraction": args.hover_settled_fraction,
            "max_hover_abs_z_error_m": args.max_hover_abs_z_error_m,
            "max_final_landed_z_m": args.max_final_landed_z_m,
            "max_xy_distance_m": args.max_xy_distance_m,
            "max_tilt_rad": args.max_tilt_rad,
            "min_airborne_tilt_z_m": args.min_airborne_tilt_z_m,
            "max_contact_tilt_warning_rad": args.max_contact_tilt_warning_rad,
        },
        "blockers": blockers,
        "warnings": warnings,
        "claim_boundary": [
            "This proves only a bounded Gazebo takeoff-hover-land response using the declared controller runtime.",
            "Airborne attitude stability is evaluated separately from low-altitude/contact attitude, which remains reported as a warning.",
            "It does not prove generated C/C++ deployment, full SIL equivalence, competition controller performance, planner_ready, final closed_loop acceptance, or multi-UAV readiness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller-report-json", required=True, type=Path)
    parser.add_argument("--controller-trace-jsonl", required=True, type=Path)
    parser.add_argument("--adapter-trace-jsonl", required=True, type=Path)
    parser.add_argument("--truth-pose-jsonl", required=True, type=Path)
    parser.add_argument("--truth-summary-json", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--hover-altitude-m", type=float, default=1.0)
    parser.add_argument("--min-controller-samples", type=int, default=120)
    parser.add_argument("--min-adapter-samples", type=int, default=120)
    parser.add_argument("--min-phase-samples", type=int, default=20)
    parser.add_argument("--min-duration-s", type=float, default=18.0)
    parser.add_argument("--min-takeoff-peak-z-m", type=float, default=0.85)
    parser.add_argument("--max-hover-abs-z-error-m", type=float, default=0.45)
    parser.add_argument("--hover-settled-fraction", type=float, default=0.5)
    parser.add_argument("--max-final-landed-z-m", type=float, default=0.45)
    parser.add_argument("--max-xy-distance-m", type=float, default=1.2)
    parser.add_argument("--max-tilt-rad", type=float, default=0.35)
    parser.add_argument("--min-airborne-tilt-z-m", type=float, default=0.18)
    parser.add_argument("--max-contact-tilt-warning-rad", type=float, default=0.80)
    args = parser.parse_args()
    output = project_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
