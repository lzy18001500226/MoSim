#!/usr/bin/env python3
"""Compare six graphical PID MIL trajectories with the CFunction MIL references."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALGORITHMS = [
    "cascade_pid",
    "gain_scheduled_pid",
    "fuzzy_pid",
    "neural_pid",
    "anti_windup",
    "feedforward_profile",
]
OUTPUTS = ["command", "outer_command", "unsaturated_command", "integral", "scheduled_gain"]


def load_rows(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return [{key: float(value) for key, value in row.items() if key == "time" or key in OUTPUTS}
                for row in csv.DictReader(stream)]


def compare(reference_dir: Path, graphical_dir: Path, tolerance: float) -> dict[str, object]:
    variants: dict[str, object] = {}
    for algorithm_id in ALGORITHMS:
        reference_path = reference_dir / f"{algorithm_id}.csv"
        graphical_path = graphical_dir / f"{algorithm_id}.csv"
        reference = load_rows(reference_path)
        graphical = load_rows(graphical_path)
        sample_count_ok = len(reference) == len(graphical) and len(reference) > 10
        errors = {name: float("inf") for name in OUTPUTS}
        time_error = float("inf")
        if sample_count_ok:
            time_error = max(abs(a["time"] - b["time"]) for a, b in zip(reference, graphical))
            errors = {name: max(abs(a[name] - b[name]) for a, b in zip(reference, graphical)) for name in OUTPUTS}
        ok = sample_count_ok and time_error <= tolerance and all(value <= tolerance for value in errors.values())
        variants[algorithm_id] = {
            "reference_csv": str(reference_path.resolve()),
            "graphical_csv": str(graphical_path.resolve()),
            "sample_count": len(graphical),
            "sample_count_ok": sample_count_ok,
            "max_abs_time_error": time_error,
            "max_abs_error": errors,
            "behavior_equivalence_ok": ok,
        }
    return {
        "schema": "mosim.pid_six_variant_graphical_equivalence.v1",
        "source_pair": ["MWORKS_CFUNCTION_MIL", "MWORKS_GRAPHICAL_MIL"],
        "tolerance": tolerance,
        "variants": variants,
        "six_variant_graphical_equivalence": all(item["behavior_equivalence_ok"] for item in variants.values()),
        "claim_boundary": (
            "Equivalence covers the six configured 21-sample fixed-input MIL trajectories only; "
            "dynamic reset/enable, ATTITUDE_THRUST, and Gazebo/PX4/MAVROS remain open."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--graphical-dir", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    payload = compare(args.reference_dir, args.graphical_dir, args.tolerance)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["six_variant_graphical_equivalence"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
