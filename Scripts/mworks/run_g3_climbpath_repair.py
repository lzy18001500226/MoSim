#!/usr/bin/env python3
"""Run bounded G3 repairs without overwriting the frozen G2 evidence.

G2 remains the immutable 48-route screening record.  This driver reuses the
single-route MWORKS execution path from ``run_phase2_full_48_climbpath.py``
but writes every retry below ``phase2_full_48_climbpath/g3_repair``.  Each G3
record binds the original failed G2 record and hashes the current runner,
adapter, bridge, allocator, plant, and other directly reachable Modelica
sources.  Repeated G3 attempts are archived inside the G3 route only.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import time
from pathlib import Path
from typing import Any

import run_phase2_full_48_climbpath as phase2


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
G2_ROOT = ROOT / "Results" / "control_platform" / "phase2_full_48_climbpath"
G3_ROOT = G2_ROOT / "g3_repair"
G2_MATRIX_PATH = G2_ROOT / "G2_MATRIX.json"
G2_STATUS_PATH = G2_ROOT / "G2_STATUS.json"
G3_MATRIX_PATH = G3_ROOT / "G3_MATRIX.json"
G3_STATUS_PATH = G3_ROOT / "G3_STATUS.json"
G3_CONTRACT_PATH = G3_ROOT / "G3_EXECUTION_CONTRACT.json"

EXPECTED_G2_MATRIX_SHA256 = "a9f85d8cb8b4b942b88056bf4eb336ba17a9c40b26fe1ae5d21ab12649599d80"
G3_MATRIX_SCHEMA = "mosim.phase2_full_48_climbpath_g3_matrix.v1"
G3_STATUS_SCHEMA = "mosim.phase2_full_48_climbpath_g3_status.v1"
G3_RUN_SCHEMA = "mosim.phase2_full_48_climbpath_g3_run.v1"
G3_ROUTE_STATUS_SCHEMA = "mosim.phase2_full_48_climbpath_g3_route_status.v1"

MODEL_CLASS_RE = re.compile(r"MoSimQuadrotorModel(?:\.[A-Za-z_][A-Za-z0-9_]*)+")
ROUTE_IDENTITY_KEYS = ("controller_id", "runner_id", "runner_class", "runner_file", "adapter_class")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError as exc:
        raise ValueError(f"path leaves project root: {path}") from exc


def sha256(path: Path) -> str:
    return phase2.sha256(path)


def source_entry(path: Path, role: str) -> dict[str, str]:
    return {"role": role, "path": relative(path), "sha256": sha256(path)}


def class_path(class_name: str) -> Path | None:
    parts = class_name.split(".")
    if not parts or parts[0] != "MoSimQuadrotorModel":
        return None
    candidate = MODEL_ROOT.joinpath(*parts[1:]).with_suffix(".mo")
    return candidate if candidate.is_file() else None


def current_source_bindings(row: dict[str, Any]) -> list[dict[str, str]]:
    """Capture the local Modelica dependency slice relevant to one G3 retry."""

    roots = [
        (ROOT / str(row["runner_file"]), "formal_runner"),
        (MODEL_ROOT / "package.mo", "package_root"),
        (MODEL_ROOT / "Vehicle" / "Sunray150Assembly.mo", "shared_plant"),
        (MODEL_ROOT / "Guidance" / "Trajectories" / "package.mo", "trajectory"),
    ]
    seen: set[Path] = set()
    bindings: list[dict[str, str]] = []

    def visit(path: Path, role: str, depth: int) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        if not resolved.is_file():
            raise FileNotFoundError(f"G3 source dependency is absent: {resolved}")
        try:
            resolved.relative_to(MODEL_ROOT.resolve())
        except ValueError:
            if resolved != (ROOT / str(row["runner_file"])).resolve():
                raise ValueError(f"G3 source dependency leaves model root: {resolved}")
        seen.add(resolved)
        bindings.append(source_entry(resolved, role))
        if depth <= 0:
            return
        text = resolved.read_text(encoding="utf-8")
        for match in sorted(set(MODEL_CLASS_RE.findall(text))):
            dependency = class_path(match)
            if dependency is not None:
                visit(dependency, "transitive_model_dependency", depth - 1)

    for root, role in roots:
        visit(root, role, 5)
    return sorted(bindings, key=lambda item: item["path"])


def g2_matrix() -> dict[str, Any]:
    if not G2_MATRIX_PATH.is_file():
        raise FileNotFoundError(f"frozen G2 matrix is absent: {G2_MATRIX_PATH}")
    actual = sha256(G2_MATRIX_PATH)
    if actual != EXPECTED_G2_MATRIX_SHA256:
        raise RuntimeError(
            "frozen G2 matrix hash differs from the authorized baseline: "
            f"{actual} != {EXPECTED_G2_MATRIX_SHA256}"
        )
    matrix = read_json(G2_MATRIX_PATH)
    rows = matrix.get("rows")
    if not isinstance(rows, list) or len(rows) != 48:
        raise RuntimeError("frozen G2 matrix must contain exactly 48 rows")
    return matrix


def g2_record(row: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    path = G2_ROOT / str(row["controller_id"]) / "RUN_RECORD.json"
    if not path.is_file():
        raise FileNotFoundError(f"G2 run record is absent: {relative(path)}")
    record = read_json(path)
    if record.get("controller_id") != row["controller_id"]:
        raise RuntimeError(f"G2 run record controller mismatch: {relative(path)}")
    if record.get("status") not in {"pass", "fail"}:
        raise RuntimeError(f"G2 run record is not terminal: {relative(path)}")
    return path, record


def current_routes_by_id() -> dict[str, dict[str, Any]]:
    current = phase2.build_matrix()
    rows = current.get("rows")
    if not isinstance(rows, list) or len(rows) != 48:
        raise RuntimeError("current Formal runner catalog must contain exactly 48 entries")
    return {str(row["controller_id"]): row for row in rows}


def build_g3_matrix() -> dict[str, Any]:
    baseline = g2_matrix()
    current = current_routes_by_id()
    rows: list[dict[str, Any]] = []
    for frozen in baseline["rows"]:
        controller_id = str(frozen["controller_id"])
        candidate = current.get(controller_id)
        if candidate is None:
            raise RuntimeError(f"G3 route is missing from current public catalog: {controller_id}")
        for key in ROUTE_IDENTITY_KEYS:
            if frozen.get(key) != candidate.get(key):
                raise RuntimeError(
                    f"G3 route identity drift for {controller_id} at {key}: "
                    f"{candidate.get(key)!r} != {frozen.get(key)!r}"
                )
        original_path, original = g2_record(frozen)
        rows.append(
            {
                **{key: frozen.get(key) for key in ROUTE_IDENTITY_KEYS},
                "g2_source_bindings": frozen.get("source_bindings", []),
                "g2_run_record": relative(original_path),
                "g2_status": original.get("status"),
                "g2_failure_class": original.get("failure_class"),
                "g2_failure_reasons": original.get("failure_reasons", []),
            }
        )
    return {
        "schema": G3_MATRIX_SCHEMA,
        "generated_at": phase2.now_iso(),
        "g2_matrix": {"path": relative(G2_MATRIX_PATH), "sha256": sha256(G2_MATRIX_PATH)},
        "g2_status_snapshot": {"path": relative(G2_STATUS_PATH), "sha256": sha256(G2_STATUS_PATH)} if G2_STATUS_PATH.is_file() else None,
        "scope": {
            "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
            "duration_s": phase2.STOP_TIME_S,
            "scenario_injection": "none",
            "pass_condition": f"terminal position_error_norm < {phase2.TERMINAL_ERROR_LIMIT_M:g} m with a completed 50 s result",
            "allowed_changes": "Only source fixes for verified interfaces, coordinate signs, equation bridges, allocators, and MWORKS execution-chain faults; no gain-performance optimization.",
            "evidence_root": relative(G3_ROOT),
        },
        "rows": rows,
    }


def stable_g3_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in matrix.items() if key not in {"generated_at", "g2_status_snapshot"}}


def freeze_g3_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    if G3_MATRIX_PATH.is_file():
        existing = read_json(G3_MATRIX_PATH)
        if stable_g3_matrix(existing) != stable_g3_matrix(matrix):
            raise RuntimeError("G3 route identity differs from the frozen G3 repair matrix")
        return existing
    write_json(G3_MATRIX_PATH, matrix)
    return matrix


def g3_run_dir(row: dict[str, Any]) -> Path:
    return G3_ROOT / str(row["controller_id"])


def g3_record(row: dict[str, Any]) -> tuple[Path, dict[str, Any]] | None:
    path = g3_run_dir(row) / "RUN_RECORD.json"
    if not path.is_file():
        return None
    try:
        record = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if record.get("schema") != G3_RUN_SCHEMA or record.get("status") not in {"pass", "fail"}:
        return None
    return path, record


def archive_g3_attempt(run_dir: Path) -> str | None:
    existing = phase2.existing_terminal_record(run_dir)
    if existing is None:
        return None
    archive = run_dir / "superseded" / time.strftime("%Y%m%d_%H%M%S")
    archive.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    names = [
        "RUN_RECORD.json", "G3_ROUTE_STATUS.json", "G3_RUN_CONTEXT.json", "RUN_CONFIG.json",
        "logs", "raw", "metrics", "screenshots",
    ]
    names.extend(path.name for path in run_dir.glob("native_result*"))
    for name in dict.fromkeys(names):
        source = run_dir / name
        if not source.exists():
            continue
        destination = archive / name
        if source.is_file():
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination)
        copied.append(relative(destination))
    write_json(
        archive / "ARCHIVE_MANIFEST.json",
        {
            "schema": "mosim.phase2_full_48_climbpath_g3_superseded_attempt.v1",
            "archived_at": phase2.now_iso(),
            "source_run_dir": relative(run_dir),
            "copied": copied,
        },
    )
    for name in names:
        source = run_dir / name
        if source.is_file():
            source.unlink()
        elif source.is_dir():
            shutil.rmtree(source)
    return relative(archive)


def archive_incomplete_g3_attempt(run_dir: Path) -> str | None:
    """Preserve an interrupted retry before its directory is reused."""

    if phase2.existing_terminal_record(run_dir) is not None or not run_dir.is_dir():
        return None
    names = [
        "RUN_RECORD.json", "G3_ROUTE_STATUS.json", "G3_RUN_CONTEXT.json", "RUN_CONFIG.json",
        "OPERATOR_STOP_RECORD.json", "logs", "raw", "metrics", "screenshots",
    ]
    names.extend(path.name for path in run_dir.glob("native_result*"))
    sources = [run_dir / name for name in dict.fromkeys(names) if (run_dir / name).exists()]
    if not sources:
        return None
    archive = run_dir / "interrupted" / time.strftime("%Y%m%d_%H%M%S")
    archive.mkdir(parents=True, exist_ok=False)
    moved: list[str] = []
    for source in sources:
        destination = archive / source.name
        shutil.move(str(source), str(destination))
        moved.append(relative(destination))
    write_json(
        archive / "ARCHIVE_MANIFEST.json",
        {
            "schema": "mosim.phase2_full_48_climbpath_g3_interrupted_attempt.v1",
            "archived_at": phase2.now_iso(),
            "source_run_dir": relative(run_dir),
            "moved": moved,
        },
    )
    return relative(archive)


def write_g3_route_status(record: dict[str, Any], run_dir: Path) -> None:
    write_json(
        run_dir / "G3_ROUTE_STATUS.json",
        {
            "schema": G3_ROUTE_STATUS_SCHEMA,
            "generated_at": phase2.now_iso(),
            "controller_id": record["controller_id"],
            "runner_class": record["runner_class"],
            "status": record["status"],
            "failure_class": record.get("failure_class"),
            "position_rmse_m": record.get("position_rmse_m"),
            "terminal_position_error_norm_m": record.get("terminal_position_error_norm_m"),
            "run_record": relative(run_dir / "RUN_RECORD.json"),
        },
    )


def configure_phase2_execution() -> None:
    """Retarget the proven single-route executor to the G3-owned evidence tree."""

    phase2.RESULT_ROOT = G3_ROOT
    phase2.MATRIX_PATH = G3_MATRIX_PATH
    phase2.STATUS_PATH = G3_STATUS_PATH
    phase2.CONTRACT_PATH = G3_CONTRACT_PATH
    phase2.SCHEMA = G3_RUN_SCHEMA
    phase2.MATRIX_SCHEMA = G3_MATRIX_SCHEMA
    phase2.STATUS_SCHEMA = G3_STATUS_SCHEMA
    phase2.archive_existing_record = archive_g3_attempt
    phase2.write_route_status = write_g3_route_status


def write_contract(matrix: dict[str, Any]) -> None:
    write_json(
        G3_CONTRACT_PATH,
        {
            "schema": "mosim.phase2_full_48_climbpath_g3_contract.v1",
            "generated_at": phase2.now_iso(),
            "g2_matrix": matrix["g2_matrix"],
            "g3_matrix": {"path": relative(G3_MATRIX_PATH), "sha256": sha256(G3_MATRIX_PATH)},
            "scope": matrix["scope"],
            "acceptance": {
                "all_48_effective_records_required": True,
                "terminal_position_error_limit_m": phase2.TERMINAL_ERROR_LIMIT_M,
                "no_seven_scenario_runs": True,
                "no_gain_performance_optimization": True,
                "g2_evidence_mutation": "forbidden",
                "g3_attempt_archiving": "required before rerun",
            },
        },
    )


def write_status(matrix: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    failure_counts: dict[str, int] = {}
    g3_attempt_count = 0
    for row in matrix["rows"]:
        baseline_path, baseline = g2_record(row)
        repaired = g3_record(row)
        if repaired is None:
            effective_path, effective = baseline_path, baseline
            source = "g2_frozen"
        else:
            effective_path, effective = repaired
            source = "g3_latest"
            g3_attempt_count += 1
        status = str(effective.get("status"))
        failure = effective.get("failure_class") if status == "fail" else None
        if failure:
            key = str(failure)
            failure_counts[key] = failure_counts.get(key, 0) + 1
        rows.append(
            {
                "controller_id": row["controller_id"],
                "runner_class": row["runner_class"],
                "effective_source": source,
                "effective_run_record": relative(effective_path),
                "status": status,
                "position_rmse_m": effective.get("position_rmse_m"),
                "terminal_position_error_norm_m": effective.get("terminal_position_error_norm_m"),
                "failure_class": failure,
                "failure_reasons": effective.get("failure_reasons", []),
                "g2_run_record": row["g2_run_record"],
                "g2_status": row["g2_status"],
                "g3_attempted": repaired is not None,
            }
        )
    passed_count = sum(row["status"] == "pass" for row in rows)
    return {
        "schema": G3_STATUS_SCHEMA,
        "generated_at": phase2.now_iso(),
        "g2_matrix": matrix["g2_matrix"],
        "g3_matrix": {"path": relative(G3_MATRIX_PATH), "sha256": sha256(G3_MATRIX_PATH)},
        "runner_count": len(rows),
        "g2_baseline_passed_count": sum(row["g2_status"] == "pass" for row in matrix["rows"]),
        "g2_baseline_failed_count": sum(row["g2_status"] == "fail" for row in matrix["rows"]),
        "g3_attempt_count": g3_attempt_count,
        "effective_passed_count": passed_count,
        "effective_failed_count": len(rows) - passed_count,
        "effective_failure_counts": failure_counts,
        "completed": passed_count == len(rows),
        "rows": rows,
    }


def selected_rows(matrix: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    by_id = {str(row["controller_id"]): row for row in matrix["rows"]}
    by_runner = {str(row["runner_id"]): row for row in matrix["rows"]}
    if args.only:
        requested = {item.strip() for item in args.only.split(",") if item.strip()}
        unknown = requested - set(by_id) - set(by_runner)
        if unknown:
            raise ValueError(f"unknown G3 route selector(s): {sorted(unknown)}")
        return [row for row in matrix["rows"] if row["controller_id"] in requested or row["runner_id"] in requested]
    if args.all:
        return list(matrix["rows"])
    return [row for row in matrix["rows"] if row["g2_status"] == "fail"]


def run_row(row: dict[str, Any], matrix_hash: str, args: argparse.Namespace) -> None:
    run_dir = g3_run_dir(row)
    if not args.rerun and g3_record(row) is not None:
        return
    incomplete_archive = archive_incomplete_g3_attempt(run_dir)
    execution_row = dict(row)
    execution_row["source_bindings"] = current_source_bindings(row)
    original_path, original = g2_record(row)
    context = {
        "schema": "mosim.phase2_full_48_climbpath_g3_run_context.v1",
        "generated_at": phase2.now_iso(),
        "controller_id": row["controller_id"],
        "repair_note": args.repair_note,
        "g2_run_record": relative(original_path),
        "g2_status": original.get("status"),
        "g2_failure_class": original.get("failure_class"),
        "g2_failure_reasons": original.get("failure_reasons", []),
        "g2_matrix": {"path": relative(G2_MATRIX_PATH), "sha256": sha256(G2_MATRIX_PATH)},
        "g3_matrix": {"path": relative(G3_MATRIX_PATH), "sha256": matrix_hash},
        "current_source_bindings": execution_row["source_bindings"],
    }
    if incomplete_archive:
        context["supersedes_incomplete_attempt"] = incomplete_archive
    write_json(run_dir / "G3_RUN_CONTEXT.json", context)
    phase2.run_route(execution_row, matrix_hash, rerun=args.rerun, wrapper=args.wrapper)
    record_path = run_dir / "RUN_RECORD.json"
    record = read_json(record_path)
    record["schema"] = G3_RUN_SCHEMA
    record["claim_boundary"] = (
        "G3 nominal MWORKS whole-aircraft ClimbPath repair verification only; not gain-performance optimization, "
        "seven-scenario work, code generation, Gazebo, PX4, ROS, or flight-runtime evidence."
    )
    record["controller_execution_boundary"] = (
        "native_continuous_boundary"
        if row["controller_id"] == "official_pid"
        else "unified_100hz_discrete_boundary"
    )
    record["g3_repair"] = {
        "repair_note": args.repair_note,
        "g2_run_record": relative(original_path),
        "g2_status": original.get("status"),
        "g2_failure_class": original.get("failure_class"),
        "g2_failure_reasons": original.get("failure_reasons", []),
        "g2_matrix": {"path": relative(G2_MATRIX_PATH), "sha256": sha256(G2_MATRIX_PATH)},
        "g3_matrix": {"path": relative(G3_MATRIX_PATH), "sha256": matrix_hash},
        "current_source_bindings": execution_row["source_bindings"],
    }
    if incomplete_archive:
        record["g3_repair"]["supersedes_incomplete_attempt"] = incomplete_archive
    if record.get("failure_class") == "other" and any(
        "Timeout waiting for MCP method tools/call" in str(reason)
        for reason in record.get("failure_reasons", [])
    ):
        record["failure_class"] = "simulation_timeout"
    write_json(record_path, record)
    write_g3_route_status(record, run_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="comma-separated controller IDs or FormalRunner IDs")
    parser.add_argument("--all", action="store_true", help="include the original G2 pass routes for an impact regression")
    parser.add_argument("--rerun", action="store_true", help="archive and rerun an existing G3 terminal record")
    parser.add_argument("--plan-only", action="store_true", help="validate/freeze the G3 repair contract without MWORKS")
    parser.add_argument("--repair-note", default="", help="concise diagnosis or repair note recorded with this attempt")
    parser.add_argument("--wrapper", help="optional explicit project-local Sysplorer MCP wrapper")
    parser.add_argument(
        "--simulation-timeout-s",
        type=float,
        default=120.0,
        help="bounded wall-clock limit for one nominal 50 s MWORKS simulation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.simulation_timeout_s <= 0:
        raise ValueError("--simulation-timeout-s must be positive")
    G3_ROOT.mkdir(parents=True, exist_ok=True)
    matrix = freeze_g3_matrix(build_g3_matrix())
    write_contract(matrix)
    selected = selected_rows(matrix, args)
    if args.plan_only:
        status = write_status(matrix)
        write_json(G3_STATUS_PATH, status)
        print(json.dumps({"planned_runner_count": len(selected), "status": status}, ensure_ascii=False, indent=2))
        return 0

    configure_phase2_execution()
    phase2.SIMULATION_TIMEOUT_S = args.simulation_timeout_s
    matrix_hash = sha256(G3_MATRIX_PATH)
    for row in selected:
        run_row(row, matrix_hash, args)
        status = write_status(matrix)
        write_json(G3_STATUS_PATH, status)
    status = write_status(matrix)
    write_json(G3_STATUS_PATH, status)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
