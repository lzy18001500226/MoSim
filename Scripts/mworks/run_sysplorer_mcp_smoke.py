#!/usr/bin/env python3
"""Run an embedded MoSim quadrotor baseline simulation through Sysplorer MCP.

The script writes project-local raw CSV, metrics, and MCP JSONL evidence.
By default it keeps the Windows Sysplorer GUI/session reusable between runs to
avoid repeated startup cost. Pass --shutdown-session only when explicit cleanup
is needed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

RESULTS_SCRIPT_DIR = Path(__file__).resolve().parents[1] / "results"
if str(RESULTS_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(RESULTS_SCRIPT_DIR))

from calc_metrics import compute_metrics


def default_wrapper_candidates() -> list[str]:
    """Return known Sysplorer MCP wrapper locations for WSL and Windows shells."""
    home = Path.home()
    project_root = Path(__file__).resolve().parents[2]
    names = ["sysplorer_mcp.sh", "sysplorer_mcp.bat", "sysplorer_mcp.cmd", "sysplorer_mcp.ps1"]
    raw_candidates = []
    if os.name == "nt":
        raw_candidates.append(
            str(
                project_root
                / "Docs"
                / "Skills"
                / "Mworks"
                / "mworks-mcp-operations"
                / "wrappers"
                / "sysplorer_mcp.cmd"
            )
        )
    else:
        raw_candidates.append(str(project_root / "Scripts" / "mworks" / "sysplorer_mcp_wsl_bridge.sh"))
        raw_candidates.append("/home/linux/mcp-wrappers/sysplorer_mcp.sh")
    raw_candidates.extend(str(home / "mcp-wrappers" / name) for name in names)
    candidates: list[str] = []
    seen: set[str] = set()
    for candidate in raw_candidates:
        if candidate not in seen:
            seen.add(candidate)
            candidates.append(candidate)
    return candidates


DEFAULT_WRAPPER_CANDIDATES = default_wrapper_candidates()
DEFAULT_MODEL_FILE = r"C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\package.mo"
DEFAULT_MODEL_NAME = "MoSimQuadrotorModel.Vehicle.Examples.Example1"
GUI_ANIMATION_TIMEOUT_S = 180
WINDOWS_NATIVE_RESULT_PATH_LIMIT = 180
DEFAULT_VARIABLES = {
    "time": "time",
    "x": "sensors1_1.PosMea[1]",
    "y": "sensors1_1.PosMea[2]",
    "z": "sensors1_1.PosMea[3]",
    "x_ref": "climbePath.position_command[1]",
    "y_ref": "climbePath.position_command[2]",
    "z_ref": "climbePath.position_command[3]",
    "roll": "sensors1_1.AngleMea[1]",
    "pitch": "sensors1_1.AngleMea[2]",
    "yaw": "sensors1_1.AngleMea[3]",
    "u1": "controller3_2.y",
    "u2": "controller3_2.y1",
    "u3": "controller3_2.y2",
    "u4": "controller3_2.y3",
}
CORE_VARIABLE_ALIASES = {"time", "x", "y", "z", "x_ref", "y_ref", "z_ref"}
VARIABLE_PROFILES = {"standard_tracking", "diagnostics_declared"}
METRICS_PROFILES = {"standard_tracking", "diagnostics_smoke"}


def windows_path(path: Path) -> str:
    """Return an absolute Windows path for paths under the shared project tree."""
    resolved = path.resolve()
    text = str(resolved)
    if os.name == "nt":
        return text
    if text.startswith("/mnt/") and len(text) > 6 and text[6] == "/":
        drive = text[5].upper()
        rest = text[7:].replace("/", "\\")
        return f"{drive}:\\{rest}"
    return text.replace("/", "\\")


def parse_extra_variables(items: list[str], *, allow_default_override: bool = False) -> dict[str, str]:
    variables: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Extra variable must use alias=model.variable syntax: {item}")
        alias, model_var = item.split("=", 1)
        alias = alias.strip()
        model_var = model_var.strip()
        if not alias or not model_var:
            raise ValueError(f"Extra variable must use alias=model.variable syntax: {item}")
        if alias in variables or (not allow_default_override and alias in DEFAULT_VARIABLES):
            raise ValueError(f"Duplicate result variable alias: {alias}")
        variables[alias] = model_var
    return variables


def choose_verify_result_var(variable_profile: str, variables: dict[str, str]) -> str:
    """Pick a result variable that should exist for this export profile."""
    if variable_profile == "diagnostics_declared":
        for alias, model_var in variables.items():
            if alias != "time" and model_var != "time":
                return model_var
        return "time"
    return variables.get("z", "sensors1_1.PosMea[3]")


class JsonlMcpClient:
    """Minimal JSON-lines MCP client for the local Sysplorer wrapper."""

    def __init__(self, command: list[str], log_path: Path) -> None:
        self.log_path = log_path
        self.next_id = 1
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        self.stdout_queue: queue.Queue[str] = queue.Queue()
        self.stderr_queue: queue.Queue[str] = queue.Queue()
        threading.Thread(target=self._read_lines, args=(self.proc.stdout, self.stdout_queue), daemon=True).start()
        threading.Thread(target=self._read_lines, args=(self.proc.stderr, self.stderr_queue), daemon=True).start()

    @staticmethod
    def _read_lines(stream: Any, target: queue.Queue[str]) -> None:
        if stream is None:
            return
        for line in stream:
            target.put(line)

    def _append_log(self, payload: dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def set_log_path(self, log_path: Path) -> None:
        self.log_path = log_path

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        self._append_log({"direction": "notify", **payload})
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def request(self, method: str, params: dict[str, Any] | None = None, timeout_s: float = 360.0) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        self._append_log({"direction": "request", **payload})
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

        start = time.monotonic()
        while time.monotonic() - start < timeout_s:
            while not self.stderr_queue.empty():
                self._append_log({"direction": "stderr", "text": self.stderr_queue.get().rstrip()})
            try:
                line = self.stdout_queue.get(timeout=0.2)
            except queue.Empty:
                if self.proc.poll() is not None:
                    raise RuntimeError(f"MCP process exited with code {self.proc.returncode}")
                continue

            response = json.loads(line)
            self._append_log({"direction": "response", **response})
            if response.get("id") == request_id:
                return response

        raise TimeoutError(f"Timeout waiting for MCP method {method}")

    def call_tool(self, name: str, arguments: dict[str, Any], timeout_s: float = 360.0) -> dict[str, Any]:
        response = self.request(
            "tools/call",
            {"name": name, "arguments": arguments},
            timeout_s=timeout_s,
        )
        result = response.get("result", {})
        raw = result.get("structuredContent", {}).get("result")
        if raw:
            return json.loads(raw)
        content = result.get("content") or []
        if content and isinstance(content[0], dict):
            return json.loads(content[0].get("text", "{}"))
        return result

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.proc.terminate()
                self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def write_csv(series_by_alias: dict[str, list[float]], variables: dict[str, str], output: Path) -> None:
    names = list(variables)
    missing_core = [name for name in names if name in CORE_VARIABLE_ALIASES and name not in series_by_alias]
    if missing_core:
        raise ValueError(f"Missing required result series: {', '.join(missing_core)}")
    if not series_by_alias or "time" not in series_by_alias or not series_by_alias["time"]:
        raise ValueError("MCP result series is empty; refusing to overwrite raw CSV")
    row_count = min(len(item) for item in series_by_alias.values())
    if row_count <= 0:
        raise ValueError("MCP result series has zero rows; refusing to overwrite raw CSV")
    inconsistent_lengths = {
        name: len(series)
        for name, series in series_by_alias.items()
        if len(series) != row_count
    }
    if inconsistent_lengths:
        print(
            "Warning: MCP result series lengths are inconsistent; truncating to "
            f"{row_count} common rows: {inconsistent_lengths}",
            file=sys.stderr,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_suffix(output.suffix + ".tmp")
    with temp_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        for index in range(row_count):
            writer.writerow([
                series_by_alias[name][index] if name in series_by_alias else ""
                for name in names
            ])
    temp_output.replace(output)


def read_numeric_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        data = {name: [] for name in reader.fieldnames}
        for row in reader:
            for name in reader.fieldnames:
                value = row.get(name, "")
                try:
                    data[name].append(float(value) if value != "" else float("nan"))
                except ValueError:
                    data[name].append(float("nan"))
    return data


def read_result_series(
    client: JsonlMcpClient,
    model_name: str,
    variables: dict[str, str],
) -> dict[str, list[float]]:
    series_by_alias: dict[str, list[float]] = {}
    missing: dict[str, str] = {}
    for alias, variable in variables.items():
        read_result = client.call_tool(
            "result_manager",
            {
                "action": "get_vars_values",
                "model_name": model_name,
                "var_names": [variable],
            },
            timeout_s=240,
        )
        data = read_result.get("data") if read_result.get("ok") else None
        if isinstance(data, list) and data and isinstance(data[0], list) and data[0]:
            series_by_alias[alias] = data[0]
        else:
            missing[alias] = variable
    missing_core = [name for name in missing if name in CORE_VARIABLE_ALIASES]
    if missing_core:
        detail = ", ".join(f"{name}={missing[name]}" for name in missing_core)
        raise RuntimeError(f"Missing required result variables: {detail}")
    if missing:
        detail = ", ".join(f"{name}={variable}" for name, variable in missing.items())
        print(f"Warning: optional result variables were not exported and will be blank in CSV: {detail}", file=sys.stderr)
    return series_by_alias


def open_existing_native_result_for_reading(
    client: JsonlMcpClient,
    native_result: Path,
) -> dict[str, Any]:
    """Open one project-local Result.msr without loading or simulating a model."""
    project_root = Path(__file__).resolve().parents[2]
    resolved = native_result.resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise ValueError(f"--read-native-result must remain under the project root: {resolved}") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"Existing native result is missing: {resolved}")

    source = f"""
