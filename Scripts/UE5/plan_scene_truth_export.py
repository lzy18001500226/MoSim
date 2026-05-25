#!/usr/bin/env python3
"""Plan the Unreal Editor commands needed to export MoSim scene truth."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_scene_source import (
    DEFAULT_SCENE_ROOT,
    DEFAULT_TRUTH_ROOT,
    audit_project,
    find_uprojects,
    read_default_map_packages,
)
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


def map_file_from_package(project_root: Path, package: str) -> Path | None:
    if not package.startswith("/Game/"):
        return None
    candidate = project_root / "Content" / (package.removeprefix("/Game/") + ".umap")
    return candidate if candidate.exists() else None


def recommend_project_map(uproject_path: Path) -> tuple[str, Path | None]:
    """Return a fast map recommendation without scanning every project asset."""
    project_root = uproject_path.parent
    defaults = read_default_map_packages(project_root)
    for key in ("GameDefaultMap", "EditorStartupMap", "ServerDefaultMap"):
        package = defaults.get(key, "")
        if not package:
            continue
        map_file = map_file_from_package(project_root, package)
        if map_file:
            return package, map_file

    row = audit_project(uproject_path)
    recommended_maps = row.get("recommended_review_maps", [])
    if recommended_maps:
        package = str(recommended_maps[0].get("package", ""))
        path_text = str(recommended_maps[0].get("path", ""))
        return package, resolve_project_path(path_text) if path_text else None
    if row.get("umap_samples"):
        path_text = str(row["umap_samples"][0])
        return "", resolve_project_path(path_text)
    return "", None


def plan_exports(scene_root: Path, truth_root: Path, query: str = "") -> list[dict[str, str]]:
    plans: list[dict[str, str]] = []
    query_lower = query.lower()
    uprojects = find_uprojects(scene_root)
    if query_lower:
        uprojects = [path for path in uprojects if query_lower in path.parent.name.lower()]
    for uproject in uprojects:
        name = uproject.parent.name
        map_id = slug(name)
        output = truth_root / f"{map_id}_collision_truth.json"
        uproject_path = uproject
        script_path = ROOT / "Scripts" / "UE5" / "export_unreal_scene_truth.py"
        map_package, map_sample_path = recommend_project_map(uproject_path)
        plans.append(
            {
                "name": name,
                "uproject_path": to_windows_path(uproject_path),
                "recommended_map_sample": to_windows_path(map_sample_path) if map_sample_path else "",
                "recommended_map_package": map_package,
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
            print(f"  Map package: {plan['recommended_map_package']}")
            print("  Run inside Unreal Editor Python:")
            print(f"    {plan['editor_python_command']}")
            print("  Then run in MoSim shell:")
            print(f"    {plan['validate_command']}")
            print(f"    {plan['audit_command']}")
    return 0 if plans else 1


if __name__ == "__main__":
    raise SystemExit(main())
