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


def inter_uav_braking_guard(
    position_a: Iterable[float],
    velocity_a: Iterable[float],
    position_b: Iterable[float],
    velocity_b: Iterable[float],
    min_distance_m: float,
    deceleration_mps2: float,
    margin_m: float,
    min_predictive_closing_speed_mps: float = 0.05,
) -> dict[str, float | bool]:
    """Predict whether a closing UAV pair needs an immediate hold."""
    vectors = [
        tuple(float(value) for value in values)
        for values in (position_a, velocity_a, position_b, velocity_b)
    ]
    if not all(len(values) == 3 for values in vectors):
        raise ValueError("pair-guard vectors must contain exactly three values")
    if not all(math.isfinite(value) for values in vectors for value in values):
        raise ValueError("pair-guard vectors must contain finite values")
    if (
        min_distance_m < 0.0
        or deceleration_mps2 <= 0.0
        or margin_m < 0.0
        or min_predictive_closing_speed_mps < 0.0
    ):
        raise ValueError("pair-guard distances must be non-negative and deceleration positive")

    pa, va, pb, vb = vectors
    relative_position = tuple(pb[i] - pa[i] for i in range(3))
    relative_velocity = tuple(vb[i] - va[i] for i in range(3))
    distance_m = math.sqrt(sum(value * value for value in relative_position))
    if distance_m <= 1e-9:
        closing_speed_mps = math.sqrt(sum(value * value for value in relative_velocity))
    else:
        distance_rate_mps = sum(
            relative_position[i] * relative_velocity[i] for i in range(3)
        ) / distance_m
        closing_speed_mps = max(0.0, -distance_rate_mps)
    braking_distance_m = closing_speed_mps * closing_speed_mps / (2.0 * deceleration_mps2)
    trigger_distance_m = min_distance_m + margin_m + braking_distance_m
    # The buffer is predictive: it applies only for a meaningful closing rate.
    # This prevents normal formation-spacing odometry noise from turning the
    # buffer into a false emergency hold, while hard-distance violations remain
    # unconditional.
    hard_distance_violation = distance_m <= min_distance_m
    predicted_braking_violation = (
        closing_speed_mps >= min_predictive_closing_speed_mps
        and distance_m <= trigger_distance_m
    )
    return {
        "triggered": hard_distance_violation or predicted_braking_violation,
        "distance_m": distance_m,
        "closing_speed_mps": closing_speed_mps,
        "braking_distance_m": braking_distance_m,
        "trigger_distance_m": trigger_distance_m,
        "min_predictive_closing_speed_mps": min_predictive_closing_speed_mps,
        "hard_distance_violation": hard_distance_violation,
        "predicted_braking_violation": predicted_braking_violation,
    }


def body_to_world_vector(
    quaternion_xyzw: Iterable[float], body_vector: Iterable[float]
) -> tuple[float, float, float]:
    """Rotate a body-frame vector into the pose's world frame."""
    quaternion = tuple(float(value) for value in quaternion_xyzw)
    vector = tuple(float(value) for value in body_vector)
    if len(quaternion) != 4 or len(vector) != 3:
        raise ValueError("quaternion must be xyzw and vector must contain three values")
    if not all(math.isfinite(value) for value in (*quaternion, *vector)):
        raise ValueError("quaternion and vector must be finite")
    x, y, z, w = quaternion
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 1e-9:
        raise ValueError("quaternion norm must be positive")
    x, y, z, w = (x / norm, y / norm, z / norm, w / norm)
    vx, vy, vz = vector
    return (
        (1.0 - 2.0 * (y * y + z * z)) * vx + 2.0 * (x * y - z * w) * vy + 2.0 * (x * z + y * w) * vz,
        2.0 * (x * y + z * w) * vx + (1.0 - 2.0 * (x * x + z * z)) * vy + 2.0 * (y * z - x * w) * vz,
        2.0 * (x * z - y * w) * vx + 2.0 * (y * z + x * w) * vy + (1.0 - 2.0 * (x * x + y * y)) * vz,
    )


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
    velocity_reference_limit = max_velocity_mps
    if max_velocity_mps > 0.0 and max_acceleration_mps2 > 0.0 and max_jerk_mps3 > 0.0:
        # Begin braking before the hard speed boundary. The full a^2/j budget
        # covers both the outward-acceleration ramp-down and direction changes
        # in 3-D. This avoids the discontinuous final velocity clip that would
        # otherwise violate the jerk limit.
        braking_margin = max_acceleration_mps2 * max_acceleration_mps2 / max_jerk_mps3
        velocity_reference_limit = max(0.0, max_velocity_mps - braking_margin)
    desired_velocity = _limit_norm(desired_velocity, velocity_reference_limit)
    acceleration = tuple((desired_velocity[i] - v0[i]) / dt for i in range(3))
    original_acceleration = acceleration

    # Project acceleration and jerk without a terminal speed clip. Speed is
    # controlled by the braking-aware reference above; clipping the integrated
    # velocity here would create an acceleration step and defeat the jerk gate.
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


def enforce_position_z_bounds(
    position: Iterable[float],
    velocity: Iterable[float],
    acceleration: Iterable[float],
    jerk: Iterable[float],
    min_z: float,
    max_z: float,
) -> dict[str, tuple[float, float, float] | bool]:
    """Apply the final hard altitude gate after kinematic integration."""
    vectors = [
        tuple(float(value) for value in values)
        for values in (position, velocity, acceleration, jerk)
    ]
    if not all(len(values) == 3 for values in vectors):
        raise ValueError("kinematic vectors must contain exactly three values")
    if min_z > max_z:
        raise ValueError("min_z must not exceed max_z")

    bounded_position, bounded_velocity, bounded_acceleration, bounded_jerk = vectors
    corrected = False
    if bounded_position[2] < min_z:
        bounded_position = (bounded_position[0], bounded_position[1], min_z)
        corrected = True
    elif bounded_position[2] > max_z:
        bounded_position = (bounded_position[0], bounded_position[1], max_z)
        corrected = True

    if corrected:
        bounded_velocity = (bounded_velocity[0], bounded_velocity[1], 0.0)
        bounded_acceleration = (bounded_acceleration[0], bounded_acceleration[1], 0.0)
        bounded_jerk = (bounded_jerk[0], bounded_jerk[1], 0.0)

    return {
        "position": bounded_position,
        "velocity": bounded_velocity,
        "acceleration": bounded_acceleration,
        "jerk": bounded_jerk,
        "corrected": corrected,
    }
