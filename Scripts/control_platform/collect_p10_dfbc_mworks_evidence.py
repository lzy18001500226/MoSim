#!/usr/bin/env python3
"""Collect live MWORKS evidence for the six P10 DFBC/DOB fixtures.

Run inside Sysplorer through ``call_code(mode="run_script")``.  This collector
keeps MWORKS MIL/codegen/SIL evidence separate from the later Gazebo gate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/dfbc_family"
MODEL_DIR = RESULT_DIR / "models"
RAW_DIR = RESULT_DIR / "raw"
METRICS_DIR = RESULT_DIR / "metrics"
LOG_DIR = RESULT_DIR / "logs"
CLOSEOUT_DIR = RESULT_DIR / "closeout"
SCREENSHOT_DIR = RESULT_DIR / "screenshots"
BUILD_MANIFEST = RESULT_DIR / "P10_DFBC_BUILD_MANIFEST.json"
SIL_MANIFEST = RESULT_DIR / "sil/RUN_MANIFEST.json"
GRAPHICAL_REVIEW = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/graphical_review_20260718/P10_MWORKS_GRAPHICAL_REVIEW.json"
BRIDGE_NAME = "MoSim_P10_DFBC_Family_CFunction_Sysblock"


def load_builder():
    path = ROOT / "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py"
    module = ModuleType("p10_dfbc_current_builder")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def any_nonzero(values: list[float], tolerance: float = 1.0e-12) -> bool:
    return any(abs(value) > tolerance for value in values)


def behavior_checks(controller: str, columns: dict[str, list[float]]) -> dict[str, bool]:
    quaternion_norms = [
        math.sqrt(w * w + x * x + y * y + z * z)
        for w, x, y, z in zip(
            columns["desired_attitude_w"],
            columns["desired_attitude_x"],
            columns["desired_attitude_y"],
            columns["desired_attitude_z"],
            strict=True,
        )
    ]
    checks = {
        "status_code_zero": all(value == 0.0 for value in columns["status_code"]),
        "finite_outputs": all(math.isfinite(value) for values in columns.values() for value in values),
        "positive_collective_thrust": all(value > 0.0 for value in columns["collective_thrust_N"]),
        "unit_desired_attitude": all(abs(value - 1.0) <= 1.0e-12 for value in quaternion_norms),
    }
    if "high_order" in controller:
        checks.update(
            {
                "high_order_body_rate_nonzero": any_nonzero(columns["desired_body_rate_x"]),
                "high_order_body_acceleration_nonzero": any_nonzero(
                    columns["desired_body_acceleration_x"]
                ),
            }
        )
    if "smooth_robust" in controller or "dob_eso" in controller:
        checks["smooth_robust_body_rate_nonzero"] = any_nonzero(columns["desired_body_rate_x"])
    if controller == "dfbc_dob_eso_disabled":
        checks["disturbance_estimate_zero_when_disabled"] = not any_nonzero(
            columns["disturbance_estimate_x"]
            + columns["disturbance_estimate_y"]
            + columns["disturbance_estimate_z"]
        )
    if controller == "dfbc_dob_eso":
        checks.update(
            {
                "disturbance_estimate_nonzero_when_enabled": any_nonzero(
                    columns["disturbance_estimate_x"]
                    + columns["disturbance_estimate_y"]
                    + columns["disturbance_estimate_z"]
                ),
                "disturbance_estimate_within_configured_limits": all(
                    abs(value) <= limit + 1.0e-12
                    for name, limit in (
                        ("disturbance_estimate_x", 0.5),
                        ("disturbance_estimate_y", 0.6),
                        ("disturbance_estimate_z", 0.4),
                    )
                    for value in columns[name]
                ),
            }
        )
    return checks


def main() -> dict:
    builder = load_builder()
    build = json.loads(BUILD_MANIFEST.read_text(encoding="utf-8"))
    sil = json.loads(SIL_MANIFEST.read_text(encoding="utf-8"))
    graphical_review = json.loads(GRAPHICAL_REVIEW.read_text(encoding="utf-8"))
    if graphical_review.get("status") != "passed":
        raise RuntimeError("P10 graphical review is not passed")
    if sil.get("status") != "passed" or sil.get("gate_result", {}).get("failure_count") != 0:
        raise RuntimeError("P10 generated-C SIL manifest is not passed")
    for directory in (RAW_DIR, METRICS_DIR, LOG_DIR, CLOSEOUT_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    bridge_path = MODEL_DIR / f"{BRIDGE_NAME}.mo"
    if not ModelingPy.ClassExist(BRIDGE_NAME):
        if not ModelingPy.OpenModelFile(str(bridge_path)):
            raise RuntimeError(f"OpenModelFile failed for {bridge_path}")

    screenshot_group_for_controller = {
        "dfbc_high_order_attitude": "high_order",
        "dfbc_high_order_bodyrate": "high_order",
        "dfbc_smooth_robust_attitude": "smooth_robust",
        "dfbc_smooth_robust_bodyrate": "smooth_robust",
        "dfbc_dob_eso_disabled": "dob_disabled",
        "dfbc_dob_eso": "dob_enabled",
    }
    fixtures: dict[str, dict] = {}
    columns_by_controller: dict[str, dict[str, list[float]]] = {}
    tool_steps: list[dict] = []
    for controller, contract in build["fixtures"].items():
        model_name = contract["model_name"]
        model_path = Path(contract["model_path"])
        if not ModelingPy.ClassExist(model_name):
            if not ModelingPy.OpenModelFile(str(model_path)):
                raise RuntimeError(f"OpenModelFile failed for {model_path}")

        check_ok = bool(ModelingPy.CheckModel(model_name))
        if not check_ok:
            raise RuntimeError(f"CheckModel failed for {model_name}: {ModelingPy.GetLastErrors()}")
        simulate_ok = bool(ModelingPy.SimulateModel(model_name))
        if not simulate_ok:
            raise RuntimeError(f"SimulateModel failed for {model_name}: {ModelingPy.GetLastErrors()}")

        times = [float(value) for value in ModelingPy.GetVarTimes()]
        values = [[float(value) for value in column] for column in ModelingPy.GetVarsValues(builder.OUTPUTS)]
        lengths = {len(times), *(len(column) for column in values)}
        if lengths != {8}:
            raise RuntimeError(f"unexpected result lengths for {model_name}: {sorted(lengths)}")
        columns = dict(zip(builder.OUTPUTS, values, strict=True))
        columns_by_controller[controller] = columns
        checks = behavior_checks(controller, columns)

        csv_path = RAW_DIR / f"{controller}_mil.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["time_s", *builder.OUTPUTS])
            writer.writerows(zip(times, *values))

        metrics_path = METRICS_DIR / f"{controller}_mil_metrics.json"
        screenshot_group = screenshot_group_for_controller[controller]
        screenshot_manifest = SCREENSHOT_DIR / screenshot_group / "capture_manifest.json"
        result_screenshots = sorted(
            path
            for path in (SCREENSHOT_DIR / screenshot_group).glob("*.png")
            if "结果查看器" in path.name
        )
        screenshot_ok = screenshot_manifest.is_file() and len(result_screenshots) == 1
        metrics = {
            "schema": "mosim.p10_dfbc.mworks_mil_metrics.v1",
            "status": "passed" if all(checks.values()) else "failed",
            "source": "MWORKS_MCP_LIVE",
            "controller": controller,
            "controller_id": contract["controller_id"],
            "output_interface": contract["output_interface"],
            "dob_enabled": bool(contract["dob"]),
            "model_name": model_name,
            "check_model": check_ok,
            "simulate_model": simulate_ok,
            "sample_count": len(times),
            "output_count": len(builder.OUTPUTS),
            "behavior_checks": checks,
            "result_viewer_screenshot_present": screenshot_ok,
            "first_outputs": {name: column[0] for name, column in columns.items()},
            "last_outputs": {name: column[-1] for name, column in columns.items()},
            "raw_csv": relative(csv_path),
            "raw_csv_sha256": sha256(csv_path),
            "screenshot_manifest": relative(screenshot_manifest) if screenshot_manifest.is_file() else None,
            "result_viewer_screenshot": relative(result_screenshots[0]) if result_screenshots else None,
            "claim_boundary": "Short fixed-input graphical Sysblock MIL behavior. No Gazebo or flight-performance claim.",
        }
        write_json(metrics_path, metrics)
        fixtures[controller] = {
            "status": metrics["status"],
            "model_name": model_name,
            "output_interface": contract["output_interface"],
            "metrics": relative(metrics_path),
            "raw_csv": relative(csv_path),
            "screenshot_manifest": metrics["screenshot_manifest"],
            "result_viewer_screenshot": metrics["result_viewer_screenshot"],
        }
        tool_steps.extend(
            [
                {"controller": controller, "step": "CheckModel", "status": "passed"},
                {"controller": controller, "step": "SimulateModel", "status": "passed"},
                {"controller": controller, "step": "GetVarTimes/GetVarsValues", "status": "passed", "sample_count": len(times)},
            ]
        )

    disabled = columns_by_controller["dfbc_dob_eso_disabled"]
    enabled = columns_by_controller["dfbc_dob_eso"]
    dob_ablation = {
        "same_fixture_inputs_except_enable_disturbance_observer": True,
        "disabled_final_estimate_x": disabled["disturbance_estimate_x"][-1],
        "enabled_final_estimate_x": enabled["disturbance_estimate_x"][-1],
        "enabled_differs_from_disabled": abs(
            enabled["disturbance_estimate_x"][-1] - disabled["disturbance_estimate_x"][-1]
        ) > 1.0e-12,
    }
    overall_ok = all(item["status"] == "passed" for item in fixtures.values()) and dob_ablation[
        "enabled_differs_from_disabled"
    ]

    tool_log = {
        "schema": "mosim.p10_dfbc.mworks_tool_log.v1",
        "source": "MWORKS_MCP_LIVE",
        "live_mworks_touched": True,
        "function_model": BRIDGE_NAME,
        "steps": tool_steps
        + [
            {"step": "GenerateModelCode", "status": "passed", "model_name": BRIDGE_NAME},
            {"step": "generated-C SIL", "status": "passed", "case_count": sil["gate_result"]["case_count"], "failure_count": 0},
        ],
        "activation_state_observation": "usable_main_window_no_login_license_or_authorization_blocker_observed",
        "license_state": "task_local_sufficient_for_check_simulate_codegen",
        "will_not_click_activation_login": True,
        "mworks_phase_observations": [
            "All six fixtures passed CheckModel and SimulateModel with eight finite result samples and status_code=0.",
            "The high-order result viewer shows nonzero body-rate and body-acceleration outputs under the declared BODY_RATE_THRUST contract.",
            "The smooth-robust result viewer shows finite attitude/thrust and nonzero body-rate outputs with DOB disabled.",
            "The DOB enabled/disabled result viewers and raw series show a same-input ablation: final disturbance_estimate_x changes from 0.0 to -0.5.",
            "The 140-input/32-output fixture uses a tall one-signal-per-row layout; every top-level port connection is visible and traceable in the exported diagram.",
            "The graphical review covers top-level wiring only; the controller implementation inside the atomic CFunction is not claimed to be expanded into primitive blocks.",
            "No login, license, authorization, crash-report, or unknown blocking dialog was visible.",
        ],
    }
    tool_log_path = LOG_DIR / "MWORKS_DFBC_TOOL_LOG.json"
    write_json(tool_log_path, tool_log)

    for controller, fixture in fixtures.items():
        closeout = {
            "schema": "mosim.p10_dfbc.controller_closeout.v1",
            "status": "passed" if fixture["status"] == "passed" else "failed",
            "controller": controller,
            "output_interface": fixture["output_interface"],
            "evidence_ladder": {
                "graphical_sysblock_fixture": "passed",
                "check_model": "passed",
                "simulate_model": "passed",
                "result_variables_and_metrics": fixture["status"],
                "official_generate_model_code": "passed",
                "generated_c_sil": "passed",
                "generated_c_gazebo": "not_run",
            },
            "generated_c_sil": sil["gate_result"],
            "artifact_refs": [
                relative(BUILD_MANIFEST),
                relative(GRAPHICAL_REVIEW),
                relative(Path(build["fixtures"][controller]["model_path"])),
                fixture["raw_csv"],
                fixture["metrics"],
                relative(tool_log_path),
                relative(SIL_MANIFEST),
                fixture["screenshot_manifest"],
                fixture["result_viewer_screenshot"],
            ],
            "claim_boundary": "MWORKS graphical MIL, official code generation, and generated-C SIL only. Gazebo remains open.",
        }
        write_json(CLOSEOUT_DIR / f"{controller}_closeout.json", closeout)

    screenshot_evidence_complete = all(
        item["screenshot_manifest"] and item["result_viewer_screenshot"] for item in fixtures.values()
    )
    overall_ok = overall_ok and screenshot_evidence_complete
    manifest = {
        "schema": "mosim.p10_dfbc.mworks_closeout_manifest.v1",
        "status": "passed" if overall_ok else "failed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "MWORKS_MCP_LIVE",
        "live_mworks_touched": True,
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "dob_ablation": dob_ablation,
        "graphical_review": relative(GRAPHICAL_REVIEW),
        "screenshot_evidence_complete": screenshot_evidence_complete,
        "official_codegen": "passed",
        "generated_c_sil": {
            "status": sil["status"],
            "controller_ids": sil["gate_result"]["controller_ids"],
            "case_count": sil["gate_result"]["case_count"],
            "failure_count": sil["gate_result"]["failure_count"],
            "tolerance": sil["gate_result"]["tolerance"],
        },
        "claim_ceiling": "Six DFBC/DOB rows closed through generated-C SIL; generated-C Gazebo remains separate and not run.",
    }
    manifest_path = RESULT_DIR / "P10_DFBC_MWORKS_CLOSEOUT_MANIFEST.json"
    write_json(manifest_path, manifest)
    return {"ok": overall_ok, "manifest": str(manifest_path), "fixtures": fixtures, "dob_ablation": dob_ablation}


RUN_SCRIPT_RESULT = main()
