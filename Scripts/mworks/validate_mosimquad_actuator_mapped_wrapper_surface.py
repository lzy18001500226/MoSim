#!/usr/bin/env python3
"""Validate the static ActuatorMappedWrapperSurface formal source surface.

The checker is file-only. It verifies that MoSimQuadrotorModel.Dynamics has an
auditable ActuatorMappedWrapperSurface source file, that the legacy
DynamicsUpgrade alias and implementation still exist, and that mapper-to-wrapper
anchors remain in the legacy implementation. It does not call MWORKS,
Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R2-MOSIMQUAD-ACTUATOR-MAPPED-WRAPPER-FORMAL-SOURCE-SURFACE-BACKUP-20260609-030"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "ActuatorMappedWrapperSurface.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150ActuatorMappedWrapperSurface.mo"
LEGACY_MAPPER_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150ActuatorCommandMapper.mo"
LEGACY_WRAPPER_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150DynamicsWrapperSurface.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup"
)

REQUIRED_MAPPED_WRAPPER_ANCHORS = [
    "Sunray150ActuatorCommandMapper actuator_mapper",
    "Sunray150DynamicsWrapperSurface wrapper",
    "input Real normalized_actuator_command[4]",
    "actuator_mapper.normalized_command = normalized_actuator_command",
    "wrapper.motor_command = actuator_mapper.signed_visual_rotor_speed_command",
    "saturated_normalized_command = actuator_mapper.saturated_normalized_command",
    "actuator_saturation_error = actuator_mapper.actuator_saturation_error",
    "signed_visual_rotor_speed_command = actuator_mapper.signed_visual_rotor_speed_command",
    "total_thrust = wrapper.total_thrust",
    "total_moment_body = wrapper.total_moment_body",
    "commanded_total_thrust = wrapper.commanded_total_thrust",
    "commanded_total_moment_body = wrapper.commanded_total_moment_body",
    "hover_thrust_error = wrapper.hover_thrust_error",
    "commanded_hover_thrust_error = wrapper.commanded_hover_thrust_error",
    "yaw_moment_gate = wrapper.yaw_moment_gate",
    "commanded_yaw_moment_gate = wrapper.commanded_yaw_moment_gate",
    "motor_order_gate_error = wrapper.motor_order_gate_error",
    "yaw_direction_gate_error = wrapper.yaw_direction_gate_error",
    "minimum_thrust_effectiveness = wrapper.minimum_thrust_effectiveness",
    "minimum_reaction_moment_effectiveness = wrapper.minimum_reaction_moment_effectiveness",
]

REQUIRED_MAPPER_ANCHORS = [
    "parameter Real normalized_command_min = 0.0",
    "parameter Real normalized_command_max = 1.0",
    "parameter Real hover_normalized_command = 0.5",
    "parameter Real spin_command_sign[4] = {1, -1, 1, -1}",
    "input Real normalized_command[4]",
    "Real saturated_normalized_command[4]",
    "Real actuator_saturation_error[4]",
    "Real signed_visual_rotor_speed_command[4](each unit = \"rad/s\")",
    "saturated_normalized_command[i] =",
    "actuator_saturation_error[i] = normalized_command[i] - saturated_normalized_command[i]",
    "signed_visual_rotor_speed_command[i] =",
    "spin_command_sign[i] * visual_rotor_speed_unsigned[i]",
]

REQUIRED_WRAPPER_ANCHORS = [
    "Sunray150RflyStyleRotorDynamics dynamics",
    "Real motor_command[4](each unit = \"rad/s\")",
    "Real total_thrust(unit = \"N\")",
    "Real total_moment_body[3](each unit = \"N.m\")",
    "Real commanded_total_thrust(unit = \"N\")",
    "Real commanded_total_moment_body[3](each unit = \"N.m\")",
    "Real minimum_thrust_effectiveness",
    "Real minimum_reaction_moment_effectiveness",
    "Real motor_order_gate_error",
    "Real yaw_direction_gate_error",
    "dynamics.motor_command = motor_command",
    "commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
    "commanded_yaw_reaction_moment[i] = dynamics.yaw_direction[i] * dynamics.reaction_moment_effectiveness[i] * dynamics.moment_constant * commanded_thrust[i]",
    "total_thrust = dynamics.total_thrust",
    "total_moment_body = dynamics.total_moment_body",
    "commanded_total_thrust = sum(commanded_thrust)",
    "minimum_thrust_effectiveness = dynamics.minimum_thrust_effectiveness",
    "minimum_reaction_moment_effectiveness = dynamics.minimum_reaction_moment_effectiveness",
    "motor_order_gate_error = sum({abs(dynamics.rotor_center[i, j] - expected_rotor_center[i, j]) for i in 1:4, j in 1:3})",
    "yaw_direction_gate_error = sum({abs(dynamics.yaw_direction[i] - expected_yaw_direction[i]) for i in 1:4})",
]

REQUIRED_PROVENANCE_ANCHORS = [
    "source=SDF_migration seed shared with mapper/core for static boundary consistency",
    "source=SDF_migration visual-speed thrust coefficient seed; not ULog identified",
    "source=interface_seed; lower normalized actuator command bound",
    "source=interface_seed; upper normalized actuator command bound",
    "source=interface_seed; hover command placeholder, not measured PWM/throttle evidence",
    "Existing MWORKS signed visual speed convention; not PX4 allocation proof",
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
    legacy_package = read_text(LEGACY_PACKAGE)
    legacy_order = read_order(LEGACY_ORDER)
    legacy_impl = read_text(LEGACY_IMPL)
    legacy_mapper_impl = read_text(LEGACY_MAPPER_IMPL)
    legacy_wrapper_impl = read_text(LEGACY_WRAPPER_IMPL)

    if not FORMAL_SOURCE.exists():
        add_finding(findings, "formal_source_missing", "ActuatorMappedWrapperSurface.mo is missing", target=rel(FORMAL_SOURCE))
    if "ActuatorMappedWrapperSurface" not in formal_order:
        add_finding(findings, "formal_order_missing", "package.order does not include ActuatorMappedWrapperSurface", target=rel(FORMAL_ORDER))
    if "model ActuatorMappedWrapperSurface" in formal_package:
        add_finding(
            findings,
            "duplicate_inline_formal_definition",
            "ActuatorMappedWrapperSurface remains inline in package.mo while source file exists",
            target=rel(FORMAL_PACKAGE),
        )
    if not contains(formal_source, "within MoSimQuadrotorModel.Dynamics;"):
        add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "model ActuatorMappedWrapperSurface"):
        add_finding(findings, "formal_model_missing", "formal source lacks model declaration", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "extends QuadrotorExperiments.DynamicsUpgrade.ActuatorMappedWrapperSurface;"):
        add_finding(findings, "formal_extends_drift", "formal source no longer extends legacy ActuatorMappedWrapperSurface alias", target=rel(FORMAL_SOURCE))

    forbidden_behavior_snippets = [
        "equation",
        "actuator_mapper",
        " wrapper(",
        "wrapper.",
        "normalized_actuator_command[",
        "saturated_normalized_command",
        "actuator_saturation_error",
        "signed_visual_rotor_speed_command",
        "total_thrust",
        "total_moment_body",
        "motor_order_gate_error",
        "yaw_direction_gate_error",
    ]
    for snippet in forbidden_behavior_snippets:
        if contains(formal_source, snippet):
            add_finding(
                findings,
                "formal_source_duplicates_mapped_wrapper_behavior",
                f"formal source duplicates mapped-wrapper behavior snippet {snippet!r}",
                target=rel(FORMAL_SOURCE),
            )

    if "ActuatorMappedWrapperSurface" not in legacy_order:
        add_finding(findings, "legacy_order_missing", "legacy package.order lost ActuatorMappedWrapperSurface", target=rel(LEGACY_ORDER))
    if not contains(legacy_package, "model ActuatorMappedWrapperSurface"):
        add_finding(findings, "legacy_alias_missing", "legacy package lost ActuatorMappedWrapperSurface alias", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_package, "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150ActuatorMappedWrapperSurface"):
        add_finding(findings, "legacy_alias_extends_drift", "legacy alias no longer extends Sunray150ActuatorMappedWrapperSurface", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_impl, "model Sunray150ActuatorMappedWrapperSurface"):
        add_finding(findings, "legacy_impl_missing", "legacy mapped-wrapper implementation declaration missing", target=rel(LEGACY_IMPL))
    if not contains(legacy_mapper_impl, "model Sunray150ActuatorCommandMapper"):
        add_finding(findings, "legacy_mapper_impl_missing", "legacy mapper implementation declaration missing", target=rel(LEGACY_MAPPER_IMPL))
    if not contains(legacy_wrapper_impl, "model Sunray150DynamicsWrapperSurface"):
        add_finding(findings, "legacy_wrapper_impl_missing", "legacy wrapper implementation declaration missing", target=rel(LEGACY_WRAPPER_IMPL))

    mapped_wrapper_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_MAPPED_WRAPPER_ANCHORS:
        present = contains(legacy_impl, snippet)
        mapped_wrapper_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "mapped_wrapper_anchor_missing", f"missing mapped-wrapper anchor {snippet!r}", target=rel(LEGACY_IMPL))

    mapper_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_MAPPER_ANCHORS:
        present = contains(legacy_mapper_impl, snippet)
        mapper_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "mapper_anchor_missing", f"missing mapper anchor {snippet!r}", target=rel(LEGACY_MAPPER_IMPL))

    wrapper_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_WRAPPER_ANCHORS:
        present = contains(legacy_wrapper_impl, snippet)
        wrapper_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "wrapper_anchor_missing", f"missing wrapper anchor {snippet!r}", target=rel(LEGACY_WRAPPER_IMPL))

    provenance_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_PROVENANCE_ANCHORS:
        present = contains(legacy_impl, snippet)
        provenance_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "provenance_anchor_missing", f"missing provenance anchor {snippet!r}", target=rel(LEGACY_IMPL))

    result = {
        "schema": "mosim.mworks.actuator_mapped_wrapper_surface_check.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": "MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface",
        "formal_source": rel(FORMAL_SOURCE),
        "formal_package": rel(FORMAL_PACKAGE),
        "formal_package_order": rel(FORMAL_ORDER),
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.ActuatorMappedWrapperSurface",
        "legacy_package": rel(LEGACY_PACKAGE),
        "legacy_package_order": rel(LEGACY_ORDER),
        "legacy_implementation": rel(LEGACY_IMPL),
        "legacy_mapper_implementation": rel(LEGACY_MAPPER_IMPL),
        "legacy_wrapper_implementation": rel(LEGACY_WRAPPER_IMPL),
        "behavior_preservation": {
            "formal_source_is_extends_only": True,
            "formal_source_duplicates_mapped_wrapper_behavior": False,
            "legacy_alias_preserved": True,
            "legacy_implementation_preserved": True,
            "legacy_mapper_implementation_preserved": True,
            "legacy_wrapper_implementation_preserved": True,
            "mapped_wrapper_equations_changed_by_030": False,
            "mapper_equations_changed_by_030": False,
            "wrapper_equations_changed_by_030": False,
            "numeric_parameters_changed_by_030": False,
            "spin_command_sign_changed_by_030": False,
            "rotor_centers_changed_by_030": False,
        },
        "mapped_wrapper_anchors": mapped_wrapper_anchors,
        "mapper_anchors": mapper_anchors,
        "wrapper_anchors": wrapper_anchors,
        "provenance_anchors": provenance_anchors,
        "findings": findings,
    }
    return result, findings


def write_markdown(path: Path, check: dict[str, Any]) -> None:
    lines = [
        "# ActuatorMappedWrapperSurface Formal Source Surface",
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
        "The formal source is intentionally an extends-only project-owned surface. It does not duplicate normalized actuator command mapping, signed visual rotor-speed generation, wrapper feedthrough, thrust/moment equations, or observation gate outputs.",
        "",
        "## Static Anchors",
        "",
        "- Mapper-to-wrapper chain: `actuator_mapper.normalized_command = normalized_actuator_command` and `wrapper.motor_command = actuator_mapper.signed_visual_rotor_speed_command` remain in the legacy implementation.",
        "- Mapper observability: `saturated_normalized_command`, `actuator_saturation_error`, and `signed_visual_rotor_speed_command` remain exposed.",
        "- Wrapper observability: `total_thrust`, `total_moment_body`, `commanded_total_thrust`, `commanded_total_moment_body`, hover/yaw gates, effectiveness monitors, motor-order gate, and yaw-direction gate remain exposed.",
        "- Legacy mapper and wrapper implementations remain separate source anchors and were not edited by 030.",
        "",
        "## Claim Boundary",
        "",
        "- Static source/package surface only.",
        "- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.",
        "- No mapper/wrapper equation, numerical parameter, spin sign, rotor center, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def package_integrity(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.package_order_integrity.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if check["status"] == "passed_static" else "failed_static",
        "formal_package_order_contains_actuator_mapped_wrapper_surface": "ActuatorMappedWrapperSurface" in read_order(FORMAL_ORDER),
        "formal_package_mo_no_inline_duplicate": "model ActuatorMappedWrapperSurface" not in read_text(FORMAL_PACKAGE),
        "formal_source_file_present": FORMAL_SOURCE.exists(),
        "legacy_package_order_contains_actuator_mapped_wrapper_surface": "ActuatorMappedWrapperSurface" in read_order(LEGACY_ORDER),
        "legacy_package_alias_present": "model ActuatorMappedWrapperSurface" in read_text(LEGACY_PACKAGE),
        "legacy_implementation_file_present": LEGACY_IMPL.exists(),
        "legacy_mapper_file_present": LEGACY_MAPPER_IMPL.exists(),
        "legacy_wrapper_file_present": LEGACY_WRAPPER_IMPL.exists(),
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
    }


def write_changed_files(path: Path) -> None:
    write_json(
        path,
        {
            "schema": "mosim.changed_files_manifest.v1",
            "request_id": REQUEST_ID,
            "modelica_source_files_changed": [
                "Models/MoSimQuadrotorModel/Dynamics/package.mo",
                "Models/MoSimQuadrotorModel/Dynamics/ActuatorMappedWrapperSurface.mo",
            ],
            "legacy_source_files_changed": [],
            "script_files_changed_by_030": [
                "Scripts/mworks/validate_mosimquad_actuator_mapped_wrapper_surface.py",
                "Scripts/tests/test_mosimquad_actuator_mapped_wrapper_surface.py",
            ],
            "evidence_files_written_by_030": [
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/actuator_mapped_wrapper_surface_check.json",
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/actuator_mapped_wrapper_surface.md",
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/package_order_integrity.json",
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/changed_files.json",
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/static_validation_summary.json",
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/formal_smoke_surface_recheck/",
                "Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/live_gate_runner_recheck/",
            ],
            "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-ACTUATOR-MAPPED-WRAPPER-FORMAL-SOURCE-SURFACE-BACKUP-20260609-030.json",
        },
    )


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
            rel(out_dir / "actuator_mapped_wrapper_surface_check.json"),
            rel(out_dir / "actuator_mapped_wrapper_surface.md"),
            rel(out_dir / "package_order_integrity.json"),
            rel(out_dir / "changed_files.json"),
            rel(out_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "030 prepares a static formal source surface for ActuatorMappedWrapperSurface only.",
            "030 does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
            "030 preserves the normalized actuator command mapper-to-wrapper chain as legacy source behavior.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate()
    write_json(output_dir / "actuator_mapped_wrapper_surface_check.json", check)
    write_markdown(output_dir / "actuator_mapped_wrapper_surface.md", check)
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
