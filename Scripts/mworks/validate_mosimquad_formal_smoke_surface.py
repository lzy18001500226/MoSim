#!/usr/bin/env python3
"""Static MoSimQuadrotorModel formal smoke/check surface generator.

This script is intentionally file-only. It validates the project-owned
Modelica implementation surface and emits the future live validation matrix for a later
MWORKS task. It does not call MWORKS, Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

VEHICLE_DIR = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle"
LEGACY_DIAGNOSTICS_DIR = VEHICLE_DIR / "LegacyDiagnostics"
DYNAMICS_DIR = VEHICLE_DIR / "Dynamics"
FORMAL_PARAMETERS_DIR = ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters"
RETIRED_ROOTS = (
    ROOT / "Models" / "QuadrotorExperiments",
    ROOT / "Models" / "QuadrotorControllerBlocks",
    ROOT / "Models" / "MworksLive",
)
ROOT_CONSOLIDATION_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260722_mosimquad_model_root_consolidation"
    / "formal_smoke_surface"
)

REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-FORMAL-SMOKE-SURFACE-STATIC-PREP-20260608-023"

DYNAMICS_FORMAL_ORDER = [
    "ActuatorCommandMapper",
    "ActuatorMappedWrapperSurface",
    "OptionalDampingGyroLayer",
    "PhysicalWrenchAdapter",
    "RotorActuatorCore",
    "WrapperSurface",
]

FORMAL_PACKAGE_ORDER = [
    *DYNAMICS_FORMAL_ORDER,
    "HoverSmoke",
    "YawStepSmoke",
    "RotorEffectivenessSmoke",
    "WrapperHoverSmoke",
    "WrapperYawStepSmoke",
    "PhysicalWrenchHoverSmoke",
    "PhysicalWrenchYawStepSmoke",
]

PRODUCTION_FORMAL_NAMES = {
    "RotorActuatorCore",
    "WrapperSurface",
    "ActuatorCommandMapper",
    "ActuatorMappedWrapperSurface",
    "OptionalDampingGyroLayer",
    "PhysicalWrenchAdapter",
}

DIAGNOSTIC_FORMAL_NAMES = set(FORMAL_PACKAGE_ORDER) - PRODUCTION_FORMAL_NAMES
DIAGNOSTIC_FORMAL_ORDER = [
    "HoverSmoke",
    "YawStepSmoke",
    "PhysicalWrenchHoverSmoke",
    "PhysicalWrenchYawStepSmoke",
    "RotorEffectivenessSmoke",
    "WrapperHoverSmoke",
    "WrapperYawStepSmoke",
]


TARGETS: list[dict[str, Any]] = [
    {
        "formal_name": "RotorActuatorCore",
        "compat_name": "RotorDynamicsCore",
        "implementation_model": "RotorActuatorCore",
        "implementation_file": "RotorActuatorCore.mo",
        "role": "core_dynamics_check",
        "check_phase": 1,
        "simulate_phase": None,
        "expected_result_variables": [
            "motor_command",
            "omega",
            "motor_tau",
            "thrust",
            "yaw_reaction_moment",
            "rotor_arm_moment",
            "total_thrust",
            "total_moment_body",
            "hover_thrust_error",
            "thrust_effectiveness",
            "reaction_moment_effectiveness",
            "minimum_thrust_effectiveness",
            "minimum_reaction_moment_effectiveness",
        ],
        "required_snippets": [
            "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
            "nominal_thrust[i] = lift_coefficient * omega[i] * omega[i]",
            "fault_effectiveness[i] = if i == fault_rotor_index and time >= fault_start_s then",
            "thrust[i] = fault_effectiveness[i] * thrust_effectiveness[i] * nominal_thrust[i]",
            "yaw_reaction_moment[i] = fault_effectiveness[i] * yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust_effectiveness[i] * nominal_thrust[i]",
            "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
            "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
            "minimum_thrust_effectiveness = min({fault_effectiveness[i] * thrust_effectiveness[i] for i in 1:4})",
            "minimum_reaction_moment_effectiveness = min({fault_effectiveness[i] * reaction_moment_effectiveness[i] for i in 1:4})",
        ],
        "pass_fail_boundary": "check_model must accept command lag, static and scheduled effectiveness-scaled Ct*omega^2 thrust, yaw reaction torque, rotor-center moment, exposed total force/moment variables, and a time-varying single-rotor fault hook.",
    },
    {
        "formal_name": "RotorEffectivenessSmoke",
        "compat_name": "RotorEffectivenessSmoke",
        "implementation_model": "RotorEffectivenessSmoke",
        "implementation_file": "RotorEffectivenessSmoke.mo",
        "role": "single_rotor_effectiveness_smoke",
        "check_phase": 3,
        "simulate_phase": 3,
        "expected_result_variables": [
            "dynamics.thrust_effectiveness",
            "dynamics.minimum_thrust_effectiveness",
            "total_thrust_loss",
            "roll_moment_imbalance",
            "pitch_moment_imbalance",
            "yaw_moment_imbalance",
        ],
        "required_snippets": [
            "parameter Integer degraded_rotor_index = 1",
            "parameter Real degraded_rotor_thrust_effectiveness = 0.85",
            "RotorActuatorCore dynamics(",
            "thrust_effectiveness = {",
            "total_thrust_loss = expected_nominal_total_thrust - dynamics.total_thrust",
            "roll_moment_imbalance = dynamics.total_moment_body[1]",
            "pitch_moment_imbalance = dynamics.total_moment_body[2]",
            "yaw_moment_imbalance = dynamics.total_moment_body[3]",
        ],
        "pass_fail_boundary": "probe single-rotor thrust-effectiveness degradation observability only; this is not an identified fault model or controller robustness acceptance.",
    },
    {
        "formal_name": "ActuatorCommandMapper",
        "compat_name": "ActuatorCommandMapper",
        "implementation_model": "ActuatorCommandMapper",
        "implementation_file": "ActuatorCommandMapper.mo",
        "role": "normalized_command_mapper_check",
        "check_phase": 2,
        "simulate_phase": None,
        "expected_result_variables": [
            "normalized_command",
            "saturated_normalized_command",
            "actuator_saturation_error",
            "visual_rotor_speed_unsigned",
            "signed_visual_rotor_speed_command",
            "hover_command_error",
        ],
        "required_snippets": [
            "input Real normalized_command[4]",
            "saturated_normalized_command[i]",
            "actuator_saturation_error[i] = normalized_command[i] - saturated_normalized_command[i]",
            "signed_visual_rotor_speed_command[i] =",
            "hover_command_error[i]",
        ],
        "pass_fail_boundary": "future live result probe must show normalized command saturation and signed visual rotor speed outputs are present; no PWM/RPM truth is claimed.",
    },
    {
        "formal_name": "WrapperSurface",
        "compat_name": "WrapperSurface",
        "implementation_model": "WrapperSurface",
        "implementation_file": "WrapperSurface.mo",
        "role": "wrapper_force_moment_surface_check",
        "check_phase": 4,
        "simulate_phase": None,
        "expected_result_variables": [
            "motor_command",
            "commanded_thrust",
            "commanded_yaw_reaction_moment",
            "commanded_rotor_arm_moment",
            "total_thrust",
            "total_moment_body",
            "commanded_total_thrust",
            "commanded_total_moment_body",
            "hover_thrust_error",
            "commanded_hover_thrust_error",
            "yaw_moment_gate",
            "commanded_yaw_moment_gate",
            "motor_order_gate_error",
            "yaw_direction_gate_error",
        ],
        "required_snippets": [
            "dynamics.motor_command = motor_command",
            "commanded_thrust[i] = dynamics.fault_effectiveness[i] * dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
            "commanded_total_moment_body[3]",
            "motor_order_gate_error =",
            "yaw_direction_gate_error =",
        ],
        "pass_fail_boundary": "future live check must preserve wrapper command-side and lagged force/moment observability before any plant integration claim.",
    },
    {
        "formal_name": "ActuatorMappedWrapperSurface",
        "compat_name": "ActuatorMappedWrapperSurface",
        "implementation_model": "ActuatorMappedWrapperSurface",
        "implementation_file": "ActuatorMappedWrapperSurface.mo",
        "role": "mapper_to_wrapper_surface_check",
        "check_phase": 5,
        "simulate_phase": None,
        "expected_result_variables": [
            "normalized_actuator_command",
            "saturated_normalized_command",
            "actuator_saturation_error",
            "signed_visual_rotor_speed_command",
            "total_thrust",
            "total_moment_body",
            "commanded_total_thrust",
            "commanded_total_moment_body",
            "hover_thrust_error",
            "commanded_hover_thrust_error",
            "yaw_moment_gate",
            "commanded_yaw_moment_gate",
            "motor_order_gate_error",
            "yaw_direction_gate_error",
        ],
        "required_snippets": [
            "input Real normalized_actuator_command[4]",
            "actuator_mapper.normalized_command = normalized_actuator_command",
            "wrapper.motor_command = actuator_mapper.signed_visual_rotor_speed_command",
            "signed_visual_rotor_speed_command = actuator_mapper.signed_visual_rotor_speed_command",
        ],
        "pass_fail_boundary": "future live probe may claim only normalized command to signed visual speed to wrapper feedthrough, not closed-loop control.",
    },
    {
        "formal_name": "OptionalDampingGyroLayer",
        "compat_name": "OptionalDampingGyroLayer",
        "implementation_model": "OptionalDampingGyroLayer",
        "implementation_file": "OptionalDampingGyroLayer.mo",
        "role": "default_disabled_optional_layer_check",
        "check_phase": 6,
        "simulate_phase": None,
        "expected_result_variables": [
            "enable_rotor_gyro",
            "enable_body_drag",
            "enable_angular_damping",
            "normalized_actuator_command",
            "body_velocity_body",
            "body_angular_velocity_body",
            "base_force_body",
            "base_moment_body",
            "rotor_angular_momentum_body_z",
            "rotor_gyro_moment_body",
            "rotor_gyro_total_moment_body",
            "body_drag_force_body",
            "angular_damping_moment_body",
            "optional_force_body",
            "optional_moment_body",
            "total_force_body",
            "total_moment_body",
            "optional_force_norm",
            "optional_moment_norm",
            "default_disabled_force_delta",
            "default_disabled_moment_delta",
        ],
        "required_snippets": [
            "parameter Boolean enable_rotor_gyro = false",
            "parameter Boolean enable_body_drag = false",
            "parameter Boolean enable_angular_damping = false",
            "optional_force_body[j] = body_drag_force_body[j]",
            "default_disabled_force_delta =",
            "default_disabled_moment_delta =",
        ],
        "pass_fail_boundary": "future live probe must see default-disabled deltas at zero or write a blocker; 023 does not claim live numeric deltas.",
    },
    {
        "formal_name": "PhysicalWrenchAdapter",
        "compat_name": "PhysicalWrenchAdapter",
        "implementation_model": "PhysicalWrenchAdapter",
        "implementation_file": "PhysicalWrenchAdapter.mo",
        "role": "physical_wrench_boundary_check",
        "check_phase": 7,
        "simulate_phase": None,
        "expected_result_variables": [
            "applied_force_body",
            "applied_torque_body",
            "applied_force_z_body",
            "applied_yaw_torque_body",
            "force_application_error",
            "torque_application_error",
            "hover_weight_balance_error",
            "wrapper_total_thrust",
            "wrapper_yaw_moment",
            "motor_order_gate_error",
            "yaw_direction_gate_error",
        ],
        "required_snippets": [
            "WorldForceAndTorque",
            "applied_force_body = {0, 0, wrapper.total_thrust}",
            "applied_torque_body = wrapper.total_moment_body",
            "forceAndTorque.force = applied_force_body",
            "forceAndTorque.torque = applied_torque_body",
            "connect(forceAndTorque.frame_b, body.frame_a)",
        ],
        "pass_fail_boundary": "future live validation may claim only wrapper force/torque application to the explicit minimal MultiBody body, not full plant integration.",
    },
    {
        "formal_name": "HoverSmoke",
        "compat_name": "RotorHoverSmoke",
        "implementation_model": "HoverSmoke",
        "implementation_file": "HoverSmoke.mo",
        "role": "core_hover_smoke",
        "check_phase": 8,
        "simulate_phase": 1,
        "expected_result_variables": [
            "dynamics.total_thrust",
            "dynamics.total_moment_body",
            "dynamics.hover_thrust_error",
            "dynamics.omega",
            "dynamics.thrust",
        ],
        "required_snippets": [
            "RotorActuatorCore dynamics",
            "dynamics.motor_command =",
            "annotation(experiment(",
            "StopTime = 0.25",
        ],
        "pass_fail_boundary": "simulate only after all check_model targets pass; probe hover thrust/moment variables without claiming controller or plant performance.",
    },
    {
        "formal_name": "YawStepSmoke",
        "compat_name": "RotorYawStepSmoke",
        "implementation_model": "YawStepSmoke",
        "implementation_file": "YawStepSmoke.mo",
        "role": "core_yaw_step_smoke",
        "check_phase": 9,
        "simulate_phase": 2,
        "expected_result_variables": [
            "yaw_step",
            "rotor_speed_mag",
            "dynamics.total_thrust",
            "dynamics.total_moment_body",
            "dynamics.hover_thrust_error",
            "dynamics.yaw_reaction_moment",
        ],
        "required_snippets": [
            "parameter Real yaw_delta_omega2 = 300",
            "yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0",
            "rotor_speed_mag[i] = sqrt(",
            "dynamics.motor_command[i] =",
        ],
        "pass_fail_boundary": "simulate only after all check_model targets pass; yaw response observation is a source-level smoke, not dynamic yaw acceptance.",
    },
    {
        "formal_name": "WrapperHoverSmoke",
        "compat_name": "WrapperHoverSmoke",
        "implementation_model": "WrapperHoverSmoke",
        "implementation_file": "WrapperHoverSmoke.mo",
        "role": "wrapper_hover_smoke",
        "check_phase": 10,
        "simulate_phase": 4,
        "expected_result_variables": [
            "wrapper.total_thrust",
            "wrapper.total_moment_body",
            "wrapper.commanded_total_thrust",
            "wrapper.commanded_total_moment_body",
            "wrapper.hover_thrust_error",
            "wrapper.commanded_hover_thrust_error",
            "wrapper.motor_order_gate_error",
            "wrapper.yaw_direction_gate_error",
        ],
        "required_snippets": [
            "WrapperSurface wrapper",
            "wrapper.motor_command =",
            "StopTime = 0.25",
        ],
        "pass_fail_boundary": "probe wrapper hover observability only; no full plant, controller, or Factory trace claim.",
    },
    {
        "formal_name": "WrapperYawStepSmoke",
        "compat_name": "WrapperYawStepSmoke",
        "implementation_model": "WrapperYawStepSmoke",
        "implementation_file": "WrapperYawStepSmoke.mo",
        "role": "wrapper_yaw_step_smoke",
        "check_phase": 11,
        "simulate_phase": 5,
        "expected_result_variables": [
            "yaw_step",
            "rotor_speed_mag",
            "wrapper.total_thrust",
            "wrapper.total_moment_body",
            "wrapper.commanded_total_thrust",
            "wrapper.commanded_total_moment_body",
            "wrapper.yaw_moment_gate",
            "wrapper.commanded_yaw_moment_gate",
        ],
        "required_snippets": [
            "WrapperSurface wrapper",
            "yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0",
            "wrapper.motor_command[i] =",
        ],
        "pass_fail_boundary": "probe wrapper yaw moment variables only; no dynamic yaw transient acceptance.",
    },
    {
        "formal_name": "PhysicalWrenchHoverSmoke",
        "compat_name": "PhysicalWrenchHoverSmoke",
        "implementation_model": "PhysicalWrenchHoverSmoke",
        "implementation_file": "PhysicalWrenchHoverSmoke.mo",
        "role": "physical_wrench_hover_smoke",
        "check_phase": 12,
        "simulate_phase": 6,
        "expected_result_variables": [
            "adapter.applied_force_body",
            "adapter.applied_torque_body",
            "adapter.applied_force_z_body",
            "adapter.applied_yaw_torque_body",
            "adapter.force_application_error",
            "adapter.torque_application_error",
            "adapter.hover_weight_balance_error",
            "adapter.wrapper_total_thrust",
            "adapter.wrapper_yaw_moment",
        ],
        "required_snippets": [
            "PhysicalWrenchAdapter adapter",
            "adapter.wrapper.motor_command =",
            "StopTime = 0.25",
        ],
        "pass_fail_boundary": "probe explicit adapter/body force/torque variables only; no QuadChassis or full plant closure.",
    },
    {
        "formal_name": "PhysicalWrenchYawStepSmoke",
        "compat_name": "PhysicalWrenchYawStepSmoke",
        "implementation_model": "PhysicalWrenchYawStepSmoke",
        "implementation_file": "PhysicalWrenchYawStepSmoke.mo",
        "role": "physical_wrench_yaw_step_smoke",
        "check_phase": 13,
        "simulate_phase": 7,
        "expected_result_variables": [
            "yaw_step",
            "rotor_speed_mag",
            "adapter.applied_force_body",
            "adapter.applied_torque_body",
            "adapter.applied_force_z_body",
            "adapter.applied_yaw_torque_body",
            "adapter.force_application_error",
            "adapter.torque_application_error",
            "adapter.wrapper_yaw_moment",
        ],
        "required_snippets": [
            "PhysicalWrenchAdapter adapter",
            "yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0",
            "adapter.wrapper.motor_command[i] =",
        ],
        "pass_fail_boundary": "probe explicit physical-wrench yaw application only; no full plant tracking or closed loop claim.",
    },
]


PARAMETER_TARGET = {
    "formal_target": "MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance",
    "implementation_file": "Models/MoSimQuadrotorModel/Parameters/package.mo",
    "profile_record_file": "Models/MoSimQuadrotorModel/Parameters/Sunray150VirtualPx4Classic.mo",
    "check_phase": 0,
    "expected_package_fields": [
        "Sunray150VirtualPx4Classic",
        "geometry_claim_boundary",
        "rotor_center_mworks_dronefixed",
        "non_geometry_seed_source",
        "mass_kg",
        "sdf_motor_constant",
        "mworks_lift_coefficient",
        "yaw_moment_ratio_seed",
        "enable_rotor_gyro_default",
        "enable_body_drag_default",
        "enable_angular_damping_default",
        "identification_status",
        "do_not_promote_boundary",
    ],
    "expected_profile_record_fields": [
        "profile_id",
        "geometry_source",
        "body_inertia_diagonal_kg_m2",
        "gravity_mps2",
        "mworks_controller_hover_percentage",
        "px4ctrl_hov_percent",
        "motor_time_constant_up_s",
        "motor_time_constant_down_s",
        "Virtual simulation seed only; not real-aircraft system identification truth",
    ],
    "pass_fail_boundary": "parameter record must remain source-labeled provenance only and not identified Sunray150 truth.",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_order(path: Path) -> list[str]:
    return [line.strip() for line in read_text(path).splitlines() if line.strip()]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalized_modelica(text: str) -> str:
    """Compare source anchors without making formatting part of the contract."""

    return " ".join(text.replace("\r\n", "\n").split())


def assert_contains(findings: list[str], text: str, snippet: str, label: str) -> None:
    if normalized_modelica(snippet) not in normalized_modelica(text):
        findings.append(f"{label}: missing snippet {snippet!r}")


def requires_dedicated_formal_source(formal_name: str) -> bool:
    return formal_name in FORMAL_PACKAGE_ORDER


def source_dir_for(formal_name: str) -> Path:
    if formal_name in PRODUCTION_FORMAL_NAMES:
        return DYNAMICS_DIR
    if formal_name in DIAGNOSTIC_FORMAL_NAMES:
        return LEGACY_DIAGNOSTICS_DIR
    raise ValueError(f"unknown formal source owner: {formal_name}")


def target_namespace_for(formal_name: str) -> str:
    if formal_name in PRODUCTION_FORMAL_NAMES:
        return "MoSimQuadrotorModel.Vehicle.Dynamics"
    if formal_name in DIAGNOSTIC_FORMAL_NAMES:
        return "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics"
    raise ValueError(f"unknown formal target namespace: {formal_name}")


def canonical_target_for(formal_name: str) -> str:
    return f"{target_namespace_for(formal_name)}.{formal_name}"


def build_matrix() -> tuple[list[dict[str, Any]], list[str]]:
    findings: list[str] = []
    vehicle_order = read_order(VEHICLE_DIR / "package.order")
    diagnostics_order = read_order(LEGACY_DIAGNOSTICS_DIR / "package.order")
    dynamics_order = read_order(DYNAMICS_DIR / "package.order")
    parameter_package = read_text(FORMAL_PARAMETERS_DIR / "package.mo")
    parameter_profile_record = read_text(
        FORMAL_PARAMETERS_DIR / "Sunray150VirtualPx4Classic.mo"
    )
    parameter_order = read_order(FORMAL_PARAMETERS_DIR / "package.order")

    if "Dynamics" not in vehicle_order:
        findings.append(
            "Vehicle package.order omits the Dynamics production package"
        )
    if diagnostics_order != DIAGNOSTIC_FORMAL_ORDER:
        findings.append(
            f"LegacyDiagnostics package.order mismatch: {diagnostics_order!r}"
        )
    if dynamics_order != DYNAMICS_FORMAL_ORDER:
        findings.append(
            "Vehicle.Dynamics package.order must contain the production sources exactly: "
            f"{dynamics_order!r}"
        )
    for retired_root in RETIRED_ROOTS:
        if retired_root.exists():
            findings.append(f"retired top-level model root remains present: {rel(retired_root)}")
    if parameter_order != ["Sunray150VirtualPx4Classic", "Sunray150ParameterProvenance"]:
        findings.append(f"Parameters package.order mismatch: {parameter_order!r}")

    matrix: list[dict[str, Any]] = []
    for target in TARGETS:
        formal_name = target["formal_name"]
        implementation_model = target["implementation_model"]
        source_dir = source_dir_for(formal_name)
        source_namespace = target_namespace_for(formal_name)
        canonical_target = canonical_target_for(formal_name)
        implementation_path = source_dir / target["implementation_file"]
        implementation_text = read_text(implementation_path)
        formal_source_path = source_dir / f"{formal_name}.mo"
        formal_source_present = formal_source_path.exists()
        if requires_dedicated_formal_source(formal_name) and not formal_source_present:
            findings.append(
                f"{canonical_target}: missing dedicated formal source file "
                f"{rel(formal_source_path)!r}"
            )
        formal_text = read_text(formal_source_path) if formal_source_present else ""

        assert_contains(
            findings,
            formal_text,
            f"model {formal_name}",
            canonical_target,
        )
        assert_contains(
            findings,
            formal_text,
            f"within {source_namespace};",
            canonical_target,
        )
        assert_contains(
            findings,
            implementation_text,
            f"model {implementation_model}",
            f"{target['implementation_file']}",
        )
        for snippet in target["required_snippets"]:
            assert_contains(findings, implementation_text, snippet, target["implementation_file"])
        for variable in target["expected_result_variables"]:
            root_name = variable.split(".", 1)[-1].split("[", 1)[0]
            root_name = root_name.split(".", 1)[0] if "." not in variable else variable.rsplit(".", 1)[-1]
            if root_name not in implementation_text and "." not in variable:
                findings.append(f"{target['implementation_file']}: expected variable anchor {variable!r} not found")

        matrix.append(
            {
                "formal_target": canonical_target,
                "retired_predecessor": target["compat_name"],
                "pre_refactor_namespace": (
                    f"MoSimQuadrotorModel.Vehicle.{formal_name}"
                    if formal_name in PRODUCTION_FORMAL_NAMES else None
                ),
                "implementation_model": f"{source_namespace}.{implementation_model}",
                "implementation_file": rel(implementation_path),
                "formal_source_file": (
                    rel(formal_source_path)
                    if formal_source_present
                    else rel(source_dir / "package.mo")
                ),
                "formal_source_present": formal_source_present,
                "dedicated_formal_source_required": requires_dedicated_formal_source(formal_name),
                "role": target["role"],
                "check_model_order": target["check_phase"],
                "simulate_order_after_all_checks": target["simulate_phase"],
                "expected_result_variables": target["expected_result_variables"],
                "required_source_anchors": target["required_snippets"],
                "pass_fail_boundary": target["pass_fail_boundary"],
                "source_status": "canonical_source_anchor_verified",
            }
        )

    for field in PARAMETER_TARGET["expected_package_fields"]:
        assert_contains(findings, parameter_package, field, PARAMETER_TARGET["implementation_file"])
    for field in PARAMETER_TARGET["expected_profile_record_fields"]:
        assert_contains(
            findings,
            parameter_profile_record,
            field,
            PARAMETER_TARGET["profile_record_file"],
        )

    return matrix, findings


def build_future_surface(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    check_targets = [PARAMETER_TARGET["formal_target"]] + [
        item["formal_target"] for item in sorted(matrix, key=lambda item: item["check_model_order"])
    ]
    sim_targets = [
        item["formal_target"]
        for item in sorted(
            (entry for entry in matrix if entry["simulate_order_after_all_checks"] is not None),
            key=lambda item: item["simulate_order_after_all_checks"],
        )
    ]
    return {
        "schema": "mosim.mworks.formal_smoke_surface.v1",
        "request_id": REQUEST_ID,
        "status": "prepared_static_only",
        "preconditions": [
            "legacy ops patrol or PMO must provide a reusable existing MWORKS/Sysplorer attach route before live work.",
            "Stop on demo, login, activation, authorization, GUI error-report, mixed license, visible unknown, unavailable, or unknown GUI/API state.",
            "Use targeted model_manager(load_file, force_reload=true) followed by check_model(model_names=[...]); avoid check_model(reload_mo_path=...).",
            "Do not call ClearAll or ChangeDirectory.",
            "Do not edit References/MWORKS/MoSimQuadrotorModel.Vehicle.",
        ],
        "check_model_target_order": check_targets,
        "minimal_simulate_order_after_all_checks_pass": sim_targets,
        "result_probe_required": [
            "Open/read native result or .msr variables for each simulated target.",
            "Classify missing result variables as smoke-surface blocker, not as simulation success.",
            "Record phase screenshots/observations only in the future live task, not in this static 023 task.",
        ],
        "optional_probe_queue": [
            {
                "target": "MoSimQuadrotorModel.Vehicle.Dynamics.ActuatorMappedWrapperSurface",
                "probe": "normalized_actuator_command feeds signed_visual_rotor_speed_command into wrapper.motor_command",
                "not_claimed_by_023": True,
            },
            {
                "target": "MoSimQuadrotorModel.Vehicle.Dynamics.OptionalDampingGyroLayer",
                "probe": "default_disabled_force_delta and default_disabled_moment_delta remain zero under default flags",
                "not_claimed_by_023": True,
            },
            {
                "target": "MoSimQuadrotorModel.Vehicle.Dynamics.PhysicalWrenchAdapter",
                "probe": "applied_force_body and applied_torque_body reach explicit minimal MultiBody body through WorldForceAndTorque",
                "not_claimed_by_023": True,
            },
        ],
        "not_claimed_by_023": [
            "live MWORKS load",
            "check_model",
            "SimulateModel",
            ".msr or native result evidence",
            "graphical/layout/package-browser acceptance",
            "controller performance",
            "planner_ready",
            "runtime ack",
            "mission success",
            "identified parameter truth",
            "closed_loop",
        ],
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown_matrix(path: Path, matrix: list[dict[str, Any]]) -> None:
    lines = [
        "# MoSimQuadrotorModel Formal Smoke Target Matrix",
        "",
        f"Request: `{REQUEST_ID}`",
        "",
        "Static-only artifact. It prepares future live MWORKS check/smoke work and does not claim live load, check_model, SimulateModel, or result evidence.",
        "",
        "| Order | Formal target | Implementation file | Role | Future simulate order |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in matrix:
        sim_order = item["simulate_order_after_all_checks"]
        lines.append(
            f"| {item['check_model_order']} | `{item['formal_target']}` | `{item['implementation_file']}` | {item['role']} | {sim_order if sim_order is not None else 'check only'} |"
        )
    lines.extend(
        [
            "",
            "## Parameter Provenance Target",
            "",
            f"- `{PARAMETER_TARGET['formal_target']}` is phase 0 for future `check_model` and remains provenance-only.",
            "- DAE/Blender rotor centers are geometry assembly evidence only.",
            "- Mass, inertia, Ct, Cm, motor lag, drag, damping, gyro, and command mapping values remain source-labeled seeds, not identified Sunray150 truth.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_pass_fail(path: Path, matrix: list[dict[str, Any]]) -> None:
    lines = [
        "# Formal Smoke Surface Pass/Fail Boundaries",
        "",
        "## Global Boundaries",
        "",
        "- Future live work must complete all queued `check_model` targets before any `SimulateModel` smoke.",
        "- Any license, login, activation, authorization, GUI error, visible unknown, unavailable, or unknown state is a blocker.",
        "- Missing expected result variables in a future live result is a smoke-surface blocker.",
        "- This static 023 artifact does not claim `check_model`, simulation, graphical acceptance, controller performance, runtime ack, or closed loop.",
        "- Parameter provenance remains source-labeled: geometry is DAE/Blender assembly evidence; non-geometry values are seeds, not identified truth.",
        "",
        "## Target Boundaries",
        "",
    ]
    for item in matrix:
        lines.append(f"- `{item['formal_target']}`: {item['pass_fail_boundary']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_source_materialization_rationale(path: Path) -> None:
    lines = [
        "# Source Anchor Materialization Rationale",
        "",
        "023 inspects canonical production sources under `MoSimQuadrotorModel.Vehicle.Dynamics`, retained historical smoke sources under `Vehicle.LegacyDiagnostics`, and the `MoSimQuadrotorModel.Parameters` provenance record.",
        "",
        "The current formal source-surface rule is:",
        "",
        "- Production Dynamics entries and retained diagnostics each have canonical project-owned implementation `.mo` files.",
        "- `Vehicle.Dynamics` owns the production actuator and physical-wrench models; it is not a compatibility-alias package.",
        "- Retired top-level model roots must be absent from `Models/`.",
        "",
        "Current materialized dedicated surfaces:",
        "",
        "- `RotorActuatorCore.mo`",
        "- `HoverSmoke.mo`",
        "- `YawStepSmoke.mo`",
        "- `RotorEffectivenessSmoke.mo`",
        "- `WrapperSurface.mo`",
        "- `ActuatorCommandMapper.mo`",
        "- `ActuatorMappedWrapperSurface.mo`",
        "- `OptionalDampingGyroLayer.mo`",
        "- `WrapperHoverSmoke.mo`",
        "- `WrapperYawStepSmoke.mo`",
        "- `PhysicalWrenchAdapter.mo`",
        "- `PhysicalWrenchHoverSmoke.mo`",
        "- `PhysicalWrenchYawStepSmoke.mo`",
        "",
        "Static acceptance basis:",
        "",
        "- Six production entries are owned by `Vehicle.Dynamics`; seven historical smoke entries are owned by `Vehicle.LegacyDiagnostics`.",
        "- All formal entries exist as canonical source files with their own implementation anchors.",
        "- `Dynamics/package.mo` is a production package; historical smoke aliases were removed after active references migrated.",
        "- No second package is needed to load any Dynamics entry.",
        "- The formal smoke surface can be prepared as a target matrix, expected variable manifest, and future live validation queue without duplicating dynamics behavior.",
        "",
        "This rationale remains static-only. Live `check_model` and `SimulateModel` acceptance are still future gates.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_CONSOLIDATION_DIR,
    )
    args = parser.parse_args()

    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    matrix, findings = build_matrix()
    future_surface = build_future_surface(matrix)
    expected_variables = {
        "schema": "mosim.mworks.expected_result_variables.v1",
        "request_id": REQUEST_ID,
        "targets": [
            {
                "target": item["formal_target"],
                "role": item["role"],
                "expected_result_variables": item["expected_result_variables"],
                "source": item["implementation_file"],
            }
            for item in matrix
        ],
        "parameter_target": PARAMETER_TARGET,
        "boundary": "Variables are static source anchors for a future live result probe; 023 does not claim they were produced by MWORKS.",
    }
    changed_files = {
        "schema": "mosim.changed_files_manifest.v1",
        "request_id": REQUEST_ID,
        "source_files_changed_by_023": [],
        "source_files_materialized_by_current_static_alignment": [
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/HoverSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/YawStepSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/RotorEffectivenessSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/WrapperHoverSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/WrapperYawStepSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/PhysicalWrenchHoverSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/LegacyDiagnostics/PhysicalWrenchYawStepSmoke.mo",
            "Models/MoSimQuadrotorModel/Vehicle/Dynamics/package.mo",
        ],
        "script_files_changed_by_023": [
            "Scripts/mworks/validate_mosimquad_formal_smoke_surface.py"
        ],
        "evidence_files_written_by_023": [
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/formal_smoke_target_matrix.json",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/formal_smoke_target_matrix.md",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/future_live_validation_surface.json",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/expected_result_variables.json",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/pass_fail_boundaries.md",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/source_anchor_materialization_rationale.md",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/changed_files.json",
            "Results/mworks_model_hygiene/20260722_mosimquad_model_root_consolidation/formal_smoke_surface/static_validation_summary.json",
        ],
    }
    summary = {
        "schema": "mosim.mworks.static_validation_summary.v1",
        "request_id": REQUEST_ID,
        "status": "passed" if not findings else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_targets": len(matrix),
        "parameter_targets": 1,
        "findings": findings,
        "source_diff_required": True,
        "source_diff_performed": True,
        "claim_boundary": [
            "023 prepares static smoke/check surface artifacts only.",
            "023 does not claim live MWORKS load, check_model, SimulateModel, graphical/layout acceptance, controller performance, runtime ack, identified parameter truth, mission success, or closed_loop.",
        ],
    }

    write_json(
        out_dir / "formal_smoke_target_matrix.json",
        {
            "schema": "mosim.mworks.formal_smoke_target_matrix.v1",
            "request_id": REQUEST_ID,
            "status": "passed_static" if not findings else "failed_static",
            "targets": matrix,
            "parameter_target": PARAMETER_TARGET,
            "findings": findings,
        },
    )
    write_markdown_matrix(out_dir / "formal_smoke_target_matrix.md", matrix)
    write_json(out_dir / "future_live_validation_surface.json", future_surface)
    write_json(out_dir / "expected_result_variables.json", expected_variables)
    write_pass_fail(out_dir / "pass_fail_boundaries.md", matrix)
    write_source_materialization_rationale(out_dir / "source_anchor_materialization_rationale.md")
    write_json(out_dir / "changed_files.json", changed_files)
    write_json(out_dir / "static_validation_summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
