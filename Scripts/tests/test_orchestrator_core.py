from __future__ import annotations

import json
import time
from pathlib import Path

from src.orchestration import MoSimOrchestrator


class FakeRuntimeBackend:
    backend_id = "test_backend"

    def __init__(self) -> None:
        self.attach_calls = 0
        self.detach_calls = 0

    def start(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_started", "pid": 123}

    def stop(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_stopped"}

    def reset(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_reset"}

    def apply_injection(self, manifest, command):
        return {"accepted": True, "reason_code": "test_injection_applied", "applied_value": command["value"]}

    def close_all_rviz(self, manifest):
        return {"accepted": True, "reason_code": "rviz_sessions_closed", "closed_count": 2}

    def start_ue_recording(self, manifest):
        return {
            "accepted": True,
            "reason_code": "ue_recording_started",
            "output_path": f"Results/ui_platform/{manifest['run_id']}.mp4",
        }

    def stop_ue_recording(self, manifest):
        return {
            "accepted": True,
            "reason_code": "ue_recording_stopped",
            "output_path": manifest["recording"]["output_path"],
        }

    def attach_display(self, session):
        self.attach_calls += 1
        return {"accepted": True, "reason_code": "display_attached"}

    def detach_display(self, session):
        self.detach_calls += 1
        return {"accepted": True, "reason_code": "display_detached"}


class StartingRuntimeBackend(FakeRuntimeBackend):
    def start(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_starting", "lifecycle_state": "starting"}

    def poll(self, manifest):
        return {"lifecycle_state": "running", "reason_code": "runtime_ready"}


class FailingDetachBackend(FakeRuntimeBackend):
    def detach_display(self, session):
        self.detach_calls += 1
        return {"accepted": False, "reason_code": "display_detach_failed"}


class ModelOperationBackend(FakeRuntimeBackend):
    def __init__(self) -> None:
        super().__init__()
        self.model_starts = []
        self.model_state = "running"

    def start_model_operation(self, manifest, *, action, operation_id):
        self.model_starts.append((manifest["run_id"], action, operation_id))
        return {"accepted": True, "reason_code": "model_operation_started", "process_id": 4321}

    def poll_model_operation(self, manifest, *, action, operation_id):
        if self.model_state == "completed":
            return {
                "state": "completed",
                "reason_code": f"{action}_completed",
                "result_gate": f"mworks/{action}/result.json",
            }
        if self.model_state == "failed":
            return {"state": "failed", "reason_code": f"{action}_failed"}
        return {"state": "running", "reason_code": "mworks_operation_running"}


PROFILE = "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json"
THREE_UAV_PROFILE = "Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json"
MWORKS_LIVE_PROFILE = "Config/profiles/experiments/mworks_live_official_pid_hover_50hz_v2.json"
MWORKS_LIVE_200HZ_PROFILE = "Config/profiles/experiments/mworks_live_official_pid_hover_200hz_v1.json"
FUEL_FIXED64_PROFILE = "Config/profiles/experiments/factory_l2_fuel_fixed64_exploration_v1.json"


def passing_connection_preflight(**endpoint):
    return {
        "schema": "mosim.mworks_live_connection_preflight.v1",
        "accepted": True,
        "reason_code": "connection_preflight_passed",
        "resolved_target_addresses": ["127.0.0.1"],
        "rt1": {
            "reachable": True,
            "protocol_version": 1,
            "rtt_p95_ms": 1.25,
            "measured_payload_bytes_per_s": 44800.0,
            "estimated_ip_udp_wire_bytes_per_s": 50400.0,
        },
        "endpoint_echo": endpoint,
    }


def write_disarmed_telemetry(run_root: Path, run_id: str, *, vehicle_count: int = 1) -> None:
    run_dir = run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "telemetry.json").write_text(
        json.dumps(
            {
                "schema": "mosim.runtime_telemetry.v2",
                "run_id": run_id,
                "timestamp": time.time(),
                "vehicle_count": vehicle_count,
                "vehicles": [
                    {"vehicle_id": f"uav{index}", "state": {"connected": True, "armed": False}}
                    for index in range(1, vehicle_count + 1)
                ],
            }
        ),
        encoding="utf-8",
    )


def test_fuel_fixed64_profile_prepares_for_px4ctrl_single_uav(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    response = orchestrator.prepare_run(
        request_id="prepare-fuel-fixed64",
        profile_path=FUEL_FIXED64_PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
    )
    assert response["accepted"] is True
    assert response["manifest"]["experiment_profile_id"] == "factory_l2_fuel_fixed64_exploration_v1"
    assert response["manifest"]["controller_id"] == "px4ctrl"
    assert response["manifest"]["scenario_path"] == "Config/scenarios/ui/factory_l2_fuel_fixed64_exploration.json"
    assert response["manifest"]["scenario_hash"]
    scenario = response["manifest"]["scenario_snapshot"]
    assert scenario["exploration_boundary"]["min_x_m"] == -42.575025
    assert scenario["exploration_boundary"]["max_x_m"] == 21.424975
    assert scenario["mission"] == {
        "type": "fuel_single_exploration",
        "duration_s": 300,
        "random_seed": 1,
        "max_velocity_mps": 2.0,
        "max_acceleration_mps2": 1.5,
        "px4ctrl_core_profile": "l1_awff",
    }


def test_three_uav_profile_freezes_formation_target_in_run_manifest(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    response = orchestrator.prepare_run(
        request_id="prepare-formation",
        profile_path=THREE_UAV_PROFILE,
        controller_id="px4ctrl",
        vehicle_count=3,
    )
    assert response["accepted"] is True
    scenario = response["manifest"]["scenario_snapshot"]
    assert scenario["formation"]["target_center_xy_m"] == [-16.679266719908025, -8.0868185505691]
    assert scenario["formation"]["expected_min_pair_distance_m"] == 1.5


def test_prepare_rejects_a_second_run_until_active_runtime_stops(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    first = orchestrator.prepare_run(
        request_id="prepare-first",
        profile_path=PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
    )
    first_run_id = first["run_id"]
    assert orchestrator.start_run(request_id="start-first", run_id=first_run_id)["accepted"] is True

    rejected = orchestrator.prepare_run(
        request_id="prepare-second",
        profile_path=FUEL_FIXED64_PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
    )
    assert rejected["accepted"] is False
    assert rejected["reason_code"] == "active_run_must_stop_before_prepare"
    assert rejected["run_id"] == first_run_id
    assert orchestrator.active_run_id == first_run_id

    write_disarmed_telemetry(tmp_path, first_run_id)
    assert orchestrator.stop_run(request_id="stop-first", run_id=first_run_id)["accepted"] is True
    second = orchestrator.prepare_run(
        request_id="prepare-second-after-stop",
        profile_path=FUEL_FIXED64_PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
    )
    assert second["accepted"] is True
    assert second["run_id"] != first_run_id


def test_safe_stop_is_idempotent_and_requires_matching_terminal_ack(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare-safe-stop",
        profile_path=FUEL_FIXED64_PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
    )
    run_id = prepared["run_id"]
    assert orchestrator.start_run(request_id="start-safe-stop", run_id=run_id)["accepted"] is True

    requested = orchestrator.request_safe_stop(request_id="safe-stop-1", run_id=run_id)
    operation_id = requested["operation"]["operation_id"]
    assert requested["accepted"] is True
    assert requested["operation"]["state"] == "running"
    request_packet = json.loads((tmp_path / run_id / "safe_stop" / "request.json").read_text())
    assert request_packet["operation_id"] == operation_id

    reused = orchestrator.request_safe_stop(request_id="safe-stop-2", run_id=run_id)
    assert reused["reason_code"] == "safe_stop_request_reused"
    assert reused["operation"]["operation_id"] == operation_id

    ack_path = tmp_path / run_id / "safe_stop" / "ack.json"
    ack = {
        "schema": "mosim.safe_stop.ack.v1",
        "run_id": run_id,
        "request_id": "wrong-request",
        "operation_id": operation_id,
        "stage": "completed",
        "progress_percent": 100,
        "terminal": True,
        "accepted": True,
    }
    ack_path.write_text(json.dumps(ack), encoding="utf-8")
    pending = orchestrator.get_operation_progress(
        request_id="poll-wrong-ack", run_id=run_id, operation_id=operation_id
    )
    assert pending["operation"]["state"] == "running"

    ack["request_id"] = "safe-stop-1"
    ack["reason_code"] = "safe_stop_completed"
    ack_path.write_text(json.dumps(ack), encoding="utf-8")
    completed = orchestrator.get_operation_progress(
        request_id="poll-complete", run_id=run_id, operation_id=operation_id
    )
    assert completed["operation"]["state"] == "completed"
    assert completed["operation"]["reason_code"] == "safe_stop_completed"
    assert orchestrator._get_manifest(run_id)["safe_stop"]["stage"] == "completed"
    stopped = orchestrator.stop_run(request_id="stop-after-safe-stop", run_id=run_id)
    assert stopped["accepted"] is True
    assert stopped["stop_evidence"]["source"] == "mission_adapter_ack"


def test_runtime_stop_rejects_armed_or_incomplete_vehicle_state(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare-stop-gate",
        profile_path=THREE_UAV_PROFILE,
        controller_id="px4ctrl",
        vehicle_count=3,
    )
    run_id = prepared["run_id"]
    assert orchestrator.start_run(request_id="start-stop-gate", run_id=run_id)["accepted"] is True

    write_disarmed_telemetry(tmp_path, run_id, vehicle_count=2)
    incomplete = orchestrator.stop_run(request_id="stop-incomplete", run_id=run_id)
    assert incomplete["accepted"] is False
    assert incomplete["reason_code"] == "runtime_stop_vehicle_state_incomplete"

    telemetry_path = tmp_path / run_id / "telemetry.json"
    telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
    telemetry["vehicle_count"] = 3
    telemetry["vehicles"].append(
        {"vehicle_id": "uav3", "state": {"connected": True, "armed": True}}
    )
    telemetry["timestamp"] = time.time()
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    armed = orchestrator.stop_run(request_id="stop-armed", run_id=run_id)
    assert armed["accepted"] is False
    assert armed["reason_code"] == "runtime_stop_rejected_vehicle_armed"


def test_starting_runtime_requires_fresh_disarm_evidence_before_stop(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=StartingRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare-starting-stop-gate",
        profile_path=PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
    )
    run_id = prepared["run_id"]
    started = orchestrator.start_run(request_id="start-starting-stop-gate", run_id=run_id)
    assert started["reason_code"] == "run_starting"

    missing = orchestrator.stop_run(request_id="stop-starting-missing", run_id=run_id)
    assert missing["accepted"] is False
    assert missing["reason_code"] == "runtime_stop_requires_fresh_disarm_evidence"

    write_disarmed_telemetry(tmp_path, run_id)
    telemetry_path = tmp_path / run_id / "telemetry.json"
    telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
    telemetry["vehicles"][0]["state"]["armed"] = True
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    armed = orchestrator.stop_run(request_id="stop-starting-armed", run_id=run_id)
    assert armed["accepted"] is False
    assert armed["reason_code"] == "runtime_stop_rejected_vehicle_armed"

    telemetry["timestamp"] = time.time()
    telemetry["vehicles"][0]["state"]["armed"] = False
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    disarmed = orchestrator.stop_run(request_id="stop-starting-disarmed", run_id=run_id)
    assert disarmed["accepted"] is True
    assert disarmed["stop_evidence"]["source"] == "runtime_sidecar"


def test_real_connection_preflight_module_import_is_self_contained(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path)
    result = orchestrator._invoke_connection_preflight(
        target_host="bad host",
        rt1_udp_port=49020,
        ros_master_uri="",
        local_advertised_ip="auto",
        requested_rate_hz=200,
        timeout_s=0.01,
        sample_count=1,
    )
    assert result["accepted"] is False
    assert result["reason_code"] == "invalid_target_host"


def test_capability_gates_reject_unaccepted_controller_and_scale(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path)
    controller = orchestrator.validate_experiment_profile(
        request_id="controller", profile_path=PROFILE, controller_id="nmpc_outer", vehicle_count=3
    )
    assert controller["accepted"] is False
    assert controller["reason_code"] == "controller_runtime_gate_pending"
    scale = orchestrator.validate_experiment_profile(
        request_id="scale", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=5
    )
    assert scale["accepted"] is False
    assert scale["reason_code"] == "vehicle_scale_gate_pending"


def test_mworks_live_200hz_transport_does_not_bypass_rt0_gate(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(
        run_root=tmp_path,
        connection_preflight_runner=passing_connection_preflight,
    )
    preflight = orchestrator.preflight_connection(
        request_id="preflight-200",
        profile_path=MWORKS_LIVE_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
        target_host="127.0.0.1",
        rt1_udp_port=49020,
        ros_master_uri="http://127.0.0.1:11311",
        requested_rate_hz=200,
    )

    assert preflight["accepted"] is False
    assert preflight["reason_code"] == "requested_rate_unvalidated"
    assert preflight["preflight"]["transport_ok"] is True
    assert preflight["preflight"]["rate_validated"] is False


def test_mworks_live_published_200hz_profile_passes_rate_gate(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(
        run_root=tmp_path,
        connection_preflight_runner=passing_connection_preflight,
    )
    preflight = orchestrator.preflight_connection(
        request_id="preflight-published-200",
        profile_path=MWORKS_LIVE_200HZ_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
        target_host="127.0.0.1",
        rt1_udp_port=49020,
        ros_master_uri="http://127.0.0.1:11311",
        requested_rate_hz=200,
    )

    assert preflight["accepted"] is True
    assert preflight["preflight"]["transport_ok"] is True
    assert preflight["preflight"]["rate_validated"] is True


def test_mworks_live_prepare_freezes_accepted_connection_preflight(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(
        run_root=tmp_path,
        connection_preflight_runner=passing_connection_preflight,
    )
    missing = orchestrator.prepare_run(
        request_id="prepare-missing",
        profile_path=MWORKS_LIVE_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
    )
    assert missing["accepted"] is False
    assert missing["reason_code"] == "connection_preflight_required"

    preflight = orchestrator.preflight_connection(
        request_id="preflight-50",
        profile_path=MWORKS_LIVE_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
        target_host="127.0.0.1",
        rt1_udp_port=49020,
        ros_master_uri="http://127.0.0.1:11311",
        requested_rate_hz=50,
    )
    assert preflight["accepted"] is True

    prepared = orchestrator.prepare_run(
        request_id="prepare-accepted",
        profile_path=MWORKS_LIVE_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
        connection_preflight_id=preflight["preflight"]["preflight_id"],
    )
    assert prepared["accepted"] is True
    frozen = prepared["manifest"]["mworks_live_connection"]
    assert frozen["selected_rate_hz"] == 50
    assert frozen["preflight_id"] == preflight["preflight"]["preflight_id"]
    assert frozen["preflight_result_hash"] == preflight["preflight"]["preflight_result_hash"]


def test_mworks_live_prepare_rejects_tampered_preflight(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(
        run_root=tmp_path,
        connection_preflight_runner=passing_connection_preflight,
    )
    preflight = orchestrator.preflight_connection(
        request_id="preflight-tamper",
        profile_path=MWORKS_LIVE_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
        target_host="127.0.0.1",
        rt1_udp_port=49020,
        ros_master_uri="http://127.0.0.1:11311",
        requested_rate_hz=50,
    )
    preflight_id = preflight["preflight"]["preflight_id"]
    packet_path = tmp_path / "_preflight" / f"{preflight_id}.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["endpoint"]["rt1_udp_port"] = 49999
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    prepared = orchestrator.prepare_run(
        request_id="prepare-tampered",
        profile_path=MWORKS_LIVE_PROFILE,
        controller_id="official_pid",
        vehicle_count=1,
        connection_preflight_id=preflight_id,
    )
    assert prepared["accepted"] is False
    assert prepared["reason_code"] == "connection_preflight_identity_mismatch"


def test_profile_must_match_controller_and_vehicle_count(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path)
    controller = orchestrator.validate_experiment_profile(
        request_id="controller-profile", profile_path=PROFILE, controller_id="cascade_pid", vehicle_count=1
    )
    assert controller["accepted"] is False
    assert controller["reason_code"] == "profile_controller_mismatch"
    vehicle_count = orchestrator.validate_experiment_profile(
        request_id="vehicle-profile", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=3
    )
    assert vehicle_count["accepted"] is False
    assert vehicle_count["reason_code"] == "profile_vehicle_count_mismatch"

    accepted_three = orchestrator.validate_experiment_profile(
        request_id="three-uav", profile_path=THREE_UAV_PROFILE, controller_id="px4ctrl", vehicle_count=3
    )
    assert accepted_three["accepted"] is True


def test_unconfigured_backend_cannot_claim_runtime_start(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path)
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    assert prepared["accepted"] is True
    started = orchestrator.start_run(request_id="start", run_id=prepared["run_id"])
    assert started["accepted"] is False
    assert started["reason_code"] == "runtime_backend_unconfigured"
    assert prepared["manifest"]["runtime_started"] is False


def test_injection_refreshes_starting_run_before_rejecting_it(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=StartingRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    run_id = prepared["run_id"]
    assert orchestrator.start_run(request_id="start", run_id=run_id)["reason_code"] == "run_starting"
    injected = orchestrator.apply_injection(
        request_id="inject", run_id=run_id, command={"target": "wind_speed_mps", "value": 2.0}
    )
    assert injected["accepted"] is True
    assert orchestrator.manifests[run_id]["lifecycle_state"] == "running"


def test_full_offline_contract_with_explicit_test_backend(tmp_path: Path) -> None:
    evidence = tmp_path / "review.png"
    evidence.write_bytes(b"evidence")
    orchestrator = MoSimOrchestrator(run_root=tmp_path / "runs", backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare",
        profile_path=PROFILE,
        controller_id="px4ctrl",
        vehicle_count=1,
        parameter_set={"wind_speed_mps": 2.0},
    )
    run_id = prepared["run_id"]
    started = orchestrator.start_run(request_id="start", run_id=run_id)
    assert started["accepted"] is True
    assert started["profile_hash"] == prepared["profile_hash"]

    injection = orchestrator.apply_injection(
        request_id="inject", run_id=run_id, command={"target": "wind_speed_mps", "value": 3.0}
    )
    assert injection["requested_value"] == injection["applied_value"] == 3.0

    display = orchestrator.prepare_display_session(
        request_id="display", run_id=run_id, displays=["rviz_pointcloud", "unreal"]
    )
    session_id = display["session"]["session_id"]
    assert orchestrator.attach_display(request_id="attach", session_id=session_id)["accepted"] is True

    evidence_path = Path("Results") / "ui_platform" / "test-evidence.png"
    project_evidence = Path(__file__).resolve().parents[2] / evidence_path
    project_evidence.parent.mkdir(parents=True, exist_ok=True)
    project_evidence.write_bytes(evidence.read_bytes())
    try:
        assert orchestrator.capture_display_evidence(
            request_id="capture", run_id=run_id, session_id=session_id, evidence_path=str(evidence_path)
        )["accepted"] is True
        outside = orchestrator.capture_display_evidence(
            request_id="outside", run_id=run_id, session_id=session_id, evidence_path=str(evidence)
        )
        assert outside["accepted"] is False
        assert outside["reason_code"] == "display_evidence_outside_project"
    finally:
        project_evidence.unlink(missing_ok=True)

    assert orchestrator.open_model_context(request_id="model", run_id=run_id)["accepted"] is True
    write_disarmed_telemetry(tmp_path / "runs", run_id)
    assert orchestrator.stop_run(request_id="stop", run_id=run_id)["accepted"] is True
    assert orchestrator.reset_run(request_id="reset", run_id=run_id)["accepted"] is True

    manifest = json.loads((tmp_path / "runs" / run_id / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["lifecycle_state"] == "ready"
    assert manifest["runtime_started"] is False
    assert manifest["vehicle_count"] == 1
    assert manifest["experiment_profile_hash"]


def test_every_response_contains_frontend_contract_fields(tmp_path: Path) -> None:
    response = MoSimOrchestrator(run_root=tmp_path).get_run_state(request_id="missing", run_id="absent")
    assert {"request_id", "accepted", "reason_code", "run_id", "profile_hash", "timestamp"} <= response.keys()


def test_controller_catalog_is_dynamic_and_explains_disabled_entries(tmp_path: Path) -> None:
    response = MoSimOrchestrator(run_root=tmp_path).list_controllers(request_id="controllers")
    assert response["accepted"] is True
    by_id = {item["module_id"]: item for item in response["controllers"]}
    assert by_id["px4ctrl"]["enabled"] is True
    assert by_id["trained_neural_residual"]["enabled"] is False
    assert by_id["trained_neural_residual"]["disabled_reason"]
    assert response["registry_hash"]


def test_agent_proposes_registered_task_without_flight_authority(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path)
    response = orchestrator.propose_operator_task(request_id="agent", prompt="请运行三机编队避障")
    assert response["accepted"] is True
    proposal = response["proposal"]
    assert proposal["profile_id"] == "factory_l2_three_uav_swarm_formation_v1"
    assert proposal["controller_id"] == "px4ctrl"
    assert proposal["vehicle_count"] == 3
    assert proposal["requires_user_confirmation"] is True
    assert proposal["may_start_flight"] is False
    assert proposal["next_action"] == "confirm_then_prepare_run"


def test_agent_rejects_unknown_or_empty_intent(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path)
    empty = orchestrator.propose_operator_task(request_id="empty", prompt="  ")
    unknown = orchestrator.propose_operator_task(request_id="unknown", prompt="帮我处理一下")
    assert empty["reason_code"] == "agent_prompt_empty"
    assert unknown["reason_code"] == "agent_intent_not_recognized"


def test_operation_progress_reaches_runtime_ready(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=StartingRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    started = orchestrator.start_run(request_id="start", run_id=prepared["run_id"])
    assert started["operation"]["state"] == "running"
    progress = orchestrator.get_operation_progress(
        request_id="poll",
        run_id=prepared["run_id"],
        operation_id=started["operation"]["operation_id"],
    )
    assert progress["operation"]["state"] == "completed"
    assert progress["operation"]["progress_percent"] == 100


def test_model_operations_are_run_owned_and_return_a_gate_packet(tmp_path: Path) -> None:
    backend = ModelOperationBackend()
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=backend)
    prepared = orchestrator.prepare_run(
        request_id="prepare-model",
        profile_path="Config/profiles/experiments/cascade_pid_figure8_generated_c_v1.json",
        controller_id="cascade_pid",
        vehicle_count=1,
    )
    run_id = prepared["run_id"]
    mil = orchestrator.run_mil(request_id="mil", run_id=run_id)
    assert mil["accepted"] is True
    assert mil["operation"]["max_attempts"] == 1
    backend.model_state = "completed"
    progress = orchestrator.get_operation_progress(
        request_id="poll-mil", run_id=run_id, operation_id=mil["operation"]["operation_id"]
    )
    assert progress["operation"]["state"] == "completed"

    backend.model_state = "running"
    codegen = orchestrator.generate_code(request_id="codegen", run_id=run_id)
    assert codegen["accepted"] is True
    backend.model_state = "completed"
    state = orchestrator.get_model_gate_state(request_id="gate", run_id=run_id)
    assert state["accepted"] is True
    assert state["packet"]["status"] == "passed"
    assert set(state["packet"]["passed_actions"]) == {"generate_code", "run_mil"}
    packet = orchestrator.get_result_packet(request_id="result", run_id=run_id)
    assert packet["accepted"] is True
    assert packet["packet"]["schema"] == "mosim.model_studio.gate_packet.v1"


def test_model_operation_failure_requires_manual_review_and_is_not_retried(tmp_path: Path) -> None:
    backend = ModelOperationBackend()
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=backend)
    prepared = orchestrator.prepare_run(
        request_id="prepare-model-fail",
        profile_path="Config/profiles/experiments/cascade_pid_figure8_generated_c_v1.json",
        controller_id="cascade_pid",
        vehicle_count=1,
    )
    operation = orchestrator.generate_code(request_id="codegen-fail", run_id=prepared["run_id"])["operation"]
    backend.model_state = "failed"
    progress = orchestrator.get_operation_progress(
        request_id="poll-codegen-fail",
        run_id=prepared["run_id"],
        operation_id=operation["operation_id"],
    )
    assert progress["operation"]["state"] == "failed"
    assert progress["operation"]["stage_id"] == "manual_confirmation_required"
    assert progress["operation"]["attempt"] == progress["operation"]["max_attempts"] == 1
    assert len(backend.model_starts) == 1


def test_recording_and_rviz_cleanup_are_owned_operations(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    run_id = prepared["run_id"]
    recording = orchestrator.start_ue_recording(request_id="record", run_id=run_id)
    assert recording["accepted"] is True
    assert recording["recording"]["active"] is True
    stopped = orchestrator.stop_ue_recording(request_id="stop-record", run_id=run_id)
    assert stopped["recording"]["active"] is False
    cleanup = orchestrator.close_all_rviz(request_id="rviz", run_id=run_id)
    assert cleanup["accepted"] is True
    assert cleanup["cleanup"]["closed_count"] == 2


def test_display_session_is_idempotent_and_recovers_after_restart(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    backend = FakeRuntimeBackend()
    orchestrator = MoSimOrchestrator(run_root=run_root, backend=backend)
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    run_id = prepared["run_id"]

    first = orchestrator.prepare_display_session(
        request_id="display-1", run_id=run_id, displays=["unreal", "rviz_pointcloud", "unreal"]
    )
    second = orchestrator.prepare_display_session(
        request_id="display-2", run_id=run_id, displays=["rviz_pointcloud", "unreal"]
    )
    session_id = first["session"]["session_id"]
    assert second["reason_code"] == "display_session_reused"
    assert second["session"]["session_id"] == session_id

    assert orchestrator.attach_display(request_id="attach-1", session_id=session_id)["accepted"] is True
    repeated_attach = orchestrator.attach_display(request_id="attach-2", session_id=session_id)
    assert repeated_attach["reason_code"] == "display_already_attached"
    assert backend.attach_calls == 1

    restarted_backend = FakeRuntimeBackend()
    restarted = MoSimOrchestrator(run_root=run_root, backend=restarted_backend)
    detached = restarted.detach_display(request_id="detach-1", session_id=session_id)
    assert detached["reason_code"] == "display_detached"
    assert restarted_backend.detach_calls == 1
    repeated_detach = restarted.detach_display(request_id="detach-2", session_id=session_id)
    assert repeated_detach["reason_code"] == "display_already_detached"
    assert restarted_backend.detach_calls == 1

    session_file = run_root / run_id / "displays" / session_id / "DISPLAY_SESSION.json"
    assert json.loads(session_file.read_text(encoding="utf-8"))["state"] == "detached"


def test_display_session_index_drops_unrecoverable_legacy_ids(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    orchestrator = MoSimOrchestrator(run_root=run_root, backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    run_id = prepared["run_id"]
    manifest_path = run_root / run_id / "RUN_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["display_sessions"].append("display-legacy-without-session-record")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    legacy_dir = run_root / run_id / "displays" / "display-legacy-without-session-record"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "DISPLAY_STATUS.json").write_text(
        json.dumps({"state": "attached"}), encoding="utf-8"
    )

    restarted = MoSimOrchestrator(run_root=run_root, backend=FakeRuntimeBackend())
    display = restarted.prepare_display_session(
        request_id="display", run_id=run_id, displays=["unreal"]
    )

    assert display["accepted"] is True
    reconciled = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert reconciled["display_sessions"] == [display["session"]["session_id"]]
    assert legacy_dir.is_dir()
    assert any(
        event["event_type"] == "display_session_index_reconciled"
        for event in reconciled["events"]
    )


def test_display_session_rejects_second_active_configuration(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    run_id = prepared["run_id"]
    first = orchestrator.prepare_display_session(
        request_id="display-1", run_id=run_id, displays=["unreal"]
    )
    conflict = orchestrator.prepare_display_session(
        request_id="display-2", run_id=run_id, displays=["rviz_pointcloud"]
    )

    assert conflict["accepted"] is False
    assert conflict["reason_code"] == "display_session_conflict"
    assert conflict["session"]["session_id"] == first["session"]["session_id"]
    assert len(orchestrator.manifests[run_id]["display_sessions"]) == 1


def test_display_detach_failure_is_persisted_and_retried_once(tmp_path: Path) -> None:
    backend = FailingDetachBackend()
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=backend)
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    display = orchestrator.prepare_display_session(
        request_id="display", run_id=prepared["run_id"], displays=["unreal"]
    )
    session_id = display["session"]["session_id"]
    orchestrator.attach_display(request_id="attach", session_id=session_id)

    detached = orchestrator.detach_display(request_id="detach", session_id=session_id)

    assert detached["accepted"] is False
    assert detached["session"]["state"] == "detach_failed"
    assert backend.detach_calls == 2
    session_path = tmp_path / prepared["run_id"] / "displays" / session_id / "DISPLAY_SESSION.json"
    assert json.loads(session_path.read_text(encoding="utf-8"))["state"] == "detach_failed"


def test_get_run_state_returns_recoverable_display_session(tmp_path: Path) -> None:
    orchestrator = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    display = orchestrator.prepare_display_session(
        request_id="display", run_id=prepared["run_id"], displays=["unreal", "rviz_pointcloud"]
    )
    session_id = display["session"]["session_id"]
    orchestrator.attach_display(request_id="attach", session_id=session_id)

    restarted = MoSimOrchestrator(run_root=tmp_path, backend=FakeRuntimeBackend())
    state = restarted.get_run_state(request_id="state", run_id=prepared["run_id"])

    assert state["accepted"] is True
    assert state["session"]["session_id"] == session_id
    assert state["session"]["state"] == "attached"
