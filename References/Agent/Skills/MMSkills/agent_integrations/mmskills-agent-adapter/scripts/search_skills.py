#!/usr/bin/env python3
"""Search the public MMSkills preview index on Hugging Face."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DATASET = "zhangkangning/mmskills"
CONFIG = "skills_preview"
SPLIT = "train"
ROWS_ENDPOINT = "https://datasets-server.huggingface.co/rows"


def cache_root() -> Path:
    return Path(os.environ.get("MMSKILLS_HOME", "~/.cache/mmskills")).expanduser()


def cache_path() -> Path:
    return cache_root() / "skills_preview_index.json"


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "mmskills-agent-adapter/0.1"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503, 504}:
                raise
        except urllib.error.URLError as error:
            last_error = error
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def fetch_index() -> list[dict]:
    rows: list[dict] = []
    offset = 0
    length = 100
    total = None

    while total is None or offset < total:
        params = urllib.parse.urlencode(
            {
                "dataset": DATASET,
                "config": CONFIG,
                "split": SPLIT,
                "offset": offset,
                "length": length,
            }
        )
        payload = fetch_json(f"{ROWS_ENDPOINT}?{params}")
        total = int(payload.get("num_rows_total", 0))
        batch = payload.get("rows", [])
        if not batch:
            break

        for item in batch:
            row = item.get("row", {})
            rows.append(
                {
                    "package": row.get("package", ""),
                    "domain": row.get("domain", ""),
                    "skill": row.get("skill", ""),
                    "skill_title": row.get("skill_title", ""),
                    "skill_path": row.get("skill_path", ""),
                    "state_cards": row.get("state_cards", 0),
                    "views": row.get("views", 0),
                    "view_types": row.get("view_types", ""),
                    "procedure_words": row.get("procedure_words", 0),
                }
            )
        offset += len(batch)

    cache_path().parent.mkdir(parents=True, exist_ok=True)
    cache_path().write_text(json.dumps({"fetched_at": int(time.time()), "rows": rows}, indent=2))
    return rows


def load_index(refresh: bool = False) -> list[dict]:
    path = cache_path()
    if not refresh and path.exists():
        try:
            return json.loads(path.read_text()).get("rows", [])
        except Exception:
            pass
    return fetch_index()


def normalize(value: str) -> str:
    return " ".join(value.replace("_", " ").replace("-", " ").lower().split())


def score(row: dict, tokens: list[str]) -> int:
    if not tokens:
        return 1
    title = normalize(row.get("skill_title", ""))
    skill = normalize(row.get("skill", ""))
    domain = normalize(row.get("domain", ""))
    package = normalize(row.get("package", ""))
    path = normalize(row.get("skill_path", ""))
    text = " ".join([title, skill, domain, package, path])

    value = 0
    for token in tokens:
        if token in title:
            value += 5
        if token in skill:
            value += 4
        if token in domain:
            value += 3
        if token in package:
            value += 2
        if token in text:
            value += 1
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*", help="Search terms, for example: chrome bookmark")
    parser.add_argument("--package", choices=["ubuntu", "mac", "vab_minecraft", "mario"], help="Restrict package")
    parser.add_argument("--domain", help="Restrict domain, for example: chrome or productivity")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results to show")
    parser.add_argument("--refresh", action="store_true", help="Refresh cached Hugging Face index")
    parser.add_argument("--json", action="store_true", help="Print JSON results")
    args = parser.parse_args()

    rows = load_index(refresh=args.refresh)
    if args.package:
        rows = [row for row in rows if row.get("package") == args.package]
    if args.domain:
        wanted = normalize(args.domain)
        rows = [row for row in rows if normalize(row.get("domain", "")) == wanted]

    tokens = normalize(" ".join(args.query)).split()
    ranked = [(score(row, tokens), row) for row in rows]
    ranked = [(item_score, row) for item_score, row in ranked if item_score > 0]
    ranked.sort(key=lambda item: (-item[0], item[1].get("package", ""), item[1].get("domain", ""), item[1].get("skill", "")))
    results = [row for _, row in ranked[: args.limit]]

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    if not results:
        print("No matching MMSkills found.", file=sys.stderr)
        return 1

    for index, row in enumerate(results, start=1):
        package_dir = row["skill_path"].removesuffix("/SKILL.md")
        print(f"{index}. {row['skill_title']} [{row['package']}/{row['domain']}]")
        print(f"   skill: {row['skill']}")
        print(f"   path:  {package_dir}")
        print(f"   cards: {row['state_cards']} states, {row['views']} views")
        print(f"   download: python scripts/download_skill.py {package_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
