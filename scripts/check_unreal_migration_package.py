#!/usr/bin/env python3
"""Validate a candidate Unreal migration package before it enters the repo.

This is a gate for assets exported from a temporary UE/RflySim migration
project. It checks file-size limits, forbidden binary/package types, and the
project-owned scene asset registry contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = (
    ROOT
    / "unreal"
    / "MworksUnrealRenderer"
    / "Content"
    / "MworksData"
    / "scene_asset_registry.schema.json"
)

MAX_GITHUB_FILE_BYTES = 100 * 1024 * 1024
REVIEW_WARNING_BYTES = 50 * 1024 * 1024
FORBIDDEN_SUFFIXES = {
    ".7z",
    ".dll",
    ".exe",
    ".iso",
    ".msr",
    ".pak",
    ".pdb",
    ".rar",
    ".tar",
    ".zip",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def assert_inside_project(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            f"Refusing to inspect outside project boundary: {resolved}. "
            "Copy or export a small migration package under this project first."
        ) from exc
    return resolved


def iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def check_files(files: list[Path]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden file type: {path}")
        size = path.stat().st_size
        if size > MAX_GITHUB_FILE_BYTES:
            errors.append(f"file exceeds 100MB GitHub limit: {path} ({size} bytes)")
        elif size > REVIEW_WARNING_BYTES:
            warnings.append(f"file exceeds 50MB review threshold: {path} ({size} bytes)")
    return errors, warnings


def find_registry(package_dir: Path, registry_name: str) -> Path:
    candidates = sorted(package_dir.rglob(registry_name))
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"Expected exactly one {registry_name} under {package_dir}, found {len(candidates)}"
        )
    return candidates[0]


def check_registry(registry_path: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    schema = load_json(schema_path)
    registry = load_json(registry_path)

    if registry.get("schema") != "quadrotor.scene_asset_registry.v1":
        errors.append("scene asset registry schema must be quadrotor.scene_asset_registry.v1")

    for field in schema.get("required_top_level_fields", []):
        if field not in registry:
            errors.append(f"scene asset registry missing top-level field: {field}")

    assets = registry.get("assets", [])
    proxies = registry.get("collision_proxies", [])
    if not isinstance(assets, list) or not assets:
        errors.append("scene asset registry must contain non-empty assets list")
        assets = []
    if not isinstance(proxies, list):
        errors.append("scene asset registry collision_proxies must be a list")
        proxies = []

    proxy_ids = {proxy.get("collision_proxy_id") for proxy in proxies if isinstance(proxy, dict)}
    asset_ids: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict):
            errors.append("asset entry must be an object")
            continue
        asset_id = asset.get("asset_id")
        if not asset_id:
            errors.append("asset missing asset_id")
        elif asset_id in asset_ids:
            errors.append(f"duplicate asset_id: {asset_id}")
        else:
            asset_ids.add(asset_id)

        source = asset.get("source", {})
        license_status = source.get("license_status")
        if license_status in {"do_not_ship", None, ""}:
            errors.append(f"asset {asset_id or '<missing>'} has invalid license_status: {license_status}")

        binding = asset.get("truth_binding", {})
        render_only = bool(binding.get("render_only", False))
        proxy_id = binding.get("collision_proxy_id")
        semantic_type = asset.get("semantic_type")
        obstacle_like = semantic_type in {
            "terrain",
            "tree",
            "building",
            "wall",
            "gate",
            "ring",
            "obstacle",
        }
        if obstacle_like and not render_only:
            if not proxy_id:
                errors.append(f"asset {asset_id or '<missing>'} requires collision_proxy_id")
            elif proxy_id not in proxy_ids:
                errors.append(f"asset {asset_id or '<missing>'} references missing proxy {proxy_id}")

    for proxy in proxies:
        if not isinstance(proxy, dict):
            errors.append("collision proxy entry must be an object")
            continue
        proxy_id = proxy.get("collision_proxy_id")
        if not proxy_id:
            errors.append("collision proxy missing collision_proxy_id")
        if proxy.get("source_asset_id") and proxy["source_asset_id"] not in asset_ids:
            errors.append(f"proxy {proxy_id or '<missing>'} references missing source_asset_id")
        if proxy.get("frame") != "mworks_world":
            errors.append(f"proxy {proxy_id or '<missing>'} frame must be mworks_world")
        if proxy.get("geometry_type") not in {"box", "capsule", "sphere", "convex_hull", "heightfield", "occupancy_grid"}:
            errors.append(f"proxy {proxy_id or '<missing>'} has invalid geometry_type")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--registry-name", default="scene_asset_registry.json")
    args = parser.parse_args()

    package_dir = assert_inside_project(args.package_dir)
    if not package_dir.exists():
        raise FileNotFoundError(package_dir)
    if not package_dir.is_dir():
        raise NotADirectoryError(package_dir)

    files = iter_files(package_dir)
    errors, warnings = check_files(files)
    registry_path = find_registry(package_dir, args.registry_name)
    errors.extend(check_registry(registry_path, args.schema))

    for warning in warnings:
        print(f"[WARN] {warning}")
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print(f"[OK] migration package: {package_dir}")
    print(f"[OK] files checked: {len(files)}")
    print(f"[OK] registry: {registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
