#!/usr/bin/env python3
"""Run the fail-closed MWORKS Sysplorer RT0 external-I/O capability gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = ROOT / "Models/MoSimQuadrotorModel/LiveIntegration/package.mo"
CLIENT = ROOT / "Scripts/mworks_live/run_rt0_probe_client.py"
ANALYZER = ROOT / "Scripts/mworks_live/analyze_rt0_trace.py"
DEFAULT_OUTPUT = ROOT / "Results/control_platform/mworks_live_full_loop_20260719/rt0"
RATE_CONFIG = {
    50: {
        "model_name": "MoSimQuadrotorModel.LiveIntegration.RT0RealtimeProbe50Hz",
        "model_source": ROOT / "Models/MoSimQuadrotorModel/LiveIntegration/RT0RealtimeProbe50Hz.mo",
        "contract": ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v1.json",
        "sim_stop_time": 22.0,
        "frequency_profile": "attitude_thrust_50hz_v1",
    },
    200: {
        "model_name": "MoSimQuadrotorModel.LiveIntegration.RT0RealtimeProbe200Hz",
        "model_source": ROOT / "Models/MoSimQuadrotorModel/LiveIntegration/RT0RealtimeProbe200Hz.mo",
        "contract": ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v3_candidate_200hz.json",
        "sim_stop_time": 12.0,
        "frequency_profile": "attitude_thrust_200hz_candidate_v2",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def call_ok(client: Any, tool: str, arguments: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    response = client.call_tool(tool, arguments, timeout_s=timeout_s)
    if not response.get("ok"):
        raise RuntimeError(f"{tool} failed: {response}")
    return response


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wrapper", type=Path)
    parser.add_argument("--client-duration-s", type=float, default=30.0)
    parser.add_argument("--rate-hz", type=int, choices=sorted(RATE_CONFIG), default=50)
    args = parser.parse_args()
    rate_config = RATE_CONFIG[args.rate_hz]
    model_name = str(rate_config["model_name"])
    model_source = Path(rate_config["model_source"])
    contract = Path(rate_config["contract"])
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    trace = output / "rt0_trace.jsonl"
    capture_summary = output / "rt0_capture.json"
    analysis = output / "rt0_analysis.json"
    invocation = output / "rt0_invocation.json"
    mcp_log = output / "sysplorer_mcp.jsonl"
    client_stdout = output / "probe_client.stdout.log"
    client_stderr = output / "probe_client.stderr.log"

    sys.path.insert(0, str(ROOT / "Scripts/mworks"))
    import run_sysplorer_mcp_smoke as mcp  # type: ignore

    started = time.time()
    record: dict[str, Any] = {
        "schema": "mosim.mworks_live_rt0_invocation.v1",
        "status": "running",
        "model_name": model_name,
        "model_file": MODEL_FILE.relative_to(ROOT).as_posix(),
        "model_sha256": sha256(MODEL_FILE),
        "model_source": model_source.relative_to(ROOT).as_posix(),
        "model_source_sha256": sha256(model_source),
        "contract": contract.relative_to(ROOT).as_posix(),
        "contract_sha256": sha256(contract),
        "requested_rate_hz": args.rate_hz,
        "sim_mode": 2,
        "started_at_unix": started,
        "execution_source": "mworks_sysplorer_realtime",
    }
    write_json(invocation, record)

    wrapper = mcp.resolve_wrapper(args.wrapper)
    client = mcp.JsonlMcpClient(mcp.wrapper_command(wrapper), mcp_log)
    probe: subprocess.Popen[str] | None = None
    stdout_handle = client_stdout.open("w", encoding="utf-8")
    stderr_handle = client_stderr.open("w", encoding="utf-8")
    try:
        record["mcp_health"] = mcp.initialize_mcp_client(client)
        record["load"] = call_ok(
            client,
            "model_manager",
            {
                "action": "load_file",
                "file_path": str(MODEL_FILE),
                "force_reload": True,
                "auto_load_deps": True,
            },
            300,
        )
        record["check"] = call_ok(
            client,
            "check_model",
            {"model_name": model_name, "stop_on_error": True},
            300,
        )
        # Compile/cache the external function before timing starts. This run is
        # intentionally excluded from RT0 evidence.
        record["warmup"] = call_ok(
            client,
            "simulate_model",
            {
                "model_name": model_name,
                "sim_mode": 0,
                "target_time": [0.0, 0.1],
                "verify_result_var": "processedFrames",
                "verify_time_point": "end",
            },
            360,
        )
        probe = subprocess.Popen(
            [
                sys.executable,
                str(CLIENT),
                "--duration-s",
                str(args.client_duration_s),
                "--rate-hz",
                str(args.rate_hz),
                "--minimum-responses",
                "1000",
                "--trace",
                str(trace),
                "--summary",
                str(capture_summary),
            ],
            cwd=ROOT,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
        )
        time.sleep(0.2)
        record["realtime"] = call_ok(
            client,
            "simulate_model",
            {
                "model_name": model_name,
                "sim_mode": 2,
                "target_time": [0.0, float(rate_config["sim_stop_time"])],
                "verify_result_var": "processedFrames",
                "verify_time_point": "end",
            },
            360,
        )
        probe_code = probe.wait(timeout=args.client_duration_s + 5.0)
        record["probe_client_return_code"] = probe_code
        analyzer = subprocess.run(
            [
                sys.executable,
                str(ANALYZER),
                str(trace),
                "--contract",
                str(contract),
                "--frequency-profile",
                str(rate_config["frequency_profile"]),
                "--capture-summary",
                str(capture_summary),
                "--json-out",
                str(analysis),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        record["analyzer_return_code"] = analyzer.returncode
        record["analyzer_stdout"] = analyzer.stdout
        record["analyzer_stderr"] = analyzer.stderr
        accepted = probe_code == 0 and analyzer.returncode == 0
        record["status"] = "passed" if accepted else "failed"
        return_code = 0 if accepted else 2
    except Exception as exc:
        record["status"] = "blocked"
        record["reason_code"] = "rt0_runtime_exception"
        record["detail"] = repr(exc)
        return_code = 3
    finally:
        if probe is not None and probe.poll() is None:
            probe.terminate()
            try:
                probe.wait(timeout=3)
            except subprocess.TimeoutExpired:
                probe.kill()
        stdout_handle.close()
        stderr_handle.close()
        client.close()
        record["completed_at_unix"] = time.time()
        record["elapsed_s"] = record["completed_at_unix"] - started
        write_json(invocation, record)
    print(json.dumps({"status": record["status"], "invocation": str(invocation), "analysis": str(analysis)}, indent=2))
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
