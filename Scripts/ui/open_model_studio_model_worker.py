#!/usr/bin/env python3
"""Load a complete Model Studio model context through MWORKS ModelingPy."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy
import psutil


def last_errors() -> str:
    try:
        return str(ModelingPy.GetLastErrors())
    except Exception as exc:
        return f"GetLastErrors failed: {exc}"


def write_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mworks-exe", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--model-file", action="append", default=[])
    parser.add_argument("--result-path", type=Path, required=True)
    parser.add_argument("--check-model", action="store_true")
    args = parser.parse_args()

    result: dict[str, Any] = {
        "schema": "mosim.model_studio.model_load_worker.v1",
        "model_name": args.model_name,
        "model_files": args.model_file,
        "started": False,
        "loaded": [],
        "class_exists": False,
        "model_opened": False,
        "check_model": None,
    }
    try:
        before_pids = {process.pid for process in psutil.process_iter(["name"]) if process.info["name"] == "mworks.exe"}
        ModelingPy.StartSysplorer(start_mode="-gui", processPath=args.mworks_exe)
        result["started"] = True
        after_pids = {process.pid for process in psutil.process_iter(["name"]) if process.info["name"] == "mworks.exe"}
        result["mworks_process_ids"] = sorted(after_pids - before_pids)
        for value in args.model_file:
            loaded = bool(ModelingPy.OpenModelFile(value))
            result["loaded"].append({"path": value, "ok": loaded})
            if not loaded:
                raise RuntimeError(f"OpenModelFile failed: {value}; {last_errors()}")

        result["class_exists"] = bool(ModelingPy.ClassExist(args.model_name))
        if not result["class_exists"]:
            raise RuntimeError(f"model class not loaded: {args.model_name}; {last_errors()}")

        result["model_opened"] = bool(
            ModelingPy.OpenModel(args.model_name, ModelingPy.ModelView.Diagram)
        )
        if not result["model_opened"]:
            raise RuntimeError(f"OpenModel failed: {args.model_name}; {last_errors()}")

        if args.check_model:
            result["check_model"] = bool(ModelingPy.CheckModel(args.model_name))
            if not result["check_model"]:
                raise RuntimeError(f"CheckModel failed: {args.model_name}; {last_errors()}")
    except Exception as exc:
        result["error"] = str(exc)
        result["last_errors"] = last_errors()
        write_result(args.result_path, result)
        return 1

    write_result(args.result_path, result)
    # ModelingPy owns the loaded class context. Keep the worker connected until
    # the dedicated Sysplorer process closes so the manually operated model
    # remains checkable and simulatable after the APP command returns.
    tracked_pids = result["mworks_process_ids"]
    while any(psutil.pid_exists(pid) for pid in tracked_pids):
        time.sleep(1.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
