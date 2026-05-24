#!/usr/bin/env python3
"""Plan the Unreal Editor commands needed to export MoSim scene truth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_scene_source import DEFAULT_SCENE_ROOT, DEFAULT_TRUTH_ROOT, audit_scene_root
from export_unreal_scene_truth import slug


ROOT = Path(__file__).resolve().parents[2]


def quote(path: Path | str) -> str:
    return f'"{path}"'


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def to_windows_path(path: Path | str) -> str:
    text = str(path)
    if text.startswith("/mnt/") and len(text) > 6 and text[6] == "/":
        drive = text[5].upper()
        rest = text[7:].replace("/", "\\")
        return f"{drive}:\\{rest}"
    return text.replace("/", "\\")


def plan_exports(scene_root: Path, truth_root: Path, query: str = "") -> list[dict[str, str]]:
    rows = audit_scene_root(scene_root)
    plans: list[dict[str, str]] = []
    query_lower = query.lower()
    for row in rows:
        name = str(row["name"])
        if query_lower and query_lower not in name.lower():
            continue
        map_id = slug(name)
        output = truth_root / f"{map_id}_collision_truth.json"
        uproject_path = resolve_project_path(str(row["uproject_path"]))
        script_path = ROOT / "Scripts" / "UE5" / "export_unreal_scene_truth.py"
        map_sample = str(row["umap_samples"][0]) if row["umap_samples"] else ""
        map_sample_path = resolve_project_path(map_sample) if map_sample else None
        plans.append(
            {
                "name": name,
                "uproject_path": to_windows_path(uproject_path),
                "recommended_map_sample": to_windows_path(map_sample_path) if map_sample_path else "",
                "truth_output": str(output),
                "editor_python_command": (
                    f"py {quote(to_windows_path(script_path))} export "
                    f"--scene-id {map_id} --map-id {map_id} "
                    f"--output {quote(to_windows_path(output))}"
                ),
                "validate_command": (
                    "uv run python Scripts/UE5/export_unreal_scene_truth.py validate "
                    f"{quote(output)}"
                ),
                "audit_command": "uv run python Scripts/UE5/audit_scene_source.py",
            }
        )
    return plans


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-root", type=Path, default=DEFAULT_SCENE_ROOT)
    parser.add_argument("--truth-root", type=Path, default=DEFAULT_TRUTH_ROOT)
    parser.add_argument("--query", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plans = plan_exports(args.scene_root, args.truth_root, args.query)
    if args.json:
        print(json.dumps(plans, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for plan in plans:
            print(f"Scene: {plan['name']}")
            print(f"  Project: {plan['uproject_path']}")
            print(f"  Map sample: {plan['recommended_map_sample']}")
            print("  Run inside Unreal Editor Python:")
            print(f"    {plan['editor_python_command']}")
            print("  Then run in MoSim shell:")
            print(f"    {plan['validate_command']}")
            print(f"    {plan['audit_command']}")
    return 0 if plans else 1


if __name__ == "__main__":
    raise SystemExit(main())
