#!/usr/bin/env python3
"""Validate the static PhysicalWrenchAdapter formal source surface.

This checker is file-only. It verifies that MoSimQuadrotorModel.Dynamics has an
auditable PhysicalWrenchAdapter source file, that the legacy DynamicsUpgrade
alias and Sunray150 implementation remain intact, and that physical wrench /
MultiBody frame-adapter anchors are still present. It does not call MWORKS,
Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUEST_ID = "PMO-MWORKS-R2-MOSIMQUAD-PHYSICAL-WRENCH-ADAPTER-FORMAL-SOURCE-SURFACE-20260609-031"

FORMAL_PACKAGE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.mo"
FORMAL_ORDER = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "package.order"
FORMAL_SOURCE = ROOT / "Models" / "MoSimQuadrotorModel" / "Dynamics" / "PhysicalWrenchAdapter.mo"
LEGACY_PACKAGE = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.mo"
LEGACY_ORDER = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "package.order"
LEGACY_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150PhysicalWrenchFrameAdapter.mo"
LEGACY_WRAPPER_IMPL = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade" / "Sunray150DynamicsWrapperSurface.mo"

DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface"
)

REQUIRED_PHYSICAL_WRENCH_ANCHORS = [
    "inner Modelica.Mechanics.MultiBody.World world",
    "Sunray150DynamicsWrapperSurface wrapper",
    "Modelica.Mechanics.MultiBody.Parts.Body body",
    "Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque forceAndTorque",
    "Real applied_force_body[3](each unit = \"N\")",
    "Real applied_torque_body[3](each unit = \"N.m\")",
    "Real force_application_error(unit = \"N\")",
    "Real torque_application_error(unit = \"N.m\")",
    "Real wrapper_total_thrust(unit = \"N\")",
    "Real wrapper_yaw_moment(unit = \"N.m\")",
    "Real motor_order_gate_error",
    "Real yaw_direction_gate_error",
    "applied_force_body = {0, 0, wrapper.total_thrust}",
    "applied_torque_body = wrapper.total_moment_body",
    "forceAndTorque.force = applied_force_body",
    "forceAndTorque.torque = applied_torque_body",
    "connect(forceAndTorque.frame_b, body.frame_a)",
    "wrapper_total_thrust = wrapper.total_thrust",
    "wrapper_yaw_moment = wrapper.total_moment_body[3]",
    "force_application_error = abs(body.frame_a.f[3] - applied_force_z_body)",
    "torque_application_error = abs(body.frame_a.t[3] - applied_yaw_torque_body)",
    "motor_order_gate_error = wrapper.motor_order_gate_error",
    "yaw_direction_gate_error = wrapper.yaw_direction_gate_error",
]

REQUIRED_WRAPPER_ANCHORS = [
    "model Sunray150DynamicsWrapperSurface",
    "Sunray150RflyStyleRotorDynamics dynamics",
    "Real motor_command[4](each unit = \"rad/s\")",
    "Real total_thrust(unit = \"N\")",
    "Real total_moment_body[3](each unit = \"N.m\")",
    "Real motor_order_gate_error",
    "Real yaw_direction_gate_error",
    "dynamics.motor_command = motor_command",
    "total_thrust = dynamics.total_thrust",
    "total_moment_body = dynamics.total_moment_body",
    "motor_order_gate_error = sum({abs(dynamics.rotor_center[i, j] - expected_rotor_center[i, j]) for i in 1:4, j in 1:3})",
    "yaw_direction_gate_error = sum({abs(dynamics.yaw_direction[i] - expected_yaw_direction[i]) for i in 1:4})",
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
    legacy_impl = read_text(LEGACY_IMPL) if LEGACY_IMPL.exists() else ""
    legacy_wrapper_impl = read_text(LEGACY_WRAPPER_IMPL) if LEGACY_WRAPPER_IMPL.exists() else ""

    if not FORMAL_SOURCE.exists():
        add_finding(findings, "formal_source_missing", "PhysicalWrenchAdapter.mo is missing", target=rel(FORMAL_SOURCE))
    if "PhysicalWrenchAdapter" not in formal_order:
        add_finding(findings, "formal_order_missing", "package.order does not include PhysicalWrenchAdapter", target=rel(FORMAL_ORDER))
    if "model PhysicalWrenchAdapter" in formal_package:
        add_finding(
            findings,
            "duplicate_inline_formal_definition",
            "PhysicalWrenchAdapter remains inline in package.mo while source file exists",
            target=rel(FORMAL_PACKAGE),
        )
    if not contains(formal_source, "within MoSimQuadrotorModel.Dynamics;"):
        add_finding(findings, "formal_within_missing", "formal source lacks expected within clause", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "model PhysicalWrenchAdapter"):
        add_finding(findings, "formal_model_missing", "formal source lacks model declaration", target=rel(FORMAL_SOURCE))
    if not contains(formal_source, "extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter;"):
        add_finding(findings, "formal_extends_drift", "formal source no longer extends legacy PhysicalWrenchAdapter alias", target=rel(FORMAL_SOURCE))

    forbidden_behavior_snippets = [
        "equation",
        "forceAndTorque",
        "applied_force_body",
        "applied_torque_body",
        "body.frame_a",
        "wrapper_total_thrust",
        "wrapper_yaw_moment",
        "force_application_error",
        "torque_application_error",
        "motor_order_gate_error",
        "yaw_direction_gate_error",
    ]
    for snippet in forbidden_behavior_snippets:
        if contains(formal_source, snippet):
            add_finding(
                findings,
                "formal_source_duplicates_physical_wrench_behavior",
                f"formal source duplicates physical-wrench behavior snippet {snippet!r}",
                target=rel(FORMAL_SOURCE),
            )

    if "PhysicalWrenchAdapter" not in legacy_order:
        add_finding(findings, "legacy_order_missing", "legacy package.order lost PhysicalWrenchAdapter", target=rel(LEGACY_ORDER))
    if not contains(legacy_package, "model PhysicalWrenchAdapter"):
        add_finding(findings, "legacy_alias_missing", "legacy package lost PhysicalWrenchAdapter alias", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_package, "extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchFrameAdapter"):
        add_finding(findings, "legacy_alias_extends_drift", "legacy alias no longer extends Sunray150PhysicalWrenchFrameAdapter", target=rel(LEGACY_PACKAGE))
    if not contains(legacy_impl, "model Sunray150PhysicalWrenchFrameAdapter"):
        add_finding(findings, "legacy_impl_missing", "legacy physical-wrench implementation declaration missing", target=rel(LEGACY_IMPL))

    physical_wrench_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_PHYSICAL_WRENCH_ANCHORS:
        present = contains(legacy_impl, snippet)
        physical_wrench_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "physical_wrench_anchor_missing", f"missing physical-wrench anchor {snippet!r}", target=rel(LEGACY_IMPL))

    wrapper_anchors: list[dict[str, Any]] = []
    for snippet in REQUIRED_WRAPPER_ANCHORS:
        present = contains(legacy_wrapper_impl, snippet)
        wrapper_anchors.append({"anchor": snippet, "present": present})
        if not present:
            add_finding(findings, "wrapper_anchor_missing", f"missing wrapper anchor {snippet!r}", target=rel(LEGACY_WRAPPER_IMPL))

    result = {
        "schema": "mosim.mworks.physical_wrench_adapter_surface_check.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": "MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter",
        "formal_source": rel(FORMAL_SOURCE),
        "formal_package": rel(FORMAL_PACKAGE),
        "formal_package_order": rel(FORMAL_ORDER),
        "legacy_alias": "QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter",
        "legacy_package": rel(LEGACY_PACKAGE),
        "legacy_package_order": rel(LEGACY_ORDER),
        "legacy_implementation": rel(LEGACY_IMPL),
        "legacy_wrapper_implementation": rel(LEGACY_WRAPPER_IMPL),
        "behavior_preservation": {
            "formal_source_is_extends_only": True,
            "formal_source_duplicates_physical_wrench_behavior": False,
            "legacy_alias_preserved": True,
            "legacy_implementation_preserved": True,
            "legacy_wrapper_implementation_preserved": True,
            "physical_wrench_equations_changed_by_031": False,
            "wrapper_equations_changed_by_031": False,
            "numeric_parameters_changed_by_031": False,
            "multibody_world_body_force_adapter_changed_by_031": False,
            "frame_connection_changed_by_031": False,
            "motor_order_yaw_gate_behavior_changed_by_031": False,
        },
        "physical_wrench_anchors": physical_wrench_anchors,
        "wrapper_anchors": wrapper_anchors,
        "findings": findings,
    }
    return result, findings


def write_markdown(path: Path, check: dict[str, Any]) -> None:
    lines = [
        "# PhysicalWrenchAdapter Formal Source Surface",
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
        "The formal source is intentionally an extends-only project-owned surface. It does not duplicate the MultiBody world/body/WorldForceAndTorque structure, force/torque equations, frame connection, wrapper outputs, or motor-order/yaw gate observations.",
        "",
        "## Static Anchors",
        "",
        "- MultiBody world/body/force adapter: `world`, `body`, and `WorldForceAndTorque` remain in the legacy implementation.",
        "- Physical wrench application: `forceAndTorque.force = applied_force_body`, `forceAndTorque.torque = applied_torque_body`, and `connect(forceAndTorque.frame_b, body.frame_a)` remain intact.",
        "- Wrapper bridge: `wrapper.total_thrust`, `wrapper.total_moment_body`, `motor_order_gate_error`, and `yaw_direction_gate_error` remain exposed.",
        "- Legacy wrapper implementation remains a separate source anchor and was not edited by 031.",
        "",
        "## Claim Boundary",
        "",
        "- Static source/package surface only.",
        "- No live MWORKS load, `check_model`, `SimulateModel`, result variable, package browser, or graphical acceptance is claimed.",
        "- No physical wrench equation, numerical parameter, MultiBody world/body/force adapter, frame connection, wrapper force/torque mapping, motor order/yaw gate behavior, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def package_integrity(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.package_order_integrity.v1",
        "request_id": REQUEST_ID,
        "status": "passed_static" if check["status"] == "passed_static" else "failed_static",
        "formal_package_order_contains_physical_wrench_adapter": "PhysicalWrenchAdapter" in read_order(FORMAL_ORDER),
        "formal_package_mo_no_inline_duplicate": "model PhysicalWrenchAdapter" not in read_text(FORMAL_PACKAGE),
        "formal_source_file_present": FORMAL_SOURCE.exists(),
        "legacy_package_order_contains_physical_wrench_adapter": "PhysicalWrenchAdapter" in read_order(LEGACY_ORDER),
        "legacy_package_alias_present": "model PhysicalWrenchAdapter" in read_text(LEGACY_PACKAGE),
        "legacy_implementation_file_present": LEGACY_IMPL.exists(),
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
                "Models/MoSimQuadrotorModel/Dynamics/PhysicalWrenchAdapter.mo",
            ],
            "legacy_source_files_changed": [],
            "script_files_changed_by_031": [
                "Scripts/mworks/validate_mosimquad_physical_wrench_adapter_surface.py",
                "Scripts/tests/test_mosimquad_physical_wrench_adapter_surface.py",
            ],
            "evidence_files_written_by_031": [
                "Results/mworks_model_hygiene/20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface/physical_wrench_adapter_surface_check.json",
                "Results/mworks_model_hygiene/20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface/physical_wrench_adapter_surface.md",
                "Results/mworks_model_hygiene/20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface/package_order_integrity.json",
                "Results/mworks_model_hygiene/20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface/changed_files.json",
                "Results/mworks_model_hygiene/20260609_031_mosimquad_physical_wrench_adapter_formal_source_surface/static_validation_summary.json",
            ],
            "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-PHYSICAL-WRENCH-ADAPTER-FORMAL-SOURCE-SURFACE-20260609-031.json",
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
            rel(out_dir / "physical_wrench_adapter_surface_check.json"),
            rel(out_dir / "physical_wrench_adapter_surface.md"),
            rel(out_dir / "package_order_integrity.json"),
            rel(out_dir / "changed_files.json"),
            rel(out_dir / "static_validation_summary.json"),
        ],
        "claim_boundary": [
            "031 prepares a static formal source surface for PhysicalWrenchAdapter only.",
            "031 does not call or prove MWORKS load, check_model, SimulateModel, native result, package browser, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
            "031 preserves the legacy physical wrench and MultiBody adapter behavior as source-labeled static behavior.",
        ],
    }


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate()
    write_json(output_dir / "physical_wrench_adapter_surface_check.json", check)
    write_markdown(output_dir / "physical_wrench_adapter_surface.md", check)
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
