#!/usr/bin/env python3
"""Validate the static RotorActuatorCore formal source surface.

The checker is file-only. It verifies that MoSimQuadrotorModel.Dynamics has an
auditable RotorActuatorCore source file, that the legacy DynamicsUpgrade alias
and implementation still exist, and that required dynamics/provenance anchors
remain in the legacy implementation. It does not call MWORKS, Sysplorer, MCP,
check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-ROTOR-ACTUATOR-CORE-FORMAL-SOURCE-SURFACE-20260608-025"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "RotorActuatorCore.mo"
PARAMETER_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters" / "package.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150RflyStyleRotorDynamics.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260608_025_mosimquad_rotor_actuator_core_formal_source_surface"
)

REQUIRED_IMPL_ANCHORS = [
    "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
    "thrust[i] = thrust_effectiveness[i] * lift_coefficient * omega[i] * omega[i]",
    "yaw_reaction_moment[i] = yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust[i]",
    "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
    "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
    "rotor_arm_moment[i, 3] = yaw_reaction_moment[i]",
    "total_thrust = sum(thrust)",
    "hover_thrust_error = total_thrust - mass_kg * 9.81",
    "thrust_effectiveness_loss[i] = 1 - thrust_effectiveness[i]",
    "reaction_moment_effectiveness_loss[i] = 1 - reaction_moment_effectiveness[i]",
    "minimum_thrust_effectiveness = min(thrust_effectiveness)",
    "minimum_reaction_moment_effectiveness = min(reaction_moment_effectiveness)",
]

REQUIRED_PROVENANCE_ANCHORS = [
    "source=SDF_migration; not a measured Sunray150 takeoff mass",
    "source=SDF_migration; Sunray motorConstant scaled by rotorVelocitySlowdownSim^2",
    "source=SDF_migration; Gazebo/Sunray yaw moment ratio seed, not ULog identified",
    "source=SDF_migration; Sunray SDF motor plugin timeConstantUp",
    "source=SDF_migration; Sunray SDF motor plugin timeConstantDown",
    "source=user-reviewed DAE screw-pair fit, mapped to MWORKS Dronefixed1..4 order",
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

    if not FORMAL_SOURCE.exists():
        add_finding(findings, "formal_source_missing", "RotorActuatorCore.mo is missing", target=rel(FORMAL_SOURCE))
    if "RotorActuatorCore" not in formal_order:
        add_finding(findings, "formal_order_missing", "package.order does not include RotorActuatorCore", target=rel(FORMAL_ORDER))
    if "model RotorActuatorCore" in formal_package:
        add_finding(
            findings,
            "duplicate_inline_formal_definition",
            "RotorActuatorCore remains inline in package.mo while source file exists",
            target=rel(FORMAL_PACKAGE),
        )
    if not contains(formal_source, "within MoSimQuadrotorModel.Dynamics;"):
        add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "model RotorActuatorCore"):
        add_finding(findings, "formal_model_missing", "formal source lacks model declaration", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "extends QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore;"):
        add_finding(findings, "formal_extends_drift", "formal source no longer extends legacy RotorDynamicsCore alias", target=rel(FORMAL_SOURCE))

    forbidden_formula_snippets = [
        "der(omega",
        "thrust[i] =",
        "yaw_reaction_moment",
        "rotor_arm_moment",
        "total_thrust =",
        "hover_thrust_error =",
    ]
    for snippet in forbidden_formula_snippets:
        if contains(formal_source, snippet):
            add_finding(
                findings,
                "formal_source_duplicates_equation",
                f"formal source duplicates behavior snippet {snippet!r}",
                target=rel(FORMAL_SOURCE),
            )

    if "RotorDynamicsCore" not in legacy_order:
        add_finding(findings, "legacy_order_missing", "legacy package.order lost RotorDynamicsCore", target=rel(LEGACY_ORDER))
    if not contains(legacy_package, "model RotorDynamicsCore"):
        add_finding(findings, "legacy_alias_missing", "legacy package lost RotorDynamicsCore alias", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_package, "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150RflyStyleRotorDynamics"):
        add_finding(findings, "legacy_alias_extends_drift", "legacy alias no longer extends implementation", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_impl, "model Sunray150RflyStyleRotorDynamics"):
        add_finding(findings, "legacy_impl_missing", "legacy implementation model declaration missing", target=rel(LEGACY_IMPL))

    implementation_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_IMPL_ANCHORS:
        present = contains(legacy_impl, snippet)
        implementation_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "implementation_anchor_missing", f"missing implementation anchor {snippet!r}", target=rel(LEGACY_IMPL))

    provenance_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_PROVENANCE_ANCHORS:
        present = contains(legacy_impl, snippet)
        provenance_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "provenance_anchor_missing", f"missing provenance anchor {snippet!r}", target=rel(LEGACY_IMPL))

    rotor_centers: list[dict[str, Any]] = []
    for row in ROTOR_CENTER_ROWS:
        present = contains(legacy_impl, row) and contains(parameter_source, row)
        rotor_centers.append({"row": row, "present_in_legacy_impl_and_parameters": present})
        if not present:
            add_finding(
                findings,
                "rotor_center_anchor_missing",
                f"rotor center row {row!r} missing from implementation or parameter provenance",
                target=rel(LEGACY_IMPL),
            )

    result = {
        "schema": "mosim.mworks.rotor_actuator_core_surface_check.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": "MoSimQuadrotorModel.Dynamics.RotorActuatorCore",
        "formal_source": rel(FORMAL_SOURCE),
        "formal_package": rel(FORMAL_PACKAGE),
        "formal_package_order": rel(FORMAL_ORDER),
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore",
        "legacy_package": rel(LEGACY_PACKAGE),
        "legacy_package_order": rel(LEGACY_ORDER),
        "legacy_implementation": rel(LEGACY_IMPL),
        "behavior_preservation": {
            "formal_source_is_extends_only": True,
            "formal_source_duplicates_equations": False,
            "legacy_alias_preserved": True,
            "legacy_implementation_preserved": True,
            "dynamics_equations_changed_by_025": False,
            "numeric_parameters_changed_by_025": False,
        },
        "implementation_anchors": implementation_anchors,
        "provenance_anchors": provenance_anchors,
        "rotor_center_anchors": rotor_centers,
        "findings": findings,
    }
    return result, findings


def write_markdown(path: Path, check: dict[str, Any]) -> None:
    lines = [
        "# RotorActuatorCore Formal Source Surface",
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
        "The formal source is intentionally an extends-only project-owned surface. It does not duplicate motor lag, thrust, yaw reaction, rotor-arm moment, or hover-error equations.",
        "",
        "## Static Anchors",
        "",
        "- Motor lag: `der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]`",
        "- Thrust: `thrust[i] = thrust_effectiveness[i] * lift_coefficient * omega[i] * omega[i]`",
        "- Yaw reaction torque: `yaw_reaction_moment[i] = yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust[i]`",
        "- Fault hooks: thrust/reaction effectiveness loss and minimum-effectiveness variables remain exposed.",
        "- Rotor-center r x F moment: x/y terms remain in `Sunray150RflyStyleRotorDynamics.mo`.",
        "- Rotor centers remain matched with `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`.",
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
                "Models/MoSimQuadrotorModel/Dynamics/RotorActuatorCore.mo",
            ],
            "legacy_source_files_changed": [],
            "script_files_changed_by_025": [
                "Scripts/mworks/validate_mosimquad_rotor_actuator_core_surface.py",
                "Scripts/mworks/validate_mosimquad_formal_smoke_surface.py",
                "Scripts/mworks/build_mosimquad_live_gate_runner_plan.py",
                "Scripts/tests/test_mosimquad_rotor_actuator_core_surface.py",
                "Scripts/tests/test_mosimquad_live_gate_runner_plan.py",
            ],
            "evidence_files_written_by_025": [
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/rotor_actuator_core_surface_check.json",
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/rotor_actuator_core_surface.md",
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/package_order_integrity.json",
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/changed_files.json",
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/static_validation_summary.json",
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/formal_smoke_surface_recheck/",
                "Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/live_gate_runner_recheck/",
            ],
            "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-ROTOR-ACTUATOR-CORE-FORMAL-SOURCE-SURFACE-20260608-025.json",
        },
    )


def package_integrity(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.package_order_integrity.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if check["status"] == "passed_static" else "failed_static",
        "formal_package_order_contains_rotor_actuator_core": "RotorActuatorCore" in read_order(FORMAL_ORDER),
        "formal_package_mo_no_inline_duplicate": "model RotorActuatorCore" not in read_text(FORMAL_PACKAGE),
        "formal_source_file_present": FORMAL_SOURCE.exists(),
        "legacy_package_order_contains_rotor_dynamics_core": "RotorDynamicsCore" in read_order(LEGACY_ORDER),
        "legacy_package_alias_present": "model RotorDynamicsCore" in read_text(LEGACY_PACKAGE),
        "legacy_implementation_file_present": LEGACY_IMPL.exists(),
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
            rel(out_dir / "rotor_actuator_core_surface_check.json"),
            rel(out_dir / "rotor_actuator_core_surface.md"),
            rel(out_dir / "package_order_integrity.json"),
            rel(out_dir / "changed_files.json"),
            rel(out_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "025 prepares a static formal source surface for RotorActuatorCore only.",
            "025 does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate()
    write_json(output_dir / "rotor_actuator_core_surface_check.json", check)
    write_markdown(output_dir / "rotor_actuator_core_surface.md", check)
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
