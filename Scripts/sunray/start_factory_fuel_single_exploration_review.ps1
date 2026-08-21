param(
    [string]$RunId = ("factory_l2_fuel_single_exploration_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$FuelRandomSeed = 1,
    [double]$ExplorationExecuteS = 600.0,
    [double]$EgoTakeoverTimeoutS = 90.0,
    [int]$MissionTotalTimeoutS = 0,
    [double]$MinimumExpectedRealTimeFactor = 0.20,
    [int]$ReviewHoldS = 300,
    [double]$TargetZ = 1.2,
    [double]$TakeoffHeight = -1.0,
    [double]$Px4ctrlRelativeTakeoffHeight = [double]::NaN,
    [double]$TakeoffTimeoutS = 120.0,
    [bool]$PublishHoverDuringTakeoff = $true,
    [double]$PublishHoverDuringTakeoffDelayS = 0.5,
    [double]$StartX = [double]::NaN,
    [double]$StartY = [double]::NaN,
    [double]$StartYaw = 0.0,
    [double]$FuelWindowXYM = [double]::NaN,
    [double]$FuelWindowYM = [double]::NaN,
    [double]$FuelBoxMinXOverride = [double]::NaN,
    [double]$FuelBoxMaxXOverride = [double]::NaN,
    [double]$FuelBoxMinYOverride = [double]::NaN,
    [double]$FuelBoxMaxYOverride = [double]::NaN,
    [double]$FuelWindowZM = 3.0,
    [double]$FuelBoxMinZM = 0.90,
    [double]$FuelBoxMaxZM = 1.60,
    [double]$FuelFrameOffsetZM = [double]::NaN,
    [double]$FuelLocalFlightZM = [double]::NaN,
    [double]$FuelVirtualCeilHeightM = 1.60,
    [double]$FuelManagerLocalSegmentLength = 6.0,
    [double]$FuelGridResolutionM = 0.2,
    [double]$FuelMaxRayLengthM = 12.0,
    [switch]$FuelCloudFreeSpaceRays,
    [int]$FuelCloudFreeSpaceRayCount = 72,
    [double]$FuelCloudFreeSpaceRayLengthMarginM = 0.5,
    [switch]$FuelDiagnosePointcloudRaycast,
    [double]$FuelDiagnosePointcloudRaycastThrottleS = 5.0,
    [switch]$FuelAstarDiagnoseRejection,
    [double]$FuelAstarDiagnoseRejectionThrottleS = 1.0,
    [double]$FuelPerceptionMaxDistM = 12.0,
    [double]$FuelPerceptionVisDistM = 8.0,
    [double]$FuelPerceptionTopAngleRad = 0.56125,
    [double]$FuelPerceptionLeftAngleRad = 0.69222,
    [double]$FuelPerceptionRightAngleRad = 0.68901,
    [switch]$FuelPerceptionOmniHorizontal = $true,
    [int]$FuelFrontierClusterMin = 60,
    [double]$FuelFrontierClusterSizeXY = 4.0,
    [int]$FuelFrontierMinVisibNum = 5,
    [double]$FuelFrontierMinViewFinishFraction = 0.2,
    [double]$FuelFrontierMinCandidateClearance = 0.12,
    [double]$FuelFrontierCandidateDphiRad = 0.2617993833333333,
    [int]$FuelFrontierCandidateRnum = 3,
    [double]$FuelFrontierCandidateRmin = 1.5,
    [double]$FuelFrontierCandidateRmax = 2.5,
    [switch]$FuelAllowNearUnknownCandidate,
    [switch]$FuelAllowUnknownRayVisibility,
    [switch]$FuelFrontierDiagnoseClusterViewpoints,
    [int]$FuelFrontierDiagnoseClusterLogLimit = 20,
    [switch]$FuelNoLocalRefine,
    [double]$FuelExplorationRefinedRadius = 5.0,
    [int]$FuelExplorationTopViewNum = 15,
    [switch]$FuelNearFrontierEscape = $true,
    [double]$FuelNearFrontierEscapeDistanceM = 0.75,
    [double]$FuelNearFrontierEscapeMaxSpeedMps = 0.25,
    [double]$FuelNearFrontierEscapeAlternativeDistanceM = 2.0,
    [switch]$FuelGlobalExpansionBias,
    [int]$FuelGlobalExpansionBiasRankWindow = 12,
    [double]$FuelGlobalExpansionBiasDistWeight = 0.35,
    [double]$FuelGlobalExpansionBiasLateralWeight = 0.65,
    [int]$FuelGlobalExpansionBiasAxis = -1,
    [double]$FuelGlobalExpansionBiasMinGain = 2.0,
    [switch]$FuelGlobalExpansionBiasOverrideRefine,
    [switch]$FuelCoverageExpansion,
    [int]$FuelCoverageExpansionAxis = 1,
    [int]$FuelCoverageExpansionRankWindow = 20,
    [double]$FuelCoverageExpansionMinGain = 1.0,
    [double]$FuelCoverageExpansionDistWeight = 0.05,
    [double]$FuelCoverageExpansionGridResolutionM = 2.0,
    [double]$FuelCoverageExpansionSensorRadiusM = 8.0,
    [double]$FuelCoverageExpansionProjectHorizonM = 5.0,
    [double]$FuelCoverageExpansionGridWeight = 1.0,
    [double]$FuelCoverageExpansionSpanWeight = 0.2,
    [double]$FuelCoverageExpansionUncoveredTargetWeight = 0.0,
    [switch]$FuelCoverageExpansionScoreCommittedGoal,
    [switch]$FuelCoverageExpansionDirectUncoveredFallback,
    [switch]$FuelCoverageExpansionGlobalSelector,
    [switch]$FuelCoverageExpansionLogCandidates,
    [double]$FuelPOcc = 0.80,
    [double]$FuelObstaclesInflationM = 0.35,
    [string]$ControllerCoreProfile = "original",
    [ValidateRange(0.05, 0.95)]
    [double]$Px4ctrlHoverPercentage = 0.456,
    [double]$FuelPlannerMaxVelMps = 2.0,
    [double]$FuelPlannerMaxAccMps2 = 1.5,
    [double]$FuelCmdSmoothMaxSpeedMps = 2.0,
    [double]$FuelCmdSmoothMaxStepM = 0.0,
    [double]$FuelCmdMaxVelocityMps = 2.0,
    [double]$FuelCmdMaxAccelerationMps2 = 1.5,
    [double]$FuelCmdMaxLateralAccelerationMps2 = 1.5,
    [double]$FuelCmdMaxJerkMps3 = 4.0,
    [bool]$FuelCmdSmoothEnable = $false,
    [bool]$FuelCmdRecomputeVelocityFromPosition = $false,
    [double]$FuelMaxXYTargetDistanceFromOdomM = 0.5,
    [double]$CmdMinZM = [double]::NaN,
    [double]$CmdMaxZM = [double]::NaN,
    [double]$CmdFixedZM = [double]::NaN,
    [bool]$PlannerCmdAdapterInitialEnabled = $false,
    [double]$PointCloudMaxAbsOdomXYM = 700.0,
    [double]$PointCloudTransformMinWorldZM = -0.2,
    [double]$PointCloudReviewMinWorldZM = 0.2,
    [string]$OccupancyReviewSourceTopic = "/mosim/fuel/occupancy_all_global",
    [double]$ContinuousOccupancyVoxelSizeM = 0.20,
    [int]$ContinuousOccupancyClosingIterations = 1,
    [int]$ContinuousOccupancyMinComponentVoxels = 8,
    [ValidateSet(1, 2, 3)]
    [int]$ContinuousOccupancyConnectivity = 3,
    [switch]$EnableCoverageSupervisor,
    [double]$CoverageBoundaryMinX = [double]::NaN,
    [double]$CoverageBoundaryMaxX = [double]::NaN,
    [double]$CoverageBoundaryMinY = [double]::NaN,
    [double]$CoverageBoundaryMaxY = [double]::NaN,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [double]$MinSensorCoverageRatio = 0.80,
    [double]$CoverageSupervisorMaxRuntimeS = 0.0,
    [double]$CoverageSupervisorInitialDelayS = 35.0,
    [double]$CoverageSupervisorTriggerIntervalS = 45.0,
    [double]$CoverageSupervisorStaleBsplineS = 20.0,
    [double]$CoverageSupervisorMinTriggerMoveM = 0.5,
    [string]$CoverageSupervisorTimeBasis = "wall",
    [string]$ExplorationTimeBasis = "ros_sim_time",
    [bool]$CoverageSupervisorRequireTargetZ = $true,
    [double]$CoverageSupervisorTriggerZToleranceM = 0.3,
    [double]$CoverageSupervisorNoGrowthTimeoutS = 0.0,
    [int]$CoverageSupervisorMinGrowthCells = 1,
    [double]$BodyAxisLengthM = 1.00,
    [double]$BodyAxisShaftM = 0.060,
    [double]$BodyAxisHeadDiameterM = 0.16,
    [double]$BodyAxisHeadLengthM = 0.24,
    [string]$FuelWorkspaceWsl = "/opt/mosim_work/sunray_ws/fuel_ws_release_20260713",
    [string]$FuelExplorationAsanOptions = "",
    [switch]$FuelDisableRosout,
    [ValidateSet("mavros", "pointcloud_odom", "fastlio")]
    [string]$FuelSensorPoseSource = "fastlio",
    [ValidateSet("fastlio", "truth", "truth_delta")]
    [string]$FuelFastlioAlignmentZSource = "truth",
    [ValidateRange(1, 32)]
    [int]$Mid360PluginDownsample = 4,
    [ValidateRange(0.05, 2.0)]
    [double]$FastlioFilterSizeSurfM = 0.5,
    [ValidateRange(0.05, 2.0)]
    [double]$FastlioFilterSizeMapM = 0.5,
    [switch]$ProfileRuntimeProcesses,
    [ValidateRange(0.25, 10.0)]
    [double]$ProfileRuntimeSamplePeriodS = 1.0,
    [switch]$SkipPreflight,
    [switch]$UnlimitedAccumulation,
    [switch]$RecordRosbag,
    [switch]$RecordRawSensorTopics,
    [switch]$NoRviz,
    [int]$UnrealUdpPort = 5005,
    [string]$UnrealPoseTopic = "/uav1/sunray/gazebo_pose",
    [double]$UnrealStateRateHz = 100.0,
    [ValidateRange(1, 240)]
    [int]$UnrealMaxFps = 30,
    [ValidateRange(1.0, 60.0)]
    [double]$UnrealPlaybackNominalRateHz = 5.0,
    [ValidateRange(1.0, 240.0)]
    [double]$UnrealPlaybackMinimumDisplayRateHz = 30.0,
    [ValidateRange(0.05, 2.0)]
    [double]$UnrealPlaybackMaxInterpolationDurationS = 0.5,
    [switch]$NoUnreal,
    [switch]$ReuseUnrealWindow,
    [switch]$DisableReviewAccumulation,
    [switch]$NoKeepAlive,
    [switch]$Foreground
)

$ErrorActionPreference = "Stop"
$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$ProjectRootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$EnvelopePathWin = Join-Path $ProjectRootWin "Config\gazebo\scene_profiles\factory_l2_exploration_envelope.json"
$ResultDirWin = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $ProjectRootWsl + "/Results/sunray_ros1/" + $RunId
$FactoryWorldWsl = $ProjectRootWsl + "/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
$FactoryModelPathWsl = $ProjectRootWsl + "/Config/gazebo/models"
$RecordRosbagValue = $RecordRosbag.IsPresent.ToString().ToLowerInvariant()
$RosbagTopics = @(
    "/clock",
    "/tf",
    "/tf_static",
    "/gazebo/model_states",
    "/uav1/mavros/state",
    "/uav1/mavros/local_position/odom",
    "/uav1/sunray/gazebo_pose",
    "/mosim/goal4/livox_world_accumulated",
    "/mosim/goal4/occupancy_accumulated",
    "/mosim/goal4/occupancy_object_review",
    "/mosim/goal4/truth_path",
    "/mosim/goal4/position_cmd_path",
    "/mosim/goal4/body_axes",
    "/fuel/position_cmd_raw",
    "/position_cmd",
    "/planning/bspline",
    "/mosim/fuel/planning_vis/trajectory_world"
)
if ($RecordRawSensorTopics) {
    $RosbagTopics += @(
        "/uav1/livox/lidar",
        "/uav1/livox_world"
    )
}
$RosbagTopicArgs = ($RosbagTopics | ForEach-Object { "'$_'" }) -join " "
$MinimumExpectedRealTimeFactor = [Math]::Max(0.05, [Math]::Min(1.0, $MinimumExpectedRealTimeFactor))
$TotalTimeoutS = if ($MissionTotalTimeoutS -gt 0) {
    $MissionTotalTimeoutS
} else {
    [int]([Math]::Ceiling(($ExplorationExecuteS / $MinimumExpectedRealTimeFactor) + 180))
}
$PointCloudCap = if ($UnlimitedAccumulation) { 0 } else { 2000000 }
$OccupancyCap = if ($UnlimitedAccumulation) { 0 } else { 1000000 }
$OpenRvizValue = if ($NoRviz) { "false" } else { "true" }
$KeepAliveValue = if ($NoKeepAlive) { "false" } else { "true" }
$ReviewAccumulationValue = if ($DisableReviewAccumulation) { "false" } else { "true" }
$ProfileRuntimeProcessesValue = $ProfileRuntimeProcesses.IsPresent.ToString().ToLowerInvariant()
if ($FuelRandomSeed -lt -1) {
    throw "FuelRandomSeed must be -1 (random_device) or a non-negative integer: $FuelRandomSeed"
}
$envelope = Get-Content -LiteralPath $EnvelopePathWin -Raw | ConvertFrom-Json
$boundary = $envelope.exploration_boundary
$BoundaryMinX = [double]$boundary.min_x_m
$BoundaryMaxX = [double]$boundary.max_x_m
$BoundaryMinY = [double]$boundary.min_y_m
$BoundaryMaxY = [double]$boundary.max_y_m
if ([double]::IsNaN($StartX) -or [double]::IsNaN($StartY)) {
    if ([double]::IsNaN($StartX)) {
        $StartX = [double]$boundary.center_x_m
    }
    if ([double]::IsNaN($StartY)) {
        $StartY = [double]$boundary.center_y_m
    }
}

$FuelWindowXEffectiveInput = if ([double]::IsNaN($FuelWindowXYM)) { [double]$boundary.size_x_m } else { $FuelWindowXYM }
$FuelWindowYEffectiveInput = if ([double]::IsNaN($FuelWindowYM)) { [double]$boundary.size_y_m } else { $FuelWindowYM }
$FuelHalfXY = $FuelWindowXEffectiveInput * 0.5
$FuelHalfY = $FuelWindowYEffectiveInput * 0.5
$FuelBoxMinX = if ([double]::IsNaN($FuelBoxMinXOverride)) { $StartX - $FuelHalfXY } else { $FuelBoxMinXOverride }
$FuelBoxMaxX = if ([double]::IsNaN($FuelBoxMaxXOverride)) { $StartX + $FuelHalfXY } else { $FuelBoxMaxXOverride }
$FuelBoxMinY = if ([double]::IsNaN($FuelBoxMinYOverride)) { $StartY - $FuelHalfY } else { $FuelBoxMinYOverride }
$FuelBoxMaxY = if ([double]::IsNaN($FuelBoxMaxYOverride)) { $StartY + $FuelHalfY } else { $FuelBoxMaxYOverride }
$FuelFrameOffsetZEffective = if (-not [double]::IsNaN($FuelFrameOffsetZM)) {
    $FuelFrameOffsetZM
} elseif (-not [double]::IsNaN($FuelLocalFlightZM)) {
    $TargetZ - $FuelLocalFlightZM
} else {
    0.0
}
$FuelBoxMinZWorld = $FuelBoxMinZM + $FuelFrameOffsetZEffective
$FuelBoxMaxZWorld = $FuelBoxMaxZM + $FuelFrameOffsetZEffective
$CmdMinZEffective = if ([double]::IsNaN($CmdMinZM)) { $FuelBoxMinZWorld } else { $CmdMinZM }
$CmdMaxZEffective = if ([double]::IsNaN($CmdMaxZM)) { $FuelBoxMaxZWorld } else { $CmdMaxZM }
$CmdFixedZEffective = if ([double]::IsNaN($CmdFixedZM)) { "" } else { [string]$CmdFixedZM }
if ($FuelBoxMinZWorld -ge $FuelBoxMaxZWorld) {
    throw "FUEL world Z bounds are invalid: min=$FuelBoxMinZWorld max=$FuelBoxMaxZWorld"
}
if ($CmdMinZEffective -ge $CmdMaxZEffective) {
    throw "Position-command Z bounds are invalid: min=$CmdMinZEffective max=$CmdMaxZEffective"
}
if ($CmdMaxZEffective -lt $FuelBoxMinZWorld -or $CmdMinZEffective -gt $FuelBoxMaxZWorld) {
    throw "FUEL world Z bounds [$FuelBoxMinZWorld, $FuelBoxMaxZWorld] do not overlap position-command Z bounds [$CmdMinZEffective, $CmdMaxZEffective]"
}
if (-not [double]::IsNaN($CmdFixedZM) -and ($CmdFixedZM -lt $CmdMinZEffective -or $CmdFixedZM -gt $CmdMaxZEffective)) {
    throw "Fixed command Z $CmdFixedZM is outside position-command Z bounds [$CmdMinZEffective, $CmdMaxZEffective]"
}
$FuelWindowXEffective = [Math]::Max(0.1, $FuelBoxMaxX - $FuelBoxMinX)
$FuelWindowYEffective = [Math]::Max(0.1, $FuelBoxMaxY - $FuelBoxMinY)
$CoverageMinXEffective = if ([double]::IsNaN($CoverageBoundaryMinX)) { $BoundaryMinX } else { $CoverageBoundaryMinX }
$CoverageMaxXEffective = if ([double]::IsNaN($CoverageBoundaryMaxX)) { $BoundaryMaxX } else { $CoverageBoundaryMaxX }
$CoverageMinYEffective = if ([double]::IsNaN($CoverageBoundaryMinY)) { $BoundaryMinY } else { $CoverageBoundaryMinY }
$CoverageMaxYEffective = if ([double]::IsNaN($CoverageBoundaryMaxY)) { $BoundaryMaxY } else { $CoverageBoundaryMaxY }
$CoverageSupervisorEnabledValue = if ($EnableCoverageSupervisor) { "true" } else { "false" }
$EffectiveTakeoffHeight = if ($TakeoffHeight -gt 0.0) { $TakeoffHeight } else { $TargetZ }
$SunrayInitialZ = 0.2
$EffectivePx4ctrlRelativeTakeoffHeight = if (-not [double]::IsNaN($Px4ctrlRelativeTakeoffHeight)) {
    $Px4ctrlRelativeTakeoffHeight
} else {
    $EffectiveTakeoffHeight - $SunrayInitialZ
}
if ($EffectivePx4ctrlRelativeTakeoffHeight -le 0.0) {
    throw "PX4Ctrl relative takeoff height must be positive: target=$EffectiveTakeoffHeight initial_z=$SunrayInitialZ relative=$EffectivePx4ctrlRelativeTakeoffHeight"
}

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null
$UnrealReceiverMetricsPath = Join-Path $ResultDirWin "observability\gazebo_ue_receiver.json"
$UnrealFrameMetricsPath = Join-Path $ResultDirWin "observability\ue_frame_timing.json"

function Start-UnrealLiveMirrorWindow {
    $ue = "D:\\Program Files\\Epic Games\\UE_5.5\\Engine\\Binaries\\Win64\\UnrealEditor.exe"
    $uproject = Join-Path $ProjectRootWin "UE5\\MoSimSceneLibrary\\MoSimSceneLibrary.uproject"
    if (!(Test-Path -LiteralPath $ue)) {
        throw "UnrealEditor.exe not found: $ue"
    }
    if (!(Test-Path -LiteralPath $uproject)) {
        throw "Unreal project not found: $uproject"
    }

    Get-CimInstance Win32_Process -Filter "name = 'UnrealEditor.exe'" |
        Where-Object { $_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and $_.CommandLine -like '* -game*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2

    $args = @(
        $uproject,
        "-game",
        "-windowed",
        "-ResX=1280",
        "-ResY=720",
        "-NoSplash",
        "/Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode",
        "-MoSimSimulationReview",
        "-MoSimDayReview",
        "-MoSimReviewSunIntensity=6.0",
        "-MoSimReviewSkyLightIntensity=2.0",
        "-MoSimReviewExposureBias=0.0",
        "-MoSimPlaybackActorCount=1",
        "-MoSimPlaybackBaseUdpPort=$UnrealUdpPort",
        "-MoSimPlaybackInterpolate",
        "-MoSimPlaybackUseArrivalTiming",
        "-MoSimPlaybackNominalRateHz=$UnrealPlaybackNominalRateHz",
        "-MoSimPlaybackMinimumDisplayRateHz=$UnrealPlaybackMinimumDisplayRateHz",
        "-MoSimPlaybackMaxInterpolationDurationS=$UnrealPlaybackMaxInterpolationDurationS",
        "-MoSimFollowPlaybackCamera",
        "-MoSimFollowCameraBackCm=55",
        "-MoSimFollowCameraRightCm=-14",
        "-MoSimFollowCameraUpCm=28",
        "-MoSimFollowCameraLocationInterpSpeed=0",
        "-MoSimFollowCameraRotationInterpSpeed=0",
        "-MoSimObservabilityRunId=$RunId",
        "-MoSimUeReceiverMetrics=$UnrealReceiverMetricsPath",
        "-MoSimUeFrameMetrics=$UnrealFrameMetricsPath",
        "-ExecCmds=`"t.MaxFPS $UnrealMaxFps`"",
        "-MoSimNoReviewCollision"
    )
    $ueProcess = Start-Process -FilePath $ue -ArgumentList $args -PassThru
    try {
        $ueProcess.PriorityClass = "BelowNormal"
    } catch {
        Write-Warning "Unable to lower UE review process priority: $($_.Exception.Message)"
    }
    [pscustomobject]@{
        process_id = $ueProcess.Id
        udp_port = $UnrealUdpPort
        state_rate_hz = $UnrealStateRateHz
        max_render_fps = $UnrealMaxFps
        process_priority = "BelowNormal"
        display_interpolation = [pscustomobject]@{
            enabled = $true
            timing_basis = "arrival_wall_clock"
            nominal_input_rate_hz = $UnrealPlaybackNominalRateHz
            minimum_display_rate_hz = $UnrealPlaybackMinimumDisplayRateHz
            max_duration_s = $UnrealPlaybackMaxInterpolationDurationS
            claim_boundary = "UE display smoothing only; Gazebo/MAVROS trajectories remain authoritative."
        }
        observability = [pscustomobject]@{
            receiver_metrics_path = $UnrealReceiverMetricsPath
            frame_metrics_path = $UnrealFrameMetricsPath
        }
        pose_topic = $UnrealPoseTopic
        fuel_random_seed = $FuelRandomSeed
        camera = "follow_playback_fixed_offset"
        actual_trail = "disabled"
        planned_trail = "disabled"
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $ResultDirWin "ue_live_mirror_launch.json") -Encoding UTF8
}

if (-not $NoUnreal -and -not $ReuseUnrealWindow) {
    Start-UnrealLiveMirrorWindow
}

$envParts = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "PLANNER_VARIANT=fuel",
    "FUEL_RANDOM_SEED=$FuelRandomSeed",
    "PX4CTRL_CORE_PROFILE=$ControllerCoreProfile",
    "PX4CTRL_HOVER_PERCENTAGE=$Px4ctrlHoverPercentage",
    "MAVROS_STREAM_RATE_HZ=100",
    "MAVROS_SET_STREAM_GROUPS=raw_sensors position extra1 extra2",
    "MAVROS_SET_MESSAGE_INTERVALS=true",
    "MAVROS_SET_MESSAGE_IDS=105:HIGHRES_IMU 30:ATTITUDE 31:ATTITUDE_QUATERNION 32:LOCAL_POSITION_NED",
    "GUI=false",
    "OPEN_RVIZ=$OpenRvizValue",
    "KEEP_ALIVE=$KeepAliveValue",
    "FUEL_OPEN_SPLIT_RVIZ=$OpenRvizValue",
    "UE_LIVE_MIRROR=$((-not $NoUnreal).ToString().ToLowerInvariant())",
    "UE_LIVE_MIRROR_HOST=auto",
    "UE_LIVE_MIRROR_PORT=$UnrealUdpPort",
    "UE_LIVE_MIRROR_ODOM_TOPIC=$UnrealPoseTopic",
    "UE_LIVE_MIRROR_RATE_HZ=$UnrealStateRateHz",
    "WORLD_FILE=$FactoryWorldWsl",
    "FACTORY_MODEL_PATH=$FactoryModelPathWsl",
    "SUNRAY_GAZEBO_LAUNCH_FILE=$ProjectRootWsl/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    "SUNRAY_STRIP_PX4_MODEL_PATH=true",
    "SUNRAY_MID360_PLUGIN_DOWNSAMPLE=$Mid360PluginDownsample",
    "SUNRAY_LIVOX_PLUGIN_FILENAME=$ProjectRootWsl/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws/devel/lib/liblivox_laser_simulation.so",
    "SUNRAY_MID360_CSV_FILE_NAME=mid360-real-centr.csv",
    "SUNRAY_MID360_GOAL5_CSV_STRIDE=4",
    "SUNRAY_UAV_INIT_X=$StartX",
    "SUNRAY_UAV_INIT_Y=$StartY",
    "SUNRAY_UAV_INIT_Z=$SunrayInitialZ",
    "SUNRAY_UAV_INIT_YAW=$StartYaw",
    "TARGET_X=$StartX",
    "TARGET_Y=$StartY",
    "TARGET_Z=$TargetZ",
    "FUEL_FRAME_BRIDGE_ENABLED=true",
    "FUEL_FSM_VISUALIZATION_ENABLED=true",
    "FUEL_VISUALIZATION_BRIDGE_ENABLED=true",
    "FUEL_COVERAGE_VISUALIZATION_ENABLED=false",
    "FUEL_COVERAGE_VISUALIZATION_MIN_X=$BoundaryMinX",
    "FUEL_COVERAGE_VISUALIZATION_MAX_X=$BoundaryMaxX",
    "FUEL_COVERAGE_VISUALIZATION_MIN_Y=$BoundaryMinY",
    "FUEL_COVERAGE_VISUALIZATION_MAX_Y=$BoundaryMaxY",
    "FUEL_COVERAGE_VISUALIZATION_RESOLUTION_M=$CoverageGridResolutionM",
    "FUEL_COVERAGE_VISUALIZATION_SENSOR_RADIUS_M=$CoverageSensorRadiusM",
    "GOAL4_BODY_AXIS_LENGTH_M=$BodyAxisLengthM",
    "GOAL4_BODY_AXIS_SHAFT_M=$BodyAxisShaftM",
    "GOAL4_BODY_AXIS_HEAD_DIAMETER_M=$BodyAxisHeadDiameterM",
    "GOAL4_BODY_AXIS_HEAD_LENGTH_M=$BodyAxisHeadLengthM",
    "FUEL_SENSOR_POSE_SOURCE=$FuelSensorPoseSource",
    "FUEL_FASTLIO_ALIGNMENT_Z_SOURCE=$FuelFastlioAlignmentZSource",
    "FASTLIO_FILTER_SIZE_SURF=$FastlioFilterSizeSurfM",
    "FASTLIO_FILTER_SIZE_MAP=$FastlioFilterSizeMapM",
    "FUEL_FRAME_OFFSET_X=$StartX",
    "FUEL_FRAME_OFFSET_Y=$StartY",
    "FUEL_FRAME_OFFSET_Z=$FuelFrameOffsetZEffective",
    "FUEL_INIT_X=$StartX",
    "FUEL_INIT_Y=$StartY",
    "FUEL_INIT_Z=$TargetZ",
    "FUEL_MAP_SIZE_X=$FuelWindowXEffective",
    "FUEL_MAP_SIZE_Y=$FuelWindowYEffective",
    "FUEL_MAP_SIZE_Z=$FuelWindowZM",
    "FUEL_GRID_RESOLUTION_M=$FuelGridResolutionM",
    "FUEL_MAX_RAY_LENGTH_M=$FuelMaxRayLengthM",
    "FUEL_CLOUD_FREE_SPACE_RAYS_ENABLE=$($FuelCloudFreeSpaceRays.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_CLOUD_FREE_SPACE_RAY_COUNT=$FuelCloudFreeSpaceRayCount",
    "FUEL_CLOUD_FREE_SPACE_RAY_LENGTH_MARGIN=$FuelCloudFreeSpaceRayLengthMarginM",
    "FUEL_DIAGNOSE_POINTCLOUD_RAYCAST=$($FuelDiagnosePointcloudRaycast.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_DIAGNOSE_POINTCLOUD_RAYCAST_THROTTLE_S=$FuelDiagnosePointcloudRaycastThrottleS",
    "FUEL_ASTAR_DIAGNOSE_REJECTION=$($FuelAstarDiagnoseRejection.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_ASTAR_DIAGNOSE_REJECTION_THROTTLE_S=$FuelAstarDiagnoseRejectionThrottleS",
    "FUEL_PERCEPTION_MAX_DIST_M=$FuelPerceptionMaxDistM",
    "FUEL_PERCEPTION_VIS_DIST_M=$FuelPerceptionVisDistM",
    "FUEL_PERCEPTION_TOP_ANGLE_RAD=$FuelPerceptionTopAngleRad",
    "FUEL_PERCEPTION_LEFT_ANGLE_RAD=$FuelPerceptionLeftAngleRad",
    "FUEL_PERCEPTION_RIGHT_ANGLE_RAD=$FuelPerceptionRightAngleRad",
    "FUEL_PERCEPTION_OMNI_HORIZONTAL=$($FuelPerceptionOmniHorizontal.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_FRONTIER_CLUSTER_MIN=$FuelFrontierClusterMin",
    "FUEL_FRONTIER_CLUSTER_SIZE_XY=$FuelFrontierClusterSizeXY",
    "FUEL_FRONTIER_MIN_VISIB_NUM=$FuelFrontierMinVisibNum",
    "FUEL_FRONTIER_MIN_VIEW_FINISH_FRACTION=$FuelFrontierMinViewFinishFraction",
    "FUEL_FRONTIER_MIN_CANDIDATE_CLEARANCE=$FuelFrontierMinCandidateClearance",
    "FUEL_FRONTIER_CANDIDATE_DPHI_RAD=$FuelFrontierCandidateDphiRad",
    "FUEL_FRONTIER_CANDIDATE_RNUM=$FuelFrontierCandidateRnum",
    "FUEL_FRONTIER_CANDIDATE_RMIN=$FuelFrontierCandidateRmin",
    "FUEL_FRONTIER_CANDIDATE_RMAX=$FuelFrontierCandidateRmax",
    "FUEL_FRONTIER_ALLOW_NEAR_UNKNOWN_CANDIDATE=$($FuelAllowNearUnknownCandidate.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_FRONTIER_ALLOW_UNKNOWN_RAY_VISIBILITY=$($FuelAllowUnknownRayVisibility.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_FRONTIER_DIAGNOSE_CLUSTER_VIEWPOINTS=$($FuelFrontierDiagnoseClusterViewpoints.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_FRONTIER_DIAGNOSE_CLUSTER_LOG_LIMIT=$FuelFrontierDiagnoseClusterLogLimit",
    "FUEL_EXPLORATION_REFINE_LOCAL=$(((-not $FuelNoLocalRefine.IsPresent)).ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_REFINED_RADIUS=$FuelExplorationRefinedRadius",
    "FUEL_EXPLORATION_TOP_VIEW_NUM=$FuelExplorationTopViewNum",
    "FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_ENABLE=$($FuelNearFrontierEscape.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_DISTANCE=$FuelNearFrontierEscapeDistanceM",
    "FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_MAX_SPEED=$FuelNearFrontierEscapeMaxSpeedMps",
    "FUEL_EXPLORATION_NEAR_FRONTIER_ESCAPE_ALTERNATIVE_DISTANCE=$FuelNearFrontierEscapeAlternativeDistanceM",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_ENABLE=$($FuelGlobalExpansionBias.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_RANK_WINDOW=$FuelGlobalExpansionBiasRankWindow",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_DIST_WEIGHT=$FuelGlobalExpansionBiasDistWeight",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_LATERAL_WEIGHT=$FuelGlobalExpansionBiasLateralWeight",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_AXIS=$FuelGlobalExpansionBiasAxis",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_MIN_GAIN=$FuelGlobalExpansionBiasMinGain",
    "FUEL_EXPLORATION_GLOBAL_EXPANSION_BIAS_OVERRIDE_REFINE=$($FuelGlobalExpansionBiasOverrideRefine.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_ENABLE=$($FuelCoverageExpansion.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_AXIS=$FuelCoverageExpansionAxis",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_RANK_WINDOW=$FuelCoverageExpansionRankWindow",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_MIN_GAIN=$FuelCoverageExpansionMinGain",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_DIST_WEIGHT=$FuelCoverageExpansionDistWeight",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_GRID_RESOLUTION=$FuelCoverageExpansionGridResolutionM",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_SENSOR_RADIUS=$FuelCoverageExpansionSensorRadiusM",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_PROJECT_HORIZON=$FuelCoverageExpansionProjectHorizonM",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_GRID_WEIGHT=$FuelCoverageExpansionGridWeight",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_SPAN_WEIGHT=$FuelCoverageExpansionSpanWeight",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_UNCOVERED_TARGET_WEIGHT=$FuelCoverageExpansionUncoveredTargetWeight",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_SCORE_COMMITTED_GOAL=$($FuelCoverageExpansionScoreCommittedGoal.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_DIRECT_UNCOVERED_FALLBACK=$($FuelCoverageExpansionDirectUncoveredFallback.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_GLOBAL_SELECTOR=$($FuelCoverageExpansionGlobalSelector.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_EXPLORATION_COVERAGE_EXPANSION_LOG_CANDIDATES=$($FuelCoverageExpansionLogCandidates.IsPresent.ToString().ToLowerInvariant())",
    "FUEL_P_OCC=$FuelPOcc",
    "FUEL_OBSTACLES_INFLATION=$FuelObstaclesInflationM",
    "EGO_MAX_VEL=$FuelPlannerMaxVelMps",
    "EGO_MAX_ACC=$FuelPlannerMaxAccMps2",
    "FUEL_BOX_MIN_X=$FuelBoxMinX",
    "FUEL_BOX_MIN_Y=$FuelBoxMinY",
    "FUEL_BOX_MIN_Z=$FuelBoxMinZWorld",
    "FUEL_BOX_MAX_X=$FuelBoxMaxX",
    "FUEL_BOX_MAX_Y=$FuelBoxMaxY",
    "FUEL_BOX_MAX_Z=$FuelBoxMaxZWorld",
    "FACTORY_INDOOR_BOUNDARY_MIN_X=$CoverageMinXEffective",
    "FACTORY_INDOOR_BOUNDARY_MAX_X=$CoverageMaxXEffective",
    "FACTORY_INDOOR_BOUNDARY_MIN_Y=$CoverageMinYEffective",
    "FACTORY_INDOOR_BOUNDARY_MAX_Y=$CoverageMaxYEffective",
    "FUEL_COVERAGE_SUPERVISOR_ENABLED=$CoverageSupervisorEnabledValue",
    "FUEL_COVERAGE_SUPERVISOR_MAX_RUNTIME_S=$CoverageSupervisorMaxRuntimeS",
    "FUEL_COVERAGE_SUPERVISOR_INITIAL_DELAY_S=$CoverageSupervisorInitialDelayS",
    "FUEL_COVERAGE_SUPERVISOR_TRIGGER_INTERVAL_S=$CoverageSupervisorTriggerIntervalS",
    "FUEL_COVERAGE_SUPERVISOR_STALE_BSPLINE_S=$CoverageSupervisorStaleBsplineS",
    "FUEL_COVERAGE_SUPERVISOR_MIN_TRIGGER_MOVE_M=$CoverageSupervisorMinTriggerMoveM",
    "FUEL_COVERAGE_SUPERVISOR_TIME_BASIS=$CoverageSupervisorTimeBasis",
    "FUEL_COVERAGE_SUPERVISOR_REQUIRE_TARGET_Z=$($CoverageSupervisorRequireTargetZ.ToString().ToLowerInvariant())",
    "FUEL_COVERAGE_SUPERVISOR_TRIGGER_Z_TOLERANCE_M=$CoverageSupervisorTriggerZToleranceM",
    "FUEL_COVERAGE_SUPERVISOR_NO_GROWTH_TIMEOUT_S=$CoverageSupervisorNoGrowthTimeoutS",
    "FUEL_COVERAGE_SUPERVISOR_MIN_GROWTH_CELLS=$CoverageSupervisorMinGrowthCells",
    "FUEL_COVERAGE_SUPERVISOR_GRID_RESOLUTION_M=$CoverageGridResolutionM",
    "FUEL_COVERAGE_SUPERVISOR_SENSOR_RADIUS_M=$CoverageSensorRadiusM",
    "FUEL_COVERAGE_SUPERVISOR_MIN_RATIO=$MinSensorCoverageRatio",
    "FUEL_VIRTUAL_CEIL_HEIGHT=$FuelVirtualCeilHeightM",
    "FUEL_MANAGER_LOCAL_SEGMENT_LENGTH=$FuelManagerLocalSegmentLength",
    "EGO_VIRTUAL_CEIL_HEIGHT=$FuelVirtualCeilHeightM",
    "EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.80",
    "DIFF_CMD_MIN_Z=$CmdMinZEffective",
    "DIFF_CMD_MAX_Z=$CmdMaxZEffective",
    "FUEL_CMD_FIXED_Z=$CmdFixedZEffective",
    "FUEL_CMD_ZERO_ALL_DYNAMICS=false",
    "FUEL_EXPLORATION_EXECUTE_S=$ExplorationExecuteS",
    "PLANNER_EXPLORATION_TIME_BASIS=$ExplorationTimeBasis",
    "FACTORY_MIN_EXPECTED_REAL_TIME_FACTOR=$MinimumExpectedRealTimeFactor",
    "GOAL4_TAKEOFF_HEIGHT=$EffectiveTakeoffHeight",
    "PX4CTRL_AUTO_TAKEOFF_HEIGHT=$EffectivePx4ctrlRelativeTakeoffHeight",
    "GOAL4_TAKEOFF_TIMEOUT_S=$TakeoffTimeoutS",
    "DIFF_PUBLISH_HOVER_DURING_TAKEOFF=$($PublishHoverDuringTakeoff.ToString().ToLowerInvariant())",
    "DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S=$PublishHoverDuringTakeoffDelayS",
    "FUEL_CMD_SMOOTH_ENABLE=$($FuelCmdSmoothEnable.ToString().ToLowerInvariant())",
    "FUEL_CMD_SMOOTH_MAX_SPEED_MPS=$FuelCmdSmoothMaxSpeedMps",
    "FUEL_CMD_SMOOTH_MAX_STEP_M=$FuelCmdSmoothMaxStepM",
    "FUEL_CMD_SMOOTH_ZERO_DYNAMICS=false",
    "FUEL_CMD_MOTION_TIME_BASIS=ros_sim_time",
    "FUEL_CMD_RECOMPUTE_VELOCITY_FROM_POSITION=$($FuelCmdRecomputeVelocityFromPosition.ToString().ToLowerInvariant())",
    "FUEL_CMD_MAX_VELOCITY_MPS=$FuelCmdMaxVelocityMps",
    "FUEL_CMD_MAX_ACCELERATION_MPS2=$FuelCmdMaxAccelerationMps2",
    "FUEL_CMD_MAX_LATERAL_ACCELERATION_MPS2=$FuelCmdMaxLateralAccelerationMps2",
    "FUEL_CMD_MAX_JERK_MPS3=$FuelCmdMaxJerkMps3",
    "PLANNER_CMD_ODOM_TARGET_GUARD_ENABLE=true",
    "PLANNER_CMD_ODOM_TARGET_GUARD_TOPIC=/uav1/mavros/local_position/odom",
    "PLANNER_CMD_ODOM_TARGET_GUARD_TIMEOUT_S=0.3",
    "PLANNER_CMD_MAX_TARGET_DISTANCE_FROM_ODOM_M=0",
    "PLANNER_CMD_MAX_XY_TARGET_DISTANCE_FROM_ODOM_M=$FuelMaxXYTargetDistanceFromOdomM",
    "PLANNER_CMD_ODOM_DISTANCE_POLICY=project_toward_raw",
    "PLANNER_CMD_ODOM_GUARD_ZERO_DYNAMICS=false",
    "FUEL_FORWARD_BEFORE_FIRST_BSPLINE=false",
    "PLANNER_CMD_ADAPTER_INITIAL_ENABLED=$($PlannerCmdAdapterInitialEnabled.ToString().ToLowerInvariant())",
    "PLANNER_CMD_REQUIRE_FRESH_RAW_AFTER_ENABLE=true",
    "PLANNER_CMD_SEED_FROM_ODOM_ON_ENABLE=true",
    "GOAL4_EGO_TAKEOVER_TIMEOUT_S=$EgoTakeoverTimeoutS",
    "GOAL4_RECORD_HZ=100",
    "GOAL4_RECORD_CMD_HZ=100",
    "GOAL4_MAX_PATH_POINTS=0",
    "GOAL4_PATH_PUBLISH_HZ=20",
    "GOAL4_REVIEW_HOLD_PATH_PUBLISH_HZ=10",
    "POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08",
    "POINTCLOUD_MAX_SENSOR_RANGE_M=80.0",
    "POINTCLOUD_MIN_WORLD_Z_M=$PointCloudTransformMinWorldZM",
    "POINTCLOUD_MAX_WORLD_Z_M=4.0",
    "POINTCLOUD_MAX_ABS_ODOM_XY_M=$PointCloudMaxAbsOdomXYM",
    "POINTCLOUD_REVIEW_MIN_WORLD_Z_M=$PointCloudReviewMinWorldZM",
    "POINTCLOUD_REVIEW_MAX_WORLD_Z_M=4.0",
    "POINTCLOUD_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "POINTCLOUD_REVIEW_MAX_ACCUMULATED_POINTS=$PointCloudCap",
    "POINTCLOUD_REVIEW_PUBLISH_RATE_HZ=2.0",
    "OCCUPANCY_REVIEW_SOURCE_TOPIC=$OccupancyReviewSourceTopic",
    "OCCUPANCY_TOPIC=/sdf_map/occupancy_all",
    "OCCUPANCY_REVIEW_MIN_Z=0.20",
    "OCCUPANCY_REVIEW_MAX_Z=4.0",
    "OCCUPANCY_REVIEW_VOXEL_SIZE_M=0.20",
    "OCCUPANCY_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "OCCUPANCY_REVIEW_MAX_ACCUMULATED_POINTS=$OccupancyCap",
    "OCCUPANCY_REVIEW_PUBLISH_RATE_HZ=2.0",
    "OCCUPANCY_REVIEW_QUALITY_ODOM_TOPIC=/uav1/mavros/local_position/odom",
    "ENABLE_POINTCLOUD_REVIEW_ACCUMULATION=$ReviewAccumulationValue",
    "ENABLE_OCCUPANCY_REVIEW_ACCUMULATION=$ReviewAccumulationValue",
    "ENABLE_CONTINUOUS_OCCUPANCY_REVIEW=$ReviewAccumulationValue",
    "CONTINUOUS_OCCUPANCY_REVIEW_SOURCE_TOPIC=/mosim/goal4/livox_world_accumulated",
    "CONTINUOUS_OCCUPANCY_REVIEW_TOPIC=/mosim/goal4/occupancy_object_review",
    "CONTINUOUS_OCCUPANCY_REVIEW_VOXEL_SIZE_M=$ContinuousOccupancyVoxelSizeM",
    "CONTINUOUS_OCCUPANCY_REVIEW_MIN_Z=$PointCloudReviewMinWorldZM",
    "CONTINUOUS_OCCUPANCY_REVIEW_MAX_Z=4.0",
    "CONTINUOUS_OCCUPANCY_REVIEW_CLOSING_ITERATIONS=$ContinuousOccupancyClosingIterations",
    "CONTINUOUS_OCCUPANCY_REVIEW_MIN_COMPONENT_VOXELS=$ContinuousOccupancyMinComponentVoxels",
    "CONTINUOUS_OCCUPANCY_REVIEW_CONNECTIVITY=$ContinuousOccupancyConnectivity",
    "CONTINUOUS_OCCUPANCY_REVIEW_MAX_POINTS_PER_CLOUD=500000",
    "CONTINUOUS_OCCUPANCY_REVIEW_MAX_ACCUMULATED_VOXELS=$OccupancyCap",
    "CONTINUOUS_OCCUPANCY_REVIEW_MAX_DENSE_VOXELS=12000000",
    "CONTINUOUS_OCCUPANCY_REVIEW_PUBLISH_RATE_HZ=1.0",
    "GOAL4_RECORD_ROSBAG=$RecordRosbagValue",
    "MAVROS_READY_TIMEOUT_S=120",
    "TOTAL_TIMEOUT_S=$TotalTimeoutS",
    "DIFF_INTERACTIVE_REVIEW_HOLD_S=$ReviewHoldS"
)
if (-not [string]::IsNullOrWhiteSpace($FuelExplorationAsanOptions)) {
    $envParts += "FUEL_EXPLORATION_ASAN_OPTIONS=$FuelExplorationAsanOptions"
}
if ($FuelDisableRosout) {
    $envParts += "FUEL_DISABLE_ROSOUT=true"
}
if (-not [string]::IsNullOrWhiteSpace($FuelWorkspaceWsl)) {
    $envParts += "GOAL4_FUEL_WS=$FuelWorkspaceWsl"
}

function ConvertTo-BashEnvAssignment {
    param([Parameter(Mandatory = $true)][string]$Assignment)

    $separatorIndex = $Assignment.IndexOf("=")
    if ($separatorIndex -le 0) {
        throw "Invalid Bash environment assignment: $Assignment"
    }

    $name = $Assignment.Substring(0, $separatorIndex)
    if ($name -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
        throw "Invalid Bash environment variable name: $name"
    }

    $singleQuote = [string][char]39
    $doubleQuote = [string][char]34
    $value = $Assignment.Substring($separatorIndex + 1)
    $escapedValue = $value.Replace($singleQuote, $singleQuote + $doubleQuote + $singleQuote + $doubleQuote + $singleQuote)
    return ($name + "=" + $singleQuote + $escapedValue + $singleQuote)
}

$bashEnvParts = @($envParts | ForEach-Object { ConvertTo-BashEnvAssignment $_ })

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$bashStatus = '$?'
$bashScriptWin = Join-Path $ResultDirWin "start_factory_fuel_single_exploration_review.sh"
$bashScriptWsl = $ResultDirWsl + "/start_factory_fuel_single_exploration_review.sh"
$command = @"
#!/usr/bin/env bash
set -e
cd $ProjectRootWsl
mkdir -p '$ResultDirWsl'
exec > >(tee -a '$ResultDirWsl/bootstrap.log') 2>&1
date --iso-8601=seconds > '$ResultDirWsl/background_start_marker.txt'
$preflight || { echo $bashStatus > '$ResultDirWsl/preflight_exit_code.txt'; exit 2; }
echo 0 > '$ResultDirWsl/preflight_exit_code.txt'
export GAZEBO_MODEL_PATH='$FactoryModelPathWsl':"`${GAZEBO_MODEL_PATH:-}"
rosbag_pid=""
rosbag_watch_pid=""
profile_pid=""
if [[ '$ProfileRuntimeProcessesValue' == 'true' ]]; then
  python3 Scripts/sunray/profile_fuel_runtime_processes.py \
    --output-csv '$ResultDirWsl/fuel_runtime_process_profile.csv' \
    --output-json '$ResultDirWsl/fuel_runtime_process_profile.json' \
    --sample-period-s '$ProfileRuntimeSamplePeriodS' \
    --startup-wait-s 240 \
    --max-runtime-s '$TotalTimeoutS' \
    > '$ResultDirWsl/fuel_runtime_process_profile.log' 2>&1 &
  profile_pid=`$!
fi
if [[ '$RecordRosbagValue' == 'true' ]]; then
  source /opt/ros/noetic/setup.bash
  if command -v rosbag >/dev/null 2>&1; then
    (
      until rostopic list >/dev/null 2>&1; do sleep 1; done
      exec rosbag record --lz4 -O '$ResultDirWsl/factory_fuel_review.bag' $RosbagTopicArgs
    ) > '$ResultDirWsl/rosbag_record.log' 2>&1 &
    rosbag_pid=`$!
    (
      while [[ ! -s '$ResultDirWsl/EGO_SINGLE_METRICS.json' ]]; do sleep 1; done
      sleep 5
      kill -INT "`$rosbag_pid" >/dev/null 2>&1 || true
    ) > '$ResultDirWsl/rosbag_stop_watcher.log' 2>&1 &
    rosbag_watch_pid=`$!
    echo "started" > '$ResultDirWsl/rosbag_status.txt'
  else
    echo "rosbag command not found" > '$ResultDirWsl/rosbag_status.txt'
  fi
fi
echo "starting run_px4ctrl_ego_single_gate.sh"
set +e
$($bashEnvParts -join " ") bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh > '$ResultDirWsl/background_launcher.log' 2>&1
run_exit=$bashStatus
echo `$run_exit > '$ResultDirWsl/background_exit_code.txt'
if [[ -n "`$profile_pid" ]]; then
  kill -INT "`$profile_pid" >/dev/null 2>&1 || true
  wait "`$profile_pid" >/dev/null 2>&1 || true
fi
if [[ -n "`$rosbag_pid" ]]; then
  kill -INT "`$rosbag_pid" >/dev/null 2>&1 || true
  wait "`$rosbag_pid" >/dev/null 2>&1 || true
  if [[ -s '$ResultDirWsl/factory_fuel_review.bag' ]]; then
    echo "complete" > '$ResultDirWsl/rosbag_status.txt'
  fi
fi
if [[ -n "`$rosbag_watch_pid" ]]; then
  kill "`$rosbag_watch_pid" >/dev/null 2>&1 || true
fi
exit `$run_exit
"@

[System.IO.File]::WriteAllText($bashScriptWin, $command, [System.Text.UTF8Encoding]::new($false))
$stdoutLog = Join-Path $ResultDirWin "windows_child_stdout.log"
$stderrLog = Join-Path $ResultDirWin "windows_child_stderr.log"
if ($Foreground) {
    & wsl.exe -d Ubuntu-20.04 --exec bash $bashScriptWsl
    $runExitCode = $LASTEXITCODE
    [pscustomobject]@{
        RunId = $RunId
        ProcessId = $null
        ResultDir = $ResultDirWin
        World = $FactoryWorldWsl
        PointCloudAccumulationCap = $PointCloudCap
        OccupancyAccumulationCap = $OccupancyCap
        ExitCode = $runExitCode
        ExecutionMode = "foreground"
    }
    exit $runExitCode
} else {
    $proc = Start-Process -FilePath "wsl.exe" -ArgumentList @("-d", "Ubuntu-20.04", "--exec", "bash", $bashScriptWsl) -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru

    [pscustomobject]@{
        RunId = $RunId
        ProcessId = $proc.Id
        ResultDir = $ResultDirWin
        World = $FactoryWorldWsl
        PointCloudAccumulationCap = $PointCloudCap
        OccupancyAccumulationCap = $OccupancyCap
        ExecutionMode = "background"
    }
}
