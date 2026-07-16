#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    camera_header = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.h").read_text(encoding="utf-8")
    camera_source = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.cpp").read_text(encoding="utf-8")
    game_mode_source = (ROOT / "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MoSimSceneLibraryGameMode.cpp").read_text(encoding="utf-8")
    input_config = (ROOT / "UE5/MoSimSceneLibrary/Config/DefaultInput.ini").read_text(encoding="utf-8")
    launcher = (ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_review.ps1").read_text(encoding="utf-8")
    airborne_gate = (ROOT / "Scripts/sunray/wait_for_swarm_airborne.py").read_text(encoding="utf-8")

    require("SetFollowTargets" in camera_header, "Multi-UAV follow API is missing")
    require("FollowViewIndex = 0" in camera_header, "Formation overview must be the default view")
    require("LocationSum / static_cast<float>(ValidCount)" in camera_source, "Formation camera must use the UAV centroid")
    require("ForwardSum.Rotation().Yaw" in camera_source, "Formation camera must use the mean UAV heading")
    require("MworksReviewCycleTarget" in camera_source, "Formation/UAV view-cycle binding is missing")
    require("ReviewPawn->SetFollowTargets(FollowActors)" in game_mode_source, "GameMode does not provide every playback actor to the camera")
    require('ActionName="MworksReviewCycleTarget"' in input_config and "Key=Q" in input_config, "Q must cycle formation and UAV views")

    require('"-MoSimPlaybackActorCount=3"' in launcher, "UE review must spawn three UAV actors")
    require('"-MoSimPlaybackBaseUdpPort=$UnrealUdpBasePort"' in launcher, "UE review must use a deterministic UDP port base")
    require("@($UnrealUdpBasePort, ($UnrealUdpBasePort + 1), ($UnrealUdpBasePort + 2))" in launcher, "UE launch evidence must record ports 5005/5006/5007 without PowerShell array-flattening")
    for uav_index in range(1, 4):
        require(f"/uav{uav_index}/sunray/gazebo_pose" in launcher, f"uav{uav_index} Gazebo truth topic is missing")
        require(f"--vehicle-id uav{uav_index}" in launcher, f"uav{uav_index} UE identity is missing")
    require("UnrealStateRateHz = 100.0" in launcher, "UE truth mirrors must default to 100 Hz")
    require('"-MoSimFollowCameraLocationInterpSpeed=0"' in launcher, "UE camera must not add a second location interpolation layer")
    require('"-MoSimFollowCameraRotationInterpSpeed=0"' in launcher, "UE camera must not add a second rotation interpolation layer")
    require('"-MoSimFollowCameraBackCm=231.25"' in launcher and '"-MoSimFollowCameraUpCm=95"' in launcher, "Formation overview camera must stay about 2.5 m from the centroid")
    require("px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash" in launcher, "UE bridge shell must load quadrotor controller messages")
    require("swarm_formation_ws_d1_20260701_173306/devel/setup.bash" in launcher, "UE bridge shell must load Swarm-Formation messages")
    require("ip route show default" in launcher and "default\\s+via" in launcher, "UE bridge must resolve the WSL Windows gateway from the default route")
    require("[switch]$NoRviz" in launcher, "UE-only review mode is missing")
    ready_gate = launcher.index("if (-not $ready)")
    unreal_start = launcher.index("$unrealProcess = Start-Process")
    require(ready_gate < unreal_start, "UE must start only after the live MAVROS/truth readiness gate")
    require("three_truth_samples_three_mavros_connected_and_three_uavs_airborne" in launcher, "UE launch evidence must name its airborne live-input startup gate")
    require("AirborneMinZ = 0.8" in launcher and "wait_for_swarm_airborne.py" in launcher, "UE must wait for the ROS airborne gate")
    require("state.connected" in airborne_gate and "state.armed" in airborne_gate, "Airborne gate must require connected and armed MAVROS states")
    require("pose.pose.position.z <= args.min_z" in airborne_gate, "Airborne gate must enforce the minimum altitude")
    require("max_sample_age_s" in airborne_gate, "Airborne gate must reject stale state and pose samples")
    require("awk" not in launcher, "Airborne gate must not depend on nested shell text parsing")
    require('"-ExecCmds=`"t.MaxFPS $UnrealMaxFps`""' in launcher, "UE review must cap render FPS")
    require('$unrealProcess.PriorityClass = "BelowNormal"' in launcher, "UE review must run below the control runtime priority")

    print("Factory L2 three-UAV UE review contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
