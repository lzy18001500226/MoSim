#!/usr/bin/env python3
"""Generate controller event_log.json from a standard raw CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


EVENT_NAMES = {
    10: "NORMAL",
    20: "SAFETY_FILTER_ACTIVE",
    30: "DEGRADED_RETURN",
    40: "EMERGENCY_LAND",
}


def parse_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    try:
        return float(value)
    except ValueError:
        return math.nan


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "time" not in reader.fieldnames:
            raise ValueError(f"CSV must contain a time column: {path}")
        rows: list[dict[str, float]] = []
        for row in reader:
            rows.append({key: parse_float(value) for key, value in row.items()})
        return rows


def rounded_code(value: float, fallback: int) -> int:
    if math.isnan(value) or math.isinf(value):
        return fallback
    return int(round(value))


def build_event_log(rows: list[dict[str, float]], *, scene_id: str, controller_id: str) -> dict[str, object]:
    events: list[dict[str, object]] = []
    previous_mode: int | None = None
    previous_event: int | None = None
    max_safety_active = 0.0

    for row in rows:
        time_s = row.get("time", math.nan)
        mode = rounded_code(row.get("controller_mode", math.nan), 1)
        event_code = rounded_code(row.get("event_code", math.nan), 10)
        safety_active = row.get("safety_active", 0.0)
        if math.isfinite(safety_active):
            max_safety_active = max(max_safety_active, safety_active)

        if previous_mode is None:
            previous_mode = mode
            previous_event = event_code
            events.append(
                {
                    "time_s": time_s,
                    "event": EVENT_NAMES.get(event_code, f"EVENT_{event_code}"),
                    "controller_mode": mode,
                    "event_code": event_code,
                    "reason": "initial_mode",
                }
            )
            continue

        if mode != previous_mode or event_code != previous_event:
            events.append(
                {
                    "time_s": time_s,
                    "event": EVENT_NAMES.get(event_code, f"EVENT_{event_code}"),
                    "controller_mode": mode,
                    "event_code": event_code,
                    "previous_mode": previous_mode,
                    "reason": "mode_or_event_code_changed",
                }
            )
            previous_mode = mode
            previous_event = event_code

    return {
        "scene_id": scene_id,
        "controller_id": controller_id,
        "source": "raw_csv_controller_debug_signals",
        "event_count": len(events),
        "max_safety_active": max_safety_active,
        "events": events,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--scene-id", default="")
    parser.add_argument("--controller-id", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_event_log(
        read_rows(args.raw_csv),
        scene_id=args.scene_id or args.raw_csv.stem,
        controller_id=args.controller_id,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output_json}")
    print(f"Events: {payload['event_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
