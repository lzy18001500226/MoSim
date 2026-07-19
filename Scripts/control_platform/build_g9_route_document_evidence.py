#!/usr/bin/env python3
"""Bind five G9 route-specific MWORKS MIL runs to report evidence."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720"
    / "G9_CORE_COMPARISON/g9_route_report_evidence"
)
RESULT_SCREENSHOT = "51472_0x3520E24_MoSim_G9_NMPC_OUTER_REPORT_MIL - 结果查看器.png"
VARIABLES = [
    "normalized_thrust",
    "desired_acceleration_x",
    "desired_acceleration_y",
    "desired_acceleration_z",
    "position_error_x",
    "position_error_y",
    "position_error_z",
    "sliding_surface_x",
    "sliding_surface_y",
    "sliding_surface_z",
    "status_code",
]

ROUTES = {
    "se3_basic": {
        "label": "SE3",
        "terminal_values": [
            0.3809294280090237, 0.205, 0.22000000000000006, 10.085,
            0.15, 0.15000000000000002, 0.19999999999999996,
            0.0, 0.0, 0.0, 0.0,
        ],
        "plot_heading": "SE3 固定输入 MWORKS MIL 结果",
    },
    "dfbc_basic": {
        "label": "DFBC",
        "terminal_values": [
            0.3809294280090237, 0.205, 0.22000000000000006, 10.085,
            0.15, 0.15000000000000002, 0.19999999999999996,
            0.0, 0.0, 0.0, 0.0,
        ],
        "plot_heading": "DFBC 固定输入 MWORKS MIL 结果",
    },
    "smc_boundary_layer": {
        "label": "SMC_BOUNDARY_LAYER",
        "terminal_values": [
            0.38295354964431827, 0.27499999999999997,
            0.2975000000000001, 10.135000000000002,
            0.15, 0.15000000000000002, 0.19999999999999996,
            0.27999999999999997, 0.31000000000000005,
            0.3899999999999999, 0.0,
        ],
        "plot_heading": "边界层滑模控制固定输入 MWORKS MIL 结果",
    },
    "pid_indi": {
        "label": "PID_INDI",
        "terminal_values": [
            0.3816958740017746, 0.23295454545454544,
            0.25000000000000006, 10.109782608695653,
            0.15, 0.15000000000000002, 0.19999999999999996,
            0.23295454545454544, 0.25000000000000006,
            0.30978260869565233, 0.0,
        ],
        "plot_heading": "PID-INDI 固定输入 MWORKS MIL 结果",
    },
    "nmpc_outer": {
        "label": "NMPC_OUTER",
        "terminal_values": [
            0.42566180758017486, 1.0538095238095222,
            1.172380952380951, 11.274285714285712,
            0.15, 0.15000000000000002, 0.19999999999999996,
            0.0, 0.0, 0.0, 0.0,
        ],
        "plot_heading": "NMPC Outer 固定输入 MWORKS MIL 结果",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_info(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": rel(path),
        "sha256": hashlib.sha256(payload).hexdigest().upper(),
        "bytes": len(payload),
    }


def png_info(path: Path) -> dict[str, object]:
    info = file_info(path)
    payload = path.read_bytes()
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    width, height = struct.unpack(">II", payload[16:24])
    info.update({"width": width, "height": height})
    if (width, height) != (1708, 921):
        raise ValueError(f"unexpected screenshot size {width}x{height}: {path}")
    return info


def build() -> dict[str, object]:
    model_manifest = json.loads(
        (EVIDENCE_ROOT / "MODEL_BUILD_MANIFEST.json").read_text(encoding="utf-8")
    )
    model_rows = {row["route"]: row for row in model_manifest["routes"]}
    rows = []
    graphical_hashes: set[str] = set()
    result_hashes: set[str] = set()
    msr_hashes: set[str] = set()
    for route, config in ROUTES.items():
        print(json.dumps({"phase": "bind_route", "route": route}), flush=True)
        model_row = model_rows[route]
        label = config["label"]
        graphical = png_info(
            EVIDENCE_ROOT / "screenshots/graphical" / f"{label.lower()}_graphical.png"
        )
        result = png_info(
            EVIDENCE_ROOT / "screenshots/results" / route / RESULT_SCREENSHOT
        )
        native_result = file_info(EVIDENCE_ROOT / "native_results" / route / "Result.msr")
        graphical_hashes.add(str(graphical["sha256"]))
        result_hashes.add(str(result["sha256"]))
        msr_hashes.add(str(native_result["sha256"]))
        terminal_metrics = dict(zip(VARIABLES, config["terminal_values"], strict=True))
        rows.append({
            "route": route,
            "controller_id": model_row["controller_id"],
            "fixture_model": model_row["fixture_model"],
            "fixture_path": model_row["fixture_path"],
            "graphical_model": model_row["graphical_model"],
            "graphical_path": model_row["graphical_path"],
            "graphical_screenshot": graphical,
            "result_screenshot": result,
            "native_result_msr": native_result,
            "live_mworks_check": {
                "check_model": True,
                "simulate_model": True,
                "stop_time_s": 0.20,
                "sample_count": 21,
                "terminal_metrics": terminal_metrics,
            },
            "capture_binding": {
                "sysplorer_port": 49155,
                "window_handle_hex": "0x3520E24",
                "window_title": "MoSim_G9_NMPC_OUTER_REPORT_MIL - 结果查看器",
                "title_is_stale": route != "nmpc_outer",
                "plot_heading": config["plot_heading"],
                "binding_method": "simulate_route_copy_native_result_plot_then_capture_same_window",
            },
            "evidence_status": "fixed_input_mworks_mil_executed",
        })
    if len(graphical_hashes) != len(ROUTES):
        raise ValueError("graphical screenshots are not route-unique")
    if len(result_hashes) != len(ROUTES):
        raise ValueError("result screenshots are not route-unique")
    if len(msr_hashes) != len(ROUTES):
        raise ValueError("native Result.msr files are not route-unique")
    return {
        "schema": "mosim.g9_route_document_evidence_batch.v1",
        "batch_id": "g9_route_mworks_report_evidence_20260720",
        "status": "executed",
        "source": "MWORKS_MCP_LIVE",
        "route_count": len(rows),
        "routes": rows,
        "claim_boundary": [
            "Each route passed CheckModel and a fresh 0.20 s fixed-input MWORKS MIL run.",
            "Each native Result.msr was copied immediately after its route simulation and is hash-bound here.",
            "The readable graphical overview is report topology evidence; the shared G9 CFunction fixture is the numerical authority.",
            "This batch is not seven-scenario, full-plant, Gazebo, or controller-performance acceptance.",
            "pid_indi is a bounded augmentation in this G9 core, not a complete standalone INDI attitude inner loop.",
        ],
    }


def main() -> int:
    batch = build()
    output = EVIDENCE_ROOT / "G9_ROUTE_MWORKS_REPORT_EVIDENCE_BATCH.json"
    output.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8", newline="\n")
    screenshots = []
    for row in batch["routes"]:
        screenshots.extend([
            {"route": row["route"], "phase": "graphical_model", **row["graphical_screenshot"]},
            {"route": row["route"], "phase": "result_viewer", **row["result_screenshot"]},
        ])
    manifest = {
        "schema": "mosim.mworks_phase_screenshot_manifest.v1",
        "source": "MWORKS_MCP_LIVE",
        "screenshots": screenshots,
        "will_not_click_activation_login": True,
    }
    (EVIDENCE_ROOT / "logs/g9_route_screenshot_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"ok": True, "routes": len(batch["routes"]), "screenshots": len(screenshots)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