import mworks.sysplorer as ModelingPy

results = {{}}
try:
    results["open_result"] = ModelingPy.OpenResult({windows_path(resolved)!r})
except Exception as exc:
    results["open_result_error"] = repr(exc)
RUN_SCRIPT_RESULT = results
"""
    result = client.call_tool(
        "call_code",
        {"mode": "run_script", "payload": {"python_source": source}},
        timeout_s=60,
    )
    nested = result.get("run_script_result") if isinstance(result.get("run_script_result"), dict) else {}
    if not result.get("ok") or nested.get("open_result") is not True:
        raise RuntimeError(f"Native Result.msr OpenResult failed: {result}")
    return result


def simulate_modelingpy(
    client: JsonlMcpClient,
    *,
    model_name: str,
    target_time: list[float],
    native_result_dir: Path | None,
    verify_result_var: str,
    verify_time_point: str = "end",
    interval: float | None = None,
    simulation_api: str = "simulate_model",
    simulate_model_options: dict[str, Any] | None = None,
    simulate_ex_options: dict[str, Any] | None = None,
    timeout_s: float = 360,
) -> dict[str, Any]:
    if len(target_time) != 2:
        raise ValueError(f"target_time must contain start and stop time, got: {target_time}")
    if simulation_api not in {"simulate_model", "simulate_model_ex"}:
        raise ValueError(f"Unsupported simulation_api: {simulation_api}")
    if timeout_s <= 0:
        raise ValueError(f"simulation timeout must be positive, got: {timeout_s}")
    start_time = float(target_time[0])
    stop_time = float(target_time[1])
    result_dir = windows_path(native_result_dir) if native_result_dir is not None else ""
    interval_arg = "None" if interval is None else repr(float(interval))
    if simulation_api == "simulate_model":
        if simulate_model_options is not None and not isinstance(simulate_model_options, dict):
            raise ValueError("simulate_model_options must be a dictionary when provided")
        options = dict(simulate_model_options or {})
        protected = {"startTime", "stopTime", "interval", "simMode", "path"}
        conflicting = sorted(protected.intersection(options))
        if conflicting:
            raise ValueError(
                "SimulateModel options must not override target-time or result-binding fields: "
                + ", ".join(conflicting)
            )
        if any(not isinstance(key, str) for key in options):
            raise ValueError("SimulateModel option keys must be strings")
        api_name = "ModelingPy.SimulateModel"
        simulation_call = f"""ModelingPy.SimulateModel(
        {model_name!r},
        startTime={start_time!r},
        stopTime={stop_time!r},
        interval={interval_arg},
        simMode=0,
        path={result_dir!r},
        **{options!r},
    )"""
    else:
        if simulate_model_options:
            raise ValueError("simulate_model_options applies only to SimulateModel")
        options = {"startTime": start_time, "stopTime": stop_time}
        if interval is not None:
            options["interval"] = float(interval)
        if simulate_ex_options:
            protected = {"startTime", "stopTime", "interval"}
            conflicting = sorted(protected.intersection(simulate_ex_options))
            if conflicting:
                raise ValueError(
                    "SimulateModelEx options must not override target-time fields: "
                    + ", ".join(conflicting)
                )
            options.update(simulate_ex_options)
        api_name = "ModelingPy.SimulateModelEx"
        simulation_call = f"ModelingPy.SimulateModelEx({model_name!r}, {options!r})"
    script = f"""
