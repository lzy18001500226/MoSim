#!/usr/bin/env python3
"""Shared static plan for G4 current-model entry mapping.

This module deliberately distinguishes a historical graphical controller-core
copy from a current whole-aircraft simulation.  It never opens MWORKS or
changes a historical source file.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from apply_g5_smart_layout import normalized_visual_metadata


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
INVENTORY_PATH = (
    ROOT
    / "Results"
    / "control_platform"
    / "g1_control_scheme_execution_inventory_20260722"
    / "CONTROL_SCHEME_EXECUTION_INVENTORY.json"
)
CURRENT_MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
APPROVED_GRAPHICAL_IMPORT_VARIANTS_PATH = (
    ROOT / "Config" / "control_platform" / "approved_graphical_import_variants.json"
)
APPROVED_GRAPHICAL_IMPORT_VARIANTS_SCHEMA = "mosim.approved_graphical_import_variants.v1"
CONTROL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Control"
GRAPHICAL_ROOT = CONTROL_ROOT / "Implementations"
GRAPHICAL_PACKAGE = "MoSimQuadrotorModel.Control.Implementations"
CONTROL_ORDER_PATH = CONTROL_ROOT / "package.order"
SINGLE_UAV_ORDER_PATH = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "SingleUav" / "package.order"
)
INTEGRATED_CHAINS_ROOT = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "SingleUav" / "IntegratedChains"
)
INTEGRATED_CHAINS_PACKAGE = "MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains"
MWORKS_MODEL_VERSION = "26.3.0"

FAMILY_PACKAGES = {
    "pid_family": "PidFamily",
    "linear_robust_state_feedback": "ClassicRobust",
    "nonlinear_adaptive": "ClassicRobust",
    "sliding_mode": "SlidingMode",
    "optimization_predictive": "Optimization",
    "geometric_flatness": "GeometricFlatness",
    "learning": "Learning",
}
FAMILY_ORDER = [
    "PidFamily",
    "ClassicRobust",
    "SlidingMode",
    "Optimization",
    "GeometricFlatness",
    "Learning",
]
# The seven semantic families currently occupy six physical implementation
# packages: linear/robust and nonlinear/adaptive cores share the existing
# ClassicRobust storage package until a separately approved source move.
# Sysblocks and Graphical remain project-owned sibling packages, not semantic
# families. Graphical owns strict whole-aircraft review cores and must stay
# discoverable without being folded into a historical controller-import family.
IMPLEMENTATIONS_PACKAGE_ORDER = [
    "PidFamily",
    "Graphical",
    *FAMILY_ORDER[1:],
    "Sysblocks",
]

SPECIAL_PRIMARY_SOURCES = {
    "official_pid": ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Control"
    / "PID"
    / "OfficialPidGraphicalCore.mo",
    # These historical Wave-A entries were CFunction wrappers.  Their direct
    # graphical counterparts are generated through the official Sysplorer API
    # and become the current G5 review targets; the wrappers remain intact as
    # compatibility and formula-provenance artifacts.
    "lqr_baseline": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "lqr_baseline"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo",
    "lqi_baseline": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "lqi_baseline"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_LQI_DIRECT_GRAPHICAL_MIL.mo",
    "backstepping_baseline": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "backstepping_baseline"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_BACKSTEPPING_DIRECT_GRAPHICAL_MIL.mo",
    # The next classic batch follows the same direct graphical route. Each
    # source is built through the official Sysplorer API from its documented
    # current law, while the historical CFunction wrappers remain provenance.
    "pole_placement_luenberger": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "pole_placement_luenberger"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_POLE_PLACEMENT_LUENBERGER_DIRECT_GRAPHICAL_MIL.mo",
    "mrac": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "mrac"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL.mo",
    "ndi": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "ndi"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL.mo",
    "fopid": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "fopid"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL.mo",
    "h2_state_feedback": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "h2_state_feedback"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_H2_STATE_FEEDBACK_DIRECT_GRAPHICAL_MIL.mo",
    "hinf_hover_wrench": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "hinf_hover_wrench"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL.mo",
    "terminal_smc": ROOT
    / "Results"
    / "control_platform"
    / "p3_sliding_mode_mworks_20260716"
    / "models"
    / "graphical_variants"
    / "MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo",
    # The four P10 DFBC entries previously resolved to CFunction wrappers.  The
    # direct graphical sources below are generated through the official
    # Sysplorer API and expose the distinct high-order / smooth-robust and
    # attitude / body-rate paths for G5 topology review.  Their CFunction
    # wrappers remain compatibility and formula-provenance artifacts.
    "dfbc_high_order_attitude": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "dfbc_high_order_attitude"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo",
    "dfbc_high_order_bodyrate": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "dfbc_high_order_bodyrate"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_DFBC_HIGH_ORDER_BODYRATE_DIRECT_GRAPHICAL_MIL.mo",
    "dfbc_smooth_robust_attitude": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "dfbc_smooth_robust_attitude"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo",
    "dfbc_smooth_robust_bodyrate": ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "runs"
    / "dfbc_smooth_robust_bodyrate"
    / "raw"
    / "frozen_bound_sources"
    / "01_MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL.mo",
}

DIRECT_GRAPHICAL_PRIMARY = frozenset(
    {
        "lqr_baseline",
        "lqi_baseline",
        "backstepping_baseline",
        "pole_placement_luenberger",
        "mrac",
        "ndi",
        "fopid",
        "h2_state_feedback",
        "hinf_hover_wrench",
        "dfbc_high_order_attitude",
        "dfbc_high_order_bodyrate",
        "dfbc_smooth_robust_attitude",
        "dfbc_smooth_robust_bodyrate",
    }
)

# These current package members remain executable compatibility/provenance
# artifacts while their G5 review targets move to direct graphical cores. They
# must stay in package.order until the separate R1 dependency audit authorizes
# retirement; omitting them from generated metadata would make the importer
# falsely treat a safe additive update as an unknown destructive overwrite.
LEGACY_COMPATIBILITY_MODELS_BY_FAMILY = {
    "ClassicRobust": (
        "MoSim_Classic_FOPID_MIL",
        "MoSim_Classic_H2_STATE_FEEDBACK_MIL",
        "MoSim_Classic_MRAC_MIL",
        "MoSim_Classic_NDI_MIL",
        "MoSim_Classic_POLE_PLACEMENT_LUENBERGER_MIL",
        "MoSim_P10_HINF_HOVER_WRENCH_MIL",
    ),
}

# Sysplorer keeps these Wave-A wrapper artifacts discoverable after the direct
# graphical replacements are imported.  They are intentionally listed after
# primary entries because that is their existing native package order.  They
# are not current G5 targets and must not be deleted before R1.
TRAILING_LEGACY_COMPATIBILITY_MODELS_BY_FAMILY = {
    "ClassicRobust": (
        "MoSim_WaveA_BACKSTEPPING_MIL",
        "MoSim_WaveA_LQI_MIL",
        "MoSim_WaveA_LQR_MIL",
    ),
    # These original P10 DFBC CFunction wrappers remain valid provenance and
    # compatibility entries.  The four direct graphical cores are the current
    # G5 review targets, so retain the wrappers after the independently
    # loadable graphical entries instead of dropping them from package.order.
    "GeometricFlatness": (
        "MoSim_P10_DFBC_HIGH_ORDER_ATTITUDE_MIL",
        "MoSim_P10_DFBC_HIGH_ORDER_BODYRATE_MIL",
        "MoSim_P10_DFBC_SMOOTH_ROBUST_ATTITUDE_MIL",
        "MoSim_P10_DFBC_SMOOTH_ROBUST_BODYRATE_MIL",
    ),
}

GRAPHICAL_SUPPORT_SOURCES = (
    {
        "support_id": "wave_a_cfunction_sysblock",
        "family_package": "ClassicRobust",
        "source_file": ROOT
        / "Results"
        / "control_platform"
        / "g5_mworks_closeout_20260716"
        / "wave_a"
        / "models"
        / "MoSim_WaveA_CFunction_Sysblock.mo",
        "purpose": "Shared CFunction bridge required by the WaveA LQR, LQI, and backstepping graphical wrappers.",
        "required_by_scheme_ids": (
            "lqr_baseline",
            "lqi_baseline",
            "backstepping_baseline",
        ),
    },
    {
        "support_id": "classic_cfunction_sysblock",
        "family_package": "ClassicRobust",
        "source_file": ROOT
        / "Results"
        / "control_platform"
        / "classic_controller_closeout_20260717"
        / "mworks"
        / "models"
        / "MoSim_Classic_CFunction_Sysblock.mo",
        "purpose": "Shared CFunction bridge required by the classic FOPID, H2, MRAC, NDI, and pole-placement graphical wrappers.",
        "required_by_scheme_ids": (
            "fopid",
            "h2_state_feedback",
            "mrac",
            "ndi",
            "pole_placement_luenberger",
        ),
    },
    {
        "support_id": "hinf_wrench_adapter_cfunction_sysblock",
        "family_package": "ClassicRobust",
        "source_file": ROOT
        / "Results"
        / "control_platform"
        / "behavior_equivalence_20260814"
        / "legacy_head_snapshot"
        / "tree"
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Implementations"
        / "ClassicRobust"
        / "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock.mo",
        "purpose": "Shared CFunction bridge required by the P10 H-infinity hover-wrench graphical wrapper.",
        "required_by_scheme_ids": (
            "hinf_hover_wrench",
        ),
    },
    {
        "support_id": "dfbc_family_cfunction_sysblock",
        "family_package": "GeometricFlatness",
        "source_file": ROOT
        / "Results"
        / "control_platform"
        / "behavior_equivalence_20260814"
        / "legacy_head_snapshot"
        / "tree"
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Implementations"
        / "GeometricFlatness"
        / "MoSim_P10_DFBC_Family_CFunction_Sysblock.mo",
        "purpose": "Shared executable DFBC bridge required by the four P10 high-order and smooth-robust DFBC wrappers. It restores model-check dependency resolution only; G5 still requires a separately readable internal control-law topology.",
        "required_by_scheme_ids": (
            "dfbc_high_order_attitude",
            "dfbc_high_order_bodyrate",
            "dfbc_smooth_robust_attitude",
            "dfbc_smooth_robust_bodyrate",
        ),
    },
    {
        "support_id": "qp_nmpc_safety_graphical_review_core",
        "family_package": "Optimization",
        "source_file": ROOT
        / "Results"
        / "control_platform"
        / "behavior_equivalence_20260814"
        / "legacy_head_snapshot"
        / "tree"
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Implementations"
        / "Optimization"
        / "MoSim_G5_QPNMPC_SAFETY_DIRECT_GRAPHICAL_MIL.mo",
        "purpose": "Readable native graphical QP/NMPC safety control-law core for the fixed QP/NMPC/L1/INDI/CBF chain. It replaces no whole-aircraft alias and is used only for G5 internal-topology review.",
        "required_by_scheme_ids": (
            "qp_nmpc_l1_indi_cbf",
        ),
    },
)
FULL_PROFILE_RUNNER_SPECS = {
    "awff_pid": {
        "runner_model": "AwffPidGraphicalRunner",
        "runner_file": INTEGRATED_CHAINS_ROOT / "AwffPidGraphicalRunner.mo",
        "runner_class": f"{INTEGRATED_CHAINS_PACKAGE}.AwffPidGraphicalRunner",
        "source_file": INTEGRATED_CHAINS_ROOT / "AwffPidGraphicalRunner.mo",
        "source_model_class": f"{INTEGRATED_CHAINS_PACKAGE}.AwffPidGraphicalRunner",
        "historical_source_file": ROOT / "Results" / "model_library_refactor" / "controller_route_execution_current" / "runs" / "fixed_awff_pid" / "raw" / "frozen_bound_sources" / "01_Example1AWFFSysblockClosedLoop.mo",
        "historical_source_model_class": "MoSimQuadrotorModel.Experiment.Templates.Official.Example1AWFFSysblockClosedLoop",
    },
    "awff_l1_residual": {
        "runner_model": "AwffL1ResidualGraphicalRunner",
        "runner_file": INTEGRATED_CHAINS_ROOT / "AwffL1ResidualGraphicalRunner.mo",
        "runner_class": f"{INTEGRATED_CHAINS_PACKAGE}.AwffL1ResidualGraphicalRunner",
        "source_file": INTEGRATED_CHAINS_ROOT / "AwffL1ResidualGraphicalRunner.mo",
        "source_model_class": f"{INTEGRATED_CHAINS_PACKAGE}.AwffL1ResidualGraphicalRunner",
        "historical_source_file": ROOT / "Results" / "model_library_refactor" / "controller_route_execution_current" / "runs" / "fixed_awff_l1_residual" / "raw" / "frozen_bound_sources" / "01_Example1L1SysblockClosedLoop.mo",
        "historical_source_model_class": "MoSimQuadrotorModel.Experiment.Templates.Official.Example1L1SysblockClosedLoop",
    },
    "awff_l1_indi": {
        "runner_model": "AwffL1IndiGraphicalRunner",
        "runner_file": INTEGRATED_CHAINS_ROOT / "AwffL1IndiGraphicalRunner.mo",
        "runner_class": f"{INTEGRATED_CHAINS_PACKAGE}.AwffL1IndiGraphicalRunner",
        "source_file": INTEGRATED_CHAINS_ROOT / "AwffL1IndiGraphicalRunner.mo",
        "source_model_class": f"{INTEGRATED_CHAINS_PACKAGE}.AwffL1IndiGraphicalRunner",
        "historical_source_file": ROOT / "Results" / "model_library_refactor" / "controller_route_execution_current" / "runs" / "fixed_awff_l1_indi" / "raw" / "frozen_bound_sources" / "01_Example1INDISysblockClosedLoop.mo",
        "historical_source_model_class": "MoSimQuadrotorModel.Experiment.Templates.Official.Example1INDISysblockClosedLoop",
    },
    "linear_mpc_l1_indi": {
        "runner_model": "LinearMpcL1IndiGraphicalRunner",
        "runner_file": INTEGRATED_CHAINS_ROOT / "LinearMpcL1IndiGraphicalRunner.mo",
        "runner_class": f"{INTEGRATED_CHAINS_PACKAGE}.LinearMpcL1IndiGraphicalRunner",
        "source_file": INTEGRATED_CHAINS_ROOT / "LinearMpcL1IndiGraphicalRunner.mo",
        "source_model_class": f"{INTEGRATED_CHAINS_PACKAGE}.LinearMpcL1IndiGraphicalRunner",
        "historical_source_file": ROOT / "Results" / "model_library_refactor" / "controller_route_execution_current" / "runs" / "fixed_linear_mpc_l1_indi" / "raw" / "frozen_bound_sources" / "01_Example1LinearMPCSysblockClosedLoop.mo",
        "historical_source_model_class": "MoSimQuadrotorModel.Experiment.Templates.Official.Example1LinearMPCSysblockClosedLoop",
    },
    "qp_nmpc_l1_indi_cbf": {
        "runner_model": "QpNmpcL1IndiCbfGraphicalRunner",
        "runner_file": INTEGRATED_CHAINS_ROOT / "QpNmpcL1IndiCbfGraphicalRunner.mo",
        "runner_class": f"{INTEGRATED_CHAINS_PACKAGE}.QpNmpcL1IndiCbfGraphicalRunner",
        "source_file": INTEGRATED_CHAINS_ROOT / "QpNmpcL1IndiCbfGraphicalRunner.mo",
        "source_model_class": f"{INTEGRATED_CHAINS_PACKAGE}.QpNmpcL1IndiCbfGraphicalRunner",
        "historical_source_file": ROOT / "Results" / "model_library_refactor" / "controller_route_execution_current" / "runs" / "fixed_qp_nmpc_l1_indi_cbf" / "raw" / "frozen_bound_sources" / "01_Example1QPNMPCSafetySysblockClosedLoop.mo",
        "historical_source_model_class": "MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1QPNMPCSafetySysblockClosedLoop",
    },
}



class MappingError(ValueError):
    """Raised when a deterministic G4 mapping input is incomplete or unsafe."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MappingError(f"JSON object required: {path}")
    return value


