#!/usr/bin/env python3
"""Summarize the P6 safety runtime provenance matrix without inflating claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MODES = (
    "safety_filter",
    "cbf",
    "reference_governor",
    "geofence",
    "emergency_stop",
    "return_and_land",
    "failsafe_state_machine",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    errors = []
    for mode in MODES:
        path = args.result_root / mode / "SAFETY_GENERATED_RUNTIME_PROVENANCE.json"
        if not path.is_file():
            errors.append(f"missing provenance: {path}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        row = {
            "mode": mode,
            "status": payload.get("status"),
            "expected_action": payload.get("expected_action"),
            "event_state": payload.get("event_state"),
            "active_constraints": payload.get("active_constraints"),
            "safe_thrust": payload.get("safe_thrust"),
            "runtime_loaded_symbol": payload.get("runtime_loaded_symbol"),
            "binary_generated_symbol_present": payload.get(
                "binary_generated_symbol_present"
            ),
            "event_acknowledged": payload.get("event_acknowledged"),
            "provenance_path": str(path),
        }
        rows.append(row)
        if payload.get("status") != "passed":
            errors.append(f"{mode}: provenance status is not passed")
        if not payload.get("event_acknowledged"):
            errors.append(f"{mode}: expected safety event was not acknowledged")
        if not payload.get("binary_generated_symbol_present"):
            errors.append(f"{mode}: generated symbol is absent from px4ctrl binary")

    output = {
        "schema": "mosim.p6_safety_runtime_matrix.v1",
        "status": "passed" if len(rows) == len(MODES) and not errors else "blocked",
        "claim_boundary": (
            "Generated SafetySupervisor code was loaded and the expected event "
            "was acknowledged in the ROS1 Gazebo/PX4/MAVROS/px4ctrl runtime. "
            "This matrix does not claim ordinary takeoff-hover-land success for "
            "deliberate STOP, HOLD, or RETURN scenarios."
        ),
        "mode_count": len(rows),
        "expected_mode_count": len(MODES),
        "modes": rows,
        "errors": errors,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(output, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(args.json_out)
    return 0 if output["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
