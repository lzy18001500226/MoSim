#!/usr/bin/env python3
"""Build the deterministic strict-graphical migration registry for 48 profiles.

The profile catalog, current-model map, and formal-harness map remain the
authoritative sources for their respective domains. This file joins their
current entries with the strict Sysblock migration order and never changes
controller sources or runtime evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = ROOT / "Config" / "control_platform"
CATALOG_PATH = CONFIG_ROOT / "control_scheme_catalog.json"
ENTRY_MAP_PATH = CONFIG_ROOT / "current_model_entry_map.json"
HARNESS_MAP_PATH = CONFIG_ROOT / "formal_closed_loop_harness_map.json"
OUTPUT_PATH = CONFIG_ROOT / "strict_graphical_sysblock_registry.json"

ACTIVE_ENTRY_COUNT = 48
SCHEMA = "mosim.strict_graphical_sysblock_registry.v1"

GOLDEN_ROUTE = "official_pid"
AWFF_ROUTE = "awff_pid"
L1_RESIDUAL_ROUTE = "awff_l1_residual"
L1_INDI_ROUTE = "awff_l1_indi"
LINEAR_MPC_ROUTE = "linear_mpc_l1_indi"
QP_NMPC_ROUTE = "qp_nmpc_l1_indi_cbf"
PROJECT_OWNED_SEQUENCE = (
    "awff_pid",
    "awff_l1_residual",
    "awff_l1_indi",
    "linear_mpc_l1_indi",
    "qp_nmpc_l1_indi_cbf",
    "pid_awff_linear_eso",
    "px4ctrl",
)
OWNER_DIR_BY_CATEGORY = {
    "pid_family": "PID",
    "linear_robust_state_feedback": "LinearRobust",
    "nonlinear_adaptive": "NonlinearAdaptive",
    "sliding_mode": "SlidingMode",
    "optimization_predictive": "Optimization",
    "geometric_flatness": "GeometricFlatness",
    "learning": "Learning",
    "engineering_deployment_baseline": "ProjectOwned",
}
WAVE_BY_CATEGORY = {
    "pid_family": (2, "pid_and_intelligent_pid"),
    "linear_robust_state_feedback": (3, "linear_robust_state_feedback"),
    "sliding_mode": (4, "sliding_mode"),
    "nonlinear_adaptive": (5, "nonlinear_adaptive"),
    "geometric_flatness": (6, "geometric_flatness"),
    "optimization_predictive": (7, "optimization_predictive"),
    "learning": (8, "learning"),
}

GOLDEN_EVIDENCE = (
    "Results/mworks_live_gate/official_pid_strict_graphical_20260805/"
    "golden_pid_gate_status.json"
)
GOLDEN_NATIVE_BLOCKER_EVIDENCE = (
    "Results/mworks_live_gate/native_sysblock_modelica_embedding_20260805/"
    "native_sysblock_modelica_embedding_blocker.json"
)
AWFF_BLOCKER_EVIDENCE = (
    "Results/mworks_live_gate/awff_strict_graphical_20260805/"
    "awff_strict_graphical_blocker.json"
)
L1_REBUILD_EVIDENCE = (
    "Results/control_platform/strict_graphical_sysblock_registry_20260805/"
    "l1_strict_graphical_candidate_audit.json"
)
L1_INDI_REBUILD_EVIDENCE = (
    "Results/control_platform/strict_graphical_sysblock_registry_20260805/"
    "l1_indi_strict_graphical_candidate_audit.json"
)
LINEAR_MPC_REBUILD_EVIDENCE = (
    "Results/control_platform/strict_graphical_sysblock_registry_20260805/"
    "linear_mpc_strict_graphical_candidate_audit.json"
)
QP_NMPC_REBUILD_EVIDENCE = (
    "Results/control_platform/strict_graphical_sysblock_registry_20260805/"
    "qp_nmpc_strict_graphical_candidate_audit.json"
)


class RegistryError(ValueError):
    """Raised when a source map cannot produce a complete registry."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RegistryError(f"JSON object required: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def records_by_scheme(source: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    records = source.get("schemes")
    if not isinstance(records, list) or len(records) != ACTIVE_ENTRY_COUNT:
        raise RegistryError(f"{label} must contain {ACTIVE_ENTRY_COUNT} scheme records")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise RegistryError(f"{label} contains a non-object scheme")
        scheme_id = str(record.get("scheme_id") or "")
        if not scheme_id or scheme_id in result:
            raise RegistryError(f"{label} has a missing or duplicate scheme_id: {scheme_id}")
        result[scheme_id] = record
    return result


def require_file(relative_path: str) -> None:
    path = ROOT / relative_path
    if not path.is_file():
        raise RegistryError(f"required migration source is missing: {relative_path}")


def migration_wave(scheme_id: str, category: str) -> tuple[int, str, int]:
    if scheme_id == GOLDEN_ROUTE:
        return 0, "golden_pid_reference", 0
    if scheme_id in PROJECT_OWNED_SEQUENCE:
        return 1, "project_owned_fixed_chains", PROJECT_OWNED_SEQUENCE.index(scheme_id)
    try:
        ordinal, wave_id = WAVE_BY_CATEGORY[category]
    except KeyError as error:
        raise RegistryError(f"{scheme_id}: unsupported migration category {category}") from error
    return ordinal, wave_id, 0


def strict_status(scheme_id: str, entry: dict[str, Any]) -> tuple[str, str]:
    mapping_state = str(entry.get("mapping_state") or "")
    if scheme_id == GOLDEN_ROUTE:
        return (
            "blocked_native_sysblock_modelica_embedding",
            "The current Golden PID graph reuses a text-backed Modelica controller base. A native Sysblock compiles alone, but MWORKS cannot flatten its ports into the shared Modelica plant, so no strict whole-aircraft claim is allowed.",
        )
    if scheme_id == AWFF_ROUTE:
        return (
            "blocked_mworks_compiler_internal_error",
            "AWFF source surface passes, but core and adapter CheckModel remain blocked; no runtime claim is allowed.",
        )
    if scheme_id == L1_RESIDUAL_ROUTE:
        return (
            "strict_core_rebuild_required",
            "The existing L1 graphical candidate omits Formal filter, estimator, and anti-windup state relations, so it cannot be promoted as an equivalent strict core.",
        )
    if scheme_id == L1_INDI_ROUTE:
        return (
            "strict_core_rebuild_required",
            "The existing L1/INDI graphical candidate omits Formal L1 states and substitutes a delayed-command path for measured-rate and acceleration-estimator INDI relations.",
        )
    if scheme_id == LINEAR_MPC_ROUTE:
        return (
            "strict_core_rebuild_required",
            "The existing LinearMPC graphical candidate substitutes discrete delays and ordinary integrators for Formal filter, estimator, anti-windup, and measured-acceleration INDI state relations.",
        )
    if scheme_id == QP_NMPC_ROUTE:
        return (
            "strict_core_rebuild_required",
            "The existing QP/NMPC graphical candidate is a fixed-input design reference and omits the Formal nominal LinearMPC, exact QP projection, mode-event, and return-reference relations.",
        )
    if scheme_id == "px4ctrl":
        return (
            "explicit_exception_pending_mworks_equivalent_core",
            "The engineering/deployment baseline needs a C++ behavior/interface-equivalent MWORKS core before strict graphical review.",
        )
    if mapping_state == "planned_profile_no_model":
        return (
            "explicit_exception_planned_profile",
            "No project-owned Modelica core, adapter, or formal runner exists yet.",
        )
    if scheme_id in {"smc_boundary_layer", "nmpc_outer"}:
        return (
            "explicit_exception_fixed_input_probe",
            "The current graphical probe has no public reference and measurement controller boundary.",
        )
    if mapping_state == "resolved_current_model":
        return (
            "not_started_strict_graphical_migration",
            "A current graphical review target exists, but strict core, adapter, whole-aircraft entry, and SG evidence are not yet registered.",
        )
    raise RegistryError(f"{scheme_id}: unsupported mapping_state {mapping_state}")


def strict_targets(scheme_id: str, category: str) -> dict[str, Any]:
    owner_dir = OWNER_DIR_BY_CATEGORY.get(category)
    if not owner_dir:
        raise RegistryError(f"{scheme_id}: no graphical owner directory for {category}")
    if scheme_id == GOLDEN_ROUTE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID",
            "strict_core_class": "MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidNativeSysblockCore",
            "adapter_class": None,
            "whole_aircraft_runner_class": None,
            "formal_runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner",
            "legacy_modelica_graphical_candidate_class": "MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidCoreSysblock",
            "legacy_modelica_graphical_adapter_class": "MoSimQuadrotorModel.Control.Adapters.OfficialPIDGraphicalRotorAdapter",
            "legacy_modelica_graphical_runner_class": "MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner",
            "evidence": {
                "legacy_modelica_graphical": GOLDEN_EVIDENCE,
                "strict_native_blocker": GOLDEN_NATIVE_BLOCKER_EVIDENCE,
            },
        }
    if scheme_id == AWFF_ROUTE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned",
            "strict_core_class": "MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned.AWFFCoreSysblock",
            "adapter_class": "MoSimQuadrotorModel.Control.Adapters.AWFFGraphicalRotorAdapter",
            "whole_aircraft_runner_class": "MoSimQuadrotorModel.Experiment.Runners.Graphical.AwffSingleUavGraphicalRunner",
            "formal_runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.AwffFormalRunner",
            "evidence": AWFF_BLOCKER_EVIDENCE,
        }
    if scheme_id == L1_RESIDUAL_ROUTE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned",
            "strict_core_class": None,
            "adapter_class": None,
            "whole_aircraft_runner_class": None,
            "formal_runner_class": None,
            "evidence": L1_REBUILD_EVIDENCE,
        }
    if scheme_id == L1_INDI_ROUTE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned",
            "strict_core_class": None,
            "adapter_class": None,
            "whole_aircraft_runner_class": None,
            "formal_runner_class": None,
            "evidence": L1_INDI_REBUILD_EVIDENCE,
        }
    if scheme_id == LINEAR_MPC_ROUTE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned",
            "strict_core_class": None,
            "adapter_class": None,
            "whole_aircraft_runner_class": None,
            "formal_runner_class": None,
            "evidence": LINEAR_MPC_REBUILD_EVIDENCE,
        }
    if scheme_id == QP_NMPC_ROUTE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned",
            "strict_core_class": None,
            "adapter_class": None,
            "whole_aircraft_runner_class": None,
            "formal_runner_class": None,
            "evidence": QP_NMPC_REBUILD_EVIDENCE,
        }
    if scheme_id in PROJECT_OWNED_SEQUENCE:
        return {
            "owner_directory": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned",
            "strict_core_class": None,
            "adapter_class": None,
            "whole_aircraft_runner_class": None,
            "formal_runner_class": None,
            "evidence": None,
        }
    return {
        "owner_directory": f"Models/MoSimQuadrotorModel/Control/Implementations/Graphical/{owner_dir}",
        "strict_core_class": None,
        "adapter_class": None,
        "whole_aircraft_runner_class": None,
        "formal_runner_class": None,
        "evidence": None,
    }


