#!/usr/bin/env python3
"""Fail closed if G4's 49-scheme current-model map or imports drift."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import (
    CURRENT_MAP_PATH,
    MappingError,
    build_current_map,
    import_plan,
    read_json,
    verify_imported_files,
)


def load_inputs() -> dict[str, Any]:
    current = read_json(CURRENT_MAP_PATH)
    expected = build_current_map(require_imports=False)
    catalog = read_json(Path(expected["source_files"]["control_scheme_catalog"]))
    inventory = read_json(Path(expected["source_files"]["g1_execution_inventory"]))
    return {
        "current": current,
        "expected": expected,
        "import_errors": verify_imported_files(import_plan(catalog, inventory)),
    }


def validate(inputs: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    current = inputs.get("current")
    expected = inputs.get("expected")
    if not isinstance(current, dict) or not isinstance(expected, dict):
        add("CMEM-READ-01", "current and expected current-model maps must be JSON objects")
        return errors
    if current.get("schema") != "mosim.current_model_entry_map.v1":
        add("CMEM-SCHEMA-01", "current model map schema is invalid")
    rows = current.get("schemes")
    if not isinstance(rows, list) or len(rows) != 49:
        add("CMEM-ROWS-01", "current model map must have exactly 49 schemes")
    else:
        ids = [str(row.get("scheme_id")) for row in rows if isinstance(row, dict)]
        if len(ids) != len(set(ids)):
            add("CMEM-ROWS-02", "current model map has duplicate scheme IDs")
        for row in rows:
            if not isinstance(row, dict):
                add("CMEM-ROWS-03", "current model map contains a non-object scheme row")
                continue
            state = row.get("mapping_state")
            scheme_id = str(row.get("scheme_id") or "<missing>")
            if state not in {"resolved_current_model", "blocked_missing_current_model", "not_applicable_runtime_baseline"}:
                add("CMEM-STATE-01", f"{scheme_id}: invalid mapping state: {state}")
            if row.get("mworks_run_eligible") is not False:
                add("CMEM-STATE-02", f"{scheme_id}: G4 mapping cannot enable MWORKS")
            if state == "resolved_current_model" and not str(row.get("current_model_file") or "").startswith("Models/"):
                add("CMEM-STATE-03", f"{scheme_id}: resolved model must be project-owned below Models/")
            if state == "not_applicable_runtime_baseline" and scheme_id != "px4ctrl":
                add("CMEM-STATE-04", "only px4ctrl may use not_applicable_runtime_baseline")
            if scheme_id == "px4ctrl" and state != "not_applicable_runtime_baseline":
                add("CMEM-STATE-05", "px4ctrl must remain the non-graphical runtime baseline")
    if current != expected:
        add("CMEM-DRIFT-01", "current_model_entry_map.json diverges from the deterministic G4 source/hash/package mapping")
    for error in inputs.get("import_errors") or []:
        add("CMEM-IMPORT-01", str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    try:
        inputs = load_inputs()
        errors = validate(inputs)
    except Exception as exc:
        errors = [{"code": "CMEM-READ-02", "message": str(exc)}]
        inputs = {}
    report = {
        "schema": "mosim.current_model_entry_map_check.v1",
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }
    if args.output_json:
        output = args.output_json if args.output_json.is_absolute() else Path.cwd() / args.output_json
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
