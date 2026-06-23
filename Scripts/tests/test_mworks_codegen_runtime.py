#!/usr/bin/env python3
"""Regression checks for MWORKS generated controller runtime artifacts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import textwrap


ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT / "Results" / "codegen_probe" / "AWFF_PID_Sysblock_Demo_api" / "AWFF_PID_Sysblock_Demo"
MODEL_NAME = "AWFF_PID_Sysblock_Demo"


def load_checker():
    path = ROOT / "Scripts" / "mworks" / "check_codegen_runtime.py"
    spec = importlib.util.spec_from_file_location("check_codegen_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_codegen_runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(*extra: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "mworks" / "check_codegen_runtime.py"),
            "--code-dir",
            str(CODE_DIR.relative_to(ROOT)),
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


def test_codegen_runtime_summary_contract() -> None:
    payload = run_checker("--expect-sample-time", "0.01")
    if payload["schema"] != "mosim.mworks_codegen_runtime_check.v1":
        raise AssertionError(payload)
    if not payload["ok"]:
        raise AssertionError(payload)
    if payload["runtime_adapter_shape"] != "global_struct_input_output_init_step":
        raise AssertionError(payload)
    if payload["sample_time_s"] != 0.01:
        raise AssertionError(payload)
    if payload["functions"] != ["Step", "Init"]:
        raise AssertionError(payload)
    input_fields = next(iter(payload["input_globals"].values()))["fields"]
    output_fields = next(iter(payload["output_globals"].values()))["fields"]
    if input_fields != ["z_error"]:
        raise AssertionError(payload)
    if output_fields != ["thrust_cmd"]:
        raise AssertionError(payload)
    if not payload["sil_gate_required"]:
        raise AssertionError(payload)


def test_codegen_runtime_compile_gate() -> None:
    payload = run_checker("--compile", "--run-smoke", "--expect-sample-time", "0.01")
    if not payload["ok"]:
        raise AssertionError(payload)
    compile_result = payload["compile"]
    if not compile_result["available"]:
        raise AssertionError(payload)
    if not compile_result["ok"]:
        raise AssertionError(payload)
    if compile_result["returncode"] != 0:
        raise AssertionError(payload)
    if not compile_result["object_dir_removed"]:
        raise AssertionError(payload)
    runtime_smoke = payload["runtime_smoke"]
    if not runtime_smoke["ok"]:
        raise AssertionError(payload)
    if not runtime_smoke["temp_dir_removed"]:
        raise AssertionError(payload)
    if [row["time_s"] for row in runtime_smoke["rows"]] != [0.01, 0.02, 0.03]:
        raise AssertionError(payload)
    if [row["input"] for row in runtime_smoke["rows"]] != [0.1, 0.2, -0.1]:
        raise AssertionError(payload)
    if [row["inputs"]["z_error"] for row in runtime_smoke["rows"]] != [0.1, 0.2, -0.1]:
        raise AssertionError(payload)
    if "thrust_cmd" not in runtime_smoke["rows"][0]["outputs"]:
        raise AssertionError(payload)


def test_codegen_runtime_multi_io_schema_harness(tmp_path: Path) -> None:
    checker = load_checker()
    code_dir = tmp_path / "MultiController"
    code_dir.mkdir()
    (code_dir / "mwb_types.h").write_text(
        "typedef double MwbDouble;\ntypedef int MwbInt32;\ntypedef signed char MwbInt8;\n",
        encoding="utf-8",
    )
    (code_dir / "mwb_runtime.h").write_text("", encoding="utf-8")
    (code_dir / "MultiController.h").write_text(
        textwrap.dedent(
            """
            #ifndef MULTI_CONTROLLER_H
            #define MULTI_CONTROLLER_H
            #include "mwb_types.h"
            typedef struct multi_controllerTagEmd multi_controllerEmd;
            struct multi_controllerTagEmd{
              MwbDouble m_curTime;
              MwbDouble m_startTime;
              MwbDouble m_stepSize;
              MwbInt32 m_timeTickCount;
            };
            extern struct multi_controllerExtU multi_controllerGbIn;
            extern struct multi_controllerExtY multi_controllerGbOut;
            extern multi_controllerEmd*const multi_controllerGbMd;
            void Step(void);
            void Init(void);
            #endif
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (code_dir / "MultiController_private.h").write_text(
        textwrap.dedent(
            """
            #include "MultiController.h"
            struct multi_controllerExtU
            {
              MwbDouble x_error;
              MwbDouble y_error;
              MwbDouble z_error;
              MwbDouble z_ref_rate;
            };
            struct multi_controllerExtY
            {
              MwbDouble y;
              MwbDouble y1;
            };
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (code_dir / "MultiController.c").write_text(
        textwrap.dedent(
            """
            #include "MultiController.h"
            #include "MultiController_private.h"
            struct multi_controllerExtU multi_controllerGbIn;
            struct multi_controllerExtY multi_controllerGbOut;
            static struct multi_controllerTagEmd multi_controllerStMd;
            multi_controllerEmd*const multi_controllerGbMd = &multi_controllerStMd;
            void Step(void)
            {
              multi_controllerGbOut.y = multi_controllerGbIn.x_error + multi_controllerGbIn.z_error;
              multi_controllerGbOut.y1 = multi_controllerGbIn.y_error - multi_controllerGbIn.z_ref_rate;
              ++multi_controllerGbMd->m_timeTickCount;
              multi_controllerGbMd->m_curTime = multi_controllerGbMd->m_startTime + (MwbDouble)multi_controllerGbMd->m_timeTickCount * multi_controllerGbMd->m_stepSize;
            }
            void Init(void)
            {
              multi_controllerGbMd->m_startTime = 0.0;
              multi_controllerGbMd->m_curTime = 0.0;
              multi_controllerGbMd->m_timeTickCount = 0;
              multi_controllerGbMd->m_stepSize = 0.01;
            }
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (code_dir / "MultiController_data.c").write_text("", encoding="utf-8")
    (code_dir / "mwb_main.c").write_text("", encoding="utf-8")
    runtime_schema = {
        "input_global": "multi_controllerGbIn",
        "output_global": "multi_controllerGbOut",
        "input_fields": ["x_error", "y_error", "z_error", "z_ref_rate"],
        "output_fields": ["y", "y1"],
        "input_sequence": [
            {"x_error": 1.0, "y_error": 2.0, "z_error": 3.0, "z_ref_rate": 0.5},
            {"x_error": -1.0, "y_error": 4.0, "z_error": 0.25, "z_ref_rate": 1.5},
        ],
    }
    payload = checker.summarize(
        code_dir,
        "MultiController",
        do_compile=True,
        do_run_smoke=True,
        input_sequence=[],
        runtime_schema=runtime_schema,
    )
    if not payload["ok"]:
        raise AssertionError(payload)
    rows = payload["runtime_smoke"]["rows"]
    if rows[0]["outputs"] != {"y": 4.0, "y1": 1.5}:
        raise AssertionError(payload)
    if rows[1]["outputs"] != {"y": -0.75, "y1": 2.5}:
        raise AssertionError(payload)
    if rows[0]["time_s"] != 0.01 or rows[1]["time_s"] != 0.02:
        raise AssertionError(payload)


def test_codegen_runtime_project_path_guard() -> None:
    checker = load_checker()
    try:
        checker.project_path("/mnt/c/Users/HP/Desktop/not_mosim/code")
    except SystemExit:
        return
    raise AssertionError("project_path accepted a path outside MoSim")


def main() -> int:
    test_codegen_runtime_summary_contract()
    test_codegen_runtime_compile_gate()
    test_codegen_runtime_project_path_guard()
    print("[OK] MWORKS codegen runtime regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
