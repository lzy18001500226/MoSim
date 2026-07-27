#!/usr/bin/env python3
"""Build the deterministic G4 current-model entry map for 48 active profiles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import CURRENT_MAP_PATH, build_current_map, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CURRENT_MAP_PATH)
    parser.add_argument("--check", action="store_true", help="Compare the existing map with the deterministic current mapping.")
    args = parser.parse_args()
    try:
        value = build_current_map(require_imports=True)
        output = args.output if args.output.is_absolute() else Path.cwd() / args.output
        if args.check:
            if not output.is_file():
                raise ValueError(f"Missing current model map: {output}")
            existing = json.loads(output.read_text(encoding="utf-8"))
            if existing != value:
                raise ValueError(f"Current model map is stale or diverged: {output}")
        else:
            write_json(output, value)
        report = {"ok": True, "output": str(output), "summary": value["summary"], "check": args.check}
    except Exception as exc:
        report = {"ok": False, "error": str(exc), "check": args.check}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
