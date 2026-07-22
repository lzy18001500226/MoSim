#!/usr/bin/env python3
"""Regression checks for generated-code SIL equivalence smoke gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = "Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo"
MODEL_NAME = "AWFF_PID_Sysblock_Demo"


def run_sil_smoke(*extra: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "mworks" / "check_codegen_sil_equivalence.py"),
            "--code-dir",
            CODE_DIR,
            "--model-name",
            MODEL_NAME,
            *extra,
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_zero_input_sil_smoke_contract() -> None:
    payload = run_sil_smoke("--input-sequence", "0,0,0", "--tolerance", "1e-12")
    if payload["schema"] != "mosim.mworks_codegen_sil_equivalence.v1":
        raise AssertionError(payload)
    if payload["gate_type"] != "zero_input_sil_smoke":
        raise AssertionError(payload)
    if not payload["ok"]:
        raise AssertionError(payload)
    if payload["mworks_reference_source"] != "offline_zero_input_reference_from_model_structure":
        raise AssertionError(payload)
    if payload["comparison"]["max_abs_error"] != 0.0:
        raise AssertionError(payload)
    if len(payload["comparison"]["comparisons"]) != 3:
        raise AssertionError(payload)
    if not payload["limitations"]:
        raise AssertionError(payload)
    if not any("nonzero SIL remains" in item for item in payload["limitations"]):
        raise AssertionError(payload)


def test_nonzero_sequence_fails_zero_reference() -> None:
    command = [
        sys.executable,
        str(ROOT / "Scripts" / "mworks" / "check_codegen_sil_equivalence.py"),
        "--code-dir",
        CODE_DIR,
        "--model-name",
        MODEL_NAME,
        "--input-sequence",
        "0.1,0.2,-0.1",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode == 0:
        raise AssertionError(result.stdout)
    payload = json.loads(result.stdout)
    if payload["ok"]:
        raise AssertionError(payload)
    if payload["comparison"]["max_abs_error"] <= 0.0:
        raise AssertionError(payload)


def test_nonzero_constant_mworks_reference_passes() -> None:
    payload = run_sil_smoke(
        "--input-sequence",
        "0.1,0.1,0.1,0.1",
        "--mworks-reference-json",
        "Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json",
        "--tolerance",
        "1e-5",
    )
    if payload["gate_type"] != "nonzero_input_sil_smoke":
        raise AssertionError(payload)
    if payload["mworks_reference_source"] != "Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json":
        raise AssertionError(payload)
    if not payload["ok"]:
        raise AssertionError(payload)
    if payload["comparison"]["max_abs_error"] > 1e-5:
        raise AssertionError(payload)
    if not any("output order" in item for item in payload["limitations"]):
        raise AssertionError(payload)


def test_multi_output_schema_reference_passes() -> None:
    runtime_schema = ROOT / "Results" / "generated_mworks" / "AWFF_FullController_Sysblock_20260620_032747" / "runtime_schema.json"
    runtime_smoke = ROOT / "Results" / "generated_mworks" / "AWFF_FullController_Sysblock_20260620_032747" / "runtime_schema_smoke_check.json"
    smoke_payload = json.loads(runtime_smoke.read_text(encoding="utf-8"))
    reference_rows = []
    for row in smoke_payload["runtime_smoke"]["rows"]:
        reference_rows.append(
            {
                "index": row["index"],
                "time_s": row["time_s"] - 0.01,
                "outputs": row["outputs"],
            }
        )
    reference = {
        "schema": "mosim.mworks_codegen_sil_reference.v1",
        "model_name": "AWFF_FullController_Sysblock_SIL_SyntheticReference",
        "source_label": "synthetic_test_reference",
        "rows": reference_rows,
    }
    with tempfile.TemporaryDirectory(prefix="mosim_sil_multi_ref_", dir=ROOT / "Results" / "tmp") as temp_dir:
        reference_path = Path(temp_dir) / "awff_multi_reference.json"
        reference_path.write_text(json.dumps(reference), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts" / "mworks" / "check_codegen_sil_equivalence.py"),
                "--code-dir",
                "Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FullController_Sysblock",
                "--model-name",
                "AWFF_FullController_Sysblock",
                "--runtime-schema-json",
                str(runtime_schema.relative_to(ROOT)),
                "--mworks-reference-json",
                str(reference_path.relative_to(ROOT)),
                "--tolerance",
                "1e-12",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    payload = json.loads(result.stdout)
    if not payload["ok"]:
        raise AssertionError(payload)
    if payload["runtime_schema_source"] != runtime_schema.relative_to(ROOT).as_posix():
        raise AssertionError(payload)
    first = payload["comparison"]["comparisons"][0]
    if sorted(first["fields"]) != ["y", "y1", "y2", "y3"]:
        raise AssertionError(payload)
    if payload["comparison"]["max_abs_error"] != 0.0:
        raise AssertionError(payload)


def test_awff_full_controller_real_constant_reference_passes() -> None:
    runtime_schema = (
        ROOT
        / "Results"
        / "generated_mworks"
        / "AWFF_FullController_Sysblock_20260620_032747"
        / "runtime_schema_constant_positive.json"
    )
    reference = (
        ROOT
        / "Results"
        / "generated_mworks"
        / "AWFF_FullController_Sysblock_20260620_032747"
        / "mworks_awff_fullcontroller_constant_reference.json"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "mworks" / "check_codegen_sil_equivalence.py"),
            "--code-dir",
            "Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FullController_Sysblock",
            "--model-name",
            "AWFF_FullController_Sysblock",
            "--runtime-schema-json",
            str(runtime_schema.relative_to(ROOT)),
            "--mworks-reference-json",
            str(reference.relative_to(ROOT)),
            "--tolerance",
            "1e-5",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    if payload["gate_type"] != "nonzero_input_sil_smoke":
        raise AssertionError(payload)
    if not payload["ok"]:
        raise AssertionError(payload)
    if payload["source_label"] != "MWORKS_MCP_SIMULATE_MODEL_PLUS_GENERATED_C_RUNTIME":
        raise AssertionError(payload)
    if payload["comparison"]["max_abs_error"] > 1e-5:
        raise AssertionError(payload)


def main() -> int:
    test_zero_input_sil_smoke_contract()
    test_nonzero_sequence_fails_zero_reference()
    test_nonzero_constant_mworks_reference_passes()
    test_multi_output_schema_reference_passes()
    test_awff_full_controller_real_constant_reference_passes()
    print("[OK] MWORKS codegen SIL smoke regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
