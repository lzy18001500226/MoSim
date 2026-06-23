#!/usr/bin/env python3
"""Audit Gazebo Sunray150 assembled plant parameters against reviewed sources."""

from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSEMBLY = ROOT / "Results" / "unreal_scene_mapping" / "sunray150_dae_assembly_parameters_20260604.json"
DEFAULT_SDF = ROOT / "Config" / "gazebo" / "models" / "sunray150_assembled" / "model.sdf"
DEFAULT_SCENARIO = ROOT / "Config" / "scenarios" / "system" / "sunray150_single_uav_competition_light.yaml"
DEFAULT_OUT_DIR = ROOT / "Results" / "gazebo_ros2" / "sunray150_assembled_parameter_audit_20260618"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def floats(text: str | None) -> list[float]:
    if text is None:
        return []
    return [float(item) for item in text.split()]


def find_model(root: ET.Element) -> ET.Element:
    model = root.find("model")
    if model is None:
        raise ValueError("SDF root has no model element")
    return model


def link(model: ET.Element, name: str) -> ET.Element:
    for item in model.findall("link"):
        if item.get("name") == name:
            return item
    raise ValueError(f"link not found: {name}")


def plugin_values(model: ET.Element) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for plugin in model.findall("plugin"):
        joint = plugin.findtext("jointName")
        if not joint or not joint.startswith("rotor_"):
            continue
        values.append(
            {
                "jointName": joint,
                "linkName": plugin.findtext("linkName"),
                "turningDirection": plugin.findtext("turningDirection"),
                "motorConstant": float(plugin.findtext("motorConstant") or "nan"),
                "momentConstant": float(plugin.findtext("momentConstant") or "nan"),
                "maxRotVelocity": float(plugin.findtext("maxRotVelocity") or "nan"),
                "rotorVelocitySlowdownSim": float(plugin.findtext("rotorVelocitySlowdownSim") or "nan"),
                "timeConstantUp": float(plugin.findtext("timeConstantUp") or "nan"),
                "timeConstantDown": float(plugin.findtext("timeConstantDown") or "nan"),
                "motorNumber": plugin.findtext("motorNumber"),
                "actuator_number": plugin.findtext("actuator_number"),
                "commandSubTopic": plugin.findtext("commandSubTopic"),
            }
        )
    return sorted(values, key=lambda item: item["jointName"])


def near(left: list[float], right: list[float], tol: float = 1e-9) -> bool:
    return len(left) == len(right) and all(abs(a - b) <= tol for a, b in zip(left, right))


def format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.9g}"
    if isinstance(value, list):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def status_for(source_policy: str, actual: Any, expected: Any) -> str:
    if source_policy == "hold_for_review":
        return "held_for_review" if actual != expected else "matches_held_candidate"
    if source_policy == "do_not_replace":
        return "separate_source_required"
    if isinstance(actual, list) and isinstance(expected, list):
        return "adopted" if near(actual, expected) else "mismatch"
    return "adopted" if actual == expected else "mismatch"


