from __future__ import annotations

from Scripts.ros.pointcloud_to_local_voxel_map_ros2 import (
    LocalMapConfig,
    Transform3D,
    Voxel,
    project_voxels_to_grid,
    transform_point,
    transform_points,
    voxel_center,
    voxelize_points,
)


def test_voxelize_points_filters_bounds_and_deduplicates() -> None:
    config = LocalMapConfig(
        voxel_size_m=0.2,
        grid_resolution_m=0.2,
        local_radius_m=1.0,
        z_min_m=-0.5,
        z_max_m=1.0,
    )
    points = [
        (0.01, 0.01, 0.01),
        (0.19, 0.19, 0.01),
        (-0.01, -0.01, 0.01),
        (1.10, 0.0, 0.0),
        (0.0, 0.0, 1.20),
        (0.0, 0.0, -0.60),
        (0.39, -0.21, 0.99),
    ]

    assert voxelize_points(points, config) == {
        Voxel(0, 0, 0),
        Voxel(-1, -1, 0),
        Voxel(1, -2, 4),
    }


def test_voxel_center_uses_cell_midpoint() -> None:
    assert voxel_center(Voxel(1, -2, 4), 0.2) == (0.30000000000000004, -0.30000000000000004, 0.9)


def test_project_voxels_to_grid_marks_projected_occupied_cells() -> None:
    config = LocalMapConfig(
        voxel_size_m=0.2,
        grid_resolution_m=0.5,
        local_radius_m=1.0,
        z_min_m=-1.0,
        z_max_m=1.0,
    )
    projection = project_voxels_to_grid({Voxel(0, 0, 0), Voxel(-1, -1, 0)}, config)

    assert projection.width == 4
    assert projection.height == 4
    assert projection.origin_x_m == -1.0
    assert projection.origin_y_m == -1.0

    occupied = [index for index, value in enumerate(projection.data) if value == 100]
    assert occupied == [5, 10]
    assert projection.data.count(-1) == 14


def test_transform_point_applies_translation_and_quaternion_rotation() -> None:
    transform = Transform3D(
        translation_xyz=(1.0, 2.0, 3.0),
        rotation_xyzw=(0.0, 0.0, 0.7071067811865476, 0.7071067811865476),
    )

    x, y, z = transform_point((1.0, 0.0, 0.0), transform)

    assert round(x, 6) == 1.0
    assert round(y, 6) == 3.0
    assert round(z, 6) == 3.0


def test_transform_points_supports_sensor_frame_to_map_voxelization() -> None:
    transform = Transform3D(
        translation_xyz=(10.0, 0.0, 0.0),
        rotation_xyzw=(0.0, 0.0, 0.0, 1.0),
    )
    config = LocalMapConfig(
        voxel_size_m=0.5,
        grid_resolution_m=0.5,
        local_radius_m=2.0,
        z_min_m=-1.0,
        z_max_m=1.0,
        center_x_m=10.0,
        center_y_m=0.0,
        center_z_m=0.0,
    )

    voxels = voxelize_points(transform_points([(0.0, 0.0, 0.0), (3.0, 0.0, 0.0)], transform), config)

    assert voxels == {Voxel(20, 0, 0)}
