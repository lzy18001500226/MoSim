#!/usr/bin/env python3
"""Statically verify the locked Sunray150 virtual PX4 Classic parameter contract.

This checker is intentionally source-only. It does not start MWORKS, Gazebo,
ROS, PX4, RViz, or Unreal, and it does not promote the virtual seed to
identified real-aircraft truth.
"""

from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "Config" / "plant" / "sunray150_virtual_px4_classic_profile.json"
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "quality"
    / "sunray150_virtual_px4_classic_profile"
    / "static_profile_check.json"
)

PARAMETER_RECORD = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Parameters"
    / "Sunray150VirtualPx4Classic.mo"
)
PARAMETER_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters" / "package.mo"
PARAMETER_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters" / "package.order"
ROS1_SYNC = ROOT / "Scripts" / "sunray" / "sync_assembled_model_into_sunray_ros1.py"
PX4CTRL_RUNTIME_CONFIG = (
    ROOT
    / "References"
    / "Lab"
    / "planning_local"
    / "Fast-Drone-250"
    / "src"
    / "realflight_modules"
    / "px4ctrl"
    / "config"
    / "ctrl_param_fpv.yaml"
)

COMPATIBILITY_SDFS = {
    "assembled": ROOT / "Config" / "gazebo" / "models" / "sunray150_assembled" / "model.sdf",
    "assembled_motor_test": (
        ROOT
        / "Config"
        / "gazebo"
        / "models"
        / "sunray150_assembled_motor_test"
        / "model.sdf"
    ),
}

FORMAL_PROFILE_FILES = {
    "rotor_core": ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "RotorActuatorCore.mo",
    "command_mapper": ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "ActuatorCommandMapper.mo",
    "wrapper_surface": ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "WrapperSurface.mo",
    "physical_wrench": ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "PhysicalWrenchAdapter.mo",
    "plant_adapter": ROOT / "Models" / "MoSimQuadrotorModel" / "Plant" / "package.mo",
}

DFBC_GRAPHICAL_MODELS = [
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Controllers"
    / "GraphicalMIL"
    / "GeometricFlatness"
    / name
    for name in (
        "MoSim_P10_DFBC_HIGH_ORDER_ATTITUDE_MIL.mo",
        "MoSim_P10_DFBC_HIGH_ORDER_BODYRATE_MIL.mo",
        "MoSim_P10_DFBC_SMOOTH_ROBUST_ATTITUDE_MIL.mo",
        "MoSim_P10_DFBC_SMOOTH_ROBUST_BODYRATE_MIL.mo",
    )
]

CONTROLLER_ANCHORS = {
    PX4CTRL_RUNTIME_CONFIG: [
        "mass        : 1.0 # kg, locked virtual Sunray150 takeoff mass",
        "gra         : 9.80665",
        "estimate_enable: false",
        "hover_percentage: 0.37",
    ],
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Controllers"
    / "GraphicalMIL"
    / "ClassicRobust"
    / "MoSim_P10_HINF_HOVER_WRENCH_MIL.mo": [
        "mass_source(k=1.0)",
        "gravity_source(k=9.80665)",
        "hover_percentage_source(k=0.37)",
    ],
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Controllers"
    / "GraphicalMIL"
    / "ClassicRobust"
    / "MoSim_Classic_CFunction_Sysblock.mo": ["1.0, 9.80665, 0.37"],
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Controllers"
    / "GraphicalMIL"
    / "ClassicRobust"
    / "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock.mo": [
        "params->mass = 1.0;",
        "params->gravity = 9.80665;",
        "params->hover_percentage = 0.37;",
    ],
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "LiveIntegration"
    / "RT1OfficialPidShadow50Hz.mo": [
        "sunray150_virtual_px4_classic_mass_kg",
        "sunray150_virtual_px4_classic_gravity_mps2",
        "sunray150_virtual_px4_classic_mworks_controller_hover_percentage",
    ],
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "LiveIntegration"
    / "RT1OfficialPidShadow200Hz.mo": [
        "sunray150_virtual_px4_classic_mass_kg",
        "sunray150_virtual_px4_classic_gravity_mps2",
        "sunray150_virtual_px4_classic_mworks_controller_hover_percentage",
    ],
    ROOT / "Scripts" / "control_platform" / "run_linear_robust_attitude_thrust_gate.py": [
        "1.0 * math.sqrt",
        "1.0 * 9.80665 / 0.37",
    ],
    ROOT / "Scripts" / "control_platform" / "run_wave_a_controller_gate.py": [
        "9.80665 / 0.37",
        "1.0 * 9.80665 / 0.37",
    ],
    ROOT / "Scripts" / "control_platform" / "run_wave_b_smc_gate.py": ["9.80665 / 0.37"],
    ROOT / "Scripts" / "control_platform" / "synthesize_wave_b_hinf_gain.m": ["gravity = 9.80665;"],
    ROOT / "Scripts" / "sunray" / "px4ctrl_golden_slice" / "run_px4ctrl_g7b_gazebo_ab_gate.sh": [
        "PX4CTRL_HOVER_PERCENTAGE:-0.37"
    ],
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def append_finding(
    findings: list[dict[str, str]], code: str, message: str, target: Path | str
) -> None:
    findings.append({"code": code, "message": message, "target": str(target)})


def close_enough(actual: float, expected: float, tolerance: float = 1.0e-12) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance)


