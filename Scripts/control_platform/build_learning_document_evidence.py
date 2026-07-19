#!/usr/bin/env python3
"""Bind P9 learning models, screenshots, and current evidence authorities."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "Results/control_platform/p9_learning_mworks_20260717"
OUTPUT_ROOT = ROOT / "Results/control_platform/controller_document_evidence_20260720/P9_LEARNING"
ROUTES = {
    "trained_neural_residual": "MoSim_P9_TRAINED_NEURAL_RESIDUAL",
    "rl_gain_scheduler": "MoSim_P9_RL_GAIN_SCHEDULER",
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


def one_png(folder: Path) -> Path:
    candidates = sorted(folder.glob("*.png"))
    if len(candidates) != 1:
        raise ValueError(f"expected one PNG under {folder}, found {len(candidates)}")
    return candidates[0]


def build() -> dict[str, object]:
    mil_path = SOURCE_ROOT / "MWORKS_MIL_EVIDENCE.json"
    mil = json.loads(mil_path.read_text(encoding="utf-8"))
    by_route = {route: mil["models"][route] for route in ROUTES}
    routes = []
    for route, prefix in ROUTES.items():
        routes.append({
            "route": route,
            "graphical_model": rel(SOURCE_ROOT / "models/graphical_variants" / f"{prefix}_GRAPHICAL_MIL.mo"),
            "numerical_model": rel(SOURCE_ROOT / "models" / f"{prefix}_MIL.mo"),
            "graphical_screenshot": png_info(one_png(OUTPUT_ROOT / route / "screenshots/graphical")),
            "result_screenshot": png_info(one_png(OUTPUT_ROOT / route / "screenshots/result_capture")),
            "graphical_live_check": {
                "check_model": True,
                "simulate_model": True,
                "stop_time_s": 0.4,
            },
            "numerical_live_check": {
                "check_model": True,
                "simulate_model": True,
                "stop_time_s": 0.5,
            },
            "mworks_mil_summary": by_route[route],
        })
    return {
        "schema": "mosim.controller_document_evidence_batch.v1",
        "batch_id": "p9_learning_mworks_evidence_20260720",
        "status": "executed_with_blocked_performance_acceptance",
        "source": "MWORKS_MCP_LIVE",
        "live_mworks_touched": True,
        "sysplorer_port": 49155,
        "route_count": len(routes),
        "routes": routes,
        "numerical_authority": rel(mil_path),
        "codegen_authority": rel(SOURCE_ROOT / "MWORKS_MIL_CODEGEN_EVIDENCE.json"),
        "generated_sil_authority": rel(SOURCE_ROOT / "sil/P9_GENERATED_SIL_EQUIVALENCE.json"),
        "runtime_authority": "Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json",
        "native_result_msr": None,
        "claim_boundary": [
            "Each graphical fixture documents the learning-control topology and does not replace the original CFunction numerical implementation.",
            "Each result-viewer screenshot is bound to the corresponding original P9 MWORKS MIL fixture.",
            "Both routes executed through MWORKS MIL, generated-C SIL, and bounded Gazebo A/B, but strict performance acceptance remains blocked.",
            "Both learning routes remain experimental and selectable=false; no stable superiority claim is made.",
            "No Result.msr is promoted because an exact native file binding was not established.",
        ],
    }


def main() -> int:
    batch = build()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "P9_LEARNING_MWORKS_EVIDENCE_BATCH.json").write_text(
        json.dumps(batch, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    screenshots = []
    for route in batch["routes"]:
        screenshots.extend([
            {"route": route["route"], "phase": "graphical_model", **route["graphical_screenshot"]},
            {"route": route["route"], "phase": "result_viewer", **route["result_screenshot"]},
        ])
    log_dir = OUTPUT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "screenshot_manifest.json").write_text(
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
