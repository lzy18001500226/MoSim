# Factory Three-UAV Self-Service Flow

This workflow is the reproducible, no-QGC/no-UE entry for the current fixed
three-UAV Swarm-Formation obstacle-crossing route. It does not establish
autonomous exploration, online multi-UAV avoidance, FAST-LIO localization, or
support for four to nine vehicles.

## Preconditions

- Work from `C:\Users\HP\Desktop\MoSim`.
- Do not start a second Sunray/Gazebo/PX4 runtime while one is active.
- Keep the backend terminal visible. It is the first error surface and owns the
  Gazebo/PX4/MAVROS/planner lifecycle.

## Operator Sequence

1. Double-click `cmd/01_预检Factory三机环境.cmd`.
   - It is read-only: it verifies the ROS1/Sunray environment, reports the
     current WSL resource state, and detects an existing three-UAV runner.
   - When it reports `busy`, do not start another backend. Run
     `cmd/06_停止Factory三机编队.cmd`, wait for the runner to exit, then repeat the
     preflight.
2. Double-click `cmd/03_启动Factory三机固定编队.cmd`.
   - This opens a visible terminal and starts Gazebo, three PX4/MAVROS pairs,
     three px4ctrl instances, the fixed three-UAV Swarm-Formation planner, and
     the known-target obstacle-crossing mission.
   - The launcher writes a result directory below
     `Results\sunray_ros1\factory_l2_swarm_formation_manual_*` and records
     the active run pointer.
   - Leave this terminal open. The default `KeepAlive` mode keeps the runtime
     available for review after the mission ends.
3. Run `cmd/05_检查Factory三机状态.cmd` until it reports `passed`.
   - A pass requires all three MAVROS links to be connected, three live
     `/uavN/livox_world` clouds, and three `occupancy_inflate` voxel clouds.
   - The evidence packet is `SWARM_RUNTIME_STATUS.json` inside the active run
     directory. A blocked result is a startup/diagnostic result, not a flight
     or formation failure claim.
4. Double-click `cmd/04_打开Factory三机RViz审核.cmd`.
   - It attaches only to the existing backend. It intentionally does not start
     QGC or UE.
   - The accepted reference run must contain three passed gates: backend
     mission, formation/separation, and post-flight obstacle-clearance. The
     clearance gate checks executed Gazebo trajectories only after the flight;
     it never supplies scene truth to the planner.
   - It opens two RViz windows: one for the three accumulated MID360 clouds,
     and one for the three inflated occupancy voxel maps plus body axes.
   - The RViz configuration subscribes directly to the live three-UAV topics,
     not to the historical Diff-Planner relay topics.
   - Run `cmd/05_检查Factory三机状态.cmd` once more if a text check is wanted: its
     `review_*accumulated_cloud` rows become nonempty after this attachment.
5. Use the backend terminal and the result directory for mission logs. Use
   RViz for map/point-cloud/trajectory-frame review. Gazebo/PX4/MAVROS logs
   remain the authority for flight success.
6. End with `cmd/06_停止Factory三机编队.cmd`.
   - It sends `SIGINT` only to the active `run_px4ctrl_ego_swarm_gate.sh`
     runner, waits briefly, then sends SIGTERM only to that same runner if it
     is still present. It closes only the RViz helper nodes/configurations
     created by this review route.
   - The runner then executes its owned-process cleanup. Do not launch a new
     run until this script reports that the runner exited.
   - For a mission that had already passed all backend, formation,
     obstacle-clearance and planner-log gates, the active pointer finishes as
     `finished_after_operator_stop` and preserves both the raw interrupted
     gate exit code and the final successful lifecycle exit code. Stopping
     before those gates pass remains `stopped_or_failed`.

## Failure Triage

| Symptom | First action |
|---|---|
| Status check says a point cloud or grid is empty | Inspect the named topic in `SWARM_RUNTIME_STATUS.json`, then the backend terminal and its `ros_logs/`; do not tune controller gains. |
| RViz opens but map is blank | Run the status check. If it passes, inspect RViz fixed frame (`world`) and enabled display names before changing sensor or planner settings. |
| Backend terminal reports MAVROS/PX4/Gazebo startup failure | Preserve the terminal output and the run directory. Stop the run, then repair the named runtime dependency before retrying. |
| Stop script cannot find the runner | Do not start another swarm run. Check the backend terminal and `Results\sunray_ros1`; use the broad `cmd/停止所有仿真.cmd` only when the user intends to stop every managed simulation. |

## Evidence Boundary

The review clouds are generated from live Gazebo/Sunray MID360 topics and
Gazebo truth pose for display. They are not FAST-LIO output. The fixed
three-UAV route is a known-target formation test. Scaling beyond three UAVs
requires a separate generated launch/profile/port/start-pose design and
incremental runtime gates.
