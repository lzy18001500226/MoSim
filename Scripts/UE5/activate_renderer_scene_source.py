#!/usr/bin/env python3
"""Activate one local scene source inside the MoSim renderer project.

Unreal sample projects frequently use hard-coded `/Game/...` package paths such
as `/Game/Blueprints` and `/Game/Meshes`.  Multiple source projects cannot keep
those conflicting top-level folders mounted at the same time.  This script
switches the renderer Content links to one selected source project, including
World Partition `__ExternalActors__` / `__ExternalObjects__` companion folders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from link_renderer_scene_source import (
    DEFAULT_REGISTRY,
    RENDERER_CONTENT,
    ROOT,
    create_link,
    link_target,
    load_registry,
    rel,
    rel_lexical,
    source_by_id,
)


SCENE_ROOT = ROOT / "References/UnrealScenes"
COMPANION_ROOTS = ("__ExternalActors__", "__ExternalObjects__")
PROTECTED_CONTENT_NAMES = {
    "Collections",
    "Developers",
    "MworksData",
    *COMPANION_ROOTS,
}


def path_points_into_scene_root(path: Path) -> bool:
    if not path.is_symlink():
        return False
    try:
        target = path.resolve(strict=False)
        target.relative_to(SCENE_ROOT)
        return True
    except Exception:
        return False


def remove_link(path: Path, *, dry_run: bool) -> dict[str, str]:
    payload = {"path": rel_lexical(path), "target": str(path.resolve(strict=False)), "action": "remove_link"}
    if not dry_run:
        path.unlink()
    return payload


def remove_active_scene_links(*, dry_run: bool) -> list[dict[str, str]]:
    removed: list[dict[str, str]] = []
    if not RENDERER_CONTENT.exists():
        return removed

    for child in sorted(RENDERER_CONTENT.iterdir(), key=lambda item: item.name.lower()):
        if child.name in PROTECTED_CONTENT_NAMES:
            continue
        if path_points_into_scene_root(child):
            removed.append(remove_link(child, dry_run=dry_run))

    for companion_name in COMPANION_ROOTS:
        companion_root = RENDERER_CONTENT / companion_name
        if not companion_root.exists():
            continue
        for child in sorted(companion_root.iterdir(), key=lambda item: item.name.lower()):
            if path_points_into_scene_root(child):
                removed.append(remove_link(child, dry_run=dry_run))
    return removed


def content_links_for_source(source: dict[str, Any]) -> list[dict[str, Path | str]]:
    project_root = ROOT / str(source["project_root"])
    source_content = project_root / "Content"
    links: list[dict[str, Path | str]] = []
    if not source_content.exists():
        raise FileNotFoundError(f"source Content root missing: {rel(source_content)}")

    for child in sorted(source_content.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir() or child.name in PROTECTED_CONTENT_NAMES:
            continue
        links.append(
            {
                "kind": "content",
                "name": child.name,
                "source": child,
                "target": RENDERER_CONTENT / child.name,
            }
        )

    for companion_name in COMPANION_ROOTS:
        source_companion_root = source_content / companion_name
        if not source_companion_root.exists():
            continue
        for child in sorted(source_companion_root.iterdir(), key=lambda item: item.name.lower()):
            if not child.is_dir():
                continue
            links.append(
                {
                    "kind": companion_name,
                    "name": child.name,
                    "source": child,
                    "target": RENDERER_CONTENT / companion_name / child.name,
                }
            )
    return links


def create_scene_links(links: list[dict[str, Path | str]], *, dry_run: bool) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for link in links:
        source = link["source"]
        target = link["target"]
        if not isinstance(source, Path) or not isinstance(target, Path):
            continue
        if target.exists() and not path_points_into_scene_root(target):
            raise RuntimeError(f"refusing to replace non-scene renderer path: {rel_lexical(target)}")
        action = create_link(source, target, dry_run=dry_run)
        results.append(
            {
                "kind": str(link["kind"]),
                "name": str(link["name"]),
                "action": action,
                "source": rel(source),
                "target": rel_lexical(target),
            }
        )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--scene-source-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_registry(args.registry)
    source = source_by_id(registry, args.scene_source_id)
    target = link_target(source)
    planned_links = content_links_for_source(source)
    removed = remove_active_scene_links(dry_run=args.dry_run)
    created = create_scene_links(planned_links, dry_run=args.dry_run)

    errors: list[str] = []
    target_map = target["target_map"]
    if isinstance(target_map, Path) and not args.dry_run and not target_map.exists():
        errors.append(f"renderer map missing after activation: {rel_lexical(target_map)}")

    payload = {
        "ok": not errors,
        "scene_source_id": args.scene_source_id,
        "dry_run": args.dry_run,
        "renderer_map_package": target["renderer_map_package"],
        "renderer_map_asset": rel_lexical(target_map) if isinstance(target_map, Path) else "",
        "removed_links": removed,
        "created_links": created,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
