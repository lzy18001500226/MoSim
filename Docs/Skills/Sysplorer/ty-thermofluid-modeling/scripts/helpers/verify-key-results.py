"""Validate key result variables against simple thresholds.

Expected JSON structure:
{
  "validations": [
    {
      "name": "outletTemperature",
      "value": 315.2,
      "min": 300.0,
      "max": 330.0,
      "unit": "K"
    }
  ]
}

If `passed` is provided, it takes priority. Otherwise the script evaluates
`value` against optional `min` / `max` bounds.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def evaluate(item: dict) -> tuple[bool, str]:
    name = str(item.get("name", "unnamed"))
    if "passed" in item:
        passed = bool(item["passed"])
        message = str(item.get("message", "passed" if passed else "validation failed"))
        return passed, f"{name}: {message}"

    value = item.get("value")
    minimum = item.get("min")
    maximum = item.get("max")
    unit = str(item.get("unit", "")).strip()

    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return False, f"{name}: invalid numeric value"
    if isinstance(minimum, (int, float)) and value < minimum:
        return False, f"{name}: {value} {unit}".strip() + f" < min {minimum}"
    if isinstance(maximum, (int, float)) and value > maximum:
        return False, f"{name}: {value} {unit}".strip() + f" > max {maximum}"
    return True, f"{name}: {value} {unit}".strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python verify-key-results.py <results.json>")
        return 1

    result_path = Path(sys.argv[1])
    if not result_path.exists():
        print(f"Results file not found: {result_path}")
        return 1

    data = json.loads(result_path.read_text(encoding="utf-8"))
    validations = data.get("validations", [])
    if not isinstance(validations, list):
        print("FAILED")
        print("validations must be a list")
        return 1

    results = [evaluate(item) for item in validations if isinstance(item, dict)]
    failed = [message for passed, message in results if not passed]

    if failed:
        print("FAILED")
        for message in failed:
            print(message)
        return 1

    print("PASSED")
    for _, message in results:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
