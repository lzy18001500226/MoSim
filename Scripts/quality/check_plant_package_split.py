#!/usr/bin/env python3
"""Validate the canonical Vehicle assembly and its shared Runner boundary.

The former monolithic vehicle package was already split before the current
eight-layer migration.  This checker therefore verifies the current physical
surface instead of trying to re-run a historical split against a retired
namespace.  It is source-only; fresh MWORKS model checks and simulations remain
separate acceptance gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VEHICLE_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle"
ROOT_PACKAGE = VEHICLE_ROOT / "package.mo"
ORDER_PATH = VEHICLE_ROOT / "package.order"
RUNNER_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners"
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "model_library_refactor"
    / "20260726_vehicle_assembly"
    / "VEHICLE_ASSEMBLY_STATIC_CHECK.json"
)

EXPECTED_ORDER = (
    "Sunray150Assembly",
    "Sunray150GazeboAlignedVisualChassis",
    "Dynamics",
    "Blocks",
    "Electricals",
    "Examples",
    "GroundModel",
    "Mechanics",
    "Sensors",
    "Utilities",
    "LegacyDiagnostics",
)
RUNNER_SOURCES = (
    "AttitudeThrustRunner.mo",
    "BodyRateThrustRunner.mo",
    "WrenchRunner.mo",
    "RotorCommandRunner.mo",
    "FormalAttitudeThrustRunnerBase.mo",
)
CANONICAL_CHASSIS = VEHICLE_ROOT / "Sunray150GazeboAlignedVisualChassis.mo"
CANONICAL_ASSEMBLY = VEHICLE_ROOT / "Sunray150Assembly.mo"


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def missing_anchors(path: Path, anchors: tuple[str, ...]) -> list[str]:
    if not path.is_file():
        return list(anchors)
    text = normalized_text(path)
    return [anchor for anchor in anchors if anchor not in text]


def package_member_status(name: str) -> dict[str, str]:
    package_path = VEHICLE_ROOT / name / "package.mo"
    model_path = VEHICLE_ROOT / f"{name}.mo"
    if package_path.is_file():
        return {"name": name, "path": relative(package_path), "status": "passed"}
    if model_path.is_file():
        return {"name": name, "path": relative(model_path), "status": "passed"}
    return {"name": name, "path": relative(model_path), "status": "missing"}


def check_vehicle_contract() -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    root_text = normalized_text(ROOT_PACKAGE) if ROOT_PACKAGE.is_file() else ""
    expected_root = (
        "within MoSimQuadrotorModel;\n"
        "package Vehicle \"Sunray150 assembly, physical plant, actuation, and sensing\"\n"
        "  extends Modelica.Icons.Package;\n"
        "  annotation(uses(Modelica(version = \"4.0.0.TY.1\")));\n"
        "end Vehicle;\n"
    )
    if root_text != expected_root:
        findings.append({"code": "vehicle_root_surface_drift", "message": relative(ROOT_PACKAGE)})

    actual_order = ORDER_PATH.read_text(encoding="utf-8").splitlines() if ORDER_PATH.is_file() else []
    if actual_order != list(EXPECTED_ORDER):
        findings.append({"code": "vehicle_package_order_drift", "message": relative(ORDER_PATH)})

    members = [package_member_status(name) for name in EXPECTED_ORDER]
    for item in members:
        if item["status"] != "passed":
            findings.append({"code": "vehicle_member_missing", "message": item["path"]})

    chassis_anchors = (
        "within MoSimQuadrotorModel.Vehicle;",
        "model Sunray150GazeboAlignedVisualChassis",
        "extends MoSimQuadrotorModel.Vehicle.Mechanics.QuadChassis(",
        "propellers4(",
    )
    assembly_anchors = (
        "within MoSimQuadrotorModel.Vehicle;",
        "model Sunray150Assembly",
        "parameter Real initial_rotor_speed[4]",
        "Modelica.Blocks.Interfaces.RealInput rotor_command[4];",
        "Modelica.Blocks.Interfaces.RealOutput position[3];",
        "Modelica.Blocks.Interfaces.RealOutput attitude[3];",
        "Modelica.Blocks.Interfaces.RealOutput rotor_speed[4];",
        "MoSimQuadrotorModel.Vehicle.Dynamics.PhysicalWrenchAdapter physical(",
        "MoSimQuadrotorModel.Vehicle.Sensors.Sensors sensors;",
        "connect(gust.frame_b, physical.body.frame_a);",
        "connect(physical.body.frame_a, sensors.frame_a);",
        "physical.wrapper.motor_command[i] = rotor_command[i];",
        "rotor_speed[i] = physical.wrapper.dynamics.omega[i];",
        "rotor_thrust[i] = physical.wrapper.dynamics.thrust[i];",
        "rotor_yaw_reaction_moment[i] = physical.wrapper.dynamics.yaw_reaction_moment[i];",
        "applied_reaction_yaw_moment = physical.applied_yaw_torque_body;",
        "position = sensors.PosMea;",
        "attitude = sensors.AngleMea;",
    )
    canonical = {
        "canonical_chassis": relative(CANONICAL_CHASSIS),
        "canonical_assembly": relative(CANONICAL_ASSEMBLY),
        "canonical_chassis_missing_anchors": missing_anchors(CANONICAL_CHASSIS, chassis_anchors),
        "canonical_assembly_missing_anchors": missing_anchors(CANONICAL_ASSEMBLY, assembly_anchors),
        "runner_sources": [],
    }
    for label in ("canonical_chassis", "canonical_assembly"):
        missing = canonical[f"{label}_missing_anchors"]
        if missing:
            findings.append({"code": "canonical_vehicle_anchor_missing", "message": f"{label}: {', '.join(missing)}"})

    expected_reference = "MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant"
    for name in RUNNER_SOURCES:
        path = RUNNER_ROOT / name
        text = normalized_text(path) if path.is_file() else ""
        item = {"path": relative(path), "status": "passed"}
        if expected_reference not in text:
            item["status"] = "failed"
            findings.append({"code": "runner_not_on_shared_vehicle", "message": item["path"]})
        canonical["runner_sources"].append(item)

    return {
        "schema": "mosim.vehicle_assembly_static_check.v1",
        "status": "passed" if not findings else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "root_package": relative(ROOT_PACKAGE),
        "package_order": actual_order,
        "members": members,
        "canonical_assembly": canonical,
        "findings": findings,
        "claim_boundary": "This validates current source structure and shared Vehicle wiring only. Fresh MWORKS CheckModel and simulation are still required for acceptance.",
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = check_vehicle_contract()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    write_report(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
