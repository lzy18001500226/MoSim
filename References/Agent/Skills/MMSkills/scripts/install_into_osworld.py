#!/usr/bin/env python3
"""Install MMSkills integration files into an OSWorld checkout."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

AGENT_FILES = [
    "general_agent.py",
    "general_skill_agent.py",
    "general_text_skill_agent.py",
    "_mm_skill_base.py",
    "_mm_skill_planner.py",
    "_mm_skill_state_cards.py",
    "_mm_skill_long_plan.py",
    "_mm_skill_adapter_base.py",
    "mm_skill_agent.py",
    "skill_loader.py",
    "task_skill_resolver.py",
]

RUNNER_FILES = [
    "run.py",
    "lib_run_single.py",
    "lib_results_logger.py",
]


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("osworld_root", type=Path, help="Path to a local OSWorld checkout.")
    parser.add_argument(
        "--with-runner",
        action="store_true",
        help="Also install the MMSkills-aware run.py/lib_run_single.py helper files.",
    )
    parser.add_argument(
        "--with-skills",
        action="store_true",
        help="Copy the public skills subset into OSWorld/skills_library.",
    )
    args = parser.parse_args()
    osworld_root = args.osworld_root.expanduser().resolve()

    for filename in AGENT_FILES:
        copy_file(REPO_ROOT / "mm_agents" / filename, osworld_root / "mm_agents" / filename)
    copy_file(
        REPO_ROOT / "mm_agents" / "utils" / "qwen_vl_utils.py",
        osworld_root / "mm_agents" / "utils" / "qwen_vl_utils.py",
    )

    if args.with_runner:
        for filename in RUNNER_FILES:
            copy_file(REPO_ROOT / "osworld_integration" / filename, osworld_root / filename)

    if args.with_skills:
        copy_tree(REPO_ROOT / "skills_library", osworld_root / "skills_library")
        copy_tree(REPO_ROOT / "task_skill_mappings", osworld_root / "task_skill_mappings")

    print(f"Installed MMSkills integration into {osworld_root}")


if __name__ == "__main__":
    main()
