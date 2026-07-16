from __future__ import annotations

import json
from pathlib import Path

from src.orchestration import MoSimOrchestrator


class FakeRuntimeBackend:
    backend_id = "test_backend"

    def start(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_started", "pid": 123}

    def stop(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_stopped"}

    def reset(self, manifest):
        return {"accepted": True, "reason_code": "test_runtime_reset"}

    def apply_injection(self, manifest, command):
        return {"accepted": True, "reason_code": "test_injection_applied", "applied_value": command["value"]}


PROFILE = "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json"
THREE_UAV_PROFILE = "Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json"


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
