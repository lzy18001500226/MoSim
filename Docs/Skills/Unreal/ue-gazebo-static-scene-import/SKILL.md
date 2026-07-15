---
name: ue-gazebo-static-scene-import
description: Use when importing an accepted Unreal Engine scene or map into Gazebo Classic as a static physical scene base, preparing Factory L2-style Gazebo review assets, validating SDF/model outputs, or adding a reversible Sunray/Gazebo scene profile. This skill is not for UE runtime display, ROS/PX4 runtime acceptance, SLAM, planner, or controller success claims.
---

# UE Gazebo Static Scene Import

Use this skill only for UE-derived static scene-base work.

## Load First

Read the workflow before acting:

```text
Docs/Workflows/ue_to_gazebo_static_scene_import.md
```

For Factory-specific design and current accepted evidence, also read:

```text
Docs/Design/架构/04_展示与实验平台/Factory地图导入与全局态势视图.md
```

For live ROS1/Sunray runtime checks after static scene acceptance, switch to:

```text
Docs/Workflows/sunray_ros1_current_runtime_lane.md
Docs/Workflows/sunray_ros1_execution_checklist.md
```

## Boundary

The maximum claim from this skill is static Gazebo scene-base readiness or user
acceptance. Do not claim ROS/PX4/MAVROS/RViz, SLAM, planner, controller, UE
Data Bridge, or closed-loop success from static import evidence.

## Required Evidence

Produce or update:

```text
Results/unreal_scene_mapping/<scene>_l2_static_import/gazebo_review/MANIFEST.json
Results/unreal_scene_mapping/<scene>_l2_static_import/gazebo_review/VERIFICATION.json
Results/unreal_scene_mapping/<scene>_l2_static_import/gazebo_review/SUMMARY.md
```

After user acceptance, add a scene profile under:

```text
Config/gazebo/scene_profiles/
```

Optional Sunray launch entries belong under `Scripts/sunray/` and must be
reversible; never replace accepted baseline launch files.
