#!/usr/bin/env python3
"""Reconcile the fixed 48-entry catalog with historical and current G3 evidence.

The historical G3 matrix and ``G3_STATUS.json`` remain immutable execution
evidence. This script derives a separate current catalog-48 view so
post-freeze FormalRunner records can be accounted for without changing the
48-entry denominator or silently replacing historical G3-only rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
ALIAS_MAP_PATH = ROOT / "Config" / "control_platform" / "scheme_id_alias_map.json"
G3_STATUS_PATH = (
    ROOT / "Results" / "control_platform" / "phase2_full_48_climbpath" / "g3_repair" / "G3_STATUS.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "control_platform"
    / "phase2_full_48_climbpath"
    / "g3_repair"
    / "G3_CATALOG_48_CURRENT_STATUS.json"
)
SCHEMA = "mosim.phase2_full_48_climbpath.g3_catalog_reconciliation.v1"
CATALOG_COUNT = 48
TERMINAL_ERROR_LIMIT_M = 5.0


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def now_cst() -> str:
    offset = timezone(timedelta(hours=8))
    return datetime.now(timezone.utc).astimezone(offset).isoformat(timespec="seconds")


def require_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    return float(value)


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be boolean")
    return value


def index_unique(rows: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError(f"{label} must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{label} contains a non-object row")
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label} row is missing {key}")
        if value in indexed:
            raise ValueError(f"{label} contains duplicate {key}: {value}")
        indexed[value] = row
    return indexed


def historical_row(catalog_scheme: dict[str, Any], g3_controller_id: str, g3_row: dict[str, Any]) -> dict[str, Any]:
    status = g3_row.get("status")
    if status not in {"pass", "fail"}:
        raise ValueError(f"historical G3 row {g3_controller_id} has unsupported status {status!r}")
    return {
        "scheme_id": catalog_scheme["scheme_id"],
        "display_name_zh": catalog_scheme.get("display_name_zh"),
        "category": catalog_scheme.get("category"),
        "status": status,
        "completion_state": "completed",
        "evidence_origin": "historical_g3_execution",
        "historical_g3_controller_id": g3_controller_id,
        "runner_class": g3_row.get("runner_class"),
        "source_record": g3_row.get("effective_run_record"),
        "terminal_position_error_norm_m": g3_row.get("terminal_position_error_norm_m"),
        "position_rmse_m": g3_row.get("position_rmse_m"),
        "failure_class": g3_row.get("failure_class"),
        "failure_reasons": g3_row.get("failure_reasons", []),
    }


def supplemental_row(catalog_scheme: dict[str, Any], definition: dict[str, Any]) -> dict[str, Any]:
    source_value = definition.get("run_record")
    if not isinstance(source_value, str) or not source_value:
        raise ValueError(f"{catalog_scheme['scheme_id']} supplemental evidence has no run_record")
    source_path = ROOT / source_value
    if not source_path.is_file():
        raise ValueError(f"supplemental run record is missing: {source_value}")
    record = read_json(source_path)
    scheme_id = catalog_scheme["scheme_id"]
    if record.get("controller_id") != scheme_id:
        raise ValueError(f"supplemental run record controller_id mismatch for {scheme_id}")

    if "native_simulation" in record:
        model = record.get("model")
        simulation = record.get("native_simulation")
        check_model = record.get("native_check_model")
        if not isinstance(model, dict) or not isinstance(simulation, dict) or not isinstance(check_model, dict):
            raise ValueError(f"{scheme_id} native record is missing model, simulation, or CheckModel details")
        if check_model.get("formal_runner") != "passed":
            raise ValueError(f"{scheme_id} FormalRunner CheckModel did not pass")
        api_ok = require_bool(simulation.get("api_ok"), f"{scheme_id}.native_simulation.api_ok")
        if not api_ok:
            completion = simulation.get("mworks_completion_verification")
            if simulation.get("mcp_call_status") != "timed_out_after_300_s":
                raise ValueError(f"{scheme_id} native simulation API did not succeed")
            if not isinstance(completion, dict):
                raise ValueError(f"{scheme_id} MCP timeout lacks native completion verification")
            if require_number(completion.get("exit_state"), f"{scheme_id}.exit_state") != 0:
                raise ValueError(f"{scheme_id} native completion has nonzero exit state")
            if completion.get("state") != "Idle":
                raise ValueError(f"{scheme_id} native completion is not Idle")
            if abs(require_number(completion.get("sim_time_s"), f"{scheme_id}.sim_time_s") - 50.0) > 1e-9:
                raise ValueError(f"{scheme_id} native completion did not reach 50 s")
            if not require_bool(completion.get("result_readable"), f"{scheme_id}.result_readable"):
                raise ValueError(f"{scheme_id} native completion result is not readable")
        stop_time_s = require_number(simulation.get("completed_to_stop_time_s"), f"{scheme_id}.stop_time_s")
        terminal_error_m = require_number(
            simulation.get("terminal_position_error_norm_m"), f"{scheme_id}.terminal_position_error_norm_m"
        )
        runner_class = model.get("runner_class")
        sample_count = model.get("result_sample_count")
        source_status = record.get("execution_status")
        if api_ok:
            check_model_status = (
                "formal_runner_passed_direct_core_error_retained"
                if check_model.get("equation_core") == "failed_mworks_compiler_internal_error"
                else "formal_runner_passed"
            )
        else:
            check_model_status = "formal_runner_passed_mcp_timeout_native_completion_verified"
    else:
        metrics = record.get("metrics")
        check_model = record.get("check_model")
        simulation = record.get("simulate_model")
        if not isinstance(metrics, dict) or not isinstance(check_model, dict) or not isinstance(simulation, dict):
            raise ValueError(f"{scheme_id} experimental record is missing metrics, simulation, or CheckModel details")
        if not require_bool(check_model.get("passed"), f"{scheme_id}.check_model.passed"):
            raise ValueError(f"{scheme_id} CheckModel did not pass")
        if not require_bool(simulation.get("returned"), f"{scheme_id}.simulate_model.returned"):
            raise ValueError(f"{scheme_id} simulation did not return true")
        stop_time_s = require_number(metrics.get("time_end_s"), f"{scheme_id}.metrics.time_end_s")
        terminal_error_m = require_number(
            metrics.get("terminal_position_error_norm_m"), f"{scheme_id}.metrics.terminal_position_error_norm_m"
        )
        runner_class = record.get("runner_class")
        sample_count = metrics.get("sample_count")
        source_status = record.get("status")
        check_model_status = "passed"

    if abs(stop_time_s - 50.0) > 1e-9:
        raise ValueError(f"{scheme_id} must retain a completed 50 s ClimbPath record")
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count <= 0:
        raise ValueError(f"{scheme_id} sample_count must be a positive integer")

    status = "pass" if terminal_error_m < TERMINAL_ERROR_LIMIT_M else "fail"
    expected_status = definition.get("expected_status")
    if expected_status != status:
        raise ValueError(
            f"{scheme_id} supplemental evidence expected {expected_status!r}, computed {status!r}; update mapping only after review"
        )
    return {
        "scheme_id": scheme_id,
        "display_name_zh": catalog_scheme.get("display_name_zh"),
        "category": catalog_scheme.get("category"),
        "status": status,
        "completion_state": "completed",
        "evidence_origin": "post_freeze_formal_runner_record",
        "historical_g3_controller_id": None,
        "runner_class": runner_class,
        "source_record": repo_path(source_path),
        "source_record_sha256": sha256_file(source_path),
        "source_status": source_status,
        "check_model_status": check_model_status,
        "stop_time_s": stop_time_s,
        "sample_count": sample_count,
        "terminal_position_error_norm_m": terminal_error_m,
        "position_rmse_m": (record.get("metrics") or {}).get("position_rmse_m"),
        "failure_class": None if status == "pass" else "terminal_position_error_exceeds_5m",
        "failure_reasons": []
        if status == "pass"
        else [f"terminal position_error_norm {terminal_error_m:.12g} m is not below {TERMINAL_ERROR_LIMIT_M:g} m"],
        "claim_boundary": definition.get("claim_boundary"),
    }


def current_override_row(
    catalog_scheme: dict[str, Any], definition: dict[str, Any], historical_row_value: dict[str, Any]
) -> dict[str, Any]:
    """Apply a newer, source-bound 50 s record to a historically mapped catalog row."""
    source_value = definition.get("run_record")
    if not isinstance(source_value, str) or not source_value:
        raise ValueError(f"{catalog_scheme['scheme_id']} override evidence has no run_record")
    source_path = ROOT / source_value
    if not source_path.is_file():
        raise ValueError(f"override run record is missing: {source_value}")
    record = read_json(source_path)
    scheme_id = catalog_scheme["scheme_id"]

    expected_model = definition.get("model_name")
    if not isinstance(expected_model, str) or not expected_model:
        raise ValueError(f"{scheme_id} override evidence has no model_name")
    if record.get("model_name") != expected_model:
        raise ValueError(f"{scheme_id} override model_name does not match the declared formal runner")
    if record.get("trajectory") != "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath":
        raise ValueError(f"{scheme_id} override evidence is not a ClimbPath run")

    check_model = record.get("check_model")
    simulation_contract = record.get("simulation_contract")
    native_result = record.get("native_result")
    metrics = record.get("metrics")
    if not all(isinstance(value, dict) for value in (check_model, simulation_contract, native_result, metrics)):
        raise ValueError(f"{scheme_id} override record is missing CheckModel, contract, native result, or metrics")
    if check_model.get("status") != "pass" or not require_bool(check_model.get("data"), f"{scheme_id}.check_model.data"):
        raise ValueError(f"{scheme_id} override CheckModel did not pass")
    if require_number(check_model.get("gui_error_count"), f"{scheme_id}.check_model.gui_error_count") != 0:
        raise ValueError(f"{scheme_id} override CheckModel has GUI errors")
    if abs(require_number(simulation_contract.get("start_time_s"), f"{scheme_id}.start_time_s")) > 1e-9:
        raise ValueError(f"{scheme_id} override must start at 0 s")
    if abs(require_number(simulation_contract.get("stop_time_s"), f"{scheme_id}.stop_time_s") - 50.0) > 1e-9:
        raise ValueError(f"{scheme_id} override must target 50 s")
    for key in ("solver_changed", "parameters_changed", "source_changed"):
        if require_bool(simulation_contract.get(key), f"{scheme_id}.simulation_contract.{key}"):
            raise ValueError(f"{scheme_id} override has forbidden {key}")
    stop_time_s = require_number(native_result.get("time_end_s"), f"{scheme_id}.native_result.time_end_s")
    if abs(stop_time_s - 50.0) > 1e-9:
        raise ValueError(f"{scheme_id} override native result did not reach 50 s")
    sample_count = native_result.get("sample_count")
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count <= 0:
        raise ValueError(f"{scheme_id} override sample_count must be a positive integer")
    if not require_bool(native_result.get("finite_series"), f"{scheme_id}.native_result.finite_series"):
        raise ValueError(f"{scheme_id} override result contains non-finite values")
    terminal_error_m = require_number(metrics.get("terminal_position_error_m"), f"{scheme_id}.terminal_position_error_m")
    position_rmse_m = require_number(metrics.get("position_rmse_m"), f"{scheme_id}.position_rmse_m")
    status = "pass" if terminal_error_m < TERMINAL_ERROR_LIMIT_M else "fail"
    if definition.get("expected_status") != status:
        raise ValueError(f"{scheme_id} override status does not match expected_status")

    return {
        "scheme_id": scheme_id,
        "display_name_zh": catalog_scheme.get("display_name_zh"),
        "category": catalog_scheme.get("category"),
        "status": status,
        "completion_state": "completed",
        "evidence_origin": "post_freeze_current_override_record",
        "historical_g3_controller_id": historical_row_value.get("historical_g3_controller_id"),
        "runner_class": expected_model,
        "source_record": repo_path(source_path),
        "source_record_sha256": sha256_file(source_path),
        "source_status": "completed",
        "check_model_status": "passed",
        "stop_time_s": stop_time_s,
        "sample_count": sample_count,
        "terminal_position_error_norm_m": terminal_error_m,
        "position_rmse_m": position_rmse_m,
        "failure_class": None if status == "pass" else "terminal_position_error_exceeds_5m",
        "failure_reasons": []
        if status == "pass"
        else [f"terminal position_error_norm {terminal_error_m:.12g} m is not below {TERMINAL_ERROR_LIMIT_M:g} m"],
        "supersedes_historical_g3_record": {
            "source_record": historical_row_value.get("source_record"),
            "failure_class": historical_row_value.get("failure_class"),
        },
        "claim_boundary": definition.get("claim_boundary"),
    }


def not_run_row(catalog_scheme: dict[str, Any], definition: dict[str, Any]) -> dict[str, Any]:
    reason = definition.get("reason")
    if not isinstance(reason, str) or not reason:
        raise ValueError(f"{catalog_scheme['scheme_id']} missing-formal-runner row has no reason")
    return {
        "scheme_id": catalog_scheme["scheme_id"],
        "display_name_zh": catalog_scheme.get("display_name_zh"),
        "category": catalog_scheme.get("category"),
        "status": "not_run",
        "completion_state": "not_run",
        "evidence_origin": "catalog_entry_without_formal_runner",
        "historical_g3_controller_id": None,
        "runner_class": None,
        "source_record": None,
        "terminal_position_error_norm_m": None,
        "position_rmse_m": None,
        "failure_class": "formal_runner_missing",
        "failure_reasons": [reason],
    }


def build_status() -> dict[str, Any]:
    catalog = read_json(CATALOG_PATH)
    alias_map = read_json(ALIAS_MAP_PATH)
    historical_g3 = read_json(G3_STATUS_PATH)

    catalog_by_id = index_unique(catalog.get("schemes"), "scheme_id", "catalog schemes")
    g3_by_id = index_unique(historical_g3.get("rows"), "controller_id", "historical G3 rows")
    if len(catalog_by_id) != CATALOG_COUNT or len(g3_by_id) != CATALOG_COUNT:
        raise ValueError("both catalog and frozen G3 status must retain exactly 48 unique rows")

    alias_by_catalog: dict[str, str] = {}
    for row in alias_map.get("aliases", []):
        if not isinstance(row, dict):
            raise ValueError("aliases contains a non-object row")
        catalog_id = row.get("catalog_scheme_id")
        g3_id = row.get("g3_controller_id")
        if not isinstance(catalog_id, str) or not isinstance(g3_id, str):
            raise ValueError("each alias must bind catalog_scheme_id to g3_controller_id")
        if catalog_id in alias_by_catalog:
            raise ValueError(f"duplicate alias for {catalog_id}")
        alias_by_catalog[catalog_id] = g3_id

    supplemental_by_catalog = index_unique(
        alias_map.get("catalog_current_supplemental_evidence"),
        "catalog_scheme_id",
        "catalog_current_supplemental_evidence",
    )
    override_by_catalog = index_unique(
        alias_map.get("catalog_current_override_evidence", []),
        "catalog_scheme_id",
        "catalog_current_override_evidence",
    )
    missing_by_catalog = index_unique(
        alias_map.get("catalog_only_no_runner"), "catalog_scheme_id", "catalog_only_no_runner"
    )
    g3_only_by_id = index_unique(
        alias_map.get("runner_only_no_catalog_entry"), "g3_controller_id", "runner_only_no_catalog_entry"
    )

    rows: list[dict[str, Any]] = []
    mapped_g3_ids: set[str] = set()
    categories = Counter()
    for scheme_id, catalog_scheme in catalog_by_id.items():
        choices = sum(
            (
                scheme_id in g3_by_id,
                scheme_id in alias_by_catalog,
                scheme_id in supplemental_by_catalog,
                scheme_id in missing_by_catalog,
            )
        )
        if choices != 1:
            raise ValueError(f"{scheme_id} must have exactly one current reconciliation route, found {choices}")
        if scheme_id in g3_by_id:
            row = historical_row(catalog_scheme, scheme_id, g3_by_id[scheme_id])
            mapped_g3_ids.add(scheme_id)
            categories["historical_g3_exact"] += 1
        elif scheme_id in alias_by_catalog:
            g3_id = alias_by_catalog[scheme_id]
            if g3_id not in g3_by_id:
                raise ValueError(f"alias target is absent from frozen G3 status: {g3_id}")
            row = historical_row(catalog_scheme, g3_id, g3_by_id[g3_id])
            mapped_g3_ids.add(g3_id)
            categories["historical_g3_alias"] += 1
        elif scheme_id in supplemental_by_catalog:
            row = supplemental_row(catalog_scheme, supplemental_by_catalog[scheme_id])
            categories["supplemental_current_record"] += 1
        else:
            row = not_run_row(catalog_scheme, missing_by_catalog[scheme_id])
            categories["formal_runner_missing"] += 1
        if scheme_id in override_by_catalog:
            if row.get("evidence_origin") != "historical_g3_execution":
                raise ValueError(f"{scheme_id} override must replace a historical G3-mapped current row")
            row = current_override_row(catalog_scheme, override_by_catalog[scheme_id], row)
            categories["post_freeze_current_override_record"] += 1
        rows.append(row)

    g3_only_ids = set(g3_by_id) - mapped_g3_ids
    if g3_only_ids != set(g3_only_by_id):
        raise ValueError(
            "runner_only_no_catalog_entry must exactly describe frozen G3 rows outside the current catalog: "
            f"expected={sorted(g3_only_ids)}, declared={sorted(g3_only_by_id)}"
        )
    historical_g3_only_rows = [
        {
            "historical_g3_controller_id": controller_id,
            "status": g3_by_id[controller_id].get("status"),
            "runner_class": g3_by_id[controller_id].get("runner_class"),
            "source_record": g3_by_id[controller_id].get("effective_run_record"),
            "claim_boundary": "Preserved historical G3 execution evidence; not counted in the current catalog-48 denominator.",
        }
        for controller_id in sorted(g3_only_ids)
    ]
    status_counts = Counter(row["status"] for row in rows)
    if set(status_counts) - {"pass", "fail", "not_run"}:
        raise ValueError(f"unsupported reconciled status values: {sorted(status_counts)}")
    completed = status_counts["pass"] == CATALOG_COUNT

    return {
        "schema": SCHEMA,
        "generated_at": now_cst(),
        "authority": (
            "Current status for the fixed 48-entry catalog. Historical G3_STATUS.json remains immutable "
            "execution evidence and is not overwritten by this reconciliation."
        ),
        "scope": "Nominal 50 s ClimbPath evidence only. No scenario, tuning, deployment, ROS, Gazebo, or runtime claim.",
        "source_files": {
            "control_scheme_catalog": {"path": repo_path(CATALOG_PATH), "sha256": sha256_file(CATALOG_PATH)},
            "scheme_id_alias_map": {"path": repo_path(ALIAS_MAP_PATH), "sha256": sha256_file(ALIAS_MAP_PATH)},
            "historical_g3_status": {"path": repo_path(G3_STATUS_PATH), "sha256": sha256_file(G3_STATUS_PATH)},
        },
        "summary": {
            "catalog_entry_count": len(rows),
            "historical_g3_execution_row_count": len(g3_by_id),
            "historical_g3_exact_count": categories["historical_g3_exact"],
            "historical_g3_alias_count": categories["historical_g3_alias"],
            "historical_g3_mapped_catalog_count": len(mapped_g3_ids),
            "supplemental_current_record_count": categories["supplemental_current_record"],
            "post_freeze_current_override_record_count": categories["post_freeze_current_override_record"],
            "formal_runner_missing_count": categories["formal_runner_missing"],
            "historical_g3_only_count": len(historical_g3_only_rows),
            "passed_count": status_counts["pass"],
            "failed_count": status_counts["fail"],
            "not_run_count": status_counts["not_run"],
            "inventory_reconciled": True,
            "completed": completed,
        },
        "rows": rows,
        "historical_g3_only_rows": historical_g3_only_rows,
        "unresolved_catalog_entries": [row["scheme_id"] for row in rows if row["status"] == "not_run"],
        "claim_boundary": (
            "This artifact reconciles evidence identities and statuses for the existing 48-entry catalog. "
            "It does not change the frozen historical G3 matrix, constitute a G3 retry, or claim 48/48 acceptance."
        ),
    }


def validate_status(status: dict[str, Any]) -> None:
    if status.get("schema") != SCHEMA:
        raise ValueError(f"unexpected schema: {status.get('schema')!r}")
    rows_by_id = index_unique(status.get("rows"), "scheme_id", "reconciled rows")
    if len(rows_by_id) != CATALOG_COUNT:
        raise ValueError("reconciled status must retain exactly 48 unique catalog rows")
    status_counts = Counter(row.get("status") for row in rows_by_id.values())
    if set(status_counts) - {"pass", "fail", "not_run"}:
        raise ValueError("reconciled rows contain an unsupported status")
    summary = status.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("summary must be an object")
    expected = {
        "catalog_entry_count": CATALOG_COUNT,
        "passed_count": status_counts["pass"],
        "failed_count": status_counts["fail"],
        "not_run_count": status_counts["not_run"],
        "completed": status_counts["pass"] == CATALOG_COUNT,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ValueError(f"summary {key} is stale: expected {value!r}, got {summary.get(key)!r}")
    if summary.get("historical_g3_mapped_catalog_count") != 41:
        raise ValueError("historical G3 mapping must account for 41 catalog entries")
    if summary.get("supplemental_current_record_count") != 7:
        raise ValueError("supplemental current evidence must account for exactly seven catalog entries")
    if summary.get("post_freeze_current_override_record_count") != 2:
        raise ValueError("two post-freeze current override records must be retained")
    if summary.get("formal_runner_missing_count") != 0:
        raise ValueError("no catalog entry may remain without a FormalRunner")
    if summary.get("historical_g3_only_count") != 7:
        raise ValueError("seven historical G3-only rows must remain preserved")
    if not summary.get("inventory_reconciled"):
        raise ValueError("inventory_reconciled must be true")


def canonical_for_compare(status: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(status)
    value.pop("generated_at", None)
    return value


def output_path(value: Path) -> Path:
    return value if value.is_absolute() else ROOT / value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Derived status JSON path.")
    parser.add_argument("--check", action="store_true", help="Validate the existing output against current inputs without writing.")
    args = parser.parse_args()
    path = output_path(args.output)
    expected = build_status()
    validate_status(expected)
    if args.check:
        actual = read_json(path)
        validate_status(actual)
        if canonical_for_compare(actual) != canonical_for_compare(expected):
            raise ValueError(f"{repo_path(path)} is stale; regenerate it from current inputs")
        result = {"ok": True, "mode": "check", "output": repo_path(path), "summary": actual["summary"]}
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = {"ok": True, "mode": "write", "output": repo_path(path), "summary": expected["summary"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
