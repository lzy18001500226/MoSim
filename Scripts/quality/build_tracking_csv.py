"""Build standard MoSim tracking.csv from reference and state CSV logs.

This converter is offline. It aligns a trajectory/reference CSV with a
state/truth CSV and writes the standard tracking.csv consumed by
compute_tracking_metrics.py. It does not start ROS, Gazebo, PX4, MAVROS,
RViz, UE, or MWORKS.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import sys
from pathlib import Path
from typing import Any


STANDARD_COLUMNS = [
    "time_s",
    "phase",
    "ref_x_m",
    "ref_y_m",
    "ref_z_m",
    "truth_x_m",
    "truth_y_m",
    "truth_z_m",
    "saturated",
]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRACKING_SOURCES = ROOT / "Config" / "profiles" / "tracking_sources.json"
DEFAULT_COLUMN_ARGS = {
    "ref_time": "time_s",
    "ref_x": "ref_x_m",
    "ref_y": "ref_y_m",
    "ref_z": "ref_z_m",
    "state_time": "time_s",
    "state_x": "x_m",
    "state_y": "y_m",
    "state_z": "z_m",
    "phase_source": "reference",
    "default_phase": "unknown",
    "saturated_source": "state",
    "default_saturated": "0",
    "max_time_delta_s": 0.05,
}


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        rows = list(reader)
    if not columns:
        raise ValueError(f"{path}: CSV has no header")
    if not rows:
        raise ValueError(f"{path}: CSV has no rows")
    return columns, rows


def load_tracking_source_profiles(path: Path) -> dict[str, Any]:
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"tracking source profile file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"tracking source profile file is invalid JSON: {path}: {exc}") from exc
    profiles = packet.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError(f"{path}: expected top-level profiles object")
    return profiles


def get_tracking_source_profile(profiles: dict[str, Any], profile_id: str) -> dict[str, Any]:
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        raise ValueError(f"unknown tracking source profile: {profile_id}")
    return profile


def _optional_nested_mapping(profile: dict[str, Any], name: str, preferred_section: str) -> dict[str, Any]:
    sections = [preferred_section, "reference" if preferred_section == "state" else "state"]
    for section in sections:
        payload = profile.get(section, {}).get(name)
        if isinstance(payload, dict):
            return payload
    return {}


def _set_if_unset(args: argparse.Namespace, name: str, value: Any) -> None:
    if value is not None and getattr(args, name, None) is None:
        setattr(args, name, value)


def apply_standard_tracking_source_defaults(args: argparse.Namespace) -> argparse.Namespace:
    for name, value in DEFAULT_COLUMN_ARGS.items():
        if getattr(args, name, None) is None:
            setattr(args, name, value)
    return args


def apply_tracking_source_profile(
    args: argparse.Namespace,
    experiment_id: str | None = None,
) -> argparse.Namespace:
    profile_id = getattr(args, "tracking_source_profile", None)
    if profile_id:
        profiles = load_tracking_source_profiles(Path(args.tracking_sources))
        profile = get_tracking_source_profile(profiles, profile_id)
        compatible_ids = profile.get("compatible_experiment_ids", ["*"])
        if experiment_id and "*" not in compatible_ids and experiment_id not in compatible_ids:
            raise ValueError(
                f"tracking source profile {profile_id} is not compatible with experiment profile {experiment_id}"
            )

        reference = profile.get("reference", {})
        state = profile.get("state", {})
        alignment = profile.get("alignment", {})
        phase = _optional_nested_mapping(profile, "phase", "reference")
        saturated = _optional_nested_mapping(profile, "saturated", "state")

        _set_if_unset(args, "ref_time", reference.get("time"))
        _set_if_unset(args, "ref_x", reference.get("x"))
        _set_if_unset(args, "ref_y", reference.get("y"))
        _set_if_unset(args, "ref_z", reference.get("z"))
        _set_if_unset(args, "state_time", state.get("time"))
        _set_if_unset(args, "state_x", state.get("x"))
        _set_if_unset(args, "state_y", state.get("y"))
        _set_if_unset(args, "state_z", state.get("z"))
        _set_if_unset(args, "phase_column", phase.get("column"))
        _set_if_unset(args, "phase_source", phase.get("source"))
        _set_if_unset(args, "default_phase", phase.get("default"))
        _set_if_unset(args, "saturated_column", saturated.get("column"))
        _set_if_unset(args, "saturated_source", saturated.get("source"))
        _set_if_unset(args, "default_saturated", saturated.get("default"))
        _set_if_unset(args, "max_time_delta_s", alignment.get("max_time_delta_s"))
        args.tracking_source_profile_applied = profile_id
    else:
        args.tracking_source_profile_applied = None

    return apply_standard_tracking_source_defaults(args)


def require_column(columns: list[str], column: str, label: str) -> None:
    if column not in columns:
        raise ValueError(f"{label} CSV is missing required column: {column}")


def parse_float(row: dict[str, str], column: str, label: str) -> float:
    try:
        return float(row[column])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} column {column} is not numeric: {row.get(column)!r}") from exc


def sorted_by_time(rows: list[dict[str, str]], time_column: str, label: str) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: parse_float(row, time_column, label))


def closest_row(
    rows: list[dict[str, str]],
    times: list[float],
    target_time: float,
) -> tuple[dict[str, str], float]:
    index = bisect.bisect_left(times, target_time)
    candidates = []
    if index < len(rows):
        candidates.append((abs(times[index] - target_time), rows[index]))
    if index > 0:
        candidates.append((abs(times[index - 1] - target_time), rows[index - 1]))
    if not candidates:
        raise ValueError("state CSV has no rows after sorting")
    delta, row = min(candidates, key=lambda item: item[0])
    return row, delta


def validate_columns(args: argparse.Namespace, ref_columns: list[str], state_columns: list[str]) -> None:
    for column in (args.ref_time, args.ref_x, args.ref_y, args.ref_z):
        require_column(ref_columns, column, "reference")
    for column in (args.state_time, args.state_x, args.state_y, args.state_z):
        require_column(state_columns, column, "state")
    if args.phase_column and args.phase_source == "reference":
        require_column(ref_columns, args.phase_column, "reference")
    if args.phase_column and args.phase_source == "state":
        require_column(state_columns, args.phase_column, "state")
    if args.saturated_column and args.saturated_source == "reference":
        require_column(ref_columns, args.saturated_column, "reference")
    if args.saturated_column and args.saturated_source == "state":
        require_column(state_columns, args.saturated_column, "state")


def optional_value(
    ref_row: dict[str, str],
    state_row: dict[str, str],
    column: str | None,
    source: str,
    default: str,
) -> str:
    if not column:
        return default
    row = ref_row if source == "reference" else state_row
    return row.get(column, default)


def build_tracking_rows(
    args: argparse.Namespace,
    ref_rows: list[dict[str, str]],
    state_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    ref_sorted = sorted_by_time(ref_rows, args.ref_time, "reference")
    state_sorted = sorted_by_time(state_rows, args.state_time, "state")
    state_times = [parse_float(row, args.state_time, "state") for row in state_sorted]
    output_rows = []
    deltas = []
    for ref_row in ref_sorted:
        ref_time = parse_float(ref_row, args.ref_time, "reference")
        state_row, delta = closest_row(state_sorted, state_times, ref_time)
        if delta > args.max_time_delta_s:
            raise ValueError(
                f"no state sample within {args.max_time_delta_s}s for reference time {ref_time}; nearest delta={delta}"
            )
        deltas.append(delta)
        output_rows.append(
            {
                "time_s": f"{ref_time:.9g}",
                "phase": optional_value(ref_row, state_row, args.phase_column, args.phase_source, args.default_phase),
                "ref_x_m": ref_row[args.ref_x],
                "ref_y_m": ref_row[args.ref_y],
                "ref_z_m": ref_row[args.ref_z],
                "truth_x_m": state_row[args.state_x],
                "truth_y_m": state_row[args.state_y],
                "truth_z_m": state_row[args.state_z],
                "saturated": optional_value(
                    ref_row,
                    state_row,
                    args.saturated_column,
                    args.saturated_source,
                    args.default_saturated,
                ),
            }
        )
    return output_rows, {
        "aligned_rows": len(output_rows),
        "max_time_delta_s": max(deltas) if deltas else None,
        "mean_time_delta_s": sum(deltas) / len(deltas) if deltas else None,
    }


def validate_numeric_tracking(rows: list[dict[str, str]]) -> None:
    numeric_columns = [column for column in STANDARD_COLUMNS if column != "phase"]
    for index, row in enumerate(rows, start=2):
        for column in numeric_columns:
            try:
                float(row[column])
            except (KeyError, ValueError) as exc:
                raise ValueError(f"output row {index}: {column} is not numeric: {row.get(column)!r}") from exc


def write_tracking_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STANDARD_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def build_report(args: argparse.Namespace, row_stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "generator": "Scripts/quality/build_tracking_csv.py",
        "reference_csv": str(Path(args.reference_csv)),
        "state_csv": str(Path(args.state_csv)),
        "output_csv": str(Path(args.out)),
        "tracking_source_profile": getattr(args, "tracking_source_profile_applied", None),
        "alignment": {
            "mode": "nearest",
            "max_allowed_time_delta_s": args.max_time_delta_s,
            **row_stats,
        },
        "columns": {
            "reference": {
                "time": args.ref_time,
                "x": args.ref_x,
                "y": args.ref_y,
                "z": args.ref_z,
            },
            "state": {
                "time": args.state_time,
                "x": args.state_x,
                "y": args.state_y,
                "z": args.state_z,
            },
            "phase": {"source": args.phase_source, "column": args.phase_column, "default": args.default_phase},
            "saturated": {
                "source": args.saturated_source,
                "column": args.saturated_column,
                "default": args.default_saturated,
            },
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-csv", required=True, help="Reference trajectory CSV")
    parser.add_argument("--state-csv", required=True, help="State/truth CSV")
    parser.add_argument("--out", required=True, help="Standard tracking.csv output path")
    parser.add_argument("--tracking-source-profile", help="Registered TrackingSourceProfile id")
    parser.add_argument(
        "--tracking-sources",
        default=str(DEFAULT_TRACKING_SOURCES),
        help="TrackingSourceProfile registry JSON path",
    )
    parser.add_argument("--ref-time", help="Reference time column")
    parser.add_argument("--ref-x", help="Reference x column")
    parser.add_argument("--ref-y", help="Reference y column")
    parser.add_argument("--ref-z", help="Reference z column")
    parser.add_argument("--state-time", help="State time column")
    parser.add_argument("--state-x", help="State x column")
    parser.add_argument("--state-y", help="State y column")
    parser.add_argument("--state-z", help="State z column")
    parser.add_argument("--phase-column", help="Optional phase column")
    parser.add_argument("--phase-source", choices=("reference", "state"))
    parser.add_argument("--default-phase")
    parser.add_argument("--saturated-column", help="Optional saturated column")
    parser.add_argument("--saturated-source", choices=("reference", "state"))
    parser.add_argument("--default-saturated")
    parser.add_argument("--max-time-delta-s", type=float)
    parser.add_argument("--report", help="Optional JSON report output path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        apply_tracking_source_profile(args)
        ref_columns, ref_rows = load_rows(Path(args.reference_csv))
        state_columns, state_rows = load_rows(Path(args.state_csv))
        validate_columns(args, ref_columns, state_columns)
        tracking_rows, row_stats = build_tracking_rows(args, ref_rows, state_rows)
        validate_numeric_tracking(tracking_rows)
        write_tracking_csv(Path(args.out), tracking_rows)
        report = build_report(args, row_stats)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
