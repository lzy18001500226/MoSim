#!/usr/bin/env python3
"""Geometry-only filtering for known peer UAV airframe LiDAR returns.

The planner must keep static-scene obstacle returns.  This helper removes a
point only when it falls inside the narrow body envelope of a peer whose odom
timestamp is fresh against the source cloud timestamp.  Missing or stale peer
odom therefore retains the point, which is the conservative behavior for
collision clearance.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PeerOdomSample:
    topic: str
    center_xyz: tuple[float, float, float]
    stamp_s: float


@dataclass(frozen=True)
class PeerFilterCenter:
    topic: str
    center_xyz: tuple[float, float, float]
    stamp_delta_s: float


def select_fresh_peer_filter_centers(
    samples_by_topic: Mapping[str, PeerOdomSample],
    required_topics: Sequence[str],
    cloud_stamp_s: float,
    max_age_s: float,
) -> tuple[list[PeerFilterCenter], list[str]]:
    """Return only peer centers synchronized to this cloud.

    A missing, zero-stamped, or stale peer sample is returned in ``stale`` and
    deliberately does not authorize removing any point around that peer.
    """

    if max_age_s < 0.0:
        raise ValueError("max_age_s must be non-negative")

    centers: list[PeerFilterCenter] = []
    stale_topics: list[str] = []
    for topic in required_topics:
        sample = samples_by_topic.get(topic)
        if sample is None or cloud_stamp_s <= 0.0 or sample.stamp_s <= 0.0:
            stale_topics.append(topic)
            continue
        stamp_delta_s = abs(cloud_stamp_s - sample.stamp_s)
        if stamp_delta_s > max_age_s:
            stale_topics.append(topic)
            continue
        centers.append(
            PeerFilterCenter(
                topic=topic,
                center_xyz=sample.center_xyz,
                stamp_delta_s=stamp_delta_s,
            )
        )
    return centers, stale_topics


def match_peer_airframe(
    point_xyz: tuple[float, float, float],
    centers: Sequence[PeerFilterCenter],
    radius_xy_m: float,
    z_min_m: float,
    z_max_m: float,
) -> str | None:
    """Return the matching peer topic when ``point_xyz`` is inside its body box."""

    if radius_xy_m <= 0.0 or z_min_m > z_max_m:
        return None
    px, py, pz = point_xyz
    radius_sq = radius_xy_m * radius_xy_m
    for center in centers:
        cx, cy, cz = center.center_xyz
        dz = pz - cz
        if dz < z_min_m or dz > z_max_m:
            continue
        dx = px - cx
        dy = py - cy
        if dx * dx + dy * dy <= radius_sq:
            return center.topic
    return None
