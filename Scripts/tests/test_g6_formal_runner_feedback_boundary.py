from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners"
BINDING_ROOT = ROOT / "Config" / "control_platform" / "g6_champion_bindings"
RUNNERS = {
    "cascade_pid": "CascadePidFormalRunner.mo",
    "lqr_baseline": "LqrBaselineFormalRunner.mo",
    "super_twisting_smc": "SuperTwistingSmcFormalRunner.mo",
    "linear_mpc": "LinearMpcFormalRunner.mo",
    "dfbc_high_order_attitude": "DfbcHighOrderFormalRunner.mo",
    "trained_neural_residual": "TrainedNeuralResidualFormalRunner.mo",
}
SAMPLED_SIGNALS = [
    "reference.position_command -> controller.position_ref",
    "reference.velocity_command -> controller.velocity_ref",
    "reference.acceleration_command -> controller.acceleration_ref",
    "plant.position -> controller.position_mea",
    "plant.attitude -> controller.attitude_mea",
]
CONTINUOUS_INNER_LOOP_SIGNALS = ["plant.attitude -> offline_inner_allocator.attitude_mea"]
SHARED_CLOSURE_ROLES = {
    "shared_sunray150_assembly",
    "physical_wrench_adapter",
    "wrapper_surface",
    "rotor_actuator_core",
    "plant_sensor_surface",
    "virtual_px4_classic_profile",
    "climb_path_reference",
}


def test_formal_runners_delay_only_promoted_controller_inputs() -> None:
    for controller_id, filename in RUNNERS.items():
        source = (RUNNER_ROOT / filename).read_text(encoding="utf-8")

        assert "connect(reference.position_command, sampled_position_ref.u)" in source, controller_id
        assert "connect(sampled_position_ref.y, controller.position_ref)" in source, controller_id
        assert "connect(reference.velocity_command, sampled_velocity_ref.u)" in source, controller_id
        assert "connect(sampled_velocity_ref.y, controller.velocity_ref)" in source, controller_id
        assert "connect(reference.acceleration_command, sampled_acceleration_ref.u)" in source, controller_id
        assert "connect(sampled_acceleration_ref.y, controller.acceleration_ref)" in source, controller_id
        assert "connect(plant.position, sampled_position.u)" in source, controller_id
        assert "connect(sampled_position.y, controller.position_mea)" in source, controller_id
        assert "connect(plant.attitude, sampled_attitude.u)" in source, controller_id
        assert "connect(sampled_attitude.y, controller.attitude_mea)" in source, controller_id
        assert "connect(plant.attitude, offline_inner_allocator.attitude_mea)" in source, controller_id
        assert "connect(sampled_attitude.y, offline_inner_allocator.attitude_mea)" not in source, controller_id


def test_formal_bindings_declare_the_same_sampled_and_continuous_boundaries() -> None:
    for controller_id in RUNNERS:
        binding = json.loads((BINDING_ROOT / f"{controller_id}.json").read_text(encoding="utf-8"))
        boundary = binding["formal_harness_feedback_boundary"]

        assert boundary["kind"] == "sampled_controller_inputs"
        assert boundary["sample_period_s"] == 0.01
        assert boundary["initial_measurement"] == "zero"
        assert boundary["signals"] == SAMPLED_SIGNALS
        assert boundary["continuous_inner_loop_signals"] == CONTINUOUS_INNER_LOOP_SIGNALS
        roles = {source["role"] for source in binding["source_bindings"]}
        assert SHARED_CLOSURE_ROLES.issubset(roles)
        assert "visual_chassis" not in roles
