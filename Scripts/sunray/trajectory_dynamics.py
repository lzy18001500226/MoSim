#!/usr/bin/env python3
"""Pure kinematic constraints shared by ROS trajectory adapters and tests."""

from __future__ import annotations

import math
from typing import Iterable


def _limit_norm(values: tuple[float, ...], maximum: float) -> tuple[float, ...]:
    if maximum <= 0.0:
        return values
    norm = math.sqrt(sum(value * value for value in values))
    if norm <= maximum or norm <= 1e-12:
        return values
    scale = maximum / norm
    return tuple(value * scale for value in values)


def constrain_kinematic_step(
    previous_position: Iterable[float],
    previous_velocity: Iterable[float],
    previous_acceleration: Iterable[float],
    target_position: Iterable[float],
    dt: float,
    max_velocity_mps: float = 0.0,
    max_acceleration_mps2: float = 0.0,
    max_lateral_acceleration_mps2: float = 0.0,
    max_jerk_mps3: float = 0.0,
) -> dict[str, tuple[float, float, float] | bool]:
    """Return a position-consistent velocity/acceleration/jerk command.

    A non-positive limit disables that individual constraint. Position is
    integrated from the constrained velocity so the controller never receives
    mutually inconsistent position and derivative references.
    """
    dt = max(float(dt), 1e-4)
    p0 = tuple(float(value) for value in previous_position)
    v0 = tuple(float(value) for value in previous_velocity)
    a0 = tuple(float(value) for value in previous_acceleration)
    target = tuple(float(value) for value in target_position)
    if not all(len(values) == 3 for values in (p0, v0, a0, target)):
        raise ValueError("kinematic vectors must contain exactly three values")
    if not all(math.isfinite(value) for values in (p0, v0, a0, target) for value in values):
        raise ValueError("kinematic vectors must contain finite values")

    desired_velocity = tuple((target[i] - p0[i]) / dt for i in range(3))
    acceleration = tuple((desired_velocity[i] - v0[i]) / dt for i in range(3))
    original_acceleration = acceleration

    # The acceleration, jerk and next-velocity limits are convex sets. A few
    # alternating projections are sufficient for this 3-D command filter and
    # avoid relaxing one bound while enforcing another.
    for _ in range(8):
        if max_lateral_acceleration_mps2 > 0.0:
            lateral = _limit_norm(acceleration[:2], max_lateral_acceleration_mps2)
            acceleration = (lateral[0], lateral[1], acceleration[2])
        acceleration = _limit_norm(acceleration, max_acceleration_mps2)

        jerk = tuple((acceleration[i] - a0[i]) / dt for i in range(3))
        jerk = _limit_norm(jerk, max_jerk_mps3)
        if max_jerk_mps3 > 0.0:
            acceleration = tuple(a0[i] + jerk[i] * dt for i in range(3))

        velocity = tuple(v0[i] + acceleration[i] * dt for i in range(3))
        limited_velocity = _limit_norm(velocity, max_velocity_mps)
        if limited_velocity != velocity:
            acceleration = tuple((limited_velocity[i] - v0[i]) / dt for i in range(3))

    velocity = tuple(v0[i] + acceleration[i] * dt for i in range(3))
    velocity = _limit_norm(velocity, max_velocity_mps)
    acceleration = tuple((velocity[i] - v0[i]) / dt for i in range(3))
    jerk = tuple((acceleration[i] - a0[i]) / dt for i in range(3))
    position = tuple(p0[i] + velocity[i] * dt for i in range(3))
    limited = any(abs(acceleration[i] - original_acceleration[i]) > 1e-9 for i in range(3))
    return {
        "position": position,
        "velocity": velocity,
        "acceleration": acceleration,
        "jerk": jerk,
        "limited": limited,
    }
