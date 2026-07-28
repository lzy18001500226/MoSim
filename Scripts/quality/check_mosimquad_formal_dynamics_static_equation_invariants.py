#!/usr/bin/env python3
"""Check static equation invariants for formal Dynamics smoke variables.

This checker does not run MWORKS. It verifies that the expected future-live
smoke variables are backed by explicit Modelica declaration/equation anchors in
the current source surface.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = {
    "vehicle": ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle",
    "dynamics": ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Dynamics",
    "legacy_diagnostics": ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "LegacyDiagnostics",
    "parameters": ROOT / "Models" / "MoSimQuadrotorModel" / "Parameters",
}
CURRENT_STATIC_ROOT = (
    ROOT
    / "Results"
    / "model_library_refactor"
    / "20260726_plant_runner_baseline"
    / "static_checks"
)
READINESS = CURRENT_STATIC_ROOT / "dynamics_smoke_readiness.json"
DEFAULT_OUTPUT = CURRENT_STATIC_ROOT / "formal_dynamics_invariants.json"


ANCHOR_GROUPS: dict[str, dict[str, Any]] = {
    "rotor_core": {
        "source_root": "dynamics",
        "source": "RotorActuatorCore.mo",
        "anchors": [
            "parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile",
            "nominal_thrust[i] = lift_coefficient * omega[i] * omega[i]",
            "fault_effectiveness[i] = if i == fault_rotor_index and time >= fault_start_s then",
            "thrust[i] = fault_effectiveness[i] * thrust_effectiveness[i] * nominal_thrust[i]",
            "yaw_reaction_moment[i] = fault_effectiveness[i] * yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust_effectiveness[i] * nominal_thrust[i]",
            "rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i]",
            "rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i]",
            "rotor_arm_moment[i, 3] = yaw_reaction_moment[i]",
            "total_thrust = sum(thrust)",
            "total_moment_body[1] = sum({rotor_arm_moment[i, 1] for i in 1:4})",
            "total_moment_body[2] = sum({rotor_arm_moment[i, 2] for i in 1:4})",
            "total_moment_body[3] = sum({rotor_arm_moment[i, 3] for i in 1:4})",
            "hover_thrust_error = total_thrust - mass_kg * gravity_mps2",
            "minimum_thrust_effectiveness = min({fault_effectiveness[i] * thrust_effectiveness[i] for i in 1:4})",
            "minimum_reaction_moment_effectiveness = min({fault_effectiveness[i] * reaction_moment_effectiveness[i] for i in 1:4})",
        ],
    },
    "virtual_px4_classic_profile": {
        "source_root": "parameters",
        "source": "Sunray150VirtualPx4Classic.mo",
        "anchors": [
            "record Sunray150VirtualPx4Classic",
            "parameter Real gravity_mps2(unit = \"m/s2\") = 9.80665",
            "parameter Real takeoff_mass_kg(unit = \"kg\") = 1.0",
            "parameter Real mworks_quad_chassis_body_mass_kg(unit = \"kg\") = 0.980",
            "parameter Real mworks_physical_wrench_body_mass_kg(unit = \"kg\") = 1.0",
            "parameter Real mworks_rotor_center_m[4, 3]",
            "parameter Real mworks_yaw_direction[4] = {1, -1, 1, -1}",
        ],
    },
    "wrapper_surface": {
        "source_root": "dynamics",
        "source": "WrapperSurface.mo",
        "anchors": [
            "dynamics.motor_command = motor_command",
            "commanded_thrust[i] = dynamics.fault_effectiveness[i] * dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
            "commanded_yaw_reaction_moment[i] = dynamics.fault_effectiveness[i] * dynamics.yaw_direction[i] * dynamics.reaction_moment_effectiveness[i] * dynamics.moment_constant * dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i]",
            "total_thrust = dynamics.total_thrust",
            "total_moment_body = dynamics.total_moment_body",
            "commanded_total_thrust = sum(commanded_thrust)",
            "commanded_total_moment_body[3] = sum({commanded_rotor_arm_moment[i, 3] for i in 1:4})",
            "yaw_moment_gate = total_moment_body[3]",
            "commanded_yaw_moment_gate = commanded_total_moment_body[3]",
            "motor_order_gate_error = sum({abs(dynamics.rotor_center[i, j] - expected_rotor_center[i, j]) for i in 1:4, j in 1:3})",
            "yaw_direction_gate_error = sum({abs(dynamics.yaw_direction[i] - expected_yaw_direction[i]) for i in 1:4})",
        ],
    },
    "physical_wrench_adapter": {
        "source_root": "dynamics",
        "source": "PhysicalWrenchAdapter.mo",
        "anchors": [
            "applied_force_body = {0, 0, wrapper.total_thrust}",
            "applied_torque_body = wrapper.total_moment_body",
            "forceAndTorque.force = applied_force_body",
            "forceAndTorque.torque = applied_torque_body",
            "connect(forceAndTorque.frame_b, body.frame_a)",
            "applied_force_z_body = applied_force_body[3]",
            "applied_yaw_torque_body = applied_torque_body[3]",
            "force_application_error = abs(body.frame_a.f[3] - applied_force_z_body)",
            "torque_application_error = abs(body.frame_a.t[3] - applied_yaw_torque_body)",
            "hover_weight_balance_error = wrapper.total_thrust - wrapper.dynamics.mass_kg * world.g",
        ],
    },
    "rotor_effectiveness_smoke": {
        "source_root": "legacy_diagnostics",
        "source": "RotorEffectivenessSmoke.mo",
        "anchors": [
            "parameter Real degraded_rotor_thrust_effectiveness = 0.85",
            "thrust_effectiveness = {",
            "total_thrust_loss = expected_nominal_total_thrust - dynamics.total_thrust",
            "roll_moment_imbalance = dynamics.total_moment_body[1]",
            "pitch_moment_imbalance = dynamics.total_moment_body[2]",
            "yaw_moment_imbalance = dynamics.total_moment_body[3]",
        ],
    },
}


IMPLEMENTATION_BY_MODEL = {
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.HoverSmoke": "HoverSmoke.mo",
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.YawStepSmoke": "YawStepSmoke.mo",
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperHoverSmoke": "WrapperHoverSmoke.mo",
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperYawStepSmoke": "WrapperYawStepSmoke.mo",
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchHoverSmoke": "PhysicalWrenchHoverSmoke.mo",
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchYawStepSmoke": "PhysicalWrenchYawStepSmoke.mo",
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.RotorEffectivenessSmoke": "RotorEffectivenessSmoke.mo",
}

HISTORICAL_DIAGNOSTIC_NAMESPACES = (
    "MoSimQuadrotorModel.Vehicle.Dynamics.",
    "MoSimQuadrotorModel.Dynamics.",
)
HISTORICAL_DIAGNOSTIC_NAMES = frozenset(
    model_name.rsplit(".", 1)[1] for model_name in IMPLEMENTATION_BY_MODEL
)

DEPENDENCY_GROUPS_BY_MODEL = {
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.HoverSmoke": ["rotor_core", "virtual_px4_classic_profile"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.YawStepSmoke": ["rotor_core", "virtual_px4_classic_profile"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperHoverSmoke": ["wrapper_surface", "rotor_core", "virtual_px4_classic_profile"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperYawStepSmoke": ["wrapper_surface", "rotor_core", "virtual_px4_classic_profile"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchHoverSmoke": ["physical_wrench_adapter", "wrapper_surface", "rotor_core", "virtual_px4_classic_profile"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchYawStepSmoke": ["physical_wrench_adapter", "wrapper_surface", "rotor_core", "virtual_px4_classic_profile"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.RotorEffectivenessSmoke": ["rotor_effectiveness_smoke", "rotor_core", "virtual_px4_classic_profile"],
}

INSTANCE_ANCHORS_BY_MODEL = {
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.HoverSmoke": ["MoSimQuadrotorModel.Vehicle.Dynamics.RotorActuatorCore dynamics"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.YawStepSmoke": [
        "Real yaw_step",
        "Real rotor_speed_mag[4]",
        "MoSimQuadrotorModel.Vehicle.Dynamics.RotorActuatorCore dynamics",
    ],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperHoverSmoke": ["MoSimQuadrotorModel.Vehicle.Dynamics.WrapperSurface wrapper"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperYawStepSmoke": [
        "Real yaw_step",
        "Real rotor_speed_mag[4]",
        "MoSimQuadrotorModel.Vehicle.Dynamics.WrapperSurface wrapper",
    ],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchHoverSmoke": ["MoSimQuadrotorModel.Vehicle.Dynamics.PhysicalWrenchAdapter adapter"],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchYawStepSmoke": [
        "Real yaw_step",
        "Real rotor_speed_mag[4]",
        "MoSimQuadrotorModel.Vehicle.Dynamics.PhysicalWrenchAdapter adapter",
    ],
    "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.RotorEffectivenessSmoke": [
        "MoSimQuadrotorModel.Vehicle.Dynamics.RotorActuatorCore dynamics",
        "thrust_effectiveness = {",
        "Real total_thrust_loss",
        "Real roll_moment_imbalance",
        "Real pitch_moment_imbalance",
        "Real yaw_moment_imbalance",
    ],
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def normalized(text: str) -> str:
    return " ".join(text.replace("\r\n", "\n").split())


def canonical_model_name(model_name: str) -> str:
    """Map historical result references onto the current diagnostic source FQN."""

    for namespace in HISTORICAL_DIAGNOSTIC_NAMESPACES:
        if model_name.startswith(namespace):
            leaf_name = model_name[len(namespace) :]
            if leaf_name in HISTORICAL_DIAGNOSTIC_NAMES:
                return "MoSimQuadrotorModel.Vehicle.LegacyDiagnostics." + leaf_name
    return model_name


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str | None = None) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    if target:
        item["target"] = target
    findings.append(item)


def check_anchor_group(name: str, group: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any]:
    source_root = str(group.get("source_root", "vehicle"))
    source = SOURCE_ROOTS[source_root] / str(group["source"])
    if not source.exists():
        add_finding(findings, "missing_source", "invariant source file is missing", rel(source))
        return {"group": name, "source": rel(source), "missing_anchors": group["anchors"]}
    text = normalized(source.read_text(encoding="utf-8"))
    missing = [anchor for anchor in group["anchors"] if normalized(anchor) not in text]
    if missing:
        add_finding(findings, "missing_equation_anchor", "one or more expected equation anchors are missing", rel(source))
    return {"group": name, "source": rel(source), "anchor_count": len(group["anchors"]), "missing_anchors": missing}


def check_model_sources(readiness: dict[str, Any], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for scenario in readiness.get("scenarios", []):
        requested_model_name = str(scenario.get("model_name") or "")
        model_name = canonical_model_name(requested_model_name)
        source_name = IMPLEMENTATION_BY_MODEL.get(model_name)
        if not source_name:
            add_finding(findings, "missing_model_source_mapping", "no implementation source mapping for model", model_name)
            continue
        source = SOURCE_ROOTS["legacy_diagnostics"] / source_name
        if not source.exists():
            add_finding(findings, "missing_model_source", "mapped implementation source is missing", rel(source))
            continue
        text = normalized(source.read_text(encoding="utf-8"))
        expected_variables = [str(item) for item in scenario.get("expected_result_variables", [])]
        instance_anchors = INSTANCE_ANCHORS_BY_MODEL.get(model_name, [])
        missing_instance_anchors = [anchor for anchor in instance_anchors if normalized(anchor) not in text]
        if missing_instance_anchors:
            add_finding(findings, "missing_instance_anchor", "scenario source is missing expected instance or local variable anchors", rel(source))
        dependency_groups = DEPENDENCY_GROUPS_BY_MODEL.get(model_name, [])
        if not dependency_groups:
            add_finding(findings, "missing_dependency_group_mapping", "no dependency invariant group mapping for model", model_name)
        summaries.append(
            {
                "model_name": model_name,
                "requested_model_name": requested_model_name,
                "source": rel(source),
                "dependency_anchor_groups": dependency_groups,
                "expected_variable_count": len(expected_variables),
                "missing_instance_anchors": missing_instance_anchors,
            }
        )
    return summaries


def build_summary(readiness_path: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    readiness = read_json(readiness_path)
    if readiness.get("status") != "ready_but_blocked_by_gui":
        add_finding(findings, "readiness_status_drift", "live-smoke readiness must be ready_but_blocked_by_gui before invariant check", rel(readiness_path))

    groups = [check_anchor_group(name, group, findings) for name, group in ANCHOR_GROUPS.items()]
    model_sources = check_model_sources(readiness, findings)

    return {
        "schema": "mosim.mworks.formal_dynamics_static_equation_invariants.v1",
        "status": "passed" if not findings else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "readiness": rel(readiness_path),
        "anchor_groups": groups,
        "model_sources": model_sources,
        "claim_boundary": [
            "This checks Modelica source anchors only.",
            "It does not run MWORKS, check_model, SimulateModel, result extraction, controller performance, mission success, or closed_loop.",
            "Equation anchors explain future-live smoke variables but do not prove runtime solvability.",
        ],
        "findings": findings,
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Formal Dynamics Static Equation Invariants",
        "",
        f"Status: `{summary['status']}`",
        "",
        "Static-only source-anchor check for future live smoke variables.",
        "",
        "## Anchor Groups",
        "",
    ]
    for group in summary["anchor_groups"]:
        lines.append(f"- `{group['group']}` -> `{group['source']}` anchors={group.get('anchor_count', 0)}")
    lines.extend(["", "## Model Sources", ""])
    for item in summary["model_sources"]:
        lines.append(f"- `{item['model_name']}` -> `{item['source']}` variables={item['expected_variable_count']}")
    lines.extend(["", "## Findings", ""])
    if summary["findings"]:
        for item in summary["findings"]:
            lines.append(f"- `{item['code']}`: {item['message']}")
    else:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readiness", type=Path, default=READINESS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    readiness = args.readiness if args.readiness.is_absolute() else ROOT / args.readiness
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary = build_summary(readiness)
    write_json(output, summary)
    write_markdown(output.with_suffix(".md"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
