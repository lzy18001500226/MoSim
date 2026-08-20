from __future__ import annotations

import importlib.util
import pytest
import sys
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MEASUREMENT = ROOT / "Scripts" / "sunray" / "measure_gazebo_raw_cloud_pacing.py"


def load_module():
    spec = importlib.util.spec_from_file_location("measure_gazebo_raw_cloud_pacing", MEASUREMENT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_raw_cloud_summary_preserves_pointcloud2_layout() -> None:
    module = load_module()
    snapshot = {
        "messages": 12,
        "nonempty_messages": 12,
        "latest_point_count": 4,
        "latest_data_bytes": 64,
        "latest_frame_id": "uav1/base_link",
        "latest_stamp_s": 12.5,
        "latest_point_step": 16,
        "latest_row_step": 64,
        "latest_is_bigendian": False,
        "latest_fields": [
            {"name": "x", "offset": 0, "datatype": 7, "count": 1},
            {"name": "y", "offset": 4, "datatype": 7, "count": 1},
            {"name": "z", "offset": 8, "datatype": 7, "count": 1},
        ],
        "latest_xyz_summary": {"status": "available", "finite_point_count": 4},
        "observations": [
            {"arrival_monotonic_s": 9.95, "header_stamp_s": 12.45, "nonempty": True},
            {"arrival_monotonic_s": 10.05, "header_stamp_s": 12.55, "nonempty": True},
            {"arrival_monotonic_s": 12.50, "header_stamp_s": 15.00, "nonempty": True},
            {"arrival_monotonic_s": 14.95, "header_stamp_s": 17.45, "nonempty": True},
        ],
    }

    summary = module.raw_cloud_summary(
        snapshot,
        initial_messages=2,
        initial_nonempty_messages=2,
        duration_s=5.0,
        window_start_monotonic_s=10.0,
        window_end_monotonic_s=15.0,
    )

    assert summary["messages_in_window"] == 10
    assert summary["nonempty_messages_in_window"] == 10
    assert summary["wall_rate_hz"] == 2.0
    assert summary["latest_point_step"] == 16
    assert summary["latest_row_step"] == 64
    assert summary["latest_is_bigendian"] is False
    assert summary["latest_fields"] == snapshot["latest_fields"]
    assert summary["latest_xyz_summary"] == snapshot["latest_xyz_summary"]
    assert summary["continuity"]["nonempty_observations_in_window"] == 3
    assert summary["continuity"]["max_nonempty_wall_gap_s"] == pytest.approx(2.45)


def test_continuity_summary_counts_a_silent_tail_gap() -> None:
    module = load_module()

    summary = module.continuity_summary(
        [
            {"arrival_monotonic_s": 9.98, "header_stamp_s": 4.98, "nonempty": True},
            {"arrival_monotonic_s": 10.04, "header_stamp_s": 5.04, "nonempty": True},
            {"arrival_monotonic_s": 10.10, "header_stamp_s": 5.10, "nonempty": True},
        ],
        window_start_monotonic_s=10.0,
        window_end_monotonic_s=11.0,
    )

    assert summary["max_nonempty_wall_gap_s"] == pytest.approx(0.9)


def test_cloud_stream_continuity_allows_only_bounded_scheduler_jitter() -> None:
    module = load_module()

    assert module.cloud_stream_continuous(True, 0.25039, 0.25, 0.005)
    assert not module.cloud_stream_continuous(True, 0.25501, 0.25, 0.005)
    assert not module.cloud_stream_continuous(True, None, 0.25, 0.005)
    assert not module.cloud_stream_continuous(False, 0.05, 0.25, 0.005)


def test_pointcloud_xyz_summary_reads_little_endian_xyz_fields() -> None:
    module = load_module()
    data = b"".join(
        struct.pack("<ffff", x, y, z, 1.0)
        for x, y, z in ((1.0, -2.0, 3.0), (4.0, 5.0, -6.0))
    )

    summary = module.pointcloud_xyz_summary(
        data,
        point_count=2,
        point_step=16,
        fields=[
            {"name": "x", "offset": 0, "datatype": 7, "count": 1},
            {"name": "y", "offset": 4, "datatype": 7, "count": 1},
            {"name": "z", "offset": 8, "datatype": 7, "count": 1},
        ],
        is_bigendian=False,
    )

    assert summary["status"] == "available"
    assert summary["finite_point_count"] == 2
    assert summary["min_xyz"] == [1.0, -2.0, -6.0]
    assert summary["max_xyz"] == [4.0, 5.0, 3.0]
    assert summary["sum_xyz"] == [5.0, 3.0, -3.0]