def require_value(
    findings: list[dict[str, str]], name: str, actual: float, expected: float
) -> None:
    if not close_enough(actual, expected):
        append_finding(
            findings,
            "profile_value_mismatch",
            f"{name}={actual!r}, expected {expected!r}",
            PROFILE_PATH,
        )


def require_text_anchors(
    findings: list[dict[str, str]], path: Path, anchors: list[str], category: str
) -> list[str]:
    if not path.exists():
        append_finding(findings, "missing_source", f"{category} source is missing", path)
        return anchors
    text = path.read_text(encoding="utf-8")
    missing = [anchor for anchor in anchors if anchor not in text]
    if missing:
        append_finding(
            findings,
            "missing_anchor",
            f"{category} is missing anchors: {missing}",
            path,
        )
    return missing


def parse_sdf_link_masses(path: Path) -> dict[str, float]:
    root = ET.parse(path).getroot()
    masses: dict[str, float] = {}
    for link in root.findall(".//link"):
        name = link.attrib.get("name")
        mass = link.find("./inertial/mass")
        if name and mass is not None and mass.text:
            masses[name] = float(mass.text.strip())
    return masses


def validate_profile(profile: dict[str, Any], findings: list[dict[str, str]]) -> dict[str, Any]:
    if profile.get("schema") != "mosim.sunray150_virtual_px4_classic_profile.v1":
        append_finding(findings, "profile_schema", "unexpected profile schema", PROFILE_PATH)
    if profile.get("profile_id") != "sunray150_virtual_px4_classic_v1":
        append_finding(findings, "profile_id", "unexpected profile id", PROFILE_PATH)

    mass = profile["mass_accounting"]
    total_mass = float(mass["total_takeoff_mass_kg"])
    gravity = float(profile["gravity_mps2"])
    rotor_count = int(mass["rotor_count"])
    rotor_mass = float(mass["rotor_mass_kg_each"])
    require_value(findings, "total_takeoff_mass_kg", total_mass, 1.0)
    require_value(findings, "gravity_mps2", gravity, 9.80665)
    require_value(findings, "rotor_count", float(rotor_count), 4.0)
    require_value(findings, "rotor_mass_kg_each", rotor_mass, 0.005)

    closures = {
        "mworks_quad_chassis": float(mass["mworks_quad_chassis"]["body_mass_kg"]) + rotor_count * rotor_mass,
        "mworks_physical_wrench": float(mass["mworks_physical_wrench"]["one_body_mass_kg"]),
        "ros1_nested_mid360": (
            float(mass["ros1_gazebo_classic"]["nested_mid360"]["base_link_mass_kg"])
            + float(mass["ros1_gazebo_classic"]["nested_mid360"]["flight_imu_mass_kg"])
            + rotor_count * rotor_mass
            + float(mass["ros1_gazebo_classic"]["nested_mid360"]["mid360_nested_model_mass_kg"])
            + float(mass["ros1_gazebo_classic"]["nested_mid360"]["camera_sensor_model_mass_kg_each"])
            * int(mass["ros1_gazebo_classic"]["nested_mid360"]["camera_sensor_model_count"])
        ),
        "ros1_inline_mid360": (
            float(mass["ros1_gazebo_classic"]["inline_mid360"]["base_link_mass_kg"])
            + float(mass["ros1_gazebo_classic"]["inline_mid360"]["flight_imu_mass_kg"])
            + rotor_count * rotor_mass
            + float(mass["ros1_gazebo_classic"]["inline_mid360"]["camera_sensor_model_mass_kg_each"])
            * int(mass["ros1_gazebo_classic"]["inline_mid360"]["camera_sensor_model_count"])
        ),
        "gazebo_sim_assembled": float(mass["gazebo_sim_assembled_compatibility"]["base_link_mass_kg"])
        + rotor_count * rotor_mass,
        "gazebo_sim_assembled_motor_test": float(
            mass["gazebo_sim_assembled_motor_test_compatibility"]["base_link_mass_kg"]
        )
        + rotor_count * rotor_mass,
        "px4ctrl_runtime": float(mass["px4ctrl_runtime_mass_kg"]),
    }
    for name, closure_mass in closures.items():
        require_value(findings, f"mass_closure.{name}", closure_mass, total_mass)

    rotor = profile["rotor"]
    expected_map = [0, 2, 1, 3]
    if rotor["gazebo_to_mworks_indices"] != expected_map:
        append_finding(findings, "rotor_reorder", "expected Gazebo-to-MWORKS map [0, 2, 1, 3]", PROFILE_PATH)
    reordered_centers = [rotor["gazebo_centers_m"][index] for index in expected_map]
    if reordered_centers != rotor["mworks_centers_m"]:
        append_finding(findings, "rotor_center_reorder", "MWORKS centers do not match reordered Gazebo centers", PROFILE_PATH)
    reordered_directions = [rotor["gazebo_turning_direction"][index] for index in expected_map]
    if reordered_directions != ["ccw", "cw", "ccw", "cw"]:
        append_finding(findings, "rotor_direction_reorder", "unexpected MWORKS rotor directions after reorder", PROFILE_PATH)
    if rotor["mworks_spin_command_sign"] != [1, -1, 1, -1]:
        append_finding(findings, "mworks_spin_sign", "unexpected MWORKS command signs", PROFILE_PATH)
    if rotor["mworks_yaw_direction"] != [1, -1, 1, -1]:
        append_finding(findings, "mworks_yaw_sign", "unexpected MWORKS yaw signs", PROFILE_PATH)

    motor = profile["motor_model"]
    motor_constant = float(motor["motor_constant_n_per_rad_s2"])
    slowdown = float(motor["rotor_velocity_slowdown_sim"])
    require_value(findings, "motor_constant_n_per_rad_s2", motor_constant, 5.84e-6)
    require_value(findings, "moment_constant_ratio_m", float(motor["moment_constant_ratio_m"]), 0.06)
    require_value(findings, "motor_time_constant_up_s", float(motor["time_constant_up_s"]), 0.0125)
    require_value(findings, "motor_time_constant_down_s", float(motor["time_constant_down_s"]), 0.025)
    require_value(findings, "max_rotor_velocity_rad_s", float(motor["max_rotor_velocity_rad_s"]), 1100.0)
    require_value(findings, "rotor_velocity_slowdown_sim", slowdown, 10.0)
    require_value(
        findings,
        "mworks_visual_thrust_coefficient",
        float(motor["mworks_visual_thrust_coefficient_n_per_rad_s2"]),
        motor_constant * slowdown * slowdown,
    )
    hover_physical = math.sqrt(total_mass * gravity / (rotor_count * motor_constant))
    require_value(findings, "hover_physical_rotor_speed_rad_s", float(motor["hover_physical_rotor_speed_rad_s"]), hover_physical)
    hover_visual = hover_physical / slowdown
    require_value(findings, "hover_visual_rotor_speed_rad_s", float(motor["hover_visual_rotor_speed_rad_s"]), hover_visual)
    require_value(
        findings,
        "hover_normalized_command",
        float(motor["hover_normalized_command"]),
        hover_visual / float(motor["max_visual_rotor_speed_rad_s"]),
    )
    require_value(
        findings,
        "max_total_thrust_n",
        float(motor["max_total_thrust_n"]),
        rotor_count * motor_constant * float(motor["max_rotor_velocity_rad_s"]) ** 2,
    )

    calibration = profile["controller_calibration"]
    require_value(findings, "mworks_controller_hover_percentage", float(calibration["mworks_controller_hover_percentage"]), 0.37)
    require_value(findings, "px4ctrl_hov_percent", float(calibration["px4ctrl_hov_percent"]), 0.37)
    if calibration.get("px4ctrl_thrust_estimate_enable") is not False:
        append_finding(
            findings,
            "profile_value_mismatch",
            "px4ctrl_thrust_estimate_enable must be false for the nominal virtual profile",
            PROFILE_PATH,
        )
    return {"mass_closures_kg": closures, "hover_physical_rad_s": hover_physical, "hover_visual_rad_s": hover_visual}


