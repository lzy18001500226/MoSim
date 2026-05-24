#!/usr/bin/env python3
"""Read-only Epic Launcher / Fab local library inventory for MoSim."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any


DEFAULT_MANIFESTS_DIR = Path("/mnt/c/ProgramData/Epic/EpicGamesLauncher/Data/Manifests")
DEFAULT_LAUNCHER_INSTALLED = Path("/mnt/c/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat")
DEFAULT_FAB_LIBRARY_DIR = Path("/mnt/c/ProgramData/Epic/EpicGamesLauncher/VaultCache/FabLibrary")
DEFAULT_VAULT_CACHE_DIR = Path("/mnt/c/ProgramData/Epic/EpicGamesLauncher/VaultCache")
DEFAULT_LAUNCHER_SAVED_DATA_DIR = Path("/mnt/c/Users/HP/AppData/Local/EpicGamesLauncher/Saved/Data")

ACCOUNT_APP_ALLOWLIST = {
    "AutomotiveBeachScene": "Automotive Beach Scene",
    "CitySample": "City Sample",
    "ElectricDreamsSample": "Electric Dreams Env",
    "KiteDemo": "A Boy and His Kite",
    "LandscapeMountains": "Landscape Mountains",
    "ParagonProps": "Paragon: Agora and Monolith",
    "SoulCity": "Soul: City",
}

ACCOUNT_APP_PREFIXES = {
    "CityPark": "City Park Environment Collection",
    "DarkRuin": "Dark Ruins Megascans Sample",
    "Derelict": "Derelict Corridor Megascans Sample",
    "FactoryP": "Factory Environment Collection",
    "MedievalGame": "Medieval Village Megascans Sample",
    "ModularR": "Modular Rural Assets",
    "OldMine": "Old Mine",
    "RainFore": "Rain Forest (PCG Environment)",
}

SENSITIVE_KEYS = {
    "ownershiptoken",
    "token",
    "authtoken",
    "authorization",
    "secret",
    "password",
    "user_uid",
    "entitlement_uid",
    "email",
    "account",
}

ENGINE_ITEM_FIELDS = (
    "DisplayName",
    "AppName",
    "AppVersionString",
    "InstallLocation",
    "LaunchExecutable",
    "CatalogItemId",
    "CatalogNamespace",
    "MainGameAppName",
    "ManifestHash",
    "InstallSize",
    "InstallTags",
    "CompatibleApps",
)


def normalize_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith("C:\\"):
        return Path("/mnt/c/" + text[3:].replace("\\", "/"))
    if text.startswith("D:\\"):
        return Path("/mnt/d/" + text[3:].replace("\\", "/"))
    if text.startswith("G:\\"):
        return Path("/mnt/g/" + text[3:].replace("\\", "/"))
    return Path(text)


def redact_mapping(data: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in data.items():
        lowered = key.lower()
        if any(marker in lowered for marker in SENSITIVE_KEYS):
            safe[key] = "<redacted>"
        else:
            safe[key] = value
    return safe


def safe_item_fields(data: dict[str, Any], source: Path) -> dict[str, Any]:
    item = {key: data.get(key) for key in ENGINE_ITEM_FIELDS if key in data}
    item["source_manifest"] = str(source)
    item["kind"] = classify_install_item(item)
    return redact_mapping(item)


def classify_install_item(item: dict[str, Any]) -> str:
    app_name = str(item.get("AppName", ""))
    display_name = str(item.get("DisplayName", ""))
    if app_name.startswith("UE_") or display_name == "Unreal Engine":
        return "engine"
    if app_name.startswith("FabPlugin"):
        return "plugin_fab"
    if app_name.startswith("QuixelBridge"):
        return "plugin_quixel_bridge"
    if "Twinmotion" in display_name or app_name.startswith("TMtoUnrealContent"):
        return "plugin_twinmotion_content"
    return "launcher_item"


def load_item_manifests(manifests_dir: Path = DEFAULT_MANIFESTS_DIR) -> list[dict[str, Any]]:
    manifests_dir = normalize_path(manifests_dir)
    if not manifests_dir.exists():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(manifests_dir.glob("*.item")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        items.append(safe_item_fields(data, path))
    return items


def load_launcher_installed(path: Path = DEFAULT_LAUNCHER_INSTALLED) -> list[dict[str, Any]]:
    path = normalize_path(path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    installs = []
    for item in data.get("InstallationList", []):
        if isinstance(item, dict):
            safe = redact_mapping(dict(item))
            safe["source_manifest"] = str(path)
            safe["kind"] = classify_install_item({"AppName": safe.get("AppName"), "DisplayName": safe.get("AppName")})
            installs.append(safe)
    return installs


def _connect_readonly_sqlite(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _table_exists(con: sqlite3.Connection, table: str) -> bool:
    row = con.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone()
    return row is not None


def _read_fab_db(db_path: Path, fab_library_dir: Path) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    if not db_path.exists():
        return assets
    con = _connect_readonly_sqlite(db_path)
    try:
        if not _table_exists(con, "catalog"):
            return assets
        query = """
            select
              c.listing_uid,
              c.title,
              c.thumbnail,
              c.namespace,
              dm.format,
              dm.path,
              dm.cache_size,
              dm.downloaded_at,
              ll.listing_type,
              ll.published_at,
              ll.user_seller_name,
              ll.category_name,
              ll.category_path
            from catalog c
            left join download_meta dm on dm.listing_uid = c.listing_uid
            left join local_listing ll on ll.uid = c.listing_uid
            order by c.title
        """
        for row in con.execute(query):
            (
                listing_uid,
                title,
                thumbnail,
                namespace,
                fmt,
                cache_path,
                cache_size,
                downloaded_at,
                listing_type,
                published_at,
                seller,
                category_name,
                category_path,
            ) = row
            cache_dir = normalize_path(cache_path) if cache_path else _guess_fab_cache_dir(fab_library_dir, title)
            assets.append(
                {
                    "listing_uid": listing_uid,
                    "title": title,
                    "namespace": namespace,
                    "thumbnail": thumbnail,
                    "format": fmt,
                    "cache_path": str(cache_dir) if cache_dir else "",
                    "cache_size": cache_size,
                    "downloaded_at": downloaded_at,
                    "listing_type": listing_type,
                    "published_at": published_at,
                    "seller": seller,
                    "category_name": category_name,
                    "category_path": category_path,
                    "has_local_cache": bool(cache_dir and cache_dir.exists()),
                    "manifest_path": _find_asset_manifest(cache_dir),
                    "source_db": str(db_path),
                }
            )
    finally:
        con.close()
    return [redact_mapping(asset) for asset in assets]


def _guess_fab_cache_dir(fab_library_dir: Path, title: str | None) -> Path | None:
    if not title or not fab_library_dir.exists():
        return None
    normalized = "".join(ch if ch.isalnum() else "_" for ch in title).strip("_").lower()
    for child in fab_library_dir.iterdir():
        if child.is_dir() and child.name.lower().startswith(normalized[:16]):
            return child
    return None


def _find_asset_manifest(cache_dir: Path | None) -> str:
    if cache_dir is None:
        return ""
    manifest = cache_dir / "unreal-engine" / "manifest"
    return str(manifest) if manifest.exists() else ""


def _find_uproject(root: Path, max_depth: int = 5) -> str:
    """Find the first .uproject without traversing large generated trees."""
    root = normalize_path(root)
    ignored_dirs = {"Binaries", "DerivedDataCache", "Intermediate", "Saved", ".git"}
    root_parts = len(root.parts)
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.parts) - root_parts
        dirs[:] = [name for name in dirs if name not in ignored_dirs]
        if depth >= max_depth:
            dirs[:] = []
        for filename in sorted(files):
            if filename.endswith(".uproject"):
                return str(current_path / filename)
    return ""


def _read_fab_cache_dirs(fab_library_dir: Path) -> list[dict[str, Any]]:
    if not fab_library_dir.exists():
        return []
    assets = []
    for child in sorted(fab_library_dir.iterdir()):
        if not child.is_dir():
            continue
        manifest = child / "unreal-engine" / "manifest"
        assets.append(
            {
                "title": child.name.rsplit("-", 1)[0].replace("_", " "),
                "cache_path": str(child),
                "has_local_cache": True,
                "manifest_path": str(manifest) if manifest.exists() else "",
                "source_db": "",
            }
        )
    return assets


def load_fab_assets(fab_library_dir: Path = DEFAULT_FAB_LIBRARY_DIR) -> list[dict[str, Any]]:
    fab_library_dir = normalize_path(fab_library_dir)
    db_path = fab_library_dir / "listings_v1.db"
    assets = _read_fab_db(db_path, fab_library_dir)
    seen_paths = {asset.get("cache_path") for asset in assets if asset.get("cache_path")}
    for asset in _read_fab_cache_dirs(fab_library_dir):
        if asset.get("cache_path") not in seen_paths:
            assets.append(asset)
    return sorted(assets, key=lambda item: str(item.get("title", "")).lower())


def load_vault_cache_projects(vault_cache_dir: Path = DEFAULT_VAULT_CACHE_DIR) -> list[dict[str, Any]]:
    """List old-style VaultCache project folders without reading account tokens."""
    vault_cache_dir = normalize_path(vault_cache_dir)
    if not vault_cache_dir.exists():
        return []
    projects: list[dict[str, Any]] = []
    for child in sorted(vault_cache_dir.iterdir()):
        if not child.is_dir() or child.name == "FabLibrary":
            continue
        uproject = _find_uproject(child)
        projects.append(
            {
                "cache_name": child.name,
                "cache_path": str(child),
                "uproject_path": uproject,
                "has_uproject": bool(uproject),
            }
        )
    return projects


PRINTABLE_RE = re.compile(rb"[A-Za-z0-9_.:/@ -]{3,}")
VERSION_SUFFIX_RE = re.compile(r"_(?:4\.\d+|5(?:\.\d+)?|\d+\.\d+)$")


def _printable_strings(path: Path) -> list[str]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    strings: list[str] = []
    for match in PRINTABLE_RE.finditer(data):
        try:
            text = match.group(0).decode("utf-8", errors="ignore").strip()
        except UnicodeDecodeError:
            continue
        if text:
            strings.append(text)
    return strings


def _base_account_app_name(app_name: str) -> str:
    base = VERSION_SUFFIX_RE.sub("", app_name)
    # Examples such as SoulCity419 encode the UE version at the end.
    if base.startswith("SoulCity"):
        return "SoulCity"
    if base.startswith("MedievalGame"):
        return "MedievalGame"
    return base


def _display_name_from_account_app(app_name: str) -> str | None:
    base = _base_account_app_name(app_name)
    for exact, display in ACCOUNT_APP_ALLOWLIST.items():
        if base == exact:
            return display
    for prefix, display in ACCOUNT_APP_PREFIXES.items():
        if base.startswith(prefix):
            return display
    return None


def _version_from_account_app(app_name: str) -> str:
    match = re.search(r"_(4\.\d+|5(?:\.\d+)?)$", app_name)
    if match:
        return match.group(1)
    if app_name.startswith("SoulCity") and app_name[-3:].isdigit():
        return f"{app_name[-3]}.{app_name[-2:]}"
    return ""


def load_account_library_items(
    saved_data_dir: Path = DEFAULT_LAUNCHER_SAVED_DATA_DIR,
) -> list[dict[str, Any]]:
    """Parse account-side Launcher cache for owned asset app names.

    The Epic Launcher cache can also contain OAuth/session material in nearby
    files. This parser reads only `OC_*.dat`, emits allowlisted asset fields,
    and never returns raw cache strings.
    """
    saved_data_dir = normalize_path(saved_data_dir)
    if not saved_data_dir.exists():
        return []

    grouped: dict[str, dict[str, Any]] = {}
    for path in sorted(saved_data_dir.glob("OC_*.dat")):
        for text in _printable_strings(path):
            display = _display_name_from_account_app(text)
            if not display:
                continue
            base = _base_account_app_name(text)
            item = grouped.setdefault(
                base,
                {
                    "display_name": display,
                    "base_app_name": base,
                    "app_names": [],
                    "versions": [],
                    "source_cache": str(path),
                },
            )
            if text not in item["app_names"]:
                item["app_names"].append(text)
            version = _version_from_account_app(text)
            if version and version not in item["versions"]:
                item["versions"].append(version)

    for item in grouped.values():
        item["app_names"] = sorted(item["app_names"])
        item["versions"] = sorted(item["versions"])
    return sorted(grouped.values(), key=lambda row: row["display_name"].lower())


def filter_items(items: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    if not query:
        return items
    needle = query.lower()
    return [item for item in items if needle in json.dumps(item, ensure_ascii=False).lower()]


def build_inventory(
    query: str = "",
    manifests_dir: Path = DEFAULT_MANIFESTS_DIR,
    launcher_installed: Path = DEFAULT_LAUNCHER_INSTALLED,
    fab_library_dir: Path = DEFAULT_FAB_LIBRARY_DIR,
    vault_cache_dir: Path = DEFAULT_VAULT_CACHE_DIR,
    launcher_saved_data_dir: Path = DEFAULT_LAUNCHER_SAVED_DATA_DIR,
) -> dict[str, Any]:
    launcher_items = load_item_manifests(manifests_dir)
    launcher_installs = load_launcher_installed(launcher_installed)
    fab_assets = load_fab_assets(fab_library_dir)
    vault_cache_projects = load_vault_cache_projects(vault_cache_dir)
    account_library_items = load_account_library_items(launcher_saved_data_dir)
    if query:
        launcher_items = filter_items(launcher_items, query)
        launcher_installs = filter_items(launcher_installs, query)
        fab_assets = filter_items(fab_assets, query)
        vault_cache_projects = filter_items(vault_cache_projects, query)
        account_library_items = filter_items(account_library_items, query)
    return {
        "schema": "mosim.epic_library_inventory.v1",
        "roots": {
            "manifests_dir": str(normalize_path(manifests_dir)),
            "launcher_installed": str(normalize_path(launcher_installed)),
            "fab_library_dir": str(normalize_path(fab_library_dir)),
            "vault_cache_dir": str(normalize_path(vault_cache_dir)),
            "launcher_saved_data_dir": str(normalize_path(launcher_saved_data_dir)),
        },
        "summary": {
            "launcher_item_count": len(launcher_items),
            "launcher_install_count": len(launcher_installs),
            "fab_asset_count": len(fab_assets),
            "vault_cache_project_count": len(vault_cache_projects),
            "account_library_item_count": len(account_library_items),
        },
        "launcher_items": launcher_items,
        "launcher_installs": launcher_installs,
        "fab_assets": fab_assets,
        "vault_cache_projects": vault_cache_projects,
        "account_library_items": account_library_items,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Filter inventory by text.")
    parser.add_argument("--manifests-dir", type=Path, default=DEFAULT_MANIFESTS_DIR)
    parser.add_argument("--launcher-installed", type=Path, default=DEFAULT_LAUNCHER_INSTALLED)
    parser.add_argument("--fab-library-dir", type=Path, default=DEFAULT_FAB_LIBRARY_DIR)
    parser.add_argument("--vault-cache-dir", type=Path, default=DEFAULT_VAULT_CACHE_DIR)
    parser.add_argument("--launcher-saved-data-dir", type=Path, default=DEFAULT_LAUNCHER_SAVED_DATA_DIR)
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    args = parser.parse_args(argv)

    inventory = build_inventory(
        query=args.query,
        manifests_dir=args.manifests_dir,
        launcher_installed=args.launcher_installed,
        fab_library_dir=args.fab_library_dir,
        vault_cache_dir=args.vault_cache_dir,
        launcher_saved_data_dir=args.launcher_saved_data_dir,
    )
    indent = None if args.compact else 2
    print(json.dumps(inventory, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
