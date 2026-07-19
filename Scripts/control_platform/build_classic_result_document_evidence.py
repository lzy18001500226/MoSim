#!/usr/bin/env python3
"""Bind ten classic-controller MWORKS result screenshots to report evidence."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "Results/control_platform/controller_document_evidence_20260720"
RESULT_LEAF = "51472_0x3520E24_MoSim_Classic_H2_STATE_FEEDBACK_MIL - 结果查看器.png"
MATRIX_PATH = (
    ROOT
    / "Results/control_platform/classic_controller_closeout_20260717"
    / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
)

ROUTES = {
    "official_pid": {
        "cohort": "G9_CORE_COMPARISON",
        "model": "Results/control_platform/controller_document_evidence_20260720/G9_CORE_COMPARISON/official_pid/models/MoSim_OFFICIAL_PID_REPORT_MIL.mo",
        "graphical": "Results/control_platform/g5_mworks_closeout_20260716/official_pid/screenshots/40544_0x11409CE_AWFF_PID_Sysblock_Demo_SIL_Constant_QuadrotorControllerBlocks_ - Sysplorer _教育版_.png",
        "terminal_variable": "thrust_command",
        "terminal_value": 1.7025000000000001,
        "stop_time_s": 0.5,
        "numeric_authority": "Results/control_platform/controller_family_final_acceptance_20260717/g9_core/official_pid/takeoff_hover_land_retry2/PX4CTRL_BASIC_MISSION_METRICS.json",
        "native_result_msr": "Results/mworks_generated_profiles/cert-official-pid-20260719-v2/native_result/MoSimGenerated_cert_official_pid_20260719_v2/Result.msr",
    },
    "lqr_baseline": {
        "cohort": "P10_CLASSIC_RECONCILIATION",
        "model": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/models/MoSim_WaveA_LQR_MIL.mo",
        "graphical": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/diagrams/MoSim_WaveA_LQR_MIL.png",
        "terminal_value": 0.4470204082,
        "numeric_authority": "Results/control_platform/wave_a_generated_gazebo_20260718/lqr_baseline/takeoff_hover_land_retry3_px4_startup/PX4CTRL_BASIC_MISSION_METRICS.json",
    },
    "lqi_baseline": {
        "cohort": "P10_CLASSIC_RECONCILIATION",
        "model": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/models/MoSim_WaveA_LQI_MIL.mo",
        "graphical": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/diagrams/MoSim_WaveA_LQI_MIL.png",
        "terminal_value": 0.4474281633,
        "numeric_authority": "Results/control_platform/wave_a_generated_gazebo_20260718/lqi_baseline/takeoff_hover_land_retry4_ram_dataman_wait120/PX4CTRL_BASIC_MISSION_METRICS.json",
    },
    "so3_attitude": {
        "cohort": "P10_CLASSIC_RECONCILIATION",
        "model": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/models/MoSim_WaveA_SO3_MIL.mo",
        "graphical": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/diagrams/MoSim_WaveA_SO3_MIL.png",
        "terminal_value": 0.3702254036,
        "numeric_authority": "Results/control_platform/wave_a_generated_gazebo_20260718/so3_attitude/takeoff_hover_land_r1_ram_dataman_wait120/PX4CTRL_BASIC_MISSION_METRICS.json",
    },
    "backstepping_baseline": {
        "cohort": "P10_CLASSIC_RECONCILIATION",
        "model": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/models/MoSim_WaveA_BACKSTEPPING_MIL.mo",
        "graphical": "Results/control_platform/g5_mworks_closeout_20260716/wave_a/diagrams/MoSim_WaveA_BACKSTEPPING_MIL.png",
        "terminal_value": 0.4620846939,
        "numeric_authority": "Results/control_platform/wave_a_generated_gazebo_20260718/backstepping_baseline/takeoff_hover_land_r1_ram_dataman_wait120/PX4CTRL_BASIC_MISSION_METRICS.json",
    },
    "pole_placement_luenberger": {
        "cohort": "P11_CLASSIC_ADDITIONS",
        "model": "Results/control_platform/classic_controller_closeout_20260717/mworks/models/MoSim_Classic_POLE_PLACEMENT_LUENBERGER_MIL.mo",
        "graphical": "Results/control_platform/classic_controller_closeout_20260717/mworks/diagrams/pole_placement_luenberger.png",
        "terminal_value": 0.3246651570,
        "numeric_authority": "Results/control_platform/classic_controller_closeout_20260717/mworks/metrics/pole_placement_luenberger_mil_metrics.json",
    },
    "mrac": {
        "cohort": "P11_CLASSIC_ADDITIONS",
        "model": "Results/control_platform/classic_controller_closeout_20260717/mworks/models/MoSim_Classic_MRAC_MIL.mo",
        "graphical": "Results/control_platform/classic_controller_closeout_20260717/mworks/diagrams/mrac.png",
        "terminal_value": 0.3290157374,
        "numeric_authority": "Results/control_platform/classic_controller_closeout_20260717/mworks/metrics/mrac_mil_metrics.json",
    },
    "ndi": {
        "cohort": "P11_CLASSIC_ADDITIONS",
        "model": "Results/control_platform/classic_controller_closeout_20260717/mworks/models/MoSim_Classic_NDI_MIL.mo",
        "graphical": "Results/control_platform/classic_controller_closeout_20260717/mworks/diagrams/ndi.png",
        "terminal_value": 0.3233310226,
        "numeric_authority": "Results/control_platform/classic_controller_closeout_20260717/mworks/metrics/ndi_mil_metrics.json",
    },
    "fopid": {
        "cohort": "P11_CLASSIC_ADDITIONS",
        "model": "Results/control_platform/classic_controller_closeout_20260717/mworks/models/MoSim_Classic_FOPID_MIL.mo",
        "graphical": "Results/control_platform/classic_controller_closeout_20260717/mworks/diagrams/fopid.png",
        "terminal_value": 0.3468217868,
        "numeric_authority": "Results/control_platform/classic_controller_closeout_20260717/mworks/metrics/fopid_mil_metrics.json",
    },
    "h2_state_feedback": {
        "cohort": "P11_CLASSIC_ADDITIONS",
        "model": "Results/control_platform/classic_controller_closeout_20260717/mworks/models/MoSim_Classic_H2_STATE_FEEDBACK_MIL.mo",
        "graphical": "Results/control_platform/classic_controller_closeout_20260717/mworks/diagrams/h2_state_feedback.png",
        "terminal_value": 0.3244017987,
        "numeric_authority": "Results/control_platform/classic_controller_closeout_20260717/mworks/metrics/h2_state_feedback_mil_metrics.json",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def png_info(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    width, height = struct.unpack(">II", payload[16:24])
    return {
        "path": rel(path),
        "sha256": hashlib.sha256(payload).hexdigest().upper(),
        "width": width,
        "height": height,
        "bytes": len(payload),
    }


def build() -> dict[str, object]:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    matrix_rows = {row["controller"]: row for row in matrix["rows"]}
    routes = []
    for route, config in ROUTES.items():
        result_path = (
            OUTPUT_ROOT
            / config["cohort"]
            / route
            / "screenshots/result_capture"
            / RESULT_LEAF
        )
        graphical_path = ROOT / config["graphical"]
        for required in (ROOT / config["model"], graphical_path, result_path, ROOT / config["numeric_authority"]):
            if not required.is_file():
                raise FileNotFoundError(required)
        row = matrix_rows[route]
        routes.append({
            "route": route,
            "cohort": config["cohort"],
            "matrix_status": row["status"],
            "claim_ceiling": row["claim_ceiling"],
            "model": config["model"],
            "graphical_screenshot": png_info(graphical_path),
            "result_screenshot": png_info(result_path),
            "live_mworks_check": {
                "check_model": True,
                "simulate_model": True,
                "stop_time_s": config.get("stop_time_s", 0.03),
                "terminal_variable": config.get("terminal_variable", "normalized_thrust"),
                "terminal_value": config["terminal_value"],
            },
            "numeric_authority": config["numeric_authority"],
            "native_result_msr": config.get("native_result_msr"),
            "capture_binding": {
                "sysplorer_port": 49155,
                "window_handle_hex": "0x3520E24",
                "window_title": "MoSim_Classic_H2_STATE_FEEDBACK_MIL - 结果查看器",
                "plot_heading": route,
                "title_is_stale": route != "h2_state_feedback",
                "binding_method": "simulate_route_then_create_plot_then_capture_same_result_window",
            },
        })
    return {
        "schema": "mosim.controller_document_evidence_batch.v1",
        "batch_id": "classic_result_mworks_evidence_20260720",
        "status": "executed_with_documented_performance_blockers",
        "source": "MWORKS_MCP_LIVE",
        "route_count": len(routes),
        "routes": routes,
        "claim_boundary": [
            "The screenshots show route-specific fixed-input MWORKS MIL results and do not constitute seven-scenario acceptance.",
            "All ten matrix rows remain executed_blocked at their declared deployment acceptance ceilings.",
            "The reusable result-viewer window retained a stale H2 title; route identity is bound by the immediately preceding simulation, plot heading, selected result tree, route directory, and screenshot hash.",
            "Only official_pid retains a separately certified native Result.msr binding; no native result is promoted for the other nine routes.",
        ],
    }


def main() -> int:
    batch = build()
    batch_path = OUTPUT_ROOT / "P10_P11_CLASSIC_RESULT_EVIDENCE_BATCH.json"
    batch_path.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8", newline="\n")
    screenshots = []
    for route in batch["routes"]:
        screenshots.extend([
            {"route": route["route"], "phase": "graphical_model", **route["graphical_screenshot"]},
            {"route": route["route"], "phase": "result_viewer", **route["result_screenshot"]},
        ])
    log_dir = OUTPUT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "classic_result_screenshot_manifest.json").write_text(
        json.dumps({
            "schema": "mosim.mworks_phase_screenshot_manifest.v1",
            "source": "MWORKS_MCP_LIVE",
            "screenshots": screenshots,
            "will_not_click_activation_login": True,
        }, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"ok": True, "routes": len(batch["routes"]), "screenshots": len(screenshots)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
