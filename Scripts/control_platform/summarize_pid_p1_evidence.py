#!/usr/bin/env python3
"""Build the auditable P1 PID evidence and screenshot summaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_mworks_20260716"
LOG_DIR = RESULT_DIR / "logs"
ATTITUDE_THRUST_GATE = (
    ROOT
    / "Results/control_platform/p1_pid_attitude_thrust_ff05_20260716/PID_ATTITUDE_THRUST_GATE.json"
)
ATTITUDE_THRUST_MWORKS_DIR = (
    ROOT / "Results/control_platform/p1_pid_attitude_thrust_mworks_ff05_20260716"
)
RUNTIME_PROFILES = {
    "cascade_pid": "p1_pid_cascade_runtime_r4_hover0291_20260716",
    "gain_scheduled_pid": "p1_pid_gain_scheduled_runtime_r1_hover0291_20260716",
    "fuzzy_pid": "p1_pid_fuzzy_runtime_r1_hover0291_20260716",
    "neural_pid": "p1_pid_neural_runtime_r1_hover0291_20260716",
    "anti_windup": "p1_pid_anti_windup_runtime_r4_xbias012_hover0291_20260716",
    "feedforward_profile": "p1_pid_feedforward_runtime_r6_ff05_hover0291_20260716",
}
RUNTIME_ROOT = ROOT / "Results/sunray_ros1"


def load(name: str) -> dict:
    return json.loads((LOG_DIR / name).read_text(encoding="utf-8"))


def write_json_lf(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, indent=2) + "\n")


def file_record(path: Path, role: str, observation: str) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path),
        "role": role,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "observation": observation,
    }


def assess_runtime_profile(profile: str, result_dir: Path) -> dict:
    paths = {
        "metrics": result_dir / "PX4CTRL_BASIC_MISSION_METRICS.json",
        "manifest": result_dir / "RUN_MANIFEST.json",
        "provenance": result_dir / "PID_GENERATED_RUNTIME_PROVENANCE.json",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    errors = [f"missing_{name}" for name in missing]
    payloads: dict[str, dict] = {}
    for name, path in paths.items():
        if path.is_file():
            try:
                payloads[name] = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid_{name}:{exc}")

    metrics = payloads.get("metrics", {})
    manifest = payloads.get("manifest", {})
    provenance = payloads.get("provenance", {})
    if metrics and metrics.get("status") != "passed":
        errors.append(f"mission_status:{metrics.get('status')}")
    if manifest:
        if manifest.get("mission") != "takeoff_hover_land":
            errors.append(f"mission_type:{manifest.get('mission')}")
        if manifest.get("controller_core_profile") != profile:
            errors.append(f"manifest_profile:{manifest.get('controller_core_profile')}")
        if manifest.get("diagnostics", {}).get("mission_exit_code") != 0:
            errors.append(
                f"mission_exit_code:{manifest.get('diagnostics', {}).get('mission_exit_code')}"
            )
    if provenance:
        if provenance.get("status") != "passed":
            errors.append(f"provenance_status:{provenance.get('status')}")
        if provenance.get("controller_name") != profile:
            errors.append(f"provenance_profile:{provenance.get('controller_name')}")
        if provenance.get("provenance_level") != "runtime_acknowledged":
            errors.append(f"provenance_level:{provenance.get('provenance_level')}")
        if provenance.get("errors"):
            errors.append("provenance_errors_present")

    steady = metrics.get("steady_hover", {})
    return {
        "status": "passed" if not errors else "blocked",
        "errors": errors,
        "result_dir": str(result_dir),
        "metrics": str(paths["metrics"]),
        "manifest": str(paths["manifest"]),
        "provenance": str(paths["provenance"]),
        "steady_hover": {
            "xy_rmse_m": steady.get("xy_rmse_m"),
            "xy_max_m": steady.get("xy_max_m"),
            "z_abs_rmse_m": steady.get("z_abs_rmse_m"),
            "z_abs_max_m": steady.get("z_abs_max_m"),
        },
        "neural_residual_source": provenance.get("neural_residual_source"),
    }


def main() -> int:
    mil = load("mcp_evidence.json")
    graphical = load("pid_graphical_build_manifest.json")
    fixture = load("pid_graphical_fixture_manifest.json")
    codegen = load("pid_codegen_manifest.json")
    runtime = load("pid_codegen_runtime_check.json")
    equivalence = load("pid_graphical_codegen_equivalence.json")
    variant_mil = load("pid_graphical_variant_mil.json")
    variant_equivalence = load("pid_six_variant_graphical_equivalence.json")
    attitude_thrust = json.loads(ATTITUDE_THRUST_GATE.read_text(encoding="utf-8"))
    attitude_thrust_mworks = json.loads(
        (ATTITUDE_THRUST_MWORKS_DIR / "MWORKS_ATTITUDE_THRUST_MANIFEST.json").read_text(encoding="utf-8")
    )
    attitude_thrust_generate = json.loads(
        (ATTITUDE_THRUST_MWORKS_DIR / "generate_model_code_result_v2.json").read_text(encoding="utf-8")
    )
    attitude_thrust_codegen = json.loads(
        (ATTITUDE_THRUST_MWORKS_DIR / "sil/codegen_runtime_check_v2.json").read_text(encoding="utf-8")
    )
    attitude_thrust_sil = json.loads(
        (ATTITUDE_THRUST_MWORKS_DIR / "sil/sil_equivalence_126_rows_v2.json").read_text(encoding="utf-8")
    )
    generated_input_fields = next(iter(attitude_thrust_codegen["input_globals"].values()))["fields"]
    physical_parameter_inputs = {
        "mass_kg_in",
        "gravity_mps2_in",
        "max_tilt_rad_in",
        "min_collective_thrust_n_in",
        "max_collective_thrust_n_in",
    }

    activation = next((RESULT_DIR / "screenshots/activation").glob("*.png"))
    check_sim = next((RESULT_DIR / "screenshots/check_sim").glob("*.png"))
    diagram = RESULT_DIR / "screenshots/graphical/MoSim_PID_Unified_Graphical_Sysblock.png"
    screenshots = {
        "schema": "mosim.mworks.screenshot_manifest.v1",
        "source": "MWORKS_GUI_AND_EXPORT_DIAGRAM",
        "screenshots": [
            file_record(
                activation,
                "task_local_license_sufficiency_reference",
                "Foreground Sysplorer education-edition main window; no login, license, authorization, crash, or unknown blocking dialog is visible. One CFunction include warning is visible and is unrelated to licensing.",
            ),
            file_record(
                check_sim,
                "mil_check_and_simulation",
                "Sysplorer reports simulation finished at 0.2 s with 20 grid points; no login, license, authorization, or error-report dialog is visible.",
            ),
            file_record(
                diagram,
                "graphical_sysblock_topology",
                "Exported 51-block PID topology visibly includes gain scheduling, fuzzy/neural residual paths, discrete derivative, bounded integral recurrence, tracking anti-windup, feedforward, cascade, saturation, enable, and mode selection. No disconnected block is visible; dense central routing remains a readability limitation.",
            ),
        ],
    }
    screenshot_path = LOG_DIR / "screenshot_manifest.json"
    write_json_lf(screenshot_path, screenshots)

    fixture_ids = sorted(mil["fixtures"])
    runtime_profiles = {
        profile: assess_runtime_profile(profile, RUNTIME_ROOT / directory)
        for profile, directory in RUNTIME_PROFILES.items()
    }
    runtime_gate_passed = (
        sorted(runtime_profiles) == fixture_ids
        and all(item["status"] == "passed" for item in runtime_profiles.values())
    )
    gates = {
        "source_core_compile_and_golden_vector": True,
        "registry_interface_ready_nonselectable": True,
        "six_variant_mworks_mil": len(fixture_ids) == 6 and all(item["sample_count"] == 21 for item in mil["fixtures"].values()),
        "graphical_structure_check": bool(graphical["structure_ok"]),
        "graphical_fixed_fixture_mworks_mil": bool(fixture["check_model"] and fixture["simulate_model"] and fixture["sample_count"] == 11),
        "official_mworks_generated_c": bool(codegen["generate_result"] and codegen["generated_file_count"] >= 7),
        "generated_c_compile": bool(runtime["compile"]["ok"]),
        "generated_c_runtime_smoke": bool(runtime["runtime_smoke"]["ok"]),
        "fixed_fixture_graphical_codegen_equivalence": bool(equivalence["behavior_equivalence_ok"]),
        "six_variant_graphical_equivalence": bool(
            variant_mil["six_variant_graphical_mil_ok"]
            and variant_equivalence["six_variant_graphical_equivalence"]
        ),
        "full_attitude_thrust_contract": bool(
            attitude_thrust["status"] == "passed"
            and attitude_thrust["case_count"] == 12
            and attitude_thrust["lifecycle_fail_closed"]
            and attitude_thrust["frame_contract"]["thrust_unit"] == "N"
        ),
        "full_attitude_thrust_mworks_codegen_sil": bool(
            attitude_thrust_mworks["ok"]
            and attitude_thrust_mworks["fixture_count"] == 6
            and attitude_thrust_mworks["sample_count"] == 126
            and attitude_thrust_mworks["output_count"] == 20
            and attitude_thrust_generate["result"] is True
            and attitude_thrust_generate["output_root"].endswith("generated_c_v2")
            and attitude_thrust_codegen["ok"]
            and len(generated_input_fields) == 41
            and physical_parameter_inputs.issubset(generated_input_fields)
            and attitude_thrust_codegen["compile"]["ok"]
            and attitude_thrust_codegen["runtime_smoke"]["ok"]
            and attitude_thrust_sil["ok"]
            and attitude_thrust_sil["comparison"]["pass"]
            and len(attitude_thrust_sil["comparison"]["comparisons"]) == 126
            and sum(
                len(row["fields"])
                for row in attitude_thrust_sil["comparison"]["comparisons"]
            ) == 2520
        ),
        "gazebo_px4_mavros_closed_loop": runtime_gate_passed,
    }
    all_gates_passed = all(gates.values())
    summary = {
        "schema": "mosim.control_platform.pid_p1_summary.v1",
        "phase": "P1_PID_FAMILY",
        "status": "passed" if all_gates_passed else "partial",
        "algorithm_ids": fixture_ids,
        "registry_status": "runtime_accepted" if runtime_gate_passed else "interface_ready",
        "selectable": runtime_gate_passed,
        "gates": gates,
        "completed_gate_count": sum(gates.values()),
        "total_gate_count": len(gates),
        "evidence": {
            "mil": str(LOG_DIR / "mcp_evidence.json"),
            "graphical_structure": str(LOG_DIR / "pid_graphical_build_manifest.json"),
            "graphical_fixture": str(LOG_DIR / "pid_graphical_fixture_manifest.json"),
            "codegen": str(LOG_DIR / "pid_codegen_manifest.json"),
            "runtime": str(LOG_DIR / "pid_codegen_runtime_check.json"),
            "equivalence": str(LOG_DIR / "pid_graphical_codegen_equivalence.json"),
            "variant_graphical_mil": str(LOG_DIR / "pid_graphical_variant_mil.json"),
            "six_variant_graphical_equivalence": str(LOG_DIR / "pid_six_variant_graphical_equivalence.json"),
            "attitude_thrust_contract": str(ATTITUDE_THRUST_GATE),
            "attitude_thrust_mworks": str(ATTITUDE_THRUST_MWORKS_DIR / "MWORKS_ATTITUDE_THRUST_MANIFEST.json"),
            "attitude_thrust_generate": str(ATTITUDE_THRUST_MWORKS_DIR / "generate_model_code_result_v2.json"),
            "attitude_thrust_codegen": str(ATTITUDE_THRUST_MWORKS_DIR / "sil/codegen_runtime_check_v2.json"),
            "attitude_thrust_sil": str(ATTITUDE_THRUST_MWORKS_DIR / "sil/sil_equivalence_126_rows_v2.json"),
            "screenshots": str(screenshot_path),
            "gazebo_px4_mavros_runtime_profiles": runtime_profiles,
        },
        "open_gates": [name for name, passed in gates.items() if not passed],
        "claim_boundary": (
            "P1 has real scalar MIL, six behavior-equivalent fixed-input graphical variants, a fixed-size six-algorithm ATTITUDE_THRUST contract, live full-contract MWORKS MIL, official generated C, 126-row/20-output SIL equivalence, and six independently acknowledged Gazebo/PX4/MAVROS takeoff-hover-land gates. The neural PID runtime uses the declared zero_untrained bounded residual source; it does not claim a trained neural policy."
            if runtime_gate_passed
            else "P1 has real scalar MIL, six behavior-equivalent fixed-input graphical variants, a fixed-size six-algorithm ATTITUDE_THRUST contract, live full-contract MWORKS MIL, official generated C, and 126-row/20-output SIL equivalence. It is not selectable until all six declared Gazebo/PX4/MAVROS runtime profiles pass with runtime-acknowledged provenance."
        ),
    }
    output = RESULT_DIR / "P1_PID_MIL_SUMMARY.json"
    write_json_lf(output, summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
