"""Spherical coordinate helpers shared by the Factory L2 display gates.

The QGC overlay uses QGeoCoordinate::atDistanceAndAzimuth twice: first on
the world Y axis and then on the world X axis.  These helpers implement the
same spherical great-circle construction without adding a Python dependency.
They are intentionally limited to the local map-sized coordinate contract.
"""

from __future__ import annotations

import math
from typing import Mapping, Tuple


EARTH_RADIUS_M = 6_371_000.0


def _finite(value: object, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}_not_numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name}_not_finite")
    return number


def _anchor(anchor: Mapping[str, object]) -> Tuple[float, float]:
    return (
        _finite(anchor["latitude_deg"], "anchor_latitude_deg"),
        _finite(anchor["longitude_deg"], "anchor_longitude_deg"),
    )


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_longitude_delta_deg(delta_deg: float) -> float:
    """Return a longitude delta in the conventional [-180, 180] range."""

    delta = float(delta_deg)
    while delta > 180.0:
        delta -= 360.0
    while delta < -180.0:
        delta += 360.0
    return delta


def _direct_spherical(
    latitude_deg: float,
    longitude_deg: float,
    distance_m: float,
    azimuth_deg: float,
) -> Tuple[float, float]:
    """Match QGeoCoordinate::atDistanceAndAzimuth for a spherical Earth."""

    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)
    distance = _finite(distance_m, "distance_m")
    if distance < 0.0:
        raise ValueError("distance_m_negative")
    azimuth = math.radians(azimuth_deg)
    angular_distance = distance / EARTH_RADIUS_M

    sin_lat = math.sin(latitude)
    cos_lat = math.cos(latitude)
    sin_distance = math.sin(angular_distance)
    cos_distance = math.cos(angular_distance)
    sin_lat_2 = _clamp(
        sin_lat * cos_distance + cos_lat * sin_distance * math.cos(azimuth),
        -1.0,
        1.0,
    )
    latitude_2 = math.asin(sin_lat_2)
    longitude_2 = longitude + math.atan2(
        math.sin(azimuth) * sin_distance * cos_lat,
        cos_distance - sin_lat * sin_lat_2,
    )
    return math.degrees(latitude_2), normalize_longitude_delta_deg(math.degrees(longitude_2))


def _great_circle_distance_m(
    latitude_a_deg: float,
    longitude_a_deg: float,
    latitude_b_deg: float,
    longitude_b_deg: float,
) -> float:
    phi_a = math.radians(latitude_a_deg)
    phi_b = math.radians(latitude_b_deg)
    delta_phi = phi_b - phi_a
    delta_lambda = math.radians(normalize_longitude_delta_deg(longitude_b_deg - longitude_a_deg))
    haversine = math.sin(delta_phi / 2.0) ** 2 + (
        math.cos(phi_a) * math.cos(phi_b) * math.sin(delta_lambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_M * math.asin(math.sqrt(_clamp(haversine, 0.0, 1.0)))


def coordinate_for_world(
    anchor: Mapping[str, object],
    world_x_m: float,
    world_y_m: float,
    altitude_m: object = None,
) -> dict[str, float]:
    """Convert local world metres to the QGC overlay's geographic coordinate."""

    anchor_latitude, anchor_longitude = _anchor(anchor)
    world_x = _finite(world_x_m, "world_x_m")
    world_y = _finite(world_y_m, "world_y_m")
    north_latitude, north_longitude = _direct_spherical(
        anchor_latitude,
        anchor_longitude,
        abs(world_y),
        0.0 if world_y >= 0.0 else 180.0,
    )
    latitude, longitude = _direct_spherical(
        north_latitude,
        north_longitude,
        abs(world_x),
        90.0 if world_x >= 0.0 else 270.0,
    )
    if altitude_m is None:
        altitude = _finite(anchor.get("altitude_m", 0.0), "anchor_altitude_m")
    else:
        altitude = _finite(altitude_m, "altitude_m")
    return {
        "latitude_deg": latitude,
        "longitude_deg": longitude,
        "altitude_m": altitude,
    }


def world_for_coordinate(
    anchor: Mapping[str, object],
    latitude_deg: float,
    longitude_deg: float,
) -> dict[str, float]:
    """Invert the overlay's north/south-then-east/west spherical construction."""

    anchor_latitude, anchor_longitude = _anchor(anchor)
    latitude = _finite(latitude_deg, "latitude_deg")
    longitude = _finite(longitude_deg, "longitude_deg")
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude_out_of_range")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude_out_of_range")

    delta_longitude_deg = normalize_longitude_delta_deg(longitude - anchor_longitude)
    delta_longitude = math.radians(delta_longitude_deg)
    if abs(delta_longitude) > math.pi / 2.0:
        raise ValueError("longitude_span_out_of_local_contract")

    # For the second, due-east/west great-circle leg, this is the latitude of
    # the intermediate point on the anchor meridian.
    target_latitude = math.radians(latitude)
    intermediate_latitude = math.atan2(
        math.sin(target_latitude),
        math.cos(target_latitude) * math.cos(delta_longitude),
    )
    intermediate_latitude_deg = math.degrees(intermediate_latitude)
    world_y = (intermediate_latitude - math.radians(anchor_latitude)) * EARTH_RADIUS_M

    distance = _great_circle_distance_m(
        intermediate_latitude_deg,
        anchor_longitude,
        latitude,
        longitude,
    )
    if abs(delta_longitude_deg) < 1.0e-12:
        world_x = 0.0
    else:
        world_x = math.copysign(distance, delta_longitude_deg)
    return {"x_m": world_x, "y_m": world_y}


def horizontal_distance_m(first: Mapping[str, object], second: Mapping[str, object]) -> float:
    return _great_circle_distance_m(
        _finite(first["latitude_deg"], "first_latitude_deg"),
        _finite(first["longitude_deg"], "first_longitude_deg"),
        _finite(second["latitude_deg"], "second_latitude_deg"),
        _finite(second["longitude_deg"], "second_longitude_deg"),
    )


def world_distance_m(first: Mapping[str, object], second: Mapping[str, object]) -> float:
    return math.hypot(
        _finite(first["x_m"], "first_x_m") - _finite(second["x_m"], "second_x_m"),
        _finite(first["y_m"], "first_y_m") - _finite(second["y_m"], "second_y_m"),
    )

