#!/usr/bin/env python3
"""Validate that the MoSim reference index covers the current References tree."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / "References"
INDEX = ROOT / "Docs" / "Index" / "reference_project_index.md"
FAMILIES_WITH_CHILD_PROJECTS = {
    "Agent",
    "AirSim",
    "Log",
    "Lab",
    "MWORKS",
    "RflySim",
    "UnrealScenes",
}
AGENT_CATEGORY_DIRS = {
    "Platforms",
    "Control",
    "Gateway",
    "Workflow",
    "Frameworks",
    "Skills",
    "Memory",
    "Security",
    "UI",
    "SDK",
    "Domain",
    "ReviewLater",
}


def tracked_reference_paths() -> set[str] | None:
    """Return tracked reference files, or None outside a Git checkout."""
    if not (ROOT / ".git").exists():
        return None
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--", "References"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git ls-files failed")
    return {line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}


def has_tracked_descendant(path: Path, tracked: set[str] | None) -> bool:
    if tracked is None:
        return True
    prefix = path_text(path).rstrip("/") + "/"
    return any(item.startswith(prefix) for item in tracked)


def collect_expected_paths(tracked: set[str] | None = None) -> list[str]:
    expected: set[str] = set()
    for family_dir in sorted(p for p in REFERENCES.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if not has_tracked_descendant(family_dir, tracked):
            continue
        expected.add(path_text(family_dir))
        if family_dir.name == "Agent":
            expected.update(collect_agent_paths(family_dir, tracked))
            continue
        if family_dir.name in FAMILIES_WITH_CHILD_PROJECTS:
            for child in sorted(p for p in family_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
                if not has_tracked_descendant(child, tracked):
                    continue
                expected.add(path_text(child))
    return sorted(expected)


def collect_agent_paths(agent_dir: Path, tracked: set[str] | None = None) -> set[str]:
    paths: set[str] = set()
    for child in sorted(p for p in agent_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if not has_tracked_descendant(child, tracked):
            continue
        paths.add(path_text(child))
        if child.name in AGENT_CATEGORY_DIRS:
            for project in sorted(p for p in child.iterdir() if p.is_dir() and not p.name.startswith(".")):
                if not has_tracked_descendant(project, tracked):
                    continue
                paths.add(path_text(project))
    return paths


def collect_indexed_paths() -> list[str]:
    text = INDEX.read_text(encoding="utf-8")
    matches = re.findall(r"`(References/[^`]+)`", text)
    return sorted(set(matches))


def path_text(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="return non-zero when coverage is incomplete")
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="include filesystem-only reference imports; default checks the project-tracked tree",
    )
    args = parser.parse_args()

    tracked = None if args.include_untracked else tracked_reference_paths()
    expected = set(collect_expected_paths(tracked))
    indexed = set(collect_indexed_paths())

    missing = sorted(expected - indexed)
    stale = sorted(path for path in indexed if path.startswith("References/") and not (ROOT / path).exists())
    result = {
        "expected_count": len(expected),
        "indexed_count": len(indexed),
        "missing": missing,
        "stale": stale,
        "ok": not missing and not stale,
        "index_path": path_text(INDEX),
        "tracked_only": tracked is not None,
        "tracked_file_count": len(tracked) if tracked is not None else None,
    }

    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"index: {result['index_path']}")
        print(f"expected: {result['expected_count']}")
        print(f"indexed: {result['indexed_count']}")
        print(f"missing: {len(missing)}")
        print(f"stale: {len(stale)}")
        if missing:
            print("missing paths:")
            for item in missing:
                print(f"  - {item}")
        if stale:
            print("stale paths:")
            for item in stale:
                print(f"  - {item}")
        print(f"ok: {result['ok']}")

    return 1 if args.strict and not result["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
