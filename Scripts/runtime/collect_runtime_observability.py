#!/usr/bin/env python3
"""Collect same-run host and process metrics for a MoSim runtime."""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import queue
import subprocess
import time
from pathlib import Path
from typing import Any

import psutil


PROCESS_GROUPS = {
    "unreal": frozenset(("unrealeditor.exe", "mosimscenelibrary.exe")),
    "qgc": frozenset(("qgroundcontrol.exe", "flightconsole.exe")),
    "wsl_vm": frozenset(("vmmemwsl", "vmmemwsl.exe", "vmmem", "vmmem.exe")),
    "mworks_solver": frozenset(("mwsolver", "mwsolver.exe")),
}


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def counter_rates(current: Any, previous: Any, elapsed_s: float, fields: tuple[str, ...]) -> dict[str, float]:
    elapsed_s = max(elapsed_s, 1e-9)
    return {
        f"{field}_per_s": max(0.0, float(getattr(current, field) - getattr(previous, field))) / elapsed_s
        for field in fields
    }


def percentile(values: list[float], quantile: float) -> float | None:
    finite = sorted(value for value in values if math.isfinite(value))
    if not finite:
        return None
    index = min(len(finite) - 1, max(0, math.ceil(quantile * len(finite)) - 1))
    return finite[index]


def summarize(samples: list[dict[str, Any]]) -> dict[str, Any]:
    numeric: dict[str, list[float]] = {}
    for sample in samples:
        for key, value in sample["host"].items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric.setdefault(key, []).append(float(value))
    return {
        key: {
            "mean": sum(values) / len(values),
            "p95": percentile(values, 0.95),
            "max": max(values),
        }
        for key, values in sorted(numeric.items())
        if values
    }


def component_metrics(sample: dict[str, Any], name: str) -> dict[str, Any]:
    component = sample.get("components", {}).get(name, {})
    metrics = component.get("metrics") if isinstance(component, dict) else None
    return metrics if isinstance(metrics, dict) else {}


