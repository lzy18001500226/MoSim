#!/usr/bin/env python3
"""Regression checks for Epic/Fab local library inventory parsing."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "epic_library_index.py"
    spec = importlib.util.spec_from_file_location("epic_library_index", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load epic_library_index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_ue5_module(name: str):
    path = ROOT / "Scripts" / "UE5" / f"{name}.py"
    script_dir = str(path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
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


def test_epic_library_health_check_query_uses_baseline_for_global_checks(tmp_path: Path) -> None:
    manifests = tmp_path / "Manifests"
    fab = tmp_path / "FabLibrary"
    saved = tmp_path / "SavedData"
    vault = tmp_path / "VaultCache"
    for folder in (manifests, fab, saved, vault):
        folder.mkdir()
    launcher = tmp_path / "LauncherInstalled.dat"
    launcher.write_text(json.dumps({"InstallationList": []}), encoding="utf-8")
    (manifests / "engine.item").write_text(
        json.dumps({"DisplayName": "Unreal Engine", "AppName": "UE_5.5"}),
        encoding="utf-8",
    )
    (saved / "OC_test.dat").write_bytes(b"FactoryPbfa035615186V1\x00")

    script = ROOT / "Scripts" / "UE5" / "check_epic_library_inventory.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--query",
            "Factory",
            "--json",
            "--manifests-dir",
            str(manifests),
            "--launcher-installed",
            str(launcher),
            "--fab-library-dir",
            str(fab),
            "--vault-cache-dir",
            str(vault),
            "--launcher-saved-data-dir",
            str(saved),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    data = json.loads(completed.stdout)
    if data["baseline_summary"]["launcher_item_count"] != 1:
        raise AssertionError(data)
    if data["summary"]["launcher_item_count"] != 0:
        raise AssertionError(data)
    if not data["checks"]["has_launcher_manifest_or_install"]:
        raise AssertionError(data)
    if not data["checks"]["query_has_results"]:
        raise AssertionError(data)


def test_epic_library_view_merges_account_fab_and_vault_entries(monkeypatch) -> None:
    module = load_ue5_module("epic_library_view")

    def fake_inventory():
        return {
            "account_library_items": [
                {
                    "display_name": "Factory Environment Collection",
                    "app_names": ["FactoryPbfa035615186V1"],
                    "versions": ["5.5"],
                }
            ],
            "fab_assets": [
                {
                    "title": "Factory Environment Collection",
                    "cache_path": "C:/Fab/Factory",
                    "has_local_cache": True,
                }
            ],
            "vault_cache_projects": [
                {
                    "cache_name": "Factory Environment Collection",
                    "cache_path": "C:/Vault/Factory",
                    "has_uproject": True,
                    "uproject_path": "C:/Vault/Factory/Factory.uproject",
                }
            ],
        }

    monkeypatch.setattr(module, "build_inventory", fake_inventory)
    rows = module.merge_library_view("Factory")
    if len(rows) != 1:
        raise AssertionError(rows)
    row = rows[0]
    if not row["openable_project"] or not row["installed_or_cached"]:
        raise AssertionError(row)
    if set(row["states"]) != {"account_owned", "fab_cached", "vault_cached_project"}:
        raise AssertionError(row)


def test_scene_source_audit_detects_truth_gap_and_truth_ready(tmp_path: Path) -> None:
    module = load_ue5_module("audit_scene_source")
    project = tmp_path / "FactoryScene"
    content = project / "Content" / "Maps"
    content.mkdir(parents=True)
    uproject = project / "FactoryScene.uproject"
    uproject.write_text(json.dumps({"EngineAssociation": "5.5"}), encoding="utf-8")
    (content / "Main.umap").write_bytes(b"map")
    (content / "Factory.uasset").write_bytes(b"asset")

    first = module.audit_project(uproject)
    if first["verdict"] != "needs_truth_extraction_or_proxy":
        raise AssertionError(first)
    if first["planning_truth_ready"]:
        raise AssertionError(first)

    (project / "Content" / "Maps" / "factory_occupancy_truth.json").write_text("{}", encoding="utf-8")
    second = module.audit_project(uproject)
    if second["verdict"] != "ready_for_truth_backed_planning":
        raise AssertionError(second)
    if not second["planning_truth_ready"]:
        raise AssertionError(second)

    (project / "Content" / "Maps" / "collision_proxy.uasset").write_bytes(b"proxy")
    third = module.audit_project(uproject)
    if not third["truth"]["has_explicit_truth_source"]:
        raise AssertionError(third)
    if not third["truth"]["has_ue_truth_proxy_candidates"]:
        raise AssertionError(third)


def test_scene_source_audit_accepts_exported_scene_truth(tmp_path: Path) -> None:
    module = load_ue5_module("audit_scene_source")
    project = tmp_path / "DerelictCorridorMegascans"
    content = project / "Content" / "Maps"
    truth_root = tmp_path / "scene_truth"
    content.mkdir(parents=True)
    truth_root.mkdir()
    uproject = project / "DerelictCorridorMegascans.uproject"
    uproject.write_text(json.dumps({"EngineAssociation": "5.5"}), encoding="utf-8")
    (content / "Main.umap").write_bytes(b"map")
    (content / "Factory.uasset").write_bytes(b"asset")
    (truth_root / "derelictcorridormegascans_collision_truth.json").write_text("{}", encoding="utf-8")

    row = module.audit_project(uproject, truth_root=truth_root)
    if row["verdict"] != "ready_for_truth_backed_planning":
        raise AssertionError(row)
    if not row["truth"]["explicit_truth_candidates"]:
        raise AssertionError(row)


def test_unreal_scene_truth_payload_validation() -> None:
    module = load_ue5_module("export_unreal_scene_truth")
    payload = module.build_payload(
        scene_id="factory_scene",
        map_id="factory_map",
        project_path="C:/Scenes/Factory/Factory.uproject",
        level_name="Main",
        assets=[
            {
                "asset_id": "asset_box_001",
                "semantic_type": "building",
                "truth_binding": {"collision_proxy_id": "box_001", "render_only": False},
            }
        ],
        collision_proxies=[
            {
                "collision_proxy_id": "box_001",
                "geometry_type": "box",
                "frame": "mworks_world",
                "center_m": [1.0, 2.0, 1.5],
                "size_m": [2.0, 3.0, 3.0],
                "min_m": [0.0, 0.5, 0.0],
                "max_m": [2.0, 3.5, 3.0],
                "source_asset_id": "asset_box_001",
            }
        ],
    )
    errors = module.validate_truth_payload(payload)
    if errors:
        raise AssertionError(errors)

    payload["collision_proxies"][0]["collision_proxy_id"] = ""
    errors = module.validate_truth_payload(payload)
    if not errors:
        raise AssertionError("invalid payload unexpectedly passed")


def test_scene_source_registry_sanitizes_external_paths(monkeypatch, tmp_path: Path) -> None:
    module = load_ue5_module("build_scene_source_registry")
    monkeypatch.setattr(
        module,
        "build_inventory",
        lambda: {
            "summary": {"account_library_item_count": 1},
        },
    )
    monkeypatch.setattr(
        module,
        "merge_library_view",
        lambda: [
            {
                "display_name": "Factory Environment Collection",
                "states": ["account_owned", "fab_cached"],
                "versions": ["5.5"],
                "installed_or_cached": True,
                "openable_project": False,
                "uproject_paths": [],
                "local_cache_paths": ["C:/ProgramData/Epic/FabLibrary/Factory"],
            }
        ],
    )
    monkeypatch.setattr(
        module,
        "audit_scene_root",
        lambda scene_root, max_files, max_dirs, truth_root: [
            {
                "source_type": "local_unreal_project",
                "name": "DerelictCorridorMegascans",
                "project_root": "References/UnrealScenes/DerelictCorridorMegascans",
                "uproject_path": "References/UnrealScenes/DerelictCorridorMegascans/DerelictCorridorMegascans.uproject",
                "engine_association": "5.5",
                "plugins": [],
                "umap_count": 1,
                "umap_samples": ["References/UnrealScenes/DerelictCorridorMegascans/Content/Maps/DerelictCorridor.umap"],
                "uasset_count": 1,
                "uasset_samples": ["References/UnrealScenes/DerelictCorridorMegascans/Content/Maps/Wall.uasset"],
                "uplugin_count": 0,
                "editable_candidate": True,
                "renderable_candidate": True,
                "planning_truth_ready": True,
                "truth": {
                    "explicit_truth_candidates": [
                        "UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json"
                    ],
                    "truth_gap": "",
                },
                "verdict": "ready_for_truth_backed_planning",
            }
        ],
    )
    monkeypatch.setattr(module, "validate_truth_file", lambda path: [])

    registry = module.build_registry(scene_root=Path("References/UnrealScenes"), truth_root=Path("UE5/MworksUnrealRenderer/Content/MworksData/scene_truth"))
    errors = module.validate_registry(registry)
    if errors:
        raise AssertionError(errors)
    serialized = json.dumps(registry, ensure_ascii=False)
    if "C:/ProgramData" in serialized or "/ProgramData/" in serialized:
        raise AssertionError(serialized)
    if registry["fab_route"]["status"] != "inventory_visible_not_scene_accepted":
        raise AssertionError(registry)
    if registry["policy"]["primary_scene_source_id"] != "local_derelictcorridormegascans":
        raise AssertionError(registry)
    [entry] = registry["fab_route"]["candidate_entries"]
    if entry["external_cache_path_count"] != 1 or entry["project_local_cache_paths"]:
        raise AssertionError(entry)


def test_scene_source_registry_validation_rejects_polluted_paths(monkeypatch, tmp_path: Path) -> None:
    module = load_ue5_module("build_scene_source_registry")

    registry = {
        "schema": "mosim.unreal_scene_source_registry.v1",
        "generated_at": "2026-05-25T00:00:00+00:00",
        "policy": {
            "active_strategy": "local_editable_fallback_until_fab_import_truth_verified",
            "acceptance_gates": ["import_edit", "render", "planning_truth"],
            "primary_scene_source_id": "local_derelictcorridormegascans",
        },
        "fab_route": {
            "status": "inventory_visible_not_scene_accepted",
            "library_summary": {},
            "candidate_entries": [
                {
                    "display_name": "Polluted",
                    "states": ["fab_cached"],
                    "project_local_cache_paths": ["C:/Users/HP/AppData/Local/Epic/FabLibrary/private"],
                }
            ],
        },
        "local_editable_fallback": {
            "status": "active",
            "scene_sources": [
                {
                    "scene_source_id": "local_derelictcorridormegascans",
                    "status": "accepted_local_truth_fallback",
                    "truth_artifacts": ["UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/fake.json"],
                }
            ],
        },
    }

    monkeypatch.setattr(module, "validate_truth_file", lambda path: [])
    errors = module.validate_registry(registry)
    if not any("forbidden external/private path string" in error for error in errors):
        raise AssertionError(errors)


def test_unreal_world_name_uses_available_methods() -> None:
    module = load_ue5_module("export_unreal_scene_truth")

    class WithPath:
        def get_path_name(self) -> str:
            return "/Game/Maps/Main.Main"

    class WithName:
        def get_map_name(self) -> str:
            raise AttributeError("missing in this UE version")

        def get_name(self) -> str:
            return "Main"

    if module.unreal_world_name(WithPath()) != "/Game/Maps/Main.Main":
        raise AssertionError("path fallback failed")
    if module.unreal_world_name(WithName()) != "Main":
        raise AssertionError("name fallback failed")


def test_component_or_actor_bounds_falls_back_to_actor() -> None:
    module = load_ue5_module("export_unreal_scene_truth")

    class ComponentWithoutBounds:
        pass

    class ActorWithBounds:
        def get_actor_bounds(self, only_colliding_components: bool):
            if only_colliding_components:
                raise AssertionError("expected broad actor bounds fallback")
            return "origin", "extent"

    origin, extent, rotation = module.component_or_actor_bounds(ComponentWithoutBounds(), ActorWithBounds())
    if (origin, extent, rotation) != ("origin", "extent", None):
        raise AssertionError((origin, extent, rotation))


def test_plan_scene_truth_export_outputs_editor_and_validation_commands(tmp_path: Path) -> None:
    plan_module = load_ue5_module("plan_scene_truth_export")
    project = tmp_path / "DerelictCorridorMegascans"
    content = project / "Content" / "Maps"
    truth_root = tmp_path / "scene_truth"
    content.mkdir(parents=True)
    truth_root.mkdir()
    uproject = project / "DerelictCorridorMegascans.uproject"
    uproject.write_text(json.dumps({"EngineAssociation": "5.5"}), encoding="utf-8")
    (content / "DerelictCorridor.umap").write_bytes(b"map")
    (content / "Wall.uasset").write_bytes(b"asset")

    plans = plan_module.plan_exports(tmp_path, truth_root, "Derelict")

    if len(plans) != 1:
        raise AssertionError(plans)
    editor_command = plans[0]["editor_python_command"]
    if "export_unreal_scene_truth.py" not in editor_command or " export " not in editor_command:
        raise AssertionError(plans)
    if "\\scene_truth\\derelictcorridormegascans_collision_truth.json" not in editor_command:
        raise AssertionError(plans)
    if "export_unreal_scene_truth.py validate" not in plans[0]["validate_command"]:
        raise AssertionError(plans)


def test_run_scene_truth_export_builds_windows_command_and_batch(tmp_path: Path) -> None:
    run_module = load_ue5_module("run_scene_truth_export")
    project = tmp_path / "DerelictCorridorMegascans"
    content = project / "Content" / "Maps"
    truth_root = tmp_path / "scene_truth"
    batch_script = tmp_path / "run_export.py"
    fake_engine = tmp_path / "UE_5.5"
    editor_cmd = fake_engine / "Engine" / "Binaries" / "Win64" / "UnrealEditor-Cmd.exe"
    content.mkdir(parents=True)
    truth_root.mkdir()
    editor_cmd.parent.mkdir(parents=True)
    editor_cmd.write_text("", encoding="utf-8")
    uproject = project / "DerelictCorridorMegascans.uproject"
    uproject.write_text(json.dumps({"EngineAssociation": "5.5"}), encoding="utf-8")
    (content / "DerelictCorridor.umap").write_bytes(b"map")
    (content / "Wall.uasset").write_bytes(b"asset")

    plan = run_module.first_plan(tmp_path, truth_root, "Derelict")
    run_module.write_batch_script(plan, batch_script, "/Game/DerelictCorridor/Maps/DerelictCorridor")
    command = run_module.build_command(
        editor_cmd=editor_cmd,
        uproject_path=run_module.to_wsl_path(plan["uproject_path"]),
        batch_script=batch_script,
        map_path="/Game/DerelictCorridor/Maps/DerelictCorridor",
    )

    batch_text = batch_script.read_text(encoding="utf-8")
    if "unreal.EditorLevelLibrary.load_level" not in batch_text:
        raise AssertionError(batch_text)
    if "C:\\\\Users\\\\HP\\\\Desktop\\\\MoSim\\\\Scripts\\\\UE5\\\\export_unreal_scene_truth.py" not in batch_text:
        raise AssertionError(batch_text)
    if "\\\\scene_truth\\\\derelictcorridormegascans_collision_truth.json" not in batch_text:
        raise AssertionError(batch_text)
    if "-run=pythonscript" not in command:
        raise AssertionError(command)
    if not any(str(part).endswith("UnrealEditor-Cmd.exe") for part in command):
        raise AssertionError(command)


def test_unreal_editor_mcp_probe_helpers(monkeypatch, tmp_path: Path) -> None:
    module = load_ue5_module("probe_unreal_editor_mcp_tools")
    monkeypatch.setattr(module, "wsl_default_gateway", lambda: "172.17.48.1")

    if module.default_host(None) != "172.17.48.1":
        raise AssertionError("WSL default gateway fallback failed")
    if module.default_host("127.0.0.1") != "127.0.0.1":
        raise AssertionError("explicit host override failed")
    generated_name = module.unique_actor_name("Probe Name")
    if not generated_name.startswith("Probe_Name_") or len(generated_name) <= len("Probe_Name_"):
        raise AssertionError(generated_name)
    generated_from_cli = module.unique_actor_name_from_user_value("MoSimMcpProbe_DoNotSave")
    if generated_from_cli == "MoSimMcpProbe_DoNotSave" or not generated_from_cli.startswith(
        "MoSimMcpProbe_DoNotSave_"
    ):
        raise AssertionError(generated_from_cli)

    actors_response = {"status": "success", "result": {"actors": [{"name": "A"}, {"name": "B"}]}}
    if module.actor_count(actors_response) != 2:
        raise AssertionError("actor_count did not unwrap MCP result payload")

    direct_response = {"actors": [{"name": "A"}]}
    if module.actor_count(direct_response) != 1:
        raise AssertionError("actor_count did not handle direct payload")

    entry_response = {
        "status": "success",
        "result": {
            "world": {
                "persistentLevel": "/Engine/Maps/Entry.Entry:PersistentLevel",
            }
        },
    }
    if module.current_level_name(entry_response) != "/Engine/Maps/Entry.Entry:PersistentLevel":
        raise AssertionError("current_level_name did not inspect nested MCP payloads")
    if not module.is_entry_level("/Engine/Maps/Entry.Entry:PersistentLevel"):
        raise AssertionError("Entry map was not detected")
    if module.is_entry_level("/Game/DerelictCorridor/Maps/DerelictCorridor"):
        raise AssertionError("non-Entry map was classified as Entry")

    output = tmp_path / "evidence.json"
    data = {"ok": True, "steps": []}
    output.write_text(json.dumps(data), encoding="utf-8")
    if json.loads(output.read_text(encoding="utf-8")) != data:
        raise AssertionError("probe evidence JSON sanity check failed")