import mworks.sysplorer as ModelingPy
import json

results = {{}}
results["simulation_api"] = {api_name!r}

def _json_safe(value):
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except Exception:
        return repr(value)

def _capture_simulation_diagnostic(api_name):
    diagnostic = {{"api": api_name}}
    try:
        member = getattr(ModelingPy, api_name)
        value = member() if callable(member) else member
        diagnostic["ok"] = True
        diagnostic["data"] = _json_safe(value)
    except Exception as exc:
        diagnostic["ok"] = False
        diagnostic["error"] = repr(exc)
    return diagnostic

try:
    results["simulate"] = {simulation_call}
except Exception as exc:
    results["simulate_error"] = repr(exc)

# Capture the solver/compiler state before any result APIs can overwrite the
# active MWORKS diagnostic buffer.  Some formal runners emit a fresh but empty
# Result.msr after a rejected solver start, so result readability is not a
# substitute for this immediate state capture.
results["post_simulation_diagnostics"] = {{
    api_name: _capture_simulation_diagnostic(api_name)
    for api_name in (
        "GetSimulationExitState",
        "GetSimulationState",
        "GetCurrentSimTime",
        "MessageText",
        "GetLastErrors",
    )
}}

last_errors_diagnostic = results["post_simulation_diagnostics"]["GetLastErrors"]
if last_errors_diagnostic.get("ok"):
    last_errors = last_errors_diagnostic.get("data")
    if isinstance(last_errors, (list, tuple)):
        results["last_errors"] = [str(item) for item in last_errors]
    elif last_errors is None:
        results["last_errors"] = []
    else:
        results["last_errors"] = [str(last_errors)]
else:
    results["last_errors"] = []
    results["last_errors_error"] = last_errors_diagnostic.get("error")

try:
    results["result_probe_type"] = ModelingPy.GetResultVariableInfo({verify_result_var!r}, "Type")
    results["has_readable_result"] = True
except Exception as exc:
    results["result_probe_error"] = repr(exc)
    results["has_readable_result"] = False

try:
    results["get_var_value_at"] = ModelingPy.GetVarValueAt({verify_result_var!r}, {verify_time_point!r})
except Exception as exc:
    results["get_var_value_at_error"] = repr(exc)

