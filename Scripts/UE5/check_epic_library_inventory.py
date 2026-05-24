#!/usr/bin/env python3
"""Health check for MoSim's read-only Epic/Fab/Launcher inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from epic_library_index import build_inventory


DEFAULT_MIN_ACCOUNT_ITEMS = 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Optional query to validate.")
    parser.add_argument("--min-account-items", type=int, default=DEFAULT_MIN_ACCOUNT_ITEMS)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    inventory = build_inventory(query=args.query)
    summary = inventory["summary"]
    checks = {
        "has_launcher_manifest_or_install": (
            summary["launcher_item_count"] > 0 or summary["launcher_install_count"] > 0
        ),
        "has_account_library_items": summary["account_library_item_count"] >= args.min_account_items,
        "has_any_scene_source": (
            summary["account_library_item_count"]
            + summary["fab_asset_count"]
            + summary["vault_cache_project_count"]
            > 0
        ),
    }
    ok = all(checks.values())
    payload = {
        "ok": ok,
        "query": args.query,
        "summary": summary,
        "checks": checks,
        "sample_account_library_items": [
            {
                "display_name": item.get("display_name"),
                "base_app_name": item.get("base_app_name"),
                "versions": item.get("versions", []),
            }
            for item in inventory.get("account_library_items", [])[:8]
        ],
        "roots": inventory["roots"],
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
