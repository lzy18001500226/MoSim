#!/usr/bin/env python3
"""Check the lightweight Unreal MWORKS bridge source layout."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "unreal" / "QuadrotorMworksBridge"
RENDERER = ROOT / "unreal" / "MworksUnrealRenderer"
SCENE_REGISTRY = RENDERER / "Content" / "MworksData" / "rflysim_scene_registry.json"
SCENE_PROFILES = RENDERER / "Content" / "MworksData" / "unreal_scene_profiles.json"
MAZE_RENDER_MAP = RENDERER / "Content" / "MworksData" / "map_maze_building_render_map.json"
ASSET_REGISTRY_SCHEMA = RENDERER / "Content" / "MworksData" / "scene_asset_registry.schema.json"
VISION_RING_PLAN = ROOT / "results" / "rflysim" / "rflysim_vision_ring_migration_plan.json"
VISION_RING_CHECKLIST = ROOT / "results" / "rflysim" / "rflysim_vision_ring_manual_review_checklist.md"
MIGRATION_CHECKER = ROOT / "scripts" / "check_unreal_migration_package.py"
S0_S1_READINESS_CHECKER = ROOT / "scripts" / "check_unreal_s0_s1_readiness.py"
VISION_RING_STAGING = ROOT / "unreal" / "migration_staging" / "rflysim_vision_ring"
GATE_RING_STAGING = ROOT / "unreal" / "migration_staging" / "gate_ring_indoor"
GATE_RING_RENDER_MAP = RENDERER / "Content" / "MworksData" / "map_corridor_gate_render_map.json"
SCENE_PROFILE_PLANNER = ROOT / "scripts" / "plan_unreal_scene_profiles.py"
SCENE_PROFILE_PACKAGE_CREATOR = ROOT / "scripts" / "create_unreal_scene_profile_package.py"
SCENE_PROFILE_PLAN = ROOT / "results" / "unreal" / "unreal_scene_profile_implementation_plan.json"

REQUIRED_FILES = [
    "QuadrotorMworksBridge.uplugin",
    "Source/QuadrotorMworksBridge/QuadrotorMworksBridge.Build.cs",
    "Source/QuadrotorMworksBridge/Public/QuadrotorMworksBridge.h",
    "Source/QuadrotorMworksBridge/Public/QuadrotorMworksTypes.h",
    "Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpReceiverComponent.h",
    "Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackComponent.h",
    "Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackActor.h",
    "Source/QuadrotorMworksBridge/Public/QuadrotorMworksMapActor.h",
    "Source/QuadrotorMworksBridge/Private/QuadrotorMworksBridge.cpp",
    "Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp",
    "Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackComponent.cpp",
    "Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackActor.cpp",
    "Source/QuadrotorMworksBridge/Private/QuadrotorMworksMapActor.cpp",
]


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (PLUGIN / path).exists()]
    if missing:
        for path in missing:
            print(f"[FAIL] missing {PLUGIN / path}")
        return 1

    renderer_descriptor = RENDERER / "MworksUnrealRenderer.uproject"
    if not renderer_descriptor.exists():
        print(f"[FAIL] missing {renderer_descriptor}")
        return 1

    descriptor = json.loads((PLUGIN / "QuadrotorMworksBridge.uplugin").read_text(encoding="utf-8"))
    modules = descriptor.get("Modules", [])
    names = {module.get("Name") for module in modules}
    if "QuadrotorMworksBridge" not in names:
        print("[FAIL] uplugin missing QuadrotorMworksBridge module")
        return 1

    build_text = (PLUGIN / "Source/QuadrotorMworksBridge/QuadrotorMworksBridge.Build.cs").read_text(encoding="utf-8")
    required_modules = ["Json", "JsonUtilities", "Networking", "ProceduralMeshComponent", "Sockets"]
    missing_modules = [name for name in required_modules if f'"{name}"' not in build_text]
    if missing_modules:
        print(f"[FAIL] Build.cs missing dependencies: {', '.join(missing_modules)}")
        return 1

    source = (PLUGIN / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp").read_text(
        encoding="utf-8"
    )
    required_tokens = [
        "FUdpSocketBuilder",
        "FJsonSerializer::Deserialize",
        "quadrotor.unreal_state.",
        "AsyncTask(ENamedThreads::GameThread",
        "OnFrameReceived.Broadcast",
        "LocalPlanPointsMeters",
        "mission",
        "start_m",
        "goal_m",
        "current_goal_m",
        "local_known_map",
        "origin_m",
        "grid_m",
        "radius_m",
        "cells",
        "render_only",
        "evidence_backed",
        "status",
        "controller_mode",
        "planner_state",
        "safety_state",
        "evidence_level",
        "overlays",
        "quality_flags",
        "map_id",
    ]
    missing_tokens = [token for token in required_tokens if token not in source]
    if missing_tokens:
        print(f"[FAIL] receiver source missing tokens: {', '.join(missing_tokens)}")
        return 1

    types_source = (PLUGIN / "Source/QuadrotorMworksBridge/Public/QuadrotorMworksTypes.h").read_text(encoding="utf-8")
    for token in [
        "SceneId",
        "MapId",
        "RadarNearRadiusMeters",
        "LocalPlanPointsMeters",
        "FQuadrotorMworksMission",
        "FQuadrotorMworksLocalKnownMap",
        "FQuadrotorMworksStatus",
        "FQuadrotorMworksOverlays",
        "LocalPlanSource",
        "bLocalPlanEvidenceBacked",
    ]:
        if token not in types_source:
            print(f"[FAIL] frame type missing token: {token}")
            return 1

    playback = (PLUGIN / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackComponent.cpp").read_text(
        encoding="utf-8"
    )
    required_playback_tokens = [
        "MworksPositionToUnreal",
        "MworksRotationToUnreal",
        "SetActorLocationAndRotation",
        "PropellerAnglesDegrees",
        "LocalPlanPointsUnreal",
        "TrajectoryTrailUnreal",
        "RadarNearRadiusCentimeters",
        "ResetTrail",
    ]
    missing_playback_tokens = [token for token in required_playback_tokens if token not in playback]
    if missing_playback_tokens:
        print(f"[FAIL] playback source missing tokens: {', '.join(missing_playback_tokens)}")
        return 1

    playback_actor = (PLUGIN / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackActor.cpp").read_text(
        encoding="utf-8"
    )
    for token in ["MworksUdpReceiver", "MworksPlayback", "ApplyPropellerVisuals"]:
        if token not in playback_actor:
            print(f"[FAIL] playback actor missing token: {token}")
            return 1
    for token in [
        "LocalPlanSpline",
        "TrajectoryTrailSpline",
        "ReferenceMarker",
        "RadarDirectionMarker",
        "RadarNearSectorMesh",
        "RadarFarSectorMesh",
        "UpdateVisualHelpers",
        "UpdateSplineFromPoints",
        "UpdateRadarSectorMesh",
        "BuildSectorMesh",
        "CreateMeshSection_LinearColor",
    ]:
        if token not in playback_actor:
            print(f"[FAIL] playback actor visualization helper missing token: {token}")
            return 1
    for token in ["ApplyDefaultMaterials", "BodyColor", "PropellerColor", "BasicShapeMaterial"]:
        if token not in playback_actor:
            print(f"[FAIL] playback actor material setup missing token: {token}")
            return 1

    map_actor = (PLUGIN / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksMapActor.cpp").read_text(
        encoding="utf-8"
    )
    for token in [
        "LoadRenderMapSummary",
        "SceneRegistryJson",
        "SceneProfilesJson",
        "ResolveMapId",
        "ApplyFrameMapSelection",
        "CurrentMapId",
        "CurrentSceneProfileId",
        "map_ids",
        "render_map_json",
        "Selected scene profile has no static render map",
        "direct_editor_open_supported",
        "random_column_count",
        "wall_box_count",
        "UInstancedStaticMeshComponent",
        "AddBoxInstance",
        "TerrainInstances",
        "RandomColumnInstances",
        "WallInstances",
        "ApplyPreviewMaterials",
        "TerrainColor",
        "RandomColumnColor",
        "WallColor",
    ]:
        if token not in map_actor:
            print(f"[FAIL] map actor missing token: {token}")
            return 1
    playback_actor_header = (
        PLUGIN / "Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackActor.h"
    ).read_text(encoding="utf-8")
    for token in ["AQuadrotorMworksMapActor", "MapActor"]:
        if token not in playback_actor_header:
            print(f"[FAIL] playback actor header missing map-selection token: {token}")
            return 1
    for token in ["UpdateMapSelection", "ApplyFrameMapSelection"]:
        if token not in playback_actor:
            print(f"[FAIL] playback actor missing map-selection token: {token}")
            return 1

    if not SCENE_REGISTRY.exists():
        print(f"[FAIL] missing scene registry: {SCENE_REGISTRY}")
        return 1
    registry = json.loads(SCENE_REGISTRY.read_text(encoding="utf-8"))
    if registry.get("schema") != "quadrotor.rflysim_scene_registry.v1":
        print("[FAIL] scene registry schema mismatch")
        return 1
    if registry.get("direct_use_supported") is not False:
        print("[FAIL] scene registry must mark RflySim maps as migration-only")
        return 1
    if registry.get("direct_editor_open_supported") is not False:
        print("[FAIL] scene registry must mark local RflySim editor project as not directly openable")
        return 1
    blockers = registry.get("direct_editor_open_blockers", [])
    if not blockers:
        print("[FAIL] scene registry missing direct-editor blocker evidence")
        return 1
    for token in ["RflySim3D", "Rfly3DSimPlugin"]:
        if token not in "\n".join(blockers):
            print(f"[FAIL] scene registry missing expected blocker token: {token}")
            return 1
    scenes = registry.get("scenes", [])
    if not any(scene.get("priority") == "P0" for scene in scenes):
        print("[FAIL] scene registry has no P0 migration candidate")
        return 1

    if not SCENE_PROFILES.exists():
        print(f"[FAIL] missing project-owned Unreal scene profiles: {SCENE_PROFILES}")
        return 1
    profiles_doc = json.loads(SCENE_PROFILES.read_text(encoding="utf-8"))
    if profiles_doc.get("schema") != "quadrotor.unreal_scene_profiles.v1":
        print("[FAIL] Unreal scene profiles schema mismatch")
        return 1
    required_profiles = {
        "renderer_framework",
        "competition_industrial_hybrid",
        "gate_ring_attitude",
        "park_city_patrol",
        "open_grass_robustness",
        "maze_indoor_occlusion",
        "dense_forest_high_obstacle",
        "multi_uav_formation",
    }
    profiles = {profile.get("profile_id"): profile for profile in profiles_doc.get("profiles", [])}
    missing_profiles = sorted(required_profiles - set(profiles))
    if missing_profiles:
        print(f"[FAIL] Unreal scene profiles missing: {', '.join(missing_profiles)}")
        return 1
    for profile_id, profile in profiles.items():
        if not profile.get("map_ids"):
            print(f"[FAIL] scene profile missing map_ids: {profile_id}")
            return 1
        if profile_id in {"gate_ring_attitude", "maze_indoor_occlusion"} and not profile.get("render_map_json"):
            print(f"[FAIL] scene profile missing render_map_json: {profile_id}")
            return 1
        stage_id = profile.get("stage_id")
        if not stage_id:
            print(f"[FAIL] scene profile missing stage_id: {profile_id}")
            return 1
        truth = profile.get("truth_geometry", {})
        if truth.get("global_map_available_to_planner") is not False:
            print(f"[FAIL] scene profile must not expose global map to planner: {profile_id}")
            return 1
        if not truth.get("required_proxy_classes"):
            print(f"[FAIL] scene profile missing collision proxy classes: {profile_id}")
            return 1
        if not profile.get("acceptance"):
            print(f"[FAIL] scene profile missing acceptance list: {profile_id}")
            return 1
    # Planned-stage inventory gate. These files prove that later S2/S5
    # contracts are still documented, but they do not mean those stages are
    # unlocked or visually verified.
    if not MAZE_RENDER_MAP.exists():
        print(f"[FAIL] missing maze/building render map: {MAZE_RENDER_MAP}")
        return 1
    if not GATE_RING_RENDER_MAP.exists():
        print(f"[FAIL] missing gate/ring render map: {GATE_RING_RENDER_MAP}")
        return 1
    maze_map = json.loads(MAZE_RENDER_MAP.read_text(encoding="utf-8"))
    if maze_map.get("schema") != "quadrotor.unreal_render_map.v1":
        print("[FAIL] maze/building render map schema mismatch")
        return 1
    maze_obstacles = maze_map.get("obstacles", {})
    if maze_obstacles.get("wall_box_count", 0) < 10:
        print("[FAIL] maze/building render map has too few wall boxes")
        return 1
    gate_map = json.loads(GATE_RING_RENDER_MAP.read_text(encoding="utf-8"))
    if gate_map.get("schema") != "quadrotor.unreal_render_map.v1":
        print("[FAIL] gate/ring render map schema mismatch")
        return 1
    gate_obstacles = gate_map.get("obstacles", {})
    if gate_obstacles.get("wall_box_count", 0) < 3:
        print("[FAIL] gate/ring render map must include gate obstacle boxes")
        return 1

    if not VISION_RING_PLAN.exists():
        print(f"[FAIL] missing P0 migration plan: {VISION_RING_PLAN}")
        return 1
    if not VISION_RING_CHECKLIST.exists():
        print(f"[FAIL] missing P0 manual review checklist: {VISION_RING_CHECKLIST}")
        return 1
    plan = json.loads(VISION_RING_PLAN.read_text(encoding="utf-8"))
    if plan.get("schema") != "quadrotor.rflysim_scene_migration_plan.v1":
        print("[FAIL] RflySim migration plan schema mismatch")
        return 1
    if plan.get("scene_id") != "rflysim_vision_ring":
        print("[FAIL] RflySim migration plan must cover rflysim_vision_ring")
        return 1
    if plan.get("direct_use_supported") is not False:
        print("[FAIL] RflySim migration plan must remain migration-only")
        return 1
    if plan.get("direct_editor_open_supported") is not False:
        print("[FAIL] RflySim migration plan must preserve direct editor blocker state")
        return 1
    if not plan.get("direct_editor_open_blockers"):
        print("[FAIL] RflySim migration plan missing direct-editor blockers")
        return 1

    if not SCENE_PROFILE_PLANNER.exists():
        print(f"[FAIL] missing Unreal scene profile planner: {SCENE_PROFILE_PLANNER}")
        return 1
    if not SCENE_PROFILE_PACKAGE_CREATOR.exists():
        print(f"[FAIL] missing Unreal scene profile package creator: {SCENE_PROFILE_PACKAGE_CREATOR}")
        return 1
    if not SCENE_PROFILE_PLAN.exists():
        print(f"[FAIL] missing Unreal scene profile implementation plan: {SCENE_PROFILE_PLAN}")
        return 1
    profile_plan = json.loads(SCENE_PROFILE_PLAN.read_text(encoding="utf-8"))
    if profile_plan.get("schema") != "quadrotor.unreal_scene_profile_implementation_plan.v1":
        print("[FAIL] Unreal scene profile implementation plan schema mismatch")
        return 1
    if profile_plan.get("profile_count", 0) < len(required_profiles):
        print("[FAIL] Unreal scene profile implementation plan is incomplete")
        return 1
    active_scope = profile_plan.get("active_execution_scope", {})
    if active_scope.get("allowed_to_implement_now") != ["S0", "S1"]:
        print("[FAIL] Unreal scene profile plan must keep active implementation scope to S0/S1")
        return 1
    stage_ids = {stage.get("stage_id") for stage in profile_plan.get("stage_roadmap", [])}
    if not {"S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"}.issubset(stage_ids):
        print("[FAIL] Unreal scene profile plan missing full S0-S7 roadmap")
        return 1
    if profile_plan.get("rflysim_direct_use_supported") is not False:
        print("[FAIL] Unreal scene profile plan must keep RflySim as non-direct-use")
        return 1
    if profile_plan.get("rflysim_direct_editor_open_supported") is not False:
        print("[FAIL] Unreal scene profile plan must preserve RflySim editor-open blocker")
        return 1
    for profile in profile_plan.get("profiles", []):
        if not profile.get("reconstruction_units"):
            print(f"[FAIL] scene profile plan missing reconstruction units: {profile.get('profile_id')}")
            return 1
        if profile.get("profile_id") in {
            "competition_industrial_hybrid",
            "gate_ring_attitude",
            "park_city_patrol",
            "open_grass_robustness",
            "maze_indoor_occlusion",
            "dense_forest_high_obstacle",
        }:
            if not profile.get("rflysim_reference_scenes"):
                print(f"[FAIL] scene profile plan missing RflySim reference scenes: {profile.get('profile_id')}")
                return 1

    if not ASSET_REGISTRY_SCHEMA.exists():
        print(f"[FAIL] missing asset registry schema: {ASSET_REGISTRY_SCHEMA}")
        return 1
    if not MIGRATION_CHECKER.exists():
        print(f"[FAIL] missing migration package checker: {MIGRATION_CHECKER}")
        return 1
    if not S0_S1_READINESS_CHECKER.exists():
        print(f"[FAIL] missing S0/S1 readiness checker: {S0_S1_READINESS_CHECKER}")
        return 1
    if not VISION_RING_STAGING.exists():
        print(f"[FAIL] missing VisionRing migration staging package: {VISION_RING_STAGING}")
        return 1
    if not GATE_RING_STAGING.exists():
        print(f"[FAIL] missing project-owned gate/ring staging package: {GATE_RING_STAGING}")
        return 1
    for profile_id in ["renderer_framework", "competition_industrial_hybrid"]:
        package_dir = ROOT / "unreal" / "migration_staging" / profile_id
        registry_path = package_dir / "scene_asset_registry.json"
        readme_path = package_dir / "README.md"
        if not registry_path.exists():
            print(f"[FAIL] missing active scene profile staging registry: {registry_path}")
            return 1
        if not readme_path.exists():
            print(f"[FAIL] missing active scene profile staging readme: {readme_path}")
            return 1
        registry_doc = json.loads(registry_path.read_text(encoding="utf-8"))
        if registry_doc.get("schema") != "quadrotor.scene_asset_registry.v1":
            print(f"[FAIL] active scene profile staging registry schema mismatch: {profile_id}")
            return 1
        if registry_doc.get("global_map_available_to_planner") is not False:
            print(f"[FAIL] active scene profile staging must not expose global planner truth: {profile_id}")
            return 1
        proxies = registry_doc.get("collision_proxies", [])
        proxy_ids = {proxy.get("collision_proxy_id") for proxy in proxies if isinstance(proxy, dict)}
        if not proxy_ids:
            print(f"[FAIL] active scene profile staging must define collision proxies: {profile_id}")
            return 1
        if profile_id == "renderer_framework":
            expected = {
                "proxy_renderer_framework_scene_bounds_box",
                "proxy_renderer_framework_optional_ground_plane",
                "proxy_renderer_framework_debug_collision_proxy",
            }
            missing_expected = sorted(expected - proxy_ids)
            if missing_expected:
                print(f"[FAIL] renderer framework missing proxy ids: {', '.join(missing_expected)}")
                return 1
        if profile_id == "competition_industrial_hybrid":
            expected = {
                "proxy_competition_industrial_hybrid_takeoff_pad_box",
                "proxy_competition_industrial_hybrid_landing_pad_box",
            }
            missing_expected = sorted(expected - proxy_ids)
            if missing_expected:
                print(f"[FAIL] competition industrial profile missing distinct pad proxies: {', '.join(missing_expected)}")
                return 1
    asset_schema = json.loads(ASSET_REGISTRY_SCHEMA.read_text(encoding="utf-8"))
    if asset_schema.get("schema") != "quadrotor.scene_asset_registry.schema.v1":
        print("[FAIL] scene asset registry schema mismatch")
        return 1
    rules = "\n".join(asset_schema.get("rules", []))
    for token in ["collision_proxy_id", "visible obstacle", "RflySim assets"]:
        if token not in rules:
            print(f"[FAIL] scene asset registry schema missing rule token: {token}")
            return 1

    forbidden_paks = sorted((RENDERER / "Content").rglob("*.pak"))
    if forbidden_paks:
        for path in forbidden_paks[:10]:
            print(f"[FAIL] packaged asset should not be committed: {path}")
        return 1

    print(f"[OK] Unreal bridge plugin layout: {PLUGIN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
