#!/usr/bin/env python3
"""Build the current 46-route controller interface and dependency matrix.

The current graphical controller models are deliberately separated from their
future whole-aircraft adapters.  This builder keeps that distinction explicit:
it reports the ports actually exposed by the source, identifies fixed-input
graphical probes, and records the target typed Runner boundary without
promoting a route to a closed-loop claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = ROOT / "Config" / "control_platform"
CATALOG_PATH = CONFIG_ROOT / "control_scheme_catalog.json"
CURRENT_MAP_PATH = CONFIG_ROOT / "current_model_entry_map.json"
HARNESS_MAP_PATH = CONFIG_ROOT / "formal_closed_loop_harness_map.json"
RUNNER_CONTRACT_PATH = CONFIG_ROOT / "offline_runner_interface_contract_v1.json"
OUTPUT_PATH = CONFIG_ROOT / "controller_route_interface_matrix.json"

SCHEMA = "mosim.controller_route_interface_matrix.v1"

PORT_PATTERN = re.compile(
    r"^\s*SysplorerEmbeddedCoder\.Port\.(Inport|Outport)\s+([A-Za-z_]\w*)\b",
    re.MULTILINE,
)
CONSTANT_PATTERN = re.compile(
    r"^\s*SysplorerEmbeddedCoder\.Sources\.Constant\s+([A-Za-z_]\w*)\b",
    re.MULTILINE,
)
IMPORT_PATTERN = re.compile(r"^\s*import\s+([^;]+);", re.MULTILINE)
EXTENDS_PATTERN = re.compile(r"^\s*extends\s+([^;]+);", re.MULTILINE)
PROJECT_REFERENCE_PATTERN = re.compile(
    r"\bMoSimQuadrotorModel(?:\.[A-Za-z_]\w*)+\b"
)

SEVEN_SCENARIO_AB_MATRIX = (
    "hover",
    "step",
    "figure8",
    "spiral",
    "wind",
    "parameter_mismatch",
    "motor_efficiency_fault",
)


class MatrixError(ValueError):
    """Raised when one source map cannot produce a safe route row."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MatrixError(f"JSON object required: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def project_file(path_text: Any, label: str) -> Path:
    if not isinstance(path_text, str) or not path_text:
        raise MatrixError(f"{label}: project-relative file path is required")
    path = ROOT / path_text
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise MatrixError(f"{label}: path leaves the project: {path_text}") from exc
    if not path.is_file():
        raise MatrixError(f"{label}: missing file: {path_text}")
    return path


