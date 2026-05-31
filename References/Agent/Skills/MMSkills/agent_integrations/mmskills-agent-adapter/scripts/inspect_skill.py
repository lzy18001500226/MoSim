#!/usr/bin/env python3
"""Inspect a downloaded MMSkills package and print agent read-order guidance."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def find_skill_dir(path: Path) -> Path:
    path = path.expanduser()
    if path.is_file() and path.name == "SKILL.md":
        return path.parent
    if (path / "SKILL.md").exists():
        return path
    raise FileNotFoundError(f"No SKILL.md found at {path}")


def frontmatter(markdown: str) -> tuple[dict, str]:
    if not markdown.startswith("---\n"):
        return {}, markdown
    end = markdown.find("\n---", 4)
    if end < 0:
        return {}, markdown
    meta = {}
    for line in markdown[4:end].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta, markdown[end + 4 :].lstrip()


def first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    return "MMSkills package"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Downloaded package directory or SKILL.md")
    parser.add_argument("--show-skill", action="store_true", help="Print full SKILL.md after the summary")
    args = parser.parse_args()

    skill_dir = find_skill_dir(args.path)
    skill_text = (skill_dir / "SKILL.md").read_text()
    meta, body = frontmatter(skill_text)
    runtime_path = skill_dir / "runtime_state_cards.json"
    runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else {}
    states = runtime.get("states") or runtime.get("state_cards") or []
    images = sorted((skill_dir / "Images").glob("*")) if (skill_dir / "Images").exists() else []

    print(f"Skill: {meta.get('name') or first_heading(body)}")
    print(f"Path:  {skill_dir}")
    if meta.get("description"):
        print(f"Description: {meta['description']}")
    print(f"Runtime states: {len(states)}")
    print(f"Images: {len([item for item in images if item.is_file()])}")
    print("")
    print("Recommended read order for an agent:")
    print("1. Read SKILL.md for procedure, applicability, and failure modes.")
    print("2. Read runtime_state_cards.json when current UI state or verification is ambiguous.")
    print("3. Open Images/* only for state matching, visual grounding, or verification.")

    if states:
        print("")
        print("Runtime state names:")
        for state in states[:10]:
            print(f"- {state.get('state_name') or state.get('state_id')}")
        if len(states) > 10:
            print(f"- ... {len(states) - 10} more")

    if args.show_skill:
        print("\n--- SKILL.md ---\n")
        print(skill_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
