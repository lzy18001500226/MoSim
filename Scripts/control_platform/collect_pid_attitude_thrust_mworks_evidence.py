#!/usr/bin/env python3
"""Collect live MWORKS reference rows for the full PID attitude/thrust contract.

Run this file inside Sysplorer through ``call_code(mode="run_script")``.  The
result rows come only from the live MWORKS result API and are ordered exactly
like the generated-C runtime schema used by the SIL checker.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_attitude_thrust_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models"
RAW_DIR = RESULT_DIR / "raw"
SIL_DIR = RESULT_DIR / "sil"
CODEGEN_ROOT = RESULT_DIR / "generated_c_v2"
BRIDGE_NAME = "MoSim_PID_AttitudeThrust_CFunction_Sysblock"


def load_builder():
    path = ROOT / "Scripts/control_platform/build_pid_attitude_thrust_mworks_models.py"
    spec = importlib.util.spec_from_file_location("pid_attitude_thrust_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_ok(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value in (0, 1)
    return not any(marker in str(value).lower() for marker in ("error", "failed", "false"))


def write_json_lf(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, indent=2) + "\n")


def normalize_codegen_archive(code_dir: Path) -> None:
    for path in sorted(item for item in code_dir.rglob("*") if item.is_file()):
        text = path.read_text(encoding="utf-8", errors="strict")
        normalized = "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"
        path.write_text(normalized, encoding="utf-8", newline="\n")


def generated_globals(code_dir: Path) -> tuple[str, str]:
    header = (code_dir / f"{BRIDGE_NAME}.h").read_text(encoding="utf-8", errors="replace")
    names = re.findall(r"^extern\s+struct\s+\w+\s+(\w+)\s*;", header, re.MULTILINE)
    if len(names) < 2:
        raise RuntimeError(f"cannot discover generated input/output globals in {code_dir}")
    return names[0], names[1]


def main() -> dict:
    builder = load_builder()
    for directory in (RAW_DIR, SIL_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    code_dir = CODEGEN_ROOT / BRIDGE_NAME
    normalize_codegen_archive(code_dir)
    input_global, output_global = generated_globals(code_dir)
    all_rows = []
    input_sequence = []
    fixtures = {}

    for algorithm_id, algorithm_name in builder.VARIANTS.items():
        model_name = f"MoSim_PID_{algorithm_name.upper()}_ATTITUDE_THRUST_MIL"
        model_path = MODEL_DIR / f"{model_name}.mo"
        if not ModelingPy.ClassExist(model_name):
            ModelingPy.OpenModelFile(str(model_path))

        check_result = ModelingPy.CheckModel(model_name)
        if not check_ok(check_result):
            raise RuntimeError(f"CheckModel failed for {model_name}: {check_result}")
        simulate_result = ModelingPy.SimulateModel(model_name)
        if not check_ok(simulate_result):
            raise RuntimeError(f"SimulateModel failed for {model_name}: {simulate_result}")

        times = [float(value) for value in ModelingPy.GetVarTimes()]
        columns = [[float(value) for value in values] for values in ModelingPy.GetVarsValues(builder.OUTPUTS)]
        lengths = {len(times), *(len(values) for values in columns)}
        if lengths != {21}:
            raise RuntimeError(f"unexpected sample lengths for {model_name}: {sorted(lengths)}")
        if not all(math.isfinite(value) for values in columns for value in values):
            raise RuntimeError(f"NaN or Inf found in {model_name}")

        csv_path = RAW_DIR / f"{algorithm_name}_attitude_thrust.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["time_s", *builder.OUTPUTS])
            writer.writerows(zip(times, *columns))

        for local_index, time_s in enumerate(times):
            all_rows.append({
                "index": len(all_rows),
                "time_s": time_s,
                "algorithm_id": algorithm_id,
                "algorithm_name": algorithm_name,
                "outputs": {
                    f"{name}_out": columns[column_index][local_index]
                    for column_index, name in enumerate(builder.OUTPUTS)
                },
            })
            inputs = {"algorithm_id_in": float(algorithm_id)}
            inputs.update({f"{name}_in": float(value) for name, value in builder.BASE_INPUTS.items()})
            input_sequence.append(inputs)

        fixtures[algorithm_name] = {
            "algorithm_id": algorithm_id,
            "model_name": model_name,
            "check_model": str(check_result),
            "simulate_model": str(simulate_result),
            "sample_count": len(times),
            "raw_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
            "raw_csv_sha256": sha256(csv_path),
        }

    reference = {
        "schema": "mosim.pid_attitude_thrust_mworks_reference.v1",
        "source_label": "MWORKS_MCP_LIVE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_count": len(fixtures),
        "sample_count": len(all_rows),
        "output_count": len(builder.OUTPUTS),
        "rows": all_rows,
        "fixtures": fixtures,
        "claim_boundary": "Live fixed-input MWORKS MIL reference for full ATTITUDE_THRUST output fields; Gazebo/PX4/MAVROS remains a separate gate.",
    }
    reference_path = SIL_DIR / "mworks_reference_126_rows.json"
    write_json_lf(reference_path, reference)

    runtime_schema = {
        "schema": "mosim.mworks_codegen_runtime_schema.v1",
        "model_name": BRIDGE_NAME,
        "source_model_names": [item["model_name"] for item in fixtures.values()],
        "input_global": input_global,
        "output_global": output_global,
        "input_fields": [f"{name}_in" for name in builder.INPUTS],
        "output_fields": [f"{name}_out" for name in builder.OUTPUTS],
        "input_sequence": input_sequence,
    }
    schema_path = SIL_DIR / "runtime_schema_126_rows.json"
    write_json_lf(schema_path, runtime_schema)

    manifest = {
        "schema": "mosim.pid_attitude_thrust_mworks_evidence.v1",
        "ok": len(all_rows) == 126,
        "source": "MWORKS_MCP_LIVE",
        "bridge_model": BRIDGE_NAME,
        "fixture_count": len(fixtures),
        "sample_count": len(all_rows),
        "output_count": len(builder.OUTPUTS),
        "reference_json": str(reference_path.relative_to(ROOT)).replace("\\", "/"),
        "runtime_schema_json": str(schema_path.relative_to(ROOT)).replace("\\", "/"),
        "generated_code_dir": str(code_dir.relative_to(ROOT)).replace("\\", "/"),
        "generated_code_archive_normalization": "LF line endings and trailing horizontal whitespace removed after GenerateModelCode for Git hygiene; executable tokens are unchanged.",
        "generated_source_hashes": {
            str(path.relative_to(code_dir)).replace("\\", "/"): sha256(path)
            for path in sorted(code_dir.rglob("*")) if path.is_file()
        },
        "fixtures": fixtures,
    }
    manifest_path = RESULT_DIR / "MWORKS_ATTITUDE_THRUST_MANIFEST.json"
    write_json_lf(manifest_path, manifest)
    return {"ok": manifest["ok"], "manifest": str(manifest_path), "sample_count": len(all_rows)}


RUN_SCRIPT_RESULT = main()
