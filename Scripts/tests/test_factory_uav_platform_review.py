#!/usr/bin/env python3
"""Regression checks for the Factory-first UE UAV platform review route."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/UE5/review_factory_uav_platform.sh"
STREAMER = ROOT / "Scripts/UE5/stream_unreal_udp.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    text = SCRIPT.read_text(encoding="utf-8")
    require("--coordinate-policy mworks_world_m_z_up" in text, "Factory UAV review must use MWORKS coordinate policy")
    require("OPEN_RVIZ" not in text and "rviz2" not in text.lower(), "Factory UAV platform gate must not open RViz")
    require("--local-map-cells 0" in text, "Factory UAV review should not stream old local-grid overlays")
    require("--lidar-point-limit 0" in text, "Factory UAV review should not stream old UE lidar overlay")
    require("--disable-visual-helpers" in text, "Factory UAV review must hide render-only helper geometry")
    require("EXPECTED_FIRST_X_M" in text and "-55.33" in text, "Factory first frame must align with the accepted UAV task start")
    require("EXPECTED_FIRST_YAW_RAD" in text and "neutral heading" in text, "Factory visual gate must neutralize the first-frame yaw")
    require('REVIEW_CAMERA_X_CM="${REVIEW_CAMERA_X_CM:--5733}"' in text, "Factory review camera must be offset from the UAV center")
    require('REVIEW_CAMERA_Z_CM="${REVIEW_CAMERA_Z_CM:-280}"' in text, "Factory review camera must start above the UAV center")
    require("-MoSimDayReview" in text, "Factory UAV review should launch with daylight review")
    require("STREAM_ONLY" in text, "Factory UAV review must support replaying into an already-open UE window")
    require("STREAM_PATH_REPLAY" in text, "Factory visual gate must require explicit opt-in before replaying the old path")
    require("FOLLOW_UAV_CAMERA" in text, "Factory review must provide a separate follow-camera movement gate")
    require("FOLLOW_UAV_CAMERA=1" in text and 'if [[ -z "${FOLLOW_UAV_CAMERA+x}" ]]' in text, "Factory UAV review should default to the follow/orbit camera view unless explicitly overridden")
    require("MWORKS_STATE_REPLAY_CSV" in text, "Follow-camera movement gate must default to the MWORKS/Sysplorer state CSV, not sparse render_replay.csv")
    require("Using MWORKS/Sysplorer state replay" in text, "Movement gate must disclose when it is using the MWORKS state source")
    require("do not accept pure path-point translation as simulation" in text, "Movement gate must reject path-point translation as simulation evidence")
    require("-MoSimFollowPlaybackCamera" in text, "Follow-camera gate must ask UE camera to follow the playback actor")
    require("FOLLOW_CAMERA_BACK_CM" in text and "80" in text, "Follow-camera gate should default to the accepted 80 cm rear inspection distance")
    require("FOLLOW_CAMERA_RIGHT_CM" in text and "-20" in text, "Follow-camera gate should default to the accepted 20 cm left-rear inspection distance")
    require("STREAM_RESAMPLE_HZ" in text and "60" in text, "Factory movement replay should resample sparse CSV poses to the 60 Hz render contract")
    require("FOLLOW_CAMERA_UP_CM" in text and "40" in text, "Follow-camera gate should default to the accepted 40 cm upper inspection distance")
    require("STREAM_MAX_FRAMES" in text and 'STREAM_MAX_FRAMES:-1' in text, "Factory visual gate should default to a first-frame hold")
    require("arrow keys orbit the UAV camera with fixed radius" in text, "Manual gate must state follow/orbit camera policy")
    require("visible blue UAV body" not in text, "Manual gate must not describe the old bright-blue debug UAV material")
    require("reference-colored Sunray150" in text, "Manual gate must describe the current reference-colored Sunray150 review target")

    result = subprocess.run(
        [
            "bash",
            str(SCRIPT.relative_to(ROOT)),
        ],
        cwd=ROOT,
        env={
            **dict(),
            "PATH": __import__("os").environ.get("PATH", ""),
            "OPEN_UE": "0",
            "REVIEW_DRY_RUN": "1",
        },
        text=True,
        capture_output=True,
        check=False,
    )
    require(result.returncode == 0, result.stdout + "\n" + result.stderr)
    require('"frame_coordinate_policy": "mworks_world_m_z_up"' in result.stdout, result.stdout)
    require('"map_id": "local_factoryenvironmentcollect"' in result.stdout, result.stdout)
    require('"scene_id": "factoryenvironmentcollect_uav_platform_review"' in result.stdout, result.stdout)
    require('"position_m": [\n      -55.33,\n      -24.23,\n      1.9\n    ]' in result.stdout, result.stdout)
    require('"rpy_rad": [\n      0.0,\n      0.0,\n      0.0\n    ]' in result.stdout, result.stdout)
    require('"near_radius_m": 0.0' in result.stdout, result.stdout)
    require('"cells": []' in result.stdout, result.stdout)
    require("Factory UAV platform review stream complete." in result.stdout, result.stdout)
    require("Streamed 3 frames" in result.stdout, result.stdout)

    follow_dryrun = subprocess.run(
        [
            "bash",
            str(SCRIPT.relative_to(ROOT)),
        ],
        cwd=ROOT,
        env={
            **dict(),
            "PATH": __import__("os").environ.get("PATH", ""),
            "FOLLOW_UAV_CAMERA": "1",
            "OPEN_UE": "0",
            "REVIEW_DRY_RUN": "1",
        },
        text=True,
        capture_output=True,
        check=False,
    )
    require(follow_dryrun.returncode == 0, follow_dryrun.stdout + "\n" + follow_dryrun.stderr)
    require("Using MWORKS/Sysplorer state replay" in follow_dryrun.stdout, follow_dryrun.stdout)
    require("sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv" in follow_dryrun.stdout, follow_dryrun.stdout)
    require('"position_m": [\n      -55.58,\n      -24.48,\n      1.9\n    ]' in follow_dryrun.stdout, follow_dryrun.stdout)
    require('"rpy_rad": [\n      -0.0,\n      -0.0,\n      -0.0\n    ]' in follow_dryrun.stdout or '"rpy_rad": [\n      0.0,\n      0.0,\n      0.0\n    ]' in follow_dryrun.stdout, follow_dryrun.stdout)

    stream_only = subprocess.run(
        [
            "bash",
            str(SCRIPT.relative_to(ROOT)),
        ],
        cwd=ROOT,
        env={
            **dict(),
            "PATH": __import__("os").environ.get("PATH", ""),
            "STREAM_ONLY": "1",
            "FOLLOW_UAV_CAMERA": "0",
            "STREAM_MAX_FRAMES": "1",
            "STREAM_FPS": "1000",
        },
        text=True,
        capture_output=True,
        check=False,
    )
    require(stream_only.returncode == 0, stream_only.stdout + "\n" + stream_only.stderr)
    require("Streamed 1 frames to udp://" in stream_only.stdout, stream_only.stdout)
    require('"type": "hello"' not in stream_only.stdout, "STREAM_ONLY must live-stream, not dry-run JSON")

    path_replay = subprocess.run(
        [
            "bash",
            str(SCRIPT.relative_to(ROOT)),
        ],
        cwd=ROOT,
        env={
            **dict(),
            "PATH": __import__("os").environ.get("PATH", ""),
            "STREAM_ONLY": "1",
            "FOLLOW_UAV_CAMERA": "0",
            "STREAM_PATH_REPLAY": "1",
            "STREAM_LOOP_COUNT": "1",
            "STREAM_FPS": "1000",
        },
        text=True,
        capture_output=True,
        check=False,
    )
    require(path_replay.returncode == 0, path_replay.stdout + "\n" + path_replay.stderr)
    require("Streamed 497 frames to udp://" in path_replay.stdout, path_replay.stdout)

    streamer_text = STREAMER.read_text(encoding="utf-8")
    require('default="mworks_world_m_z_up"' in streamer_text, "streamer default should stay MWORKS coordinates")
    bridge_header = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackActor.h").read_text(encoding="utf-8")
    bridge_source = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackActor.cpp").read_text(encoding="utf-8")
    require("SunrayMaxBodyTriangles = 0" in bridge_header, "Sunray body must load full STL for visual gate")
    require("sunray150_mid360_propeller.stl" in bridge_header, "Sunray propellers must use the MWORKS visual mesh that matches the accepted MWORKS animation")
    require("SunrayPropellerVisualScale = 0.125f" in bridge_header, "Sunray propellers must use MWORKS length/width/height=0.00125 m converted to UE cm")
    review_camera_header = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.h").read_text(encoding="utf-8")
    review_camera_source = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.cpp").read_text(encoding="utf-8")
    game_mode_source = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MoSimSceneLibraryGameMode.cpp").read_text(encoding="utf-8")
    require("SetFollowTarget" in review_camera_header, "Review camera must expose a follow target for UAV movement review")
    require("FollowOffsetCm = FVector(-80.0f, -20.0f, 40.0f)" in review_camera_header, "Follow camera default must stay 80 cm behind, 20 cm left, and 40 cm above the UAV")
    require("FollowLocationInterpSpeed = 0.0f" in review_camera_header, "Follow camera should lock to the already-smoothed render pose instead of adding visible chase lag")
    require("FollowOrbitDegPerSec = 70.0f" in review_camera_header, "Follow camera must expose a keyboard orbit speed")
    require("FollowMinElevationDeg" in review_camera_header and "FollowMaxElevationDeg" in review_camera_header, "Follow camera orbit must clamp vertical elevation")
    playback_header = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackComponent.h").read_text(encoding="utf-8")
    playback_source = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackComponent.cpp").read_text(encoding="utf-8")
    require("NominalControlRateHz = 20.0f" in playback_header, "UE playback should treat controller input frames as 20 Hz")
    require("MinimumDisplayRateHz = 60.0f" in playback_header, "UE playback should preserve the 60 fps display contract")
    require("bInterpolateActorTransform = false" in playback_header, "60 Hz render-frame replay should not add a second UE interpolation/chase layer")
    require("FQuat::Slerp" in playback_source and "FMath::Lerp" in playback_source, "UE playback must interpolate pose between controller frames instead of teleporting to sparse samples")
    require("MoSimFollowPlaybackCamera" in review_camera_source, "Review camera must support command-line follow mode")
    require("FollowYawRotation.RotateVector(FollowOffsetCm)" in review_camera_source, "Follow camera offset must rotate with UAV yaw")
    require("ApplyFollowOrbitInput(DeltaSeconds)" in review_camera_source, "Follow camera must accept keyboard orbit input while following the UAV")
    require("const float Radius = FollowOffsetCm.Size()" in review_camera_source, "Follow orbit must preserve the spherical camera-target radius")
    require("AxisFromKeys(PlayerController, EKeys::Right, EKeys::Left)" in review_camera_source, "Follow orbit must preserve the normal UE right-positive axis source")
    require("AzimuthDeg -= OrbitYawAxis * FollowOrbitDegPerSec" in review_camera_source, "Follow orbit must invert the actual left/right azimuth movement per manual review")
    require("AxisFromKeys(PlayerController, EKeys::Up, EKeys::Down)" in review_camera_source, "Follow orbit must map up/down arrows to elevation")
    require("(TargetLocation - DesiredLocation).Rotation()" in review_camera_source, "Follow camera must keep looking at the UAV after orbiting")
    require("ReviewPawn->SetFollowTarget(SpawnedPlaybackActor)" in game_mode_source, "GameMode must bind the review camera to the spawned playback actor")
    require("refusing load path" in bridge_source, "Bridge must refuse destructive triangle-limit downsampling")
    require("ApplySunrayReferenceVisualLayout" in bridge_source, "Bridge must apply the MWORKS visual frame before review")
    require("source=MWORKSVisualFrame" in bridge_source, "Bridge must use the MWORKS visual frame that is known-good in MWORKS animation")
    require("MworksSunrayVisualYawOffsetDegrees = -90.0f" in bridge_source, "Bridge must compensate MWORKS body lengthDirection={0,-1,0}")
    require("SunrayBodyMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 5.25f))" in bridge_source, "Bridge must apply MWORKS body r_shape={0,0,0.0525}")
    require("bUseSunrayDaeMaterialPalette = true" in bridge_header, "Sunray STL must default to DAE-informed material palette instead of a single blue material")
    require("SunrayMid360DomeColor" in bridge_header and "0.02f, 0.42f, 0.72f" in bridge_header, "Sunray visual must include the blue MID-360 dome color cue from local reference images")
    require("SunrayMid360ProtectArcColor" in bridge_header and "0.13f, 0.13f, 0.13f" in bridge_header, "MID-360 protect arcs must stay dark according to Sunray DAE physical component materials")
    require("SunrayMid360DomeMesh" in bridge_header and "SunrayMid360DomeColor" in bridge_source, "MID-360 blue optical dome cue must be isolated from the STL protect-arc section")
    require("SunrayDuctGuardColor" in bridge_header and "0.52f, 0.53f, 0.51f" in bridge_header, "Sunray protective ring/duct guard must use DAE-informed grey, not the old bright-white heuristic")
    require("BodyColor = FLinearColor(0.015f, 0.016f, 0.018f" in bridge_header, "Sunray body should default to black carbon-frame coloring, not the old bright-blue debug material")
    require("ClassifySunrayBodyTriangle" in bridge_source, "Single STL body must be procedurally sectioned for reference coloring until a textured asset is imported")
    require("ColorForSection(SectionIndex)" in bridge_source, "Sunray procedural sections must write matching vertex colors, not only material slots")
    require("dae_material_palette=%s" in bridge_source and "mid360_protect_arc=%d" in bridge_source, "Sunray STL load log must expose DAE-informed color-section evidence")
    require("FVector(6.5f, -6.5f, -2.5f)" in bridge_source, "Bridge must place inverted propellers using MWORKS Dronefixed1 translation")
    require("FVector(6.5f, 6.5f, -2.5f)" in bridge_source, "Bridge must preserve MWORKS fixed2 translation")
    require("FVector(-6.5f, 6.5f, -2.5f)" in bridge_source, "Bridge must preserve MWORKS fixed3 translation")
    require("mworks_fixed2" in bridge_source and "mworks_fixed3" in bridge_source, "Bridge must log MWORKS rotor labels")
    require("SunrayProps[Index]->SetRelativeLocation(RotorPositionsCm[Index])" in bridge_source, "Bridge must preserve MWORKS rotor translations; body STL visual yaw must not rotate physical rotor locations")
    require("Playback->PropellerAnglesDegrees[Index] + MworksSunrayVisualYawOffsetDegrees" not in bridge_source, "Bridge must not mix body STL yaw offset into the MWORKS propeller visual spin")
    require("MoSim Sunray component diagnostic" in bridge_source, "Bridge must log visual component diagnostics before review")
    require("Playback->ApplyFrame(Receiver->GetLatestFrame(), DeltaSeconds)" in bridge_source, "Playback actor must apply the latest UDP frame before visual-gate diagnostics")
    print("[OK] Factory UAV platform review route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