RUN_SCRIPT_RESULT = results
"""
    run_result = client.call_tool(
        "call_code",
        {"mode": "run_script", "payload": {"python_source": script}},
        timeout_s=timeout_s,
    )
    nested = run_result.get("run_script_result") if isinstance(run_result.get("run_script_result"), dict) else {}
    simulate_ok = bool(nested.get("simulate"))
    readable = bool(nested.get("has_readable_result")) and "get_var_value_at" in nested
    return {
        "ok": bool(run_result.get("ok")) and (simulate_ok or readable),
        "api": api_name,
        "simulation_options": (
            simulate_model_options if simulation_api == "simulate_model" else simulate_ex_options
        ),
        "data": simulate_ok,
        "simulate_api_reported_failure": not simulate_ok,
        "last_errors": nested.get("last_errors", []),
        "last_errors_error": nested.get("last_errors_error"),
        "post_simulation_diagnostics": nested.get("post_simulation_diagnostics", {}),
        "result_verification": {
            "result_probe": {
                "ok": bool(nested.get("has_readable_result")),
                "has_readable_result": bool(nested.get("has_readable_result")),
                "data": nested.get("result_probe_type"),
                "error": nested.get("result_probe_error"),
            },
            "get_var_value_at": {
                "ok": "get_var_value_at" in nested,
                "data": nested.get("get_var_value_at"),
                "error": nested.get("get_var_value_at_error"),
            },
        },
        "run_script_result": nested,
        "raw_tool_result": run_result,
    }


def write_metrics(
    raw_csv: Path,
    metrics_json: Path,
    metrics_csv: Path,
    scene_id: str,
    controller_id: str,
    evidence_level: str,
    metrics_profile: str = "standard_tracking",
) -> None:
    if metrics_profile == "standard_tracking":
        from calc_metrics import read_csv as read_project_csv

        data = read_project_csv(raw_csv)
        metrics = compute_metrics(data, raw_csv, scene_id, controller_id)
    elif metrics_profile == "diagnostics_smoke":
        data = read_numeric_csv(raw_csv)
        time_values = data.get("time", [])
        if not time_values:
            raise ValueError(f"Diagnostics smoke metrics input has no time column/data: {raw_csv}")
        duration_s = (max(time_values) - min(time_values)) if time_values else float("nan")
        numeric_columns = [name for name in data if name != "time"]
        nan_count = sum(
            1
            for values in data.values()
            for value in values
            if not math.isfinite(value)
        )
        metrics = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "raw_file": str(raw_csv),
            "scene_id": scene_id,
            "controller_id": controller_id,
            "row_count": len(time_values),
            "duration_s": duration_s,
            "sample_rate_hz": (len(time_values) - 1) / duration_s
            if duration_s and duration_s > 0 and len(time_values) > 1
            else None,
            "diagnostics_column_count": len(numeric_columns),
            "diagnostics_columns": numeric_columns,
            "nan_count": nan_count,
            "valid": len(time_values) > 10 and nan_count == 0 and bool(numeric_columns),
            "claim_role": "dynamics_smoke_only",
        }
        for name in numeric_columns:
            values = [value for value in data[name] if math.isfinite(value)]
            if values:
                metrics[f"{name}_min"] = min(values)
                metrics[f"{name}_max"] = max(values)
                metrics[f"{name}_final"] = values[-1]
    else:
        raise ValueError(f"Unsupported metrics profile: {metrics_profile}")
    metrics["source"] = "MWORKS_MCP"
    metrics["evidence_level"] = evidence_level
    metrics["metrics_profile"] = metrics_profile
    metrics_json.parent.mkdir(parents=True, exist_ok=True)
    metrics_json.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    metrics_csv.parent.mkdir(parents=True, exist_ok=True)
    with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, "" if value is None else value])


def export_existing_native_result(
    args: argparse.Namespace,
    client: JsonlMcpClient,
    *,
    variables: dict[str, str],
    active_log_output: Path,
    final_log_output: Path,
) -> dict[str, Any]:
    """Export an already-created native result without changing solver state."""
    if not args.no_gui_result_viewer or not args.no_gui_open:
        raise ValueError(
            "--read-native-result requires --no-gui-result-viewer and --no-gui-open; "
            "this recovery path only reads an existing result and must not create GUI review state"
        )

    native_result = args.read_native_result.resolve()
    open_existing_native_result_for_reading(client, native_result)
    result_series = read_result_series(client, args.model_name, variables)
    write_csv(result_series, variables, args.raw_output)
    write_metrics(
        args.raw_output,
        args.metrics_json,
        args.metrics_csv,
        args.scene_id,
        args.controller_id,
        args.evidence_level,
        args.metrics_profile,
    )
    if active_log_output != final_log_output:
        active_log_output.replace(final_log_output)

    print(f"MCP log: {final_log_output}")
    print(f"Raw CSV: {args.raw_output}")
    print(f"Metrics JSON: {args.metrics_json}")
    print(f"Metrics CSV: {args.metrics_csv}")
    print(f"Native result: {native_result}")
    print(f"Rows: {len(result_series['time'])}")
    print("Check model: skipped; existing native Result.msr was opened read-only")
    print("Simulate model: skipped; existing native Result.msr was exported")
    return {
        "raw_output": args.raw_output,
        "metrics_json": args.metrics_json,
        "metrics_csv": args.metrics_csv,
        "native_result": native_result,
        "gui_native_result": None,
        "gui_result": None,
        "log_output": final_log_output,
        "rows": len(result_series["time"]),
        "mode": "read_existing_native_result",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wrapper",
        default=os.environ.get("SYSPLORER_MCP_WRAPPER"),
        help=(
            "Sysplorer MCP wrapper path. Defaults to SYSPLORER_MCP_WRAPPER, "
            "the project MWORKS skill wrapper on Windows, /home/linux/mcp-wrappers/sysplorer_mcp.sh, "
            "then ~/mcp-wrappers/sysplorer_mcp.{sh,bat,cmd,ps1}."
        ),
    )
    parser.add_argument("--model-file", default=DEFAULT_MODEL_FILE)
    parser.add_argument(
        "--extra-model-file",
        action="append",
        default=[],
        help="Additional Modelica package file to load after --model-file. Can be repeated.",
    )
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--target-time", default="0,50", help="Comma-separated simulation target time range")
    parser.add_argument(
        "--simulation-interval",
        type=float,
        default=None,
        help=(
            "Optional SimulateModel output interval for a controlled diagnostic. "
            "When omitted, the model experiment interval is preserved."
        ),
    )
    parser.add_argument(
        "--simulation-api",
        choices=("simulate_model", "simulate_model_ex"),
        default="simulate_model",
        help="Use SimulateModel (default) or a bounded SimulateModelEx diagnostic.",
    )
    parser.add_argument(
        "--simulate-ex-options-json",
        default="{}",
        help=(
            "JSON object merged into SimulateModelEx after target-time fields are fixed; "
            "for example '{\"algorithm\": \"Euler\", \"fixedOrInitStepSize\": 0.01}'."
        ),
    )
    parser.add_argument("--raw-output", type=Path, default=Path("Results/official/example1_step/official_example1_pid_baseline/raw/official_example1_pid_baseline.csv"))
    parser.add_argument("--metrics-json", type=Path, default=Path("Results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.json"))
    parser.add_argument("--metrics-csv", type=Path)
    parser.add_argument("--log-output", type=Path, default=Path("Results/official/example1_step/official_example1_pid_baseline/logs/sysplorer_example1_pid_baseline_full.jsonl"))
    parser.add_argument(
        "--native-result-dir",
        type=Path,
        default=None,
        help="Directory for Sysplorer native result files used by GUI result viewer and animation",
    )
    parser.add_argument(
        "--read-native-result",
        type=Path,
        default=None,
        help=(
            "Open one existing project-local Result.msr and export declared variables without loading, "
            "checking, or simulating the model. Requires --no-gui-result-viewer and --no-gui-open."
        ),
    )
    parser.add_argument("--scene-id", default="official_example1_pid_baseline")
    parser.add_argument("--controller-id", default="pid_baseline")
    parser.add_argument("--evidence-level", default="real_sysplorer_mcp_full_baseline")
    parser.add_argument(
        "--variable-profile",
        choices=sorted(VARIABLE_PROFILES),
        default="standard_tracking",
        help=(
            "standard_tracking exports trajectory/control defaults; diagnostics_declared exports only time "
            "plus --extra-variable/--override-variable declarations."
        ),
    )
    parser.add_argument(
        "--metrics-profile",
        choices=sorted(METRICS_PROFILES),
        default="standard_tracking",
        help="Metric writer profile. Use diagnostics_smoke for non-trajectory Dynamics smoke outputs.",
    )
    parser.add_argument(
        "--extra-variable",
        action="append",
        default=[],
        help="Additional result variable as alias=model.variable. Can be repeated.",
    )
    parser.add_argument(
        "--override-variable",
        action="append",
        default=[],
        help="Override a default result variable such as x_ref=model.variable. Can be repeated.",
    )
    parser.add_argument(
        "--shutdown-session",
        action="store_true",
        help="Explicitly request session_manager shutdown after saving outputs. Default keeps GUI reusable.",
    )
    parser.add_argument(
        "--no-gui-result-viewer",
        action="store_true",
        help="Skip Sysplorer native result files and GUI plot/animation after simulation",
    )
    parser.add_argument(
        "--no-gui-open",
        action="store_true",
        help="Write Sysplorer native Result.msr but skip automatic GUI plot/animation opening",
    )
    parser.add_argument(
        "--gui-reset-windows",
        action="store_true",
        help="Close existing Sysplorer plot/animation windows before opening the current result for manual GUI review",
    )
    parser.add_argument(
        "--gui-review-stop-time",
        type=float,
        default=None,
        help=(
            "For diagnostics only, open GUI plot/animation from a separate shortened native result "
            "ending at this time while preserving full-length raw/metrics evidence."
        ),
    )
    parser.add_argument(
        "--gui-review-full-time",
        action="store_true",
        help=(
            "When using --gui-review-native-result-dir, keep the GUI review native result at the full "
            "target time range. Use with --gui-review-interval to reduce animation result size."
        ),
    )
    parser.add_argument(
        "--gui-review-interval",
        type=float,
        default=None,
        help="Optional output interval for the separate GUI review native result.",
    )
    parser.add_argument(
        "--gui-review-native-result-dir",
        type=Path,
        default=None,
        help="Optional native result directory for the separate GUI review run.",
    )
    parser.add_argument(
        "--allow-readable-result-after-simulate-false",
        action="store_true",
        help=(
            "Continue exporting results when SimulateModel reports false but the official "
            "result API confirms the verification variable is readable. Use only for "
            "documented MWORKS API/status mismatches."
        ),
    )
    return parser.parse_args(argv)


def resolve_wrapper(wrapper: str | None) -> str:
    candidates = [wrapper] if wrapper else []
    candidates.extend(DEFAULT_WRAPPER_CANDIDATES)
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.exists():
            return str(path)
    searched = ", ".join(str(Path(item).expanduser()) for item in candidates if item)
    raise FileNotFoundError(f"Sysplorer MCP wrapper not found. Checked: {searched}")


def wrapper_command(wrapper: str) -> list[str]:
    """Return a subprocess command for wrapper scripts on WSL or Windows."""
    path = Path(wrapper)
    if path.suffix.lower() == ".ps1":
        return ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path)]
    return [str(path)]


def parse_target_time(target_time: str) -> list[float]:
    return [float(item.strip()) for item in target_time.split(",") if item.strip()]


def parse_simulate_ex_options(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--simulate-ex-options-json must be a JSON object: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("--simulate-ex-options-json must be a JSON object")
    if any(not isinstance(key, str) for key in value):
        raise ValueError("--simulate-ex-options-json keys must be strings")
    return value


def prepare_log_output(log_output: Path) -> tuple[Path, Path]:
    log_output.parent.mkdir(parents=True, exist_ok=True)
    final_log_output = log_output
    protected_existing_log = final_log_output.exists()
    active_log_output = final_log_output
    if protected_existing_log:
        active_log_output = final_log_output.with_name(f"{final_log_output.name}.running")
    active_log_output.write_text("", encoding="utf-8")
    return active_log_output, final_log_output


def initialize_mcp_client(client: JsonlMcpClient) -> dict[str, Any]:
    client.request(
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "quadrotor-sysplorer-smoke", "version": "0.1"},
        },
        timeout_s=120,
    )
    client.notify("notifications/initialized")
    health = client.call_tool("session_manager", {"action": "health"}, timeout_s=180)
    if not health.get("ok") or not health.get("driver_ready"):
        raise RuntimeError(f"Sysplorer MCP health failed: {health}")
    return health


def default_native_result_dir(raw_output: Path) -> Path:
    return raw_output.parent.parent / "native_result"


def slugify_for_path(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._")
    return slug or "mworks_result"


def native_result_file(native_result_dir: Path, model_name: str) -> Path:
    leaf_name = model_name.rsplit(".", 1)[-1]
    return native_result_dir / leaf_name / "Result.msr"


def resolve_native_result_dir(raw_output: Path, requested_dir: Path | None, model_name: str) -> tuple[Path, Path | None]:
    """Choose a native result directory that MWORKS can write on Windows.

    MWORKS runs on Windows even when this script is launched from WSL. Paths
    shorter than Windows' traditional 260 character limit can still fail
    ModelingPy.OpenResult/CreatePlot in Sysplorer, so use a conservative
    project-local cache path for GUI-bound native results.
    """
    preferred_dir = requested_dir or default_native_result_dir(raw_output)
    preferred_result = native_result_file(preferred_dir, model_name)
    if len(windows_path(preferred_result)) <= WINDOWS_NATIVE_RESULT_PATH_LIMIT:
        return preferred_dir, None

    leaf_name = model_name.rsplit(".", 1)[-1]
    cache_key = slugify_for_path(raw_output.parent.parent.name)
    short_dir = Path("Results") / "native_result_cache" / cache_key
    manifest = preferred_dir / "native_result_manifest.json"
    return short_dir, manifest


def write_native_result_manifest(manifest: Path | None, *, native_result_dir: Path, native_result: Path, model_name: str) -> None:
    if manifest is None:
        return
    manifest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name": model_name,
        "reason": "preferred native_result path is too long for reliable Windows/MWORKS OpenResult/CreatePlot binding",
        "native_result_dir": str(native_result_dir),
        "native_result_file": str(native_result),
        "native_result_file_windows": windows_path(native_result),
    }
    manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_native_result_target(native_result: Path) -> Path:
    """Remove the exact model result folder before writing a GUI-bound run.

    Sysplorer creates ``ModelName-1``/``ModelName-2`` folders when the target
    model result directory already exists. The opener then points at stale
    ``ModelName/Result.msr`` and GUI OpenResult fails. Removing only this exact
    generated folder keeps the native result path deterministic.
    """
    result_folder = native_result.parent
    if result_folder.exists():
        try:
            shutil.rmtree(result_folder)
        except PermissionError:
            suffix = time.strftime("%Y%m%d_%H%M%S")
            result_folder = result_folder.with_name(f"{result_folder.name}_{suffix}")
            native_result = result_folder / native_result.name
    return native_result


def should_use_short_gui_review(args: argparse.Namespace, target_time: list[float]) -> bool:
    if args.gui_review_stop_time is None or args.gui_review_full_time:
        return False
    if len(target_time) != 2:
        return False
    start_time, stop_time = float(target_time[0]), float(target_time[1])
    return float(args.gui_review_stop_time) > start_time and float(args.gui_review_stop_time) < stop_time


def gui_review_target_time(args: argparse.Namespace, target_time: list[float]) -> list[float]:
    if args.gui_review_stop_time is not None and not args.gui_review_full_time:
        return [float(target_time[0]), float(args.gui_review_stop_time)]
    return [float(target_time[0]), float(target_time[1])]


def gui_review_native_result_dir(args: argparse.Namespace, native_result_dir: Path) -> Path:
    if args.gui_review_native_result_dir is not None:
        return args.gui_review_native_result_dir
    return native_result_dir.parent / f"{native_result_dir.name}_gui_review"


def open_gui_result_viewer(
    client: JsonlMcpClient,
    *,
    native_result: Path,
    model_name: str,
    variables: dict[str, str],
    reset_windows: bool = False,
) -> dict[str, Any]:
    result_file = windows_path(native_result)
    cleanup_result: dict[str, Any] | None = None
    if reset_windows:
        cleanup_script = """
