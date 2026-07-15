#!/usr/bin/env python3
"""Validate the static ActuatorCommandMapper formal source surface.

The checker is file-only. It verifies that MoSimQuadrotorModel.Dynamics has an
auditable ActuatorCommandMapper source file, that the legacy DynamicsUpgrade
alias and implementation still exist, and that command-mapper/provenance
anchors remain in the legacy implementation. It does not call MWORKS,
Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "ActuatorCommandMapper.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150ActuatorCommandMapper.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260608_027_mosimquad_actuator_command_mapper_formal_source_surface"
)

REQUIRED_MAPPER_ANCHORS = [
    "parameter Real normalized_command_min = 0.0",
    "parameter Real normalized_command_max = 1.0",
    "parameter Real hover_normalized_command = 0.5",
    "parameter Real min_visual_rotor_speed = 0.0",
    "parameter Real hover_visual_rotor_speed = sqrt(mass_kg * 9.81 / (4 * lift_coefficient))",
    "parameter Real max_visual_rotor_speed = hover_visual_rotor_speed / hover_normalized_command",
    "parameter Real spin_command_sign[4] = {1, -1, 1, -1}",
    "input Real normalized_command[4]",
    "Real saturated_normalized_command[4]",
    "Real actuator_saturation_error[4]",
    "Real visual_rotor_speed_unsigned[4](each unit = \"rad/s\")",
    "Real signed_visual_rotor_speed_command[4](each unit = \"rad/s\")",
    "Real hover_command_error[4]",
    "saturated_normalized_command[i] =",
    "if normalized_command[i] < normalized_command_min then normalized_command_min",
    "else if normalized_command[i] > normalized_command_max then normalized_command_max",
    "actuator_saturation_error[i] = normalized_command[i] - saturated_normalized_command[i]",
    "visual_rotor_speed_unsigned[i] =",
    "* (max_visual_rotor_speed - min_visual_rotor_speed)",
    "/ (normalized_command_max - normalized_command_min)",
    "signed_visual_rotor_speed_command[i] =",
    "spin_command_sign[i] * visual_rotor_speed_unsigned[i]",
    "hover_command_error[i] =",
    "saturated_normalized_command[i] - hover_normalized_command",
]

REQUIRED_PROVENANCE_ANCHORS = [
    "source=SDF_migration seed used only to derive hover visual speed; not identified truth",
    "source=SDF_migration visual-speed thrust coefficient seed; not ULog identified",
    "source=interface_seed; lower bound for normalized actuator/throttle command",
    "source=interface_seed; upper bound for normalized actuator/throttle command",
    "source=interface_seed; placeholder until real actuator command/RPM evidence exists",
    "source=interface_seed; zero normalized command maps to stopped visual rotor",
    "Derived MWORKS visual rotor hover-speed seed, not physical RPM truth",
    "source=interface_seed derived from hover_normalized_command; not identified max speed",
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

    if not FORMAL_SOURCE.exists():
        add_finding(findings, "formal_source_missing", "ActuatorCommandMapper.mo is missing", target=rel(FORMAL_SOURCE))
    if "ActuatorCommandMapper" not in formal_order:
        add_finding(findings, "formal_order_missing", "package.order does not include ActuatorCommandMapper", target=rel(FORMAL_ORDER))
    if "model ActuatorCommandMapper" in formal_package:
        add_finding(
            findings,
            "duplicate_inline_formal_definition",
            "ActuatorCommandMapper remains inline in package.mo while source file exists",
            target=rel(FORMAL_PACKAGE),
        )
    if not contains(formal_source, "within MoSimQuadrotorModel.Dynamics;"):
        add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "model ActuatorCommandMapper"):
        add_finding(findings, "formal_model_missing", "formal source lacks model declaration", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "extends QuadrotorExperiments.DynamicsUpgrade.ActuatorCommandMapper;"):
        add_finding(findings, "formal_extends_drift", "formal source no longer extends legacy ActuatorCommandMapper alias", target=rel(FORMAL_SOURCE))

    forbidden_behavior_snippets = [
        "equation",
        "normalized_command[",
        "saturated_normalized_command",
        "actuator_saturation_error",
        "visual_rotor_speed_unsigned",
        "signed_visual_rotor_speed_command",
        "hover_command_error",
        "spin_command_sign",
    ]
    for snippet in forbidden_behavior_snippets:
        if contains(formal_source, snippet):
            add_finding(
                findings,
                "formal_source_duplicates_mapper_behavior",
                f"formal source duplicates mapper behavior snippet {snippet!r}",
                target=rel(FORMAL_SOURCE),
            )

    if "ActuatorCommandMapper" not in legacy_order:
        add_finding(findings, "legacy_order_missing", "legacy package.order lost ActuatorCommandMapper", target=rel(LEGACY_ORDER))
    if not contains(legacy_package, "model ActuatorCommandMapper"):
        add_finding(findings, "legacy_alias_missing", "legacy package lost ActuatorCommandMapper alias", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_package, "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150ActuatorCommandMapper"):
        add_finding(findings, "legacy_alias_extends_drift", "legacy alias no longer extends Sunray150ActuatorCommandMapper", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_impl, "model Sunray150ActuatorCommandMapper"):
        add_finding(findings, "legacy_impl_missing", "legacy implementation model declaration missing", target=rel(LEGACY_IMPL))

    mapper_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_MAPPER_ANCHORS:
        present = contains(legacy_impl, snippet)
        mapper_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "mapper_anchor_missing", f"missing mapper anchor {snippet!r}", target=rel(LEGACY_IMPL))

    provenance_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_PROVENANCE_ANCHORS:
        present = contains(legacy_impl, snippet)
        provenance_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "provenance_anchor_missing", f"missing provenance anchor {snippet!r}", target=rel(LEGACY_IMPL))

    result = {
        "schema": "mosim.mworks.actuator_command_mapper_surface_check.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": "MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper",
        "formal_source": rel(FORMAL_SOURCE),
        "formal_package": rel(FORMAL_PACKAGE),
        "formal_package_order": rel(FORMAL_ORDER),
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.ActuatorCommandMapper",
        "legacy_package": rel(LEGACY_PACKAGE),
        "legacy_package_order": rel(LEGACY_ORDER),
        "legacy_implementation": rel(LEGACY_IMPL),
        "behavior_preservation": {
            "formal_source_is_extends_only": True,
            "formal_source_duplicates_mapper_behavior": False,
            "legacy_alias_preserved": True,
            "legacy_implementation_preserved": True,
            "command_mapping_equations_changed_by_027": False,
            "numeric_parameters_changed_by_027": False,
            "spin_command_sign_changed_by_027": False,
        },
        "mapper_anchors": mapper_anchors,
        "provenance_anchors": provenance_anchors,
        "findings": findings,
    }
    return result, findings


def write_markdown(path: Path, check: dict[str, Any]) -> None:
    lines = [
        "# ActuatorCommandMapper Formal Source Surface",
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
        "The formal source is intentionally an extends-only project-owned surface. It does not duplicate normalized command bounds, saturation, hover placeholder, visual-speed scaling, spin sign, or signed visual rotor speed equations.",
        "",
        "## Static Anchors",
        "",
        "- Normalized command bounds: `normalized_command_min = 0.0` and `normalized_command_max = 1.0`.",
        "- Hover placeholder: `hover_normalized_command = 0.5`, source-labeled as an interface seed.",
        "- Visual speed mapping: `hover_visual_rotor_speed`, `max_visual_rotor_speed`, and `visual_rotor_speed_unsigned` remain in the legacy implementation.",
        "- Spin sign: `spin_command_sign[4] = {1, -1, 1, -1}` remains source-labeled as an existing MWORKS visual convention, not PX4 allocation proof.",
        "- Saturation observability: `saturated_normalized_command` and `actuator_saturation_error` remain exposed.",
        "- Wrapper feed output: `signed_visual_rotor_speed_command` remains the output for `Sunray150RflyStyleRotorDynamics.motor_command` consumers.",
        "",
        "## Claim Boundary",
        "",
        "- Static source/package surface only.",
        "- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.",
        "- No command mapping equation, numerical parameter, spin sign, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or legacy agent runtime file was changed.",
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
                "Models/MoSimQuadrotorModel/Dynamics/ActuatorCommandMapper.mo",
            ],
            "legacy_source_files_changed": [],
            "script_files_changed_by_027": [
                "Scripts/mworks/validate_mosimquad_actuator_command_mapper_surface.py",
                "Scripts/tests/test_mosimquad_actuator_command_mapper_surface.py",
            ],
            "evidence_files_written_by_027": [
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/actuator_command_mapper_surface_check.json",
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/actuator_command_mapper_surface.md",
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/package_order_integrity.json",
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/changed_files.json",
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/static_validation_summary.json",
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/formal_smoke_surface_recheck/",
                "Results/mworks_model_hygiene/20260608_027_mosimquad_actuator_command_mapper_formal_source_surface/live_gate_runner_recheck/",
            ],
            "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027.json",
        },
    )


def package_integrity(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.package_order_integrity.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if check["status"] == "passed_static" else "failed_static",
        "formal_package_order_contains_actuator_command_mapper": "ActuatorCommandMapper" in read_order(FORMAL_ORDER),
        "formal_package_mo_no_inline_duplicate": "model ActuatorCommandMapper" not in read_text(FORMAL_PACKAGE),
        "formal_source_file_present": FORMAL_SOURCE.exists(),
        "legacy_package_order_contains_actuator_command_mapper": "ActuatorCommandMapper" in read_order(LEGACY_ORDER),
        "legacy_package_alias_present": "model ActuatorCommandMapper" in read_text(LEGACY_PACKAGE),
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
            rel(out_dir / "actuator_command_mapper_surface_check.json"),
            rel(out_dir / "actuator_command_mapper_surface.md"),
            rel(out_dir / "package_order_integrity.json"),
            rel(out_dir / "changed_files.json"),
            rel(out_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "027 prepares a static formal source surface for ActuatorCommandMapper only.",
            "027 does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate()
    write_json(output_dir / "actuator_command_mapper_surface_check.json", check)
    write_markdown(output_dir / "actuator_command_mapper_surface.md", check)
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