def diagnostic_findings(
    sample: dict[str, Any], host_summary: dict[str, Any], target_rate_hz: float | None
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    components = sample.get("components", {})
    control = component_metrics(sample, "mworks_ros_control")
    if components.get("mworks_ros_control", {}).get("state") != "available":
        findings.append({"priority": 1, "component": "mworks_ros_control", "code": "control_metrics_unavailable"})
    elif target_rate_hz:
        observed = control.get("transport", {}).get("command_receive_rate_hz")
        minimum = target_rate_hz * 0.99
        if isinstance(observed, (int, float)) and observed < minimum:
            findings.append({
                "priority": 1,
                "component": "mworks_ros_control",
                "code": "control_rate_below_target",
                "observed": observed,
                "threshold": minimum,
            })
        drop_rate = control.get("transport", {}).get("estimated_command_drop_rate")
        if isinstance(drop_rate, (int, float)) and drop_rate > 0.0:
            findings.append({
                "priority": 1,
                "component": "mworks_ros_control",
                "code": "control_command_loss_observed",
                "observed": drop_rate,
                "threshold": 0.0,
            })

    ros = component_metrics(sample, "ros1_topics")
    rtf = ros.get("gazebo", {}).get("clock_derived_real_time_factor")
    if isinstance(rtf, (int, float)) and rtf < 0.95:
        findings.append({
            "priority": 2,
            "component": "gazebo_runtime",
            "code": "gazebo_real_time_factor_low",
            "observed": rtf,
            "threshold": 0.95,
        })

    receiver = component_metrics(sample, "gazebo_ue_receiver")
    drop_rate = receiver.get("receiver_drop_rate")
    if isinstance(drop_rate, (int, float)) and drop_rate > 0.0:
        findings.append({
            "priority": 3,
            "component": "gazebo_ue_display",
            "code": "ue_receiver_sequence_loss_observed",
            "observed": drop_rate,
            "threshold": 0.0,
        })
    ue = component_metrics(sample, "ue_frame_timing")
    ue_fps = ue.get("ue_fps")
    if isinstance(ue_fps, (int, float)) and ue_fps < 55.0:
        findings.append({
            "priority": 3,
            "component": "unreal_renderer",
            "code": "ue_fps_low",
            "observed": ue_fps,
            "threshold": 55.0,
        })

    qgc = component_metrics(sample, "qgc_telemetry")
    qgc_loss = qgc.get("vehicle_counters", {}).get("mavlink_loss_percent")
    if isinstance(qgc_loss, (int, float)) and qgc_loss > 0.0:
        findings.append({
            "priority": 3,
            "component": "mavlink_qgc_display",
            "code": "qgc_mavlink_loss_observed",
            "observed": qgc_loss,
            "threshold": 0.0,
        })

    cpu_max = host_summary.get("cpu_total_percent", {}).get("max")
    if isinstance(cpu_max, (int, float)) and cpu_max > 90.0:
        findings.append({
            "priority": 4,
            "component": "windows_host",
            "code": "host_cpu_saturation",
            "observed": cpu_max,
            "threshold": 90.0,
        })
    memory_max = host_summary.get("memory_percent", {}).get("max")
    if isinstance(memory_max, (int, float)) and memory_max > 90.0:
        findings.append({
            "priority": 4,
            "component": "windows_host",
            "code": "host_memory_saturation",
            "observed": memory_max,
            "threshold": 90.0,
        })
    return sorted(findings, key=lambda value: (value["priority"], value["component"], value["code"]))


def build_summary(
    *, run_id: str, samples: list[dict[str, Any]], started: float, target_rate_hz: float | None
) -> dict[str, Any]:
    host_summary = summarize(samples)
    latest = samples[-1] if samples else {}
    return {
        "schema": "mosim.runtime_observability_summary.v1",
        "run_id": run_id,
        "sample_count": len(samples),
        "window_s": time.monotonic() - started,
        "target_control_rate_hz": target_rate_hz,
        "host_summary": host_summary,
        "component_states": {
            name: value["state"] for name, value in latest.get("components", {}).items()
        },
        "latest_components": latest.get("components", {}),
        "diagnostic_findings": diagnostic_findings(latest, host_summary, target_rate_hz) if latest else [],
        "diagnosis_order": ["mworks_ros_control", "gazebo_runtime", "display_links", "windows_host"],
        "claim_boundary": "Unavailable component metrics remain unavailable; host NIC totals are not per-link bandwidth.",
        "updated_at_unix": time.time(),
    }


def gpu_metrics() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=0.5, check=True)
        rows = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            utilization, used_mib, total_mib, temperature = (float(part.strip()) for part in line.split(","))
            rows.append({
                "utilization_percent": utilization,
                "memory_used_bytes": used_mib * 1024 * 1024,
                "memory_total_bytes": total_mib * 1024 * 1024,
                "temperature_c": temperature,
            })
        return {"available": bool(rows), "devices": rows}
    except (FileNotFoundError, subprocess.SubprocessError, ValueError):
        return {"available": False, "reason": "nvidia_smi_unavailable"}


def process_metrics() -> dict[str, Any]:
    groups: dict[str, dict[str, float | int]] = {
        name: {"process_count": 0, "cpu_time_s": 0.0, "resident_memory_bytes": 0}
        for name in PROCESS_GROUPS
    }
    for process in psutil.process_iter(("name",)):
        try:
            process_name = (process.info["name"] or "").lower()
            group_name = next(
                (name for name, executable_names in PROCESS_GROUPS.items() if process_name in executable_names),
                None,
            )
            if group_name is None:
                continue
            group = groups[group_name]
            group["process_count"] += 1
            cpu_times = process.cpu_times()
            group["cpu_time_s"] += cpu_times.user + cpu_times.system
            group["resident_memory_bytes"] += process.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return groups


def process_metrics_worker(output: Any) -> None:
    output.put((time.time(), process_metrics()))


