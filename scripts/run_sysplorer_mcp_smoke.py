#!/usr/bin/env python3
"""Run a short official QuadrotorModel simulation through Sysplorer MCP.

This script is intentionally narrow: it proves the real MWORKS/Sysplorer MCP
path for the official Example1 PID model without using offline generated data.
Outputs are project-local and labeled as MCP evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from calc_metrics import compute_metrics


DEFAULT_WRAPPER = "/home/linux/mcp-wrappers/sysplorer_mcp.sh"
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
}


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
    row_count = len(series[0])
    if any(len(item) != row_count for item in series):
        raise ValueError("MCP result series lengths are inconsistent")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        for index in range(row_count):
            writer.writerow([series[column_index][index] for column_index in range(len(names))])


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wrapper", default=DEFAULT_WRAPPER)
    parser.add_argument("--model-file", default=DEFAULT_MODEL_FILE)
    parser.add_argument(
        "--extra-model-file",
        action="append",
        default=[],
        help="Additional Modelica package file to load after --model-file. Can be repeated.",
    )
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--target-time", default="0,1", help="Comma-separated simulation target time range")
    parser.add_argument("--raw-output", type=Path, default=Path("results/raw/mworks_mcp_example1_pid_smoke.csv"))
    parser.add_argument("--metrics-json", type=Path, default=Path("results/metrics/mworks_mcp_example1_pid_smoke.json"))
    parser.add_argument("--metrics-csv", type=Path, default=Path("results/metrics/mworks_mcp_example1_pid_smoke.csv"))
    parser.add_argument("--log-output", type=Path, default=Path("results/test_reports/sysplorer_example1_pid_mcp_smoke_20260509.jsonl"))
    parser.add_argument("--scene-id", default="mworks_mcp_example1")
    parser.add_argument("--controller-id", default="pid_baseline")
    parser.add_argument("--evidence-level", default="real_sysplorer_mcp_smoke")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_time = [float(item.strip()) for item in args.target_time.split(",") if item.strip()]
    args.log_output.parent.mkdir(parents=True, exist_ok=True)
    args.log_output.write_text("", encoding="utf-8")

    client = JsonlMcpClient([args.wrapper], args.log_output)
    try:
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
                "var_names": list(DEFAULT_VARIABLES.values()),
            },
            timeout_s=240,
        )
        if not read_result.get("ok"):
            raise RuntimeError(f"Result read failed: {read_result}")

        write_csv(read_result["data"], DEFAULT_VARIABLES, args.raw_output)
        write_metrics(
            args.raw_output,
            args.metrics_json,
            args.metrics_csv,
            args.scene_id,
            args.controller_id,
            args.evidence_level,
        )

        print(f"MCP log: {args.log_output}")
        print(f"Raw CSV: {args.raw_output}")
        print(f"Metrics JSON: {args.metrics_json}")
        print(f"Metrics CSV: {args.metrics_csv}")
        print(f"Rows: {len(read_result['data'][0])}")
        print(f"Check model: ok")
        print(f"Simulate model: ok")
    finally:
        try:
            shutdown = client.call_tool("session_manager", {"action": "shutdown"}, timeout_s=60)
            print(f"Shutdown: {shutdown.get('ok')}")
        except Exception as exc:
            print(f"Shutdown warning: {exc}", file=sys.stderr)
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
