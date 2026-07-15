param(
    [string]$RunId = ("factory_l2_fuel_same_flight_coverage_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [double]$ExplorationExecuteS = 120.0,
    [double]$EgoTakeoverTimeoutS = 140.0,
    [double]$TargetZ = 1.2,
    [double]$TakeoffTimeoutS = 120.0,
    [double]$StartYaw = 0.0,
    [double]$BoundaryPaddingM = 0.0,
    [double]$FuelGridResolutionM = 0.20,
    [double]$FuelMaxRayLengthM = 4.5,
    [switch]$FuelCloudFreeSpaceRays,
    [int]$FuelCloudFreeSpaceRayCount = 72,
    [double]$FuelCloudFreeSpaceRayLengthMarginM = 0.5,
    [switch]$FuelDiagnosePointcloudRaycast,
    [double]$FuelDiagnosePointcloudRaycastThrottleS = 5.0,
    [switch]$FuelAstarDiagnoseRejection,
    [double]$FuelAstarDiagnoseRejectionThrottleS = 1.0,
    [double]$FuelPerceptionMaxDistM = 4.5,
    [double]$FuelPerceptionVisDistM = 1.0,
    [double]$FuelPerceptionTopAngleRad = 0.56125,
    [double]$FuelPerceptionLeftAngleRad = 0.69222,
    [double]$FuelPerceptionRightAngleRad = 0.68901,
    [switch]$FuelPerceptionOmniHorizontal,
    [double]$FuelFrontierCandidateDphiRad = 0.2617993833333333,
    [int]$FuelFrontierCandidateRnum = 3,
    [double]$FuelFrontierCandidateRmin = 1.5,
    [double]$FuelFrontierCandidateRmax = 2.5,
    [int]$FuelFrontierClusterMin = 60,
    [int]$FuelFrontierMinVisibNum = 5,
    [double]$FuelFrontierMinViewFinishFraction = 0.2,
    [double]$FuelFrontierMinCandidateClearance = 0.12,
    [switch]$FuelAllowNearUnknownCandidate,
    [switch]$FuelAllowUnknownRayVisibility,
    [switch]$FuelFrontierDiagnoseClusterViewpoints,
    [int]$FuelFrontierDiagnoseClusterLogLimit = 20,
    [switch]$FuelNoLocalRefine,
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
    [double]$FuelWindowZM = 3.0,
    [double]$FuelBoxMinZM = 0.90,
    [double]$FuelBoxMaxZM = 1.60,
    [double]$FuelFrameOffsetZM = [double]::NaN,
    [double]$FuelLocalFlightZM = [double]::NaN,
    [double]$FuelVirtualCeilHeightM = 1.60,
    [double]$FuelManagerLocalSegmentLength = 6.0,
    [double]$CmdMinZM = 0.90,
    [double]$CmdMaxZM = 1.60,
    [double]$FuelPlannerMaxVelMps = 0.8,
    [double]$FuelPlannerMaxAccMps2 = 0.8,
    [double]$FuelCmdSmoothMaxSpeedMps = 0.8,
    [double]$FuelCmdSmoothMaxStepM = 0.02,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [double]$MinSensorCoverageRatio = 0.80,
    [double]$CoverageSupervisorInitialDelayS = 35.0,
    [double]$CoverageSupervisorTriggerIntervalS = 35.0,
    [double]$CoverageSupervisorStaleBsplineS = 18.0,
    [double]$CoverageSupervisorMinTriggerMoveM = 0.5,
    [string]$CoverageSupervisorTimeBasis = "wall",
    [string]$ExplorationTimeBasis = "wall",
    [bool]$CoverageSupervisorRequireTargetZ = $true,
    [double]$CoverageSupervisorTriggerZToleranceM = 0.3,
    [double]$CoverageSupervisorNoGrowthTimeoutS = 300.0,
    [int]$CoverageSupervisorMinGrowthCells = 1,
    [double]$CoverageSupervisorMaxRuntimeS = 0.0,
    [int]$PollSeconds = 10,
    [int]$RuntimeTimeoutS = 0,
    [int]$OuterWaitTimeoutS = 0,
    [int]$PostCleanupMetricsWaitS = 90,
    [int]$MetricsSettleWaitS = 5,
    [int]$ReviewHoldS = 5,
    [string]$FuelWorkspaceWsl = "",
    [switch]$WithRviz,
    [switch]$KeepAlive,
    [switch]$SkipPreflight,
    [switch]$NoUnlimitedAccumulation
)

$ErrorActionPreference = "Stop"

$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$EnvelopePath = Join-Path $ProjectRootWin "Config\gazebo\scene_profiles\factory_l2_exploration_envelope.json"
$SingleRunScript = Join-Path $ProjectRootWin "Scripts\sunray\start_factory_fuel_single_exploration_review.ps1"
$ResultDir = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$CoverageDir = Join-Path $ResultDir "coverage_packet"
$ManifestPath = Join-Path $ResultDir "FACTORY_L2_FUEL_SAME_FLIGHT_COVERAGE_PROBE.json"

function Get-Number($Value, [double]$Default) {
    if ($null -eq $Value) { return $Default }
    try { return [double]$Value } catch { return $Default }
}

if (-not (Test-Path -LiteralPath $EnvelopePath)) {
    throw "missing envelope: $EnvelopePath"
}
if (-not (Test-Path -LiteralPath $SingleRunScript)) {
    throw "missing single-run script: $SingleRunScript"
}

New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null

$envelope = Get-Content -LiteralPath $EnvelopePath -Raw | ConvertFrom-Json
$boundary = $envelope.exploration_boundary
$minX = Get-Number $boundary.min_x_m 0.0
$maxX = Get-Number $boundary.max_x_m 0.0
$minY = Get-Number $boundary.min_y_m 0.0
$maxY = Get-Number $boundary.max_y_m 0.0
$centerX = Get-Number $boundary.center_x_m (($minX + $maxX) * 0.5)
$centerY = Get-Number $boundary.center_y_m (($minY + $maxY) * 0.5)
$boxMinX = $minX + $BoundaryPaddingM
$boxMaxX = $maxX - $BoundaryPaddingM
$boxMinY = $minY + $BoundaryPaddingM
$boxMaxY = $maxY - $BoundaryPaddingM
if ($boxMinX -ge $boxMaxX -or $boxMinY -ge $boxMaxY) {
    throw "invalid boundary padding: $BoundaryPaddingM"
}
$fuelWindowX = $boxMaxX - $boxMinX
$fuelWindowY = $boxMaxY - $boxMinY
$runtimeBudget = if ($RuntimeTimeoutS -gt 0) {
    $RuntimeTimeoutS
} else {
    [int]([Math]::Ceiling($ExplorationExecuteS + 240))
}
$outerWaitBudget = if ($OuterWaitTimeoutS -gt 0) {
    $OuterWaitTimeoutS
} else {
    $runtimeBudget + 180
}
$effectiveCoverageSupervisorMaxRuntimeS = if ($CoverageSupervisorMaxRuntimeS -gt 0) {
    $CoverageSupervisorMaxRuntimeS
} else {
    $ExplorationExecuteS
}

$singleArgs = @{
    RunId = $RunId
    ExplorationExecuteS = $ExplorationExecuteS
    EgoTakeoverTimeoutS = $EgoTakeoverTimeoutS
    MissionTotalTimeoutS = $runtimeBudget
    ReviewHoldS = $ReviewHoldS
    TargetZ = $TargetZ
    TakeoffTimeoutS = $TakeoffTimeoutS
    StartX = $centerX
    StartY = $centerY
    StartYaw = $StartYaw
    FuelWindowXYM = $fuelWindowX
    FuelWindowYM = $fuelWindowY
    FuelBoxMinXOverride = $boxMinX
    FuelBoxMaxXOverride = $boxMaxX
    FuelBoxMinYOverride = $boxMinY
    FuelBoxMaxYOverride = $boxMaxY
    FuelWindowZM = $FuelWindowZM
    FuelBoxMinZM = $FuelBoxMinZM
    FuelBoxMaxZM = $FuelBoxMaxZM
    FuelFrameOffsetZM = $FuelFrameOffsetZM
    FuelLocalFlightZM = $FuelLocalFlightZM
    FuelVirtualCeilHeightM = $FuelVirtualCeilHeightM
    FuelManagerLocalSegmentLength = $FuelManagerLocalSegmentLength
    FuelGridResolutionM = $FuelGridResolutionM
    FuelMaxRayLengthM = $FuelMaxRayLengthM
    FuelCloudFreeSpaceRayCount = $FuelCloudFreeSpaceRayCount
    FuelCloudFreeSpaceRayLengthMarginM = $FuelCloudFreeSpaceRayLengthMarginM
    FuelDiagnosePointcloudRaycastThrottleS = $FuelDiagnosePointcloudRaycastThrottleS
    FuelAstarDiagnoseRejectionThrottleS = $FuelAstarDiagnoseRejectionThrottleS
    FuelPerceptionMaxDistM = $FuelPerceptionMaxDistM
    FuelPerceptionVisDistM = $FuelPerceptionVisDistM
    FuelPerceptionTopAngleRad = $FuelPerceptionTopAngleRad
    FuelPerceptionLeftAngleRad = $FuelPerceptionLeftAngleRad
    FuelPerceptionRightAngleRad = $FuelPerceptionRightAngleRad
    FuelFrontierCandidateDphiRad = $FuelFrontierCandidateDphiRad
    FuelFrontierCandidateRnum = $FuelFrontierCandidateRnum
    FuelFrontierCandidateRmin = $FuelFrontierCandidateRmin
    FuelFrontierCandidateRmax = $FuelFrontierCandidateRmax
    FuelFrontierClusterMin = $FuelFrontierClusterMin
    FuelFrontierMinVisibNum = $FuelFrontierMinVisibNum
    FuelFrontierMinViewFinishFraction = $FuelFrontierMinViewFinishFraction
    FuelFrontierMinCandidateClearance = $FuelFrontierMinCandidateClearance
    FuelPOcc = $FuelPOcc
    FuelPlannerMaxVelMps = $FuelPlannerMaxVelMps
    FuelPlannerMaxAccMps2 = $FuelPlannerMaxAccMps2
    FuelCmdSmoothMaxSpeedMps = $FuelCmdSmoothMaxSpeedMps
    FuelCmdSmoothMaxStepM = $FuelCmdSmoothMaxStepM
    CmdMinZM = $CmdMinZM
    CmdMaxZM = $CmdMaxZM
    PointCloudMaxAbsOdomXYM = 1000.0
    PointCloudTransformMinWorldZM = -0.2
    PointCloudReviewMinWorldZM = 0.2
    EnableCoverageSupervisor = $true
    CoverageBoundaryMinX = $minX
    CoverageBoundaryMaxX = $maxX
    CoverageBoundaryMinY = $minY
    CoverageBoundaryMaxY = $maxY
    CoverageGridResolutionM = $CoverageGridResolutionM
    CoverageSensorRadiusM = $CoverageSensorRadiusM
    MinSensorCoverageRatio = $MinSensorCoverageRatio
    CoverageSupervisorMaxRuntimeS = $effectiveCoverageSupervisorMaxRuntimeS
    CoverageSupervisorInitialDelayS = $CoverageSupervisorInitialDelayS
    CoverageSupervisorTriggerIntervalS = $CoverageSupervisorTriggerIntervalS
    CoverageSupervisorStaleBsplineS = $CoverageSupervisorStaleBsplineS
    CoverageSupervisorMinTriggerMoveM = $CoverageSupervisorMinTriggerMoveM
    CoverageSupervisorTimeBasis = $CoverageSupervisorTimeBasis
    ExplorationTimeBasis = $ExplorationTimeBasis
    CoverageSupervisorRequireTargetZ = $CoverageSupervisorRequireTargetZ
    CoverageSupervisorTriggerZToleranceM = $CoverageSupervisorTriggerZToleranceM
    CoverageSupervisorNoGrowthTimeoutS = $CoverageSupervisorNoGrowthTimeoutS
    CoverageSupervisorMinGrowthCells = $CoverageSupervisorMinGrowthCells
}
if (-not [string]::IsNullOrWhiteSpace($FuelWorkspaceWsl)) {
    $singleArgs.FuelWorkspaceWsl = $FuelWorkspaceWsl
}
if ($FuelCloudFreeSpaceRays) { $singleArgs.FuelCloudFreeSpaceRays = $true }
if ($FuelDiagnosePointcloudRaycast) { $singleArgs.FuelDiagnosePointcloudRaycast = $true }
if ($FuelAstarDiagnoseRejection) { $singleArgs.FuelAstarDiagnoseRejection = $true }
if ($FuelPerceptionOmniHorizontal) { $singleArgs.FuelPerceptionOmniHorizontal = $true }
if ($FuelAllowNearUnknownCandidate) { $singleArgs.FuelAllowNearUnknownCandidate = $true }
if ($FuelAllowUnknownRayVisibility) { $singleArgs.FuelAllowUnknownRayVisibility = $true }
if ($FuelFrontierDiagnoseClusterViewpoints) { $singleArgs.FuelFrontierDiagnoseClusterViewpoints = $true }
$singleArgs.FuelFrontierDiagnoseClusterLogLimit = $FuelFrontierDiagnoseClusterLogLimit
if ($FuelNoLocalRefine) { $singleArgs.FuelNoLocalRefine = $true }
if ($FuelGlobalExpansionBias) { $singleArgs.FuelGlobalExpansionBias = $true }
$singleArgs.FuelGlobalExpansionBiasRankWindow = $FuelGlobalExpansionBiasRankWindow
$singleArgs.FuelGlobalExpansionBiasDistWeight = $FuelGlobalExpansionBiasDistWeight
$singleArgs.FuelGlobalExpansionBiasLateralWeight = $FuelGlobalExpansionBiasLateralWeight
$singleArgs.FuelGlobalExpansionBiasAxis = $FuelGlobalExpansionBiasAxis
$singleArgs.FuelGlobalExpansionBiasMinGain = $FuelGlobalExpansionBiasMinGain
if ($FuelGlobalExpansionBiasOverrideRefine) { $singleArgs.FuelGlobalExpansionBiasOverrideRefine = $true }
if ($FuelCoverageExpansion) { $singleArgs.FuelCoverageExpansion = $true }
$singleArgs.FuelCoverageExpansionAxis = $FuelCoverageExpansionAxis
$singleArgs.FuelCoverageExpansionRankWindow = $FuelCoverageExpansionRankWindow
$singleArgs.FuelCoverageExpansionMinGain = $FuelCoverageExpansionMinGain
$singleArgs.FuelCoverageExpansionDistWeight = $FuelCoverageExpansionDistWeight
$singleArgs.FuelCoverageExpansionGridResolutionM = $FuelCoverageExpansionGridResolutionM
$singleArgs.FuelCoverageExpansionSensorRadiusM = $FuelCoverageExpansionSensorRadiusM
$singleArgs.FuelCoverageExpansionProjectHorizonM = $FuelCoverageExpansionProjectHorizonM
$singleArgs.FuelCoverageExpansionGridWeight = $FuelCoverageExpansionGridWeight
$singleArgs.FuelCoverageExpansionSpanWeight = $FuelCoverageExpansionSpanWeight
$singleArgs.FuelCoverageExpansionUncoveredTargetWeight = $FuelCoverageExpansionUncoveredTargetWeight
if ($FuelCoverageExpansionScoreCommittedGoal) { $singleArgs.FuelCoverageExpansionScoreCommittedGoal = $true }
if ($FuelCoverageExpansionDirectUncoveredFallback) { $singleArgs.FuelCoverageExpansionDirectUncoveredFallback = $true }
if ($FuelCoverageExpansionGlobalSelector) { $singleArgs.FuelCoverageExpansionGlobalSelector = $true }
if ($FuelCoverageExpansionLogCandidates) { $singleArgs.FuelCoverageExpansionLogCandidates = $true }
if (-not $WithRviz) { $singleArgs.NoRviz = $true }
if (-not $KeepAlive) { $singleArgs.NoKeepAlive = $true }
if ($SkipPreflight) { $singleArgs.SkipPreflight = $true }
if (-not $NoUnlimitedAccumulation) { $singleArgs.UnlimitedAccumulation = $true }

$startInfo = & $SingleRunScript @singleArgs
$deadline = (Get-Date).AddSeconds($outerWaitBudget)
$exitCodePath = Join-Path $ResultDir "background_exit_code.txt"
while (-not (Test-Path -LiteralPath $exitCodePath) -and (Get-Date) -lt $deadline) {
    Start-Sleep -Seconds $PollSeconds
}

$timedOut = -not (Test-Path -LiteralPath $exitCodePath)
$cleanupAfterTimeout = $false
if ($timedOut) {
    $cleanupAfterTimeout = $true
    $cleanupLog = Join-Path $ResultDir "same_flight_timeout_cleanup.txt"
    & wsl -d Ubuntu-20.04 --exec bash -lc "set +e; ps -eo pid,ppid,stat,etime,cmd | grep -E 'run_px4ctrl_ego_single_gate|fuel_native_traj_server|fuel_compat_traj_server|exploration_node|factory_l2_same_flight_coverage_supervisor|fuel_.*bridge|goal4_.*node|px4ctrl_ego_single_mission_node|position_cmd_safety_adapter|accumulate_pointcloud_review|roslaunch|gzserver|gzclient|mavros_node|px4 |rosmaster|rosout' | grep -v grep; pkill -f 'run_px4ctrl_ego_single_gate.sh|mosim_px4ctrl_ego_single_mission|px4ctrl_ego_single_mission_node.py|fuel_native_traj_server|fuel_compat_traj_server|exploration_node|factory_l2_same_flight_coverage_supervisor|fuel_trigger_path_adapter.py|fuel_bspline_bridge.py|fuel_position_cmd_compat_bridge.py|accumulate_pointcloud_review.py|goal4_pointcloud_to_world_node.py|goal4_position_cmd_safety_adapter.py|mavros_node|gzserver|gzclient|rosmaster|rosout|/opt/mosim_work/sunray_px4.*/px4' || true" |
        Out-File -FilePath $cleanupLog -Encoding utf8
}
$exitCode = $null
if (-not $timedOut) {
    $rawExit = (Get-Content -LiteralPath $exitCodePath -Raw).Trim()
    if ($rawExit -match '^-?\d+$') {
        $exitCode = [int]$rawExit
    }
}

$metricsPath = Join-Path $ResultDir "EGO_SINGLE_METRICS.json"
if ($timedOut -and $PostCleanupMetricsWaitS -gt 0 -and -not (Test-Path -LiteralPath $metricsPath)) {
    $metricsDeadline = (Get-Date).AddSeconds($PostCleanupMetricsWaitS)
    while (-not (Test-Path -LiteralPath $metricsPath) -and (Get-Date) -lt $metricsDeadline) {
        Start-Sleep -Seconds ([Math]::Max(1, [Math]::Min(5, $PollSeconds)))
    }
}
if (Test-Path -LiteralPath $metricsPath) {
    $settleDeadline = (Get-Date).AddSeconds([Math]::Max(0, $MetricsSettleWaitS))
    $lastLength = -1L
    while ((Get-Date) -lt $settleDeadline) {
        $item = Get-Item -LiteralPath $metricsPath
        if ($item.Length -eq $lastLength -and $item.Length -gt 0) {
            break
        }
        $lastLength = $item.Length
        Start-Sleep -Seconds 1
    }
}
$backendMetricsStatus = $null
$backendMetricsBlockers = @()
if (Test-Path -LiteralPath $metricsPath) {
    try {
        $backendMetrics = Get-Content -LiteralPath $metricsPath -Raw | ConvertFrom-Json
        $backendMetricsStatus = $backendMetrics.status
        if ($null -ne $backendMetrics.blockers) {
            $backendMetricsBlockers = @($backendMetrics.blockers)
        }
    } catch {
        $backendMetricsStatus = "unreadable"
        $backendMetricsBlockers = @("ego_single_metrics_unreadable")
    }
}
$backendEvidencePassed = ($backendMetricsStatus -eq "passed" -and $backendMetricsBlockers.Count -eq 0)

$coverageExitCode = $null
New-Item -ItemType Directory -Force -Path $CoverageDir | Out-Null
try {
    $coverageOutput = & python (Join-Path $ProjectRootWin "Scripts\sunray\build_factory_l2_indoor_coverage_packet.py") `
        --run $ResultDir `
        --output-dir $CoverageDir `
        --grid-resolution-m $CoverageGridResolutionM `
        --sensor-radius-m $CoverageSensorRadiusM `
        --z-min-m $CmdMinZM `
        --z-max-m $CmdMaxZM `
        --min-sensor-coverage-ratio $MinSensorCoverageRatio 2>&1
    $coverageExitCode = $LASTEXITCODE
    $coverageOutput | Out-File -FilePath (Join-Path $ResultDir "coverage_packet_builder_stdout.txt") -Encoding utf8
} catch {
    $coverageExitCode = 1
    $_ | Out-String | Out-File -FilePath (Join-Path $ResultDir "coverage_packet_builder_error.txt") -Encoding utf8
}

$coveragePacketPath = Join-Path $CoverageDir "FACTORY_L2_INDOOR_COVERAGE_PACKET.json"
$coveragePacketStatus = $null
if (Test-Path -LiteralPath $coveragePacketPath) {
    try {
        $coveragePacket = Get-Content -LiteralPath $coveragePacketPath -Raw | ConvertFrom-Json
        $coveragePacketStatus = $coveragePacket.status
    } catch {
        $coveragePacketStatus = "unreadable"
    }
}

$status = if ($timedOut -and -not $backendEvidencePassed) {
    "blocked_runtime_timeout"
} elseif ($exitCode -ne 0) {
    "blocked_backend_exit"
} elseif ($coverageExitCode -ne 0 -or $coveragePacketStatus -ne "passed") {
    "review_required_coverage_below_threshold_or_packet_blocked"
} else {
    "passed_same_flight_coverage_threshold"
}

$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_fuel_same_flight_coverage_probe.v1"
    status = $status
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    result_dir = $ResultDir
    envelope = $EnvelopePath
    backend_exit_code = $exitCode
    timed_out = $timedOut
    cleanup_after_timeout = $cleanupAfterTimeout
    backend_metrics_status = $backendMetricsStatus
    backend_metrics_blockers = $backendMetricsBlockers
    backend_evidence_passed_after_timeout_cleanup = [bool]($timedOut -and $backendEvidencePassed)
    coverage_packet_exit_code = $coverageExitCode
    coverage_packet_status = $coveragePacketStatus
    coverage_packet = $coveragePacketPath
    start_info = $startInfo
    boundary = [pscustomobject]@{
        min_x_m = $minX
        max_x_m = $maxX
        min_y_m = $minY
        max_y_m = $maxY
        center_x_m = $centerX
        center_y_m = $centerY
        fuel_box_min_x_m = $boxMinX
        fuel_box_max_x_m = $boxMaxX
        fuel_box_min_y_m = $boxMinY
        fuel_box_max_y_m = $boxMaxY
        fuel_map_size_x_m = $fuelWindowX
        fuel_map_size_y_m = $fuelWindowY
    }
    parameters = [pscustomobject]@{
        exploration_execute_s = $ExplorationExecuteS
        runtime_budget_s = $runtimeBudget
        outer_wait_budget_s = $outerWaitBudget
        post_cleanup_metrics_wait_s = $PostCleanupMetricsWaitS
        metrics_settle_wait_s = $MetricsSettleWaitS
        review_hold_s = $ReviewHoldS
        fuel_grid_resolution_m = $FuelGridResolutionM
        fuel_frame_offset_z_m = $FuelFrameOffsetZM
        fuel_local_flight_z_m = $FuelLocalFlightZM
        fuel_manager_local_segment_length_m = $FuelManagerLocalSegmentLength
        fuel_planner_max_vel_mps = $FuelPlannerMaxVelMps
        fuel_planner_max_acc_mps2 = $FuelPlannerMaxAccMps2
        fuel_cmd_smooth_max_speed_mps = $FuelCmdSmoothMaxSpeedMps
        fuel_cmd_smooth_max_step_m = $FuelCmdSmoothMaxStepM
        fuel_frontier_candidate_dphi_rad = $FuelFrontierCandidateDphiRad
        fuel_frontier_candidate_rnum = $FuelFrontierCandidateRnum
        fuel_frontier_candidate_rmin = $FuelFrontierCandidateRmin
        fuel_frontier_candidate_rmax = $FuelFrontierCandidateRmax
        fuel_frontier_min_view_finish_fraction = $FuelFrontierMinViewFinishFraction
        fuel_frontier_diagnose_cluster_viewpoints = $FuelFrontierDiagnoseClusterViewpoints.IsPresent
        fuel_frontier_diagnose_cluster_log_limit = $FuelFrontierDiagnoseClusterLogLimit
        fuel_global_expansion_bias_axis = $FuelGlobalExpansionBiasAxis
        fuel_global_expansion_bias_min_gain = $FuelGlobalExpansionBiasMinGain
        fuel_global_expansion_bias_override_refine = $FuelGlobalExpansionBiasOverrideRefine.IsPresent
        fuel_coverage_expansion_enable = $FuelCoverageExpansion.IsPresent
        fuel_coverage_expansion_axis = $FuelCoverageExpansionAxis
        fuel_coverage_expansion_rank_window = $FuelCoverageExpansionRankWindow
        fuel_coverage_expansion_min_gain = $FuelCoverageExpansionMinGain
        fuel_coverage_expansion_dist_weight = $FuelCoverageExpansionDistWeight
        fuel_coverage_expansion_grid_resolution_m = $FuelCoverageExpansionGridResolutionM
        fuel_coverage_expansion_sensor_radius_m = $FuelCoverageExpansionSensorRadiusM
        fuel_coverage_expansion_project_horizon_m = $FuelCoverageExpansionProjectHorizonM
        fuel_coverage_expansion_grid_weight = $FuelCoverageExpansionGridWeight
        fuel_coverage_expansion_span_weight = $FuelCoverageExpansionSpanWeight
        fuel_coverage_expansion_uncovered_target_weight = $FuelCoverageExpansionUncoveredTargetWeight
        fuel_coverage_expansion_score_committed_goal = $FuelCoverageExpansionScoreCommittedGoal.IsPresent
        fuel_coverage_expansion_global_selector = $FuelCoverageExpansionGlobalSelector.IsPresent
        fuel_coverage_expansion_log_candidates = $FuelCoverageExpansionLogCandidates.IsPresent
        target_z_m = $TargetZ
        cmd_min_z_m = $CmdMinZM
        cmd_max_z_m = $CmdMaxZM
        takeoff_timeout_s = $TakeoffTimeoutS
        coverage_grid_resolution_m = $CoverageGridResolutionM
        coverage_sensor_radius_m = $CoverageSensorRadiusM
        min_sensor_coverage_ratio = $MinSensorCoverageRatio
        coverage_supervisor_max_runtime_s = $CoverageSupervisorMaxRuntimeS
        effective_coverage_supervisor_max_runtime_s = $effectiveCoverageSupervisorMaxRuntimeS
        coverage_supervisor_time_basis = $CoverageSupervisorTimeBasis
        exploration_time_basis = $ExplorationTimeBasis
        coverage_supervisor_require_target_z = [bool]$CoverageSupervisorRequireTargetZ
        coverage_supervisor_trigger_z_tolerance_m = $CoverageSupervisorTriggerZToleranceM
        coverage_supervisor_no_growth_timeout_s = $CoverageSupervisorNoGrowthTimeoutS
        coverage_supervisor_min_growth_cells = $CoverageSupervisorMinGrowthCells
        with_rviz = [bool]$WithRviz
        keep_alive = [bool]$KeepAlive
    }
    claim_boundary = @(
        "Same-flight route: one PX4/MAVROS/px4ctrl/FUEL runtime, one UAV, no restart tiling.",
        "The supervisor only republishes FUEL triggers and records odometry coverage; it does not publish position commands.",
        "Coverage acceptance still comes from FACTORY_L2_INDOOR_COVERAGE_PACKET.json and backend metrics."
    )
}
$manifest | ConvertTo-Json -Depth 8 | Out-File -FilePath $ManifestPath -Encoding utf8
$manifest

if ($timedOut -or ($exitCode -ne 0)) {
    if ($backendEvidencePassed -and $coverageExitCode -ne 0) {
        exit 1
    }
    if ($backendEvidencePassed) {
        exit 0
    }
    exit 2
}
if ($coverageExitCode -ne 0) {
    exit 1
}
exit 0
