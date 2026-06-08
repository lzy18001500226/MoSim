#!/usr/bin/env python3
"""Validate MoSimQuadrotorModel Dynamics Batch A static source migration.

Batch A is deliberately narrow: the formal source surface covers
RotorActuatorCore and WrapperSurface only. The checker is file-only and does
not call MWORKS, Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-BATCH-A-SOURCE-MIGRATION-20260608-025"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
ROTOR_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "RotorActuatorCore.mo"
WRAPPER_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "WrapperSurface.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_ROTOR_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150RflyStyleRotorDynamics.mo"
LEGACY_WRAPPER_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150DynamicsWrapperSurface.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260608_025_mosimquad_dynamics_batch_a_source_migration"
)

BATCH_A_TARGETS = [
    {
        "formal_target": "MoSimQuadrotorModel.Dynamics.RotorActuatorCore",
        "formal_source": ROTOR_SOURCE,
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore",
        "legacy_implementation": LEGACY_ROTOR_IMPL,
        "required_extends": "extends QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore;",
        "formal_model": "model RotorActuatorCore",
        "legacy_model": "model RotorDynamicsCore",
        "order_name": "RotorActuatorCore",
        "legacy_order_name": "RotorDynamicsCore",
        "legacy_alias_extends": "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150RflyStyleRotorDynamics",
    },
    {
        "formal_target": "MoSimQuadrotorModel.Dynamics.WrapperSurface",
        "formal_source": WRAPPER_SOURCE,
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.WrapperSurface",
        "legacy_implementation": LEGACY_WRAPPER_IMPL,
        "required_extends": "extends QuadrotorExperiments.DynamicsUpgrade.WrapperSurface;",
        "formal_model": "model WrapperSurface",
        "legacy_model": "model WrapperSurface",
        "order_name": "WrapperSurface",
        "legacy_order_name": "WrapperSurface",
        "legacy_alias_extends": "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperSurface",
    },
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


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_markdown_matrix(path: Path, matrix: dict[str, Any]) -> None:
    lines = [
        "# Dynamics Batch A Source Migration",
        "",
        f"Request: `{REQUEST_ID}`",
        "",
        f"Status: `{matrix['status']}`",
        "",
        "| Formal target | Formal source | Legacy alias | Legacy implementation | Migration state |",
        "|---|---|---|---|---|",
    ]
    for item in matrix["targets"]:
        lines.append(
            "| `{formal_target}` | `{formal_source}` | `{legacy_alias}` | `{legacy_implementation}` | `{migration_state}` |".format(
                **item
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Batch A is static source migration only.",
            "- Only `RotorActuatorCore` and `WrapperSurface` are in the Batch A source surface.",
            "- Legacy `QuadrotorExperiments.DynamicsUpgrade` aliases and implementation files remain the behavior source.",
            "- No live MWORKS load, `check_model`, `SimulateModel`, result variables, graphical/layout review, controller performance, planner readiness, runtime ack, mission success, or closed loop is claimed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_batch_a(output_dir: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    formal_package = read_text(FORMAL_PACKAGE)
    formal_order = read_order(FORMAL_ORDER)
    legacy_package = read_text(LEGACY_PACKAGE)
    legacy_order = read_order(LEGACY_ORDER)

    targets: list[dict[str, Any]] = []
    for target in BATCH_A_TARGETS:
        formal_source = target["formal_source"]
        legacy_impl = target["legacy_implementation"]
        source_text = read_text(formal_source) if formal_source.exists() else ""
        legacy_impl_text = read_text(legacy_impl) if legacy_impl.exists() else ""

        if not formal_source.exists():
            add_finding(findings, "formal_source_missing", "formal Batch A source file is missing", target=rel(formal_source))
        if target["order_name"] not in formal_order:
            add_finding(findings, "formal_order_missing", "formal package.order is missing Batch A target", target=rel(FORMAL_ORDER))
        if target["formal_model"] in formal_package:
            add_finding(
                findings,
                "duplicate_inline_formal_definition",
                "formal package.mo still contains an inline Batch A model definition",
                target=rel(FORMAL_PACKAGE),
            )
        if "within MoSimQuadrotorModel.Dynamics;" not in source_text:
            add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(formal_source))
        if target["formal_model"] not in source_text:
            add_finding(findings, "formal_model_missing", "formal source lacks expected model declaration", target=rel(formal_source))
        if target["required_extends"] not in source_text:
            add_finding(findings, "formal_extends_drift", "formal source no longer extends the expected legacy alias", target=rel(formal_source))
        if target["legacy_order_name"] not in legacy_order:
            add_finding(findings, "legacy_order_missing", "legacy package.order is missing required alias", target=rel(LEGACY_ORDER))
        if target["legacy_model"] not in legacy_package:
            add_finding(findings, "legacy_alias_missing", "legacy package lost required alias model", target=rel(LEGACY_PACKAGE))
        if target["legacy_alias_extends"] not in legacy_package:
            add_finding(findings, "legacy_alias_extends_drift", "legacy alias no longer extends expected implementation", target=rel(LEGACY_PACKAGE))
        if not legacy_impl.exists() or "model " not in legacy_impl_text:
            add_finding(findings, "legacy_impl_missing", "legacy implementation file/model is missing", target=rel(legacy_impl))

        targets.append(
            {
                "formal_target": target["formal_target"],
                "formal_source": rel(formal_source),
                "formal_source_present": formal_source.exists(),
                "formal_order_present": target["order_name"] in formal_order,
                "formal_package_inline_duplicate": target["formal_model"] in formal_package,
                "formal_extends_expected_legacy_alias": target["required_extends"] in source_text,
                "legacy_alias": target["legacy_alias"],
                "legacy_order_present": target["legacy_order_name"] in legacy_order,
                "legacy_alias_present": target["legacy_model"] in legacy_package,
                "legacy_alias_extends_expected_implementation": target["legacy_alias_extends"] in legacy_package,
                "legacy_implementation": rel(legacy_impl),
                "legacy_implementation_present": legacy_impl.exists(),
                "migration_state": "formal_source_materialized_extends_only",
            }
        )

    rotor_module = load_script(ROOT / "Scripts" / "mworks" / "validate_mosimquad_rotor_actuator_core_surface.py")
    wrapper_module = load_script(ROOT / "Scripts" / "mworks" / "validate_mosimquad_wrapper_surface.py")

    rotor_summary = rotor_module.generate(output_dir / "rotor_actuator_core_recheck")
    wrapper_summary = wrapper_module.generate(output_dir / "wrapper_surface_recheck")

    if rotor_summary["status"] != "passed":
        add_finding(findings, "rotor_surface_recheck_failed", "RotorActuatorCore surface checker did not pass", target=rel(output_dir / "rotor_actuator_core_recheck"))
    if wrapper_summary["status"] != "passed":
        add_finding(findings, "wrapper_surface_recheck_failed", "WrapperSurface checker did not pass", target=rel(output_dir / "wrapper_surface_recheck"))

    matrix = {
        "schema": "mosim.mworks.dynamics_batch_a_source_migration_matrix.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "batch_scope": [
            "MoSimQuadrotorModel.Dynamics.RotorActuatorCore",
            "MoSimQuadrotorModel.Dynamics.WrapperSurface",
        ],
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
            "formal_sources_are_extends_only": True,
            "legacy_aliases_preserved": True,
            "legacy_implementations_preserved": True,
            "dynamics_equations_changed_by_batch_a": False,
            "numeric_parameters_changed_by_batch_a": False,
            "broad_rename_or_search_replace_used": False,
        },
        "component_rechecks": {
            "rotor_actuator_core": {
                "status": rotor_summary["status"],
                "artifact_dir": rel(output_dir / "rotor_actuator_core_recheck"),
            },
            "wrapper_surface": {
                "status": wrapper_summary["status"],
                "artifact_dir": rel(output_dir / "wrapper_surface_recheck"),
            },
        },
        "findings": findings,
    }
    return matrix


def changed_files_manifest(output_dir: Path) -> dict[str, Any]:
    return {
        "schema": "mosim.changed_files_manifest.v1",
        "request_id": REQUEST_ID,
        "modelica_source_files_in_batch_a_surface": [
            "Models/MoSimQuadrotorModel/Dynamics/RotorActuatorCore.mo",
            "Models/MoSimQuadrotorModel/Dynamics/WrapperSurface.mo",
            "Models/MoSimQuadrotorModel/Dynamics/package.mo",
            "Models/MoSimQuadrotorModel/Dynamics/package.order",
        ],
        "modelica_source_files_changed_by_this_closeout": [],
        "legacy_source_files_changed_by_this_closeout": [],
        "script_files_added_by_this_closeout": [
            "Scripts/mworks/validate_mosimquad_dynamics_batch_a_source_migration.py",
            "Scripts/tests/test_mosimquad_dynamics_batch_a_source_migration.py",
        ],
        "evidence_files_written_by_this_closeout": [
            rel(output_dir / "batch_a_source_migration_matrix.json"),
            rel(output_dir / "batch_a_source_migration_matrix.md"),
            rel(output_dir / "changed_files.json"),
            rel(output_dir / "static_validation_summary.json"),
            rel(output_dir / "rotor_actuator_core_recheck"),
            rel(output_dir / "wrapper_surface_recheck"),
        ],
        "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-BATCH-A-SOURCE-MIGRATION-20260608-025.json",
    }


def static_summary(matrix: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.static_validation_summary.v1",
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
            "Batch A claims only static formal source migration readiness for RotorActuatorCore and WrapperSurface.",
            "Batch A does not call or prove MWORKS load, check_model, SimulateModel, native result, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = validate_batch_a(output_dir)
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
    parser = build_parser()
    args = parser.parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    summary = generate(output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
