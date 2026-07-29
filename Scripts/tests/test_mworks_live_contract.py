from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = load_module(
    "validate_live_contract",
    ROOT / "Scripts/mworks_live/validate_live_contract.py",
)
analyzer = load_module(
    "analyze_rt0_trace",
    ROOT / "Scripts/mworks_live/analyze_rt0_trace.py",
)
auditor = load_module(
    "audit_existing_generated_c",
    ROOT / "Scripts/mworks_live/audit_existing_generated_c.py",
)
probe_client = load_module(
    "run_rt0_probe_client",
    ROOT / "Scripts/mworks_live/run_rt0_probe_client.py",
)
live_backend = load_module(
    "model_studio_live_backend",
    ROOT / "Scripts/mworks_live/model_studio_live_backend.py",
)
rt1 = load_module(
    "rt1_contract",
    ROOT / "Scripts/mworks_live/rt1_contract.py",
)
preflight = load_module(
    "preflight_connection",
    ROOT / "Scripts/mworks_live/preflight_connection.py",
)
rt1_shadow_analyzer = load_module(
    "analyze_rt1_shadow",
    ROOT / "Scripts/mworks_live/analyze_rt1_shadow.py",
)


def test_contract_and_candidate_profiles_are_consistent() -> None:
    result = validator.validate(validator.DEFAULT_CONTRACT, list(validator.DEFAULT_PROFILES))
    assert result["ok"], result["errors"]
    assert len(result["profiles"]) == 2
    assert all(len(item["profile_hash"]) == 64 for item in result["profiles"])


def rt0_rows(count: int = 1001) -> list[dict[str, object]]:
    rows = []
    base = 10_000_000_000
    for sequence in range(count):
        sent = base + sequence * 10_000_000
        rows.append(
            {
                "sequence": sequence,
                "input_sent_monotonic_ns": sent,
                "compute_started_monotonic_ns": sent + 500_000,
                "compute_finished_monotonic_ns": sent + 1_500_000,
                "output_received_monotonic_ns": sent + 2_000_000,
                "command_source_stamp_ns": sent,
                "output_valid": True,
                "execution_source": "mworks_sysplorer_realtime",
                "sim_mode": 2,
            }
        )
    return rows


