#!/usr/bin/env python3
"""Bind P8 formation models, screenshots, and MWORKS authority for the report."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "Results/control_platform/p8_formation_mworks_20260717"
OUTPUT_ROOT = ROOT / "Results/control_platform/controller_document_evidence_20260720/P8_FORMATION"
MODES = (
    "leader_follower", "virtual_structure", "consensus", "containment",
    "formation_tracking", "formation_reconfiguration", "fault_tolerant_formation",
    "formation_cbf", "distributed_mpc_formation",
)


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
    mil_path = SOURCE_ROOT / "P8_FORMATION_MWORKS_MIL.json"
    mil = json.loads(mil_path.read_text(encoding="utf-8"))
    by_mode = {row["mode"]: row for row in mil["simulation"]["modes"]}
    routes = []
    for mode in MODES:
        graphical = OUTPUT_ROOT / mode / "screenshots/graphical" / f"{mode}_graphical_model.png"
        result_candidates = sorted((OUTPUT_ROOT / mode / "screenshots/result_capture").glob("*.png"))
        if len(result_candidates) != 1:
            raise ValueError(f"expected one result screenshot for {mode}, found {len(result_candidates)}")
        routes.append({
            "mode": mode,
            "graphical_model": rel(SOURCE_ROOT / "models/graphical_variants" / f"MoSim_P8_{mode.upper()}_GRAPHICAL_MIL.mo"),
            "numerical_model": rel(SOURCE_ROOT / "models" / f"MoSim_P8_{mode.upper()}_MIL.mo"),
            "graphical_screenshot": png_info(graphical),
            "result_screenshot": png_info(result_candidates[0]),
            "mworks_mil_summary": by_mode[mode],
        })
    return {
        "schema": "mosim.controller_document_evidence_batch.v1",
        "batch_id": "p8_formation_mworks_evidence_20260720",
        "status": "passed_with_documented_boundaries",
        "source": "MWORKS_MCP_LIVE",
        "live_mworks_touched": True,
        "sysplorer_port": 49155,
        "route_count": len(routes),
        "routes": routes,
        "numerical_authority": rel(mil_path),
        "generated_sil_authority": rel(SOURCE_ROOT / "sil/P8_GENERATED_SIL_EQUIVALENCE.json"),
        "native_result_msr": None,
        "claim_boundary": [
            "Each route-specific graphical fixture passed real MWORKS CheckModel and a 0.4 s simulation; it documents topology rather than replacing the CFunction numerical implementation.",
            "Each result-viewer screenshot is bound to the corresponding original nine-mode CFunction MWORKS MIL fixture.",
            "The accepted evidence covers fixed-size three-UAV formation-reference generation; complex-map reconfigurable obstacle avoidance remains separate.",
            "No Result.msr is promoted because an exact native file binding was not established.",
        ],
    }


def main() -> int:
    batch = build()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "P8_FORMATION_MWORKS_EVIDENCE_BATCH.json").write_text(
        json.dumps(batch, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    screenshots = []
    for route in batch["routes"]:
        screenshots.extend([
            {"mode": route["mode"], "phase": "graphical_model", **route["graphical_screenshot"]},
            {"mode": route["mode"], "phase": "result_viewer", **route["result_screenshot"]},
        ])
    manifest = {
        "schema": "mosim.mworks_phase_screenshot_manifest.v1",
        "source": "MWORKS_MCP_LIVE",
        "screenshots": screenshots,
        "will_not_click_activation_login": True,
    }
    log_dir = OUTPUT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "screenshot_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"ok": True, "routes": len(batch["routes"]), "screenshots": len(screenshots)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
