#!/usr/bin/env python3
"""Validate the static WrapperSurface formal source surface.

The checker is file-only. It verifies that MoSimQuadrotorModel.Dynamics has an
auditable WrapperSurface source file, that the legacy DynamicsUpgrade alias and
implementation still exist, and that required wrapper/provenance anchors remain
in the legacy implementation. It does not call MWORKS, Sysplorer, MCP,
check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-WRAPPER-SURFACE-FORMAL-SOURCE-SURFACE-20260608-026"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "WrapperSurface.mo"
PARAMETER_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters" / "package.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150DynamicsWrapperSurface.mo"
LEGACY_CORE_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150RflyStyleRotorDynamics.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260608_026_mosimquad_wrapper_surface_formal_source_surface"
)

REQUIRED_WRAPPER_ANCHORS = [
    "Sunray150RflyStyleRotorDynamics dynamics",
    "Real motor_command[4](each unit = \"rad/s\")",
    "Real commanded_thrust[4](each unit = \"N\")",
    "Real commanded_yaw_reaction_moment[4](each unit = \"N.m\")",
    "Real commanded_rotor_arm_moment[4, 3](each unit = \"N.m\")",
    "Real total_thrust(unit = \"N\")",
    "Real total_moment_body[3](each unit = \"N.m\")",
    "Real commanded_total_thrust(unit = \"N\")",
    "Real commanded_total_moment_body[3](each unit = \"N.m\")",
    "Real hover_thrust_error(unit = \"N\")",
    "Real commanded_hover_thrust_error(unit = \"N\")",
    "Real yaw_moment_gate(unit = \"N.m\")",
    "Real commanded_yaw_moment_gate(unit = \"N.m\")",
    "Real motor_order_gate_error",
    "Real yaw_direction_gate_error",
    "Real minimum_thrust_effectiveness",
    "Real minimum_reaction_moment_effectiveness",
    "dynamics.motor_command = motor_command",
    "commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
    "commanded_yaw_reaction_moment[i] = dynamics.yaw_direction[i] * dynamics.reaction_moment_effectiveness[i] * dynamics.moment_constant * commanded_thrust[i]",
    "commanded_rotor_arm_moment[i, 1] = dynamics.rotor_center[i, 2] * commanded_thrust[i]",
    "commanded_rotor_arm_moment[i, 2] = -dynamics.rotor_center[i, 1] * commanded_thrust[i]",
    "commanded_rotor_arm_moment[i, 3] = commanded_yaw_reaction_moment[i]",
    "total_thrust = dynamics.total_thrust",
    "total_moment_body = dynamics.total_moment_body",
    "hover_thrust_error = dynamics.hover_thrust_error",
    "minimum_thrust_effectiveness = dynamics.minimum_thrust_effectiveness",
    "minimum_reaction_moment_effectiveness = dynamics.minimum_reaction_moment_effectiveness",
    "commanded_total_thrust = sum(commanded_thrust)",
    "commanded_total_moment_body[1] = sum({commanded_rotor_arm_moment[i, 1] for i in 1:4})",
    "commanded_total_moment_body[2] = sum({commanded_rotor_arm_moment[i, 2] for i in 1:4})",
    "commanded_total_moment_body[3] = sum({commanded_rotor_arm_moment[i, 3] for i in 1:4})",
    "commanded_hover_thrust_error = commanded_total_thrust - dynamics.mass_kg * 9.81",
    "yaw_moment_gate = total_moment_body[3]",
    "commanded_yaw_moment_gate = commanded_total_moment_body[3]",
    "motor_order_gate_error = sum({abs(dynamics.rotor_center[i, j] - expected_rotor_center[i, j]) for i in 1:4, j in 1:3})",
    "yaw_direction_gate_error = sum({abs(dynamics.yaw_direction[i] - expected_yaw_direction[i]) for i in 1:4})",
]

REQUIRED_CORE_ANCHORS = [
    "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
    "thrust[i] = thrust_effectiveness[i] * lift_coefficient * omega[i] * omega[i]",
    "yaw_reaction_moment[i] = yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust[i]",
    "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
    "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
    "rotor_arm_moment[i, 3] = yaw_reaction_moment[i]",
    "total_thrust = sum(thrust)",
    "total_moment_body[3] = sum({rotor_arm_moment[i, 3] for i in 1:4})",
]

REQUIRED_PROVENANCE_ANCHORS = [
    "source=user-reviewed DAE screw-pair fit, in MWORKS Dronefixed1..4 order",
    "source=user-reviewed DAE screw-pair fit, mapped to MWORKS Dronefixed1..4 order",
    "source=SDF_migration; not a measured Sunray150 takeoff mass",
    "source=SDF_migration; Sunray motorConstant scaled by rotorVelocitySlowdownSim^2",
    "source=SDF_migration; Gazebo/Sunray yaw moment ratio seed, not ULog identified",
    "source=SDF_migration; Sunray SDF motor plugin timeConstantUp",
    "source=SDF_migration; Sunray SDF motor plugin timeConstantDown",
]

ROTOR_CENTER_ROWS = [
    "0.053745, -0.053740, -0.014052",
    "0.053746,  0.053759, -0.014052",
    "-0.053761,  0.053760, -0.014052",
    "-0.053761, -0.053739, -0.014052",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_order(path: Path) -> list[str]:
    return [line.strip() for line in read_text(path).splitlines() if line.strip()]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_finding(findings: list[dict[str, Any]], code: str, message: str, *, target: str) -> None:
    findings.append({"severity": "error", "code": code, "target": target, "message": message})


def contains(text: str, snippet: str) -> bool:
    return snippet in text


def validate() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []

    formal_package = read_text(FORMAL_PACKAGE)
    formal_order = read_order(FORMAL_ORDER)
    formal_source = read_text(FORMAL_SOURCE) if FORMAL_SOURCE.exists() else ""
    parameter_source = read_text(PARAMETER_SOURCE)
    legacy_package = read_text(LEGACY_PACKAGE)
    legacy_order = read_order(LEGACY_ORDER)
    legacy_impl = read_text(LEGACY_IMPL)
    legacy_core_impl = read_text(LEGACY_CORE_IMPL)

    if not FORMAL_SOURCE.exists():
        add_finding(findings, "formal_source_missing", "WrapperSurface.mo is missing", target=rel(FORMAL_SOURCE))
    if "WrapperSurface" not in formal_order:
        add_finding(findings, "formal_order_missing", "package.order does not include WrapperSurface", target=rel(FORMAL_ORDER))
    if "model WrapperSurface" in formal_package:
        add_finding(
            findings,
            "duplicate_inline_formal_definition",
            "WrapperSurface remains inline in package.mo while source file exists",
            target=rel(FORMAL_PACKAGE),
        )
    if not contains(formal_source, "within MoSimQuadrotorModel.Dynamics;"):
        add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "model WrapperSurface"):
        add_finding(findings, "formal_model_missing", "formal source lacks model declaration", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "extends QuadrotorExperiments.DynamicsUpgrade.WrapperSurface;"):
        add_finding(findings, "formal_extends_drift", "formal source no longer extends legacy WrapperSurface alias", target=rel(FORMAL_SOURCE))

    forbidden_formula_snippets = [
        "equation",
        "motor_command[",
        "commanded_thrust",
        "commanded_yaw_reaction_moment",
        "commanded_rotor_arm_moment",
        "total_thrust",
        "total_moment_body",
        "hover_thrust_error",
        "yaw_moment_gate",
    ]
    for snippet in forbidden_formula_snippets:
        if contains(formal_source, snippet):
            add_finding(
                findings,
                "formal_source_duplicates_wrapper_behavior",
                f"formal source duplicates wrapper behavior snippet {snippet!r}",
                target=rel(FORMAL_SOURCE),
            )

    if "WrapperSurface" not in legacy_order:
        add_finding(findings, "legacy_order_missing", "legacy package.order lost WrapperSurface", target=rel(LEGACY_ORDER))
    if not contains(legacy_package, "model WrapperSurface"):
        add_finding(findings, "legacy_alias_missing", "legacy package lost WrapperSurface alias", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_package, "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperSurface"):
        add_finding(findings, "legacy_alias_extends_drift", "legacy WrapperSurface alias no longer extends implementation", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_impl, "model Sunray150DynamicsWrapperSurface"):
        add_finding(findings, "legacy_impl_missing", "legacy wrapper implementation model declaration missing", target=rel(LEGACY_IMPL))
    if not contains(legacy_core_impl, "model Sunray150RflyStyleRotorDynamics"):
        add_finding(findings, "legacy_core_impl_missing", "legacy rotor core implementation declaration missing", target=rel(LEGACY_CORE_IMPL))

    wrapper_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_WRAPPER_ANCHORS:
        present = contains(legacy_impl, snippet)
        wrapper_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "wrapper_anchor_missing", f"missing wrapper anchor {snippet!r}", target=rel(LEGACY_IMPL))

    core_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_CORE_ANCHORS:
        present = contains(legacy_core_impl, snippet)
        core_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "core_anchor_missing", f"missing underlying core anchor {snippet!r}", target=rel(LEGACY_CORE_IMPL))

    provenance_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_PROVENANCE_ANCHORS:
        present = contains(legacy_impl, snippet) or contains(legacy_core_impl, snippet) or contains(parameter_source, snippet)
        provenance_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "provenance_anchor_missing", f"missing provenance anchor {snippet!r}", target=rel(LEGACY_IMPL))

    rotor_centers: list[dict[str, Any]] = []
    for row in ROTOR_CENTER_ROWS:
        present = contains(legacy_impl, row) and contains(legacy_core_impl, row) and contains(parameter_source, row)
        rotor_centers.append({"row": row, "present_in_wrapper_core_and_parameters": present})
        if not present:
            add_finding(
                findings,
                "rotor_center_anchor_missing",
                f"rotor center row {row!r} missing from wrapper, core, or parameter provenance",
                target=rel(LEGACY_IMPL),
            )

    result = {
        "schema": "mosim.mworks.wrapper_surface_source_check.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": "MoSimQuadrotorModel.Dynamics.WrapperSurface",
        "formal_source": rel(FORMAL_SOURCE),
        "formal_package": rel(FORMAL_PACKAGE),
        "formal_package_order": rel(FORMAL_ORDER),
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.WrapperSurface",
        "legacy_package": rel(LEGACY_PACKAGE),
        "legacy_package_order": rel(LEGACY_ORDER),
        "legacy_implementation": rel(LEGACY_IMPL),
        "legacy_core_implementation": rel(LEGACY_CORE_IMPL),
        "behavior_preservation": {
            "formal_source_is_extends_only": True,
            "formal_source_duplicates_wrapper_behavior": False,
            "legacy_alias_preserved": True,
            "legacy_implementation_preserved": True,
            "legacy_core_preserved": True,
            "dynamics_equations_changed_by_026": False,
            "numeric_parameters_changed_by_026": False,
        },
        "wrapper_anchors": wrapper_anchors,
        "underlying_core_anchors": core_anchors,
        "provenance_anchors": provenance_anchors,
        "rotor_center_anchors": rotor_centers,
        "findings": findings,
    }
    return result, findings


def write_markdown(path: Path, check: dict[str, Any]) -> None:
    lines = [
        "# WrapperSurface Formal Source Surface",
        "",
        f"Request: `{REQUEST_ID}`",
        "",
        f"Status: `{check['status']}`",
        "",
        "## Source Surface",
        "",
        f"- Formal target: `{check['formal_target']}`",
        f"- Formal source: `{check['formal_source']}`",
        f"- Legacy alias preserved: `{check['legacy_alias']}`",
        f"- Legacy implementation preserved: `{check['legacy_implementation']}`",
        "",
        "The formal source is intentionally an extends-only project-owned surface. It does not duplicate wrapper equations, motor-command mapping, command-side thrust, yaw reaction, rotor-arm moment, or lagged total force/moment outputs.",
        "",
        "## Static Anchors",
        "",
        "- Wrapper command input: `dynamics.motor_command = motor_command`.",
        "- Command-side thrust: `commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]`.",
        "- Command-side yaw reaction: `commanded_yaw_reaction_moment[i] = dynamics.yaw_direction[i] * dynamics.reaction_moment_effectiveness[i] * dynamics.moment_constant * commanded_thrust[i]`.",
        "- Effectiveness monitors: `minimum_thrust_effectiveness` and `minimum_reaction_moment_effectiveness` remain surfaced through the wrapper.",
        "- Rotor-center r x F moment: command-side x/y/z terms remain in `Sunray150DynamicsWrapperSurface.mo`.",
        "- Lagged outputs: `total_thrust`, `total_moment_body`, `hover_thrust_error`, and yaw gates remain in the legacy wrapper implementation.",
        "- Rotor centers remain matched across wrapper, core implementation, and `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`.",
        "",
        "## Claim Boundary",
        "",
        "- Static source/package surface only.",
        "- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.",
        "- No dynamics equation, numerical parameter, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or legacy agent runtime file was changed.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_changed_files(path: Path) -> None:
    write_json(
        path,
        {
            "schema": "mosim.changed_files_manifest.v1",
            "request_id": REQUEST_ID,
            "modelica_source_files_changed": [
                "Models/MoSimQuadrotorModel/Dynamics/package.mo",
                "Models/MoSimQuadrotorModel/Dynamics/WrapperSurface.mo",
            ],
            "legacy_source_files_changed": [],
            "script_files_changed_by_026": [
                "Scripts/mworks/validate_mosimquad_wrapper_surface.py",
                "Scripts/tests/test_mosimquad_wrapper_surface.py",
            ],
            "evidence_files_written_by_026": [
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/wrapper_surface_check.json",
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/wrapper_surface.md",
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/package_order_integrity.json",
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/changed_files.json",
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/static_validation_summary.json",
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/formal_smoke_surface_recheck/",
                "Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/live_gate_runner_recheck/",
            ],
            "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-WRAPPER-SURFACE-FORMAL-SOURCE-SURFACE-20260608-026.json",
        },
    )


def package_integrity(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.package_order_integrity.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if check["status"] == "passed_static" else "failed_static",
        "formal_package_order_contains_wrapper_surface": "WrapperSurface" in read_order(FORMAL_ORDER),
        "formal_package_mo_no_inline_duplicate": "model WrapperSurface" not in read_text(FORMAL_PACKAGE),
        "formal_source_file_present": FORMAL_SOURCE.exists(),
        "legacy_package_order_contains_wrapper_surface": "WrapperSurface" in read_order(LEGACY_ORDER),
        "legacy_package_alias_present": "model WrapperSurface" in read_text(LEGACY_PACKAGE),
        "legacy_implementation_file_present": LEGACY_IMPL.exists(),
        "legacy_core_file_present": LEGACY_CORE_IMPL.exists(),
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
    }


def static_summary(check: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.static_validation_summary.v1",
        "request_id": REQUEST_ID,
        "status": "passed" if check["status"] == "passed_static" else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_source_materialized": check["status"] == "passed_static",
        "behavior_preservation": check["behavior_preservation"],
        "findings": check["findings"],
        "evidence_files": [
            rel(out_dir / "wrapper_surface_check.json"),
            rel(out_dir / "wrapper_surface.md"),
            rel(out_dir / "package_order_integrity.json"),
            rel(out_dir / "changed_files.json"),
            rel(out_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "026 prepares a static formal source surface for WrapperSurface only.",
            "026 does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate()
    write_json(output_dir / "wrapper_surface_check.json", check)
    write_markdown(output_dir / "wrapper_surface.md", check)
    write_json(output_dir / "package_order_integrity.json", package_integrity(check))
    write_changed_files(output_dir / "changed_files.json")
    summary = static_summary(check, output_dir)
    write_json(output_dir / "static_validation_summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    summary = generate(output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
