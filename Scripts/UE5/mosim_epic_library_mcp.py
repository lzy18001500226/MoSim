#!/usr/bin/env python3
"""MCP wrapper exposing the local Epic/Fab library inventory to Codex."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from epic_library_index import build_inventory
from epic_library_view import merge_library_view


def inventory(query: str = "") -> dict[str, Any]:
    return build_inventory(query=query)


def dump_json(query: str = "") -> int:
    print(json.dumps(inventory(query), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def dump_view(query: str = "") -> int:
    print(json.dumps(merge_library_view(query), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def serve() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "Missing MCP Python SDK. Run with: uv run --with mcp python "
            "Scripts/UE5/mosim_epic_library_mcp.py serve",
            file=sys.stderr,
        )
        return 2

    mcp = FastMCP("mosim_epic_library")

    @mcp.tool()
    def list_epic_library(query: str = "") -> dict[str, Any]:
        """List local Epic Launcher installs, account cache entries, and Fab/Vault assets."""
        return inventory(query)

    @mcp.tool()
    def list_fab_assets(query: str = "") -> list[dict[str, Any]]:
        """List local Fab/Vault cached assets, optionally filtered by text."""
        return inventory(query).get("fab_assets", [])

    @mcp.tool()
    def list_unreal_installs(query: str = "") -> list[dict[str, Any]]:
        """List local Unreal Engine/plugin install records from Epic manifests."""
        data = inventory(query)
        return data.get("launcher_items", []) + data.get("launcher_installs", [])

    @mcp.tool()
    def list_account_library_items(query: str = "") -> list[dict[str, Any]]:
        """List allowlisted Epic account library items inferred from local Launcher cache."""
        return inventory(query).get("account_library_items", [])

    @mcp.tool()
    def list_vault_cache_projects(query: str = "") -> list[dict[str, Any]]:
        """List local old-style VaultCache projects and any discovered .uproject paths."""
        return inventory(query).get("vault_cache_projects", [])

    @mcp.tool()
    def list_scene_library_view(query: str = "") -> list[dict[str, Any]]:
        """List merged account/Fab/Vault scene candidates for manual review planning."""
        return merge_library_view(query)

    mcp.run()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("serve", "dump-json", "dump-view"), nargs="?", default="serve")
    parser.add_argument("--query", default="")
    args = parser.parse_args(argv)

    if args.command == "dump-json":
        return dump_json(args.query)
    if args.command == "dump-view":
        return dump_view(args.query)
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
