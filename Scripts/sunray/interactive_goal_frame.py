"""Frame-safe coordinate selection for Goal4 interactive target evaluation."""

from __future__ import annotations

import math


def normalize_frame_id(frame_id: object) -> str:
    """Normalize ROS frame spelling without treating unrelated frames as aliases."""
    return str(frame_id or "").strip().lstrip("/")


def resolve_target_for_state_frame(
    target_xyz: tuple[float, float, float],
    goal_frame_id: object,
    state_frame_id: object,
    *,
    world_frame_id: object,
    map_frame_id: object,
    world_to_map_offset_xyz: tuple[float, float, float],
    allow_world_map_transform: bool,
) -> tuple[tuple[float, float, float], str] | None:
    """Express an interactive target in the frame of one state sample.

    The map/world conversion is available only when the caller has declared
    the same offset contract used by the planner boundary. This avoids
    silently treating arbitrary ROS frame names as identical.
    """
    goal_frame = normalize_frame_id(goal_frame_id)
    state_frame = normalize_frame_id(state_frame_id)
    if not goal_frame or not state_frame:
        return None

    target = tuple(float(value) for value in target_xyz)
    offset = tuple(float(value) for value in world_to_map_offset_xyz)
    if not all(math.isfinite(value) for value in (*target, *offset)):
        return None
    if goal_frame == state_frame:
        return target, "direct"
    if not allow_world_map_transform:
        return None

    world_frame = normalize_frame_id(world_frame_id)
    map_frame = normalize_frame_id(map_frame_id)
    if not world_frame or not map_frame or world_frame == map_frame:
        return None
    if goal_frame == world_frame and state_frame == map_frame:
        return tuple(target[index] - offset[index] for index in range(3)), "world_to_map_offset"
    if goal_frame == map_frame and state_frame == world_frame:
        return tuple(target[index] + offset[index] for index in range(3)), "map_to_world_offset"
    return None


def interactive_completion_goal_count(
    waypoint_plan_size: int | None,
    require_waypoint_plan_size: bool,
    auto_pass_goal_count: int,
    publish_initial_goal: bool,
) -> int | None:
    """Return a terminal goal count without ending a manual session at its seed goal."""
    if waypoint_plan_size is not None:
        return waypoint_plan_size
    if require_waypoint_plan_size or publish_initial_goal:
        return None
    return auto_pass_goal_count
