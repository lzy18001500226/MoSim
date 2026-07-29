from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELAY = ROOT / "Scripts" / "sunray" / "swarm_formation_broadcast_relay.py"
RUNNER = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_swarm_gate.sh"
FACTORY_GATE = ROOT / "Scripts" / "sunray" / "run_factory_l2_swarm_formation_obstacle_gate.ps1"
FSM = (
    ROOT
    / "References"
    / "Lab"
    / "swarm_coordination"
    / "Swarm-Formation"
    / "src"
    / "planner"
    / "plan_manage"
    / "src"
    / "ego_replan_fsm.cpp"
)
OPTIMIZER = (
    ROOT
    / "References"
    / "Lab"
    / "swarm_coordination"
    / "Swarm-Formation"
    / "src"
    / "planner"
    / "traj_opt"
    / "src"
    / "poly_traj_optimizer.cpp"
)


def test_same_master_relay_preserves_polytraj_time_origin() -> None:
    relay = RELAY.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")

    assert 'rospy.get_param("~retime_future_s", 0.0)' in relay
    assert "must be exactly zero" in relay
    assert "rospy.Time.now() + rospy.Duration" not in relay
    assert '"mode": "transparent_single_ros_master"' in relay
    assert '"transparent_count": self.transparent_count' in relay
    assert '"retime_count": self.retime_count' in relay
    assert "SWARM_FORMATION_D3_RELAY_RETIME_FUTURE_S" in runner
    assert "must be zero: PolyTraj coefficients are relative to start_time" in runner
    assert '"mode": "single_ros_master_transparent"' in runner
    assert '"timestamp_semantics": "preserve_start_time_and_polynomial_phase"' in runner


def test_factory_gate_keeps_the_generic_floor_filter() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    factory_gate = FACTORY_GATE.read_text(encoding="utf-8")

    assert 'POINTCLOUD_MIN_WORLD_Z_M="-0.20"' not in runner
    assert '"POINTCLOUD_MIN_WORLD_Z_M=0.50"' in factory_gate
    assert '"SWARM_FORMATION_D3_RELAY_RETIME_FUTURE_S=0.0"' in factory_gate


def test_swarm_receiver_preserves_valid_trajectory_phase_until_expiry() -> None:
    fsm = FSM.read_text(encoding="utf-8")
    callback = fsm.split("void EGOReplanFSM::RecvBroadcastPolyTrajCallback", 1)[1].split(
        "void EGOReplanFSM::changeFSMExecState", 1
    )[0]

    assert "declared_duration_s" in callback
    assert "age_s < -swarm_traj_time_tolerance_s_" in callback
    assert "age_s > declared_duration_s + swarm_traj_time_tolerance_s_" in callback
    assert "Rejecting expired swarm trajectory" in callback
    assert "std::abs(time_diff_s)" not in callback


def test_swarm_collision_check_samples_trajectories_at_one_global_time() -> None:
    fsm = FSM.read_text(encoding="utf-8")
    collision = fsm.split("void EGOReplanFSM::checkCollisionCallback", 1)[1].split(
        "void EGOReplanFSM::planGlobalTrajbyGivenWps", 1
    )[0]

    assert "const double sample_global_time = info->start_time + t;" in collision
    assert "double peer_sample_time =" in collision
    assert "sample_global_time - planner_manager_->traj_.swarm_traj.at(id).start_time" in collision
    assert "peer_sample_time = std::max(0.0, peer_sample_time);" in collision
    assert "const Eigen::Vector3d own_predicted = info->traj.getPos(t);" in collision
    assert "traj.getPos(peer_sample_time)" in collision
    assert "double dist = (own_predicted - swarm_predicted).norm();" in collision
    assert "double t_X = t_cur_global" not in collision
    assert "(p_cur - swarm_pridicted).norm()" not in collision


def test_optimizer_rejects_height_band_escape_after_start_exemption() -> None:
    optimizer = OPTIMIZER.read_text(encoding="utf-8")
    collision = optimizer.split("bool PolyTrajOptimizer::checkCollision", 1)[1].split(
        "/* callbacks by the L-BFGS optimizer */", 1
    )[0]

    assert "height_band_enabled" in collision
    assert "start_within_height_band" in collision
    assert "outside_height_band" in collision
    assert "optimized trajectory height-band violation" in collision
    assert collision.index("outside_height_band") < collision.index(
        "(pos - start_pos).norm() < obs_clearance_"
    )
