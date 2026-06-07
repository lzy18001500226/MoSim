# B1 Runtime-Disabled Launch Audit 015

Request: `RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015`

Status: completed static audit only. No planner runtime was launched, no recorder was run, no `/position_cmd` was published, and no `/planning/bspline` runtime evidence is claimed.

## Inspected Files

- `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANMANAGE-LINK-PREFLIGHT-20260606-014.json`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/src/ego_planner_node.cpp`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/src/ego_replan_fsm.cpp`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/src/planner_manager.cpp`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/src/traj_server_ros2_node.cpp`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_env/src/grid_map.cpp`
- `Results/tmp/ego_planner_ros2_port_ws/src/bspline_opt/src/bspline_optimizer.cpp`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/launch/advanced_param.xml`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/launch/simple_run.launch`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/launch/run_in_sim.launch`
- `Docs/Workflows/ros2_runtime_setup.md`

Supporting scans:

- `static_parameter_topic_surface_scan.txt`
- `inspected_source_files.txt`
- `launch_and_config_file_inventory.json`
- `preflight_artifact_inventory.json`

## Static Topic And Remap Contract

Later runtime gate candidate, if PMO approves a real runtime-disabled smoke before active planning:

```text
/odom_world                    nav_msgs/msg/Odometry        remap to /Odometry
/grid_map/odom                 nav_msgs/msg/Odometry        remap to /Odometry
/grid_map/cloud                sensor_msgs/msg/PointCloud2  remap to /cloud_registered
```

Planner/FSM publisher surfaces present in compiled code but not exercised in this task:

```text
/planning/bspline              ego_planner_msgs/msg/Bspline
/planning/data_display         ego_planner_msgs/msg/DataDisp
```

GridMap visualization publishers present in compiled code:

```text
/grid_map/occupancy
/grid_map/occupancy_inflate
/grid_map/unknown
```

The existing `traj_server_ros2_node` stays disabled for this audit. If used later, it must keep `publish_enabled:=false` until PMO explicitly approves a command-output gate. It must not publish `/position_cmd` in this task.

## Static Parameter Contract

The ROS2 port uses dotted parameter names:

```text
fsm.flight_type
fsm.thresh_replan
fsm.thresh_no_replan
fsm.planning_horizon
fsm.planning_horizen_time
fsm.emergency_time_
fsm.waypoint_num
fsm.waypoint{N}_x/y/z

manager.max_vel
manager.max_acc
manager.max_jerk
manager.control_points_distance
manager.feasibility_tolerance
manager.planning_horizon

grid_map.resolution
grid_map.map_size_x/y/z
grid_map.local_update_range_x/y/z
grid_map.obstacles_inflation
grid_map.local_map_margin
grid_map.ground_height
grid_map.cx/cy/fx/fy
grid_map.use_depth_filter
grid_map.depth_filter_tolerance
grid_map.depth_filter_maxdist
grid_map.depth_filter_mindist
grid_map.depth_filter_margin
grid_map.k_depth_scaling_factor
grid_map.skip_pixel
grid_map.p_hit/p_miss/p_min/p_max/p_occ
grid_map.min_ray_length
grid_map.max_ray_length
grid_map.virtual_ceil_height
grid_map.visualization_truncate_height
grid_map.show_occ_time
grid_map.pose_type
grid_map.frame_id

optimization.lambda_smooth
optimization.lambda_collision
optimization.lambda_feasibility
optimization.lambda_fitness
optimization.dist0
optimization.max_vel
optimization.max_acc
optimization.order
```

The inspected legacy EGO XML launch files use ROS1 slash-style parameter names such as `fsm/flight_type` and `grid_map/resolution`. They are not directly usable as a ROS2 launch/parameter source without translation to dotted names.

## Runtime-Disabled Command Text

No command below was executed in this task. This is the candidate command text for a later PMO-approved static/runtime-disabled smoke:

```bash
set +u
source /opt/ros/humble/setup.bash
source /mnt/c/Users/HP/Desktop/MoSim/install/setup.bash 2>/dev/null || true
source /mnt/c/Users/HP/Desktop/MoSim/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash
set -u
export ROS_LOG_DIR=/mnt/c/Users/HP/Desktop/MoSim/Results/ros2_runtime/b1_runtime_disabled_launch_audit_20260606_015/ros_logs
timeout 10s ros2 run ego_planner ego_planner_node_preflight --ros-args \
  -r /odom_world:=/Odometry \
  -r /grid_map/odom:=/Odometry \
  -r /grid_map/cloud:=/cloud_registered \
  -p fsm.flight_type:=-1 \
  -p fsm.waypoint_num:=0 \
  -p manager.max_vel:=2.0 \
  -p manager.max_acc:=3.0 \
  -p manager.max_jerk:=4.0 \
  -p manager.control_points_distance:=0.4 \
  -p manager.feasibility_tolerance:=0.05 \
  -p manager.planning_horizon:=7.5 \
  -p optimization.lambda_smooth:=1.0 \
  -p optimization.lambda_collision:=0.5 \
  -p optimization.lambda_feasibility:=0.1 \
  -p optimization.lambda_fitness:=1.0 \
  -p optimization.dist0:=0.5 \
  -p optimization.max_vel:=2.0 \
  -p optimization.max_acc:=3.0 \
  -p grid_map.resolution:=0.1 \
  -p grid_map.map_size_x:=40.0 \
  -p grid_map.map_size_y:=40.0 \
  -p grid_map.map_size_z:=3.0 \
  -p grid_map.local_update_range_x:=5.5 \
  -p grid_map.local_update_range_y:=5.5 \
  -p grid_map.local_update_range_z:=4.5 \
  -p grid_map.obstacles_inflation:=0.099 \
  -p grid_map.local_map_margin:=30 \
  -p grid_map.ground_height:=-0.01 \
  -p grid_map.cx:=321.04638671875 \
  -p grid_map.cy:=243.44969177246094 \
  -p grid_map.fx:=387.229248046875 \
  -p grid_map.fy:=387.229248046875 \
  -p grid_map.use_depth_filter:=true \
  -p grid_map.depth_filter_tolerance:=0.15 \
  -p grid_map.depth_filter_maxdist:=5.0 \
  -p grid_map.depth_filter_mindist:=0.2 \
  -p grid_map.depth_filter_margin:=1 \
  -p grid_map.k_depth_scaling_factor:=1000.0 \
  -p grid_map.skip_pixel:=2 \
  -p grid_map.p_hit:=0.65 \
  -p grid_map.p_miss:=0.35 \
  -p grid_map.p_min:=0.12 \
  -p grid_map.p_max:=0.90 \
  -p grid_map.p_occ:=0.80 \
  -p grid_map.min_ray_length:=0.1 \
  -p grid_map.max_ray_length:=4.5 \
  -p grid_map.virtual_ceil_height:=2.5 \
  -p grid_map.visualization_truncate_height:=2.4 \
  -p grid_map.show_occ_time:=false \
  -p grid_map.pose_type:=2 \
  -p grid_map.frame_id:=world
```

The safety reason for `fsm.flight_type:=-1`: it avoids manual and preset target planning branches. This is still not a proof of planner runtime quality and should be used only as a bounded process/parameter/remap smoke after PMO approval.

## Unresolved Blockers And Risks

- No ROS2 `.launch.py` exists for this ported preflight surface.
- Legacy launch XML uses ROS1 node/param/remap syntax and cannot be accepted as a ROS2 launch artifact without conversion.
- There is no explicit `runtime_disabled` guard in `ego_planner_node_preflight`; if a later run uses manual or preset target modes and valid inputs, it can publish `/planning/bspline`.
- A later real runtime gate still needs current real `/Odometry` plus `/cloud_registered` or equivalent local sensed input, not fake map/cloud and not UE global truth.
- Recorder remains forbidden until PMO approves the next runtime gate and the planner produces real sustained outputs.

## Next PMO Approval Gate

Approve or reject a narrow follow-up task to add a ROS2 runtime-disabled launch/config artifact in the isolated workspace, with an explicit non-planning guard, before any real runtime or recorder gate. The next gate should still be `runtime_disabled_smoke_only`, not `planner` or `closed_loop`.