def build_audit(assembly: dict[str, Any], sdf_path: Path, scenario_path: Path) -> dict[str, Any]:
    tree = ET.parse(sdf_path)
    model = find_model(tree.getroot())
    base = link(model, "base_link")
    collision = base.find("collision[@name='body_collision']")
    if collision is None:
        raise ValueError("body_collision not found")
    inertial = base.find("inertial")
    if inertial is None:
        raise ValueError("base_link inertial not found")

    rows: list[dict[str, Any]] = []
    sdf_rotors = assembly["sdf_rotor_mapping"]
    for rotor_name, expected in sdf_rotors.items():
        rotor_link = link(model, rotor_name)
        actual = floats(rotor_link.findtext("pose"))[:3]
        rows.append(
            {
                "category": "geometry",
                "parameter": f"{rotor_name}.pose.xyz",
                "source_policy": "replace",
                "expected_source": "sunray150_dae_assembly_parameters_20260604.json:sdf_rotor_mapping",
                "expected": expected,
                "actual_source": rel(sdf_path),
                "actual": actual,
                "status": status_for("replace", actual, expected),
                "action": "none" if near(actual, expected) else "fix_required",
            }
        )

    collision_expected_pose = assembly["collision_envelope"]["base_link_box_pose_xyz_rpy"]
    collision_expected_size = assembly["collision_envelope"]["base_link_box_size_xyz"]
    collision_pose = floats(collision.findtext("pose"))
    collision_size = floats(collision.findtext("geometry/box/size"))
    for parameter, actual, expected in [
        ("base_link.body_collision.pose", collision_pose, collision_expected_pose),
        ("base_link.body_collision.size", collision_size, collision_expected_size),
    ]:
        rows.append(
            {
                "category": "geometry",
                "parameter": parameter,
                "source_policy": "replace",
                "expected_source": "sunray150_dae_assembly_parameters_20260604.json:collision_envelope",
                "expected": expected,
                "actual_source": rel(sdf_path),
                "actual": actual,
                "status": status_for("replace", actual, expected),
                "action": "none" if near(actual, expected) else "fix_required",
            }
        )

    lidar_pose = floats(base.findtext("sensor[@name='mid360_lidar']/pose"))
    mid360_candidate = assembly["mid360"]["mechanical_mount_pose_xyz_rpy_candidate"]
    rows.append(
        {
            "category": "sensor_geometry",
            "parameter": "base_link.mid360_lidar.pose",
            "source_policy": "hold_for_review",
            "expected_source": "sunray150_dae_assembly_parameters_20260604.json:mid360.mechanical_mount_pose_xyz_rpy_candidate",
            "expected": mid360_candidate,
            "actual_source": rel(sdf_path),
            "actual": lidar_pose,
            "status": status_for("hold_for_review", lidar_pose, mid360_candidate),
            "action": "no_change_until_lidar_extrinsic_review",
        }
    )

    base_mass = float(inertial.findtext("mass") or "nan")
    rotor_masses: list[float] = []
    for idx in range(4):
        rotor_masses.append(float(link(model, f"rotor_{idx}").findtext("inertial/mass") or "nan"))
    total_mass = base_mass + sum(rotor_masses)
    inertia = {
        axis: float(inertial.findtext(f"inertia/{axis}") or "nan")
        for axis in ["ixx", "iyy", "izz", "ixy", "ixz", "iyz"]
    }
    rows.extend(
        [
            {
                "category": "dynamics",
                "parameter": "base_link.mass",
                "source_policy": "do_not_replace",
                "expected_source": "separate plant seed/calibration; assembly JSON explicitly excludes mass",
                "expected": "not_from_assembly_json",
                "actual_source": rel(sdf_path),
                "actual": base_mass,
                "status": "separate_source_required",
                "action": "confirm_by_plant_gate_not_by_geometry_json",
            },
            {
                "category": "dynamics",
                "parameter": "rotor_links.total_mass",
                "source_policy": "do_not_replace",
                "expected_source": "SDF link inertials",
                "expected": "included_in_total_plant_mass",
                "actual_source": rel(sdf_path),
                "actual": sum(rotor_masses),
                "status": "separate_source_required",
                "action": "include_in_hover_estimate",
            },
            {
                "category": "dynamics",
                "parameter": "plant.total_link_mass",
                "source_policy": "derived",
                "expected_source": "sum(base_link.mass + rotor link masses)",
                "expected": "used_for_hover_sanity_estimate",
                "actual_source": rel(sdf_path),
                "actual": total_mass,
                "status": "derived_from_sdf",
                "action": "use_for_gazebo_plant_validation",
            },
            {
                "category": "dynamics",
                "parameter": "base_link.inertia",
                "source_policy": "do_not_replace",
                "expected_source": "separate plant seed/calibration; assembly JSON explicitly excludes inertia",
                "expected": "not_from_assembly_json",
                "actual_source": rel(sdf_path),
                "actual": inertia,
                "status": "separate_source_required",
                "action": "confirm_by_plant_gate_not_by_geometry_json",
            },
        ]
    )

    plugins = plugin_values(model)
    if plugins:
        motor_constant = plugins[0]["motorConstant"]
        max_rot_velocity = plugins[0]["maxRotVelocity"]
        hover_speed = math.sqrt(total_mass * 9.80665 / (4.0 * motor_constant))
        normalized_hover = hover_speed / max_rot_velocity
    else:
        hover_speed = float("nan")
        normalized_hover = float("nan")
    rows.append(
        {
            "category": "motor_plugin",
            "parameter": "MulticopterMotorModel.rotor_set",
            "source_policy": "do_not_replace",
            "expected_source": "separate motor plugin seed/calibration; assembly JSON explicitly excludes motorConstant/momentConstant",
            "expected": "four rotor plugins with rotor_0..rotor_3 actuator mapping",
            "actual_source": rel(sdf_path),
            "actual": plugins,
            "status": "separate_source_required",
            "action": "confirm_by_plant_gate_and_keep_controller_adapter_mapping_aligned",
        }
    )
    rows.append(
        {
            "category": "derived",
            "parameter": "theoretical_hover_normalized_command",
            "source_policy": "derived",
            "expected_source": "sqrt(total_mass*g/(4*motorConstant))/maxRotVelocity",
            "expected": "near simple-controller hover command",
            "actual_source": rel(sdf_path),
            "actual": {
                "hover_angular_speed_rad_s": hover_speed,
                "normalized_hover_command": normalized_hover,
                "total_mass_kg": total_mass,
            },
            "status": "derived_from_sdf",
            "action": "use_as_sanity_check_not_acceptance",
        }
    )

    statuses: dict[str, int] = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    return {
        "schema": "mosim.gazebo_sunray150_parameter_audit.v1",
        "status": "completed",
        "assembly_source": rel(project_path(DEFAULT_ASSEMBLY if assembly else DEFAULT_ASSEMBLY)),
        "sdf": rel(sdf_path),
        "scenario": rel(scenario_path),
        "summary": {
            "row_count": len(rows),
            "status_counts": statuses,
            "geometry_mismatches": [row["parameter"] for row in rows if row["source_policy"] == "replace" and row["status"] == "mismatch"],
            "held_for_review": [row["parameter"] for row in rows if row["status"] == "held_for_review"],
            "sdf_total_link_mass_kg": total_mass,
            "theoretical_hover_normalized_command": normalized_hover,
        },
        "rows": rows,
        "claim_boundary": [
            "This audit confirms source/parameter consistency only.",
            "Mass, inertia, motor constants, moment constants, lift coefficients, controller gains, and sensor timing are not replaced from the assembly JSON.",
            "Takeoff, hover, and landing require separate Gazebo runtime evidence.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Gazebo Sunray150 Parameter Consistency Audit",
        "",
        f"- status: `{report['status']}`",
        f"- SDF: `{report['sdf']}`",
        f"- scenario: `{report['scenario']}`",
        f"- total SDF link mass: `{report['summary']['sdf_total_link_mass_kg']:.6f} kg`",
        f"- theoretical normalized hover command: `{report['summary']['theoretical_hover_normalized_command']:.6f}`",
        "",
        "| Category | Parameter | Policy | Expected | Actual | Status | Action |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["category"],
                    f"`{row['parameter']}`",
                    row["source_policy"],
                    f"`{format_value(row['expected'])}`",
                    f"`{format_value(row['actual'])}`",
                    row["status"],
                    row["action"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- `replace` rows must match the reviewed DAE assembly parameters.",
            "- `hold_for_review` rows are intentionally not rewritten by this audit.",
            "- `do_not_replace` rows must be validated by plant/runtime gates, not by the geometry assembly JSON.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembly-json", default=DEFAULT_ASSEMBLY, type=Path)
    parser.add_argument("--sdf", default=DEFAULT_SDF, type=Path)
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO, type=Path)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, type=Path)
    args = parser.parse_args()

    assembly_path = project_path(args.assembly_json)
    sdf_path = project_path(args.sdf)
    scenario_path = project_path(args.scenario)
    out_dir = project_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assembly = load_json(assembly_path)
    report = build_audit(assembly, sdf_path, scenario_path)
    report["assembly_source"] = rel(assembly_path)
    json_path = out_dir / "gazebo_parameter_consistency_audit.json"
    md_path = out_dir / "GAZEBO_PARAMETER_CONSISTENCY_AUDIT.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": "completed", "json": rel(json_path), "markdown": rel(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
