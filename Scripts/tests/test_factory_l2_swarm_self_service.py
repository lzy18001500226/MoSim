from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_three_uav_self_service_entrypoints_are_split_by_operator_stage() -> None:
    expected = {
        "cmd/01_预检Factory三机环境.cmd": "preflight_factory_l2_swarm_formation.ps1",
        "cmd/03_启动Factory三机固定编队.cmd": "start_factory_l2_swarm_formation_backend.ps1",
        "cmd/04_打开Factory三机RViz审核.cmd": "open_factory_l2_swarm_formation_rviz_review.ps1",
        "cmd/05_检查Factory三机状态.cmd": "check_factory_l2_swarm_formation_runtime.ps1",
        "cmd/06_停止Factory三机编队.cmd": "stop_factory_l2_swarm_formation_runtime.ps1",
    }

    for name, target in expected.items():
        content = (ROOT / name).read_text(encoding="utf-8")
        assert target in content
        assert "pause" in content


def test_runtime_probe_requires_live_three_uav_clouds_grids_and_mavros_links() -> None:
    source = (ROOT / "Scripts/sunray/probe_swarm_formation_runtime.py").read_text(encoding="utf-8")

    for uid in range(1, 4):
        assert f"/mosim/swarm_formation/uav{{uid}}/livox_world_accumulated" in source
        assert f"/uav{{uid}}/livox_world" in source
        assert f"/uav{{uid}}/mavros/state" in source
    for drone_id in range(3):
        assert f"/drone_{{drone_id}}/ego_planner_node/grid_map/occupancy_inflate" in source
    assert "required_topics_missing_or_empty" in source
    assert "review_accumulated_clouds" in source
    assert "sensor_grid_readiness" in source
    assert "flight_link_readiness" in source
    assert "rviz_map_readiness" in source
    assert "Read-only liveness check" in source


def test_runtime_probe_uses_same_run_tracker_history_only_for_missed_grid_samples() -> None:
    source = (ROOT / "Scripts/sunray/probe_swarm_formation_runtime.py").read_text(encoding="utf-8")

    assert "--mission-tracker-partial" in source
    assert "EGO_SWARM_METRICS_PARTIAL.json" in source
    assert "mission_tracker_occupancy_history" in source
    assert "occupancy_grid_readiness" in source
    assert '"effective_source"' in source
    assert "A same-run mission tracker may only supplement a missed instantaneous occupancy topic sample" in source
    assert "world_missing" in source
    assert "occupancy_missing" in source


def test_status_check_does_not_overwrite_a_finished_run_from_a_stale_pointer() -> None:
    source = (ROOT / "Scripts/sunray/check_factory_l2_swarm_formation_runtime.ps1").read_text(
        encoding="utf-8"
    )

    assert 'in @(\"launch_requested\", \"running\")' in source
    assert "writing a standalone health snapshot" in source
    assert "Sensor/grid readiness" in source
    assert "Flight-link readiness" in source
    assert "RViz accumulated-map readiness" in source


def test_manual_stop_uses_precise_runner_signal_escalation_and_not_a_broad_process_kill() -> None:
    source = (ROOT / "Scripts/sunray/stop_factory_l2_swarm_formation_runtime.ps1").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")

    assert 'Send-ProcessSnapshotSignal -Signal "INT"' in source
    assert 'Send-ProcessSnapshotSignal -Signal "TERM"' in source
    assert 'Send-ProcessSnapshotSignal -Signal "KILL"' in source
    assert 'ValidateSet("INT", "TERM", "KILL")' in source
    assert "Get-RunnerProcessSnapshot" in source
    assert "Test-ProcessSnapshotAlive" in source
    assert 'f"/proc/{pid}/cmdline"' in source
    assert "starttime" in source
    assert "$WslCommandTimeoutS = 20" in source
    assert "[r]un_px4ctrl_ego_swarm_gate" in source
    assert 'pkill -f "gzserver"' not in runner
    assert 'pkill -f "mavros_node"' not in runner
    assert "owned_process_tree_snapshot" in runner
    assert "signal_owned_process_tree KILL" in runner
    assert "pkill -f \"gzserver\"" not in source
    assert "Closing only its owned RViz review processes" in source
    assert source.index("$reviewStopCommand") < source.index("if (-not $hasActiveRunner)")
    assert "RUNTIME_STOP_REQUESTED=true" in runner
    assert "trap handle_runtime_stop_signal INT TERM HUP" in runner
    assert "Invoke-SunrayWslBash" in source
    assert "& wsl -d Ubuntu-20.04" not in source
    assert "[r]un_px4ctrl_ego_swarm_gate" in source


