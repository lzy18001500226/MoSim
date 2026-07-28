#!/usr/bin/env python3
"""Validate the static four-boundary offline Runner interface contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "Config/control_platform/offline_runner_interface_contract_v1.json"
EXPECTED_BOUNDARIES = {"ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"}
REQUIRED_RESULT_NAMES = {"position_ref", "position", "attitude", "rotor_command", "position_error_norm"}
REQUIRED_CONTROLLER_INPUTS = {
    "position_ref",
    "velocity_ref",
    "acceleration_ref",
    "position_mea",
    "velocity_mea",
    "attitude_mea",
}
VELOCITY_SEMANTICS = "runner_owned_filtered_position_derivative_m_per_s"
COLLECTIVE_THRUST_SEMANTICS = "offline_collective_increment_newtons_about_hover_not_online_verified"
REQUIRED_LIFECYCLE = {"dt", "reset", "enable", "run_id", "profile_hash", "parameter_version", "random_seed"}
REQUIRED_DIAGNOSTICS = {
    "module_status",
    "input_valid",
    "output_valid",
    "finite_check_passed",
    "saturation_mask",
    "fallback_active",
    "reason_code",
}
EXPECTED_MODULE_STATUSES = {"disabled", "initializing", "active", "degraded", "fallback", "failed"}
GENERIC_RUNNERS = {
    "ATTITUDE_THRUST": "Models/MoSimQuadrotorModel/Experiment/Runners/AttitudeThrustRunner.mo",
    "BODY_RATE_THRUST": "Models/MoSimQuadrotorModel/Experiment/Runners/BodyRateThrustRunner.mo",
    "WRENCH": "Models/MoSimQuadrotorModel/Experiment/Runners/WrenchRunner.mo",
    "ROTOR_COMMAND": "Models/MoSimQuadrotorModel/Experiment/Runners/RotorCommandRunner.mo",
}
FORMAL_CHAMPION_RUNNERS = {
    "cascade_pid": "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/CascadePidFormalRunner.mo",
    "dfbc_high_order_attitude": "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/DfbcHighOrderFormalRunner.mo",
    "linear_mpc": "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LinearMpcFormalRunner.mo",
    "lqr_baseline": "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LqrBaselineFormalRunner.mo",
    "super_twisting_smc": "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/SuperTwistingSmcFormalRunner.mo",
    "trained_neural_residual": "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/TrainedNeuralResidualFormalRunner.mo",
}
FORMAL_ATTITUDE_THRUST_RUNNER_BASE = (
    "Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalAttitudeThrustRunnerBase.mo"
)
ATTITUDE_THRUST_ADAPTERS = {
    "cascade_pid": "Models/MoSimQuadrotorModel/Control/Adapters/CascadePidAttitudeThrustAdapter.mo",
    "dfbc_high_order_attitude": "Models/MoSimQuadrotorModel/Control/Adapters/DfbcHighOrderAttitudeThrustAdapter.mo",
    "linear_mpc": "Models/MoSimQuadrotorModel/Control/Adapters/LinearMpcAttitudeThrustAdapter.mo",
    "lqr_baseline": "Models/MoSimQuadrotorModel/Control/Adapters/LqrBaselineAttitudeThrustAdapter.mo",
    "super_twisting_smc": "Models/MoSimQuadrotorModel/Control/Adapters/SuperTwistingSmcAttitudeThrustAdapter.mo",
    "trained_neural_residual": "Models/MoSimQuadrotorModel/Control/Adapters/TrainedNeuralResidualAttitudeThrustAdapter.mo",
}
NONZERO_COLLECTIVE_PROBES = {
    "collective_step": "Models/MoSimQuadrotorModel/Experiment/Probes/AllocatorCollectiveStepPlantSmoke.mo",
    "combined_step": "Models/MoSimQuadrotorModel/Experiment/Probes/AllocatorCombinedStepPlantSmoke.mo",
    "combined_high_step": "Models/MoSimQuadrotorModel/Experiment/Probes/AllocatorCombinedHighStepPlantSmoke.mo",
}


def validate(contract: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "mosim.offline_runner_interface_contract.v1":
        errors.append("invalid_schema")
    shared_inputs = contract.get("shared_controller_inputs", [])
    input_by_name = {
        item.get("name"): item
        for item in shared_inputs
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    if set(input_by_name) != REQUIRED_CONTROLLER_INPUTS:
        errors.append("shared_controller_inputs_mismatch")
    elif (
        input_by_name["velocity_ref"].get("dimension") != 3
        or input_by_name["velocity_ref"].get("unit_semantics")
        != "reference_translational_velocity_m_per_s"
        or input_by_name["acceleration_ref"].get("dimension") != 3
        or input_by_name["acceleration_ref"].get("unit_semantics")
        != "reference_translational_acceleration_m_per_s2"
        or input_by_name["velocity_mea"].get("dimension") != 3
        or input_by_name["velocity_mea"].get("unit_semantics") != VELOCITY_SEMANTICS
    ):
        errors.append("velocity_measurement_contract_mismatch")
    velocity_estimator = contract.get("shared_velocity_estimator", {})
    expected_velocity_estimator = {
        "owner": "each_generic_runner_and_formal_champion_runner",
        "source_signal": "plant.position",
        "model": "Modelica.Blocks.Continuous.Derivative",
        "gain": 1.0,
        "time_constant_s": 0.05,
        "initial_output_m_per_s": 0.0,
    }
    if velocity_estimator != expected_velocity_estimator:
        errors.append("shared_velocity_estimator_contract_mismatch")
    boundaries = contract.get("boundaries", {})
    if set(boundaries) != EXPECTED_BOUNDARIES:
        errors.append("four_explicit_boundaries_required")
    for boundary, declaration in boundaries.items():
        for key in ("interface_source", "runner_source"):
            value = declaration.get(key)
            path = root / value if isinstance(value, str) else None
            if path is None or not path.is_file():
                errors.append(f"missing_{key}:{boundary}")
        outputs = declaration.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(f"outputs_required:{boundary}")
            continue
        for output in outputs:
            semantics = output.get("unit_semantics", "")
            if output.get("name") == "collective_thrust_delta":
                if semantics != COLLECTIVE_THRUST_SEMANTICS:
                    errors.append(f"collective_thrust_semantics_mismatch:{boundary}")
            elif not semantics or (
                output["name"] in {"body_force", "body_torque", "rotor_command"}
                and not any(marker in semantics for marker in ("legacy", "not_verified"))
            ):
                errors.append(f"unverified_physical_unit_overclaim:{boundary}:{output.get('name')}")
        interface_text = (root / declaration["interface_source"]).read_text(encoding="utf-8")
        runner_text = (root / declaration["runner_source"]).read_text(encoding="utf-8")
        if "Modelica.Blocks.Interfaces.RealInput velocity_mea[3]" not in interface_text:
            errors.append(f"interface_velocity_missing:{boundary}")
        for output in outputs:
            if output["name"] not in interface_text:
                errors.append(f"interface_output_missing:{boundary}:{output['name']}")
        for name in REQUIRED_RESULT_NAMES:
            if name not in runner_text:
                errors.append(f"runner_result_missing:{boundary}:{name}")
        for token in (
            "Modelica.Blocks.Continuous.Derivative velocity_estimator[3]",
            "each T = 0.05",
            "each initType = Modelica.Blocks.Types.Init.InitialOutput",
            "each y_start = 0",
            "connect(plant.position, velocity_estimator.u);",
            "connect(velocity_estimator.y, controller.velocity_mea);",
        ):
            if token not in runner_text:
                errors.append(f"runner_velocity_estimator_mismatch:{boundary}:{token}")

    formal_attitude_thrust_base = root / FORMAL_ATTITUDE_THRUST_RUNNER_BASE
    for controller_id, relative_path in FORMAL_CHAMPION_RUNNERS.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing_formal_runner:{controller_id}")
            continue
        runner_text = path.read_text(encoding="utf-8")
        base_reference = "extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase("
        if base_reference in runner_text:
            if not formal_attitude_thrust_base.is_file():
                errors.append("formal_attitude_thrust_runner_base_missing")
                continue
            runner_text = f"{runner_text}\n{formal_attitude_thrust_base.read_text(encoding='utf-8')}"
        for token in (
            "Modelica.Blocks.Continuous.Derivative velocity_estimator[3]",
            "each T = 0.05",
            "connect(sampled_position.y, velocity_estimator.u);",
            "connect(velocity_estimator.y, controller.velocity_mea);",
        ):
            if token not in runner_text:
                errors.append(f"formal_runner_velocity_estimator_mismatch:{controller_id}:{token}")

    for controller_id, relative_path in ATTITUDE_THRUST_ADAPTERS.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing_attitude_thrust_adapter:{controller_id}")
            continue
        adapter_text = path.read_text(encoding="utf-8")
        if "velocity_mea" not in adapter_text or "velocity_estimator" in adapter_text:
            errors.append(f"adapter_velocity_boundary_mismatch:{controller_id}")
        if "max_collective_thrust_delta_n" not in adapter_text:
            errors.append(f"adapter_collective_newton_limit_missing:{controller_id}")

    for probe_id, relative_path in NONZERO_COLLECTIVE_PROBES.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing_collective_probe:{probe_id}")
            continue
        if "* allocator.collective_thrust_slope" not in path.read_text(encoding="utf-8"):
            errors.append(f"collective_probe_newton_conversion_missing:{probe_id}")

    attitude_allocator = root / "Models/MoSimQuadrotorModel/Control/Allocation/OfflineAttitudeRateAllocator.mo"
    body_rate_allocator = root / "Models/MoSimQuadrotorModel/Control/Allocation/OfflineBodyRateAllocator.mo"
    if not attitude_allocator.is_file() or not body_rate_allocator.is_file():
        errors.append("offline_allocator_source_missing")
    else:
        attitude_text = attitude_allocator.read_text(encoding="utf-8")
        body_rate_text = body_rate_allocator.read_text(encoding="utf-8")
        for token in (
            "collective_thrust_slope",
            "rotor_speed_delta = collective_thrust_delta / collective_thrust_slope;",
            "Roll feedback and mixer signs are locked to Official PID parity",
            "hover_speed + rotor_speed_delta",
        ):
            if token not in attitude_text:
                errors.append(f"attitude_allocator_newton_boundary_mismatch:{token}")
        for token in (
            "collective_thrust_slope",
            "rotor_speed_delta = collective_thrust_delta / collective_thrust_slope;",
            "hover_speed + rotor_speed_delta",
        ):
            if token not in body_rate_text:
                errors.append(f"body_rate_allocator_newton_boundary_mismatch:{token}")

    result_names = {item.get("name") for item in contract.get("runner_result_surface", [])}
    if result_names != REQUIRED_RESULT_NAMES:
        errors.append("runner_result_surface_mismatch")
    lifecycle = contract.get("lifecycle_contract", {})
    if set(lifecycle.get("required_future_fields", [])) != REQUIRED_LIFECYCLE:
        errors.append("lifecycle_fields_mismatch")
    if lifecycle.get("current_model_ports_implemented") is not False:
        errors.append("lifecycle_ports_must_remain_blocked_until_model_evidence")
    if set(lifecycle.get("candidate_schema", {})) != REQUIRED_LIFECYCLE:
        errors.append("lifecycle_candidate_schema_mismatch")

    frame = contract.get("frame_contract", {})
    if frame.get("binding_state") != "not_bound_to_model_ports":
        errors.append("frame_contract_must_remain_unbound_until_model_evidence")
    if "unverified" not in str(frame.get("current_position_frame", "")):
        errors.append("offline_position_frame_overclaim")
    if "unverified" not in str(frame.get("current_body_frame", "")):
        errors.append("offline_body_frame_overclaim")

    timing = contract.get("time_contract", {})
    if timing.get("binding_state") != "solver_annotation_only":
        errors.append("time_contract_binding_overclaim")
    if timing.get("fixed_step_claim_allowed") is not False:
        errors.append("fixed_step_claim_must_remain_blocked")
    if timing.get("realtime_rate_claim_allowed") is not False:
        errors.append("realtime_rate_claim_must_remain_blocked")
    for boundary, declaration in boundaries.items():
        runner_path = root / declaration.get("runner_source", "")
        if runner_path.is_file():
            runner_text = runner_path.read_text(encoding="utf-8")
            for token in ("Algorithm = Dassl", "StartTime = 0", "StopTime = 50", "Interval = 0.01"):
                if token not in runner_text:
                    errors.append(f"runner_time_annotation_mismatch:{boundary}:{token}")

    diagnostics = contract.get("diagnostics_contract", {})
    if set(diagnostics.get("required_future_fields", [])) != REQUIRED_DIAGNOSTICS:
        errors.append("diagnostics_fields_mismatch")
    if set(diagnostics.get("module_status_values", [])) != EXPECTED_MODULE_STATUSES:
        errors.append("diagnostics_status_values_mismatch")
    if diagnostics.get("current_model_outputs_implemented") is not False:
        errors.append("diagnostics_outputs_must_remain_blocked_until_model_evidence")
    if diagnostics.get("invalid_numeric_policy") != "fail_closed_and_record_reason_code":
        errors.append("invalid_numeric_policy_must_fail_closed")
    gaps = set(contract.get("known_gaps", []))
    for required_gap in (
        "coordinate_frame_contract_not_bound_to_model_ports",
        "physical_command_units_not_verified",
        "lifecycle_context_not_bound_to_model_ports",
        "time_and_solver_statistics_not_bound_to_run_manifest",
    ):
        if required_gap not in gaps:
            errors.append(f"required_gap_missing:{required_gap}")
    return errors


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    errors = validate(contract)
    result = {"ok": not errors, "errors": errors, "boundary_count": len(contract.get("boundaries", {}))}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
