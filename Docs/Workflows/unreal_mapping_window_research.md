# UE / RViz Mapping Window Boundary

> Short current entry for mapping-window evidence. The detailed historical
> research lives in `Docs/Cache/legacy_workflows/unreal_renderer_full_20260624.md`.

Status: current boundary pointer, 2026-06-25 CST.

## Current Rule

Use this file only when a task asks whether UE, RViz, RViz2, browser HTML, or a
native preview window can count as point-cloud/map evidence.

The current MoSim P0 route is ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl with RViz
as the active point-cloud, trajectory, map, and frame review surface. UE is a
display/review enhancement layer and scene/sensor oracle; it is not the current
control-loop, localization, planner, or point-cloud evidence authority.

## Accepted Surfaces

| Surface | Accepted Scope |
|---|---|
| RViz / RViz2 or equivalent native robotics viewer | active point-cloud, TF, map, odometry, trajectory, and FAST-LIO-style review |
| Unreal / `MoSimSceneLibrary` | rendered scene, vehicle visual, camera/sensor oracle, review screenshots/video |
| HTML report preview | offline report artifact only |
| `Scripts/UE5/open_native_pointcloud_preview.*` | native preview fallback/dry-run aid; not FAST-LIO/RViz runtime evidence |

## Hard Boundary

- Browser HTML is not an accepted active point-cloud/map review surface.
- Global UE collision/occupancy truth is a validation oracle only and must not
  be fed to the planner as known global runtime input.
- Current runtime claims still need workflow-declared RViz/topic/log/metric
  evidence from `Docs/Workflows/sunray_ros1_current_runtime_lane.md` and
  `Docs/Workflows/sunray_ros1_execution_checklist.md`.
- UE screenshots or native-preview dry runs can support review, but cannot
  prove controller, localization, planner, FAST-LIO, or closed-loop success.

## Related Files

```text
Docs/Workflows/unreal_renderer.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
Docs/Workflows/sunray_ros1_execution_checklist.md
Scripts/UE5/open_native_pointcloud_preview.ps1
Scripts/UE5/open_native_pointcloud_preview.sh
```
