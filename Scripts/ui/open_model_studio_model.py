#!/usr/bin/env python3
"""Open a Model Studio model in the existing MWORKS Sysplorer session.

This entry point only loads and opens a model. It never checks or simulates the
model, opens a result, starts a flight task, or changes the solver lifecycle.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
LOG = ROOT / "Results" / "ui_platform" / "model_studio_open_model" / "latest.json"
THREE_MODEL_FILE = ROOT / "Models" / "QuadrotorExperiments" / "FormationScenarios" / "FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo"
THREE_MODEL_NAME = "QuadrotorExperiments.FormationScenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop"
LIVE_MODEL_FILE = ROOT / "Models" / "MworksLive" / "package.mo"
LIVE_MODEL_NAME = "MworksLive.RT1OfficialPidShadow50Hz"
MODEL_DECLARATION = re.compile(r"\bmodel\s+([A-Za-z_]\w*)")


def resolve_offline_model(profile_id: str, vehicle_count: int) -> tuple[Path, str]:
    if vehicle_count == 3:
        return THREE_MODEL_FILE, THREE_MODEL_NAME
    catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    entries = list(catalog.get("certified_profiles", [])) + list(catalog.get("custom_profile_proofs", []))
    entry = next((item for item in entries if item.get("profile_id") == profile_id), None)
    if entry is None:
        raise ValueError("profile_not_found_or_not_openable")
    record = ROOT / str(entry["certification_record"])
    certification = json.loads(record.read_text(encoding="utf-8-sig"))
    model_file = ROOT / str(certification["artifacts"]["model_source"])
    declaration = MODEL_DECLARATION.search(model_file.read_text(encoding="utf-8-sig"))
    if declaration is None:
        raise ValueError("model_declaration_not_found")
    return model_file, declaration.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("model", "live"), required=True)
    parser.add_argument("--profile-id", default="")
    parser.add_argument("--vehicle-count", type=int, default=1)
    args = parser.parse_args()
    if args.mode == "live":
        model_file, model_name = LIVE_MODEL_FILE, LIVE_MODEL_NAME
    else:
        model_file, model_name = resolve_offline_model(args.profile_id, args.vehicle_count)
    if not model_file.is_file():
        raise FileNotFoundError(f"model_file_not_found: {model_file}")

    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    import run_sysplorer_mcp_smoke as mcp

    LOG.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "mosim.model_studio.open_model_result.v1",
        "mode": args.mode,
        "profile_id": args.profile_id,
        "model_file": model_file.relative_to(ROOT).as_posix(),
        "model_name": model_name,
        "opened": False,
        "created_at": time.time(),
    }
    client = mcp.JsonlMcpClient(mcp.wrapper_command(mcp.resolve_wrapper(None)), LOG.with_suffix(".jsonl"))
    try:
        result["health"] = mcp.initialize_mcp_client(client)
        loaded = client.call_tool(
            "model_manager",
            {"action": "load_file", "file_path": str(model_file), "force_reload": True, "auto_load_deps": True},
            timeout_s=300,
        )
        result["load"] = loaded
        if not loaded.get("ok"):
            raise RuntimeError(f"model_load_failed: {loaded}")
        opened = client.call_tool(
            "model_manager", {"action": "open", "model_name": model_name}, timeout_s=60
        )
        result["open"] = opened
        if not opened.get("ok"):
            raise RuntimeError(f"model_open_failed: {opened}")

        # model_manager.open can update the session without painting the
        # Sysplorer diagram. Use the documented ModelingPy GUI call as the
        # visibility gate, while keeping simulation and result operations out.
        diagram = client.call_tool(
            "call_code",
            {
                "mode": "run_script",
                "payload": {
                    "python_source": (
                        "import mworks.sysplorer as ModelingPy\n"
                        "try:\n"
                        f"    RUN_SCRIPT_RESULT = {{'opened': ModelingPy.OpenModel({model_name!r}, ModelingPy.ModelView.Diagram)}}\n"
                        "except Exception:\n"
                        f"    RUN_SCRIPT_RESULT = {{'opened': ModelingPy.OpenModel({model_name!r})}}\n"
                    )
                },
            },
            timeout_s=60,
        )
        result["diagram"] = diagram
        nested = diagram.get("run_script_result") if isinstance(diagram, dict) else None
        if isinstance(nested, dict) and "opened" in nested:
            result["opened"] = bool(nested["opened"])
        else:
            result["opened"] = bool(diagram.get("ok"))
        if not result["opened"]:
            raise RuntimeError(f"diagram_open_failed: {diagram}")
    finally:
        client.close()
        LOG.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["opened"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
