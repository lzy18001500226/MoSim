#!/usr/bin/env python3
"""Health check for MoSim's read-only Epic/Fab/Launcher inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from epic_library_index import (
    DEFAULT_FAB_LIBRARY_DIR,
    DEFAULT_LAUNCHER_INSTALLED,
    DEFAULT_LAUNCHER_SAVED_DATA_DIR,
    DEFAULT_MANIFESTS_DIR,
    DEFAULT_VAULT_CACHE_DIR,
    build_inventory,
)


DEFAULT_MIN_ACCOUNT_ITEMS = 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Optional query to validate.")
    parser.add_argument("--min-account-items", type=int, default=DEFAULT_MIN_ACCOUNT_ITEMS)
    parser.add_argument("--manifests-dir", type=Path, default=DEFAULT_MANIFESTS_DIR)
    parser.add_argument("--launcher-installed", type=Path, default=DEFAULT_LAUNCHER_INSTALLED)
    parser.add_argument("--fab-library-dir", type=Path, default=DEFAULT_FAB_LIBRARY_DIR)
    parser.add_argument("--vault-cache-dir", type=Path, default=DEFAULT_VAULT_CACHE_DIR)
    parser.add_argument("--launcher-saved-data-dir", type=Path, default=DEFAULT_LAUNCHER_SAVED_DATA_DIR)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    inventory_kwargs = {
        "manifests_dir": args.manifests_dir,
        "launcher_installed": args.launcher_installed,
        "fab_library_dir": args.fab_library_dir,
        "vault_cache_dir": args.vault_cache_dir,
        "launcher_saved_data_dir": args.launcher_saved_data_dir,
    }
    baseline_inventory = build_inventory(**inventory_kwargs)
    query_inventory = build_inventory(query=args.query, **inventory_kwargs) if args.query else baseline_inventory
    baseline_summary = baseline_inventory["summary"]
    summary = query_inventory["summary"]
    checks = {
        "has_launcher_manifest_or_install": (
            baseline_summary["launcher_item_count"] > 0 or baseline_summary["launcher_install_count"] > 0
        ),
        "has_account_library_items": baseline_summary["account_library_item_count"] >= args.min_account_items,
        "has_any_scene_source": (
            baseline_summary["account_library_item_count"]
            + baseline_summary["fab_asset_count"]
            + baseline_summary["vault_cache_project_count"]
            > 0
        ),
    }
    if args.query:
        checks["query_has_results"] = (
            summary["account_library_item_count"]
            + summary["fab_asset_count"]
            + summary["vault_cache_project_count"]
            + summary["launcher_item_count"]
            + summary["launcher_install_count"]
            > 0
        )
    ok = all(checks.values())
    payload = {
        "ok": ok,
        "query": args.query,
        "baseline_summary": baseline_summary,
        "summary": summary,
        "checks": checks,
        "sample_account_library_items": [
            {
                "display_name": item.get("display_name"),
                "base_app_name": item.get("base_app_name"),
                "versions": item.get("versions", []),
            }
            for item in query_inventory.get("account_library_items", [])[:8]
        ],
        "roots": baseline_inventory["roots"],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"ok: {ok}")
        print(f"summary: {summary}")
        print(f"checks: {checks}")
        for item in payload["sample_account_library_items"]:
            versions = ",".join(item["versions"])
            print(f"- {item['display_name']} [{item['base_app_name']}] {versions}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