def source_surface(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    inports: list[str] = []
    outports: list[str] = []
    for direction, name in PORT_PATTERN.findall(text):
        if direction == "Inport":
            inports.append(name)
        else:
            outports.append(name)
    constants = CONSTANT_PATTERN.findall(text)
    extends = [item.strip() for item in EXTENDS_PATTERN.findall(text)]
    imports = [item.strip() for item in IMPORT_PATTERN.findall(text)]
    project_references = unique(PROJECT_REFERENCE_PATTERN.findall(text))
    inports = unique(inports)
    outports = unique(outports)
    constants = unique(constants)
    if inports:
        input_mode = "explicit_graphical_inports"
    elif constants:
        input_mode = "fixed_constant_sources_without_public_inports"
    else:
        input_mode = "no_public_graphical_input_detected"
    return {
        "source_sha256": sha256_file(path),
        "input_mode": input_mode,
        "inports": inports,
        "outports": outports,
        "constant_sources": constants,
        "extends": extends,
        "imports": imports,
        "project_model_references": project_references,
    }


def boundary_reference(
    boundary_name: str, boundaries: dict[str, Any]
) -> dict[str, Any] | None:
    if boundary_name == "WHOLE_AIRCRAFT_EMBEDDED":
        return None
    value = boundaries.get(boundary_name)
    if not isinstance(value, dict):
        raise MatrixError(f"unknown Runner boundary: {boundary_name}")
    return {
        "boundary": boundary_name,
        "interface": value.get("interface"),
        "interface_source": value.get("interface_source"),
        "runner": value.get("runner"),
        "runner_source": value.get("runner_source"),
        "outputs": value.get("outputs"),
    }


def candidate_boundary(scheme_id: str, outports: list[str]) -> str:
    names = set(outports)
    if scheme_id == "official_pid":
        return "ROTOR_COMMAND"
    if any(name.startswith("wrench_") for name in names) or {
        "body_force",
        "body_torque",
    } <= names:
        return "WRENCH"
    if any(name.startswith("desired_body_rate_") for name in names):
        return "BODY_RATE_THRUST"
    return "ATTITUDE_THRUST"


def core_migration_state(
    scheme_id: str,
    surface: dict[str, Any],
    target_boundary: str,
) -> tuple[str, str]:
    """Return the required core work and adapter work without overclaiming."""
    inports = surface["inports"]
    outports = set(surface["outports"])
    if scheme_id in {"trained_neural_residual", "rl_gain_scheduler"}:
        return (
            "bind_learning_residual_to_one_fixed_nominal_host_and_parameterize_inputs",
            "add_host_specific_attitude_thrust_adapter_with_explicit_fallback",
        )
    if scheme_id == "official_pid":
        return (
            "verify_graphical_baseline_against_the_existing_physical_pid_core",
            "verify_official_pid_rotor_adapter_against_the_graphical_baseline",
        )
    if target_boundary == "WRENCH":
        if inports:
            return (
                "bind_existing_explicit_ports_to_typed_inputs",
                "add_wrench_adapter_and_validate_allocator_signs",
            )
        return (
            "parameterize_fixed_graphical_inputs_before_wrench_binding",
            "add_wrench_adapter_and_validate_allocator_signs",
        )
    if target_boundary == "BODY_RATE_THRUST":
        if inports:
            return (
                "bind_existing_explicit_ports_to_typed_inputs",
                "add_body_rate_thrust_adapter_and_validate_rate_semantics",
            )
        return (
            "parameterize_fixed_graphical_inputs_before_body_rate_binding",
            "add_body_rate_thrust_adapter_and_validate_rate_semantics",
        )
    if {"desired_roll_rad_out", "desired_pitch_rad_out"} <= outports:
        if inports:
            return (
                "bind_existing_explicit_ports_to_typed_inputs",
                "add_attitude_thrust_adapter_and_validate_collective_scaling",
            )
        return (
            "parameterize_fixed_graphical_inputs_before_attitude_binding",
            "add_attitude_thrust_adapter_and_validate_collective_scaling",
        )
    if any(name.startswith("desired_acceleration_") for name in outports):
        return (
            "parameterize_fixed_graphical_inputs_and_preserve_acceleration_outputs",
            "add_acceleration_to_attitude_thrust_projection_adapter",
        )
    if "command" in outports:
        return (
            "parameterize_fixed_graphical_inputs_and_complete_vector_command_semantics",
            "add_attitude_thrust_adapter_only_after_vector_semantics_are_explicit",
        )
    return (
        "inspect_and_parameterize_the_current_graphical_core",
        "choose_one_typed_adapter_only_after_output_semantics_are_bound",
    )


def existing_adapter_candidates(scheme_id: str) -> list[dict[str, str]]:
    candidates = {
        "official_pid": [
            {
                "model_file": "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDRotorAdapter.mo",
                "model_class": "MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter",
                "binding_status": "candidate_exists_but_is_not_yet_bound_to_the_current_graphical_core_in_the_formal_harness_map",
            }
        ],
        "cascade_pid": [
            {
                "model_file": "Models/MoSimQuadrotorModel/Control/Adapters/CascadePidAttitudeThrustAdapter.mo",
                "model_class": "MoSimQuadrotorModel.Control.Adapters.CascadePidAttitudeThrustAdapter",
                "binding_status": "candidate_uses_a_separate_cfunction_core_and_requires_behavior_equivalence_to_the_graphical_core",
            }
        ],
        "linear_mpc": [
            {
                "model_file": "Models/MoSimQuadrotorModel/Control/Adapters/LinearMPCRotorAdapter.mo",
                "model_class": "MoSimQuadrotorModel.Control.Adapters.LinearMPCRotorAdapter",
                "binding_status": "legacy_candidate_not_bound_to_the_current_graphical_core",
            }
        ],
    }
    return candidates.get(scheme_id, [])


def build_route(
    catalog_row: dict[str, Any],
    current_row: dict[str, Any],
    harness_row: dict[str, Any],
    boundaries: dict[str, Any],
) -> dict[str, Any]:
    scheme_id = str(current_row["scheme_id"])
    entry_type = str(current_row["entry_type"])
    model_file = str(current_row["current_model_file"])
    model_path = project_file(model_file, scheme_id)
    state = str(harness_row["formal_harness_state"])
    role = str(current_row["current_model_role"])

    if entry_type == "fixed_integrated_scheme":
        integration = {
            "current_boundary": "WHOLE_AIRCRAFT_EMBEDDED",
            "target_contract": None,
            "current_adapter_binding": harness_row.get("formal_adapter"),
            "adapter_candidates": [],
            "core_migration_state": "preserve_the_named_whole_aircraft_chain_until_dependency_audit",
            "adapter_migration_state": "not_applicable_embedded_sysblock_and_physical_plant",
            "next_migration_gate": "normalize_the_embedded_plant_reference_to_sunray150assembly_only_after_the_shared_assembly_baseline_passes",
        }
        graphical_surface = {
            "source_sha256": sha256_file(model_path),
            "input_mode": "whole_aircraft_public_alias",
            "inports": [],
            "outports": [],
            "constant_sources": [],
            "extends": [],
            "imports": [],
            "project_model_references": [],
        }
    else:
        graphical_surface = source_surface(model_path)
        boundary_name = candidate_boundary(scheme_id, graphical_surface["outports"])
        core_state, adapter_state = core_migration_state(
            scheme_id, graphical_surface, boundary_name
        )
        integration = {
            "current_boundary": "INTERNAL_GRAPHICAL_PROBE_ONLY",
            "target_contract": boundary_reference(boundary_name, boundaries),
            "current_adapter_binding": harness_row.get("formal_adapter"),
            "adapter_candidates": existing_adapter_candidates(scheme_id),
            "core_migration_state": core_state,
            "adapter_migration_state": adapter_state,
            "next_migration_gate": "create_a_formal_root_adapter_and_whole_aircraft_runner_binding_then_update_the_formal_harness_map",
        }

    topology = harness_row.get("topology_review_target")
    if not isinstance(topology, dict):
        raise MatrixError(f"{scheme_id}: topology review target is missing")
    canonical_harness = harness_row.get("canonical_closed_loop_harness")
    if state == "resolved_canonical_whole_aircraft_harness":
        current_scenario = {
            "state": "whole_aircraft_harness_exists_but_requires_fresh_check_model_and_simulation",
            "canonical_closed_loop_harness": canonical_harness,
        }
    elif state == "missing_closed_loop_harness":
        current_scenario = {
            "state": "internal_fixed_input_graphical_probe_only",
            "internal_probe": harness_row.get("internal_probe"),
        }
    else:
        current_scenario = {
            "state": "non_runnable_until_the_formal_harness_state_is_resolved",
            "reason": harness_row.get("reason"),
        }

    load_prerequisites = harness_row.get("model_load_prerequisites")
    if load_prerequisites is None:
        load_prerequisites = []
    if not isinstance(load_prerequisites, list):
        raise MatrixError(f"{scheme_id}: model_load_prerequisites must be a list")
    provenance = current_row.get("source_provenance")
    approved_variant = (
        provenance.get("approved_project_variant")
        if isinstance(provenance, dict)
        else None
    )
    if approved_variant is not None and not isinstance(approved_variant, dict):
        raise MatrixError(f"{scheme_id}: approved project variant record is invalid")

    return {
        "scheme_id": scheme_id,
        "display_name_zh": catalog_row.get("display_name_zh"),
        "category": catalog_row.get("category"),
        "entry_type": entry_type,
        "current_model": {
            "role": role,
            "file": model_file,
            "class": current_row.get("current_model_class"),
            "sha256": current_row.get("current_model_sha256"),
            "topology_sha256": current_row.get("current_model_topology_sha256"),
        },
        "source_alignment": {
            "compatibility_decision": current_row.get("compatibility_decision"),
            "approved_project_variant": approved_variant,
        },
        "current_graphical_surface": graphical_surface,
        "topology_review_target": topology,
        "formal_closure": {
            "state": state,
            "minimum_whole_aircraft_closure_eligible": harness_row.get(
                "minimum_whole_aircraft_closure_eligible"
            ),
            "canonical_closed_loop_harness": canonical_harness,
        },
        "integration": integration,
        "scenarios": {
            "current": current_scenario,
            "next_minimum_closure": {
                "state": "pending_shared_nominal_profile_after_adapter_binding",
                "intended_scenario_id": "nominal_hover",
            },
            "champion_ab_matrix": {
                "state": "pending_only_after_this_route_passes_minimum_closure_and_is_selected_as_its_family_champion",
                "scenario_ids": list(SEVEN_SCENARIO_AB_MATRIX),
            },
        },
        "dependencies": {
            "model_load_prerequisites": load_prerequisites,
            "shared_plant_current": "MoSimQuadrotorModel.Vehicle.Sunray150Assembly",
            "legacy_compatibility_alias": "MoSimQuadrotorModel.Vehicle.Sunray150Assembly",
        },
        "claim_boundary": "This row is a source/interface migration plan. It does not prove CheckModel, graphical review, minimum aircraft closure, scenario performance, code generation, Gazebo deployment, or report acceptance.",
    }


def validate(value: dict[str, Any]) -> None:
    if value.get("schema") != SCHEMA:
        raise MatrixError("matrix schema is invalid")
    routes = value.get("routes")
    if not isinstance(routes, list) or len(routes) != 46:
        raise MatrixError("matrix must contain exactly 46 current MWORKS routes")
    ids = [row.get("scheme_id") for row in routes]
    if len(ids) != len(set(ids)):
        raise MatrixError("matrix route ids must be unique")
    role_counts = Counter(row["current_model"]["role"] for row in routes)
    if role_counts != Counter(
        {
            "graphical_controller_core": 41,
            "fixed_integrated_whole_aircraft_closed_loop": 5,
        }
    ):
        raise MatrixError(f"unexpected current model role counts: {dict(role_counts)}")
    target_counts = Counter(
        row["integration"]["target_contract"]["boundary"]
        if isinstance(row["integration"]["target_contract"], dict)
        else row["integration"]["current_boundary"]
        for row in routes
    )
    expected_targets = Counter(
        {
            "ATTITUDE_THRUST": 37,
            "BODY_RATE_THRUST": 2,
            "WRENCH": 1,
            "ROTOR_COMMAND": 1,
            "WHOLE_AIRCRAFT_EMBEDDED": 5,
        }
    )
    if target_counts != expected_targets:
        raise MatrixError(f"unexpected target boundary counts: {dict(target_counts)}")
    for row in routes:
        topology = row["topology_review_target"]
        if not topology.get("model_file") or not topology.get("model_class"):
            raise MatrixError(f"{row['scheme_id']}: incomplete topology review target")
        contract = row["integration"]["target_contract"]
        if isinstance(contract, dict) and (
            not contract.get("interface") or not contract.get("runner")
        ):
            raise MatrixError(f"{row['scheme_id']}: incomplete target Runner contract")
        alignment = row.get("source_alignment")
        if not isinstance(alignment, dict) or not alignment.get("compatibility_decision"):
            raise MatrixError(f"{row['scheme_id']}: source alignment decision is missing")


def build_matrix() -> dict[str, Any]:
    catalog = read_json(CATALOG_PATH)
    current = read_json(CURRENT_MAP_PATH)
    harness = read_json(HARNESS_MAP_PATH)
    runner_contract = read_json(RUNNER_CONTRACT_PATH)
    if catalog.get("schema") != "mosim.control_scheme_catalog.v1":
        raise MatrixError("control scheme catalog schema is invalid")
    if current.get("schema") != "mosim.current_model_entry_map.v1":
        raise MatrixError("current model entry map schema is invalid")
    if harness.get("schema") != "mosim.formal_closed_loop_harness_map.v1":
        raise MatrixError("formal harness map schema is invalid")
    if runner_contract.get("schema") != "mosim.offline_runner_interface_contract.v1":
        raise MatrixError("offline Runner contract schema is invalid")
    catalog_rows = catalog.get("schemes")
    current_rows = current.get("schemes")
    harness_rows = harness.get("schemes")
    boundaries = runner_contract.get("boundaries")
    if not all(isinstance(item, list) for item in (catalog_rows, current_rows, harness_rows)):
        raise MatrixError("catalog, current map, and harness map must contain scheme lists")
    if not isinstance(boundaries, dict):
        raise MatrixError("offline Runner contract has no boundary map")

    catalog_by_id = {str(row.get("scheme_id")): row for row in catalog_rows if isinstance(row, dict)}
    harness_by_id = {str(row.get("scheme_id")): row for row in harness_rows if isinstance(row, dict)}
    resolved_rows = [
        row
        for row in current_rows
        if isinstance(row, dict) and row.get("mapping_state") == "resolved_current_model"
    ]
    if len(resolved_rows) != 46:
        raise MatrixError(f"expected 46 resolved current routes, found {len(resolved_rows)}")
    routes = []
    for current_row in sorted(resolved_rows, key=lambda row: str(row["scheme_id"])):
        scheme_id = str(current_row["scheme_id"])
        catalog_row = catalog_by_id.get(scheme_id)
        harness_row = harness_by_id.get(scheme_id)
        if not isinstance(catalog_row, dict) or not isinstance(harness_row, dict):
            raise MatrixError(f"{scheme_id}: catalog or harness entry is missing")
        routes.append(build_route(catalog_row, current_row, harness_row, boundaries))

    value = {
        "schema": SCHEMA,
        "version": 1,
        "authority": "The deterministic current-source interface and dependency matrix for the 46 MWORKS candidates. It is the migration worklist, not simulation acceptance evidence.",
        "scope": {
            "included": "46 current MWORKS candidates: 41 graphical controller cores and five fixed integrated whole-aircraft aliases.",
            "excluded": [
                "mu_synthesis: missing implementation blocker",
                "neural_smc: missing frozen neural training/inference artifact blocker",
                "px4ctrl: ROS1/PX4 runtime baseline rather than an MWORKS graphical route",
            ],
            "migration_order": [
                "interface_matrix",
                "plant_split_and_sunray150assembly",
                "official_pid_and_four_runner_baseline",
                "family_by_family_adapter_migration",
                "46_minimum_closures",
                "six_family_champions_and_seven_scenario_ab",
                "code_generation_and_gazebo_deployment",
            ],
        },
        "source_files": {
            "catalog": str(CATALOG_PATH.relative_to(ROOT)).replace("\\", "/"),
            "current_model_entry_map": str(CURRENT_MAP_PATH.relative_to(ROOT)).replace("\\", "/"),
            "formal_closed_loop_harness_map": str(HARNESS_MAP_PATH.relative_to(ROOT)).replace("\\", "/"),
            "offline_runner_interface_contract": str(RUNNER_CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "source_sha256": {
            "catalog": sha256_file(CATALOG_PATH),
            "current_model_entry_map": sha256_file(CURRENT_MAP_PATH),
            "formal_closed_loop_harness_map": sha256_file(HARNESS_MAP_PATH),
            "offline_runner_interface_contract": sha256_file(RUNNER_CONTRACT_PATH),
        },
        "shared_runner_contract": {
            "shared_controller_inputs": runner_contract.get("shared_controller_inputs"),
            "shared_plant": runner_contract.get("shared_plant"),
            "boundaries": runner_contract.get("boundaries"),
            "known_gaps": runner_contract.get("known_gaps"),
        },
        "summary": {
            "current_route_count": len(routes),
            "current_model_role_counts": dict(
                sorted(Counter(row["current_model"]["role"] for row in routes).items())
            ),
            "current_formal_closure_counts": dict(
                sorted(Counter(row["formal_closure"]["state"] for row in routes).items())
            ),
            "target_boundary_counts": dict(
                sorted(
                    Counter(
                        row["integration"]["target_contract"]["boundary"]
                        if isinstance(row["integration"]["target_contract"], dict)
                        else row["integration"]["current_boundary"]
                        for row in routes
                    ).items()
                )
            ),
            "graphical_input_mode_counts": dict(
                sorted(
                    Counter(
                        row["current_graphical_surface"]["input_mode"] for row in routes
                    ).items()
                )
            ),
            "approved_project_variant_route_count": sum(
                isinstance(row["source_alignment"]["approved_project_variant"], dict)
                for row in routes
            ),
        },
        "routes": routes,
    }
    validate(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the committed matrix differs from current source facts",
    )
    args = parser.parse_args()
    expected = canonical_json(build_matrix())
    if args.check:
        if not OUTPUT_PATH.is_file():
            print(f"missing generated matrix: {OUTPUT_PATH}", file=sys.stderr)
            return 1
        actual = OUTPUT_PATH.read_text(encoding="utf-8")
        if actual != expected:
            print("controller route interface matrix is stale; rerun the builder", file=sys.stderr)
            return 1
        print(f"PASS {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    OUTPUT_PATH.write_bytes(expected.encode("utf-8"))
    print(f"WROTE {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MatrixError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        raise SystemExit(2)
