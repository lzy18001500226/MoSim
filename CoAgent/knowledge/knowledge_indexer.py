#!/usr/bin/env python3
"""Local CoAgent knowledge index builder and keyword search helper."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES_JSON = ROOT / "CoAgent" / "knowledge" / "knowledge_sources.json"
INDEX_JSON = ROOT / "Results" / "coagent_knowledge" / "knowledge_index.json"
TEXT_EXTS = {".md", ".txt", ".json"}
MAX_FILE_BYTES = 1_000_000


def load_sources(path: Path = SOURCES_JSON) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_source_files(
    source_path: Path,
    include_names: set[str] | None = None,
    max_files: int | None = None,
) -> list[Path]:
    if source_path.is_file():
        if include_names and source_path.name not in include_names:
            return []
        if source_path.stat().st_size > MAX_FILE_BYTES:
            return []
        return [source_path]
    files = []
    for item in sorted(source_path.rglob("*")):
        if not item.is_file():
            continue
        if item.suffix.lower() not in TEXT_EXTS:
            continue
        if include_names and item.name not in include_names:
            continue
        if item.stat().st_size > MAX_FILE_BYTES:
            continue
        files.append(item)
        if max_files is not None and len(files) >= max_files:
            break
    return files


def excerpt(text: str, limit: int = 220) -> str:
    compact = " ".join(text.split())
    return compact[:limit]


def query_terms(query: str) -> list[str]:
    terms = [term for term in re.split(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", query.lower()) if term]
    return sorted(dict.fromkeys(terms), key=terms.index)


def build_index(index_path: Path = INDEX_JSON) -> dict:
    config = load_sources()
    entries = []
    for source in config["sources"]:
        base = ROOT / source["path"]
        if not base.exists():
            continue
        include_names = set(source.get("include_names", [])) or None
        max_files = source.get("max_files")
        for file_path in iter_source_files(base, include_names=include_names, max_files=max_files):
            rel = str(file_path.relative_to(ROOT)).replace("\\", "/")
            text = file_path.read_text(encoding="utf-8", errors="replace")
            entries.append(
                {
                    "source_id": source["source_id"],
                    "category": source["category"],
                    "priority": source["priority"],
                    "path": rel,
                    "size": len(text),
                    "excerpt": excerpt(text),
                    "text": text,
                }
            )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"count": len(entries), "index_path": str(index_path.relative_to(ROOT)).replace("\\", "/")}


def load_index(index_path: Path = INDEX_JSON) -> dict:
    if not index_path.exists():
        return {"entries": []}
    return json.loads(index_path.read_text(encoding="utf-8"))


def upsert_file(
    file_path: Path,
    *,
    source_id: str,
    category: str,
    priority: int,
    index_path: Path = INDEX_JSON,
) -> dict:
    resolved = file_path if file_path.is_absolute() else ROOT / file_path
    resolved = resolved.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"file path is outside MoSim: {file_path}")
    if not resolved.exists():
        raise SystemExit(f"file path does not exist: {file_path}")
    if resolved.suffix.lower() not in TEXT_EXTS:
        raise SystemExit(f"unsupported text extension: {file_path}")
    text = resolved.read_text(encoding="utf-8", errors="replace")
    rel = str(resolved.relative_to(ROOT)).replace("\\", "/")
    data = load_index(index_path)
    entries = [entry for entry in data.get("entries", []) if entry.get("path") != rel]
    entries.append(
        {
            "source_id": source_id,
            "category": category,
            "priority": priority,
            "path": rel,
            "size": len(text),
            "excerpt": excerpt(text),
            "text": text,
        }
    )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"count": len(entries), "index_path": str(index_path.relative_to(ROOT)).replace("\\", "/"), "path": rel}


def search_index(query: str, index_path: Path = INDEX_JSON, limit: int = 20) -> dict:
    if not index_path.exists():
        raise SystemExit("knowledge index does not exist; run build first")
    data = json.loads(index_path.read_text(encoding="utf-8"))
    needle = query.lower()
    terms = query_terms(query)
    hits = []
    for entry in data["entries"]:
        hay = entry["text"].lower()
        path = entry["path"].lower()
        exact_match = needle in hay or needle in path
        matched_terms = [term for term in terms if term in hay or term in path]
        if not exact_match and not matched_terms:
            continue
        score = entry["priority"]
        if exact_match:
            score += 20
        if needle in path:
            score += 10
        score += hay.count(needle)
        for term in matched_terms:
            if term in path:
                score += 4
            score += min(hay.count(term), 8)
        hits.append(
            {
                "score": score,
                "path": entry["path"],
                "category": entry["category"],
                "excerpt": entry["excerpt"],
                "matched_terms": matched_terms,
                "exact_match": exact_match,
            }
        )
    hits.sort(key=lambda item: (-item["score"], item["path"]))
    return {"query": query, "count": len(hits[:limit]), "hits": hits[:limit]}


def list_sources() -> dict:
    return load_sources()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-sources")
    list_parser.set_defaults(func=lambda _args: list_sources())

    build_parser_cmd = subparsers.add_parser("build")
    build_parser_cmd.set_defaults(func=lambda _args: build_index())

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=20)
    search_parser.set_defaults(func=lambda args: search_index(args.query, limit=args.limit))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
