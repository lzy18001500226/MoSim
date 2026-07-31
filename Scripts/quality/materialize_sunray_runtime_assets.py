#!/usr/bin/env python3
"""Verify or materialize the manifest-listed Sunray runtime assets.

This tool copies only declared missing or mismatched files from the retained
source tree. It never removes files and it does not add large binary assets to
Git; delivery packages must include the materialized assets separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = {
    "sunray_gazebo": "src/simulation/gazebo/sunray/ASSET_MANIFEST.json",
    "sunray_gazebo_plugins": "src/simulation/gazebo/plugins/sunray/ASSET_MANIFEST.json",
}


@dataclass(frozen=True)
class Asset:
    path: PurePosixPath
    size: int
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--component", choices=("all", *MANIFESTS), default="all")
    parser.add_argument("--materialize", action="store_true", help="copy missing or mismatched manifest assets")
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"asset path must be a safe relative path: {value}")
    return path


def load_manifest(path: Path) -> tuple[dict[str, Any], list[Asset]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assets = [
        Asset(relative_path(item["path"]), int(item["bytes"]), str(item["sha256"]).lower())
        for item in payload["assets"]
    ]
    if payload.get("asset_count") != len(assets):
        raise ValueError(f"asset_count mismatch in {path}")
    return payload, assets


def inspect(root: Path, assets: list[Asset]) -> tuple[list[Asset], list[Asset]]:
    missing: list[Asset] = []
    mismatched: list[Asset] = []
    for asset in assets:
        candidate = root.joinpath(*asset.path.parts)
        if not candidate.is_file():
            missing.append(asset)
        elif candidate.stat().st_size != asset.size or sha256(candidate) != asset.sha256:
            mismatched.append(asset)
    return missing, mismatched


def materialize(source_root: Path, target_root: Path, assets: list[Asset]) -> int:
    copied = 0
    missing, mismatched = inspect(target_root, assets)
    for asset in [*missing, *mismatched]:
        source = source_root.joinpath(*asset.path.parts)
        target = target_root.joinpath(*asset.path.parts)
        if not source.is_file() or source.stat().st_size != asset.size or sha256(source) != asset.sha256:
            raise RuntimeError(f"source asset does not match manifest: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.mosim-copy-{os.getpid()}")
        try:
            shutil.copy2(source, temporary)
            if temporary.stat().st_size != asset.size or sha256(temporary) != asset.sha256:
                raise RuntimeError(f"copied asset does not match manifest: {target}")
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()
        copied += 1
    return copied


def component_report(root: Path, component_id: str, materialize_requested: bool) -> dict[str, Any]:
    manifest_path = root / MANIFESTS[component_id]
    payload, assets = load_manifest(manifest_path)
    source_root = root / relative_path(payload["source_relpath"])
    target_root = root / relative_path(payload["canonical_relpath"])
    source_missing, source_mismatched = inspect(source_root, assets)
    if source_missing or source_mismatched:
        raise RuntimeError(f"retained source assets are incomplete for {component_id}")
    copied = materialize(source_root, target_root, assets) if materialize_requested else 0
    target_missing, target_mismatched = inspect(target_root, assets)
    return {
        "component_id": component_id,
        "manifest": MANIFESTS[component_id],
        "source_relpath": payload["source_relpath"],
        "canonical_relpath": payload["canonical_relpath"],
        "asset_count": payload["asset_count"],
        "asset_bytes": payload["asset_bytes"],
        "copied_assets": copied,
        "missing_assets": len(target_missing),
        "mismatched_assets": len(target_mismatched),
        "valid": not target_missing and not target_mismatched,
    }


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    component_ids = tuple(MANIFESTS) if args.component == "all" else (args.component,)
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    for component_id in component_ids:
        try:
            reports.append(component_report(root, component_id, args.materialize))
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            errors.append(f"{component_id}: {exc}")
    result = {
        "schema": "mosim.sunray_runtime_assets.v1",
        "materialize_requested": args.materialize,
        "components": reports,
        "valid": not errors and all(item["valid"] for item in reports),
        "errors": errors,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        report = args.report if args.report.is_absolute() else root / args.report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