def write_utf8_lf(path: Path, text: str) -> None:
    """Write generated text as UTF-8 with repository-stable LF newlines."""

    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    write_utf8_lf(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_topology_sha256(path: Path) -> str:
    """Hash a model while excluding diagram-only coordinates and wire geometry.

    Sysplorer may rewrite ``Placement`` and ``Line`` annotations as a model is
    opened.  Those bytes are useful capture provenance, but they are not a
    controller-topology change.  The raw file hash is retained alongside this
    fingerprint; declarations, parameters, equations, ports, and connects
    still change the topology fingerprint.
    """

    text = topology_fingerprint_text(path.read_text(encoding="utf-8"))
    normalized = normalized_visual_metadata(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_import_delta(expected: str, current: str) -> str:
    """Hash the exact source-to-project import delta without accepting it.

    Project-side variants are an exceptional, hash-bound decision.  The delta
    fingerprint includes both sides of every changed line, so a later source,
    controller, or metadata edit cannot inherit an earlier decision.
    """

    lines = list(
        difflib.unified_diff(
            expected.splitlines(),
            current.splitlines(),
            fromfile="historical_expected_import",
            tofile="current_project_model",
            n=0,
            lineterm="",
        )
    )
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def import_item_identity(item: dict[str, Any]) -> tuple[str, str]:
    """Return the only accepted identity for a planned graphical import."""

    scheme_id = item.get("scheme_id")
    support_id = item.get("support_id")
    if isinstance(scheme_id, str) and scheme_id and not support_id:
        return ("graphical_controller_core", scheme_id)
    if isinstance(support_id, str) and support_id and not scheme_id:
        return ("graphical_support", support_id)
    raise MappingError("Graphical import item must have exactly one scheme_id or support_id")


def read_approved_graphical_import_variants() -> dict[tuple[str, str], dict[str, Any]]:
    """Load the small, exact allowlist for intentional project-side variants."""

    value = read_json(APPROVED_GRAPHICAL_IMPORT_VARIANTS_PATH)
    if value.get("schema") != APPROVED_GRAPHICAL_IMPORT_VARIANTS_SCHEMA:
        raise MappingError("Approved graphical import variants schema is invalid")
    rows = value.get("variants")
    declared_count = value.get("variant_count")
    if not isinstance(rows, list) or not isinstance(declared_count, int) or declared_count != len(rows):
        raise MappingError("Approved graphical import variants have an invalid count")
    variants: dict[tuple[str, str], dict[str, Any]] = {}
    hash_pattern = re.compile(r"^[0-9a-f]{64}$")
    required_revalidation = {
        "requires_fresh_model_check",
        "requires_fresh_simulation",
        "requires_adapter_boundary_review",
        "requires_fresh_codegen_review",
    }
    for row in rows:
        if not isinstance(row, dict):
            raise MappingError("Approved graphical import variants contains a non-object row")
        kind = row.get("import_item_kind")
        if kind == "graphical_controller_core":
            identifier = row.get("scheme_id")
        elif kind == "graphical_support":
            identifier = row.get("support_id")
        else:
            raise MappingError("Approved graphical import variant has an invalid import_item_kind")
        if not isinstance(identifier, str) or not identifier:
            raise MappingError("Approved graphical import variant is missing its item identifier")
        if (kind, identifier) in variants:
            raise MappingError(f"Duplicate approved graphical import variant: {kind}/{identifier}")
        for key in ("source_sha256", "current_model_sha256", "expected_import_delta_sha256"):
            value_hash = row.get(key)
            if not isinstance(value_hash, str) or not hash_pattern.fullmatch(value_hash):
                raise MappingError(f"{kind}/{identifier}: {key} must be a lower-case SHA-256")
        if not isinstance(row.get("change_summary"), str) or not row["change_summary"].strip():
            raise MappingError(f"{kind}/{identifier}: change_summary is required")
        revalidation = row.get("required_revalidation")
        if not isinstance(revalidation, dict) or set(revalidation) != required_revalidation:
            raise MappingError(f"{kind}/{identifier}: required_revalidation is incomplete")
        if any(not isinstance(revalidation[key], bool) for key in required_revalidation):
            raise MappingError(f"{kind}/{identifier}: required_revalidation values must be booleans")
        variants[(kind, identifier)] = row
    return variants


def approved_graphical_import_variant(
    item: dict[str, Any],
    target: Path,
    expected: str,
    *,
    variants: dict[tuple[str, str], dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Return a decision only when every source/current/delta binding matches."""

    variants = read_approved_graphical_import_variants() if variants is None else variants
    identity = import_item_identity(item)
    variant = variants.get(identity)
    if variant is None:
        return None
    source = item.get("source_file")
    if not isinstance(source, Path) or not source.is_file() or not target.is_file():
        return None
    current = target.read_text(encoding="utf-8")
    if sha256_file(source) != variant["source_sha256"]:
        return None
    if sha256_file(target) != variant["current_model_sha256"]:
        return None
    if sha256_import_delta(expected, current) != variant["expected_import_delta_sha256"]:
        return None
    return variant


def approved_variant_record(variant: dict[str, Any]) -> dict[str, Any]:
    """Expose the decision binding in generated maps without copying policy prose."""

    record = {
        "decision_file": repo_path(APPROVED_GRAPHICAL_IMPORT_VARIANTS_PATH),
        "import_item_kind": variant["import_item_kind"],
        "source_sha256": variant["source_sha256"],
        "current_model_sha256": variant["current_model_sha256"],
        "expected_import_delta_sha256": variant["expected_import_delta_sha256"],
        "change_summary": variant["change_summary"],
        "required_revalidation": variant["required_revalidation"],
    }
    if variant["import_item_kind"] == "graphical_controller_core":
        record["scheme_id"] = variant["scheme_id"]
    else:
        record["support_id"] = variant["support_id"]
    return record


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise MappingError(f"Path escapes project root: {path}") from exc


def as_strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def model_declaration(text: str) -> tuple[str | None, str]:
    match = re.match(
        r"\s*(?:within\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*;\s*)?"
        r"(?:model|block)\s+([A-Za-z_]\w*)\b",
        text,
    )
    if not match:
        raise MappingError("Expected a top-level Modelica model or block declaration")
    return match.group(1), match.group(2)


def without_top_level_within(text: str) -> str:
    clean = text.lstrip("\ufeff")
    return re.sub(r"\A\s*within\s+[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*;\s*", "", clean, count=1)


def canonical_graphical_import_text(text: str) -> str:
    """Return generated graphical-import text with stable line formatting.

    Source artifacts can contain CRLF and trailing spaces emitted by the GUI.
    Those bytes are not part of the Modelica model and would otherwise make a
    generated import fail the repository whitespace gate. This function is
    deliberately limited to newline and line-end whitespace normalization; it
    never changes indentation, declarations, equations, annotations,
    parameters, ports, or layout metadata.
    """

    clean = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip(" \t") for line in clean.split("\n")).rstrip() + "\n"


def canonical_package_file_text(text: str) -> str:
    """Compare generated package metadata without treating GUI newline normalization as drift."""

    return canonical_graphical_import_text(text)


def topology_fingerprint_text(text: str) -> str:
    """Normalize only non-semantic whitespace for topology fingerprints.

    This intentionally differs from ``canonical_graphical_import_text``:
    imported model files keep their native visual source layout, while the
    topology fingerprint ignores indentation, line-end whitespace, and blank
    lines that Sysplorer may rewrite without changing components or wires.
    """

    clean = canonical_graphical_import_text(text)
    lines = [line.strip(" \t") for line in clean.split("\n")]
    return "\n".join(line for line in lines if line).rstrip() + "\n"


def source_runtime_reference_kind(text: str) -> str:
    if "Results" not in text and "results" not in text:
        return "none"
    if "Sim_seting" in text or "CodeGeneration" in text:
        return "code_generation_output_setting_only"
    return "unclassified_results_reference"


def source_candidates(row: dict[str, Any]) -> list[Path]:
    model_entry = row.get("model_entry")
    if not isinstance(model_entry, dict):
        return []
    return [ROOT / item for item in as_strings(model_entry.get("source_model_candidates"))]


def select_primary_source(scheme_id: str, inventory_row: dict[str, Any]) -> Path:
    special = SPECIAL_PRIMARY_SOURCES.get(scheme_id)
    if special is not None:
        if not special.is_file():
            raise MappingError(f"Selected source is missing for {scheme_id}: {special}")
        return special

    candidates = source_candidates(inventory_row)
    graphical = [candidate for candidate in candidates if "graphical_variants" in candidate.as_posix()]
    selected = graphical[0] if graphical else (candidates[0] if candidates else None)
    if selected is None or not selected.is_file():
        raise MappingError(f"No readable source model candidate for {scheme_id}")
    return selected


def import_plan(catalog: dict[str, Any], inventory: dict[str, Any]) -> list[dict[str, Any]]:
    inventory_rows = inventory.get("schemes")
    if not isinstance(inventory_rows, list):
        raise MappingError("G1 inventory must expose schemes")
    by_id = {
        str(row.get("scheme_id")): row
        for row in inventory_rows
        if isinstance(row, dict) and row.get("scheme_id")
    }
    plan: list[dict[str, Any]] = []
    for scheme in catalog.get("schemes", []):
        if (
            not isinstance(scheme, dict)
            or scheme.get("entry_type") != "mworks_control_profile"
            or scheme.get("execution_kind") != "graphical_control_core"
        ):
            continue
        scheme_id = str(scheme.get("scheme_id"))
        row = by_id.get(scheme_id)
        if row is None:
            raise MappingError(f"G1 inventory misses graphical profile: {scheme_id}")
        category = str(scheme.get("category"))
        family = str(scheme.get("implementation_package") or FAMILY_PACKAGES.get(category) or "")
        if not family:
            raise MappingError(f"Unsupported current graphical family for {scheme_id}: {category}")
        if family not in FAMILY_ORDER:
            raise MappingError(f"Unsupported current graphical package for {scheme_id}: {family}")
        source = select_primary_source(scheme_id, row)
        source_text = source.read_text(encoding="utf-8")
        _, source_model = model_declaration(source_text)
        target = GRAPHICAL_ROOT / family / f"{source_model}.mo"
        plan.append(
            {
                "scheme_id": scheme_id,
                "category": category,
                "family_package": family,
                "source_file": source,
                "source_model": source_model,
                "source_sha256": sha256_file(source),
                "source_results_reference_kind": source_runtime_reference_kind(source_text),
                "target_file": target,
                "target_package": f"{GRAPHICAL_PACKAGE}.{family}",
                "target_model_class": f"{GRAPHICAL_PACKAGE}.{family}.{source_model}",
            }
        )

    scheme_ids = [item["scheme_id"] for item in plan]
    target_paths = [item["target_file"] for item in plan]
    if len(scheme_ids) != len(set(scheme_ids)) or len(target_paths) != len(set(target_paths)):
        raise MappingError("Graphical import plan has duplicate scheme IDs or target files")
    return plan


def support_import_plan() -> list[dict[str, Any]]:
    """Return project-owned support imports required by current graphical cores.

    Support imports are package dependencies, not additional Control Profiles.
    They must therefore be hash-checked and copied with the same safeguards as a
    top-level controller core without changing the active 48-entry count.
    """

    plan: list[dict[str, Any]] = []
    for spec in GRAPHICAL_SUPPORT_SOURCES:
        support_id = str(spec["support_id"])
        family = str(spec["family_package"])
        source = spec["source_file"]
        if family not in FAMILY_ORDER:
            raise MappingError(f"Unsupported graphical support family for {support_id}: {family}")
        if not isinstance(source, Path) or not source.is_file():
            raise MappingError(f"Required graphical support source is missing: {source}")
        source_text = source.read_text(encoding="utf-8")
        _, source_model = model_declaration(source_text)
        target = GRAPHICAL_ROOT / family / f"{source_model}.mo"
        plan.append(
            {
                "support_id": support_id,
                "family_package": family,
                "source_file": source,
                "source_model": source_model,
                "source_sha256": sha256_file(source),
                "source_results_reference_kind": source_runtime_reference_kind(source_text),
                "target_file": target,
                "target_package": f"{GRAPHICAL_PACKAGE}.{family}",
                "target_model_class": f"{GRAPHICAL_PACKAGE}.{family}.{source_model}",
                "purpose": str(spec["purpose"]),
                "required_by_scheme_ids": list(spec["required_by_scheme_ids"]),
            }
        )

    support_ids = [item["support_id"] for item in plan]
    target_paths = [item["target_file"] for item in plan]
    if len(support_ids) != len(set(support_ids)) or len(target_paths) != len(set(target_paths)):
        raise MappingError("Graphical support import plan has duplicate IDs or target files")
    return plan
def full_profile_runner_plan() -> list[dict[str, Any]]:
    """Plan the five current whole-aircraft runners using their public names."""

    plan: list[dict[str, Any]] = []
    for scheme_id, spec in FULL_PROFILE_RUNNER_SPECS.items():
        source = spec["source_file"]
        target = spec["runner_file"]
        source_class = str(spec["source_model_class"])
        target_class = str(spec["runner_class"])
        if not isinstance(source, Path) or not source.is_file():
            raise MappingError(f"Full-profile provenance source is missing: {source}")
        if not isinstance(target, Path) or not target.is_file():
            raise MappingError(f"Current full-profile runner is missing: {target}")
        declared_within, declared_name = model_declaration(target.read_text(encoding="utf-8"))
        declared_class = f"{declared_within}.{declared_name}" if declared_within else declared_name
        if declared_class != target_class:
            raise MappingError(
                f"Current full-profile runner declaration mismatch: {target} declares {declared_class}, expected {target_class}"
            )
        historical_source = spec.get("historical_source_file")
        historical_class = str(spec.get("historical_source_model_class") or "")
        if not isinstance(historical_source, Path) or not historical_source.is_file():
            raise MappingError(f"Historical full-profile source is missing: {historical_source}")
        if not historical_class:
            raise MappingError(f"Historical full-profile source class is missing: {scheme_id}")
        plan.append(
            {
                "scheme_id": scheme_id,
                "runner_model": str(spec["runner_model"]),
                "source_file": source,
                "source_model_class": source_class,
                "source_sha256": sha256_file(source),
                "historical_source_file": historical_source,
                "historical_source_model_class": historical_class,
                "historical_source_sha256": sha256_file(historical_source),
                "target_file": target,
                "target_model_class": target_class,
                "target_sha256": sha256_file(target),
            }
        )

    target_paths = [item["target_file"] for item in plan]
    if len(target_paths) != len(set(target_paths)):
        raise MappingError("Full-profile runner plan has duplicate target files")
    return plan


def verify_full_profile_runners(plan: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    order = SINGLE_UAV_ORDER_PATH.read_text(encoding="utf-8").splitlines() if SINGLE_UAV_ORDER_PATH.is_file() else []
    if "IntegratedChains" not in order:
        errors.append("Experiment/SingleUav/package.order must list IntegratedChains")
    for item in plan:
        source = item["source_file"]
        historical_source = item["historical_source_file"]
        target = item["target_file"]
        if sha256_file(source) != item["source_sha256"]:
            errors.append(f"Full-profile provenance source hash changed: {repo_path(source)}")
        if sha256_file(historical_source) != item["historical_source_sha256"]:
            errors.append(f"Historical full-profile source hash changed: {repo_path(historical_source)}")
        if not target.is_file():
            errors.append(f"Missing current full-profile runner: {repo_path(target)}")
            continue
        declared_within, declared_name = model_declaration(target.read_text(encoding="utf-8"))
        declared_class = f"{declared_within}.{declared_name}" if declared_within else declared_name
        if declared_class != item["target_model_class"]:
            errors.append(f"Full-profile runner declaration differs: {repo_path(target)}")
    return errors




def all_import_items(plan: list[dict[str, Any]], support_plan: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Combine support and primary imports while rejecting package collisions."""

    support_plan = support_import_plan() if support_plan is None else support_plan
    items = [*support_plan, *plan]
    target_paths = [item["target_file"] for item in items]
    source_models = [item["target_model_class"] for item in items]
    if len(target_paths) != len(set(target_paths)) or len(source_models) != len(set(source_models)):
        raise MappingError("Graphical support import collides with a primary controller import")
    return items


def expected_import_text(item: dict[str, Any]) -> str:
    source = item["source_file"]
    if not isinstance(source, Path):
        raise MappingError("Import plan source_file must be a Path")
    text = source.read_text(encoding="utf-8")
    return canonical_graphical_import_text(
        f"within {item['target_package']};\n\n{without_top_level_within(text)}"
    )


def import_equivalence_text(text: str) -> str:
    """Normalize only harmless Sysplorer/generated-import formatting changes.

    Sysplorer may remove the blank line immediately after the injected
    ``within`` declaration and the final newline when a copied graphical
    controller is opened or checked. Source artifacts can also contain only
    line-end whitespace differences. Those changes do not alter the
    source-derived model. Do not normalize the model body beyond line-end
    whitespace: any declaration, equation, annotation, or layout drift must
    remain visible to G4/G5 validation.
    """

    clean = canonical_graphical_import_text(text)
    match = re.match(
        r"\A(within\s+[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*;\n)(?:\n)?",
        clean,
    )
    if not match:
        return clean
    return f"{match.group(1)}{clean[match.end():].rstrip()}"


def import_equivalence_mode(current: str, expected: str) -> str | None:
    """Classify an allowed G4 import difference without masking model drift.

    G4 imports preserve the source controller body. A later G5 readability
    repair may change only Modelica ``Placement`` and ``Line`` annotations.
    That is a diagram-only change, so it remains admissible, but all other
    source text, including declarations and equations, must still match.
    """

    normalized_current = import_equivalence_text(current)
    normalized_expected = import_equivalence_text(expected)
    if normalized_current == normalized_expected:
        return "exact_source_copy_or_sysplorer_whitespace_only"
    if normalized_visual_metadata(normalized_current) == normalized_visual_metadata(normalized_expected):
        return "g5_visual_metadata_only"
    return None


def direct_graphical_native_text(text: str) -> str:
    """Normalize one narrowly audited Sysplorer direct-graph serialization.

    Direct graphical sources are created outside the formal package and contain
    a hidden empty ``ModelWorkspace`` plus an output-interval hint.  Sysplorer
    removes those two serialization details when the source is loaded under the
    formal package, injects ``within``, and reorders the two standard imports.
    This helper allows only those exact changes.  It deliberately leaves every
    controller declaration, parameter, equation, connect call, port, and
    non-visual annotation in the compared text.
    """

    clean = without_top_level_within(text)
    required_imports = {"BaseWorkspace.*", "SysplorerEmbeddedCoder.Types.*"}
    imports = set(
        re.findall(
            r"(?m)^\s*import\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\.\*)\s*;\s*$",
            clean,
        )
    )
    if not required_imports.issubset(imports):
        raise MappingError("Direct graphical source is missing a required native import")
    clean = re.sub(
        r"(?m)^[ \t]*import[ \t]+(?:BaseWorkspace|SysplorerEmbeddedCoder\.Types)\.\*[ \t]*;[ \t]*(?:\r?\n|$)",
        "",
        clean,
    )

    workspace_extends = re.findall(r"(?m)^\s*extends\s+ModelWorkspace\s*;\s*$", clean)
    if len(workspace_extends) > 1:
        raise MappingError("Direct graphical source has more than one ModelWorkspace extension")
    clean = re.sub(r"(?m)^\s*extends\s+ModelWorkspace\s*;\s*\n?", "", clean)

    workspace_pattern = re.compile(
        r"\n?\s*model\s+ModelWorkspace\s*\n"
        r"\s*annotation\(__MWORKS\(hide\s*=\s*true,\s*"
        r"BlockSystem\(blockKind\s*=\s*BlockKind\.modelWorkspace\)\)\);\s*\n"
        r"\s*end\s+ModelWorkspace\s*;\s*",
        re.DOTALL,
    )
    clean, workspace_count = workspace_pattern.subn("\n", clean)
    if workspace_count > 1 or "ModelWorkspace" in clean:
        raise MappingError("Direct graphical source has an unexpected ModelWorkspace body")

    # Direct graphical review cores use the native 0.01 s controller sample
    # period; older Wave-A imports happened to serialize 0.02. A 0.2 s G6
    # internal probe additionally makes Sysplorer persist its 50-sample
    # output interval as 0.004. The importer may omit only these audited
    # visual/output hints, which do not alter topology or the control law.
    clean = re.sub(r",\s*OutputInterval\s*=\s*0\.(?:004|01|02)\s*", "", clean)
    if "OutputInterval" in clean:
        raise MappingError("Direct graphical source has an unsupported OutputInterval change")

    # Loading a newly generated direct graph once can materialize this exact
    # Sysplorer default experiment tuple. It does not change the control law,
    # ports, equations, or diagram. Accept only the complete default tuple;
    # any different algorithm, interval, start/stop time, or integrator value
    # remains a visible source change.
    native_experiment_defaults = re.compile(
        r"experiment\(\s*Algorithm\s*=\s*Euler\s*,\s*Interval\s*=\s*-1\s*,\s*"
        r"IntegratorStep\s*=\s*0\s*,\s*StartTime\s*=\s*0\s*,\s*"
        r"StopTime\s*=\s*0\.2\s*,\s*StoreEventValue\s*=\s*0\s*\)"
    )
    clean, experiment_default_count = native_experiment_defaults.subn(
        "experiment(Algorithm=Euler,Interval=-1)", clean
    )
    if experiment_default_count > 1:
        raise MappingError("Direct graphical source has multiple native default experiment tuples")
    # Sysplorer inserts indentation before the model-level metadata annotation
    # when it imports a direct graph into a package. This is whitespace-only.
    clean = re.sub(r"(?m)^[ \t]+(?=annotation\(__MWORKS\()", "", clean)
    return canonical_graphical_import_text(normalized_visual_metadata(clean))


def direct_graphical_native_equivalence_mode(item: dict[str, Any], target: Path) -> str | None:
    """Accept audited source-to-package serialization changes for direct graphs."""

    direct_id = str(item.get("scheme_id") or item.get("support_id") or "")
    if direct_id not in (*DIRECT_GRAPHICAL_PRIMARY, "qp_nmpc_safety_graphical_review_core"):
        return None
    source = item.get("source_file")
    if not isinstance(source, Path) or not source.is_file() or not target.is_file():
        return None
    try:
        source_text = direct_graphical_native_text(source.read_text(encoding="utf-8"))
        target_text = direct_graphical_native_text(target.read_text(encoding="utf-8"))
    except (OSError, MappingError):
        return None
    if source_text == target_text:
        return "audited_sysplorer_native_direct_graphical_serialization"
    return None


def package_file_texts(
    plan: list[dict[str, Any]], support_plan: list[dict[str, Any]] | None = None
) -> dict[Path, str]:
    support_plan = support_import_plan() if support_plan is None else support_plan
    by_family: dict[str, list[str]] = {family: [] for family in FAMILY_ORDER}
    primary_by_family: dict[str, list[str]] = {family: [] for family in FAMILY_ORDER}
    for item in support_plan:
        by_family[str(item["family_package"])].append(str(item["source_model"]))
    for item in plan:
        primary_by_family[str(item["family_package"])].append(str(item["source_model"]))

    files: dict[Path, str] = {
        GRAPHICAL_ROOT / "package.mo": (
            "within MoSimQuadrotorModel.Control;\n"
            "package Implementations\n"
            "  \"Non-destructive graphical controller-core imports for G4 review\"\n"
            "  extends Modelica.Icons.Package;\n"
            f"  annotation(__MWORKS(version=\"{MWORKS_MODEL_VERSION}\"));\n"
            "end Implementations;"
        ),
        GRAPHICAL_ROOT / "package.order": "\n".join(IMPLEMENTATIONS_PACKAGE_ORDER) + "\n",
    }
    for family in FAMILY_ORDER:
        package_description = (
            "Graphical controller cores; route selection follows "
            "controller_route_interface_matrix.json, not batch prefixes"
            if family == "ClassicRobust"
            else "G4 imported graphical controller cores; not whole-aircraft entries"
        )
        files[GRAPHICAL_ROOT / family / "package.mo"] = (
            f"within {GRAPHICAL_PACKAGE};\n"
            f"package {family}\n"
            f"  \"{package_description}\"\n"
            "  extends Modelica.Icons.Package;\n"
            f"  annotation(__MWORKS(version=\"{MWORKS_MODEL_VERSION}\"));\n"
            f"end {family};"
        )
        # Dependencies precede the controller entries that instantiate them.
        names = [
            *by_family[family],
            *LEGACY_COMPATIBILITY_MODELS_BY_FAMILY.get(family, ()),
            *sorted(primary_by_family[family]),
            *TRAILING_LEGACY_COMPATIBILITY_MODELS_BY_FAMILY.get(family, ()),
        ]
        files[GRAPHICAL_ROOT / family / "package.order"] = "\n".join(names) + "\n"
    return files


def verify_imported_files(
    plan: list[dict[str, Any]],
    *,
    support_plan: list[dict[str, Any]] | None = None,
    full_profile_plan: list[dict[str, Any]] | None = None,
    expected_package_files: dict[Path, str] | None = None,
    require_control_order: bool = True,
) -> list[str]:
    """Verify either the complete import surface or an explicit safe subset.

    The default retains the complete G4 validation contract.  A caller that is
    adding a bounded G5 batch may provide its exact dependency, metadata, and
    full-profile scope so a pre-existing unrelated import cannot block or be
    modified by the new batch.
    """

    errors: list[str] = []
    support_plan = support_import_plan() if support_plan is None else support_plan
    full_profile_plan = full_profile_runner_plan() if full_profile_plan is None else full_profile_plan
    expected_package_files = (
        package_file_texts(plan, support_plan)
        if expected_package_files is None
        else expected_package_files
    )
    imported_items = all_import_items(plan, support_plan)
    approved_variants = read_approved_graphical_import_variants()
    planned_identities = {import_item_identity(item) for item in imported_items}
    unknown_variant_identities = sorted(set(approved_variants) - planned_identities)
    if unknown_variant_identities:
        errors.append(
            "Approved graphical import variant has no current planned import: "
            + ", ".join(f"{kind}/{identifier}" for kind, identifier in unknown_variant_identities)
        )
    if require_control_order and (
        not CONTROL_ORDER_PATH.is_file()
        or "Implementations" not in CONTROL_ORDER_PATH.read_text(encoding="utf-8").splitlines()
    ):
        errors.append("Control/package.order must list Implementations")
    for path, expected in expected_package_files.items():
        if not path.is_file():
            errors.append(f"Missing package file: {repo_path(path)}")
        elif canonical_package_file_text(path.read_text(encoding="utf-8")) != canonical_package_file_text(expected):
            errors.append(f"Unexpected package file contents: {repo_path(path)}")
    for item in imported_items:
        source = item["source_file"]
        target = item["target_file"]
        identity = import_item_identity(item)
        configured_variant = approved_variants.get(identity)
        if not source.is_file():
            errors.append(f"Missing source file: {repo_path(source)}")
            continue
        if sha256_file(source) != item["source_sha256"]:
            errors.append(f"Source hash changed while planning: {repo_path(source)}")
        if not target.is_file():
            errors.append(f"Missing imported current model: {repo_path(target)}")
            continue
        expected = expected_import_text(item)
        exact_mode = import_equivalence_mode(target.read_text(encoding="utf-8"), expected)
        native_mode = direct_graphical_native_equivalence_mode(item, target)
        if exact_mode is not None or native_mode is not None:
            if configured_variant is not None:
                errors.append(
                    "Approved graphical import variant is no longer needed and must be removed: "
                    f"{identity[0]}/{identity[1]}"
                )
            continue
        variant = approved_graphical_import_variant(
            item, target, expected, variants=approved_variants
        )
        if variant is None:
            if configured_variant is not None:
                errors.append(
                    "Approved graphical import variant binding drift: "
                    f"{identity[0]}/{identity[1]}"
                )
            else:
                errors.append(f"Imported current model differs from its exact source copy: {repo_path(target)}")
    if full_profile_plan:
        errors.extend(verify_full_profile_runners(full_profile_plan))
    return errors


def project_model_record(path: Path, model_class: str) -> dict[str, Any]:
    if not path.is_file():
        raise MappingError(f"Current project model is missing: {path}")
    declared_within, declared_name = model_declaration(path.read_text(encoding="utf-8"))
    declared_class = f"{declared_within}.{declared_name}" if declared_within else declared_name
    if declared_class != model_class:
        raise MappingError(f"Current project model declaration mismatch: {path} declares {declared_class}, expected {model_class}")
    return {
        "current_model_file": repo_path(path),
        "current_model_class": model_class,
        "current_model_sha256": sha256_file(path),
        "current_model_topology_sha256": model_topology_sha256(path),
    }


def build_current_map(
    catalog: dict[str, Any] | None = None,
    inventory: dict[str, Any] | None = None,
    *,
    require_imports: bool = True,
) -> dict[str, Any]:
    catalog = catalog if catalog is not None else read_json(CATALOG_PATH)
    inventory = inventory if inventory is not None else read_json(INVENTORY_PATH)
    catalog_rows = catalog.get("schemes")
    inventory_rows = inventory.get("schemes")
    if not isinstance(catalog_rows, list) or not isinstance(inventory_rows, list):
        raise MappingError("Catalog and inventory must expose scheme lists")
    inventory_by_id = {
        str(row.get("scheme_id")): row
        for row in inventory_rows
        if isinstance(row, dict) and row.get("scheme_id")
    }
    catalog_ids = [str(row.get("scheme_id")) for row in catalog_rows if isinstance(row, dict) and row.get("scheme_id")]
    if len(catalog_ids) != 48 or set(catalog_ids) != set(inventory_by_id):
        raise MappingError("G4 requires the active 48-entry profile catalog and matching G1 inventory IDs")

    plan = import_plan(catalog, inventory)
    support_plan = support_import_plan()
    full_profile_plan = full_profile_runner_plan()
    approved_variants = read_approved_graphical_import_variants()
    if require_imports:
        import_errors = verify_imported_files(plan, full_profile_plan=full_profile_plan)
        if import_errors:
            raise MappingError("; ".join(import_errors))
    plan_by_scheme = {item["scheme_id"]: item for item in plan}
    full_profile_by_scheme = {item["scheme_id"]: item for item in full_profile_plan}
    rows: list[dict[str, Any]] = []

    for scheme in catalog_rows:
        if not isinstance(scheme, dict):
            continue
        scheme_id = str(scheme["scheme_id"])
        inventory_row = inventory_by_id[scheme_id]
        entry_type = str(scheme["entry_type"])
        base = {
            "scheme_id": scheme_id,
            "profile_id": scheme.get("profile_id"),
            "display_name_zh": scheme.get("display_name_zh"),
            "category": scheme.get("category"),
            "entry_type": entry_type,
            "role": scheme.get("role"),
            "implementation_status": scheme.get("implementation_status"),
            "selection_eligibility": scheme.get("selection_eligibility"),
            "execution_kind": scheme.get("execution_kind"),
            "mworks_run_eligible": False,
        }
        if entry_type == "mworks_control_profile":
            execution_kind = str(scheme.get("execution_kind"))
            if execution_kind == "graphical_control_core":
                item = plan_by_scheme[scheme_id]
                target = item["target_file"]
                if not target.is_file():
                    raise MappingError(f"Import target missing while building map: {target}")
                variant = approved_graphical_import_variant(
                    item,
                    target,
                    expected_import_text(item),
                    variants=approved_variants,
                )
                base.update(
                    {
                        "mapping_state": "resolved_current_model",
                        "current_model_file": repo_path(target),
                        "current_model_class": item["target_model_class"],
                        "current_model_sha256": sha256_file(target),
                        "current_model_topology_sha256": model_topology_sha256(target),
                        "current_model_role": "graphical_controller_core",
                        "compatibility_decision": (
                            "approved_project_variant"
                            if variant is not None
                            else "g5_direct_graphical_source_import"
                            if scheme_id in DIRECT_GRAPHICAL_PRIMARY
                            else "g4_exact_source_copy_with_package_context_only"
                        ),
                        "source_provenance": {
                            "source_file": repo_path(item["source_file"]),
                            "source_model_class": item["source_model"],
                            "source_sha256": item["source_sha256"],
                            "import_mode": (
                                "official_sysplorer_direct_graphical_source_import"
                                if scheme_id in DIRECT_GRAPHICAL_PRIMARY
                                else "non_destructive_copy_with_package_context"
                            ),
                            "source_results_reference_kind": item["source_results_reference_kind"],
                            "approved_project_variant": (
                                approved_variant_record(variant) if variant is not None else None
                            ),
                        },
                        "next_gate": "G5 topology review and minimum MWORKS closed-loop gate; this core alone is not a whole-aircraft result.",
                    }
                )
            elif execution_kind == "full_profile_whole_aircraft":
                item = full_profile_by_scheme.get(scheme_id)
                if item is None:
                    raise MappingError(f"Full profile lacks current model decision: {scheme_id}")
                target = item["target_file"]
                base.update(
                    {
                        "mapping_state": "resolved_current_model",
                        **project_model_record(target, item["target_model_class"]),
                        "current_model_role": "full_profile_whole_aircraft_closed_loop",
                        "compatibility_decision": "current_project_owned_full_profile_runner",
                        "source_provenance": {
                            "source_config": inventory_row.get("model_entry", {}).get("source_config"),
                            "source_file": repo_path(item["source_file"]),
                            "source_sha256": item["source_sha256"],
                            "source_model_class": item["source_model_class"],
                            "import_mode": "current_project_owned_runner_with_historical_source_provenance",
                            "historical_source_file": repo_path(item["historical_source_file"]),
                            "historical_source_sha256": item["historical_source_sha256"],
                            "historical_source_model_class": item["historical_source_model_class"],
                        },
                        "next_gate": "G5 reviews the source wrapper's referenced internal controller first, then validates this full profile's minimum MWORKS closed loop.",
                    }
                )
            elif execution_kind == "planned_profile":
                base.update(
                    {
                        "mapping_state": "planned_profile_no_model",
                        "blocker_code": "planned_profile_implementation_not_started",
                        "blocker_reason": scheme.get("implementation_note"),
                        "next_gate": "Implement the approved profile, Adapter, formal Runner, and minimum-closure evidence before any screening or comparison.",
                    }
                )
            else:
                raise MappingError(f"Unsupported MWORKS profile execution kind: {scheme_id}/{execution_kind}")
        elif entry_type == "engineering_deployment_baseline":
            if scheme_id != "px4ctrl":
                raise MappingError(f"Only px4ctrl may be an engineering baseline: {scheme_id}")
            base.update(
                {
                    "mapping_state": "pending_mworks_equivalent_core",
                    "blocker_code": "mworks_equivalent_px4ctrl_core_not_implemented",
                    "next_gate": "Implement and validate the MWORKS-equivalent px4ctrl core with C++ behavior/interface equivalence before formal seven-scenario comparison.",
                }
            )
        else:
            raise MappingError(f"Unsupported scheme entry_type: {entry_type}")
        rows.append(base)

    states = Counter(str(row["mapping_state"]) for row in rows)
    return {
        "schema": "mosim.current_model_entry_map.v1",
        "version": 1,
        "scope": "G4 static current-model mapping. It does not authorize MWORKS, code generation, runtime, or report claims.",
        "source_files": {
            "control_scheme_catalog": repo_path(CATALOG_PATH),
            "g1_execution_inventory": repo_path(INVENTORY_PATH),
            "graphical_import_package": repo_path(GRAPHICAL_ROOT),
            "graphical_support_imports": [
                {
                    "support_id": item["support_id"],
                    "source_file": repo_path(item["source_file"]),
                    "target_file": repo_path(item["target_file"]),
                    "target_model_class": item["target_model_class"],
                    "purpose": item["purpose"],
                    "required_by_scheme_ids": item["required_by_scheme_ids"],
                }
                for item in support_plan
            ],
        },
        "source_sha256": {
            "control_scheme_catalog": sha256_json(catalog),
            "g1_execution_inventory": sha256_json(inventory),
            "graphical_support_imports": {
                item["support_id"]: item["source_sha256"] for item in support_plan
            },
        },
        "summary": {
            "top_level_entry_count": len(rows),
            "mapping_state_counts": dict(sorted(states.items())),
            "graphical_controller_core_import_count": len(plan),
            "graphical_support_import_count": len(support_plan),
                "full_profile_whole_aircraft_count": len(full_profile_plan),
            "planned_mworks_profile_count": sum(
                row["mapping_state"] == "planned_profile_no_model" for row in rows
            ),
            "mworks_equivalent_core_pending_count": sum(
                row["mapping_state"] == "pending_mworks_equivalent_core" for row in rows
            ),
            "mworks_run_eligible_count": sum(bool(row["mworks_run_eligible"]) for row in rows),
        },
        "schemes": rows,
    }