def source_projection(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "mapping_state": entry.get("mapping_state"),
        "current_model_role": entry.get("current_model_role"),
        "current_model_file": entry.get("current_model_file"),
        "current_model_class": entry.get("current_model_class"),
        "current_model_sha256": entry.get("current_model_sha256"),
        "next_gate": entry.get("next_gate"),
    }


def harness_projection(harness: dict[str, Any]) -> dict[str, Any]:
    return {
        "formal_harness_state": harness.get("formal_harness_state"),
        "whole_aircraft_tier": harness.get("whole_aircraft_tier"),
        "tier2_closure_eligibility": harness.get("tier2_closure_eligibility"),
        "canonical_closed_loop_harness": harness.get("canonical_closed_loop_harness"),
        "formal_adapter": harness.get("formal_adapter"),
    }


def build_registry() -> dict[str, Any]:
    catalog = read_json(CATALOG_PATH)
    entry_map = read_json(ENTRY_MAP_PATH)
    harness_map = read_json(HARNESS_MAP_PATH)
    catalog_rows = records_by_scheme(catalog, "catalog")
    entry_rows = records_by_scheme(entry_map, "current model entry map")
    harness_rows = records_by_scheme(harness_map, "formal harness map")
    catalog_ids = set(catalog_rows)
    if set(entry_rows) != catalog_ids or set(harness_rows) != catalog_ids:
        raise RegistryError("catalog, current-model map, and formal-harness map scheme IDs must match")

    for relative_path in (
        "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidCoreSysblock.mo",
        "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidNativeSysblockCore.mo",
        "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDGraphicalRotorAdapter.mo",
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo",
        "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/OfficialPidFormalRunner.mo",
        "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned/AWFFCoreSysblock.mo",
        "Models/MoSimQuadrotorModel/Control/Adapters/AWFFGraphicalRotorAdapter.mo",
        "Models/MoSimQuadrotorModel/Experiment/Runners/Graphical/AwffSingleUavGraphicalRunner.mo",
        "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/AwffFormalRunner.mo",
    ):
        require_file(relative_path)

    records: list[dict[str, Any]] = []
    for catalog_record in catalog.get("schemes", []):
        scheme_id = str(catalog_record["scheme_id"])
        category = str(catalog_record["category"])
        wave_ordinal, wave_id, within_wave = migration_wave(scheme_id, category)
        status, claim_boundary = strict_status(scheme_id, entry_rows[scheme_id])
        records.append(
            {
                "scheme_id": scheme_id,
                "display_name_zh": catalog_record.get("display_name_zh"),
                "category": category,
                "entry_type": catalog_record.get("entry_type"),
                "migration_wave": {
                    "ordinal": wave_ordinal,
                    "id": wave_id,
                    "within_wave": within_wave,
                },
                "strict_graphical_status": status,
                "claim_boundary": claim_boundary,
                "strict_targets": strict_targets(scheme_id, category),
                "current_source": source_projection(entry_rows[scheme_id]),
                "formal_reference": harness_projection(harness_rows[scheme_id]),
            }
        )

    records.sort(key=lambda row: (row["migration_wave"]["ordinal"], row["migration_wave"]["within_wave"], row["scheme_id"]))
    status_counts = Counter(str(row["strict_graphical_status"]) for row in records)
    wave_counts = Counter(str(row["migration_wave"]["id"]) for row in records)
    if len(records) != ACTIVE_ENTRY_COUNT or len({row["scheme_id"] for row in records}) != ACTIVE_ENTRY_COUNT:
        raise RegistryError("registry must contain each active scheme exactly once")
    if status_counts["blocked_native_sysblock_modelica_embedding"] != 1:
        raise RegistryError("the Golden PID native-Sysblock embedding blocker must remain explicit")
    if status_counts["blocked_mworks_compiler_internal_error"] != 1:
        raise RegistryError("the AWFF compiler blocker must remain explicit")

    return {
        "schema": SCHEMA,
        "version": 1,
        "authority": "Derived strict-graphical migration registry. It does not replace the catalog, current-model map, formal-harness map, or MWORKS runtime evidence.",
        "sources": {
            "catalog": {"path": str(CATALOG_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(CATALOG_PATH)},
            "current_model_entry_map": {"path": str(ENTRY_MAP_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(ENTRY_MAP_PATH)},
            "formal_closed_loop_harness_map": {"path": str(HARNESS_MAP_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(HARNESS_MAP_PATH)},
        },
        "migration_policy": {
            "golden_reference": GOLDEN_ROUTE,
            "project_owned_sequence": list(PROJECT_OWNED_SEQUENCE),
            "wave_order": [
                "golden_pid_reference",
                "project_owned_fixed_chains",
                "pid_and_intelligent_pid",
                "linear_robust_state_feedback",
                "sliding_mode",
                "nonlinear_adaptive",
                "geometric_flatness",
                "optimization_predictive",
                "learning",
            ],
            "strict_completion_rule": "A route becomes complete only after a strict core or explicit exception, a nonblank whole-aircraft graphical entry, SG-0 through SG-4 records, and current model/parameter/scenario evidence are present.",
        },
        "summary": {
            "active_entry_count": len(records),
            "strict_graphical_status_counts": dict(sorted(status_counts.items())),
            "migration_wave_counts": dict(sorted(wave_counts.items())),
        },
        "schemes": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--check", action="store_true", help="Validate the checked-in registry against current source maps.")
    args = parser.parse_args()
    try:
        registry = build_registry()
        output = args.output if args.output.is_absolute() else Path.cwd() / args.output
        if args.check:
            if not output.is_file():
                raise RegistryError(f"registry is missing: {output}")
            existing = read_json(output)
            if existing != registry:
                raise RegistryError(f"registry is stale or diverged: {output}")
        else:
            write_json(output, registry)
        report = {"ok": True, "check": args.check, "output": str(output), "summary": registry["summary"]}
    except Exception as error:
        report = {"ok": False, "check": args.check, "error": str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
