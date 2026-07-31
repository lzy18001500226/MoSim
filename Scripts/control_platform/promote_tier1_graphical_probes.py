#!/usr/bin/env python3
"""Promote the two external-input Tier1 graphical probes without touching G3.

The script connects only to the independently started Sysplorer port, changes
the graphical input boundary through ModelingPy, then runs the isolated
Experimental whole-aircraft runners.  It never starts, closes, or resets a
Sysplorer session and never changes controller or solver parameters.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
EVIDENCE_ROOT = ROOT / "Results" / "control_platform" / "tier1_formal_promotion_20260731"
ROOT_PACKAGE = MODEL_ROOT / "package.mo"
STOP_TIME_S = 50.0
INTERVAL_S = 0.01
TERMINAL_ERROR_LIMIT_M = 5.0

VARIABLES = {
    "position_x_m": "position[1]",
    "position_y_m": "position[2]",
    "position_z_m": "position[3]",
    "position_ref_x_m": "position_ref[1]",
    "position_ref_y_m": "position_ref[2]",
    "position_ref_z_m": "position_ref[3]",
    "position_error_norm_m": "position_error_norm",
}

RUNNERS = {
    "smc_boundary_layer": "MoSimQuadrotorModel.Experiment.Runners.Experimental.SmcBoundaryLayerFormalRunner",
    "nmpc_outer": "MoSimQuadrotorModel.Experiment.Runners.Experimental.NmpcOuterFormalRunner",
}

CHECK_CLASSES = [
    "MoSimQuadrotorModel.Control.Implementations.SlidingMode.MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW",
    "MoSimQuadrotorModel.Control.Implementations.Optimization.MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW",
    "MoSimQuadrotorModel.Control.Bridges.SmcBoundaryLayerEquationBridge",
    "MoSimQuadrotorModel.Control.Bridges.NmpcOuterEquationBridge",
    "MoSimQuadrotorModel.Control.Adapters.SmcBoundaryLayerAttitudeThrustAdapter",
    "MoSimQuadrotorModel.Control.Adapters.NmpcOuterAttitudeThrustAdapter",
    *RUNNERS.values(),
]

GRAPH_SPECS = (
    {
        "id": "smc_boundary_layer",
        "model": "MoSimQuadrotorModel.Control.Implementations.SlidingMode.MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW",
        "file": MODEL_ROOT / "Control" / "Implementations" / "SlidingMode" / "MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo",
        "inputs": (
            ("position_error_source", "position_error_in", "lambda_position.u", -480.0, 100.0),
            ("velocity_error_source", "velocity_error_in", "sliding_surface.u2", -480.0, 0.0),
            ("auxiliary_source", "auxiliary_in", "acceleration_sum.u2", -480.0, -100.0),
        ),
    },
    {
        "id": "nmpc_outer",
        "model": "MoSimQuadrotorModel.Control.Implementations.Optimization.MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW",
        "file": MODEL_ROOT / "Control" / "Implementations" / "Optimization" / "MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW.mo",
        "inputs": (
            ("position_error_source", "position_error_in", "position_prediction.u", -480.0, 100.0),
            ("velocity_error_source", "velocity_error_in", "velocity_prediction.u", -480.0, 0.0),
        ),
    },
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def last_errors() -> list[str]:
    try:
        return [str(item) for item in ModelingPy.GetLastErrors()]
    except Exception as exc:  # pragma: no cover - native API error path
        return [f"GetLastErrors failed: {exc}"]


def connect_new_session(minimum_port: int, timeout_s: float) -> int:
    deadline = time.monotonic() + timeout_s
    observed: list[int] = []
    while time.monotonic() < deadline:
        try:
            ports = [int(value) for value in ModelingPy.FindSysplorer()]
        except Exception:
            ports = []
        observed = sorted(set(ports))
        candidates = [port for port in observed if port >= minimum_port]
        if candidates:
            selected = max(candidates)
            ModelingPy.ConnectSysplorer("127.0.0.1", selected)
            return selected
        time.sleep(1.0)
    raise RuntimeError(
        f"independent Sysplorer port >= {minimum_port} was not available within {timeout_s:g}s; observed={observed}"
    )


def reload_project_root() -> dict[str, Any]:
    root_class = "MoSimQuadrotorModel"
    record: dict[str, Any] = {"root_package": repo_path(ROOT_PACKAGE)}
    if ModelingPy.ClassExist(root_class):
        erased = bool(ModelingPy.EraseClasses((root_class,)))
        record["erase_previous_root"] = erased
        if not erased:
            raise RuntimeError(f"EraseClasses failed: {last_errors()}")
    else:
        record["erase_previous_root"] = "not_needed"
    loaded = bool(ModelingPy.OpenModelFile(str(ROOT_PACKAGE)))
    record["open_model_file"] = loaded
    if not loaded:
        raise RuntimeError(f"OpenModelFile failed: {last_errors()}")
    return record


def graph_source_hashes() -> dict[str, str]:
    files = [spec["file"] for spec in GRAPH_SPECS]
    files.extend(
        [
            MODEL_ROOT / "Control" / "Bridges" / "SmcBoundaryLayerEquationBridge.mo",
            MODEL_ROOT / "Control" / "Bridges" / "NmpcOuterEquationBridge.mo",
            MODEL_ROOT / "Control" / "Adapters" / "SmcBoundaryLayerAttitudeThrustAdapter.mo",
            MODEL_ROOT / "Control" / "Adapters" / "NmpcOuterAttitudeThrustAdapter.mo",
            MODEL_ROOT / "Experiment" / "Runners" / "Experimental" / "SmcBoundaryLayerFormalRunner.mo",
            MODEL_ROOT / "Experiment" / "Runners" / "Experimental" / "NmpcOuterFormalRunner.mo",
        ]
    )
    return {repo_path(path): sha256(path) for path in files if path.is_file()}


def externalize_graph(spec: dict[str, Any]) -> dict[str, Any]:
    model = str(spec["model"])
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}: {last_errors()}")
    components = {str(component) for component in ModelingPy.GetComponents(model)}
    input_records: list[dict[str, Any]] = []
    changed = False
    for old_name, new_name, target, x, y in spec["inputs"]:
        item: dict[str, Any] = {
            "old_fixed_source": old_name,
            "new_public_input": new_name,
            "target": target,
        }
        if old_name in components:
            removed = bool(ModelingPy.RemoveComponent(model, old_name))
            item["removed_fixed_source"] = removed
            if not removed:
                raise RuntimeError(f"RemoveComponent failed: {model}.{old_name}: {last_errors()}")
            components.remove(old_name)
            changed = True
        else:
            item["removed_fixed_source"] = "already_absent"
        if new_name not in components:
            added = bool(
                ModelingPy.AddComponent(
                    "SysplorerEmbeddedCoder.Port.Inport", model, new_name, float(x), float(y), 28, 22
                )
            )
            item["added_public_input"] = added
            if not added:
                raise RuntimeError(f"AddComponent failed: {model}.{new_name}: {last_errors()}")
            components.add(new_name)
            changed = True
        else:
            item["added_public_input"] = "already_present"
        if changed:
            connected = bool(ModelingPy.ConnectPort(model, new_name, target))
            item["connected"] = connected
            if not connected:
                raise RuntimeError(f"ConnectPort failed: {model}: {new_name} -> {target}: {last_errors()}")
        else:
            item["connected"] = "preserved_existing"
        input_records.append(item)
    saved = bool(ModelingPy.SaveModel(model))
    if not saved:
        raise RuntimeError(f"SaveModel failed: {model}: {last_errors()}")
    model_text = str(ModelingPy.GetModelText(model))
    for old_name, new_name, _target, _x, _y in spec["inputs"]:
        if old_name in model_text or new_name not in model_text:
            raise RuntimeError(f"graphical source boundary did not persist for {model}: {old_name} -> {new_name}")
    diagram_path = EVIDENCE_ROOT / "graphs" / f"{spec['id']}_external_inputs.png"
    diagram_path.parent.mkdir(parents=True, exist_ok=True)
    exported = bool(ModelingPy.ExportDiagram(model, str(diagram_path), 2400, 1400))
    return {
        "model": model,
        "changed": changed,
        "inputs": input_records,
        "saved": saved,
        "source_path": repo_path(spec["file"]),
        "source_sha256": sha256(spec["file"]),
        "diagram_exported": exported,
        "diagram_path": repo_path(diagram_path) if diagram_path.is_file() else None,
    }


def run_prepare(port: int) -> int:
    record: dict[str, Any] = {
        "schema": "mosim.tier1_graphical_probe_promotion_check.v1",
        "created_at": now_iso(),
        "existing_independent_sysplorer_port": port,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "scope": "Externalize fixed graphical probe inputs through ModelingPy and CheckModel isolated Experimental runners. Frozen G2/G3 Formal catalog remains unchanged.",
        "source_hashes_before": graph_source_hashes(),
        "graphs": [],
        "checks": {},
    }
    try:
        record["initial_root_load"] = reload_project_root()
        for spec in GRAPH_SPECS:
            record["graphs"].append(externalize_graph(spec))
        record["reload_after_graph_save"] = reload_project_root()
        for model_name in CHECK_CLASSES:
            checked = bool(ModelingPy.CheckModel(model_name))
            record["checks"][model_name] = {
                "passed": checked,
                "last_errors": last_errors(),
            }
            if not checked:
                raise RuntimeError(f"CheckModel failed: {model_name}: {last_errors()}")
        record["status"] = "passed"
    except Exception as exc:
        record["status"] = "failed"
        record["error"] = str(exc)
        record["last_errors"] = last_errors()
    record["source_hashes_after"] = graph_source_hashes()
    record["completed_at"] = now_iso()
    write_json(EVIDENCE_ROOT / "CHECK_MODEL_RECORD.json", record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "passed" else 1


def write_csv(path: Path, series: dict[str, list[float]]) -> None:
    fields = ["time_s", *VARIABLES]
    count = len(series["time_s"])
    if count == 0 or any(len(series[key]) != count for key in VARIABLES):
        raise RuntimeError("inconsistent or empty result series")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(fields)
        for index in range(count):
            writer.writerow([series["time_s"][index], *(series[key][index] for key in VARIABLES)])


def newest_native_result(path: Path) -> str | None:
    candidates = [candidate for candidate in path.rglob("*.msr") if candidate.is_file()]
    if not candidates:
        return None
    return repo_path(max(candidates, key=lambda candidate: candidate.stat().st_mtime))


def run_one_runner(controller_id: str, model_name: str) -> dict[str, Any]:
    run_dir = EVIDENCE_ROOT / "runs" / controller_id
    native_dir = run_dir / "native_result"
    raw_path = run_dir / "raw" / "climbpath50s.csv"
    metrics_path = run_dir / "metrics" / "METRICS.json"
    native_dir.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "schema": "mosim.tier1_graphical_probe_formal_run.v1",
        "created_at": now_iso(),
        "controller_id": controller_id,
        "runner_class": model_name,
        "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
        "simulation_contract": {
            "start_time_s": 0.0,
            "stop_time_s": STOP_TIME_S,
            "interval_s": INTERVAL_S,
            "solver": "runner_default_Dassl",
            "parameter_tuning": "none",
        },
        "claim_boundary": "Isolated experimental whole-aircraft attempt only. It is excluded from the frozen 48-route G2/G3 catalog and does not claim controller acceptance, tuning, runtime, or deployment equivalence.",
    }
    try:
        checked = bool(ModelingPy.CheckModel(model_name))
        record["check_model"] = {"passed": checked, "last_errors": last_errors()}
        if not checked:
            raise RuntimeError(f"CheckModel failed before simulation: {last_errors()}")
        simulated = bool(
            ModelingPy.SimulateModel(
                model_name,
                startTime=0.0,
                stopTime=STOP_TIME_S,
                interval=INTERVAL_S,
                simMode=0,
                path=str(native_dir),
            )
        )
        record["simulate_model"] = {"returned": simulated, "last_errors": last_errors()}
        if not simulated:
            raise RuntimeError(f"SimulateModel failed: {last_errors()}")
        series = {"time_s": [float(value) for value in ModelingPy.GetVarTimes()]}
        for key, variable in VARIABLES.items():
            series[key] = [float(value) for value in ModelingPy.GetVarValues(variable)]
        if len(series["time_s"]) < 11:
            raise RuntimeError("simulation returned too few time samples")
        if abs(series["time_s"][-1] - STOP_TIME_S) > 0.02:
            raise RuntimeError(f"simulation ended at {series['time_s'][-1]:.12g}s, expected {STOP_TIME_S:.12g}s")
        if any(not math.isfinite(value) for values in series.values() for value in values):
            raise RuntimeError("simulation result contains non-finite values")
        errors = [
            math.sqrt(
                (series["position_ref_x_m"][index] - series["position_x_m"][index]) ** 2
                + (series["position_ref_y_m"][index] - series["position_y_m"][index]) ** 2
                + (series["position_ref_z_m"][index] - series["position_z_m"][index]) ** 2
            )
            for index in range(len(series["time_s"]))
        ]
        terminal_error = errors[-1]
        metrics = {
            "sample_count": len(series["time_s"]),
            "time_start_s": series["time_s"][0],
            "time_end_s": series["time_s"][-1],
            "position_rmse_m": math.sqrt(sum(error * error for error in errors) / len(errors)),
            "terminal_position_error_norm_m": terminal_error,
            "maximum_position_error_norm_m": max(errors),
            "terminal_error_gate_m": TERMINAL_ERROR_LIMIT_M,
            "terminal_error_gate_passed": terminal_error < TERMINAL_ERROR_LIMIT_M,
        }
        write_csv(raw_path, series)
        write_json(metrics_path, metrics)
        record.update(
            {
                "status": "passed" if metrics["terminal_error_gate_passed"] else "completed_gate_failed",
                "raw_csv": repo_path(raw_path),
                "metrics": metrics,
                "metrics_json": repo_path(metrics_path),
                "native_result": newest_native_result(native_dir),
            }
        )
    except Exception as exc:
        record["status"] = "failed_execution"
        record["error"] = str(exc)
        record["last_errors"] = last_errors()
        record["native_result"] = newest_native_result(native_dir)
    record["completed_at"] = now_iso()
    write_json(run_dir / "RUN_RECORD.json", record)
    return record


def run_simulation(port: int) -> int:
    record: dict[str, Any] = {
        "schema": "mosim.tier1_graphical_probe_formal_simulation.v1",
        "created_at": now_iso(),
        "existing_independent_sysplorer_port": port,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "source_hashes_before": graph_source_hashes(),
        "runs": [],
    }
    try:
        record["root_load"] = reload_project_root()
        for controller_id, model_name in RUNNERS.items():
            record["runs"].append(run_one_runner(controller_id, model_name))
        record["status"] = "passed" if all(
            run["status"] in {"passed", "completed_gate_failed"} for run in record["runs"]
        ) else "failed"
    except Exception as exc:
        record["status"] = "failed"
        record["error"] = str(exc)
        record["last_errors"] = last_errors()
    record["source_hashes_after"] = graph_source_hashes()
    record["completed_at"] = now_iso()
    write_json(EVIDENCE_ROOT / "SIMULATION_RECORD.json", record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "passed" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prepare", "simulate"), required=True)
    parser.add_argument("--port", type=int, help="Explicit independently started Sysplorer port")
    parser.add_argument("--minimum-port", type=int, default=49153)
    parser.add_argument("--connect-timeout-s", type=float, default=45.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    if args.port is not None:
        ModelingPy.ConnectSysplorer("127.0.0.1", args.port)
        port = args.port
    else:
        port = connect_new_session(args.minimum_port, args.connect_timeout_s)
    if args.phase == "prepare":
        return run_prepare(port)
    return run_simulation(port)


if __name__ == "__main__":
    raise SystemExit(main())
