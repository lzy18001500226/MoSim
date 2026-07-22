#!/usr/bin/env python3
"""Validate the canonical ownership of the former Dynamics Batch A surface.

This file-only checker proves that the active implementation is now under
``MoSimQuadrotorModel.Dynamics`` while the former
``QuadrotorExperiments.DynamicsUpgrade`` names remain hidden compatibility
aliases. It does not call MWORKS, Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosimquad_canonical_dynamics_surface as support


REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-BATCH-A-SOURCE-MIGRATION-20260608-025"
DEFAULT_OUTPUT_DIR = (
    support.ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260722_mosimquad_model_root_consolidation"
    / "dynamics_batch_a_source_migration"
)

TARGETS: tuple[dict[str, Any], ...] = (
    {
        "formal_name": "RotorActuatorCore",
        "legacy_alias_name": "RotorDynamicsCore",
        "legacy_file_name": "Sunray150RflyStyleRotorDynamics.mo",
        "legacy_file_model": "Sunray150RflyStyleRotorDynamics",
        "primary_anchors": (
            "der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]",
            "thrust[i] = thrust_effectiveness[i] * lift_coefficient * omega[i] * omega[i]",
            "yaw_reaction_moment[i] = yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust[i]",
            "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
            "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
            "total_thrust = sum(thrust)",
            "minimum_thrust_effectiveness = min(thrust_effectiveness)",
            "minimum_reaction_moment_effectiveness = min(reaction_moment_effectiveness)",
        ),
    },
    {
        "formal_name": "WrapperSurface",
        "legacy_alias_name": "WrapperSurface",
        "legacy_file_name": "Sunray150DynamicsWrapperSurface.mo",
        "legacy_file_model": "Sunray150DynamicsWrapperSurface",
        "primary_anchors": (
            "RotorActuatorCore dynamics;",
            "dynamics.motor_command = motor_command",
            "commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
            "commanded_total_moment_body[3]",
            "motor_order_gate_error =",
            "yaw_direction_gate_error =",
        ),
        "related_sources": (
            (
                "rotor core",
                support.FORMAL_ROOT / "RotorActuatorCore.mo",
                ("model RotorActuatorCore", "total_moment_body[3]"),
            ),
        ),
    },
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(support.ROOT).as_posix()
    except ValueError:
        # Unit tests and external callers may direct artifacts outside the repo.
        return path.as_posix()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown_matrix(path: Path, matrix: dict[str, Any]) -> None:
    lines = [
        "# Dynamics Batch A Source Migration",
        "",
        f"Request: `{REQUEST_ID}`",
        "",
        f"Status: `{matrix['status']}`",
        "",
        "| Canonical target | Canonical source | Legacy compatibility alias | Legacy compatibility file | Migration state |",
        "|---|---|---|---|---|",
    ]
    for item in matrix["targets"]:
        lines.append(
            "| `{formal_target}` | `{formal_source}` | `{legacy_alias}` | `{legacy_file}` | `{migration_state}` |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Batch A is static source migration only.",
            "- `RotorActuatorCore` and `WrapperSurface` are canonical project-owned implementations.",
            "- Legacy `QuadrotorExperiments.DynamicsUpgrade` files are retained only as hidden compatibility aliases.",
            "- No live MWORKS load, `check_model`, `SimulateModel`, result variables, graphical/layout review, controller performance, planner readiness, runtime ack, mission success, or closed loop is claimed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def validate_batch_a() -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    targets: list[dict[str, Any]] = []

    for target in TARGETS:
        check, component_findings = support.validate_component(**target)
        findings.extend(component_findings)
        authority = check["source_authority"]
        targets.append(
            {
                "formal_target": check["formal_target"],
                "formal_source": check["formal_source"],
                "legacy_alias": check["legacy_alias"],
                "legacy_file": check["legacy_file"],
                "canonical_source_owns_implementation": authority["canonical_source_owns_implementation"],
                "legacy_alias_preserved": authority["legacy_aliases_preserved"],
                "canonical_anchors": check["canonical_anchors"],
                "related_canonical_anchors": check["related_canonical_anchors"],
                "migration_state": "canonical_implementation_with_hidden_legacy_alias",
            }
        )

    return {
        "schema": "mosim.mworks.dynamics_batch_a_source_migration_matrix.v2",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "batch_scope": [item["formal_target"] for item in targets],
        "deferred_targets": [
            "MoSimQuadrotorModel.Dynamics.HoverSmoke",
            "MoSimQuadrotorModel.Dynamics.YawStepSmoke",
            "MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper",
            "MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface",
            "MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer",
            "MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke",
            "MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke",
            "MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter",
            "MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke",
            "MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke",
        ],
        "targets": targets,
        "source_surface_policy": {
            "formal_sources_are_canonical_implementations": True,
            "legacy_aliases_preserved": True,
            "legacy_aliases_are_hidden": True,
            "dynamics_equations_changed_by_namespace_consolidation": False,
            "numeric_parameters_changed_by_namespace_consolidation": False,
        },
        "findings": findings,
    }


def changed_files_manifest(output_dir: Path) -> dict[str, Any]:
    return {
        "schema": "mosim.changed_files_manifest.v2",
        "request_id": REQUEST_ID,
        "modelica_source_files_in_batch_a_surface": [
            "Models/MoSimQuadrotorModel/Dynamics/RotorActuatorCore.mo",
            "Models/MoSimQuadrotorModel/Dynamics/WrapperSurface.mo",
            "Models/MoSimQuadrotorModel/Dynamics/package.mo",
            "Models/MoSimQuadrotorModel/Dynamics/package.order",
        ],
        "legacy_compatibility_files_checked": [
            "Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RflyStyleRotorDynamics.mo",
            "Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperSurface.mo",
        ],
        "evidence_files_written": [
            rel(output_dir / "batch_a_source_migration_matrix.json"),
            rel(output_dir / "batch_a_source_migration_matrix.md"),
            rel(output_dir / "changed_files.json"),
            rel(output_dir / "static_validation_summary.json"),
        ],
    }


def static_summary(matrix: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.static_validation_summary.v2",
        "request_id": REQUEST_ID,
        "status": "passed" if matrix["status"] == "passed_static" else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "batch_scope": matrix["batch_scope"],
        "deferred_targets": matrix["deferred_targets"],
        "source_surface_policy": matrix["source_surface_policy"],
        "findings": matrix["findings"],
        "evidence_files": [
            rel(output_dir / "batch_a_source_migration_matrix.json"),
            rel(output_dir / "batch_a_source_migration_matrix.md"),
            rel(output_dir / "changed_files.json"),
            rel(output_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "Batch A claims only static canonical source ownership for RotorActuatorCore and WrapperSurface.",
            "Batch A does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner readiness, runtime ack, mission success, or closed loop.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = validate_batch_a()
    write_json(output_dir / "batch_a_source_migration_matrix.json", matrix)
    write_markdown_matrix(output_dir / "batch_a_source_migration_matrix.md", matrix)
    write_json(output_dir / "changed_files.json", changed_files_manifest(output_dir))
    summary = static_summary(matrix, output_dir)
    write_json(output_dir / "static_validation_summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else support.ROOT / args.output_dir
    summary = generate(output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())