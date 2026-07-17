import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts/sunray"))

from p8_formation_runtime_math import (  # noqa: E402
    common_to_odom_xy,
    next_takeoff_uid,
    odom_to_common_xy,
    point_at_distance,
    rate_limit_vector,
    should_retry_takeoff,
)


def test_frame_conversion_handles_local_zero_odom():
    start = (-12.5, -19.3)
    home = (0.01, -0.02)
    odom = (0.31, -0.12)
    common = odom_to_common_xy(start, home, odom)
    assert common == pytest.approx((-12.2, -19.4))
    assert common_to_odom_xy(start, home, common) == pytest.approx(odom)


def test_frame_conversion_handles_world_aligned_odom():
    start = (-11.3, -20.1)
    home = (-11.32, -20.08)
    odom = (-11.02, -20.18)
    common = odom_to_common_xy(start, home, odom)
    assert common == pytest.approx((-11.0, -20.2))
    assert common_to_odom_xy(start, home, common) == pytest.approx(odom)


def test_takeoff_retry_is_bounded_and_stops_after_arming():
    assert not should_retry_takeoff(0.5, 0.0, 8, 120, 1.0, False)
    assert should_retry_takeoff(1.0, 0.0, 8, 120, 1.0, False)
    assert not should_retry_takeoff(2.0, 0.0, 120, 120, 1.0, False)
    assert not should_retry_takeoff(2.0, 0.0, 8, 120, 1.0, True)


def test_takeoff_selection_is_sequential_and_stops_when_all_armed():
    assert next_takeoff_uid({1: False, 2: False, 3: False}) == 1
    assert next_takeoff_uid({1: True, 2: False, 3: False}) == 2
    assert next_takeoff_uid({1: True, 2: True, 3: False}) == 3
    assert next_takeoff_uid({1: True, 2: True, 3: True}) is None


def test_rate_limit_vector_preserves_direction_and_bounds_step():
    assert rate_limit_vector((0.0, 0.0, 0.0), (3.0, 4.0, 0.0), 1.0) == pytest.approx((0.6, 0.8, 0.0))
    assert rate_limit_vector((0.0, 0.0), (0.1, -0.1), 1.0) == pytest.approx((0.1, -0.1))
    with pytest.raises(ValueError):
        rate_limit_vector((0.0,), (0.0, 1.0), 0.1)


def test_point_at_distance_preserves_pair_direction():
    assert point_at_distance((1.0, 2.0), (4.0, 6.0), 2.5) == pytest.approx((2.5, 4.0))
    with pytest.raises(ValueError):
        point_at_distance((1.0, 2.0), (1.0, 2.0), 0.85)


def test_runtime_keeps_fault_and_cbf_acceptance_gates():
    source = (ROOT / "Scripts/sunray/p8_formation_generated_mission_node.py").read_text(encoding="utf-8")
    assert 'self.mode_id == 7' in source
    assert 'int(row["failed_mask"]) == 2' in source
    assert 'int(row["active_agents"]) == 2' in source
    assert 'self.mode_id == 8' in source
    assert 'int(row["safety_corrections"]) > 0' in source


def test_runtime_does_not_duplicate_px4ctrl_position_feedback_by_default():
    source = (ROOT / "Scripts/sunray/p8_formation_generated_mission_node.py").read_text(encoding="utf-8")
    assert 'P8_GENERATED_VELOCITY_FEEDFORWARD_SCALE", "0.0"' in source
    assert "self.generated_velocity_feedforward_scale * outputs[velocity_base]" in source
    assert '"generated_velocity_feedforward_scale"' in source
    assert 'P8_GENERATED_POSITION_RATE_LIMIT_MPS", "0.35"' in source
    assert "rate_limit_vector(" in source
    assert '"raw_formation_xy_error_m"' in source
    assert 'P8_CBF_INJECTION_DISTANCE_M", "0.85"' in source
    assert "self.cbf_event_observed" in source


def test_takeoff_phase_does_not_publish_position_commands_before_auto_takeoff():
    source = (ROOT / "Scripts/sunray/p8_formation_generated_mission_node.py").read_text(encoding="utf-8")
    takeoff_branch = source.split('if self.phase == "takeoff":', 1)[1].split('if self.phase != "hover":', 1)[0]
    assert "publish_takeoff_land" in takeoff_branch
    assert "super().publish_hover_cmds()" not in takeoff_branch


def test_basic_mission_uses_home_relative_takeoff_altitude():
    source = (ROOT / "Scripts/sunray/px4ctrl_swarm_basic_mission_node.py").read_text(encoding="utf-8")
    assert "uav.home_odom_z = float(uav.odom[\"z\"])" in source
    assert "self.takeoff_target_z(uav)" in source
    assert "(uav.home_odom_z or 0.0) + self.args.takeoff_height" in source
    assert "(uav.home_truth_z or 0.0) + self.args.takeoff_height" in source
    assert "all_landed and (not self.args.require_disarmed or all_disarmed)" in source
    assert "self.now() - hover_start < self.args.hover_s" in source


def test_p8_requires_disarm_and_retries_land_for_armed_uavs():
    source = (ROOT / "Scripts/sunray/p8_formation_generated_mission_node.py").read_text(encoding="utf-8")
    assert 'args.landed_z_max = float(os.environ.get("P8_LANDED_Z_MAX", "0.30"))' in source
    assert 'P8_STEADY_HOVER_TAIL_S", "5.0"' in source
    assert "args.require_disarmed = True" in source
    assert 'self.phase != "land"' in source
    assert "retry_land_for_armed_uavs" in source
    assert "if uav.state and uav.state.armed" in source


def test_p8_gazebo_matrix_is_serial_and_fail_fast():
    source = (ROOT / "Scripts/sunray/run_p8_formation_generated_gazebo_matrix.sh").read_text(encoding="utf-8")
    assert "for mode_id in ${P8_MODE_IDS}" in source
    assert "run_px4ctrl_ego_swarm_gate.sh" in source
    assert "P8_FORMATION_MODE_ID=\"${mode_id}\"" in source
    assert "P8_MODE_BLOCKED" in source
    assert "exit \"${mode_id}\"" in source