class AsyncProcessGroupSampler:
    def __init__(self, minimum_interval_s: float = 5.0, worker_timeout_s: float = 2.0) -> None:
        self._minimum_interval_s = minimum_interval_s
        self._worker_timeout_s = worker_timeout_s
        self._context = multiprocessing.get_context("spawn")
        self._queue = self._context.Queue(maxsize=1)
        self._process: multiprocessing.Process | None = None
        self._latest: dict[str, Any] | None = None
        self._latest_at = 0.0
        self._previous_raw: dict[str, Any] | None = None
        self._previous_at = 0.0
        self._last_started = 0.0
        self._worker_started = 0.0
        self._worker_timeout_count = 0

    def _consume(self, observed_at: float, raw: dict[str, Any]) -> None:
        elapsed_s = observed_at - self._previous_at
        metrics: dict[str, Any] = {}
        for name, values in raw.items():
            previous = (self._previous_raw or {}).get(name, {})
            cpu_percent = None
            if elapsed_s > 0.0 and "cpu_time_s" in previous:
                cpu_percent = max(0.0, values["cpu_time_s"] - previous["cpu_time_s"]) / elapsed_s * 100.0
            metrics[name] = {
                "process_count": values["process_count"],
                "cpu_percent": cpu_percent,
                "resident_memory_bytes": values["resident_memory_bytes"],
            }
        self._previous_raw = raw
        self._previous_at = observed_at
        self._latest = metrics
        self._latest_at = observed_at

    def snapshot(self, start_if_due: bool = True) -> dict[str, Any]:
        now_monotonic = time.monotonic()
        try:
            while True:
                observed_at, raw = self._queue.get_nowait()
                self._consume(observed_at, raw)
        except queue.Empty:
            pass
        if (
            self._process is not None
            and self._process.is_alive()
            and now_monotonic - self._worker_started > self._worker_timeout_s
        ):
            self._process.terminate()
            self._process.join(timeout=0.5)
            self._process = None
            self._worker_timeout_count += 1
        if self._process is not None and not self._process.is_alive():
            self._process.join(timeout=0.0)
            self._process = None
        if (
            start_if_due
            and self._process is None
            and now_monotonic - self._last_started >= self._minimum_interval_s
        ):
            self._last_started = now_monotonic
            self._process = self._context.Process(
                target=process_metrics_worker,
                args=(self._queue,),
                name="process-group-metrics",
                daemon=True,
            )
            self._process.start()
            self._worker_started = now_monotonic
        if self._latest is None:
            return {"state": "pending", "metrics": {}, "worker_timeout_count": self._worker_timeout_count}
        return {
            "state": "available",
            "age_s": max(0.0, time.time() - self._latest_at),
            "metrics": self._latest,
            "worker_timeout_count": self._worker_timeout_count,
        }

    def close(self) -> None:
        if self._process is not None and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=0.5)
        self._process = None


def read_component_metric(path: Path, run_id: str, stale_after_s: float) -> dict[str, Any]:
    if not path.exists():
        return {"state": "unavailable", "reason": "metric_file_missing", "path": str(path)}
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"state": "invalid", "reason": type(exc).__name__, "path": str(path)}
    metric_run_id = value.get("run_id")
    if metric_run_id and metric_run_id != run_id:
        return {"state": "invalid", "reason": "run_id_mismatch", "path": str(path)}
    updated_at = value.get("updated_at_unix")
    age_s = None if not isinstance(updated_at, (int, float)) else max(0.0, time.time() - updated_at)
    return {
        "state": "stale" if age_s is not None and age_s > stale_after_s else "available",
        "age_s": age_s,
        "path": str(path),
        "metrics": value,
    }


