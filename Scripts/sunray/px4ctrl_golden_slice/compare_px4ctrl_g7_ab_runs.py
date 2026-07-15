#!/usr/bin/env python3
"""Compare px4ctrl Golden Slice Gazebo A/B runs.

The comparator is intentionally result-dir based: it does not start ROS,
Gazebo, PX4, MWORKS, or any controller process. It verifies that an original
px4ctrl run and an MWORKS-generated-core run used the same frozen runtime
conditions, both passed their mission gate, and have equivalent closed-loop
metrics under the G-PX4CTRL-7 tolerance rule.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from statistics import mean
from typing import Any


METRICS_FILE = "PX4CTRL_BASIC_MISSION_METRICS.json"
MANIFEST_FILE = "RUN_MANIFEST.json"

RMSE_ABS_TOL_M = 0.005
RMSE_REL_TOL = 0.05
P95_ABS_TOL_M = 0.005
P95_REL_TOL = 0.10
STEP_P95_ABS_TOL_M = 0.005
STEP_SETTLING_EXCLUSION_S = 2.0

STEP_SCENARIOS = {"step_x", "step_y", "step_z"}

HOVER_METRIC_PATHS = [
    "steady_hover.xy_rmse_m",
    "steady_hover.xy_max_m",
    "steady_hover.z_abs_rmse_m",
    "steady_hover.z_abs_max_m",
    "all_reference_tracking.xy_rmse_m",
    "all_reference_tracking.xy_p95_m",
    "all_reference_tracking.xy_max_m",
    "all_reference_tracking.xyz_rmse_m",
    "all_reference_tracking.xyz_p95_m",
    "all_reference_tracking.xyz_max_m",
    "all_reference_tracking.z_abs_rmse_m",
    "all_reference_tracking.z_abs_p95_m",
    "all_reference_tracking.z_abs_max_m",
]

TRAJECTORY_METRIC_PATHS = [
    "trajectory.xy_rmse_m",
    "trajectory.xy_p95_m",
    "trajectory.xy_max_m",
    "trajectory.xyz_rmse_m",
    "trajectory.xyz_p95_m",
    "trajectory.xyz_max_m",
    "trajectory.z_abs_rmse_m",
    "trajectory.z_abs_p95_m",
    "trajectory.z_abs_max_m",
    "all_reference_tracking.xy_rmse_m",
    "all_reference_tracking.xy_p95_m",
    "all_reference_tracking.xy_max_m",
    "all_reference_tracking.xyz_rmse_m",
    "all_reference_tracking.xyz_p95_m",
    "all_reference_tracking.xyz_max_m",
    "all_reference_tracking.z_abs_rmse_m",
    "all_reference_tracking.z_abs_p95_m",
    "all_reference_tracking.z_abs_max_m",
]

STEP_RESPONSE_METRIC_PATHS = [
    "step_response.settled_window.xy_rmse_m",
    "step_response.settled_window.xy_p95_m",
    "step_response.settled_window.xy_max_m",
    "step_response.settled_window.xyz_rmse_m",
    "step_response.settled_window.xyz_p95_m",
    "step_response.settled_window.xyz_max_m",
    "step_response.primary_axis_settled.rmse_m",
    "step_response.primary_axis_settled.p95_m",
    "step_response.primary_axis_settled.max_m",
]

MANIFEST_COMPARE_PATHS = [
    "mission",
    "controller",
    "gazebo.max_step_size_s",
    "gazebo.real_time_update_rate_hz",
    "px4ctrl.mass",
    "px4ctrl.hover_percentage",
    "px4ctrl.Kp_xy",
    "px4ctrl.Kp_z",
    "px4ctrl.Kv_xy",
    "px4ctrl.Kv_z",
    "px4ctrl.ctrl_freq_max",
    "px4ctrl.use_bodyrate_ctrl",
    "px4ctrl.start_external_fusion",
    "px4ctrl.external_fusion_use_vision_pose",
    "px4ctrl.odom_source",
    "px4ctrl.odom_topic",
]

CSV_TREND_SPECS = [
    {
        "file": "debug_px4ctrl.csv",
        "columns": [
            "des_a_x",
            "des_a_y",
            "des_a_z",
            "des_q_x",
            "des_q_y",
            "des_q_z",
            "des_q_w",
            "des_thr",
        ],
    },
    {
        "file": "target_attitude.csv",
        "columns": ["roll", "pitch", "yaw", "body_rate_x", "body_rate_y", "body_rate_z", "thrust"],
    },
]

BAD_LOG_PATTERNS = [
    re.compile(r"\bfailsafe\b", re.IGNORECASE),
    re.compile(r"\bsegmentation fault\b", re.IGNORECASE),
    re.compile(r"\babort(?:ed)?\b", re.IGNORECASE),
    re.compile(r"\bcore dumped\b", re.IGNORECASE),
    re.compile(r"\bexception\b", re.IGNORECASE),
    re.compile(r"\bfatal\b", re.IGNORECASE),
]

KNOWN_CLEANUP_PATTERNS = [
    re.compile(r"killed roslaunch", re.IGNORECASE),
    re.compile(r"process has died.*exit code -15", re.IGNORECASE),
    re.compile(r"shutting down", re.IGNORECASE),
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def nested_get(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for key in dotted.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def rel_diff(a: float, b: float) -> float | None:
    denom = max(abs(a), abs(b))
    if denom <= 1e-12:
        return 0.0
    return abs(a - b) / denom


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    idx = (len(values) - 1) * pct
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


def compare_metric(path: str, a_value: Any, b_value: Any, *, step_response_policy: bool = False) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": path,
        "original": a_value,
        "generated": b_value,
        "status": "not_applicable",
    }
    if a_value is None and b_value is None:
        return out
    if not is_number(a_value) or not is_number(b_value):
        out["status"] = "blocked"
        out["reason"] = "metric_missing_or_non_numeric"
        return out
    a = float(a_value)
    b = float(b_value)
    abs_delta = abs(a - b)
    rd = rel_diff(a, b)
    out.update({"abs_delta": abs_delta, "relative_delta": rd})
    is_p95 = "p95" in path
    if is_p95:
        passed = abs_delta <= P95_ABS_TOL_M or (rd is not None and rd <= P95_REL_TOL)
        out["tolerance"] = {
            "abs_delta_max_m": P95_ABS_TOL_M,
            "relative_delta_max": P95_REL_TOL,
        }
        if step_response_policy:
            passed = passed or abs_delta <= STEP_P95_ABS_TOL_M
            out["tolerance"]["step_response_abs_delta_max_m"] = STEP_P95_ABS_TOL_M
    else:
        passed = abs_delta <= RMSE_ABS_TOL_M or (rd is not None and rd <= RMSE_REL_TOL)
        out["tolerance"] = {
            "abs_delta_max_m": RMSE_ABS_TOL_M,
            "relative_delta_max": RMSE_REL_TOL,
        }
    out["status"] = "passed" if passed else "blocked"
    if not passed:
        out["reason"] = "g7_closed_loop_metric_delta_exceeds_tolerance"
    return out


def metrics_from_error_rows(rows: list[dict[str, float]]) -> dict[str, Any]:
    xy = [r["xy"] for r in rows]
    xyz = [r["xyz"] for r in rows]
    z_abs = [abs(r["ez"]) for r in rows]

    def rmse(values: list[float]) -> float | None:
        return math.sqrt(mean([v * v for v in values])) if values else None

    return {
        "matched_samples": len(rows),
        "xy_rmse_m": rmse(xy),
        "xy_p95_m": percentile(xy, 0.95),
        "xy_max_m": max(xy) if xy else None,
        "xyz_rmse_m": rmse(xyz),
        "xyz_p95_m": percentile(xyz, 0.95),
        "xyz_max_m": max(xyz) if xyz else None,
        "z_abs_rmse_m": rmse(z_abs),
        "z_abs_p95_m": percentile(z_abs, 0.95),
        "z_abs_max_m": max(z_abs) if z_abs else None,
    }


def axis_metrics_from_error_rows(rows: list[dict[str, float]], axis: str) -> dict[str, Any]:
    values = [abs(r[axis]) for r in rows]

    def rmse(values: list[float]) -> float | None:
        return math.sqrt(mean([v * v for v in values])) if values else None

    return {
        "rmse_m": rmse(values),
        "p95_m": percentile(values, 0.95),
        "max_m": max(values) if values else None,
        "final_abs_m": values[-1] if values else None,
    }


def compute_step_response_from_csv(run_dir: Path, scenario: str) -> dict[str, Any] | None:
    path = run_dir / "trajectory_errors.csv"
    if scenario not in STEP_SCENARIOS or not path.exists():
        return None
    rows: list[dict[str, float]] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("phase") != scenario:
                continue
            try:
                rows.append(
                    {
                        "t": float(row["t"]),
                        "ex": float(row["ex"]),
                        "ey": float(row["ey"]),
                        "ez": float(row["ez"]),
                        "xy": float(row["xy"]),
                        "xyz": float(row["xyz"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue
    if not rows:
        return None
    start_t = min(r["t"] for r in rows)
    settled = [r for r in rows if r["t"] >= start_t + STEP_SETTLING_EXCLUSION_S]
    primary_axis = {"step_x": "ex", "step_y": "ey", "step_z": "ez"}[scenario]
    cross_axes = [axis for axis in ("ex", "ey", "ez") if axis != primary_axis]
    return {
        "schema": "mosim.sunray_ros1.px4ctrl_step_response_metrics.v1",
        "status": "passed" if settled else "blocked",
        "reason": None if settled else "no_settled_step_rows",
        "source": "computed_from_trajectory_errors_csv",
        "settling_exclusion_s": STEP_SETTLING_EXCLUSION_S,
        "raw_full_step_diagnostic": metrics_from_error_rows(rows),
        "settled_window": metrics_from_error_rows(settled),
        "primary_axis": primary_axis,
        "primary_axis_settled": axis_metrics_from_error_rows(settled, primary_axis),
        "cross_axis_settled": {axis: axis_metrics_from_error_rows(settled, axis) for axis in cross_axes},
        "settled_sample_count": len(settled),
    }


def ensure_step_response(metrics: dict[str, Any], run_dir: Path, scenario: str) -> dict[str, Any]:
    if scenario not in STEP_SCENARIOS or metrics.get("step_response") is not None:
        return metrics
    computed = compute_step_response_from_csv(run_dir, scenario)
    if computed is not None:
        metrics = dict(metrics)
        metrics["step_response"] = computed
    return metrics


def compare_manifests(a: dict[str, Any], b: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path in MANIFEST_COMPARE_PATHS:
        av = nested_get(a, path)
        bv = nested_get(b, path)
        rows.append(
            {
                "path": path,
                "original": av,
                "generated": bv,
                "status": "passed" if av == bv else "blocked",
            }
        )
    a_profile = nested_get(a, "px4ctrl.core_profile") or nested_get(a, "controller_core_profile")
    b_profile = nested_get(b, "px4ctrl.core_profile") or nested_get(b, "controller_core_profile")
    rows.append(
        {
            "path": "px4ctrl.core_profile",
            "original": a_profile,
            "generated": b_profile,
            "status": "passed" if a_profile != b_profile else "blocked",
            "expected": "different A/B profiles",
        }
    )
    return rows


def read_csv_numeric(path: Path, columns: list[str]) -> list[dict[str, float]]:
    if not path.exists():
        return []
    rows: list[dict[str, float]] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item: dict[str, float] = {}
            ok = True
            for col in columns:
                try:
                    value = float(row[col])
                except (KeyError, TypeError, ValueError):
                    ok = False
                    break
                if not math.isfinite(value):
                    ok = False
                    break
                item[col] = value
            if ok:
                rows.append(item)
    return rows


def compare_csv_trend(a_dir: Path, b_dir: Path, file_name: str, columns: list[str]) -> dict[str, Any]:
    a_rows = read_csv_numeric(a_dir / file_name, columns)
    b_rows = read_csv_numeric(b_dir / file_name, columns)
    out: dict[str, Any] = {
        "file": file_name,
        "columns": columns,
        "original_samples": len(a_rows),
        "generated_samples": len(b_rows),
        "status": "blocked",
        "column_deltas": {},
    }
    n = min(len(a_rows), len(b_rows))
    if n < 20:
        out["reason"] = "not_enough_csv_samples"
        return out

    # Align by normalized sample index. Runtime durations differ slightly, but
    # each run follows the same mission phases and gate script.
    sample_count = min(1000, n)
    if sample_count < 2:
        out["reason"] = "not_enough_common_samples"
        return out

    a_last = len(a_rows) - 1
    b_last = len(b_rows) - 1
    for col in columns:
        diffs: list[float] = []
        for i in range(sample_count):
            ratio = i / (sample_count - 1)
            ai = round(ratio * a_last)
            bi = round(ratio * b_last)
            diffs.append(a_rows[ai][col] - b_rows[bi][col])
        sq = [d * d for d in diffs]
        out["column_deltas"][col] = {
            "rmse": math.sqrt(mean(sq)),
            "p95_abs": percentile([abs(d) for d in diffs], 0.95),
            "max_abs": max(abs(d) for d in diffs),
        }
    out["status"] = "passed"
    return out


def scan_logs(run_dir: Path) -> dict[str, Any]:
    matches: list[dict[str, str]] = []
    for path in sorted(run_dir.glob("*.log")):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, 1):
            if any(clean.search(line) for clean in KNOWN_CLEANUP_PATTERNS):
                continue
            if any(pattern.search(line) for pattern in BAD_LOG_PATTERNS):
                matches.append({"file": path.name, "line": str(idx), "text": line[:500]})
                if len(matches) >= 50:
                    break
    return {
        "status": "passed" if not matches else "blocked",
        "bad_pattern_matches": matches,
    }


def write_markdown(report: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# PX4CTRL G7 A/B Compare",
        "",
        f"- status: `{report['status']}`",
        f"- scenario: `{report['scenario']}`",
        f"- original: `{report['original_run_dir']}`",
        f"- generated: `{report['generated_run_dir']}`",
        "",
        "## Metric Comparisons",
        "",
        "| metric | original | generated | abs delta | rel delta | status |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in report["metric_comparisons"]:
        if row["status"] == "not_applicable":
            continue
        lines.append(
            "| {path} | {a} | {b} | {ad} | {rd} | {status} |".format(
                path=row["path"],
                a=row.get("original"),
                b=row.get("generated"),
                ad=row.get("abs_delta", ""),
                rd=row.get("relative_delta", ""),
                status=row["status"],
            )
        )
    lines.extend(["", "## Blockers", ""])
    blockers = report.get("blockers", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-run-dir", required=True, type=Path)
    parser.add_argument("--generated-run-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()

    original_dir = args.original_run_dir.resolve()
    generated_dir = args.generated_run_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    metrics_a = ensure_step_response(load_json(original_dir / METRICS_FILE), original_dir, args.scenario)
    metrics_b = ensure_step_response(load_json(generated_dir / METRICS_FILE), generated_dir, args.scenario)
    manifest_a = load_json(original_dir / MANIFEST_FILE)
    manifest_b = load_json(generated_dir / MANIFEST_FILE)

    if args.scenario == "hover":
        metric_paths = HOVER_METRIC_PATHS
        metric_scope = "hover"
        step_response_policy = False
    elif args.scenario in STEP_SCENARIOS:
        metric_paths = STEP_RESPONSE_METRIC_PATHS
        metric_scope = "step_response_settled"
        step_response_policy = True
    else:
        metric_paths = TRAJECTORY_METRIC_PATHS
        metric_scope = "trajectory"
        step_response_policy = False
    metric_rows = [
        compare_metric(path, nested_get(metrics_a, path), nested_get(metrics_b, path), step_response_policy=step_response_policy)
        for path in metric_paths
    ]
    manifest_rows = compare_manifests(manifest_a, manifest_b)
    trend_rows = [
        compare_csv_trend(original_dir, generated_dir, spec["file"], spec["columns"])
        for spec in CSV_TREND_SPECS
    ]
    log_a = scan_logs(original_dir)
    log_b = scan_logs(generated_dir)

    blockers: list[str] = []
    if metrics_a.get("status") != "passed":
        blockers.append(f"original_mission_not_passed:{metrics_a.get('status')}:{metrics_a.get('reason')}")
    if metrics_b.get("status") != "passed":
        blockers.append(f"generated_mission_not_passed:{metrics_b.get('status')}:{metrics_b.get('reason')}")
    if metrics_a.get("mission") != metrics_b.get("mission"):
        blockers.append(f"mission_mismatch:{metrics_a.get('mission')}!={metrics_b.get('mission')}")
    if args.scenario in STEP_SCENARIOS:
        if nested_get(metrics_a, "step_response.status") != "passed":
            blockers.append(f"original_step_response_not_passed:{nested_get(metrics_a, 'step_response.status')}")
        if nested_get(metrics_b, "step_response.status") != "passed":
            blockers.append(f"generated_step_response_not_passed:{nested_get(metrics_b, 'step_response.status')}")
    blockers.extend(f"manifest_mismatch:{row['path']}" for row in manifest_rows if row["status"] != "passed")
    blockers.extend(f"metric_delta:{row['path']}" for row in metric_rows if row["status"] == "blocked")
    blockers.extend(f"trend_unavailable:{row['file']}:{row.get('reason')}" for row in trend_rows if row["status"] != "passed")
    if log_a["status"] != "passed":
        blockers.append("original_log_bad_pattern")
    if log_b["status"] != "passed":
        blockers.append("generated_log_bad_pattern")

    report: dict[str, Any] = {
        "schema": "mosim.sunray_ros1.px4ctrl_g7_ab_compare.v1",
        "status": "passed" if not blockers else "blocked",
        "scenario": args.scenario,
        "original_run_dir": str(original_dir),
        "generated_run_dir": str(generated_dir),
        "tolerances": {
            "rmse_abs_delta_m": RMSE_ABS_TOL_M,
            "rmse_relative_delta": RMSE_REL_TOL,
            "p95_abs_delta_m": P95_ABS_TOL_M,
            "p95_relative_delta": P95_REL_TOL,
            "step_response_p95_abs_delta_m": STEP_P95_ABS_TOL_M if args.scenario in STEP_SCENARIOS else None,
            "step_settling_exclusion_s": STEP_SETTLING_EXCLUSION_S if args.scenario in STEP_SCENARIOS else None,
            "metric_scope": metric_scope,
        },
        "step_response_policy": {
            "enabled": args.scenario in STEP_SCENARIOS,
            "reason": "step references are discontinuous; raw full-step trajectory metrics are retained in each mission result as diagnostics",
            "compared_paths": STEP_RESPONSE_METRIC_PATHS if args.scenario in STEP_SCENARIOS else [],
            "original_step_response_status": nested_get(metrics_a, "step_response.status"),
            "generated_step_response_status": nested_get(metrics_b, "step_response.status"),
        },
        "mission_status": {
            "original": metrics_a.get("status"),
            "generated": metrics_b.get("status"),
            "mission_original": metrics_a.get("mission"),
            "mission_generated": metrics_b.get("mission"),
        },
        "manifest_comparisons": manifest_rows,
        "metric_comparisons": metric_rows,
        "control_output_trends": trend_rows,
        "log_scan": {"original": log_a, "generated": log_b},
        "blockers": blockers,
    }

    report_path = args.out_dir / "PX4CTRL_G7_AB_COMPARE.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, args.out_dir / "PX4CTRL_G7_AB_COMPARE.md")
    print(json.dumps({"status": report["status"], "report": str(report_path), "blockers": blockers}, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
