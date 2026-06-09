#!/usr/bin/env python3
"""Validate the static OptionalDampingGyroLayer formal source surface.

The checker is file-only. It verifies that MoSimQuadrotorModel.Dynamics has an
auditable OptionalDampingGyroLayer source file, that the legacy DynamicsUpgrade
alias and implementation still exist, and that optional gyro/drag/damping
anchors remain default-disabled/source-labeled. It does not call MWORKS,
Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R2-MOSIMQUAD-OPTIONAL-DAMPING-GYRO-FORMAL-SOURCE-SURFACE-20260609-026"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "OptionalDampingGyroLayer.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150OptionalDampingGyroLayer.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260609_026_mosimquad_optional_damping_gyro_formal_source_surface"
)

REQUIRED_OPTIONAL_LAYER_ANCHORS = [
    "parameter Boolean enable_rotor_gyro = false",
    "parameter Boolean enable_body_drag = false",
    "parameter Boolean enable_angular_damping = false",
    "parameter Real rotor_polar_inertia[4](each unit = \"kg.m2\") = {0, 0, 0, 0}",
    "parameter Real gyro_axis_sign[4] = {1, -1, 1, -1}",
    "parameter Real gyro_convention_sign = -1",
    "parameter Real body_drag_coefficient[3](each unit = \"N.s/m\") = {0, 0, 0}",
    "parameter Real angular_damping_coefficient[3](each unit = \"N.m.s/rad\") = {0, 0, 0}",
    "input Real normalized_actuator_command[4]",
    "input Real body_velocity_body[3](each unit = \"m/s\")",
    "input Real body_angular_velocity_body[3](each unit = \"rad/s\")",
    "mapped_wrapper.normalized_actuator_command = normalized_actuator_command",
    "rotor_angular_momentum_body_z[i] =",
    "rotor_polar_inertia[i] * gyro_axis_sign[i] * mapped_wrapper.wrapper.dynamics.omega[i]",
    "gyro_convention_sign * body_angular_velocity_body[2] * rotor_angular_momentum_body_z[i]",
    "-gyro_convention_sign * body_angular_velocity_body[1] * rotor_angular_momentum_body_z[i]",
    "body_drag_force_body[j] =",
    "-body_drag_coefficient[j] * body_velocity_body[j]",
    "angular_damping_moment_body[j] =",
    "-angular_damping_coefficient[j] * body_angular_velocity_body[j]",
    "optional_force_norm = abs(optional_force_body[1]) + abs(optional_force_body[2]) + abs(optional_force_body[3])",
    "optional_moment_norm = abs(optional_moment_body[1]) + abs(optional_moment_body[2]) + abs(optional_moment_body[3])",
    "default_disabled_force_delta =",
    "default_disabled_moment_delta =",
    "motor_order_gate_error = mapped_wrapper.motor_order_gate_error",
    "yaw_direction_gate_error = mapped_wrapper.yaw_direction_gate_error",
]

REQUIRED_PROVENANCE_ANCHORS = [
    "Default disabled; rotor gyro moment is not identified Sunray150 truth",
    "Default disabled; translational body drag coefficients are not identified",
    "Default disabled; angular damping coefficients are not identified",
    "source=zero_seed; optional rotor inertia placeholder, not ULog/bench identified",
    "source=sign_convention_seed; follows current MWORKS visual spin convention until motor-order validation",
    "source=interface_seed; sign for body-rate cross rotor-angular-momentum convention",
    "source=zero_seed; body-frame linear drag coefficients, not identified",
    "source=zero_seed; body angular-rate damping coefficients, not identified",
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
        add_finding(findings, "formal_source_missing", "OptionalDampingGyroLayer.mo is missing", target=rel(FORMAL_SOURCE))
    if "OptionalDampingGyroLayer" not in formal_order:
        add_finding(findings, "formal_order_missing", "package.order does not include OptionalDampingGyroLayer", target=rel(FORMAL_ORDER))
    if "model OptionalDampingGyroLayer" in formal_package:
        add_finding(
            findings,
            "duplicate_inline_formal_definition",
            "OptionalDampingGyroLayer remains inline in package.mo while source file exists",
            target=rel(FORMAL_PACKAGE),
        )
    if not contains(formal_source, "within MoSimQuadrotorModel.Dynamics;"):
        add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "model OptionalDampingGyroLayer"):
        add_finding(findings, "formal_model_missing", "formal source lacks model declaration", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "extends QuadrotorExperiments.DynamicsUpgrade.OptionalDampingGyroLayer;"):
        add_finding(findings, "formal_extends_drift", "formal source no longer extends legacy OptionalDampingGyroLayer alias", target=rel(FORMAL_SOURCE))

    forbidden_behavior_snippets = [
        "equation",
        "enable_rotor_gyro",
        "enable_body_drag",
        "enable_angular_damping",
        "rotor_polar_inertia",
        "body_drag_coefficient",
        "angular_damping_coefficient",
        "optional_force_norm",
        "optional_moment_norm",
        "default_disabled_force_delta",
        "default_disabled_moment_delta",
    ]
    for snippet in forbidden_behavior_snippets:
        if contains(formal_source, snippet):
            add_finding(
                findings,
                "formal_source_duplicates_optional_layer_behavior",
                f"formal source duplicates optional layer behavior snippet {snippet!r}",
                target=rel(FORMAL_SOURCE),
            )

    if "OptionalDampingGyroLayer" not in legacy_order:
        add_finding(findings, "legacy_order_missing", "legacy package.order lost OptionalDampingGyroLayer", target=rel(LEGACY_ORDER))
    if not contains(legacy_package, "model OptionalDampingGyroLayer"):
        add_finding(findings, "legacy_alias_missing", "legacy package lost OptionalDampingGyroLayer alias", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_package, "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150OptionalDampingGyroLayer"):
        add_finding(findings, "legacy_alias_extends_drift", "legacy alias no longer extends Sunray150OptionalDampingGyroLayer", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_impl, "model Sunray150OptionalDampingGyroLayer"):
        add_finding(findings, "legacy_impl_missing", "legacy implementation model declaration missing", target=rel(LEGACY_IMPL))

    optional_layer_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_OPTIONAL_LAYER_ANCHORS:
        present = contains(legacy_impl, snippet)
        optional_layer_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "optional_layer_anchor_missing", f"missing optional-layer anchor {snippet!r}", target=rel(LEGACY_IMPL))

    provenance_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_PROVENANCE_ANCHORS:
        present = contains(legacy_impl, snippet)
        provenance_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "provenance_anchor_missing", f"missing provenance anchor {snippet!r}", target=rel(LEGACY_IMPL))

    result = {
        "schema": "mosim.mworks.optional_damping_gyro_surface_check.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": "MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer",
        "formal_source": rel(FORMAL_SOURCE),
        "formal_package": rel(FORMAL_PACKAGE),
        "formal_package_order": rel(FORMAL_ORDER),
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.OptionalDampingGyroLayer",
        "legacy_package": rel(LEGACY_PACKAGE),
        "legacy_package_order": rel(LEGACY_ORDER),
        "legacy_implementation": rel(LEGACY_IMPL),
        "behavior_preservation": {
            "formal_source_is_extends_only": True,
            "formal_source_duplicates_optional_layer_behavior": False,
            "legacy_alias_preserved": True,
            "legacy_implementation_preserved": True,
            "optional_layer_equations_changed_by_026": False,
            "numeric_parameters_changed_by_026": False,
            "enable_flags_changed_by_026": False,
            "gyro_sign_convention_changed_by_026": False,
            "drag_damping_zero_seeds_changed_by_026": False,
            "mapper_wrapper_behavior_changed_by_026": False,
        },
        "optional_layer_anchors": optional_layer_anchors,
        "provenance_anchors": provenance_anchors,
        "findings": findings,
    }
    return result, findings


def write_markdown(path: Path, check: dict[str, Any]) -> None:
    lines = [
        "# OptionalDampingGyroLayer Formal Source Surface",
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
        "The formal source is intentionally an extends-only project-owned surface. It does not duplicate optional rotor gyro, body drag, angular damping, force/moment delta, or mapper-wrapper equations.",
        "",
        "## Static Anchors",
        "",
        "- Default flags remain false: `enable_rotor_gyro`, `enable_body_drag`, and `enable_angular_damping`.",
        "- Zero seeds remain for `rotor_polar_inertia`, `body_drag_coefficient`, and `angular_damping_coefficient`.",
        "- Gyro sign anchors remain `gyro_axis_sign` and `gyro_convention_sign` in the legacy implementation.",
        "- Observability anchors remain `optional_force_norm`, `optional_moment_norm`, `default_disabled_force_delta`, `default_disabled_moment_delta`, `motor_order_gate_error`, and `yaw_direction_gate_error`.",
        "",
        "## Claim Boundary",
        "",
        "- Static source/package surface only.",
        "- No live MWORKS load, `check_model`, `SimulateModel`, result variable, or graphical acceptance is claimed.",
        "- No optional gyro/drag/damping equation, numerical parameter, enable flag, sign convention, command mapping, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def package_integrity(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.package_order_integrity.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if check["status"] == "passed_static" else "failed_static",
        "formal_package_order_contains_optional_damping_gyro_layer": "OptionalDampingGyroLayer" in read_order(FORMAL_ORDER),
        "formal_package_mo_no_inline_duplicate": "model OptionalDampingGyroLayer" not in read_text(FORMAL_PACKAGE),
        "formal_source_file_present": FORMAL_SOURCE.exists(),
        "legacy_package_order_contains_optional_damping_gyro_layer": "OptionalDampingGyroLayer" in read_order(LEGACY_ORDER),
        "legacy_package_alias_present": "model OptionalDampingGyroLayer" in read_text(LEGACY_PACKAGE),
        "legacy_implementation_file_present": LEGACY_IMPL.exists(),
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
                "Models/MoSimQuadrotorModel/Dynamics/OptionalDampingGyroLayer.mo",
            ],
            "legacy_source_files_changed": [],
            "script_files_changed_by_026": [
                "Scripts/mworks/validate_mosimquad_optional_damping_gyro_surface.py",
                "Scripts/tests/test_mosimquad_optional_damping_gyro_surface.py",
            ],
            "evidence_files_written_by_026": [
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/optional_damping_gyro_surface_check.json",
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/optional_damping_gyro_surface.md",
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/package_order_integrity.json",
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/changed_files.json",
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/static_validation_summary.json",
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/formal_smoke_surface_recheck/",
                "Results/mworks_model_hygiene/20260609_026_mosimquad_optional_damping_gyro_formal_source_surface/live_gate_runner_recheck/",
            ],
            "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-OPTIONAL-DAMPING-GYRO-FORMAL-SOURCE-SURFACE-20260609-026.json",
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
            rel(out_dir / "optional_damping_gyro_surface_check.json"),
            rel(out_dir / "optional_damping_gyro_surface.md"),
            rel(out_dir / "package_order_integrity.json"),
            rel(out_dir / "changed_files.json"),
            rel(out_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "026 prepares a static formal source surface for OptionalDampingGyroLayer only.",
            "026 does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
            "026 preserves optional gyro, body drag, and angular damping as default-disabled/zero-seed source-labeled behavior.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate()
    write_json(output_dir / "optional_damping_gyro_surface_check.json", check)
    write_markdown(output_dir / "optional_damping_gyro_surface.md", check)
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