import mworks.sysplorer as ModelingPy

results = {}
for name in ("StopAnimation", "RemoveAnimations", "RemovePlots"):
    try:
        results[name] = getattr(ModelingPy, name)()
    except Exception as exc:
        results[name + "_error"] = repr(exc)

RUN_SCRIPT_RESULT = results
"""
        try:
            cleanup_result = client.call_tool(
                "call_code",
                {"mode": "run_script", "payload": {"python_source": cleanup_script}},
                timeout_s=30,
            )
        except Exception as exc:
            cleanup_result = {"ok": False, "warning": f"gui_cleanup_failed: {exc}"}

    try:
        model_result = client.call_tool(
            "model_manager",
            {"action": "open", "model_name": model_name},
            timeout_s=30,
        )
    except Exception as exc:
        model_result = {"ok": False, "warning": f"gui_model_open_failed: {exc}"}

    declared_diagnostic_vars = [
        value for alias, value in variables.items() if alias != "time"
    ]
    plot_vars = declared_diagnostic_vars or [
        variables.get("z", "sensors1_1.PosMea[3]"),
        variables.get("z_ref", "climbePath.position_command[3]"),
        variables.get("x", "sensors1_1.PosMea[1]"),
        variables.get("x_ref", "climbePath.position_command[1]"),
    ]
    plot_vars = [item for index, item in enumerate(plot_vars) if item and item not in plot_vars[:index]]
    plot_script = f"""
