#!/usr/bin/env python3
"""Run the source-level S0/S1 Unreal renderer readiness checks.

This script intentionally does not open Unreal Editor. It validates the source,
scene/package contracts, and UDP packet schema that must be ready before a
viewport review can be meaningful. Use ``--check-listener`` to add the
editor-side UnrealMCP TCP listener probe.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_RAW = (
    ROOT
    / "results/planning/single_obstacle_astar_awff/"
    / "sunray150_planning_open_blocks_linear_mpc_sysblock/raw/"
    / "sunray150_planning_open_blocks_linear_mpc_height_profile_0p2_sensor_20hz.csv"
)
S1_RENDER_MAP = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/map_competition_industrial_hybrid_render_map.json"
SCENE_PROFILES = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json"
REVIEW_CAMERA_HEADER = ROOT / "unreal/MworksUnrealRenderer/Source/MworksUnrealRenderer/MworksReviewCameraPawn.h"
REVIEW_CAMERA_SOURCE = ROOT / "unreal/MworksUnrealRenderer/Source/MworksUnrealRenderer/MworksReviewCameraPawn.cpp"
RENDERER_GAMEMODE_SOURCE = ROOT / "unreal/MworksUnrealRenderer/Source/MworksUnrealRenderer/MworksUnrealRendererGameMode.cpp"
DEFAULT_ENGINE_INI = ROOT / "unreal/MworksUnrealRenderer/Config/DefaultEngine.ini"
OPEN_UNREAL_RENDERER = ROOT / "scripts/unreal/open_unreal_renderer.sh"


def run_step(name: str, command: list[str], *, expect_success: bool = True) -> bool:
    print(f"== {name} ==")
    print("+ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    ok = result.returncode == 0
    if ok != expect_success:
        state = "succeeded unexpectedly" if ok else f"failed with {result.returncode}"
        print(f"[FAIL] {name}: {state}")
        return False
    print(f"[OK] {name}")
    return True


def packet_has_fields(output: str, required_fields: Iterable[str]) -> bool:
    packets: list[dict[str, object]] = []
    current: list[str] = []
    depth = 0
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("{") and depth == 0:
            current = [line]
            depth = line.count("{") - line.count("}")
            if depth == 0:
                packets.append(json.loads("\n".join(current)))
                current = []
            continue
        if current:
            current.append(line)
            depth += line.count("{") - line.count("}")
            if depth == 0:
                packets.append(json.loads("\n".join(current)))
                current = []

    frame_packets = [packet for packet in packets if packet.get("type") == "frame"]
    if not frame_packets:
        print("[FAIL] UDP dry-run produced no frame packet")
        return False

    frame = frame_packets[0]
    missing = [field for field in required_fields if field not in frame]
    if missing:
        print(f"[FAIL] frame packet missing fields: {', '.join(missing)}")
        return False

    local_plan = frame.get("local_plan")
    local_known_map = frame.get("local_known_map")
    if not isinstance(local_plan, dict) or not isinstance(local_known_map, dict):
        print("[FAIL] local_plan/local_known_map must be JSON objects")
        return False
    if "evidence_backed" not in local_plan or "evidence_backed" not in local_known_map:
        print("[FAIL] packet missing evidence_backed guard flags")
        return False
    print("[OK] UDP packet contains S0/S1 contract fields")
    return True


def run_packet_check() -> bool:
    if not SAMPLE_RAW.exists():
        print(f"[FAIL] sample raw CSV missing: {SAMPLE_RAW.relative_to(ROOT)}")
        return False

    command = [
        sys.executable,
        "scripts/unreal/stream_unreal_udp.py",
        str(SAMPLE_RAW.relative_to(ROOT)),
        "--map-id",
        "renderer_framework",
        "--scene-id",
        "renderer_framework_packet_contract",
        "--max-frames",
        "1",
        "--dry-run",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    print("== udp packet dry-run ==")
    print("+ " + " ".join(command))
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout.rstrip())
        print(f"[FAIL] UDP dry-run failed with {result.returncode}")
        return False
    return packet_has_fields(
        result.stdout,
        ["uav", "reference", "mission", "perception", "local_known_map", "local_plan", "status", "overlays"],
    )


def run_s1_render_map_check() -> bool:
    print("== S1 competition industrial hybrid render map ==")
    if not S1_RENDER_MAP.exists():
        print(f"[FAIL] S1 render map missing: {S1_RENDER_MAP.relative_to(ROOT)}")
        return False
    if not SCENE_PROFILES.exists():
        print(f"[FAIL] scene profiles missing: {SCENE_PROFILES.relative_to(ROOT)}")
        return False

    render_map = json.loads(S1_RENDER_MAP.read_text(encoding="utf-8"))
    profiles_doc = json.loads(SCENE_PROFILES.read_text(encoding="utf-8"))
    profiles = {profile.get("profile_id"): profile for profile in profiles_doc.get("profiles", [])}
    s1_profile = profiles.get("competition_industrial_hybrid")
    if not s1_profile:
        print("[FAIL] S1 profile missing: competition_industrial_hybrid")
        return False
    expected = "MworksData/map_competition_industrial_hybrid_render_map.json"
    if s1_profile.get("render_map_json") != expected:
        print(f"[FAIL] S1 profile render_map_json must be {expected}")
        return False

    if render_map.get("schema") != "quadrotor.unreal_render_map.v1":
        print("[FAIL] S1 render map schema mismatch")
        return False
    if render_map.get("render_only") is not True:
        print("[FAIL] S1 render map must be render_only")
        return False
    obstacles = render_map.get("obstacles", {})
    terrain = render_map.get("terrain", {})
    if terrain.get("count", [0, 0])[0] < 10 or terrain.get("count", [0, 0])[1] < 8:
        print("[FAIL] S1 terrain grid is too small for manual review")
        return False
    if obstacles.get("random_column_count", 0) < 8:
        print("[FAIL] S1 render map needs at least 8 pillar/box/target instances")
        return False
    if obstacles.get("wall_box_count", 0) < 8:
        print("[FAIL] S1 render map needs at least 8 wall/gate/pad instances")
        return False
    if not render_map.get("start_m") or not render_map.get("goal_m"):
        print("[FAIL] S1 render map missing start_m/goal_m")
        return False
    visible_instances = []
    for collection_name in ["random_columns", "wall_boxes"]:
        collection = obstacles.get(collection_name, [])
        if not isinstance(collection, list):
            print(f"[FAIL] S1 render map obstacles.{collection_name} must be a list")
            return False
        visible_instances.extend(collection)
    missing_proxy_ids = [
        str(instance.get("id", "<missing-id>"))
        for instance in visible_instances
        if not isinstance(instance, dict)
        or not isinstance(instance.get("source"), dict)
        or not instance["source"].get("collision_proxy_id")
    ]
    if missing_proxy_ids:
        print("[FAIL] S1 render map instances missing source.collision_proxy_id: " + ", ".join(missing_proxy_ids))
        return False
    print("[OK] S1 render map is bound and reviewable")
    return True


def run_review_camera_check() -> bool:
    print("== Unreal manual review camera contract ==")
    for path in [REVIEW_CAMERA_HEADER, REVIEW_CAMERA_SOURCE, RENDERER_GAMEMODE_SOURCE]:
        if not path.exists():
            print(f"[FAIL] missing review camera file: {path.relative_to(ROOT)}")
            return False

    header = REVIEW_CAMERA_HEADER.read_text(encoding="utf-8")
    source = REVIEW_CAMERA_SOURCE.read_text(encoding="utf-8")
    gamemode = RENDERER_GAMEMODE_SOURCE.read_text(encoding="utf-8")

    required_source_tokens = [
        "AutoPossessPlayer = EAutoReceiveInput::Player0",
        "SetupPlayerInputComponent",
        "BindAxis",
        "SetReviewInputMode",
        "EKeys::W",
        "EKeys::A",
        "EKeys::S",
        "EKeys::D",
        "EKeys::Q",
        "EKeys::E",
        "EKeys::RightMouseButton",
        "GetInputMouseDelta",
        "MWORKS review camera input accepted",
    ]
    missing = [token for token in required_source_tokens if token not in source]
    if missing:
        print(f"[FAIL] review camera missing controls: {', '.join(missing)}")
        return False
    if "AMworksReviewCameraPawn" not in header:
        print("[FAIL] review camera class missing from header")
        return False
    input_text = (ROOT / "unreal/MworksUnrealRenderer/Config/DefaultInput.ini").read_text(encoding="utf-8")
    for axis_name in [
        "MworksReviewMoveForward",
        "MworksReviewMoveRight",
        "MworksReviewMoveUp",
        "MworksReviewTurn",
        "MworksReviewLookUp",
    ]:
        if axis_name not in input_text:
            print(f"[FAIL] DefaultInput.ini missing review axis mapping: {axis_name}")
            return False
    if "DefaultPawnClass = AMworksReviewCameraPawn::StaticClass()" not in gamemode:
        print("[FAIL] renderer GameMode does not use the review camera pawn")
        return False
    required_lighting_tokens = [
        "SpawnDefaultReviewLighting",
        "ADirectionalLight",
        "ASkyLight",
        "MWORKS renderer spawned default review lighting",
    ]
    missing_lighting = [token for token in required_lighting_tokens if token not in gamemode]
    if missing_lighting:
        print(f"[FAIL] renderer GameMode missing runtime review lighting: {', '.join(missing_lighting)}")
        return False
    print("[OK] manual review camera has keyboard/mouse controls and is bound to GameMode")
    return True


def run_runtime_map_check() -> bool:
    print("== Unreal runtime default map contract ==")
    if not DEFAULT_ENGINE_INI.exists():
        print(f"[FAIL] missing DefaultEngine.ini: {DEFAULT_ENGINE_INI.relative_to(ROOT)}")
        return False
    text = DEFAULT_ENGINE_INI.read_text(encoding="utf-8")
    forbidden = ["AndroidFileServerRuntimeSettings", "SecurityToken="]
    leaked = [token for token in forbidden if token in text]
    if leaked:
        print(f"[FAIL] DefaultEngine.ini contains local generated config: {', '.join(leaked)}")
        return False
    if "GameDefaultMap=/Engine/Maps/Entry" not in text:
        print("[FAIL] GameDefaultMap must be /Engine/Maps/Entry for runtime-generated renderer review")
        return False
    if "EditorStartupMap=/Engine/Maps/Entry" not in text:
        print("[FAIL] EditorStartupMap must be /Engine/Maps/Entry for runtime-generated renderer review")
        return False
    if "/Engine/Maps/Templates/OpenWorld" in text:
        print("[FAIL] OpenWorld template should not be the default runtime/editor map")
        return False
    print("[OK] runtime default map avoids the OpenWorld landscape template")
    return True


def run_editor_launcher_check() -> bool:
    print("== Unreal editor launcher process contract ==")
    if not OPEN_UNREAL_RENDERER.exists():
        print(f"[FAIL] missing launcher script: {OPEN_UNREAL_RENDERER.relative_to(ROOT)}")
        return False
    text = OPEN_UNREAL_RENDERER.read_text(encoding="utf-8")
    if 'MODE}" == "editor"' not in text:
        print("[FAIL] launcher missing editor mode branch")
        return False
    if "-and \\$_.CommandLine -notlike '* -game*'" not in text:
        print("[FAIL] editor mode must not reuse a standalone -game process")
        return False
    if 'MODE}" == "game"' not in text or "-and \\$_.CommandLine -like '* -game*'" not in text:
        print("[FAIL] launcher missing explicit game process branch")
        return False
    print("[OK] editor/game process reuse is separated")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-listener", action="store_true", help="Also require the Unreal Editor MCP listener")
    parser.add_argument("--build", action="store_true", help="Also run the UE 5.7 renderer build")
    args = parser.parse_args()

    checks = [
        run_step("python syntax: stream/check/probe", [
            sys.executable,
            "-c",
            (
                "from pathlib import Path\n"
                "for rel in ['scripts/unreal/stream_unreal_udp.py','scripts/unreal/check_unreal_bridge.py',"
                "'scripts/unreal/probe_unreal_mcp_listener.py']:\n"
                "    compile(Path(rel).read_text(encoding='utf-8'), rel, 'exec')\n"
                "print('[OK] syntax bundle')\n"
            ),
        ]),
        run_step("unreal bridge source contract", [sys.executable, "scripts/unreal/check_unreal_bridge.py"]),
        run_s1_render_map_check(),
        run_review_camera_check(),
        run_runtime_map_check(),
        run_editor_launcher_check(),
        run_packet_check(),
    ]

    if args.build:
        checks.append(run_step("UE renderer build", ["bash", "scripts/unreal/build_unreal_renderer.sh"]))

    if args.check_listener:
        checks.append(run_step("Unreal Editor MCP listener", [
            sys.executable,
            "scripts/unreal/probe_unreal_mcp_listener.py",
            "--timeout",
            "0.5",
        ]))

    if all(checks):
        print("[OK] S0/S1 Unreal renderer readiness checks passed")
        return 0
    print("[FAIL] S0/S1 Unreal renderer readiness checks failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
