#!/usr/bin/env python3
"""Execute one allowlisted Model Studio MWORKS operation for an existing run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "Results" / "ui_platform" / "orchestrator_runs"
CATALOG_PATH = ROOT / "Config" / "control_platform" / "model_operation_catalog.json"
RUN_ID_PATTERN = re.compile(r"^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
OPERATION_ID_PATTERN = re.compile(r"^op-[a-f0-9]{16}$")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def project_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("catalog_path_outside_project")
    return path


def portable(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_entry(manifest: dict[str, Any], action: str) -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = read_json(CATALOG_PATH)
    for entry in catalog.get("model_profiles", []):
        if (
            manifest.get("experiment_profile_id") in entry.get("experiment_profile_ids", [])
            and manifest.get("controller_id") in entry.get("controller_ids", [])
            and manifest.get("vehicle_count") in entry.get("vehicle_counts", [])
            and entry.get("status") == "enabled"
            and isinstance(entry.get(action), dict)
        ):
            return entry, entry[action]
    raise ValueError("model_operation_not_allowlisted")


def run_mil(manifest: dict[str, Any], spec: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    model_file = project_path(str(spec["model_file"]))
    if not model_file.is_file():
        raise FileNotFoundError(f"model_file_not_found: {portable(model_file)}")
    smoke = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
    command = [
        sys.executable,
        str(smoke),
        "--model-file", str(model_file),
        "--model-name", str(spec["model_name"]),
        "--target-time", f"0,{float(spec['stop_time_s'])}",
        "--raw-output", str(output_dir / "raw.csv"),
        "--metrics-json", str(output_dir / "metrics.json"),
        "--metrics-csv", str(output_dir / "metrics.csv"),
        "--log-output", str(output_dir / "mcp.jsonl"),
        "--native-result-dir", str(output_dir / "native_result"),
        "--scene-id", str(manifest["experiment_profile_id"]),
        "--controller-id", str(manifest["controller_id"]),
        "--evidence-level", "mworks_mil",
        "--variable-profile", "diagnostics_declared",
        "--metrics-profile", "diagnostics_smoke",
        "--no-gui-open",
    ]
    for alias, variable in spec.get("verify_variables", {}).items():
        command.extend(["--extra-variable", f"{alias}={variable}"])
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    (output_dir / "worker.stdout.log").write_text(completed.stdout, encoding="utf-8", newline="\n")
    (output_dir / "worker.stderr.log").write_text(completed.stderr, encoding="utf-8", newline="\n")
    metrics_path = output_dir / "metrics.json"
    metrics = read_json(metrics_path) if metrics_path.is_file() else {}
    accepted = completed.returncode == 0 and metrics.get("valid") is True
    result = {
        "schema": "mosim.model_studio.mworks_mil_result.v1",
        "status": "passed" if accepted else "failed",
        "run_id": manifest["run_id"],
        "profile_hash": manifest["experiment_profile_hash"],
        "controller_id": manifest["controller_id"],
        "model_name": spec["model_name"],
        "model_file": portable(model_file),
        "model_sha256": sha256(model_file),
        "official_api": "MWORKS Sysplorer MCP CheckModel and SimulateModel",
        "return_code": completed.returncode,
        "metrics": metrics,
        "evidence_paths": [portable(path) for path in sorted(output_dir.rglob("*")) if path.is_file()],
        "claim_boundary": "Run-local MWORKS MIL evidence only; code generation, SIL and Gazebo runtime remain separate gates."
    }
    write_json(output_dir / "MWORKS_MIL_RESULT.json", result)
    return result


def run_codegen(manifest: dict[str, Any], spec: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    model_file = project_path(str(spec["model_file"]))
    if not model_file.is_file():
        raise FileNotFoundError(f"model_file_not_found: {portable(model_file)}")
    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    import run_sysplorer_mcp_smoke as mcp  # type: ignore

    code_root = output_dir / "generated_c"
    source = f'''\
import mworks.sysplorer as ModelingPy

model_name = {str(spec["model_name"])!r}
model_file = {str(model_file)!r}
output_root = {str(code_root)!r}
result = {{}}
try:
    if not ModelingPy.ClassExist(model_name):
        result["open_model_file"] = ModelingPy.OpenModelFile(model_file)
    else:
        result["open_model_file"] = True
    result["check_model"] = ModelingPy.CheckModel(model_name)
    if result["check_model"]:
        options = ModelingPy.GetModelCodeGenerationOptions(model_name)
        options["CodePlatform.OutPath"] = {{"output": output_root}}
        result["set_options"] = ModelingPy.SetModelCodeGenerationOptions(model_name, options)
        result["generate_code"] = ModelingPy.GenerateModelCode(model_name) if result["set_options"] else False
except Exception as exc:
    result["exception"] = repr(exc)
try:
    result["last_errors"] = str(ModelingPy.GetLastErrors())
except Exception:
    pass
RUN_SCRIPT_RESULT = result
'''
    log_path = output_dir / "mcp.jsonl"
    wrapper = mcp.resolve_wrapper(None)
    client = mcp.JsonlMcpClient(mcp.wrapper_command(wrapper), log_path)
    try:
        health = mcp.initialize_mcp_client(client)
        response = client.call_tool(
            "call_code",
            {"mode": "run_script", "payload": {"python_source": source}},
            timeout_s=300,
        )
    finally:
        client.close()
    nested = response.get("run_script_result") if isinstance(response.get("run_script_result"), dict) else {}
    code_dir = code_root / str(spec["model_name"])
    files = {
        path.relative_to(code_dir).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(code_dir.rglob("*"))
        if path.is_file()
    } if code_dir.is_dir() else {}
    missing = sorted(set(spec.get("required_files", [])) - set(files))
    accepted = bool(response.get("ok")) and bool(nested.get("check_model")) and bool(nested.get("generate_code")) and not missing
    result = {
        "schema": "mosim.model_studio.mworks_codegen_result.v1",
        "status": "passed" if accepted else "failed",
        "run_id": manifest["run_id"],
        "profile_hash": manifest["experiment_profile_hash"],
        "controller_id": manifest["controller_id"],
        "model_name": spec["model_name"],
        "model_file": portable(model_file),
        "model_sha256": sha256(model_file),
        "official_api": "ModelingPy.GenerateModelCode",
        "mcp_health": health,
        "mworks_result": nested,
        "generated_code_dir": portable(code_dir) if code_dir.is_dir() else "",
        "generated_file_count": len(files),
        "generated_files": files,
        "missing_required_files": missing,
        "claim_boundary": "Official run-local MWORKS code generation evidence only; generated-C SIL and Gazebo runtime remain separate gates."
    }
    write_json(output_dir / "MWORKS_CODEGEN_RESULT.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True, choices=("run_mil", "generate_code"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--operation-id", required=True)
    args = parser.parse_args()
    if not RUN_ID_PATTERN.fullmatch(args.run_id) or not OPERATION_ID_PATTERN.fullmatch(args.operation_id):
        raise SystemExit("invalid run or operation id")
    run_dir = RUN_ROOT / args.run_id
    manifest = read_json(run_dir / "RUN_MANIFEST.json")
    if manifest.get("run_id") != args.run_id:
        raise SystemExit("run manifest mismatch")
    entry, spec = select_entry(manifest, args.action)
    output_dir = run_dir / "mworks" / args.action
    status_path = output_dir / "OPERATION_STATUS.json"
    write_json(status_path, {
        "schema": "mosim.model_studio.operation_status.v1",
        "status": "running",
        "reason_code": "mworks_operation_running",
        "action": args.action,
        "operation_id": args.operation_id,
        "run_id": args.run_id,
        "model_profile_id": entry["model_profile_id"],
        "started_at": time.time(),
    })
    try:
        result = run_mil(manifest, spec, output_dir) if args.action == "run_mil" else run_codegen(manifest, spec, output_dir)
        accepted = result.get("status") == "passed"
        write_json(status_path, {
            "schema": "mosim.model_studio.operation_status.v1",
            "status": "completed" if accepted else "failed",
            "reason_code": f"{args.action}_{'completed' if accepted else 'failed'}",
            "action": args.action,
            "operation_id": args.operation_id,
            "run_id": args.run_id,
            "result_gate": spec["result_gate"],
            "completed_at": time.time(),
        })
        return 0 if accepted else 2
    except Exception as exc:
        write_json(status_path, {
            "schema": "mosim.model_studio.operation_status.v1",
            "status": "failed",
            "reason_code": "mworks_operation_exception",
            "action": args.action,
            "operation_id": args.operation_id,
            "run_id": args.run_id,
            "detail": repr(exc),
            "completed_at": time.time(),
        })
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
