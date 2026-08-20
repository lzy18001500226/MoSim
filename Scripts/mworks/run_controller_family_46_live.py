#!/usr/bin/env python3
"""Run the 46 non-baseline graphical controller runners through Sysplorer MCP.

This task-local runner keeps structural, diagram, simulation, and result
evidence separate. It uses one reusable Sysplorer MCP process, writes progress
after every controller, and never treats a readable result after a reported
simulation failure as a simulation pass.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import tomllib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

try:
    import run_sysplorer_mcp_smoke as mcp_helpers
except ImportError:  # pragma: no cover
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    import run_sysplorer_mcp_smoke as mcp_helpers  # type: ignore


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
ROUTES_PATH = ROOT / "Config" / "control_platform" / "model_studio_task_routes_v1.toml"
PACKAGE_PATH = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
BASELINE_IDS = {"official_pid", "px4ctrl"}
STOP_TIME_S = 50.0
POSITION_ERROR_LIMIT_M = 5.0


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_targets() -> list[dict[str, str]]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    routes_doc = tomllib.loads(ROUTES_PATH.read_text(encoding="utf-8"))
    routes = {str(row["controller_id"]): row for row in routes_doc.get("route", [])}
    targets: list[dict[str, str]] = []
    for row in sorted(catalog["schemes"], key=lambda item: str(item["scheme_id"])):
        scheme_id = str(row["scheme_id"])
        if scheme_id in BASELINE_IDS:
            continue
        route = routes.get(scheme_id)
        if not route or not bool(route.get("available")):
            raise RuntimeError(f"Missing available task route for {scheme_id}")
        targets.append(
            {
                "scheme_id": scheme_id,
                "runner_class": str(route["runner_class"]),
                "runner_file": str(route["runner_file"]),
            }
        )
    if len(targets) != 46:
        raise RuntimeError(f"Expected 46 non-baseline routes, found {len(targets)}")
    return targets


def finite_series(values: list[float]) -> bool:
    return bool(values) and all(math.isfinite(float(value)) for value in values)


def write_diagnostics_csv(path: Path, time_values: list[float], error_values: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["time", "position_error_norm"])
        for time_value, error_value in zip(time_values, error_values):
            writer.writerow([time_value, error_value])


def diagnostics_metrics(
    scheme_id: str,
    runner_class: str,
    time_values: list[float],
    error_values: list[float],
) -> dict[str, Any]:
    finite = finite_series(time_values) and finite_series(error_values)
    same_length = len(time_values) == len(error_values)
    end_time = float(time_values[-1]) if time_values else None
    terminal_error = float(error_values[-1]) if error_values else None
    rmse = (
        math.sqrt(sum(float(value) ** 2 for value in error_values) / len(error_values))
        if error_values and finite_series(error_values)
        else None
    )
    return {
        "schema": "mosim.controller_46_live_diagnostics.v1",
        "generated_at": now_iso(),
        "source": "MWORKS_MCP",
        "evidence_level": "real_sysplorer_mcp_controller_46_50s",
        "claim_role": "single_scenario_50s_dynamics_smoke",
        "scheme_id": scheme_id,
        "runner_class": runner_class,
        "scenario": "scenario_mode=0",
        "requested_stop_time_s": STOP_TIME_S,
        "sample_count": len(time_values),
        "time_start_s": float(time_values[0]) if time_values else None,
        "time_end_s": end_time,
        "terminal_position_error_m": terminal_error,
        "position_error_norm_rmse_m": rmse,
        "finite": finite,
        "same_length": same_length,
        "completion_gates": {
            "more_than_ten_samples": len(time_values) > 10,
            "time_reaches_50s": end_time is not None and abs(end_time - STOP_TIME_S) <= 0.02,
            "finite_core_series": finite and same_length,
            "terminal_position_error_lt_5m": terminal_error is not None and terminal_error < POSITION_ERROR_LIMIT_M,
        },
    }


def run_one(
    client: mcp_helpers.JsonlMcpClient,
    target: dict[str, str],
    output_dir: Path,
) -> dict[str, Any]:
    scheme_id = target["scheme_id"]
    runner_class = target["runner_class"]
    runner_file = ROOT / target["runner_file"]
    item_dir = output_dir / scheme_id
    item_dir.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "scheme_id": scheme_id,
        "runner_class": runner_class,
        "runner_file": target["runner_file"],
        "source_sha256": sha256(runner_file) if runner_file.is_file() else None,
        "requested_stop_time_s": STOP_TIME_S,
        "scenario": "scenario_mode=0",
        "source": "MWORKS_MCP",
        "status": "failed",
        "started_at": now_iso(),
    }
    try:
        check_result = client.call_tool(
            "check_model",
            {"model_name": runner_class, "stop_on_error": True},
            timeout_s=300,
        )
        record["check_model"] = check_result
        record["check_model_ok"] = bool(check_result.get("ok"))
        if not record["check_model_ok"]:
            record["status"] = "check_model_failed"
            return record

        diagram_path = item_dir / "diagram.png"
        diagram_result = client.call_tool(
            "model_manager",
            {
                "action": "export_model_diagram",
                "model_name": runner_class,
                "output_path": mcp_helpers.windows_path(diagram_path),
                "width": 3000,
                "height": 1900,
                "open_model_first": True,
            },
            timeout_s=180,
        )
        record["diagram_export"] = diagram_result
        record["diagram_export_ok"] = bool(diagram_result.get("ok")) and diagram_path.is_file()
        record["diagram_path"] = project_relative(diagram_path) if diagram_path.is_file() else None

        simulation_result = mcp_helpers.simulate_modelingpy(
            client,
            model_name=runner_class,
            target_time=[0.0, STOP_TIME_S],
            native_result_dir=None,
            verify_result_var="position_error_norm",
            verify_time_point="end",
            timeout_s=360,
        )
        record["simulation"] = simulation_result
        record["simulate_model_ok"] = bool(simulation_result.get("data"))
        if not record["simulate_model_ok"]:
            record["status"] = "simulate_model_failed"
            record["result_read_after_simulation_failure"] = bool(
                (simulation_result.get("result_verification") or {}).get("result_probe", {}).get("ok")
            )
            return record

        variables = {"time": "time", "position_error_norm": "position_error_norm"}
        series = mcp_helpers.read_result_series(client, runner_class, variables)
        time_values = [float(value) for value in series.get("time", [])]
        error_values = [float(value) for value in series.get("position_error_norm", [])]
        raw_path = item_dir / "raw.csv"
        metrics_path = item_dir / "metrics.json"
        write_diagnostics_csv(raw_path, time_values, error_values)
        metrics = diagnostics_metrics(scheme_id, runner_class, time_values, error_values)
        write_json(metrics_path, metrics)
        record["raw_csv"] = project_relative(raw_path)
        record["metrics_json"] = project_relative(metrics_path)
        record["result_read_ok"] = True
        record["sample_count"] = len(time_values)
        record["time_end_s"] = time_values[-1] if time_values else None
        record["terminal_position_error_m"] = error_values[-1] if error_values else None
        record["tracking_gate_pass"] = bool(metrics["completion_gates"]["terminal_position_error_lt_5m"])
        record["status"] = "pass" if all(metrics["completion_gates"].values()) else "simulation_completed_tracking_gate_failed"
    except Exception as exc:  # preserve one-controller failures and continue
        record["status"] = "exception"
        record["error"] = repr(exc)
    finally:
        record["finished_at"] = now_iso()
        write_json(item_dir / "RUN_RECORD.json", record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wrapper",
        default=os.environ.get("SYSPLORER_MCP_WRAPPER"),
        help="Sysplorer MCP wrapper path",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results" / "control_platform" / "controller_46_live_20260820",
    )
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--stop-index", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = load_targets()
    selected = targets[args.start_index : args.stop_index]
    log_path = output_dir / "logs" / "controller_46_mcp.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")
    wrapper = mcp_helpers.resolve_wrapper(args.wrapper)
    client = mcp_helpers.JsonlMcpClient(mcp_helpers.wrapper_command(wrapper), log_path)
    summary: dict[str, Any] = {
        "schema": "mosim.controller_46_live_evidence.v1",
        "source": "MWORKS_MCP",
        "evidence_level": "real_sysplorer_mcp_controller_46_50s",
        "claim_role": "single_scenario_50s_dynamics_smoke",
        "baseline_excluded": sorted(BASELINE_IDS),
        "total_targets": len(targets),
        "selected_targets": len(selected),
        "requested_stop_time_s": STOP_TIME_S,
        "started_at": now_iso(),
        "status": "failed",
        "results": [],
    }
    try:
        health = mcp_helpers.initialize_mcp_client(client)
        summary["health"] = health
        if not health.get("ok") or not health.get("driver_ready"):
            raise RuntimeError(f"Sysplorer MCP health failed: {health}")
        load_result = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": mcp_helpers.windows_path(PACKAGE_PATH),
                "force_reload": True,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        summary["model_load"] = load_result
        if not load_result.get("ok"):
            raise RuntimeError(f"Model load failed: {load_result}")
        write_json(output_dir / "LIVE_BATCH_START.json", summary)

        for index, target in enumerate(selected, start=args.start_index):
            print(f"[{index + 1}/46] {target['scheme_id']}: start", flush=True)
            record = run_one(client, target, output_dir)
            summary["results"].append(record)
            counts = {
                "pass": sum(item.get("status") == "pass" for item in summary["results"]),
                "check_model_failed": sum(item.get("status") == "check_model_failed" for item in summary["results"]),
                "simulate_model_failed": sum(item.get("status") == "simulate_model_failed" for item in summary["results"]),
                "other_failed": sum(item.get("status") in {"exception", "simulation_completed_tracking_gate_failed"} for item in summary["results"]),
            }
            print(f"[{index + 1}/46] {target['scheme_id']}: {record.get('status')} {counts}", flush=True)
            write_json(output_dir / "LIVE_BATCH_PROGRESS.json", {**summary, "counts": counts, "updated_at": now_iso()})
        completed = len(summary["results"]) == len(selected)
        all_passed = completed and all(item.get("status") == "pass" for item in summary["results"])
        summary["status"] = "pass" if all_passed else ("partial" if completed else "incomplete")
        summary["counts"] = {
            "records_completed": len(summary["results"]),
            "pass": sum(item.get("status") == "pass" for item in summary["results"]),
            "check_model_failed": sum(item.get("status") == "check_model_failed" for item in summary["results"]),
            "simulate_model_failed": sum(item.get("status") == "simulate_model_failed" for item in summary["results"]),
            "tracking_gate_failed": sum(
                item.get("status") == "simulation_completed_tracking_gate_failed"
                for item in summary["results"]
            ),
            "exceptions": sum(item.get("status") == "exception" for item in summary["results"]),
        }
    except Exception as exc:
        summary["status"] = "blocked_or_failed_before_batch_completion"
        summary["error"] = repr(exc)
    finally:
        summary["finished_at"] = now_iso()
        write_json(output_dir / "CONTROLLER_46_LIVE_EVIDENCE.json", summary)
        try:
            client.close()
        except Exception:
            pass
    print(json.dumps({"status": summary["status"], "completed": len(summary["results"]), "output": project_relative(output_dir)}, ensure_ascii=False))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
