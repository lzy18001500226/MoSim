from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "planning" / "diff_planner" / "src" / "diff_planner" / "plan_manage" / "src" / "traj_server.cpp"
FSM_SOURCE = ROOT / "src" / "planning" / "diff_planner" / "src" / "diff_planner" / "plan_manage" / "src" / "diff_replan_fsm.cpp"
MANAGER_SOURCE = ROOT / "src" / "planning" / "diff_planner" / "src" / "diff_planner" / "plan_manage" / "src" / "planner_manager.cpp"


def test_default_traj_server_keeps_terminal_position_command_alive() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert "#if !FLIP_YAW_AT_END && !TURN_YAW_TO_CENTER_AT_END" in source
    terminal_branch = source.split("#if !FLIP_YAW_AT_END && !TURN_YAW_TO_CENTER_AT_END", 1)[1]
    terminal_branch = terminal_branch.split("#if FLIP_YAW_AT_END", 1)[0]
    assert "else if (t_cur >= traj_duration_)" in terminal_branch
    assert "pos = traj_->getPos(traj_duration_);" in terminal_branch
    assert "publish_cmd(pos, vel, acc, jer, yaw_yawdot.first, yaw_yawdot.second);" in terminal_branch


def test_preset_waypoints_advance_on_actual_low_speed_arrival() -> None:
    source = FSM_SOURCE.read_text(encoding="utf-8")

    assert "const double waypoint_reached_speed" in source
    assert "(odom_pos_ - final_goal_).norm() < no_replan_thresh_" in source
    assert "odom_vel_.norm() < waypoint_reached_speed" in source
    assert "actual_at_final_goal) // case 2: assign the next waypoint only after actual arrival" in source
    assert "(final_goal_ - pos).norm() < no_replan_thresh_) // case 2" not in source


def test_random_recovery_initialization_stays_in_horizontal_plane() -> None:
    source = MANAGER_SOURCE.read_text(encoding="utf-8")

    assert "Keep fallback initialization in the horizontal planning plane" in source
    assert "Eigen::Vector3d lateral(-delta(1), delta(0), 0.0);" in source
    assert "const double side = (continous_failures_count_ % 2 == 0) ? 1.0 : -1.0;" in source
    assert "(((double)rand()) / RAND_MAX" not in source
    assert "vertical_dir" not in source
