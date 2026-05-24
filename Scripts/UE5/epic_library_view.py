#!/usr/bin/env python3
"""Human-readable Epic/Fab library view for MoSim scene selection."""

from __future__ import annotations

import argparse
import json
from typing import Any

from epic_library_index import build_inventory, filter_items


def normalized_key(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def merge_library_view(query: str = "") -> list[dict[str, Any]]:
    inventory = build_inventory()
    rows: dict[str, dict[str, Any]] = {}

    def row_for(display_name: str) -> dict[str, Any]:
        key = normalized_key(display_name)
        return rows.setdefault(
            key,
            {
                "display_name": display_name,
                "account_app_names": [],
                "versions": [],
                "fab_cache_titles": [],
                "vault_cache_names": [],
                "local_cache_paths": [],
                "uproject_paths": [],
                "states": [],
            },
        )

    for item in inventory.get("account_library_items", []):
        row = row_for(str(item.get("display_name", "")))
        row["account_app_names"].extend(item.get("app_names", []))
        row["versions"].extend(item.get("versions", []))
        row["states"].append("account_owned")

    for item in inventory.get("fab_assets", []):
        title = str(item.get("title", "")).strip() or str(item.get("cache_path", ""))
        row = row_for(title)
        row["fab_cache_titles"].append(title)
        if item.get("cache_path"):
            row["local_cache_paths"].append(item["cache_path"])
        if item.get("has_local_cache"):
            row["states"].append("fab_cached")

    for item in inventory.get("vault_cache_projects", []):
        name = str(item.get("cache_name", "")).strip()
        row = row_for(name)
        row["vault_cache_names"].append(name)
        if item.get("cache_path"):
            row["local_cache_paths"].append(item["cache_path"])
        if item.get("uproject_path"):
            row["uproject_paths"].append(item["uproject_path"])
        row["states"].append("vault_cached_project" if item.get("has_uproject") else "vault_cached_asset")

    view = []
    for row in rows.values():
        for key in ("account_app_names", "versions", "fab_cache_titles", "vault_cache_names", "local_cache_paths", "uproject_paths", "states"):
            row[key] = sorted(set(row[key]))
        row["installed_or_cached"] = bool(
            row["local_cache_paths"] or row["uproject_paths"] or "fab_cached" in row["states"]
        )
        row["openable_project"] = bool(row["uproject_paths"])
        view.append(row)

    view = sorted(view, key=lambda item: item["display_name"].lower())
    if query:
        view = filter_items(view, query)
    return view


def print_table(rows: list[dict[str, Any]]) -> None:
    print(f"{'state':<24} {'project':<7} {'name'}")
    print("-" * 80)
    for row in rows:
        state = ",".join(row["states"])
        project = "yes" if row["openable_project"] else "no"
        print(f"{state[:24]:<24} {project:<7} {row['display_name']}")
        if row["versions"]:
            print(f"{'':<24} {'':<7} versions: {', '.join(row['versions'])}")
        if row["uproject_paths"]:
            print(f"{'':<24} {'':<7} uproject: {row['uproject_paths'][0]}")
        elif row["local_cache_paths"]:
            print(f"{'':<24} {'':<7} cache: {row['local_cache_paths'][0]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Filter merged view by text.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table.")
    args = parser.parse_args(argv)

    rows = merge_library_view(args.query)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_table(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
