"""Pure geometry for the RViz Diff-Swarm manual-goal contract."""

from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple


# Keep this module importable with Ubuntu 20.04's Python 3.8 runtime.
Vector3 = Tuple[float, float, float]


def default_formation_offsets(uav_num: int) -> tuple[Vector3, ...]:
    """Return the reviewed cross-track offsets around one clicked center."""

    if uav_num == 2:
        return ((0.0, -1.0, 0.0), (0.0, 1.0, 0.0))
    if uav_num == 3:
        return ((0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0))
    raise ValueError("uav_num must be 2 or 3")


def parse_vector_list(value: str, *, expected_count: int, field: str) -> tuple[Vector3, ...]:
    """Parse ``x,y,z;x,y,z`` while rejecting malformed or non-finite input."""

    parts = [part.strip() for part in value.split(";") if part.strip()]
    if len(parts) != expected_count:
        raise ValueError(f"{field} must contain {expected_count} vectors")
    vectors: list[Vector3] = []
    for index, part in enumerate(parts, start=1):
        values = [item.strip() for item in part.split(",")]
        if len(values) != 3:
            raise ValueError(f"{field}[{index}] must contain x,y,z")
        try:
            vector = tuple(float(item) for item in values)
        except ValueError as exc:
            raise ValueError(f"{field}[{index}] must be numeric") from exc
        if not all(math.isfinite(item) for item in vector):
            raise ValueError(f"{field}[{index}] must be finite")
        vectors.append(vector)  # type: ignore[arg-type]
    return tuple(vectors)


def _finite_vector(value: Sequence[float], field: str) -> Vector3:
    if len(value) != 3:
        raise ValueError(f"{field} must contain three values")
    vector = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in vector):
        raise ValueError(f"{field} must be finite")
    return vector  # type: ignore[return-value]


def route_center_goal(
    center_xyz: Sequence[float],
    formation_offsets: Iterable[Sequence[float]],
    *,
    world_to_local_offsets: Iterable[Sequence[float]] | None = None,
) -> tuple[Vector3, ...]:
    """Expand one world-frame center into per-UAV planner-frame targets.

    ``world_to_local_offsets`` is the frozen spawn offset for each UAV. When it
    is supplied, the planner target is ``center + formation - spawn``. This is
    the explicit common-world -> MAVROS-local conversion used by the Diff
    frame bridge; it must not be inferred from a topic name.
    """

    center = _finite_vector(center_xyz, "center_xyz")
    formation = tuple(_finite_vector(item, "formation_offsets") for item in formation_offsets)
    if not formation:
        raise ValueError("formation_offsets must not be empty")
    local_offsets = (
        tuple((0.0, 0.0, 0.0) for _ in formation)
        if world_to_local_offsets is None
        else tuple(_finite_vector(item, "world_to_local_offsets") for item in world_to_local_offsets)
    )
    if len(local_offsets) != len(formation):
        raise ValueError("world_to_local_offsets count must match formation_offsets")
    return tuple(
        tuple(center[axis] + formation[index][axis] - local_offsets[index][axis] for axis in range(3))
        for index in range(len(formation))
    )


def minimum_pairwise_distance(points: Iterable[Sequence[float]]) -> float:
    vectors = [_finite_vector(point, "points") for point in points]
    if len(vectors) < 2:
        return math.inf
    return min(
        math.dist(vectors[first], vectors[second])
        for first in range(len(vectors))
        for second in range(first + 1, len(vectors))
    )
