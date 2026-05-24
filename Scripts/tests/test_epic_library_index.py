#!/usr/bin/env python3
"""Regression checks for Epic/Fab local library inventory parsing."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "epic_library_index.py"
    spec = importlib.util.spec_from_file_location("epic_library_index", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load epic_library_index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_fab_db(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute(
            "create table catalog (listing_uid text primary key, title text, description text, thumbnail text, namespace text)"
        )
        con.execute(
            "create table download_meta (id integer primary key, listing_uid text not null, format text not null, "
            "quality text not null, path text not null, platform_included text not null, is_converted integer not null, "
            "downloaded_at integer not null, cache_size integer not null)"
        )
        con.execute(
            "create table local_listing (uid text primary key, user_uid text not null, category_uid text not null, "
            "entitlement_uid text, title text, description text, average_rating real, review_count integer, "
            "is_ai_forbidden integer, is_ai_generated integer, listing_type text, created_at text, updated_at text, "
            "published_at text, published_at_unix integer, last_updated_at text, thumbnail text, media text, "
            "user_seller_name text, user_profile_image_url text, user_cover_image_url text, category_name text, "
            "category_path text, category_slug text)"
        )
        con.execute("insert into catalog values (?, ?, ?, ?, ?)", ("abc", "Factory Environment", "desc", "thumb", "fab"))
        con.execute(
            "insert into download_meta values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (1, "abc", "unreal-engine", "source", str(path.parent / "Factory_Environment-abc"), "Win64", 0, 1, 123),
        )
        con.execute(
            "insert into local_listing values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "abc",
                "user-secret",
                "cat",
                "entitlement-secret",
                "Factory Environment",
                "desc",
                5.0,
                1,
                0,
                0,
                "asset",
                "2026",
                "2026",
                "2026",
                1,
                "2026",
                "thumb",
                "",
                "Seller",
                "",
                "",
                "Environment",
                "3D/Environment",
                "environment",
            ),
        )
        con.commit()
    finally:
        con.close()


def test_epic_library_inventory_reads_manifests_and_fab_db(tmp_path: Path) -> None:
    module = load_module()
    manifests = tmp_path / "Manifests"
    fab = tmp_path / "FabLibrary"
    cache = fab / "Factory_Environment-abc" / "unreal-engine"
    manifests.mkdir()
    cache.mkdir(parents=True)
    (cache / "manifest").write_text("binary-ish", encoding="utf-8")
    (manifests / "engine.item").write_text(
        json.dumps(
            {
                "DisplayName": "Unreal Engine",
                "AppName": "UE_5.5",
                "AppVersionString": "5.5",
                "InstallLocation": "D:\\Program Files\\Epic Games\\UE_5.5",
                "OwnershipToken": "must-not-leak",
            }
        ),
        encoding="utf-8",
    )
    launcher = tmp_path / "LauncherInstalled.dat"
    launcher.write_text(json.dumps({"InstallationList": []}), encoding="utf-8")
    make_fab_db(fab / "listings_v1.db")

    inventory = module.build_inventory(
        manifests_dir=manifests,
        launcher_installed=launcher,
        fab_library_dir=fab,
        vault_cache_dir=tmp_path / "VaultCache",
        launcher_saved_data_dir=tmp_path / "SavedData",
    )

    if inventory["summary"]["launcher_item_count"] != 1:
        raise AssertionError(inventory)
    if inventory["launcher_items"][0]["kind"] != "engine":
        raise AssertionError(inventory)
    serialized = json.dumps(inventory, ensure_ascii=False)
    if "must-not-leak" in serialized or "user-secret" in serialized or "entitlement-secret" in serialized:
        raise AssertionError(serialized)
    if "Factory Environment" not in serialized:
        raise AssertionError(serialized)


def test_epic_library_inventory_query_filter(tmp_path: Path) -> None:
    module = load_module()
    manifests = tmp_path / "Manifests"
    fab = tmp_path / "FabLibrary"
    manifests.mkdir()
    fab.mkdir()
    (manifests / "fab.item").write_text(
        json.dumps({"DisplayName": "Fab UE Plugin", "AppName": "FabPlugin_5.5"}),
        encoding="utf-8",
    )
    (manifests / "engine.item").write_text(
        json.dumps({"DisplayName": "Unreal Engine", "AppName": "UE_5.5"}),
        encoding="utf-8",
    )
    launcher = tmp_path / "LauncherInstalled.dat"
    launcher.write_text(json.dumps({"InstallationList": []}), encoding="utf-8")

    inventory = module.build_inventory(
        query="FabPlugin",
        manifests_dir=manifests,
        launcher_installed=launcher,
        fab_library_dir=fab,
        vault_cache_dir=tmp_path / "VaultCache",
        launcher_saved_data_dir=tmp_path / "SavedData",
    )
    if inventory["summary"]["launcher_item_count"] != 1:
        raise AssertionError(inventory)
    if inventory["launcher_items"][0]["kind"] != "plugin_fab":
        raise AssertionError(inventory)


def test_epic_library_inventory_reads_allowlisted_account_cache(tmp_path: Path) -> None:
    module = load_module()
    manifests = tmp_path / "Manifests"
    fab = tmp_path / "FabLibrary"
    saved = tmp_path / "SavedData"
    vault = tmp_path / "VaultCache"
    for folder in (manifests, fab, saved, vault):
        folder.mkdir()
    launcher = tmp_path / "LauncherInstalled.dat"
    launcher.write_text(json.dumps({"InstallationList": []}), encoding="utf-8")
    (saved / "OC_test.dat").write_bytes(
        b"\x00oauth_token_secret_should_not_leak\x00"
        b"FactoryPbfa035615186V1\x00"
        b"CitySample_5.4\x00"
        b"KiteDemo_4.27\x00"
    )

    inventory = module.build_inventory(
        manifests_dir=manifests,
        launcher_installed=launcher,
        fab_library_dir=fab,
        vault_cache_dir=vault,
        launcher_saved_data_dir=saved,
    )

    names = {item["display_name"] for item in inventory["account_library_items"]}
    if "Factory Environment Collection" not in names:
        raise AssertionError(inventory)
    if "City Sample" not in names:
        raise AssertionError(inventory)
    if "A Boy and His Kite" not in names:
        raise AssertionError(inventory)
    serialized = json.dumps(inventory, ensure_ascii=False)
    if "oauth_token_secret_should_not_leak" in serialized:
        raise AssertionError(serialized)


def test_epic_library_inventory_lists_old_vault_cache_projects(tmp_path: Path) -> None:
    module = load_module()
    manifests = tmp_path / "Manifests"
    fab = tmp_path / "FabLibrary"
    saved = tmp_path / "SavedData"
    vault = tmp_path / "VaultCache"
    project = vault / "DarkRuinac4b642bf8b9V1" / "data" / "DarkRuins"
    for folder in (manifests, fab, saved, project):
        folder.mkdir(parents=True)
    launcher = tmp_path / "LauncherInstalled.dat"
    launcher.write_text(json.dumps({"InstallationList": []}), encoding="utf-8")
    (project / "DarkRuins.uproject").write_text("{}", encoding="utf-8")

    inventory = module.build_inventory(
        manifests_dir=manifests,
        launcher_installed=launcher,
        fab_library_dir=fab,
        vault_cache_dir=vault,
        launcher_saved_data_dir=saved,
    )

    if inventory["summary"]["vault_cache_project_count"] != 1:
        raise AssertionError(inventory)
    item = inventory["vault_cache_projects"][0]
    if not item["has_uproject"] or not item["uproject_path"].endswith("DarkRuins.uproject"):
        raise AssertionError(item)