import mworks.sysplorer as ModelingPy

results = {{}}
try:
    results["open_result"] = ModelingPy.OpenResult({result_file!r})
except Exception as exc:
    results["open_result_error"] = repr(exc)

try:
    results["create_plot"] = ModelingPy.CreatePlot(
        id=1,
        x="time",
        y={plot_vars!r},
        resultFile={result_file!r},
    )
except Exception as exc:
    results["create_plot_error"] = repr(exc)

RUN_SCRIPT_RESULT = results
"""
    try:
        plot_result = client.call_tool(
            "call_code",
            {"mode": "run_script", "payload": {"python_source": plot_script}},
            timeout_s=30,
        )
    except Exception as exc:
        plot_result = {"ok": False, "warning": f"gui_plot_failed: {exc}"}

    animation_script = f"""
import mworks.sysplorer as ModelingPy

results = {{}}
try:
    try:
        results["open_model_diagram"] = ModelingPy.OpenModel({model_name!r}, ModelingPy.ModelView.Diagram)
    except Exception as exc:
        results["open_model_diagram_fallback"] = repr(exc)
        results["open_model"] = ModelingPy.OpenModel({model_name!r})
except Exception as exc:
    results["open_model_error"] = repr(exc)

try:
    results["open_result"] = ModelingPy.OpenResult({result_file!r})
