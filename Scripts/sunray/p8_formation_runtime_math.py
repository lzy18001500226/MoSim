#!/usr/bin/env python3
"""Pure frame and retry helpers for the P8 generated formation runtime."""

from __future__ import annotations

import math


def odom_to_common_xy(
    start_xy: tuple[float, float],
    home_odom_xy: tuple[float, float],
    odom_xy: tuple[float, float],
) -> tuple[float, float]:
    return (
        start_xy[0] + odom_xy[0] - home_odom_xy[0],
        start_xy[1] + odom_xy[1] - home_odom_xy[1],
    )


def common_to_odom_xy(
    start_xy: tuple[float, float],
    home_odom_xy: tuple[float, float],
    common_xy: tuple[float, float],
) -> tuple[float, float]:
    return (
        home_odom_xy[0] + common_xy[0] - start_xy[0],
        home_odom_xy[1] + common_xy[1] - start_xy[1],
    )


def should_retry_takeoff(
    now_s: float,
    last_request_s: float,
    request_count: int,
    maximum_requests: int,
    retry_interval_s: float,
    all_armed: bool,
) -> bool:
    return (
        not all_armed
        and request_count < maximum_requests
        and now_s - last_request_s >= retry_interval_s
    )


def next_takeoff_uid(armed_by_uid: dict[int, bool]) -> int | None:
    return next((uid for uid in sorted(armed_by_uid) if not armed_by_uid[uid]), None)


def rate_limit_vector(
    current: tuple[float, ...],
    target: tuple[float, ...],
    maximum_step: float,
) -> tuple[float, ...]:
    if len(current) != len(target):
        raise ValueError("current and target dimensions must match")
    delta = tuple(target_value - current_value for current_value, target_value in zip(current, target))
    distance = math.sqrt(sum(value * value for value in delta))
    if distance <= maximum_step or distance == 0.0:
        return target
    scale = maximum_step / distance
    return tuple(current_value + scale * value for current_value, value in zip(current, delta))


def point_at_distance(
    anchor: tuple[float, float],
    direction_point: tuple[float, float],
    distance: float,
) -> tuple[float, float]:
    dx = direction_point[0] - anchor[0]
    dy = direction_point[1] - anchor[1]
    norm = math.hypot(dx, dy)
    if norm == 0.0:
        raise ValueError("direction point must differ from anchor")
    return anchor[0] + distance * dx / norm, anchor[1] + distance * dy / norm