def test_rt0_analyzer_accepts_real_realtime_trace_shape() -> None:
    contract = json.loads(analyzer.DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    result = analyzer.analyze(contract, rt0_rows())
    assert result["ok"], result["errors"]
    assert result["metrics"]["output_rate_hz"] == 100.0


def test_rt0_analyzer_rejects_transport_only_provenance() -> None:
    contract = json.loads(analyzer.DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    rows = rt0_rows()
    for row in rows:
        row["execution_source"] = "python_udp_loopback"
    result = analyzer.analyze(contract, rows)
    assert not result["ok"]
    assert any("execution_source" in error for error in result["errors"])


def test_rt0_analyzer_applies_consecutive_deadline_miss_policy() -> None:
    contract = json.loads(analyzer.DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    rows = rt0_rows()
    for row in rows[10:12]:
        row["output_received_monotonic_ns"] = int(row["input_sent_monotonic_ns"]) + 11_000_000
    accepted = analyzer.analyze(contract, rows)
    assert accepted["ok"], accepted["errors"]
    assert accepted["metrics"]["max_consecutive_deadline_misses"] == 2

    rows[12]["output_received_monotonic_ns"] = int(rows[12]["input_sent_monotonic_ns"]) + 11_000_000
    rejected = analyzer.analyze(contract, rows)
    assert not rejected["ok"]
    assert rejected["metrics"]["max_consecutive_deadline_misses"] == 3


def test_rt0_analyzer_rejects_batched_average_rate() -> None:
    contract = json.loads(
        (ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v3_candidate_200hz.json").read_text(
            encoding="utf-8"
        )
    )
    rows = rt0_rows(2001)
    base = 10_000_000_000
    for sequence, row in enumerate(rows):
        batch = sequence // 4
        within_batch = sequence % 4
        sent = base + sequence * 5_000_000
        output = base + batch * 20_000_000 + within_batch * 10_000
        row.update(
            input_sent_monotonic_ns=sent,
            command_source_stamp_ns=sent,
            compute_started_monotonic_ns=output - 100_000,
            compute_finished_monotonic_ns=output - 50_000,
            output_received_monotonic_ns=output,
        )
    result = analyzer.analyze(contract, rows)
    assert result["metrics"]["output_rate_hz"] > 198.0
    assert result["ok"] is False
    assert "output period p99 exceeds output-period deadline" in result["errors"]


def test_existing_generated_c_assets_are_reusable() -> None:
    result = auditor.audit()
    assert result["ok"], result["errors"]
    assert result["decision"]["rebuild_generated_c"] is False
    assert result["official_pid"]["verified_generated_files"] >= 5
    assert result["awff"]["verified_generated_files"] >= 5
    assert result["official_pid"]["generated_hashes_match_manifest"] is True
    assert result["awff"]["current_sil_status"] == "passed"
    assert result["awff"]["runtime_provenance_refresh_required"] is True


def test_rt0_wire_layout_matches_packed_external_c_contract() -> None:
    assert probe_client.REQUEST.size == 60
    assert probe_client.RESPONSE.size == 72
    assert probe_client.REQUEST_MAGIC == 0x4D525451
    assert probe_client.RESPONSE_MAGIC == 0x4D525452

    model = (ROOT / "Models/MoSimQuadrotorModel/Deployment/RT0RealtimeProbe.mo").read_text(encoding="utf-8")
    header = (ROOT / "Models/MoSimQuadrotorModel/Deployment/Resources/Include/mosim_mworks_live_rt0_bridge.h").read_text(
        encoding="utf-8"
    )
    assert "when sample(0, samplePeriod)" in model
    assert "processedFrames := pre(processedFrames)" in model
    assert 'Library="Ws2_32"' in model
    assert "#pragma pack(push, 1)" in header
    assert "MOSIM_RT0_PORT 49010u" in header
    assert "answer only the freshest request" in header
    assert "latest_request = request;" in header
    assert "coalescedFrames" in model

    model_200 = (ROOT / "Models/MoSimQuadrotorModel/Deployment/RT0RealtimeProbe200Hz.mo").read_text(encoding="utf-8")
    timer_header = (
        ROOT / "Models/MoSimQuadrotorModel/Deployment/Resources/Include/mosim_mworks_live_rt0_timer_resolution.h"
    ).read_text(encoding="utf-8")
    assert 'Library="Winmm"' in model_200
    assert "when initial() then" in model_200
    assert "timerResolutionStatus := requestHighResolutionTimer();" in model_200
    assert "timeBeginPeriod(1)" in timer_header
    finalize_source = (ROOT / "Scripts/mworks_live/finalize_rt0_invocation.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("--contract"' in finalize_source
    assert "mosim_mworks_live_rt0_timer_resolution.h" in finalize_source


def test_model_studio_live_backend_exposes_real_profile_identity() -> None:
    result = live_backend.capability("official_pid")
    assert result["profile_id"] == "mworks_live_official_pid_hover_50hz_v2"
    assert len(result["profile_hash"]) == 64
    assert result["rt0_status"] in {"not_validated", "failed", "passed"}
    if not result["accepted"]:
        assert result["reason_code"] in {
            "rt0_not_validated",
            "rt0_failed",
            "rt0_provenance_mismatch",
            "live_profile_not_published",
        }

    result_200 = live_backend.capability("official_pid_200hz")
    assert result_200["profile_id"] == "mworks_live_official_pid_hover_200hz_v1"
    assert result_200["requested_rate_hz"] == 200
    assert result_200["reason_code"] in {
        "mworks_live_capability_ready",
        "rt0_not_validated",
        "rt0_failed",
        "rt0_provenance_mismatch",
        "live_profile_not_published",
    }


def test_rt0_provenance_ignores_only_package_discoverability_index() -> None:
    values = {
        "Models/MoSimQuadrotorModel/Deployment/package.order": "index-hash",
        "Models/MoSimQuadrotorModel/Deployment/RT0RealtimeProbe.mo": "model-hash",
    }
    assert live_backend.rt0_authoritative_hashes(values) == {
        "Models/MoSimQuadrotorModel/Deployment/RT0RealtimeProbe.mo": "model-hash"
    }


def test_connection_contract_exposes_50_100_200_scan_and_system_links() -> None:
    connection = json.loads(
        (ROOT / "Config/control_platform/mworks_live_connection_contract_v1.json").read_text(encoding="utf-8")
    )
    observability = json.loads(
        (ROOT / "Config/control_platform/runtime_observability_contract_v1.json").read_text(encoding="utf-8")
    )
    assert connection["rate_candidates_hz"] == [50, 100, 200]
    assert connection["defaults"]["requested_rate_hz"] == 200
    candidate = json.loads(validator.DEFAULT_CONTRACT.read_text(encoding="utf-8"))
    assert candidate["contract_id"] == "mworks_live_attitude_thrust_v3_candidate_200hz"
    assert candidate["timing_candidates"]["nominal_rate_hz"] == 200
    assert candidate["timing_candidates"]["soft_deadline_warning_ms"] == 5.0
    assert candidate["timing_candidates"]["deadline_ms"] == 10.0
    assert observability["control_rate_capability_scan"]["accepted_baseline_hz"] == 50
    assert observability["control_rate_capability_scan"]["target_rate_hz"] == 200
    assert {row["link_id"] for row in observability["links"]} >= {
        "mworks_ros_control",
        "mavros_px4",
        "gazebo_runtime",
        "gazebo_ue_display",
        "ros_rviz_display",
        "mavlink_qgc_display",
    }


def test_published_200hz_profile_is_bound_to_v3_rt0_evidence() -> None:
    profile_path = ROOT / "Config/profiles/experiments/mworks_live_official_pid_hover_200hz_v1.json"
    result = validator.validate(validator.DEFAULT_CONTRACT, [profile_path])
    assert result["ok"] is True
    profile = json.loads(profile_path.read_text(encoding="utf-8"))["experiment_profile"]
    assert profile["frequency_profile"] == "attitude_thrust_200hz_candidate_v2"
    assert profile["capability_status"] == "rt0_validated"


def test_connection_preflight_rejects_bad_endpoint_without_network_io() -> None:
    result = preflight.run_preflight(
        preflight.Endpoint("bad host", 49020, "", "auto", 200),
        timeout_s=0.01,
        sample_count=1,
    )
    assert result["accepted"] is False
    assert result["reason_code"] == "invalid_target_host"


def test_200hz_prepare_is_blocked_until_new_rt0_profile_is_published() -> None:
    result = live_backend.prepare_with_connection(
        "official_pid",
        host="127.0.0.1",
        port=49020,
        ros_master_uri="",
        local_advertised_ip="auto",
        requested_rate_hz=200,
    )
    assert result["accepted"] is False
    assert result["reason_code"] == "prepare_blocked:requested_rate_unvalidated"


def rt1_command(sequence: int, *, source_ns: int, run_id: str = "run-rt1"):
    return rt1.CommandFrame(
        run_id=run_id,
        sequence=sequence,
        state_sequence=sequence,
        source_stamp_ns=source_ns,
        produced_monotonic_ns=source_ns + 2_000_000,
        valid_until_ns=source_ns + 50_000_000,
        q_enu_from_flu_des_xyzw=(0.0, 0.0, 0.0, 1.0),
        collective_thrust_n=6.57,
    )


def test_rt1_fixed_size_frames_round_trip() -> None:
    state = rt1.StateReferenceFrame(
        run_id="run-rt1",
        sequence=7,
        source_stamp_ns=1_000_000_000,
        receive_monotonic_ns=1_001_000_000,
        valid_until_ns=1_050_000_000,
        armed=True,
        state_valid=True,
        reference_valid=True,
        values=tuple(float(index) for index in range(24)),
    )
    assert rt1.StateReferenceFrame.unpack(state.pack()) == state
    command = rt1_command(7, source_ns=1_000_000_000)
    assert rt1.CommandFrame.unpack(command.pack()) == command

    assert rt1.HEADER.size == 104
    assert rt1.STATE_REFERENCE_VALUES.size == 192
    assert rt1.COMMAND_VALUES.size == 48
    header = (ROOT / "Models/MoSimQuadrotorModel/Deployment/Resources/Include/mosim_mworks_live_rt1_bridge.h").read_text(
        encoding="utf-8"
    )
    assert "#pragma pack(push, 1)" in header
    assert "double values[24]" in header
    assert "MOSIM_RT1_PORT 49020u" in header
    model_200 = (ROOT / "Models/MoSimQuadrotorModel/Deployment/RT1OfficialPidShadow200Hz.mo").read_text(encoding="utf-8")
    assert "final parameter Real samplePeriod=0.005" in model_200
    assert "mosim_mworks_live_rt1_exchange_official_pid" in model_200
    assert "MOSIM_RT1_MAX_DRAIN 512" in header
    assert "for (index = 0; index < MOSIM_RT1_MAX_DRAIN; ++index)" in header
    assert "mosim_rt1_compute_and_send_official_pid" in header
    assert "Drain bounded backlog, then control from the freshest state only" in header
    assert "latest_state = state;" in header
    assert "if (have_latest && mosim_rt1_compute_and_send_official_pid" in header
    assert "++(*sent_frames);" in header
    assert "return processed;" in header
    assert "coalescedFrames" in model_200
    assert "Interval=0.005" in model_200
    assert "mosim_mworks_live_request_1ms_timer_resolution" in model_200
    assert "when initial() then" in model_200

    runtime = (ROOT / "Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    assert 'if [[ "${rt1_rate}" == "200" ]]; then\n    rt1_status_rate_hz="0.5"' in runtime
    assert 'MWORKS_LIVE_MWSOLVER_PRIORITY:-High' in runtime


def test_rt1_arbiter_requires_ground_ready_activation() -> None:
    arbiter = rt1.ControlOwnerArbiter("run-rt1")
    arbiter.enable_shadow()
    arbiter.mark_ready()
    try:
        arbiter.activate(airborne=True)
    except ValueError as exc:
        assert str(exc) == "airborne_backend_switch_forbidden"
    else:
        raise AssertionError("airborne activation must be rejected")
    arbiter.activate(airborne=False)
    assert arbiter.state == rt1.ControlState.ACTIVE


def test_rt1_arbiter_falls_back_after_three_consecutive_deadline_misses() -> None:
    arbiter = rt1.ControlOwnerArbiter("run-rt1")
    arbiter.enable_shadow()
    arbiter.mark_ready()
    arbiter.activate(airborne=False)
    base = 1_000_000_000
    for sequence in range(3):
        command = rt1_command(sequence, source_ns=base + sequence * 20_000_000)
        command = rt1.CommandFrame(
            **{
                **command.__dict__,
                "produced_monotonic_ns": command.source_stamp_ns + 11_000_000,
            }
        )
        decision = arbiter.observe(
            command,
            now_ns=command.source_stamp_ns + 12_000_000,
            latest_state_sequence=sequence,
        )
    assert not decision.accepted
    assert decision.reason_code == "consecutive_deadline_miss"
    assert arbiter.state == rt1.ControlState.FALLBACK_HOVER


def test_rt1_arbiter_falls_back_when_active_command_stream_stales() -> None:
    arbiter = rt1.ControlOwnerArbiter("run-rt1", stale_ms=50.0)
    arbiter.enable_shadow()
    arbiter.mark_ready()
    arbiter.activate(airborne=False)
    assert arbiter.observe_timeout(now_ns=1_049_000_000, last_command_receive_ns=1_000_000_000) == rt1.ControlState.ACTIVE
    assert arbiter.observe_timeout(now_ns=1_051_000_000, last_command_receive_ns=1_000_000_000) == rt1.ControlState.FALLBACK_HOVER


def test_rt1_arbiter_rejects_stale_or_wrong_run_without_switching_shadow_owner() -> None:
    arbiter = rt1.ControlOwnerArbiter("run-rt1")
    arbiter.enable_shadow()
    stale = rt1_command(0, source_ns=1_000_000_000)
    decision = arbiter.observe(stale, now_ns=1_060_000_000, latest_state_sequence=0)
    assert decision.reason_code == "output_stale"
    assert arbiter.state == rt1.ControlState.SHADOW


def test_rt1_arbiter_accepts_bounded_pipeline_lag_but_rejects_future_state() -> None:
    arbiter = rt1.ControlOwnerArbiter("run-rt1")
    arbiter.enable_shadow()
    delayed = rt1_command(0, source_ns=1_000_000_000)
    accepted = arbiter.observe(delayed, now_ns=1_005_000_000, latest_state_sequence=4)
    assert accepted.accepted is True
    future = rt1.CommandFrame(**{**rt1_command(1, source_ns=2_000_000_000).__dict__, "state_sequence": 8})
    rejected = arbiter.observe(future, now_ns=2_005_000_000, latest_state_sequence=7)
    assert rejected.accepted is False
    assert rejected.reason_code == "state_sequence_ahead"
    wrong_run = rt1_command(1, source_ns=2_000_000_000, run_id="other-run")
    decision = arbiter.observe(wrong_run, now_ns=2_002_000_000, latest_state_sequence=1)
    assert decision.reason_code == "run_id_mismatch"
    assert arbiter.state == rt1.ControlState.SHADOW


def test_rt0_gate_binds_50_and_200hz_to_separate_models_and_contracts() -> None:
    gate = (ROOT / "Scripts/mworks_live/run_rt0_sysplorer_gate.py").read_text(encoding="utf-8")
    assert '"MoSimQuadrotorModel.Deployment.RT0RealtimeProbe50Hz"' in gate
    assert '"MoSimQuadrotorModel.Deployment.RT0RealtimeProbe200Hz"' in gate
    assert "mworks_live_attitude_thrust_contract_v3_candidate_200hz.json" in gate
    assert '"model_source_sha256"' in gate
    assert '"--rate-hz"' in gate


def test_rt1_runtime_uses_unique_final_publisher_and_ground_activation_gate() -> None:
    runner = (ROOT / "Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    px4_gate = (ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")
    adapter = (ROOT / "Scripts/mworks_live/ros1_rt1_adapter.py").read_text(encoding="utf-8")
    catalog = json.loads((ROOT / "Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8"))
    entries = catalog["runtime_profiles"]
    assert any(entry["operation_id"] == "mworks_live_official_pid_hover_50hz" for entry in entries)
    assert not any(
        "candidate" in profile_id
        for entry in entries
        for profile_id in entry["experiment_profile_ids"]
    )
    assert 'PX4CTRL_ATTITUDE_OUTPUT_TOPIC="${PX4CTRL_ATTITUDE_OUTPUT_TOPIC:-/uav1/mavros/setpoint_raw/attitude}"' in px4_gate
    assert 'PX4CTRL_PRE_MISSION_OWNER_TOPIC' in px4_gate
    assert 'MWORKS_LIVE_ACTIVE_TAKEOVER:-false' in runner
    assert 'rt1_authority_args+=(--allow-active-takeover --auto-activate-ground)' in runner
    assert '"authority_mode": "active_takeover_requested"' in runner
    assert 'PX4CTRL_PRE_MISSION_OWNER_STATE="SHADOW"' in runner
    assert 'MWORKS_LIVE_SHADOW_HOLD_S:-300' in runner
    assert 'wait_for_runtime_ready' in runner
    assert 'runtime_ready_before_rt1_start' in runner
    assert 'mworks_live_official_pid_hover_200hz)' in runner
    assert '--allow-ground-hold-reference' in runner
    assert 'if self.ready():\n            self.send_state_reference(now_ns)\n        self.receive_commands(now_ns)' in adapter


def test_rt1_transport_rates_exclude_runtime_startup_wait() -> None:
    adapter = (ROOT / "Scripts/mworks_live/ros1_rt1_adapter.py").read_text(encoding="utf-8")
    assert "self.first_send_ns" in adapter
    assert '"startup_wait_before_first_state_s"' in adapter
    assert '"state_measurement_window_s"' in adapter
    assert '"command_measurement_window_s"' in adapter
    assert "self.sent_frame_count / state_window_s" in adapter


def test_rt1_adapter_uses_wall_clock_scheduler_under_gazebo_sim_time() -> None:
    adapter = (ROOT / "Scripts/mworks_live/ros1_rt1_adapter.py").read_text(encoding="utf-8")
    assert "def wall_clock_tick_loop" in adapter
    assert 'name="mworks-live-wall-clock-tick"' in adapter
    assert "next_tick = time.monotonic()" in adapter
    assert "rospy.Timer(" not in adapter


def test_rt1_adapter_bounds_receive_work_and_downsamples_success_trace() -> None:
    adapter = (ROOT / "Scripts/mworks_live/ros1_rt1_adapter.py").read_text(encoding="utf-8")
    runner = (ROOT / "Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    assert "processed < self.args.max_receive_batch" in adapter
    assert "not decision.accepted or receive_ns - self.last_accepted_trace_ns" in adapter
    assert 'parser.add_argument("--trace-sample-rate-hz"' in adapter
    assert 'export REVIEW_START_FASTLIO="false"' in runner
    assert 'export REVIEW_START_OCCUPANCY_NODE="false"' in runner


def test_rt1_cpp_adapter_freezes_wire_sizes_and_shadow_first_contract() -> None:
    adapter = (ROOT / "Scripts/mworks_live/ros1_rt1_adapter_cpp.cpp").read_text(encoding="utf-8")
    assert 'static_assert(sizeof(StateReferenceWire) == 296' in adapter
    assert 'static_assert(sizeof(CommandWire) == 152' in adapter
    assert 'adapter_backend\\\": \\\"cpp_wall_clock_v1' in adapter
    assert 'State state_=State::SHADOW' in adapter
    assert 'c.header.related_sequence>sequence_-1' in adapter
    assert 'clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME' in adapter
    assert 'command_age_max_ms_=std::max(command_age_max_ms_,age)' in adapter
    assert 'reason=="output_stale"' in adapter
    assert 'command_age_ms' in adapter
    assert r'\"command_age_ms_max\"' in adapter
    assert r'\"rejection_counts\"' in adapter


def test_200hz_runtime_selects_wall_clock_cpp_rt1_backend() -> None:
    gate = (ROOT / "Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    assert 'MWORKS_LIVE_RT1_BACKEND:-auto' in gate
    assert 'if [[ "${rt1_rate}" == "200" ]]' in gate
    assert 'rt1_backend="cpp_wall_clock_v1"' in gate
    assert 'build_ros1_rt1_adapter_cpp.sh' in gate
    assert 'cpp_gazebo_step_v1' in gate
    assert '--time-mode gazebo_step --gazebo-steps-per-command 5 --gazebo-step-size-ns 1000000' in gate
    assert 'MWORKS_LIVE_VEHICLE:-sunray150' in gate
    assert 'export SUNRAY_STRIP_PX4_MODEL_PATH="false"' in gate
    assert 'set_mwsolver_priority.ps1' in gate
    priority = (ROOT / "Scripts/mworks_live/set_mwsolver_priority.ps1").read_text(encoding="utf-8")
    assert '[string]$PriorityClass = "Normal"' in priority
    assert '$solver.PriorityClass = $PriorityClass' in priority
    assert 'MWORKS_LIVE_MWSOLVER_PRIORITY:-High' in gate
    assert 'mwsolver_priority.v1' in priority
    assert 'MWORKS_LIVE_WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world' in gate
    basic_gate = (ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")
    assert 'vehicle:="${VEHICLE}" gui:="${GUI}" rviz_enable:=false' in basic_gate


def test_200hz_live_model_keeps_scheduler_aligned_and_reserves_gate_window() -> None:
    model = (ROOT / "Models/MoSimQuadrotorModel/Deployment/RT1OfficialPidShadow200Hz.mo").read_text(encoding="utf-8")
    assert "final parameter Real samplePeriod=0.005" in model
    assert "StopTime=900" in model
    assert "Interval=0.005" in model


def test_rt1_owner_wait_uses_wall_clock_when_gazebo_clock_stops() -> None:
    waiter = (ROOT / "Scripts/mworks_live/wait_for_rt1_control_state.py").read_text(encoding="utf-8")
    assert "started = time.monotonic()" in waiter
    assert "time.sleep(0.05)" in waiter
    assert "rospy.Rate(" not in waiter


def test_rt1_shadow_analyzer_rejects_long_run_with_solver_stall() -> None:
    status = {
        "run_id": "run-stalled",
        "adapter_backend": "cpp_wall_clock_v1",
        "state": "SHADOW",
        "shadow_only": True,
        "command_age_ms_max": 572.016,
        "rejection_counts": {"output_stale": 6},
        "transport": {
            "process_window_s": 358.5,
            "state_send_rate_hz": 199.24,
            "command_receive_rate_hz": 179.53,
            "send_error_count": 0,
            "missing_command_count": 0,
            "duplicate_command_count": 0,
            "out_of_order_command_count": 0,
        },
    }
    result = rt1_shadow_analyzer.analyze(status)
    assert result["accepted"] is False
    assert result["flight_entry_allowed"] is False
    assert {failure["reason_code"] for failure in result["failures"]} >= {
        "command_rate_below_minimum",
        "command_age_exceeded",
        "stale_output_observed",
    }


def test_rt1_shadow_analyzer_accepts_synchronized_shadow() -> None:
    status = {
        "run_id": "run-synchronized",
        "adapter_backend": "gazebo_sim_step_v1",
        "state": "SHADOW",
        "shadow_only": True,
        "command_age_ms_max": 8.5,
        "rejection_counts": {"output_stale": 0},
        "transport": {
            "process_window_s": 300.1,
            "state_send_rate_hz": 199.9,
            "command_receive_rate_hz": 199.8,
            "send_error_count": 0,
            "missing_command_count": 0,
            "duplicate_command_count": 0,
            "out_of_order_command_count": 0,
        },
    }
    result = rt1_shadow_analyzer.analyze(status)
    assert result["accepted"] is True
    assert result["flight_entry_allowed"] is True
    assert result["failures"] == []


def test_gazebo_step_probe_is_bounded_and_cleans_up() -> None:
    probe = (ROOT / "Scripts/mworks_live/probe_gazebo_classic_stepping.sh").read_text(
        encoding="utf-8"
    )
    assert "gzserver --pause" in probe
    assert "gz world --multi-step 5" in probe
    assert "gz world --multi-step 10" in probe
    assert "trap cleanup EXIT" in probe
    assert "gz topic -e" in probe


def test_cpp_adapter_has_ground_only_gazebo_step_mode() -> None:
    adapter = (ROOT / "Scripts/mworks_live/ros1_rt1_adapter_cpp.cpp").read_text(
        encoding="utf-8"
    )
    builder = (ROOT / "Scripts/mworks_live/build_ros1_rt1_adapter_cpp.sh").read_text(
        encoding="utf-8"
    )
    assert 'args.time_mode != "wall_clock" && args.time_mode != "gazebo_step"' in adapter
    assert 'gazebo_step v1 is ground shadow only' in adapter
    assert 'Advertise<gazebo::msgs::WorldControl>("~/world_control")' in adapter
    assert 'message.set_multi_step(static_cast<uint32_t>(args_.gazebo_steps_per_command))' in adapter
    assert 'bootstrapGazeboStep(now_ns, sim_ns)' in adapter
    assert '"bootstrap_step_requested"' in adapter
    assert '"bootstrap_state_timeout"' in adapter
    assert r'\"bootstrap_complete\"' in adapter
    assert r'\"bootstrap_step_request_count\"' in adapter
    assert r'\"bootstrap_step_completion_count\"' in adapter
    assert '"~/world_stats", &Adapter::onWorldStats, this' in adapter
    assert 'sim_ns >= target_sim_time_ns_' in adapter
    assert 'reason="sync_state_sequence_mismatch"' in adapter
    assert 'cpp_gazebo_step_v1' in adapter
    assert 'pkg-config --cflags --libs gazebo' in builder
    responder = (
        ROOT / "Scripts/mworks_live/run_rt1_synthetic_mworks_responder.py"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "Scripts/mworks_live/run_gazebo_step_synthetic_gate.sh"
    ).read_text(encoding="utf-8")
    assert "python_synthetic_protocol_test_only" in responder
    assert "--stall-duration-s 0.3" in gate
    assert "--time-mode gazebo_step" in gate
    assert "analyze_gazebo_step_synthetic_gate.py" in gate
    assert "trap cleanup EXIT" in gate