except Exception as exc:
    results["open_result_error"] = repr(exc)

try:
    results["create_animation"] = ModelingPy.CreateAnimation()
except Exception as exc:
    results["create_animation_error"] = repr(exc)

try:
    results["animation_speed"] = ModelingPy.AnimationSpeed(0.2)
except Exception as exc:
    results["animation_speed_error"] = repr(exc)

RUN_SCRIPT_RESULT = results
"""
    try:
        animation_result = client.call_tool(
            "call_code",
            {"mode": "run_script", "payload": {"python_source": animation_script}},
            timeout_s=GUI_ANIMATION_TIMEOUT_S,
        )
    except Exception as exc:
        animation_result = {"ok": False, "warning": f"gui_animation_failed: {exc}"}

    return {
        "native_result_file": result_file,
        "native_result_exists": native_result.exists(),
        "cleanup_result": cleanup_result,
        "model_result": model_result,
        "plot_result": plot_result,
        "animation_result": animation_result,
    }


def nested_run_script_status(result: dict[str, Any] | None, key: str) -> bool:
    """Return the real nested run_script status, not only the MCP call status."""
    if not result:
        return False
    if not result.get("ok"):
        return False
    run_script_result = result.get("run_script_result")
    if isinstance(run_script_result, dict) and key in run_script_result:
        return bool(run_script_result.get(key))
    return bool(result.get(key))


def gui_result_status(gui_result: dict[str, Any] | None) -> dict[str, bool]:
    if not gui_result:
        return {"model": False, "plot": False, "animation": False}
    model_result = gui_result.get("model_result") or {}
    return {
        "model": bool(model_result.get("ok")),
        "plot": nested_run_script_status(gui_result.get("plot_result"), "create_plot"),
        "animation": nested_run_script_status(gui_result.get("animation_result"), "create_animation"),
    }


def run_mcp_simulation(
    args: argparse.Namespace,
    client: JsonlMcpClient,
    *,
    active_log_output: Path | None = None,
    final_log_output: Path | None = None,
) -> dict[str, Any]:
    if active_log_output is None or final_log_output is None:
        active_log_output, final_log_output = prepare_log_output(args.log_output)
        client.set_log_path(active_log_output)

    target_time = parse_target_time(args.target_time)
    if args.simulation_interval is not None and args.simulation_interval <= 0:
        raise ValueError("--simulation-interval must be greater than zero when provided")
    if args.simulation_api == "simulate_model_ex" and args.simulation_interval is not None:
        raise ValueError(
            "--simulation-interval applies only to SimulateModel; use --simulate-ex-options-json for SimulateModelEx"
        )
    variables = {"time": "time"} if args.variable_profile == "diagnostics_declared" else dict(DEFAULT_VARIABLES)
    variables.update(parse_extra_variables(args.override_variable, allow_default_override=True))
    variables.update(parse_extra_variables(args.extra_variable))
    if args.read_native_result is not None:
        return export_existing_native_result(
            args,
            client,
            variables=variables,
            active_log_output=active_log_output,
            final_log_output=final_log_output,
        )
    verify_result_var = choose_verify_result_var(args.variable_profile, variables)
    native_result_dir, native_result_manifest = resolve_native_result_dir(
        args.raw_output,
        args.native_result_dir,
        args.model_name,
    )
    native_result = native_result_file(native_result_dir, args.model_name)
    gui_result_viewer = not args.no_gui_result_viewer
    gui_open = gui_result_viewer and not args.no_gui_open
    if args.simulation_api == "simulate_model_ex" and gui_result_viewer:
        raise ValueError(
            "--simulation-api simulate_model_ex requires --no-gui-result-viewer because "
            "SimulateModelEx does not bind the diagnostic to a requested native-result path"
        )
    separate_gui_review = gui_open and (
        should_use_short_gui_review(args, target_time)
        or args.gui_review_native_result_dir is not None
        or args.gui_review_interval is not None
    )
    gui_native_result_dir = native_result_dir
    gui_native_result = native_result
    if separate_gui_review:
        gui_native_result_dir = gui_review_native_result_dir(args, native_result_dir)
        gui_native_result = native_result_file(gui_native_result_dir, args.model_name)
    if gui_result_viewer and not separate_gui_review:
        native_result_dir.mkdir(parents=True, exist_ok=True)
        native_result = prepare_native_result_target(native_result)
        write_native_result_manifest(
            native_result_manifest,
            native_result_dir=native_result_dir,
            native_result=native_result,
            model_name=args.model_name,
        )
    if separate_gui_review:
        gui_native_result_dir.mkdir(parents=True, exist_ok=True)
        gui_native_result = prepare_native_result_target(gui_native_result)
    success = False
    try:
        open_result = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": args.model_file,
                "force_reload": True,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        if not open_result.get("ok"):
            raise RuntimeError(f"Model load failed: {open_result}")

        for extra_model_file in args.extra_model_file:
            extra_open_result = client.call_tool(
                "model_manager",
                {
                    "action": "load_file",
                    "file_path": extra_model_file,
                    "force_reload": True,
                    "auto_load_deps": True,
                },
                timeout_s=300,
            )
            if not extra_open_result.get("ok"):
                raise RuntimeError(f"Extra model load failed for {extra_model_file}: {extra_open_result}")

        check_result = client.call_tool(
            "check_model",
            {"model_name": args.model_name, "stop_on_error": True},
            timeout_s=300,
        )
        if not check_result.get("ok"):
            raise RuntimeError(f"Model check failed: {check_result}")

        if args.simulation_api == "simulate_model_ex":
            sim_result = simulate_modelingpy(
                client,
                model_name=args.model_name,
                target_time=target_time,
                native_result_dir=None,
                verify_result_var=verify_result_var,
                verify_time_point="end",
                simulation_api=args.simulation_api,
                simulate_ex_options=args.simulate_ex_options,
            )
        elif gui_result_viewer and not separate_gui_review:
            sim_result = simulate_modelingpy(
                client,
                model_name=args.model_name,
                target_time=target_time,
                native_result_dir=native_result_dir,
                verify_result_var=verify_result_var,
                verify_time_point="end",
                interval=args.simulation_interval,
            )
        elif args.simulation_interval is not None:
            sim_result = simulate_modelingpy(
                client,
                model_name=args.model_name,
                target_time=target_time,
                native_result_dir=None,
                verify_result_var=verify_result_var,
                verify_time_point="end",
                interval=args.simulation_interval,
            )
        else:
            sim_result = client.call_tool(
                "simulate_model",
                {
                    "model_name": args.model_name,
                    "sim_mode": 0,
                    "target_time": target_time,
                    "verify_result_var": verify_result_var,
                    "verify_time_point": "end",
                },
                timeout_s=360,
            )
        if not sim_result.get("ok"):
            raise RuntimeError(f"Simulation failed: {sim_result}")
        if sim_result.get("simulate_api_reported_failure"):
            verification = sim_result.get("result_verification") if isinstance(sim_result.get("result_verification"), dict) else {}
            probe = verification.get("result_probe") if isinstance(verification.get("result_probe"), dict) else {}
            value_at = verification.get("get_var_value_at") if isinstance(verification.get("get_var_value_at"), dict) else {}
            readable_result = bool(probe.get("has_readable_result")) and bool(value_at.get("ok"))
            if not (args.allow_readable_result_after_simulate_false and readable_result):
                raise RuntimeError(f"Simulation API reported failure; refusing to read partial/empty result: {sim_result}")
            print(
                "Warning: SimulateModel reported false, but result API verification succeeded; "
                "continuing because --allow-readable-result-after-simulate-false was set.",
                file=sys.stderr,
            )

        result_series = read_result_series(client, args.model_name, variables)
        write_csv(result_series, variables, args.raw_output)
        write_metrics(
            args.raw_output,
            args.metrics_json,
            args.metrics_csv,
            args.scene_id,
            args.controller_id,
            args.evidence_level,
            args.metrics_profile,
        )
        gui_result: dict[str, Any] | None = None
        if gui_open:
            if separate_gui_review:
                gui_target_time = gui_review_target_time(args, target_time)
                gui_sim_result = simulate_modelingpy(
                    client,
                    model_name=args.model_name,
                    target_time=gui_target_time,
                    native_result_dir=gui_native_result_dir,
                    verify_result_var=verify_result_var,
                    verify_time_point="end",
                    interval=args.gui_review_interval,
                )
                if not gui_sim_result.get("ok"):
                    raise RuntimeError(f"GUI review simulation failed: {gui_sim_result}")
            gui_result = open_gui_result_viewer(
                client,
                native_result=gui_native_result,
                model_name=args.model_name,
                variables=variables,
                reset_windows=args.gui_reset_windows,
            )
        if active_log_output != final_log_output:
            active_log_output.replace(final_log_output)
        success = True

        print(f"MCP log: {final_log_output}")
        print(f"Raw CSV: {args.raw_output}")
        print(f"Metrics JSON: {args.metrics_json}")
        print(f"Metrics CSV: {args.metrics_csv}")
        if gui_result_viewer:
            if separate_gui_review:
                print("Native result: skipped for separate GUI review")
                print(f"GUI review native result: {gui_native_result}")
            else:
                print(f"Native result: {native_result}")
            if native_result_manifest is not None:
                print(f"Native result manifest: {native_result_manifest}")
        if gui_result is not None:
            status = gui_result_status(gui_result)
            print(f"GUI model: {status['model']}")
            print(f"GUI plot: {status['plot']}")
            print(f"GUI animation: {status['animation']}")
        print(f"Rows: {len(result_series['time'])}")
        print(f"Check model: ok")
        print(f"Simulate model: ok")
        return {
            "raw_output": args.raw_output,
            "metrics_json": args.metrics_json,
            "metrics_csv": args.metrics_csv,
            "native_result": native_result,
            "gui_native_result": gui_native_result,
            "gui_result": gui_result,
            "log_output": final_log_output,
            "rows": len(result_series["time"]),
        }
    finally:
        if not success and active_log_output != final_log_output:
            print(
                f"MCP failure log kept separate: {active_log_output}; existing log preserved: {final_log_output}",
                file=sys.stderr,
            )


def main() -> int:
    args = parse_args()
    args.simulate_ex_options = parse_simulate_ex_options(args.simulate_ex_options_json)
    if args.metrics_csv is None:
        args.metrics_csv = args.metrics_json.with_suffix(".csv")
    wrapper = resolve_wrapper(args.wrapper)
    active_log_output, final_log_output = prepare_log_output(args.log_output)
    client = JsonlMcpClient(wrapper_command(wrapper), active_log_output)
    try:
        initialize_mcp_client(client)
        run_mcp_simulation(
            args,
            client,
            active_log_output=active_log_output,
            final_log_output=final_log_output,
        )
    finally:
        if args.shutdown_session:
            try:
                shutdown = client.call_tool("session_manager", {"action": "shutdown"}, timeout_s=60)
                print(f"Shutdown: {shutdown.get('ok')}")
            except Exception as exc:
                print(f"Shutdown warning: {exc}", file=sys.stderr)
        else:
            print("Shutdown: skipped; Sysplorer GUI/session left reusable")
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
