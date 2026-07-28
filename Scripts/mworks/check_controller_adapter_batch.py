#!/usr/bin/env python3
"""Run a non-saving native CheckModel batch for controller bridges/adapters.

This is the reusable G1 structural-integrity gate. It loads the canonical
MoSimQuadrotorModel root once, checks the explicitly named classes, records
raw MCP traffic, and verifies that the check did not modify the source files.
It deliberately does not simulate, save models, rank controllers, or produce
closed-loop evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
MODEL_FILE = MODEL_ROOT / "package.mo"
ALLOWED_MCP_TOOLS = frozenset({"session_manager", "model_manager", "check_model"})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def normalize_lf(path: Path) -> None:
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def parse_target(kind: str, raw: list[str]) -> dict[str, str]:
    source = (ROOT / raw[0]).resolve()
    try:
        source.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"target_source_outside_project:{raw[0]}") from exc
    if not source.is_file():
        raise ValueError(f"target_source_missing:{raw[0]}")
    model_class = raw[1].strip()
    if not model_class.startswith("MoSimQuadrotorModel.Control."):
        raise ValueError(f"target_class_outside_control_namespace:{model_class}")
    return {"kind": kind, "source": repo_path(source), "model_class": model_class}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Human-readable batch identifier")
    parser.add_argument("--output-dir", required=True, type=Path, help="Project-relative evidence directory")
    parser.add_argument("--wrapper", help="Override the local Sysplorer MCP wrapper")
    parser.add_argument("--timeout-s", type=float, default=300.0)
    parser.add_argument(
        "--bridge",
        action="append",
        nargs=2,
        metavar=("SOURCE", "MODEL_CLASS"),
        default=[],
    )
    parser.add_argument(
        "--adapter",
        action="append",
        nargs=2,
        metavar=("SOURCE", "MODEL_CLASS"),
        default=[],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = [parse_target("bridge", item) for item in args.bridge]
    targets.extend(parse_target("adapter", item) for item in args.adapter)
    if not targets:
        raise SystemExit("at_least_one_bridge_or_adapter_required")
    if len({item["model_class"] for item in targets}) != len(targets):
        raise SystemExit("duplicate_model_class")

    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"output_dir_outside_project:{output_dir}") from exc
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    import run_sysplorer_mcp_smoke as mcp  # type: ignore

    tracked_paths = [
        MODEL_FILE,
        MODEL_ROOT / "Control" / "Bridges" / "package.order",
        MODEL_ROOT / "Control" / "Adapters" / "package.order",
        *(ROOT / item["source"] for item in targets),
    ]
    hashes_before = {repo_path(path): sha256(path) for path in tracked_paths}
    log_path = output_dir / "SYSPLORER_MCP_CHECK_ONLY.jsonl"
    summary_path = output_dir / "CHECK_MODEL_RESULTS.json"
    log_path.write_text("", encoding="utf-8")
    started_at = time.time()
    record: dict[str, Any] = {
        "schema": "mosim.g1_batch_checkmodel.v1",
        "batch": args.batch,
        "scope": "Native CheckModel only; no solver simulation, model save, controller performance claim, code generation, or runtime validation.",
        "model_root": repo_path(MODEL_FILE),
        "targets": [],
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "simulation_started": False,
        "allowed_mcp_tools": sorted(ALLOWED_MCP_TOOLS),
        "raw_mcp_log": repo_path(log_path),
        "source_hashes_before": hashes_before,
        "status": "running",
    }
    client: Any | None = None
    exit_code = 1
    try:
        resolved_wrapper = mcp.resolve_wrapper(args.wrapper)
        record["wrapper"] = resolved_wrapper
        client = mcp.JsonlMcpClient(mcp.wrapper_command(resolved_wrapper), log_path)
        record["mcp_initialize"] = mcp.initialize_mcp_client(client)
        record["load_root"] = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": mcp.windows_path(MODEL_FILE),
                "force_reload": True,
                "auto_load_deps": True,
            },
            timeout_s=args.timeout_s,
        )
        for target in targets:
            check_started_at = time.perf_counter()
            try:
                response = client.call_tool(
                    "check_model",
                    {"model_name": target["model_class"], "stop_on_error": True},
                    timeout_s=args.timeout_s,
                )
                passed = bool(response.get("ok"))
                error = None if passed else json.dumps(response, ensure_ascii=True)
            except Exception as exc:
                response = None
                passed = False
                error = repr(exc)
            record["targets"].append(
                {
                    **target,
                    "status": "passed" if passed else "failed",
                    "elapsed_s": round(time.perf_counter() - check_started_at, 3),
                    "error": error,
                    "mcp_response": response,
                }
            )
        load_ok = bool(record["load_root"].get("ok"))
        passed_count = sum(item["status"] == "passed" for item in record["targets"])
        record["passed_count"] = passed_count
        record["failed_count"] = len(record["targets"]) - passed_count
        record["status"] = "passed" if load_ok and record["failed_count"] == 0 else "failed"
        exit_code = 0 if record["status"] == "passed" else 1
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
    finally:
        if client is not None:
            client.close()
        normalize_lf(log_path)
        record["source_hashes_after"] = {repo_path(path): sha256(path) for path in tracked_paths}
        record["source_changed_by_check"] = record["source_hashes_before"] != record["source_hashes_after"]
        record["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record["elapsed_s"] = round(time.time() - started_at, 3)
        write_json(summary_path, record)

    print(
        json.dumps(
            {
                "batch": args.batch,
                "status": record["status"],
                "passed_count": record.get("passed_count", 0),
                "failed_count": record.get("failed_count", len(targets)),
                "summary": repo_path(summary_path),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