def test_three_uav_startup_uses_a_project_local_mavros_timeout_and_stability_gate() -> None:
    runner = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")
    launch = (ROOT / "Scripts/sunray/goal5_sunray_px4_basic.launch").read_text(encoding="utf-8")
    preloaded_launch = (ROOT / "Scripts/sunray/goal5_swarm_px4_preloaded_gazebo.launch").read_text(
        encoding="utf-8"
    )
    no_spawn_launch = (ROOT / "Scripts/sunray/goal5_px4_mavros_no_spawn.launch").read_text(encoding="utf-8")
    mission = (ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py").read_text(encoding="utf-8")

    assert "MAVROS_CONN_TIMEOUT_S" in runner
    assert "MAVROS_READY_MIN_STATE_SAMPLES" in runner
    assert "MAVROS_READY_STABLE_WALL_S" in runner
    assert "goal5_sunray_px4_basic.launch" in runner
    assert "mavros_conn_timeout_s:=" in runner
    assert '"mavros_connection"' in runner
    assert '<param name="conn/timeout" value="$(arg mavros_conn_timeout_s)" />' in launch
    assert '<arg name="mavros_conn_timeout_s" default="60.0"/>' in preloaded_launch
    assert preloaded_launch.count('mavros_conn_timeout_s" value="$(arg mavros_conn_timeout_s)"') == 3
    assert '<arg name="mavros_conn_timeout_s" default="60.0"/>' in no_spawn_launch
    assert '<param name="mavros/conn/timeout" value="$(arg mavros_conn_timeout_s)"/>' in no_spawn_launch
    assert "/mavros/cmd/arming" in runner
    assert "/mavros/set_mode" in runner
    assert "mavros_state_stability_snapshot" in mission
    assert "--mavros-ready-min-state-samples" in mission
    assert "--mavros-ready-stable-wall-s" in mission


def test_swarm_mission_keeps_the_peak_occupancy_sample_for_final_acceptance() -> None:
    mission = (ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py").read_text(encoding="utf-8")

    assert "occupancy_max_points: int = 0" in mission
    assert "uav.occupancy_max_points = max(uav.occupancy_max_points, uav.occupancy_points)" in mission
    assert "uav.occupancy_max_points < self.args.min_occupancy_points" in mission
    assert '"max_point_counts"' in mission
    assert '"occupancy_inflate": uav.occupancy_max_points' in mission


def test_swarm_formation_runtime_audit_rejects_planner_emergency_stops() -> None:
    runner = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")

    assert 'PLANNER_SEMANTIC_PROFILE="swarm_formation"' in runner
    assert '--planner-semantic-profile "${PLANNER_SEMANTIC_PROFILE}"' in runner

def test_preflight_is_read_only_and_reports_manual_wsl_restart_advice() -> None:
    source = (ROOT / "Scripts/sunray/preflight_factory_l2_swarm_formation.ps1").read_text(
        encoding="utf-8"
    )

    assert "check_sunray_ros1_runtime_preflight.sh" in source
    assert "Invoke-SunrayWslBash" in source
    assert '"wsl --shutdown"' in source
    assert "$runnerProbeFailed = $runner.ExitCode -ne 0" in source
    assert "runner_probe_failed_inspect_evidence" in source
    assert "probe_exit_code = $runner.ExitCode" in source
    assert "probe_failed = $runnerProbeFailed" in source
    assert "Read-only preflight" in source
    assert "pkill" not in source
    assert "[r]un_px4ctrl_ego_swarm_gate" in source


def test_backend_dry_run_does_not_replace_the_active_run_pointer() -> None:
    source = (ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_backend.ps1").read_text(
        encoding="utf-8"
    )

    dry_run_branch = source.index("if ($DryRun)")
    active_pointer_write = source.index("Set-Content -LiteralPath $ActivePath")
    assert dry_run_branch < active_pointer_write
    assert "without changing the active run pointer" in source


def test_backend_uses_conservative_dynamics_by_default_and_records_it() -> None:
    source = (ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_backend.ps1").read_text(
        encoding="utf-8"
    )

    assert '[ValidateSet("r6_baseline_v1", "conservative_v1")]' in source
    assert '[string]$DynamicsProfile = "conservative_v1"' in source
    assert "-DynamicsProfile $DynamicsProfile" in source
    assert "dynamics_profile = $DynamicsProfile" in source


def test_keep_alive_preserves_the_owned_runner_until_an_explicit_stop() -> None:
    runner = (ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh").read_text(encoding="utf-8")

    assert 'if [[ "${KEEP_ALIVE:-false}" == "true" && "${MISSION_EXIT_CODE}" -eq 0 ]]; then' in runner
    assert "KEEP_ALIVE_READY.json" in runner
    assert '"status": "mission_passed_keep_alive"' in runner
    assert 'stream.write("\\n")' in runner
    assert 'stream.write("\\\\n")' not in runner
    assert "os.replace(temporary_path, output_path)" in runner
    assert "Mission passed; keeping the owned three-UAV runtime alive" in runner
    assert runner.index("while true; do", runner.index("Mission passed; keeping")) < runner.rindex(
        'exit "${MISSION_EXIT_CODE}"'
    )


def test_controlled_keep_alive_stop_requires_complete_gate_evidence_before_success() -> None:
    launcher = (ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_backend.ps1").read_text(
        encoding="utf-8"
    )
    stop = (ROOT / "Scripts/sunray/stop_factory_l2_swarm_formation_runtime.ps1").read_text(
        encoding="utf-8"
    )

    assert "Test-ControlledKeepAliveCompletion" in launcher
    for artifact in (
        "KEEP_ALIVE_READY.json",
        "OPERATOR_STOP_REQUESTED.json",
        "EGO_SWARM_METRICS.json",
        "planner_runtime_log_audit.json",
        "SWARM_FORMATION_TRACKING_GATE.json",
        "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json",
    ):
        assert artifact in launcher
    assert '"mission_passed_keep_alive"' in launcher
    assert '"operator_stop_requested"' in launcher
    assert '"finished_after_operator_stop"' in launcher
    assert "raw_gate_exit_code" in launcher
    assert "Write-OperatorStopRequest" in stop
    assert "OPERATOR_STOP_REQUESTED.json" in stop
    assert '"This marker records an operator-requested stop' in stop


def test_self_service_workflow_requires_preflight_before_backend_start() -> None:
    workflow = (ROOT / "Docs/Workflows/sunray_factory_three_uav_self_service.md").read_text(
        encoding="utf-8"
    )

    assert workflow.index("cmd/01_预检Factory三机环境.cmd") < workflow.index(
        "cmd/03_启动Factory三机固定编队.cmd"
    )
    assert "When it reports `busy`, do not start another backend." in workflow


def test_swarm_review_suppresses_only_the_ros1_eol_information_popup() -> None:
    gate = (ROOT / "Scripts/sunray/run_factory_l2_swarm_formation_obstacle_gate.ps1").read_text(
        encoding="utf-8"
    )
    review = (ROOT / "Scripts/sunray/start_factory_l2_swarm_formation_review.ps1").read_text(
        encoding="utf-8"
    )

    assert '"DISABLE_ROS1_EOL_WARNINGS=1"' in gate
    assert "export DISABLE_ROS1_EOL_WARNINGS=1" in review
