#!/usr/bin/env python3
"""Link a local editable Unreal scene source into the MoSim renderer Content tree.

The default path uses a local directory link instead of copying large third-party
assets into the repository.  For DerelictCorridor this preserves the package
name `/Game/DerelictCorridor/...` expected by the exported truth artifact while
keeping `References/UnrealScenes` ignored.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json"
RENDERER_CONTENT = ROOT / "UE5/MoSimSceneLibrary/Content"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def rel_lexical(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def to_windows_path(path: Path) -> str:
    result = subprocess.run(
        ["wslpath", "-w", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def load_registry(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{rel(path)} root must be a JSON object")
    return data


def source_by_id(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    sources = registry.get("local_editable_fallback", {}).get("scene_sources", [])
    for source in sources if isinstance(sources, list) else []:
        if isinstance(source, dict) and source.get("scene_source_id") == source_id:
            return source
    raise ValueError(f"scene source not found: {source_id}")


def content_package_parts(source: dict[str, Any]) -> tuple[list[str], Path]:
    """Return the first map's package parts below Content and its source file."""
    samples = source.get("umap_samples", [])
    if not isinstance(samples, list) or not samples:
        raise ValueError(f"{source.get('scene_source_id')} has no umap_samples")
    for sample in samples:
        path = ROOT / str(sample)
        parts = list(Path(str(sample)).parts)
        if "Content" not in parts:
            continue
        content_index = parts.index("Content")
        below_content = parts[content_index + 1 :]
        if len(below_content) >= 2 and path.exists():
            return below_content, path
    raise ValueError(f"{source.get('scene_source_id')} has no existing .umap below Content")


def link_target(source: dict[str, Any]) -> dict[str, Any]:
    below_content, source_map = content_package_parts(source)
    top_level = below_content[0]
    source_project_root = ROOT / str(source["project_root"])
    source_content_root = source_project_root / "Content" / top_level
    target_content_root = RENDERER_CONTENT / top_level
    target_map = target_content_root.joinpath(*below_content[1:])
    package = "/Game/" + "/".join(Path(*below_content).with_suffix("").parts)
    return {
        "top_level": top_level,
        "source_content_root": source_content_root,
        "target_content_root": target_content_root,
        "source_map": source_map,
        "target_map": target_map,
        "renderer_map_package": package,
    }


def remove_broken_link(path: Path) -> None:
    if path.is_symlink() and not path.exists():
        path.unlink()


def create_link(source_root: Path, target_root: Path, *, dry_run: bool) -> str:
    if target_root.exists():
        return "already_exists"
    remove_broken_link(target_root)
    if dry_run:
        return "dry_run"
    target_root.parent.mkdir(parents=True, exist_ok=True)
    # Unreal runs as a Windows process.  A Linux symlink created from WSL can
    # look valid to Python on drvfs while remaining unreadable to Unreal.
    # Prefer a Windows directory junction whenever the Windows tools are
    # available, then fall back to a normal symlink on non-Windows hosts.
    if shutil.which("cmd.exe"):
        command = [
            "cmd.exe",
            "/c",
            "mklink",
            "/J",
            to_windows_path(target_root),
            to_windows_path(source_root),
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="mbcs" if sys.platform == "win32" else "gbk",
            errors="replace",
            capture_output=True,
        )
        if result.returncode == 0:
            return "junction_created"
    relative_source = os.path.relpath(source_root, target_root.parent)
    try:
        os.symlink(relative_source, target_root, target_is_directory=True)
        return "symlink_created"
    except OSError as exc:
        if sys.platform != "win32":
            raise
        # Some Windows setups require elevated privileges for symlinks.  Use a
        # junction as a local fallback; it is still ignored and not committed.
        command = [
            "cmd.exe",
            "/c",
            "mklink",
            "/J",
            str(target_root),
            str(source_root),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if result.returncode == 0:
            return "junction_created"
        raise RuntimeError(
            "failed to create symlink and junction\n"
            f"symlink_error: {exc}\n"
            f"mklink_stdout: {result.stdout}\nmklink_stderr: {result.stderr}"
        )


def verify_link(target: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not target["source_content_root"].exists():
        errors.append(f"source content root missing: {rel(target['source_content_root'])}")
    if not target["target_content_root"].exists():
        errors.append(f"renderer content root missing: {rel(target['target_content_root'])}")
    if not target["target_map"].exists():
        errors.append(f"renderer map missing: {rel(target['target_map'])}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--scene-source-id", default="local_derelictcorridormegascans")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remove", action="store_true", help="Remove only the renderer content link if it is a link.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_registry(args.registry)
    source = source_by_id(registry, args.scene_source_id)
    target = link_target(source)

    if args.remove:
        if target["target_content_root"].is_symlink():
            if not args.dry_run:
                target["target_content_root"].unlink()
            print(f"removed link: {rel(target['target_content_root'])}")
            return 0
        if target["target_content_root"].exists():
            print(f"refusing to remove non-symlink path: {rel(target['target_content_root'])}", file=sys.stderr)
            return 2
        print(f"no link to remove: {rel(target['target_content_root'])}")
        return 0

    if not target["source_content_root"].exists():
        print(f"source content root missing: {rel(target['source_content_root'])}", file=sys.stderr)
        return 1

    action = create_link(target["source_content_root"], target["target_content_root"], dry_run=args.dry_run)
    errors = verify_link(target) if not args.dry_run else []
    payload = {
        "scene_source_id": args.scene_source_id,
        "action": action,
        "source_content_root": rel(target["source_content_root"]),
        "renderer_content_root": rel_lexical(target["target_content_root"]),
        "renderer_map_asset": rel_lexical(target["target_map"]),
        "renderer_map_package": target["renderer_map_package"],
        "ok": not errors,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
