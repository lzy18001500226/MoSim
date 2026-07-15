#!/usr/bin/env python3
"""Offline FAST-LIO localization, timing, and fusion-chain diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from bisect import bisect_left
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PX4_INT_PARAMS = {
    "EKF2_EV_CTRL",
    "EKF2_HGT_REF",
    "EKF2_EV_NOISE_MD",
    "EKF2_AID_MASK",
}


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


def finite(value: Any) -> float | None:
    try:
        item = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(item):
        return None
    return item


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if isinstance(data, dict):
            rows.append(data)
    return rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_px4_params(text: str) -> dict[str, float | int | str]:
    """Extract PX4 param values from run snapshots/override logs."""
    params: dict[str, float | int | str] = {}
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("PARAM_OVERRIDE "):
            payload = line[len("PARAM_OVERRIDE ") :]
            if "=" in payload:
                name, value = payload.split("=", 1)
                params[name.strip()] = parse_param_value(value.strip())
            continue
        if line.startswith("PARAM_VERIFY_MAVPARAM "):
            current = line.rsplit(" ", 1)[-1].strip()
            continue
        if line.startswith("EKF2_") or line.startswith("MPC_"):
            current = line
            continue
        if current and line.startswith("real:"):
            if current in PX4_INT_PARAMS and current in params:
                continue
            value = parse_param_value(line.split(":", 1)[1].strip())
            params[current] = value
            continue
        if current and line.startswith("integer:") and current not in params:
            value = parse_param_value(line.split(":", 1)[1].strip())
            params[current] = value
            continue
        if current and line not in {"success: True", "success: False", "value:"}:
            value = parse_param_value(line)
            if value != line:
                params[current] = value
                current = None
    return params


def parse_param_value(value: str) -> float | int | str:
    try:
        as_float = float(value)
    except ValueError:
        return value
    if as_float.is_integer():
        return int(as_float)
    return as_float


def ev_ctrl_bits(value: Any) -> dict[str, bool] | None:
    parsed = finite(value)
    if parsed is None:
        return None
    bitmask = int(parsed)
    return {
        "horizontal_position": bool(bitmask & 1),
        "vertical_position": bool(bitmask & 2),
        "velocity_3d": bool(bitmask & 4),
        "yaw": bool(bitmask & 8),
    }


def angle_diff(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def scalar_metrics(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "rmse": None, "mean": None, "p95": None, "max": None}
    return {
        "count": len(values),
        "rmse": math.sqrt(sum(v * v for v in values) / len(values)),
        "mean": sum(values) / len(values),
        "p95": percentile(values, 0.95),
        "max": max(values),
    }


def time_stats(series: list[dict[str, Any]]) -> dict[str, Any]:
    if len(series) < 2:
        return {"count": len(series)}
    times = [float(item["t"]) for item in series]
    gaps = [b - a for a, b in zip(times, times[1:])]
    elapsed = times[-1] - times[0]
    negative = [gap for gap in gaps if gap < -1e-6]
    return {
        "count": len(series),
        "first": times[0],
        "last": times[-1],
        "duration_s": elapsed,
        "avg_hz": (len(series) - 1) / elapsed if elapsed > 0 else None,
        "min_gap_s": min(gaps),
        "max_gap_s": max(gaps),
        "negative_gap_count": len(negative),
    }


def extract_topic_series(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    series: list[dict[str, Any]] = []
    last_signature: tuple[Any, ...] | None = None
    for row in rows:
        item = row.get(key)
        if not isinstance(item, dict):
            continue
        t = finite(item.get("t"))
        x = finite(item.get("x"))
        y = finite(item.get("y"))
        z = finite(item.get("z"))
        if t is None or x is None or y is None or z is None:
            continue
        yaw = finite(item.get("yaw"))
        roll = finite(item.get("roll"))
        pitch = finite(item.get("pitch"))
        sig = (
            round(t, 6),
            round(x, 6),
            round(y, 6),
            round(z, 6),
            round(yaw, 6) if yaw is not None else None,
        )
        if sig == last_signature:
            continue
        last_signature = sig
        series.append(
            {
                "t": t,
                "x": x,
                "y": y,
                "z": z,
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw,
                "frame_id": item.get("frame_id"),
                "child_frame_id": item.get("child_frame_id"),
            }
        )
    series.sort(key=lambda item: float(item["t"]))
    return series


def nearest(series: list[dict[str, Any]], target_time: float) -> tuple[dict[str, Any], float] | None:
    if not series:
        return None
    times = [float(item["t"]) for item in series]
    idx = bisect_left(times, target_time)
    candidates: list[dict[str, Any]] = []
    if idx < len(series):
        candidates.append(series[idx])
    if idx > 0:
        candidates.append(series[idx - 1])
    if not candidates:
        return None
    best = min(candidates, key=lambda item: abs(float(item["t"]) - target_time))
    return best, float(best["t"]) - target_time


def compare_series(
    estimate: list[dict[str, Any]],
    truth: list[dict[str, Any]],
    *,
    max_delta_s: float,
    estimate_time_shift_s: float = 0.0,
) -> dict[str, Any]:
    xyz: list[float] = []
    xy: list[float] = []
    z_abs: list[float] = []
    dxs: list[float] = []
    dys: list[float] = []
    dzs: list[float] = []
    yaw_abs: list[float] = []
    deltas: list[float] = []
    first_offset: tuple[float, float, float] | None = None
    matched = 0
    for est in estimate:
        shifted_time = float(est["t"]) + estimate_time_shift_s
        match = nearest(truth, shifted_time)
        if match is None:
            continue
        tr, delta = match
        if abs(delta) > max_delta_s:
            continue
        dx = float(est["x"]) - float(tr["x"])
        dy = float(est["y"]) - float(tr["y"])
        dz = float(est["z"]) - float(tr["z"])
        if first_offset is None:
            first_offset = (dx, dy, dz)
        err_xy = math.hypot(dx, dy)
        err_xyz = math.sqrt(dx * dx + dy * dy + dz * dz)
        xyz.append(err_xyz)
        xy.append(err_xy)
        z_abs.append(abs(dz))
        dxs.append(dx)
        dys.append(dy)
        dzs.append(dz)
        if est.get("yaw") is not None and tr.get("yaw") is not None:
            yaw_abs.append(abs(angle_diff(float(est["yaw"]), float(tr["yaw"]))))
        deltas.append(delta)
        matched += 1
    return {
        "matched_count": matched,
        "time_delta_s": scalar_metrics([abs(v) for v in deltas]),
        "xyz_m": scalar_metrics(xyz),
        "xy_m": scalar_metrics(xy),
        "z_abs_m": scalar_metrics(z_abs),
        "yaw_abs_rad": scalar_metrics(yaw_abs),
        "axis_error_m": {
            "dx": scalar_metrics([abs(v) for v in dxs]),
            "dy": scalar_metrics([abs(v) for v in dys]),
            "dz": scalar_metrics([abs(v) for v in dzs]),
            "dx_mean_signed": (sum(dxs) / len(dxs)) if dxs else None,
            "dy_mean_signed": (sum(dys) / len(dys)) if dys else None,
            "dz_mean_signed": (sum(dzs) / len(dzs)) if dzs else None,
        },
        "first_offset_m": list(first_offset) if first_offset is not None else None,
        "estimate_time_shift_s": estimate_time_shift_s,
    }


def lead_lag_scan(
    estimate: list[dict[str, Any]],
    truth: list[dict[str, Any]],
    *,
    max_delta_s: float,
    scan_min_s: float,
    scan_max_s: float,
    scan_step_s: float,
) -> dict[str, Any]:
    points: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    steps = int(round((scan_max_s - scan_min_s) / scan_step_s))
    for index in range(steps + 1):
        shift = scan_min_s + index * scan_step_s
        cmp = compare_series(
            estimate,
            truth,
            max_delta_s=max_delta_s,
            estimate_time_shift_s=shift,
        )
        xyz_rmse = cmp["xyz_m"]["rmse"]
        xy_rmse = cmp["xy_m"]["rmse"]
        point = {
            "estimate_time_shift_s": shift,
            "matched_count": cmp["matched_count"],
            "xyz_rmse_m": xyz_rmse,
            "xy_rmse_m": xy_rmse,
            "z_rmse_m": cmp["z_abs_m"]["rmse"],
        }
        points.append(point)
        if xyz_rmse is not None and (best is None or xyz_rmse < best["xyz_rmse_m"]):
            best = point
    zero = min(points, key=lambda item: abs(float(item["estimate_time_shift_s"]))) if points else None
    improvement = None
    if best and zero and zero.get("xyz_rmse_m"):
        improvement = (float(zero["xyz_rmse_m"]) - float(best["xyz_rmse_m"])) / float(zero["xyz_rmse_m"])
    return {
        "definition": "estimate_time_shift_s is added to estimate timestamps before nearest-neighbor matching to truth",
        "best": best,
        "zero_shift": zero,
        "xyz_rmse_relative_improvement": improvement,
        "scan_points": points,
    }


def csv_tracking_metrics(path: Path) -> dict[str, Any]:
    rows = read_csv_rows(path)
    phase_metrics: dict[str, Any] = {}
    for phase in sorted({row.get("phase", "") for row in rows}):
        values_xyz: list[float] = []
        values_xy: list[float] = []
        values_z: list[float] = []
        for row in rows:
            if row.get("phase", "") != phase:
                continue
            for keys in (("ex", "ey", "ez"), ("error_x", "error_y", "error_z")):
                ex = finite(row.get(keys[0]))
                ey = finite(row.get(keys[1]))
                ez = finite(row.get(keys[2]))
                if ex is not None and ey is not None and ez is not None:
                    values_xyz.append(math.sqrt(ex * ex + ey * ey + ez * ez))
                    values_xy.append(math.hypot(ex, ey))
                    values_z.append(abs(ez))
                    break
        if values_xyz:
            phase_metrics[phase or "<empty>"] = {
                "xyz_m": scalar_metrics(values_xyz),
                "xy_m": scalar_metrics(values_xy),
                "z_abs_m": scalar_metrics(values_z),
            }
    return {"path": rel(path), "phase_metrics": phase_metrics}


def topic_frames(series: list[dict[str, Any]]) -> dict[str, list[str]]:
    frames = sorted({str(item.get("frame_id")) for item in series if item.get("frame_id")})
    children = sorted({str(item.get("child_frame_id")) for item in series if item.get("child_frame_id")})
    return {"frame_id": frames, "child_frame_id": children}


def analyze_run(run_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    samples_path = run_dir / "control_diagnostics_samples.jsonl"
    rows = read_jsonl(samples_path)
    series = {
        "truth": extract_topic_series(rows, "truth"),
        "gazebo_pose": extract_topic_series(rows, "gazebo_pose"),
        "local_pose": extract_topic_series(rows, "local_pose"),
        "vision_pose": extract_topic_series(rows, "vision_pose"),
        "fastlio_raw": extract_topic_series(rows, "fastlio_odom"),
        "fastlio_aligned": extract_topic_series(rows, "fastlio_aligned_odom"),
    }
    truth = series["gazebo_pose"] or series["truth"]
    aligned = series["fastlio_aligned"]
    local = series["local_pose"]
    vision = series["vision_pose"]
    raw = series["fastlio_raw"]

    comparisons = {
        "fastlio_aligned_vs_truth": compare_series(aligned, truth, max_delta_s=args.max_delta_s),
        "mavros_local_vs_truth": compare_series(local, truth, max_delta_s=args.max_delta_s),
        "mavros_local_vs_fastlio_aligned": compare_series(local, aligned, max_delta_s=args.max_delta_s),
        "vision_pose_vs_fastlio_aligned": compare_series(vision, aligned, max_delta_s=args.max_delta_s),
        "vision_pose_vs_mavros_local": compare_series(vision, local, max_delta_s=args.max_delta_s),
        "fastlio_raw_vs_truth_frame_sanity_only": compare_series(raw, truth, max_delta_s=args.max_delta_s),
    }
    lag = {
        "fastlio_aligned_vs_truth": lead_lag_scan(
            aligned,
            truth,
            max_delta_s=args.max_delta_s,
            scan_min_s=args.scan_min_s,
            scan_max_s=args.scan_max_s,
            scan_step_s=args.scan_step_s,
        ),
        "mavros_local_vs_truth": lead_lag_scan(
            local,
            truth,
            max_delta_s=args.max_delta_s,
            scan_min_s=args.scan_min_s,
            scan_max_s=args.scan_max_s,
            scan_step_s=args.scan_step_s,
        ),
        "mavros_local_vs_fastlio_aligned": lead_lag_scan(
            local,
            aligned,
            max_delta_s=args.max_delta_s,
            scan_min_s=args.scan_min_s,
            scan_max_s=args.scan_max_s,
            scan_step_s=args.scan_step_s,
        ),
        "vision_pose_vs_mavros_local": lead_lag_scan(
            vision,
            local,
            max_delta_s=args.max_delta_s,
            scan_min_s=args.scan_min_s,
            scan_max_s=args.scan_max_s,
            scan_step_s=args.scan_step_s,
        ),
    }
    control_summary = read_json(run_dir / "control_diagnostics_summary.json")
    goal3 = read_json(run_dir / "GOAL3_FASTLIO_EKF_FUSION_AUDIT.json")
    time_tf = read_json(run_dir / "time_tf_audit.json")
    px4_params = (run_dir / "px4_param_overrides.txt").read_text(
        encoding="utf-8", errors="replace"
    ) if (run_dir / "px4_param_overrides.txt").exists() else ""
    px4_snapshot = (run_dir / "px4_param_snapshot_before_mission.txt").read_text(
        encoding="utf-8", errors="replace"
    ) if (run_dir / "px4_param_snapshot_before_mission.txt").exists() else ""
    effective_px4_params = parse_px4_params(px4_params + "\n" + px4_snapshot)
    ev_ctrl = effective_px4_params.get("EKF2_EV_CTRL")
    ev_bits = ev_ctrl_bits(ev_ctrl)

    findings: list[str] = []
    aligned_xyz = comparisons["fastlio_aligned_vs_truth"]["xyz_m"]["rmse"]
    aligned_xy = comparisons["fastlio_aligned_vs_truth"]["xy_m"]["rmse"]
    aligned_z = comparisons["fastlio_aligned_vs_truth"]["z_abs_m"]["rmse"]
    local_xyz = comparisons["mavros_local_vs_truth"]["xyz_m"]["rmse"]
    local_aligned_xyz = comparisons["mavros_local_vs_fastlio_aligned"]["xyz_m"]["rmse"]
    lag_best = lag["fastlio_aligned_vs_truth"]["best"]
    lag_improve = lag["fastlio_aligned_vs_truth"]["xyz_rmse_relative_improvement"]
    if aligned_xy is not None and aligned_z is not None and aligned_xy > max(0.02, 5.0 * aligned_z):
        findings.append("FAST-LIO aligned error is dominated by horizontal XY, not Z height.")
    if local_aligned_xyz is not None and aligned_xyz is not None and local_aligned_xyz < aligned_xyz * 0.6:
        findings.append("PX4 local tracks FAST-LIO aligned reasonably; main error is already present before EKF fusion.")
    if lag_improve is not None and lag_improve > 0.2:
        findings.append("Lead-lag scan materially improves RMSE; timestamp/delay compensation is a high-priority suspect.")
    if lag_best and abs(float(lag_best["estimate_time_shift_s"])) >= 0.04:
        findings.append("Best localization timestamp shift is larger than one control period; verify FAST-LIO stamp and EKF EV delay.")
    negative_gaps = goal3.get("checks", {}).get("negative_header_gaps", {})
    if any(int(v or 0) > 0 for v in negative_gaps.values()):
        findings.append("Goal3 audit saw negative header gaps; MAVROS/local timestamp ordering needs a stricter recorder or source check.")
    if ev_bits and ev_bits.get("velocity_3d"):
        findings.append(
            "EKF2_EV_CTRL includes 3D velocity fusion; current Sunray externalFusion publishes MAVROS vision_pose PoseStamped, so verify EV velocity availability before accepting this as the default."
        )
    if local_xyz is not None and aligned_xyz is not None and local_xyz > aligned_xyz * 1.2:
        findings.append("PX4 EKF local output is worse than aligned input; fusion noise/delay/status should be checked.")

    return {
        "run_dir": rel(run_dir),
        "samples_jsonl": rel(samples_path),
        "series": {
            name: {"time": time_stats(items), "frames": topic_frames(items)}
            for name, items in series.items()
        },
        "comparisons": comparisons,
        "lead_lag": lag,
        "existing_summaries": {
            "control_diagnostics": {
                "gazebo_fastlio_aligned_xyz_rmse_m": control_summary.get("gazebo_fastlio_aligned_xyz_rmse_m"),
                "gazebo_fastlio_aligned_xy_rmse_m": control_summary.get("gazebo_fastlio_aligned_xy_rmse_m"),
                "gazebo_fastlio_aligned_z_rmse_m": control_summary.get("gazebo_fastlio_aligned_z_rmse_m"),
                "gazebo_local_z_rmse_m": control_summary.get("gazebo_local_z_rmse_m"),
                "gazebo_vision_z_rmse_m": control_summary.get("gazebo_vision_z_rmse_m"),
            },
            "goal3_status": goal3.get("status"),
            "goal3_fusion_success_ratio": goal3.get("checks", {}).get("fusion_success_ratio"),
            "goal3_negative_header_gaps": negative_gaps,
            "time_tf_use_sim_time": time_tf.get("use_sim_time"),
            "time_tf_clock": time_tf.get("clock_topic_stats", {}),
        },
        "effective_px4_params": {
            "EKF2_EV_CTRL": ev_ctrl,
            "EKF2_EV_CTRL_bits": ev_bits,
            "EKF2_HGT_REF": effective_px4_params.get("EKF2_HGT_REF"),
            "EKF2_EV_DELAY": effective_px4_params.get("EKF2_EV_DELAY"),
            "EKF2_EV_NOISE_MD": effective_px4_params.get("EKF2_EV_NOISE_MD"),
            "EKF2_EVP_NOISE": effective_px4_params.get("EKF2_EVP_NOISE"),
            "EKF2_EVV_NOISE": effective_px4_params.get("EKF2_EVV_NOISE"),
            "EKF2_EVA_NOISE": effective_px4_params.get("EKF2_EVA_NOISE"),
        },
        "tracking_metrics": csv_tracking_metrics(run_dir / "trajectory_errors.csv"),
        "findings": findings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="*", help="Sunray run directories to analyze.")
    parser.add_argument(
        "--default-fastlio-runs",
        action="store_true",
        help="Analyze current Results/sunray_ros1/*fastlio_px4ctrl_single* directories.",
    )
    parser.add_argument("--output", default="Results/sunray_ros1/FASTLIO_CHAIN_OFFLINE_ANALYSIS.json")
    parser.add_argument("--max-delta-s", type=float, default=0.08)
    parser.add_argument("--scan-min-s", type=float, default=-0.30)
    parser.add_argument("--scan-max-s", type=float, default=0.30)
    parser.add_argument("--scan-step-s", type=float, default=0.01)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_dirs = [project_path(path) for path in args.run_dirs]
    if args.default_fastlio_runs:
        base = ROOT / "Results" / "sunray_ros1"
        run_dirs.extend(sorted(path for path in base.iterdir() if path.is_dir() and "fastlio_px4ctrl_single" in path.name))
    if not run_dirs:
        raise SystemExit("no run directories provided")

    output = project_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "mosim.sunray_ros1.fastlio_chain_offline_analysis.v1",
        "note": "Passive offline analysis. It reads existing run evidence and does not claim a live rerun.",
        "parameters": {
            "max_delta_s": args.max_delta_s,
            "scan_min_s": args.scan_min_s,
            "scan_max_s": args.scan_max_s,
            "scan_step_s": args.scan_step_s,
        },
        "runs": [analyze_run(run_dir, args) for run_dir in run_dirs],
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": rel(output), "runs": len(report["runs"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
