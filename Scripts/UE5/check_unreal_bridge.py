#!/usr/bin/env python3
"""Check the lightweight Unreal MWORKS bridge source layout."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "UE5" / "Bridge"
RENDERER = ROOT / "UE5" / "MoSimSceneLibrary"
SCENE_PROFILES = RENDERER / "Content" / "MworksData" / "unreal_scene_profiles.json"
MAZE_RENDER_MAP = RENDERER / "Content" / "MworksData" / "map_maze_building_render_map.json"
ASSET_REGISTRY_SCHEMA = RENDERER / "Content" / "MworksData" / "scene_asset_registry.schema.json"
SCENE_SOURCE_REGISTRY = RENDERER / "Content" / "MworksData" / "scene_source_registry.json"
S0_S1_READINESS_CHECKER = ROOT / "Scripts" / "UE5" / "check_unreal_s0_s1_readiness.py"
GATE_RING_RENDER_MAP = RENDERER / "Content" / "MworksData" / "map_corridor_gate_render_map.json"
SCENE_PROFILE_PLANNER = ROOT / "Scripts" / "UE5" / "plan_unreal_scene_profiles.py"

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

    renderer_descriptor = RENDERER / "MoSimSceneLibrary.uproject"
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
        "SceneSourceRegistryJson",
        "ResolveMapId",
        "ResolveSceneSourceId",
        "ApplyFrameMapSelection",
        "ClearSceneSourceState",
        "Frame.MapId.StartsWith(TEXT(\"local_\"))",
        "CurrentMapId",
        "CurrentSceneProfileId",
        "CurrentSceneSourceId",
        "CurrentSceneRendererContentRoot",
        "CurrentSceneRendererMapAsset",
        "CurrentSceneRendererMapPackage",
        "CurrentSceneTruthArtifacts",
        "bCurrentScenePlanningTruthReady",
        "bCurrentSceneImportedIntoRenderer",
        "map_ids",
        "render_map_json",
        "local_editable_fallback",
        "scene_sources",
        "scene_source_id",
        "renderer_map_package",
        "Selected scene profile has no static render map",
        "Selected MoSim scene_source_id",
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

    if not ASSET_REGISTRY_SCHEMA.exists():
        print(f"[FAIL] missing asset registry schema: {ASSET_REGISTRY_SCHEMA}")
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

    if not SCENE_SOURCE_REGISTRY.exists():
        print(f"[FAIL] missing scene source registry: {SCENE_SOURCE_REGISTRY}")
        return 1
    scene_source_registry = json.loads(SCENE_SOURCE_REGISTRY.read_text(encoding="utf-8"))
    if scene_source_registry.get("schema") != "mosim.unreal_scene_source_registry.v1":
        print("[FAIL] scene source registry schema mismatch")
        return 1
    policy = scene_source_registry.get("policy", {})
    primary_scene_source_id = policy.get("primary_scene_source_id")
    if not isinstance(primary_scene_source_id, str) or not primary_scene_source_id:
        print("[FAIL] scene source registry primary fallback is empty")
        return 1
    if scene_source_registry.get("fab_route", {}).get("status") != "inventory_visible_not_scene_accepted":
        print("[FAIL] Fab route should not be accepted without import/edit/truth evidence")
        return 1
    fallback = scene_source_registry.get("local_editable_fallback", {})
    if fallback.get("status") != "active":
        print("[FAIL] local editable fallback should be active")
        return 1
    source_by_id = {
        source.get("scene_source_id"): source
        for source in fallback.get("scene_sources", [])
        if isinstance(source, dict)
    }
    primary_source = source_by_id.get(primary_scene_source_id, {})
    if not primary_source:
        print(f"[FAIL] primary scene source missing from registry: {primary_scene_source_id}")
        return 1
    for key in ["editable_candidate", "renderable_candidate", "planning_truth_ready"]:
        if not primary_source.get(key):
            print(f"[FAIL] primary scene source missing true gate: {key}")
            return 1
    if not primary_source.get("truth_artifacts"):
        print("[FAIL] primary scene source missing truth artifacts")
        return 1
    serialized_registry = json.dumps(scene_source_registry, ensure_ascii=False)
    for forbidden in ["C:/", "C:\\", "/mnt/c/", "ProgramData", "AppData"]:
        if forbidden in serialized_registry:
            print(f"[FAIL] scene source registry contains forbidden external path marker: {forbidden}")
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
