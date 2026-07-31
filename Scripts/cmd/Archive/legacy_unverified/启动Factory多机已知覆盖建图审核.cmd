@echo off
setlocal

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "WAYPOINTS=%PROJECT_ROOT%\Config\scenarios\factory_l2_swarm_gap_closeout_waypoints.json"
set "RUN_ID=factory_l2_swarm_gap_closeout_review_%RANDOM%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\Scripts\sunray\start_factory_diff_swarm_coverage_probe.ps1" ^
  -RunId "%RUN_ID%" ^
  -UavNum 3 ^
  -WaypointJsonOverride "%WAYPOINTS%" ^
  -PartitionPolicy round_robin ^
  -MaxGoalsPerUav 2 ^
  -PartitionWindowGoalsPerUav 6 ^
  -SpawnStartMode PartitionRoute ^
  -SkipPx4ParamSnapshot ^
  -TargetZ 4 ^
  -CommandMaxZ 4.3 ^
  -PlannerMaxVelMps 1.2 ^
  -PlannerMaxAccMps2 1.2 ^
  -TakeoffTimeoutS 220 ^
  -TakeoffUavStaggerS 8 ^
  -TakeoffRetryRepeats 5 ^
  -TakeoffRetryMax 5 ^
  -TargetChainGoalTimeoutS 180 ^
  -RuntimeTimeoutS 800 ^
  -OuterWaitTimeoutS 900 ^
  -WithRviz ^
  -KeepAlive

exit /b %ERRORLEVEL%
