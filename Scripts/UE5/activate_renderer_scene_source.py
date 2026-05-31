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
import contextlib
import json
import os
import shutil
import subprocess
import time
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
    to_windows_path,
)


SCENE_ROOT = ROOT / "References/UnrealScenes"
COMPANION_ROOTS = ("__ExternalActors__", "__ExternalObjects__")
ACTIVE_LINK_MANIFEST = RENDERER_CONTENT / "MworksData" / "active_scene_links.json"
ACTIVE_LINK_LOCK = RENDERER_CONTENT / "MworksData" / ".active_scene_links.lock"
ROOT_CONTENT_FILE_SUFFIXES = {".umap", ".uasset"}
PROTECTED_CONTENT_NAMES = {
    "Collections",
    "Developers",
    "MworksData",
    *COMPANION_ROOTS,
}


def load_active_manifest() -> dict[str, Any]:
    if not ACTIVE_LINK_MANIFEST.exists():
        return {}
    try:
        data = json.loads(ACTIVE_LINK_MANIFEST.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_active_manifest(scene_source_id: str, created: list[dict[str, str]], *, dry_run: bool) -> None:
    if dry_run:
        return
    ACTIVE_LINK_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "mosim.unreal.active_scene_links.v1",
        "scene_source_id": scene_source_id,
        "created": created,
    }
    ACTIVE_LINK_MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


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
        try:
            path.unlink()
        except FileNotFoundError:
            payload["action"] = "already_removed"
    return payload


@contextlib.contextmanager
def active_scene_lock(*, dry_run: bool, timeout_seconds: float = 60.0):
    if dry_run:
        yield
        return
    ACTIVE_LINK_LOCK.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(str(ACTIVE_LINK_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for active scene link lock: {rel_lexical(ACTIVE_LINK_LOCK)}")
            time.sleep(0.2)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            ACTIVE_LINK_LOCK.unlink()
        except FileNotFoundError:
            pass


def remove_manifest_paths(*, dry_run: bool) -> list[dict[str, str]]:
    removed: list[dict[str, str]] = []
    manifest = load_active_manifest()
    entries = manifest.get("created", [])
    if not isinstance(entries, list):
        return removed

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw_path = entry.get("target")
        if not isinstance(raw_path, str) or not raw_path:
            continue
        path = ROOT / raw_path
        try:
            path.relative_to(RENDERER_CONTENT)
        except ValueError:
            continue
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_dir() and not path.is_symlink():
            continue
        payload = {
            "path": rel_lexical(path),
            "target": str(path.resolve(strict=False)),
            "action": "remove_manifest_path",
        }
        if not dry_run:
            try:
                path.unlink()
            except FileNotFoundError:
                payload["action"] = "already_removed"
        removed.append(payload)
    if removed and not dry_run:
        try:
            ACTIVE_LINK_MANIFEST.unlink()
        except FileNotFoundError:
            pass
    return removed


def remove_active_scene_links(*, dry_run: bool) -> list[dict[str, str]]:
    removed: list[dict[str, str]] = remove_manifest_paths(dry_run=dry_run)
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
        if child.is_dir() and child.name not in PROTECTED_CONTENT_NAMES:
            links.append(
                {
                    "kind": "content",
                    "name": child.name,
                    "source": child,
                    "target": RENDERER_CONTENT / child.name,
                }
            )
            continue
        if child.is_file() and child.suffix.lower() in ROOT_CONTENT_FILE_SUFFIXES:
            links.append(
                {
                    "kind": "content_file",
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


def create_file_link(source: Path, target: Path, *, dry_run: bool) -> str:
    if target.exists():
        try:
            if target.samefile(source):
                return "already_exists"
        except OSError:
            pass
        raise RuntimeError(f"refusing to replace existing renderer file: {rel_lexical(target)}")
    if dry_run:
        return "dry_run"
    target.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("cmd.exe"):
        result = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/H", to_windows_path(target), to_windows_path(source)],
            cwd=ROOT,
            text=True,
            encoding="gbk",
            errors="replace",
            capture_output=True,
        )
        if result.returncode == 0:
            return "hardlink_created"
    shutil.copy2(source, target)
    return "copied"


def create_scene_links(links: list[dict[str, Path | str]], *, dry_run: bool) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for link in links:
        source = link["source"]
        target = link["target"]
        if not isinstance(source, Path) or not isinstance(target, Path):
            continue
        if target.exists() and not path_points_into_scene_root(target):
            try:
                if not target.is_file() or not target.samefile(source):
                    raise RuntimeError
            except Exception as exc:
                raise RuntimeError(f"refusing to replace non-scene renderer path: {rel_lexical(target)}") from exc
        if source.is_file():
            action = create_file_link(source, target, dry_run=dry_run)
        else:
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
    with active_scene_lock(dry_run=args.dry_run):
        registry = load_registry(args.registry)
        source = source_by_id(registry, args.scene_source_id)
        target = link_target(source)
        planned_links = content_links_for_source(source)
        removed = remove_active_scene_links(dry_run=args.dry_run)
        created = create_scene_links(planned_links, dry_run=args.dry_run)
        write_active_manifest(args.scene_source_id, created, dry_run=args.dry_run)

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
