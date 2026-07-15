#!/usr/bin/env python3
"""Locate the first sustained divergence in the FAST-LIO -> PX4 EKF chain."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]


def project_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def finite(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSONL at {rel(path)}:{line_number}: {exc}") from exc
            if isinstance(item, dict):
                rows.append(item)
    return rows


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def metrics(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "rmse": None, "p95": None, "max": None}
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "rmse": math.sqrt(sum(value * value for value in values) / len(values)),
        "p95": percentile(values, 0.95),
        "max": max(values),
    }


def vec(item: Any, names: tuple[str, str, str]) -> tuple[float, float, float] | None:
    if not isinstance(item, dict):
        return None
    values = tuple(finite(item.get(name)) for name in names)
    if any(value is None for value in values):
        return None
    return values  # type: ignore[return-value]


def difference(
    left: Any,
    right: Any,
    names: tuple[str, str, str],
) -> dict[str, float] | None:
    lhs = vec(left, names)
    rhs = vec(right, names)
    if lhs is None or rhs is None:
        return None
    dx, dy, dz = (lhs[index] - rhs[index] for index in range(3))
    return {
        "x": dx,
        "y": dy,
        "z": dz,
        "xy": math.hypot(dx, dy),
        "xyz": math.sqrt(dx * dx + dy * dy + dz * dz),
        "z_abs": abs(dz),
    }


def item_age(item: Any) -> float | None:
    if not isinstance(item, dict):
        return None
    return finite(item.get("age_s"))


def first_sustained(
    samples: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    *,
    start_time_s: float,
    min_duration_s: float,
) -> dict[str, Any] | None:
    run_start: float | None = None
    first: dict[str, Any] | None = None
    for sample in samples:
        t = finite(sample.get("t"))
        if t is None or t < start_time_s:
            continue
        if predicate(sample):
            if run_start is None:
                run_start = t
                first = sample
            if t - run_start >= min_duration_s:
                return {
                    "first_t_s": run_start,
                    "confirmed_t_s": t,
                    "duration_s": t - run_start,
                    "first_sample": first,
                    "confirmed_sample": sample,
                }
        else:
            run_start = None
            first = None
    return None


def comparison_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        t = finite(row.get("t"))
        if t is None:
            continue
        aligned = row.get("fastlio_aligned_odom")
        vision = row.get("vision_pose")
        local = row.get("local_pose")
        local_velocity = row.get("local_velocity")
        local_odom = row.get("local_odom")
        truth = row.get("gazebo_pose") or row.get("truth")
        sample: dict[str, Any] = {
            "t": t,
            "aligned_vision_position": difference(aligned, vision, ("x", "y", "z")),
            "vision_local_position": difference(vision, local, ("x", "y", "z")),
            "aligned_local_position": difference(aligned, local, ("x", "y", "z")),
            "aligned_local_velocity": difference(aligned, local_velocity, ("vx", "vy", "vz")),
            "aligned_local_odom_velocity": difference(aligned, local_odom, ("vx", "vy", "vz")),
            "aligned_truth_velocity": difference(aligned, truth, ("vx", "vy", "vz")),
            "local_truth_velocity": difference(local_velocity, truth, ("vx", "vy", "vz")),
            "ages_s": {
                "aligned": item_age(aligned),
                "vision": item_age(vision),
                "local_pose": item_age(local),
                "local_velocity": item_age(local_velocity),
                "local_odom": item_age(local_odom),
            },
        }
        samples.append(sample)
    return samples


def comparison_metrics(
    samples: list[dict[str, Any]],
    key: str,
    start_time_s: float,
) -> dict[str, Any]:
    selected = [
        sample[key]
        for sample in samples
        if float(sample["t"]) >= start_time_s and isinstance(sample.get(key), dict)
    ]
    return {
        "xy_m": metrics([float(item["xy"]) for item in selected]),
        "z_abs_m": metrics([float(item["z_abs"]) for item in selected]),
        "xyz_m": metrics([float(item["xyz"]) for item in selected]),
    }


def age_metrics(
    samples: list[dict[str, Any]],
    key: str,
    start_time_s: float,
) -> dict[str, Any]:
    values = [
        float(sample["ages_s"][key])
        for sample in samples
        if float(sample["t"]) >= start_time_s
        and finite(sample.get("ages_s", {}).get(key)) is not None
    ]
    return metrics(values)


def event(
    samples: list[dict[str, Any]],
    key: str,
    component: str,
    threshold: float,
    args: argparse.Namespace,
) -> dict[str, Any] | None:
    result = first_sustained(
        samples,
        lambda sample: isinstance(sample.get(key), dict)
        and float(sample[key][component]) > threshold,
        start_time_s=args.analysis_start_s,
        min_duration_s=args.sustained_duration_s,
    )
    if result is None:
        return None
    result.update({"comparison": key, "component": component, "threshold": threshold})
    return result


def alignment_csv_metrics(path: Path, start_time_s: float) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "count": 0}
    residuals: list[float] = []
    stamp_deltas: list[float] = []
    first_over_05: dict[str, float] | None = None
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        for row in csv.DictReader(handle):
            t = finite(row.get("fast_stamp"))
            residual = finite(row.get("xy_residual_m"))
            delta = finite(row.get("stamp_delta_s"))
            if t is None or t < start_time_s:
                continue
            if residual is not None:
                residuals.append(residual)
                if first_over_05 is None and residual > 0.5:
                    first_over_05 = {"t_s": t, "xy_residual_m": residual}
            if delta is not None:
                stamp_deltas.append(abs(delta))
    return {
        "path": rel(path),
        "count": len(residuals),
        "xy_residual_m": metrics(residuals),
        "absolute_stamp_delta_s": metrics(stamp_deltas),
        "first_xy_residual_over_0_5_m": first_over_05,
    }


def render_markdown(report: dict[str, Any]) -> str:
    events = report["first_sustained_events"]
    lines = [
        "# Control Fusion Divergence Analysis",
        "",
        f"- Run: `{report['run_dir']}`",
        f"- Classification: `{report['classification']}`",
        f"- Analysis start: `{report['parameters']['analysis_start_s']:.3f} s`",
        f"- Sustained duration: `{report['parameters']['sustained_duration_s']:.3f} s`",
        "",
        "## First Sustained Events",
        "",
        "| Event | First t (s) | Confirmed t (s) | Threshold |",
        "|---|---:|---:|---:|",
    ]
    for name, item in events.items():
        if item is None:
            lines.append(f"| {name} | none | none | - |")
        else:
            lines.append(
                f"| {name} | {item['first_t_s']:.3f} | {item['confirmed_t_s']:.3f} | "
                f"{item['threshold']:.3f} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            *[f"- {item}" for item in report["findings"]],
            "",
            "This is passive offline evidence. It does not claim that the runtime gate passed.",
            "",
        ]
    )
    return "\n".join(lines)


def analyze(run_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    diag_dir = run_dir / "control_fusion_diagnostics"
    samples_path = diag_dir / "control_diagnostics_samples.jsonl"
    if not samples_path.exists():
        raise SystemExit(f"missing diagnostics samples: {rel(samples_path)}")
    rows = read_jsonl(samples_path)
    samples = comparison_samples(rows)

    comparisons = {
        key: comparison_metrics(samples, key, args.analysis_start_s)
        for key in (
            "aligned_vision_position",
            "vision_local_position",
            "aligned_local_position",
            "aligned_local_velocity",
            "aligned_local_odom_velocity",
            "aligned_truth_velocity",
            "local_truth_velocity",
        )
    }
    ages = {
        key: age_metrics(samples, key, args.analysis_start_s)
        for key in ("aligned", "vision", "local_pose", "local_velocity", "local_odom")
    }
    events = {
        "aligned_vision_xy": event(
            samples, "aligned_vision_position", "xy", args.input_position_xy_threshold_m, args
        ),
        "aligned_vision_z": event(
            samples, "aligned_vision_position", "z_abs", args.input_position_z_threshold_m, args
        ),
        "vision_local_xy": event(
            samples, "vision_local_position", "xy", args.position_xy_threshold_m, args
        ),
        "vision_local_z": event(
            samples, "vision_local_position", "z_abs", args.position_z_threshold_m, args
        ),
        "aligned_local_velocity_xy": event(
            samples, "aligned_local_velocity", "xy", args.velocity_xy_threshold_mps, args
        ),
        "aligned_local_velocity_z": event(
            samples, "aligned_local_velocity", "z_abs", args.velocity_z_threshold_mps, args
        ),
    }

    aligned_vision_p95 = comparisons["aligned_vision_position"]["xy_m"]["p95"]
    vision_local_event = events["vision_local_xy"] or events["vision_local_z"]
    velocity_event = events["aligned_local_velocity_xy"] or events["aligned_local_velocity_z"]
    if (
        aligned_vision_p95 is not None
        and aligned_vision_p95 <= args.input_position_xy_threshold_m
        and vision_local_event is not None
    ):
        classification = "px4_estimator_divergence_after_consistent_mavros_input"
    elif events["aligned_vision_xy"] or events["aligned_vision_z"]:
        classification = "input_bridge_or_timestamp_divergence"
    else:
        classification = "no_sustained_position_divergence_at_configured_thresholds"

    findings: list[str] = []
    if classification == "px4_estimator_divergence_after_consistent_mavros_input":
        findings.append("Aligned FAST-LIO and MAVROS vision pose remain consistent before PX4 local state diverges.")
    if velocity_event and vision_local_event:
        if float(velocity_event["first_t_s"]) < float(vision_local_event["first_t_s"]):
            findings.append("PX4 velocity divergence precedes the sustained PX4 position divergence.")
        else:
            findings.append("PX4 position divergence appears before the configured velocity divergence threshold.")
    elif velocity_event:
        findings.append("A sustained PX4 velocity divergence is present without a sustained position event at the configured threshold.")
    max_age = max(
        (float(value["max"]) for value in ages.values() if value.get("max") is not None),
        default=0.0,
    )
    if max_age <= args.message_age_threshold_s:
        findings.append("Recorded message ages stay below the configured stale-data threshold.")
    else:
        findings.append("At least one recorded message age exceeds the configured stale-data threshold.")

    report = {
        "schema": "mosim.control_fusion_divergence.v1",
        "run_dir": rel(run_dir),
        "samples_jsonl": rel(samples_path),
        "classification": classification,
        "parameters": {
            "analysis_start_s": args.analysis_start_s,
            "sustained_duration_s": args.sustained_duration_s,
            "input_position_xy_threshold_m": args.input_position_xy_threshold_m,
            "input_position_z_threshold_m": args.input_position_z_threshold_m,
            "position_xy_threshold_m": args.position_xy_threshold_m,
            "position_z_threshold_m": args.position_z_threshold_m,
            "velocity_xy_threshold_mps": args.velocity_xy_threshold_mps,
            "velocity_z_threshold_mps": args.velocity_z_threshold_mps,
            "message_age_threshold_s": args.message_age_threshold_s,
        },
        "row_count": len(rows),
        "comparison_metrics": comparisons,
        "message_age_metrics_s": ages,
        "first_sustained_events": events,
        "alignment_csv": alignment_csv_metrics(
            run_dir / "control_fastlio_dynamic_alignment.csv", args.analysis_start_s
        ),
        "findings": findings,
        "claim_boundary": "Passive offline diagnosis only; no runtime gate claim.",
    }
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--analysis-start-s", type=float, default=30.0)
    parser.add_argument("--sustained-duration-s", type=float, default=0.15)
    parser.add_argument("--input-position-xy-threshold-m", type=float, default=0.10)
    parser.add_argument("--input-position-z-threshold-m", type=float, default=0.05)
    parser.add_argument("--position-xy-threshold-m", type=float, default=0.50)
    parser.add_argument("--position-z-threshold-m", type=float, default=0.25)
    parser.add_argument("--velocity-xy-threshold-mps", type=float, default=0.75)
    parser.add_argument("--velocity-z-threshold-mps", type=float, default=0.50)
    parser.add_argument("--message-age-threshold-s", type=float, default=0.10)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_dir = project_path(args.run_dir)
    output_json = project_path(args.output_json) if args.output_json else run_dir / "CONTROL_FUSION_DIVERGENCE.json"
    output_md = project_path(args.output_md) if args.output_md else run_dir / "CONTROL_FUSION_DIVERGENCE.md"
    report = analyze(run_dir, args)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "classification": report["classification"],
                "output_json": rel(output_json),
                "output_md": rel(output_md),
                "first_sustained_events": report["first_sustained_events"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
