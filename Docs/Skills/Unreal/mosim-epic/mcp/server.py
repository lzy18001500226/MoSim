#!/usr/bin/env python3
"""MoSim Epic/Fab and scene-source MCP server.

This MCP owns Epic/Fab/Launcher inventory visibility, MoSim scene-source
registry checks, and planning-truth export planning. It does not operate a live
Unreal Editor, edit actors, edit Blueprints, or modify materials.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_UE5 = ROOT / "Scripts" / "UE5"
if str(SCRIPTS_UE5) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_UE5))

from build_scene_source_registry import DEFAULT_OUTPUT as SCENE_SOURCE_REGISTRY
from build_scene_source_registry import build_registry
from check_ue_fab_goal_acceptance import build_report as build_goal_report
from epic_library_index import build_inventory
from epic_library_view import merge_library_view
from plan_scene_truth_export import plan_exports


RENDERER = ROOT / "UE5" / "MoSimSceneLibrary"
TRUTH_ROOT = RENDERER / "Content" / "MworksData" / "scene_truth"
THIS_WRAPPER = ROOT / "Docs" / "Skills" / "Unreal" / "mosim-epic" / "wrappers" / "mosim-epic.sh"

TOOLSET = [
    "epic_library_inventory",
    "epic_scene_library_view",
    "scene_source_registry",
    "scene_source_acceptance",
    "scene_truth_export_plan",
    "tool_boundary",
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel(path)} JSON root is not an object")
    return payload


def scene_registry_payload(refresh: bool = False) -> dict[str, Any]:
    if refresh:
        return build_registry()
    if SCENE_SOURCE_REGISTRY.exists():
        return read_json(SCENE_SOURCE_REGISTRY)
    return {
        "schema": "mosim.unreal_scene_source_registry.missing",
        "missing": rel(SCENE_SOURCE_REGISTRY),
    }


def truth_plan_payload(query: str = "") -> dict[str, Any]:
    return {
        "schema": "mosim.epic.scene_truth_plan.v1",
        "query": query,
        "plans": plan_exports(ROOT / "References" / "UnrealScenes", TRUTH_ROOT, query=query),
    }


def boundary_payload() -> dict[str, Any]:
    return {
        "schema": "mosim.epic_mcp.boundary.v1",
        "mosim-epic": {
            "owns": [
                "sanitized Epic/Fab/Launcher inventory",
                "account-owned/cache/vault state classification",
                "scene-source registry refresh and acceptance gates",
                "truth-export command planning for already-local editable UE scenes",
            ],
            "does_not_own": [
                "live Unreal Editor actor/Blueprint/material operations",
                "Epic/Fab login, OAuth, or password/token handling",
                "Launcher UI automation and Marketplace downloads",
                "raw Launcher webcache dumping",
            ],
        },
        "mosim-unreal": {
            "owns": [
                "running UE Editor health and project context",
                "AssetRegistry-backed scene/asset queries after content is local",
                "controlled editor edits after listener and map are verified",
                "viewport/log diagnostics and scene-truth export execution",
            ],
            "does_not_own": [
                "account-library inventory",
                "Launcher downloads",
                "Fab license or Marketplace decisions",
            ],
        },
    }


def health_payload() -> dict[str, Any]:
    return {
        "schema": "mosim.epic_mcp.health.v1",
        "mcp_server": "mosim-epic",
        "toolset": TOOLSET,
        "scene_source_registry": rel(SCENE_SOURCE_REGISTRY),
        "scene_source_registry_exists": SCENE_SOURCE_REGISTRY.exists(),
        "truth_root": rel(TRUTH_ROOT),
        "truth_root_exists": TRUTH_ROOT.exists(),
        "current_wrapper": rel(THIS_WRAPPER),
    }


def serve() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "Missing MCP Python SDK. Run with: uv run --with mcp python "
            "Docs/Skills/Unreal/mosim-epic/mcp/server.py serve",
            file=sys.stderr,
        )
        return 2

    mcp = FastMCP("mosim-epic")

    @mcp.tool()
    def epic_library_inventory(query: str = "") -> dict[str, Any]:
        """List sanitized local Epic/Fab/Launcher inventory."""
        return build_inventory(query=query)

    @mcp.tool()
    def epic_scene_library_view(query: str = "") -> list[dict[str, Any]]:
        """List merged account/Fab/Vault scene candidates for manual review planning."""
        return merge_library_view(query)

    @mcp.tool()
    def scene_source_registry(refresh: bool = False) -> dict[str, Any]:
        """Return or rebuild the MoSim scene-source registry."""
        return scene_registry_payload(refresh=refresh)

    @mcp.tool()
    def scene_source_acceptance() -> dict[str, Any]:
        """Return gate-level acceptance state for local/Fab scene-source readiness."""
        return build_goal_report()

    @mcp.tool()
    def scene_truth_export_plan(query: str = "") -> dict[str, Any]:
        """Plan Unreal Editor commands for exporting collision/planning truth."""
        return truth_plan_payload(query=query)

    @mcp.tool()
    def tool_boundary() -> dict[str, Any]:
        """Explain the split between mosim-epic and mosim-unreal."""
        return boundary_payload()

    mcp.run()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "serve",
            "dump-health",
            "dump-inventory",
            "dump-view",
            "dump-registry",
            "dump-acceptance",
            "dump-truth-plan",
            "dump-boundary",
            "dump-tools",
        ),
        nargs="?",
        default="serve",
    )
    parser.add_argument("--query", default="")
    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve()

    payload: Any
    if args.command == "dump-health":
        payload = health_payload()
    elif args.command == "dump-inventory":
        payload = build_inventory(query=args.query)
    elif args.command == "dump-view":
        payload = merge_library_view(args.query)
    elif args.command == "dump-registry":
        payload = scene_registry_payload(refresh=False)
    elif args.command == "dump-acceptance":
        payload = build_goal_report()
    elif args.command == "dump-truth-plan":
        payload = truth_plan_payload(query=args.query)
    elif args.command == "dump-boundary":
        payload = boundary_payload()
    else:
        payload = {"schema": "mosim.epic_mcp.tools.v1", "tools": TOOLSET}

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
