#!/usr/bin/env python3
"""Run an official QuadrotorModel simulation through Sysplorer MCP.

The script writes project-local raw CSV, metrics, and MCP JSONL evidence.
By default it keeps the Windows Sysplorer GUI/session reusable between runs to
avoid repeated startup cost. Pass --shutdown-session only when explicit cleanup
is needed.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from calc_metrics import compute_metrics


def default_wrapper_candidates() -> list[str]:
    """Return known Sysplorer MCP wrapper locations for WSL and Windows shells."""
    home = Path.home()
    project_root = Path(__file__).resolve().parents[1]
    names = ["sysplorer_mcp.sh", "sysplorer_mcp.bat", "sysplorer_mcp.cmd", "sysplorer_mcp.ps1"]
    raw_candidates = []
    if os.name != "nt":
        raw_candidates.append(str(project_root / "scripts" / "sysplorer_mcp_wsl_bridge.sh"))
    raw_candidates.append("/home/linux/mcp-wrappers/sysplorer_mcp.sh")
    raw_candidates.extend(str(home / "mcp-wrappers" / name) for name in names)
    if os.name == "nt":
        raw_candidates.extend(str(project_root / "mcp-wrappers" / name) for name in names)
    candidates: list[str] = []
    seen: set[str] = set()
    for candidate in raw_candidates:
        if candidate not in seen:
            seen.add(candidate)
            candidates.append(candidate)
    return candidates


DEFAULT_WRAPPER_CANDIDATES = default_wrapper_candidates()
DEFAULT_MODEL_FILE = r"C:\Users\HP\Desktop\Quadrotor\QuadrotorModel\package.mo"
DEFAULT_MODEL_NAME = "QuadrotorModel.Examples.Example1"
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


def parse_extra_variables(items: list[str]) -> dict[str, str]:
    variables: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Extra variable must use alias=model.variable syntax: {item}")
        alias, model_var = item.split("=", 1)
        alias = alias.strip()
        model_var = model_var.strip()
        if not alias or not model_var:
            raise ValueError(f"Extra variable must use alias=model.variable syntax: {item}")
        if alias in DEFAULT_VARIABLES or alias in variables:
            raise ValueError(f"Duplicate result variable alias: {alias}")
        variables[alias] = model_var
    return variables


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


def write_csv(series: list[list[float]], variables: dict[str, str], output: Path) -> None:
    names = list(variables)
    if len(series) < len(names):
        raise ValueError(f"Expected {len(names)} series, got {len(series)}")
    if not series or not series[0]:
        raise ValueError("MCP result series is empty; refusing to overwrite raw CSV")
    row_count = len(series[0])
    if row_count <= 0:
        raise ValueError("MCP result series has zero rows; refusing to overwrite raw CSV")
    if any(len(item) != row_count for item in series):
        raise ValueError("MCP result series lengths are inconsistent")

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_suffix(output.suffix + ".tmp")
    with temp_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        for index in range(row_count):
            writer.writerow([series[column_index][index] for column_index in range(len(names))])
    temp_output.replace(output)


def write_metrics(
    raw_csv: Path,
    metrics_json: Path,
    metrics_csv: Path,
    scene_id: str,
    controller_id: str,
    evidence_level: str,
) -> None:
    from calc_metrics import read_csv as read_project_csv

    data = read_project_csv(raw_csv)
    metrics = compute_metrics(data, raw_csv, scene_id, controller_id)
    metrics["source"] = "MWORKS_MCP"
    metrics["evidence_level"] = evidence_level
    metrics_json.parent.mkdir(parents=True, exist_ok=True)
    metrics_json.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    metrics_csv.parent.mkdir(parents=True, exist_ok=True)
    with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, "" if value is None else value])


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wrapper",
        default=os.environ.get("SYSPLORER_MCP_WRAPPER"),
        help=(
            "Sysplorer MCP wrapper path. Defaults to SYSPLORER_MCP_WRAPPER, "
            "/home/linux/mcp-wrappers/sysplorer_mcp.sh, then ~/mcp-wrappers/sysplorer_mcp.{sh,bat,cmd,ps1}."
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
    parser.add_argument("--raw-output", type=Path, default=Path("results/official/example1_step/official_example1_pid_baseline/raw/official_example1_pid_baseline.csv"))
    parser.add_argument("--metrics-json", type=Path, default=Path("results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.json"))
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.csv"))
    parser.add_argument("--log-output", type=Path, default=Path("results/official/example1_step/official_example1_pid_baseline/logs/sysplorer_example1_pid_baseline_full.jsonl"))
    parser.add_argument(
        "--native-result-dir",
        type=Path,
        default=None,
        help="Directory for Sysplorer native result files used by GUI result viewer and animation",
    )
    parser.add_argument("--scene-id", default="official_example1_pid_baseline")
    parser.add_argument("--controller-id", default="pid_baseline")
    parser.add_argument("--evidence-level", default="real_sysplorer_mcp_full_baseline")
    parser.add_argument(
        "--extra-variable",
        action="append",
        default=[],
        help="Additional result variable as alias=model.variable. Can be repeated.",
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


def native_result_file(native_result_dir: Path, model_name: str) -> Path:
    leaf_name = model_name.rsplit(".", 1)[-1]
    return native_result_dir / leaf_name / "Result.msr"


def open_gui_result_viewer(
    client: JsonlMcpClient,
    *,
    native_result: Path,
    model_name: str,
    variables: dict[str, str],
) -> dict[str, Any]:
    result_file = windows_path(native_result)
    try:
        model_result = client.call_tool(
            "model_manager",
            {"action": "open", "model_name": model_name},
            timeout_s=30,
        )
    except Exception as exc:
        model_result = {"ok": False, "warning": f"gui_model_open_failed: {exc}"}

    plot_vars = [
        variables.get("z", "sensors1_1.PosMea[3]"),
        variables.get("z_ref", "climbePath.position_command[3]"),
        variables.get("x", "sensors1_1.PosMea[1]"),
        variables.get("x_ref", "climbePath.position_command[1]"),
    ]
    plot_vars = [item for index, item in enumerate(plot_vars) if item and item not in plot_vars[:index]]
    try:
        plot_result = client.call_tool(
            "plot_manager",
            {
                "action": "plot_variables",
                "variables": plot_vars,
                "heading": f"{model_name} tracking",
                "clear_first": False,
            },
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
            timeout_s=15,
        )
    except Exception as exc:
        animation_result = {"ok": False, "warning": f"gui_animation_failed: {exc}"}

    return {
        "native_result_file": result_file,
        "native_result_exists": native_result.exists(),
        "model_result": model_result,
        "plot_result": plot_result,
        "animation_result": animation_result,
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
    variables = dict(DEFAULT_VARIABLES)
    variables.update(parse_extra_variables(args.extra_variable))
    native_result_dir = args.native_result_dir or default_native_result_dir(args.raw_output)
    native_result = native_result_file(native_result_dir, args.model_name)
    gui_result_viewer = not args.no_gui_result_viewer
    if gui_result_viewer:
        native_result_dir.mkdir(parents=True, exist_ok=True)
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

        sim_result = client.call_tool(
            "simulate_model",
            {
                "model_name": args.model_name,
                "sim_mode": 0,
                "target_time": target_time,
                **({"ext_res_path": windows_path(native_result_dir)} if gui_result_viewer else {}),
                "verify_result_var": "sensors1_1.PosMea[3]",
                "verify_time_point": "end",
            },
            timeout_s=360,
        )
        if not sim_result.get("ok"):
            raise RuntimeError(f"Simulation failed: {sim_result}")

        read_result = client.call_tool(
            "result_manager",
            {
                "action": "get_vars_values",
                "model_name": args.model_name,
                "var_names": list(variables.values()),
            },
            timeout_s=240,
        )
        if not read_result.get("ok"):
            raise RuntimeError(f"Result read failed: {read_result}")

        write_csv(read_result["data"], variables, args.raw_output)
        write_metrics(
            args.raw_output,
            args.metrics_json,
            args.metrics_csv,
            args.scene_id,
            args.controller_id,
            args.evidence_level,
        )
        gui_result: dict[str, Any] | None = None
        if gui_result_viewer:
            gui_result = open_gui_result_viewer(
                client,
                native_result=native_result,
                model_name=args.model_name,
                variables=variables,
            )
        if active_log_output != final_log_output:
            active_log_output.replace(final_log_output)
        success = True

        print(f"MCP log: {final_log_output}")
        print(f"Raw CSV: {args.raw_output}")
        print(f"Metrics JSON: {args.metrics_json}")
        print(f"Metrics CSV: {args.metrics_csv}")
        if gui_result_viewer:
            print(f"Native result: {native_result}")
        if gui_result is not None:
            print(f"GUI model: {gui_result['model_result'].get('ok')}")
            print(f"GUI plot: {gui_result['plot_result'].get('ok')}")
            print(f"GUI animation: {gui_result['animation_result'].get('ok')}")
        print(f"Rows: {len(read_result['data'][0])}")
        print(f"Check model: ok")
        print(f"Simulate model: ok")
        return {
            "raw_output": args.raw_output,
            "metrics_json": args.metrics_json,
            "metrics_csv": args.metrics_csv,
            "native_result": native_result,
            "gui_result": gui_result,
            "log_output": final_log_output,
            "rows": len(read_result["data"][0]),
        }
    finally:
        if not success and active_log_output != final_log_output:
            print(
                f"MCP failure log kept separate: {active_log_output}; existing log preserved: {final_log_output}",
                file=sys.stderr,
            )


def main() -> int:
    args = parse_args()
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
