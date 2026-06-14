#!/usr/bin/env python3
"""Regression checks for the Factory-first UE UAV platform review route."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/UE5/review_factory_uav_platform.sh"
STREAMER = ROOT / "Scripts/UE5/stream_unreal_udp.py"
ASSET_BUILDER = ROOT / "Scripts/UE5/assets/build_sunray150_with_mid360_blender_asset.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_review_script(env: dict[str, str]) -> subprocess.CompletedProcess[str] | None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT.relative_to(ROOT)),
        ],
        cwd=ROOT,
        env={
            **env,
            "PATH": os.environ.get("PATH", ""),
        },
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    normalized_output = output.replace("\x00", "")
    if result.returncode != 0 and ("Bash/Service/" in normalized_output or "RPC" in normalized_output):
        print("[SKIP] bash/WSL review-script execution unavailable in this Windows-native environment")
        return None
    return result


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
    require("FOLLOW_CAMERA_BACK_CM" in text and "40" in text, "Follow-camera gate should default to the accepted 40 cm rear inspection distance")
    require("FOLLOW_CAMERA_RIGHT_CM" in text and "-10" in text, "Follow-camera gate should default to the accepted 10 cm left offset")
    require("STREAM_RESAMPLE_HZ" in text and "60" in text, "Factory movement replay should resample sparse CSV poses to the 60 Hz render contract")
    require("FOLLOW_CAMERA_UP_CM" in text and "20" in text, "Follow-camera gate should default to the accepted 20 cm upper inspection distance")
    require("STREAM_MAX_FRAMES" in text and 'STREAM_MAX_FRAMES:-1' in text, "Factory visual gate should default to a first-frame hold")
    require("STREAM_PATH_REPLAY=1" not in text, "Follow-camera mode must not silently turn a bounded max-frames probe into a full loop replay")
    require("arrow keys orbit the UAV camera with fixed radius" in text, "Manual gate must state follow/orbit camera policy")
    require("visible blue UAV body" not in text, "Manual gate must not describe the old bright-blue debug UAV material")
    require("reference-colored Sunray150" in text, "Manual gate must describe the current reference-colored Sunray150 review target")

    result = run_review_script({"OPEN_UE": "0", "REVIEW_DRY_RUN": "1"})
    if result is not None:
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

        follow_dryrun = run_review_script({
            "FOLLOW_UAV_CAMERA": "1",
            "OPEN_UE": "0",
            "REVIEW_DRY_RUN": "1",
        })
        require(follow_dryrun is not None, "bash became unavailable after initial review-script run")
        require(follow_dryrun.returncode == 0, follow_dryrun.stdout + "\n" + follow_dryrun.stderr)
        require("Using MWORKS/Sysplorer state replay" in follow_dryrun.stdout, follow_dryrun.stdout)
        require("sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv" in follow_dryrun.stdout, follow_dryrun.stdout)
        require('"position_m": [\n      -55.58,\n      -24.48,\n      1.9\n    ]' in follow_dryrun.stdout, follow_dryrun.stdout)
        require('"rpy_rad": [\n      -0.0,\n      -0.0,\n      -0.0\n    ]' in follow_dryrun.stdout or '"rpy_rad": [\n      0.0,\n      0.0,\n      0.0\n    ]' in follow_dryrun.stdout, follow_dryrun.stdout)

        stream_only = run_review_script({
            "STREAM_ONLY": "1",
            "FOLLOW_UAV_CAMERA": "0",
            "STREAM_MAX_FRAMES": "1",
            "STREAM_FPS": "1000",
        })
        require(stream_only is not None, "bash became unavailable before stream-only review-script run")
        require(stream_only.returncode == 0, stream_only.stdout + "\n" + stream_only.stderr)
        require("Streamed 1 frames to udp://" in stream_only.stdout, stream_only.stdout)
        require('"type": "hello"' not in stream_only.stdout, "STREAM_ONLY must live-stream, not dry-run JSON")

        path_replay = run_review_script({
            "STREAM_ONLY": "1",
            "FOLLOW_UAV_CAMERA": "0",
            "STREAM_PATH_REPLAY": "1",
            "STREAM_LOOP_COUNT": "1",
            "STREAM_FPS": "1000",
        })
        require(path_replay is not None, "bash became unavailable before path replay review-script run")
        require(path_replay.returncode == 0, path_replay.stdout + "\n" + path_replay.stderr)
        require("Streamed 497 frames to udp://" in path_replay.stdout, path_replay.stdout)

    streamer_text = STREAMER.read_text(encoding="utf-8")
    require('default="mworks_world_m_z_up"' in streamer_text, "streamer default should stay MWORKS coordinates")
    asset_builder_text = ASSET_BUILDER.read_text(encoding="utf-8")
    require("DAE_UNIT_METER = 0.0254" in asset_builder_text, "DAE builder must keep the source unit declaration explicit")
    require("SDF_METER_TO_DAE_UNIT" not in asset_builder_text, "DAE builder must not convert meter-scale rotor centers back into DAE units after meter-baking the body")
    require("STL_MM_TO_DAE_UNIT" not in asset_builder_text, "DAE builder must not convert propeller STL into DAE units after meter-baking the body")
    require("STL_MM_TO_METER = 0.001" in asset_builder_text, "DAE builder must convert the tri-blade STL from millimeters to meters")
    require("dae_unit_to_meter" in asset_builder_text and "transform = y_up_to_z_up @ dae_unit_to_meter @ matrix" in asset_builder_text, "DAE body vertices must be baked to meters before Blender/FBX export")
    require("meter_center" in asset_builder_text and "dae_center" not in asset_builder_text, "Asset manifest should report meter-baked rotor centers, not DAE-unit centers")
    require("baked to meters" in asset_builder_text and "scale=0.001" in asset_builder_text, "Asset manifest must document the meter-baked unit rule")
    require("MID360_BASE_RADIUS_M = 0.027" in asset_builder_text, "MID-360 base supplement must be meter-scale, not a 1 m review primitive")
    require("MID360_DOME_RADIUS_M = 0.023" in asset_builder_text, "MID-360 dome supplement must be meter-scale, not a 1 m review primitive")
    require("radius=1.0" not in asset_builder_text and "depth=0.42" not in asset_builder_text, "Supplemental MID-360 primitives must not keep old DAE-unit placeholder dimensions after meter-baking")
    require("center_m" in asset_builder_text and "radius_m" in asset_builder_text, "Supplemental geometry manifest must disclose meter-scale dimensions")
    bridge_header = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackActor.h").read_text(encoding="utf-8")
    bridge_source = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackActor.cpp").read_text(encoding="utf-8")
    dae_fbx = ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.fbx"
    dae_glb = ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.glb"
    require(dae_fbx.exists() and dae_glb.exists(), "Reviewed DAE-derived Sunray FBX/GLB source assets must exist before runtime import")
    imported_uasset = ROOT / "UE5/MoSimSceneLibrary/Content/Sunray150/sunray150_with_mid360_textured.uasset"
    require(
        imported_uasset.exists() or "DAE-derived visual asset missing" in bridge_source,
        "Bridge must either find the imported UE StaticMesh or explicitly report the missing DAE-derived asset instead of using a fallback")
    require("bUseDaeDerivedVehicleVisual = true" in bridge_header, "Sunray runtime visual must default to the reviewed DAE-derived asset")
    require("/Game/Sunray150/sunray150_with_mid360_textured.sunray150_with_mid360_textured" in bridge_header, "Sunray runtime visual must point to the imported DAE-derived UE StaticMesh")
    require("sunray150_with_mid360_textured.fbx" in bridge_header, "Sunray runtime visual must disclose the reviewed FBX/GLB source when the UE asset is missing")
    require("sunray150_mid360_body.stl" not in bridge_header and "sunray150_mid360_propeller.stl" not in bridge_header, "Sunray runtime visual must not depend on MWORKS STL assets")
    review_camera_header = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.h").read_text(encoding="utf-8")
    review_camera_source = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.cpp").read_text(encoding="utf-8")
    game_mode_source = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MoSimSceneLibraryGameMode.cpp").read_text(encoding="utf-8")
    require("SetFollowTarget" in review_camera_header, "Review camera must expose a follow target for UAV movement review")
    require("FollowOffsetCm = FVector(-10.0f, 40.0f, 20.0f)" in review_camera_header, "Follow camera default must stay at the accepted left-rear review offset: FVector(-10, 40, 20)")
    require("FollowLocationInterpSpeed = 0.0f" in review_camera_header, "Follow camera should lock to the already-smoothed render pose instead of adding visible chase lag")
    require("FollowOrbitDegPerSec = 70.0f" in review_camera_header, "Follow camera must expose a keyboard orbit speed")
    require("FollowMinElevationDeg" in review_camera_header and "FollowMaxElevationDeg" in review_camera_header, "Follow camera orbit must clamp vertical elevation")
    playback_header = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackComponent.h").read_text(encoding="utf-8")
    playback_source = (ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackComponent.cpp").read_text(encoding="utf-8")
    require("NominalControlRateHz = 20.0f" in playback_header, "UE playback should treat controller input frames as 20 Hz")
    require("MinimumDisplayRateHz = 60.0f" in playback_header, "UE playback should preserve the 60 fps display contract")
    require("bInterpolateActorTransform = false" in playback_header, "60 Hz render-frame replay should not add a second UE interpolation/chase layer")
    require("PropellerVisualRotorSpeedMultiplier" not in playback_header and "PropellerVisualRotorSpeedMultiplier" not in playback_source, "UE bridge must not keep retired separate propeller visual animation state for the whole-aircraft StaticMesh gate")
    require("PropellerAnglesDegrees" not in playback_header and "PropellerAnglesDegrees" not in playback_source, "UE bridge must not compute unused legacy propeller angles for the whole-aircraft StaticMesh gate")
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
    require("LoadSunrayDaeDerivedVisualAsset" in bridge_source, "Bridge must load only the reviewed DAE-derived Sunray UE asset")
    require("MWORKS STL and MWORKS animation fallback are disabled" in bridge_source, "Bridge must fail loudly instead of falling back to MWORKS STL or animation")
    require("LoadStlIntoMesh" not in bridge_source, "Bridge must not runtime-load STL vehicle meshes for the Sunray visual gate")
    require("MWORKSVisualFrame" not in bridge_source, "Bridge must not apply the retired MWORKS animation visual frame as vehicle source")
    require("SunrayMid360DomeMesh" not in bridge_header and "SunrayMid360DomeMesh" not in bridge_source, "Bridge must not keep standalone MID-360 cue meshes after switching to DAE-derived whole-vehicle visual")
    require("SunrayBodyMesh" not in bridge_header and "SunrayBodyMesh" not in bridge_source, "Bridge must not keep retired Sunray procedural body meshes")
    require("SunrayPropellerMesh" not in bridge_header and "SunrayPropellerMesh" not in bridge_source, "Bridge must not keep retired Sunray procedural propeller meshes")
    require("PropellerMesh1" not in bridge_header and "PropellerMesh1" not in bridge_source, "Bridge must not keep separate primitive/legacy propeller components")
    require("bAllowPrimitiveUavFallback" not in bridge_header and "SetPrimitiveUavFallbackVisible" not in bridge_source, "Bridge must not keep primitive UAV fallback as an accepted visual route")
    require("ApplyMaterialColor(BodyMesh" not in bridge_source, "Bridge must preserve imported DAE-derived vehicle materials instead of applying BasicShapeMaterial to the vehicle")
    require("ClassifySunrayBodyTriangle" not in bridge_source, "Bridge must not procedurally color old STL vehicle meshes")
    require("FVector(6.5f, -6.5f, -2.5f)" not in bridge_source, "Bridge must not place visual propellers from retired MWORKS STL coordinates")
    require("mworks_fixed2" not in bridge_source and "mworks_fixed3" not in bridge_source, "Bridge must not log retired MWORKS visual rotor labels as vehicle source")
    require("Playback->PropellerAnglesDegrees[Index] + MworksSunrayVisualYawOffsetDegrees" not in bridge_source, "Bridge must not mix body STL yaw offset into the MWORKS propeller visual spin")
    require("MoSim Sunray component diagnostic" in bridge_source, "Bridge must log visual component diagnostics before review")
    require("Playback->ApplyFrame(Receiver->GetLatestFrame(), DeltaSeconds)" in bridge_source, "Playback actor must apply the latest UDP frame before visual-gate diagnostics")
    material_binding_script = (ROOT / "Scripts/UE5/fix_sunray150_runtime_material_bindings.py").read_text(encoding="utf-8")
    require("MP_NORMAL until a true tangent-space normal map is generated" in material_binding_script, "Runtime material binding must document why Blender bump maps are not wired as UE normals")
    require('connect_prop(material, normal_tex' not in material_binding_script, "Runtime material binding must not wire grayscale Blender bump maps directly to UE MP_NORMAL")
    print("[OK] Factory UAV platform review route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