def validate_sdf_models(profile: dict[str, Any], findings: list[dict[str, str]]) -> dict[str, Any]:
    total_mass = float(profile["mass_accounting"]["total_takeoff_mass_kg"])
    summaries: dict[str, Any] = {}
    for name, path in COMPATIBILITY_SDFS.items():
        if not path.exists():
            append_finding(findings, "missing_sdf", "compatibility SDF is missing", path)
            continue
        try:
            masses = parse_sdf_link_masses(path)
        except (ET.ParseError, ValueError) as exc:
            append_finding(findings, "invalid_sdf", f"cannot parse SDF masses: {exc}", path)
            continue
        expected_names = {"base_link", "rotor_0", "rotor_1", "rotor_2", "rotor_3"}
        if set(masses) != expected_names:
            append_finding(findings, "sdf_link_surface", f"unexpected inertial link set: {sorted(masses)}", path)
        summed_mass = sum(masses.values())
        if not close_enough(summed_mass, total_mass):
            append_finding(findings, "sdf_mass_closure", f"link masses sum to {summed_mass!r}, expected {total_mass!r}", path)
        summaries[name] = {"path": relative(path), "link_masses_kg": masses, "sum_kg": summed_mass}
    return summaries


def build_summary() -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if not PROFILE_PATH.exists():
        append_finding(findings, "missing_profile", "virtual profile is missing", PROFILE_PATH)
        return {"schema": "mosim.sunray150_virtual_px4_classic_profile_check.v1", "status": "failed", "findings": findings}
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile_summary = validate_profile(profile, findings)

    record_anchors = [
        "parameter Real gravity_mps2(unit = \"m/s2\") = 9.80665;",
        "parameter Real takeoff_mass_kg(unit = \"kg\") = 1.0;",
        "parameter Real mworks_quad_chassis_body_mass_kg(unit = \"kg\") = 0.980;",
        "parameter Real motor_constant_n_per_rad_s2(unit = \"N/(rad/s)^2\") = 5.84e-6;",
        "parameter Real moment_constant_ratio_m(unit = \"m\") = 0.06;",
        "parameter Real mworks_controller_hover_percentage = 0.37",
        "parameter Real px4ctrl_hov_percent = 0.37;",
        "parameter Boolean px4ctrl_thrust_estimate_enable = false",
    ]
    package_anchors = [
        "constant Real sunray150_virtual_px4_classic_mass_kg(unit = \"kg\") = 1.0",
        "constant Real sunray150_virtual_px4_classic_gravity_mps2(unit = \"m/s2\") = 9.80665",
        "constant Real sunray150_virtual_px4_classic_mworks_controller_hover_percentage = 0.37",
    ]
    missing_record = require_text_anchors(findings, PARAMETER_RECORD, record_anchors, "Modelica virtual-profile record")
    missing_package = require_text_anchors(findings, PARAMETER_PACKAGE, package_anchors, "Modelica parameter package")
    missing_order = require_text_anchors(
        findings, PARAMETER_ORDER, ["Sunray150VirtualPx4Classic", "Sunray150ParameterProvenance"], "Modelica parameter package order"
    )

    formal_missing = {
        name: require_text_anchors(
            findings,
            path,
            ["Sunray150VirtualPx4Classic"],
            f"formal profile consumer {name}",
        )
        for name, path in FORMAL_PROFILE_FILES.items()
    }
    sync_missing = require_text_anchors(
        findings,
        ROS1_SYNC,
        [
            "VIRTUAL_PROFILE_RELATIVE_PATH",
            "load_virtual_profile",
            "motor[\"motor_constant_n_per_rad_s2\"]",
            "motor[\"rotor_velocity_slowdown_sim\"]",
            "rotor[\"gazebo_turning_direction\"]",
        ],
        "ROS1 profile synchronization source",
    )
    graphical_missing = {
        relative(path): require_text_anchors(
            findings,
            path,
            ["mass_source(k=1.0)", "gravity_source(k=9.80665)", "hover_percentage_source(k=0.37)"],
            "DFBC graphical fixture",
        )
        for path in DFBC_GRAPHICAL_MODELS
    }
    controller_missing = {
        relative(path): require_text_anchors(findings, path, anchors, "controller or gate default")
        for path, anchors in CONTROLLER_ANCHORS.items()
    }
    sdf_summary = validate_sdf_models(profile, findings)

    return {
        "schema": "mosim.sunray150_virtual_px4_classic_profile_check.v1",
        "status": "passed" if not findings else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "live_runtime_touched": False,
        "profile": relative(PROFILE_PATH),
        "profile_summary": profile_summary,
        "modelica_mirror": {
            "record_missing_anchors": missing_record,
            "package_missing_anchors": missing_package,
            "package_order_missing_anchors": missing_order,
        },
        "formal_profile_consumers": formal_missing,
        "ros1_sync_missing_anchors": sync_missing,
        "graphical_fixture_missing_anchors": graphical_missing,
        "controller_gate_missing_anchors": controller_missing,
        "compatibility_sdf": sdf_summary,
        "claim_boundary": [
            "This verifies static configuration consistency only.",
            "The profile is a virtual seed, not measured Sunray150 truth.",
            "A short px4ctrl hover and yaw-sign check remain required before current runtime-performance claims.",
        ],
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    summary = build_summary()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
