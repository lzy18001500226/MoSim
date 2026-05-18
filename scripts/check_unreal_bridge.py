#!/usr/bin/env python3
"""Check the lightweight Unreal MWORKS bridge source layout."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "unreal" / "QuadrotorMworksBridge"

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

    descriptor = json.loads((PLUGIN / "QuadrotorMworksBridge.uplugin").read_text(encoding="utf-8"))
    modules = descriptor.get("Modules", [])
    names = {module.get("Name") for module in modules}
    if "QuadrotorMworksBridge" not in names:
        print("[FAIL] uplugin missing QuadrotorMworksBridge module")
        return 1

    build_text = (PLUGIN / "Source/QuadrotorMworksBridge/QuadrotorMworksBridge.Build.cs").read_text(encoding="utf-8")
    required_modules = ["Json", "JsonUtilities", "Networking", "Sockets"]
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
    ]
    missing_tokens = [token for token in required_tokens if token not in source]
    if missing_tokens:
        print(f"[FAIL] receiver source missing tokens: {', '.join(missing_tokens)}")
        return 1

    playback = (PLUGIN / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackComponent.cpp").read_text(
        encoding="utf-8"
    )
    required_playback_tokens = [
        "MworksPositionToUnreal",
        "MworksRotationToUnreal",
        "SetActorLocationAndRotation",
        "PropellerAnglesDegrees",
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

    map_actor = (PLUGIN / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksMapActor.cpp").read_text(
        encoding="utf-8"
    )
    for token in [
        "LoadRenderMapSummary",
        "random_column_count",
        "wall_box_count",
        "UInstancedStaticMeshComponent",
        "AddBoxInstance",
        "TerrainInstances",
        "RandomColumnInstances",
        "WallInstances",
    ]:
        if token not in map_actor:
            print(f"[FAIL] map actor missing token: {token}")
            return 1

    print(f"[OK] Unreal bridge plugin layout: {PLUGIN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
