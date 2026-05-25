#!/usr/bin/env python3
"""MoSim-specific Unreal Engine MCP server.

This server is intentionally narrower than generic Unreal MCP projects.  It
exposes stable MoSim simulator workflow tools around the currently opened UE
project, scene-source registry, listener health, and planning-truth gates.

It does not log in to Epic/Fab, download Marketplace assets, or operate the
Launcher.  Use ``mosim_epic_library`` for read-only Epic/Fab inventory.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from build_scene_source_registry import DEFAULT_OUTPUT as SCENE_SOURCE_REGISTRY
from build_scene_source_registry import build_registry
from check_ue_fab_goal_acceptance import build_report as build_goal_report
from epic_library_view import merge_library_view
from plan_scene_truth_export import plan_exports
from probe_unreal_mcp_listener import default_hosts, probe


ROOT = Path(__file__).resolve().parents[2]
RENDERER = ROOT / "UE5" / "MoSimSceneLibrary"
UPROJECT = RENDERER / "MoSimSceneLibrary.uproject"
DEFAULT_ENGINE = RENDERER / "Config" / "DefaultEngine.ini"
BRIDGE_PLUGIN = ROOT / "UE5" / "Bridge" / "QuadrotorMworksBridge.uplugin"
LEGACY_FLOPPERAM_WRAPPER = ROOT / "Scripts" / "UE5" / "unreal_mcp_legacy_flopperam_wsl_wrapper.sh"
THIS_WRAPPER = ROOT / "Scripts" / "UE5" / "unreal_mcp_wsl_wrapper.sh"


TOOLSET = [
    "ue_health",
    "project_context",
    "scene_source_registry",
    "ue_fab_goal_acceptance",
    "scene_truth_export_plan",
    "epic_scene_library_view",
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


def parse_ini_section_keys(path: Path) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current = ""
    if not path.exists():
        return sections
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections.setdefault(current, {})
            continue
        if current and "=" in line:
            key, value = line.split("=", 1)
            sections[current][key.strip()] = value.strip()
    return sections


def listener_health(timeout: float = 1.0, host: str | None = None, port: int = 55557) -> dict[str, Any]:
    hosts = default_hosts(host)
    results = [probe(candidate, port, timeout) for candidate in hosts]
    return {
        "ok": any(result.ok for result in results),
        "port": port,
        "hosts": [
            {
                "host": result.host,
                "ok": result.ok,
                "error": result.error,
            }
            for result in results
        ],
    }


def windows_unreal_installs() -> list[dict[str, str]]:
    roots = [
        Path("/mnt/d/Program Files/Epic Games"),
        Path("/mnt/c/Program Files/Epic Games"),
    ]
    installs: list[dict[str, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for candidate in sorted(root.glob("UE_*")):
            editor = candidate / "Engine/Binaries/Win64/UnrealEditor.exe"
            if editor.exists():
                installs.append({"version_dir": candidate.name, "editor": rel(editor)})
    return installs


def project_context_payload() -> dict[str, Any]:
    uproject = read_json(UPROJECT) if UPROJECT.exists() else {}
    engine_sections = parse_ini_section_keys(DEFAULT_ENGINE)
    registry = read_json(SCENE_SOURCE_REGISTRY) if SCENE_SOURCE_REGISTRY.exists() else {}
    policy = registry.get("policy", {}) if isinstance(registry, dict) else {}
    plugins = uproject.get("Plugins", []) if isinstance(uproject, dict) else []
    plugin_names = [
        str(item.get("Name"))
        for item in plugins
        if isinstance(item, dict) and item.get("Name")
    ]
    return {
        "schema": "mosim.unreal_engine.project_context.v1",
        "root": rel(ROOT),
        "renderer_project": rel(UPROJECT),
        "renderer_exists": UPROJECT.exists(),
        "bridge_plugin": rel(BRIDGE_PLUGIN),
        "bridge_plugin_exists": BRIDGE_PLUGIN.exists(),
        "engine_association": uproject.get("EngineAssociation", ""),
        "additional_plugin_directories": uproject.get("AdditionalPluginDirectories", []),
        "enabled_plugins": plugin_names,
        "game_default_map": engine_sections.get("/Script/EngineSettings.GameMapsSettings", {}).get(
            "GameDefaultMap", ""
        ),
        "editor_startup_map": engine_sections.get("/Script/EngineSettings.GameMapsSettings", {}).get(
            "EditorStartupMap", ""
        ),
        "primary_scene_source_id": policy.get("primary_scene_source_id", ""),
        "scene_source_registry": rel(SCENE_SOURCE_REGISTRY),
        "scene_source_registry_exists": SCENE_SOURCE_REGISTRY.exists(),
        "local_unreal_installs": windows_unreal_installs(),
    }


def scene_registry_payload(refresh: bool = False) -> dict[str, Any]:
    if refresh:
        return build_registry()
    if SCENE_SOURCE_REGISTRY.exists():
        return read_json(SCENE_SOURCE_REGISTRY)
    return {
        "schema": "mosim.unreal_scene_source_registry.missing",
        "missing": rel(SCENE_SOURCE_REGISTRY),
    }


def health_payload(timeout: float = 1.0, host: str | None = None) -> dict[str, Any]:
    context = project_context_payload()
    return {
        "schema": "mosim.unreal_engine.health.v1",
        "mcp_server": "mosim_unreal_engine_mcp",
        "server_scope": "MoSim UE project context, editor listener health, scene truth workflow",
        "toolset": TOOLSET,
        "project_ok": bool(context["renderer_exists"] and context["bridge_plugin_exists"]),
        "context": context,
        "listener": listener_health(timeout=timeout, host=host),
        "legacy_flopperam_wrapper": rel(LEGACY_FLOPPERAM_WRAPPER),
        "legacy_flopperam_wrapper_exists": LEGACY_FLOPPERAM_WRAPPER.exists(),
        "current_wrapper": rel(THIS_WRAPPER),
    }


def truth_plan_payload(query: str = "") -> dict[str, Any]:
    plans = plan_exports(
        ROOT / "References/UnrealScenes",
        RENDERER / "Content/MworksData/scene_truth",
        query=query,
    )
    return {
        "schema": "mosim.unreal_engine.scene_truth_plan.v1",
        "query": query,
        "plans": plans,
    }


def boundary_payload() -> dict[str, Any]:
    return {
        "schema": "mosim.unreal_engine.boundary.v1",
        "unreal_engine": {
            "owns": [
                "running UE Editor health and project context",
                "AssetRegistry-backed scene/asset queries after content is local",
                "controlled scene edits after listener and map are verified",
                "viewport/log diagnostics",
                "scene truth export and validation",
            ],
            "does_not_own": [
                "Epic/Fab login or OAuth",
                "Launcher UI automation and downloads",
                "raw Launcher webcache/log dumping",
                "claiming account-owned assets are editable before local import",
            ],
        },
        "mosim_epic_library": {
            "owns": [
                "sanitized Epic/Fab/Launcher inventory",
                "account-owned/cache/vault state classification",
                "scene candidate selection and registry preparation",
            ],
            "does_not_own": [
                "UE Editor object graph edits",
                "Blueprint/material graph authoring",
                "scene truth export from an opened map",
            ],
        },
    }


def serve() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "Missing MCP Python SDK. Run with: uv run --with mcp python "
            "Scripts/UE5/mosim_unreal_engine_mcp.py serve",
            file=sys.stderr,
        )
        return 2

    mcp = FastMCP("unreal_engine")

    @mcp.tool()
    def ue_health(timeout_seconds: float = 1.0, host: str = "") -> dict[str, Any]:
        """Check MoSim UE project files and the current editor-side MCP listener."""
        return health_payload(timeout=timeout_seconds, host=host or None)

    @mcp.tool()
    def project_context() -> dict[str, Any]:
        """Return MoSimSceneLibrary project metadata, plugin state, maps, and scene-source id."""
        return project_context_payload()

    @mcp.tool()
    def scene_source_registry(refresh: bool = False) -> dict[str, Any]:
        """Return the MoSim scene-source registry; optionally rebuild it from local inventory."""
        return scene_registry_payload(refresh=refresh)

    @mcp.tool()
    def ue_fab_goal_acceptance() -> dict[str, Any]:
        """Return gate-level acceptance state for the UE/Fab/local-scene objective."""
        return build_goal_report()

    @mcp.tool()
    def scene_truth_export_plan(query: str = "") -> dict[str, Any]:
        """Plan Unreal Editor Python commands for exporting collision/planning truth."""
        return truth_plan_payload(query=query)

    @mcp.tool()
    def epic_scene_library_view(query: str = "") -> list[dict[str, Any]]:
        """Return the sanitized Epic/Fab scene library view for convenience."""
        return merge_library_view(query)

    @mcp.tool()
    def tool_boundary() -> dict[str, Any]:
        """Explain the split between unreal_engine and mosim_epic_library MCP servers."""
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
            "dump-context",
            "dump-registry",
            "dump-goal",
            "dump-truth-plan",
            "dump-boundary",
            "dump-tools",
        ),
        nargs="?",
        default="serve",
    )
    parser.add_argument("--query", default="")
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--host", default="")
    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve()

    payload: Any
    if args.command == "dump-health":
        payload = health_payload(timeout=args.timeout, host=args.host or None)
    elif args.command == "dump-context":
        payload = project_context_payload()
    elif args.command == "dump-registry":
        payload = scene_registry_payload(refresh=False)
    elif args.command == "dump-goal":
        payload = build_goal_report()
    elif args.command == "dump-truth-plan":
        payload = truth_plan_payload(query=args.query)
    elif args.command == "dump-boundary":
        payload = boundary_payload()
    else:
        payload = {"schema": "mosim.unreal_engine.tools.v1", "tools": TOOLSET}

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