def read_first_component_metric(paths: tuple[Path, ...], run_id: str, stale_after_s: float) -> dict[str, Any]:
    for path in paths:
        if path.exists():
            return read_component_metric(path, run_id, stale_after_s)
    return {"state": "unavailable", "reason": "metric_file_missing", "paths": [str(path) for path in paths]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--interval-s", type=float, default=1.0)
    parser.add_argument("--duration-s", type=float, default=0.0, help="Zero runs until interrupted.")
    parser.add_argument("--component-stale-after-s", type=float, default=5.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.interval_s <= 0.0 or args.duration_s < 0.0:
        raise SystemExit("invalid sampling interval or duration")
    run_dir = Path(args.run_dir).resolve()
    manifest_path = run_dir / "RUN_MANIFEST.json"
    if not manifest_path.exists():
        raise SystemExit(f"run manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("run_id") != args.run_id:
        raise SystemExit("run_id does not match RunManifest")

    output_dir = run_dir / "observability"
    output_dir.mkdir(parents=True, exist_ok=True)
    samples_path = output_dir / "host_samples.jsonl"
    summary_path = output_dir / "RUNTIME_OBSERVABILITY_SUMMARY.json"
    previous_network = psutil.net_io_counters()
    previous_network_interfaces = psutil.net_io_counters(pernic=True)
    previous_disk = psutil.disk_io_counters()
    previous_time = time.monotonic()
    psutil.cpu_percent(interval=None)
    process_group_sampler = AsyncProcessGroupSampler()
    samples: list[dict[str, Any]] = []
    started = time.monotonic()

    with samples_path.open("a", encoding="utf-8", buffering=1) as stream:
        try:
            while args.duration_s == 0.0 or time.monotonic() - started < args.duration_s:
                time.sleep(args.interval_s)
                now = time.monotonic()
                elapsed_s = now - previous_time
                network = psutil.net_io_counters()
                network_interfaces = psutil.net_io_counters(pernic=True)
                disk = psutil.disk_io_counters()
                memory = psutil.virtual_memory()
                network_rates = counter_rates(network, previous_network, elapsed_s, ("bytes_sent", "bytes_recv"))
                network_interface_rates = {
                    name: counter_rates(counters, previous_network_interfaces[name], elapsed_s, ("bytes_sent", "bytes_recv"))
                    for name, counters in network_interfaces.items()
                    if name in previous_network_interfaces
                }
                disk_rates = {} if disk is None or previous_disk is None else counter_rates(
                    disk, previous_disk, elapsed_s, ("read_bytes", "write_bytes")
                )
                sample = {
                    "schema": "mosim.runtime_observability_sample.v1",
                    "run_id": args.run_id,
                    "sequence": len(samples),
                    "monotonic_s": now,
                    "unix_time": time.time(),
                    "host": {
                        "cpu_total_percent": psutil.cpu_percent(interval=None),
                        "memory_used_bytes": memory.used,
                        "memory_available_bytes": memory.available,
                        "memory_percent": memory.percent,
                        **network_rates,
                        **disk_rates,
                    },
                    "process_groups": process_group_sampler.snapshot(start_if_due=False),
                    "network_interfaces": network_interface_rates,
                    "gpu": gpu_metrics(),
                    "components": {
                        "mworks_ros_control": read_first_component_metric(
                            (output_dir / "RT1_STATUS.json", run_dir / "RT1_STATUS.json"),
                            args.run_id,
                            args.component_stale_after_s,
                        ),
                        "gazebo_ue_sender": read_component_metric(
                            output_dir / "gazebo_ue_sender.json", args.run_id, args.component_stale_after_s
                        ),
                        "gazebo_ue_receiver": read_component_metric(
                            output_dir / "gazebo_ue_receiver.json", args.run_id, args.component_stale_after_s
                        ),
                        "ue_frame_timing": read_component_metric(
                            output_dir / "ue_frame_timing.json", args.run_id, args.component_stale_after_s
                        ),
                        "ros1_topics": read_component_metric(
                            output_dir / "ros1_topics.json", args.run_id, args.component_stale_after_s
                        ),
                        "qgc_telemetry": read_component_metric(
                            output_dir / "mavlink_qgc.json", args.run_id, args.component_stale_after_s
                        ),
                    },
                }
                stream.write(json.dumps(sample, separators=(",", ":")) + "\n")
                samples.append(sample)
                target_rate = manifest.get("mworks_live_connection", {}).get("selected_rate_hz")
                atomic_json(
                    summary_path,
                    build_summary(
                        run_id=args.run_id,
                        samples=samples,
                        started=started,
                        target_rate_hz=float(target_rate) if isinstance(target_rate, (int, float)) else None,
                    ),
                )
                process_group_sampler.snapshot()
                previous_network = network
                previous_network_interfaces = network_interfaces
                previous_disk, previous_time = disk, now
        except KeyboardInterrupt:
            pass
    process_group_sampler.close()

    target_rate = manifest.get("mworks_live_connection", {}).get("selected_rate_hz")
    summary = build_summary(
        run_id=args.run_id,
        samples=samples,
        started=started,
        target_rate_hz=float(target_rate) if isinstance(target_rate, (int, float)) else None,
    )
    atomic_json(summary_path, summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
