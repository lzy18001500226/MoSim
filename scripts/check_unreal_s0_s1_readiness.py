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


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RAW = (
    ROOT
    / "results/planning/single_obstacle_astar_awff/"
    / "sunray150_planning_open_blocks_linear_mpc_sysblock/raw/"
    / "sunray150_planning_open_blocks_linear_mpc_height_profile_0p2_sensor_20hz.csv"
)
S1_RENDER_MAP = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/map_competition_industrial_hybrid_render_map.json"
SCENE_PROFILES = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json"


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
        "scripts/stream_unreal_udp.py",
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
    print("[OK] S1 render map is bound and reviewable")
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
                "for rel in ['scripts/stream_unreal_udp.py','scripts/check_unreal_bridge.py',"
                "'scripts/probe_unreal_mcp_listener.py']:\n"
                "    compile(Path(rel).read_text(encoding='utf-8'), rel, 'exec')\n"
                "print('[OK] syntax bundle')\n"
            ),
        ]),
        run_step("unreal bridge source contract", [sys.executable, "scripts/check_unreal_bridge.py"]),
        run_step("S0 renderer framework package", [
            sys.executable,
            "scripts/check_unreal_migration_package.py",
            "--package-dir",
            "unreal/migration_staging/renderer_framework",
        ]),
        run_step("S1 competition industrial hybrid package", [
            sys.executable,
            "scripts/check_unreal_migration_package.py",
            "--package-dir",
            "unreal/migration_staging/competition_industrial_hybrid",
        ]),
        run_s1_render_map_check(),
        run_packet_check(),
    ]

    if args.build:
        checks.append(run_step("UE renderer build", ["bash", "scripts/build_unreal_renderer.sh"]))

    if args.check_listener:
        checks.append(run_step("Unreal Editor MCP listener", [
            sys.executable,
            "scripts/probe_unreal_mcp_listener.py",
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
