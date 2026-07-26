#!/usr/bin/env python3
"""Run one non-saving G5 CheckModel against the current Sysplorer session.

The helper deliberately opens only the requested current model, never calls a
save API, and records hashes before and after the live operation.  Layout and
native-window acceptance remain separate review steps.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def import_modeling_py() -> Any:
    """Load the official API, relaunching once with MWORKS Python if needed."""

    try:
        import mworks.sysplorer as modeling_py

        return modeling_py
    except ModuleNotFoundError as exc:
        if exc.name != "mworks" or os.environ.get("MOSIM_G5_MWORKS_PYTHON") == "1":
            raise
        configured = os.environ.get("MWORKS_SYSPLORE_PYTHON", "").strip()
        candidate = Path(configured) if configured else Path(
            r"D:\Program Files\MWORKS\Sysplorer 2026a\External\python64\python.exe"
        )
        if not candidate.is_file():
            raise RuntimeError(
                "MWORKS Python is required for live G5 checks. Set "
                "MWORKS_SYSPLORE_PYTHON to the official Sysplorer Python executable."
            ) from exc
        environment = os.environ.copy()
        environment["MOSIM_G5_MWORKS_PYTHON"] = "1"
        completed = subprocess.run([str(candidate), str(Path(__file__).resolve()), *sys.argv[1:]], env=environment)
        raise SystemExit(completed.returncode)


ModelingPy = import_modeling_py()


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import model_topology_sha256


ROOT = Path(__file__).resolve().parents[2]


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def last_errors() -> list[str]:
    try:
        return [str(value) for value in ModelingPy.GetLastErrors()]
    except Exception as exc:
        return [f"GetLastErrors failed: {exc}"]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_existing_sysplorer_port(requested_port: int | None) -> int:
    """Use an explicit port when supplied, otherwise discover a reusable GUI."""

    if requested_port is not None:
        return requested_port
    # FindSysplorer writes a localized status line to stdout.  Keep the JSON
    # evidence stream clean while still using the official discovery API.
    with contextlib.redirect_stdout(io.StringIO()):
        ports = ModelingPy.FindSysplorer()
    candidates = [int(port) for port in ports if isinstance(port, (int, str)) and str(port).isdigit()]
    if not candidates:
        raise RuntimeError("FindSysplorer found no reusable Sysplorer port")
    return candidates[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-file", required=True, type=Path, help="Project-relative current .mo source")
    parser.add_argument("--model-class", required=True, help="Fully-qualified MWORKS model class")
    parser.add_argument("--output", required=True, type=Path, help="Project-relative JSON evidence path")
    parser.add_argument("--port", type=int, help="Existing Sysplorer API port; defaults to official live-session discovery")
    args = parser.parse_args(argv)

    model_file = (ROOT / args.model_file).resolve()
    output = (ROOT / args.output).resolve()
    try:
        model_file.relative_to(ROOT)
        output.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"path escapes project root: {exc}") from exc
    if not model_file.is_file():
        raise SystemExit(f"model file does not exist: {model_file}")

    port = resolve_existing_sysplorer_port(args.port)
    record: dict[str, Any] = {
        "schema": "mosim.g5_live_model_check.v1",
        "scope": "One current-source MWORKS CheckModel only. This record does not claim layout acceptance, simulation, controller behavior, code generation, runtime, or closed loop.",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "model_file": repo_path(model_file),
        "model_class": args.model_class,
        "existing_sysplorer": {
            "host": "127.0.0.1",
            "port": port,
            "port_selection": "explicit" if args.port is not None else "FindSysplorer",
        },
        "will_start_sysplorer": False,
        "will_save_model": False,
        "model_sha256_before": sha256(model_file),
        "model_topology_sha256_before": model_topology_sha256(model_file),
        "steps": {},
    }
    succeeded = False
    try:
        ModelingPy.ConnectSysplorer("127.0.0.1", port)
        record["steps"]["connect_existing_sysplorer"] = {"status": "passed"}

        root_class = args.model_class.split(".", 1)[0]
        root_loaded = bool(ModelingPy.ClassExist(root_class))
        if root_loaded:
            erased = bool(ModelingPy.EraseClasses((root_class,)))
            record["steps"]["erase_previous_root"] = {
                "status": "passed" if erased else "failed",
                "root_class": root_class,
            }
            if not erased:
                raise RuntimeError(f"EraseClasses failed: {last_errors()}")
        else:
            record["steps"]["erase_previous_root"] = {
                "status": "not_needed",
                "root_class": root_class,
                "reason": "root_not_loaded_in_fresh_sysplorer_session",
            }

        loaded = bool(ModelingPy.OpenModelFile(str(model_file)))
        record["steps"]["open_model_file"] = {"status": "passed" if loaded else "failed"}
        if not loaded:
            raise RuntimeError(f"OpenModelFile failed: {last_errors()}")

        exists = bool(ModelingPy.ClassExist(args.model_class))
        record["steps"]["class_exists"] = {"status": "passed" if exists else "failed"}
        if not exists:
            raise RuntimeError(f"model class did not load: {last_errors()}")

        opened = bool(ModelingPy.OpenModel(args.model_class, "diagram"))
        record["steps"]["open_diagram"] = {"status": "passed" if opened else "failed"}
        if not opened:
            raise RuntimeError(f"OpenModel diagram failed: {last_errors()}")

        started = time.perf_counter()
        checked = bool(ModelingPy.CheckModel(args.model_class))
        elapsed_s = round(time.perf_counter() - started, 3)
        record["steps"]["check_model"] = {
            "status": "passed" if checked else "failed",
            "elapsed_s": elapsed_s,
            "last_errors": last_errors(),
        }
        if not checked:
            raise RuntimeError(f"CheckModel failed: {last_errors()}")
        succeeded = True
    except Exception as exc:
        record["error"] = str(exc)
        record["last_errors"] = last_errors()
    finally:
        record["model_sha256_after"] = sha256(model_file)
        record["model_topology_sha256_after"] = model_topology_sha256(model_file)
        record["model_file_changed_by_live_operation"] = record["model_sha256_before"] != record["model_sha256_after"]
        record["model_topology_changed_by_live_operation"] = (
            record["model_topology_sha256_before"] != record["model_topology_sha256_after"]
        )
        record["status"] = "passed" if succeeded else "failed"
        write_json(output, record)

    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
