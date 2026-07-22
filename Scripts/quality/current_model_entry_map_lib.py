#!/usr/bin/env python3
"""Shared static plan for G4 current-model entry mapping.

This module deliberately distinguishes a historical graphical controller-core
copy from a current whole-aircraft simulation.  It never opens MWORKS or
changes a historical source file.
"""

from __future__ import annotations

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
CONTROLLERS_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Controllers"
GRAPHICAL_ROOT = CONTROLLERS_ROOT / "GraphicalMIL"
GRAPHICAL_PACKAGE = "MoSimQuadrotorModel.Controllers.GraphicalMIL"
CONTROLLERS_ORDER_PATH = CONTROLLERS_ROOT / "package.order"
INTEGRATED_CHAINS_ROOT = CONTROLLERS_ROOT / "IntegratedChains"
INTEGRATED_CHAINS_PACKAGE = "MoSimQuadrotorModel.Controllers.IntegratedChains"

FAMILY_PACKAGES = {
    "pid_family": "PidFamily",
    "classic_robust": "ClassicRobust",
    "sliding_mode": "SlidingMode",
    "optimization": "Optimization",
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

BLOCKED_PRIMARY = {
    "mu_synthesis": {
        "blocker_code": "missing_dynamic_mu_synthesis_controller_implementation",
        "reason": "Installed Syslab lacks a dynamic musyn controller implementation; a constant-matrix mu analysis is not a controller model.",
    },
    "neural_smc": {
        "blocker_code": "missing_frozen_neural_smc_training_artifact",
        "reason": "No frozen training dataset, trained Neural-SMC weights, fixed-size inference implementation, and fallback test are jointly available.",
    },
}

SPECIAL_PRIMARY_SOURCES = {
    "official_pid": ROOT / "Models" / "MoSimQuadrotorModel" / "Controllers" / "Sysblocks" / "AWFF_PID_Sysblock_Demo.mo",
    "terminal_smc": ROOT
    / "Results"
    / "control_platform"
    / "p3_sliding_mode_mworks_20260716"
    / "models"
    / "graphical_variants"
    / "MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo",
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
        / "p10_mworks_gap_closeout_20260718"
        / "hinf_hover_wrench"
        / "models"
        / "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock.mo",
        "purpose": "Shared CFunction bridge required by the P10 H-infinity hover-wrench graphical wrapper.",
        "required_by_scheme_ids": (
            "hinf_hover_wrench",
        ),
    },
)
FIXED_INTEGRATED_SPECS = {
    "fixed_awff_pid": {
        "alias_model": "FixedAwffPid",
        "source_file": ROOT / "Models" / "MoSimQuadrotorModel" / "Missions" / "Official" / "Example1AWFFSysblockClosedLoop.mo",
        "source_model_class": "MoSimQuadrotorModel.Missions.Official.Example1AWFFSysblockClosedLoop",
    },
    "fixed_awff_l1_residual": {
        "alias_model": "FixedAwffL1Residual",
        "source_file": ROOT / "Models" / "MoSimQuadrotorModel" / "Missions" / "Official" / "Example1L1SysblockClosedLoop.mo",
        "source_model_class": "MoSimQuadrotorModel.Missions.Official.Example1L1SysblockClosedLoop",
    },
    "fixed_awff_l1_indi": {
        "alias_model": "FixedAwffL1Indi",
        "source_file": ROOT / "Models" / "MoSimQuadrotorModel" / "Missions" / "Official" / "Example1INDISysblockClosedLoop.mo",
        "source_model_class": "MoSimQuadrotorModel.Missions.Official.Example1INDISysblockClosedLoop",
    },
    "fixed_linear_mpc_l1_indi": {
        "alias_model": "FixedLinearMpcL1Indi",
        "source_file": ROOT / "Models" / "MoSimQuadrotorModel" / "Missions" / "Official" / "Example1LinearMPCSysblockClosedLoop.mo",
        "source_model_class": "MoSimQuadrotorModel.Missions.Official.Example1LinearMPCSysblockClosedLoop",
    },
    "fixed_qp_nmpc_l1_indi_cbf": {
        "alias_model": "FixedQpNmpcL1IndiCbf",
        "source_file": ROOT / "Models" / "MoSimQuadrotorModel" / "Robustness" / "Scenarios" / "Example1QPNMPCSafetySysblockClosedLoop.mo",
        "source_model_class": "MoSimQuadrotorModel.Robustness.Scenarios.Example1QPNMPCSafetySysblockClosedLoop",
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


def sha256_json(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
    never changes declarations, equations, annotations, or layout metadata.
    """

    clean = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip(" \t") for line in clean.split("\n")).rstrip() + "\n"


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
        if not isinstance(scheme, dict) or scheme.get("entry_type") != "competition_primary_route":
            continue
        scheme_id = str(scheme.get("scheme_id"))
        if scheme_id in BLOCKED_PRIMARY:
            continue
        row = by_id.get(scheme_id)
        if row is None:
            raise MappingError(f"G1 inventory misses primary scheme: {scheme_id}")
        category = str(scheme.get("category"))
        family = FAMILY_PACKAGES.get(category)
        if family is None:
            raise MappingError(f"Unsupported current graphical family for {scheme_id}: {category}")
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

    Support imports are package dependencies, not additional competition schemes.
    They must therefore be hash-checked and copied with the same safeguards as a
    top-level controller core without changing the frozen 49-scheme count.
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
def fixed_integrated_alias_plan() -> list[dict[str, Any]]:
    """Plan non-destructive formal aliases for the five fixed integrated chains."""

    plan: list[dict[str, Any]] = []
    for scheme_id, spec in FIXED_INTEGRATED_SPECS.items():
        source = spec["source_file"]
        alias_model = str(spec["alias_model"])
        source_class = str(spec["source_model_class"])
        if not isinstance(source, Path) or not source.is_file():
            raise MappingError(f"Fixed integrated source is missing: {source}")
        declared_within, declared_name = model_declaration(source.read_text(encoding="utf-8"))
        declared_class = f"{declared_within}.{declared_name}" if declared_within else declared_name
        if declared_class != source_class:
            raise MappingError(f"Fixed integrated source declaration mismatch: {source}")
        plan.append(
            {
                "scheme_id": scheme_id,
                "alias_model": alias_model,
                "source_file": source,
                "source_model_class": source_class,
                "source_sha256": sha256_file(source),
                "target_file": INTEGRATED_CHAINS_ROOT / f"{alias_model}.mo",
                "target_model_class": f"{INTEGRATED_CHAINS_PACKAGE}.{alias_model}",
            }
        )

    target_paths = [item["target_file"] for item in plan]
    if len(target_paths) != len(set(target_paths)):
        raise MappingError("Fixed integrated alias plan has duplicate target files")
    return plan


def expected_fixed_integrated_alias_text(item: dict[str, Any]) -> str:
    return (
        f"within {INTEGRATED_CHAINS_PACKAGE};\n\n"
        f"model {item['alias_model']}\n"
        '  "Formal public alias for a canonical whole-aircraft controller chain"\n'
        f"  extends {item['source_model_class']};\n"
        "  annotation(__MWORKS(hide=false));\n"
        f"end {item['alias_model']};\n"
    )
def fixed_integrated_package_file_texts(plan: list[dict[str, Any]]) -> dict[Path, str]:
    names = [str(item["alias_model"]) for item in plan]
    return {
        INTEGRATED_CHAINS_ROOT / "package.mo": (
            "within MoSimQuadrotorModel.Controllers;\n"
            "package IntegratedChains\n"
            '  "Formal aliases for fixed whole-aircraft controller chains"\n'
            "  extends Modelica.Icons.Package;\n"
            "end IntegratedChains;\n"
        ),
        INTEGRATED_CHAINS_ROOT / "package.order": "\n".join(names) + "\n",
    }


def verify_fixed_integrated_aliases(plan: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    order = CONTROLLERS_ORDER_PATH.read_text(encoding="utf-8").splitlines() if CONTROLLERS_ORDER_PATH.is_file() else []
    if "IntegratedChains" not in order:
        errors.append("Controllers/package.order must list IntegratedChains")
    for path, expected in fixed_integrated_package_file_texts(plan).items():
        if not path.is_file():
            errors.append(f"Missing fixed-chain package file: {repo_path(path)}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"Unexpected fixed-chain package file contents: {repo_path(path)}")
    for item in plan:
        source = item["source_file"]
        target = item["target_file"]
        if sha256_file(source) != item["source_sha256"]:
            errors.append(f"Fixed-chain source hash changed while planning: {repo_path(source)}")
        if not target.is_file():
            errors.append(f"Missing fixed-chain formal alias: {repo_path(target)}")
        elif target.read_text(encoding="utf-8") != expected_fixed_integrated_alias_text(item):
            errors.append(f"Fixed-chain formal alias differs from its expected text: {repo_path(target)}")
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
            "within MoSimQuadrotorModel.Controllers;\n"
            "package GraphicalMIL\n"
            "  \"Non-destructive graphical controller-core imports for G4 review\"\n"
            "  extends Modelica.Icons.Package;\n"
            "end GraphicalMIL;\n"
        ),
        GRAPHICAL_ROOT / "package.order": "\n".join(FAMILY_ORDER) + "\n",
    }
    for family in FAMILY_ORDER:
        files[GRAPHICAL_ROOT / family / "package.mo"] = (
            f"within {GRAPHICAL_PACKAGE};\n"
            f"package {family}\n"
            "  \"G4 imported graphical controller cores; not whole-aircraft entries\"\n"
            "  extends Modelica.Icons.Package;\n"
            f"end {family};\n"
        )
        # Dependencies precede the controller entries that instantiate them.
        names = [*by_family[family], *sorted(primary_by_family[family])]
        files[GRAPHICAL_ROOT / family / "package.order"] = "\n".join(names) + "\n"
    return files


def verify_imported_files(plan: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    support_plan = support_import_plan()
    fixed_plan = fixed_integrated_alias_plan()
    imported_items = all_import_items(plan, support_plan)
    if not CONTROLLERS_ORDER_PATH.is_file() or "GraphicalMIL" not in CONTROLLERS_ORDER_PATH.read_text(encoding="utf-8").splitlines():
        errors.append("Controllers/package.order must list GraphicalMIL")
    for path, expected in package_file_texts(plan, support_plan).items():
        if not path.is_file():
            errors.append(f"Missing package file: {repo_path(path)}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"Unexpected package file contents: {repo_path(path)}")
    for item in imported_items:
        source = item["source_file"]
        target = item["target_file"]
        if not source.is_file():
            errors.append(f"Missing source file: {repo_path(source)}")
            continue
        if sha256_file(source) != item["source_sha256"]:
            errors.append(f"Source hash changed while planning: {repo_path(source)}")
        if not target.is_file():
            errors.append(f"Missing imported current model: {repo_path(target)}")
        elif import_equivalence_mode(target.read_text(encoding="utf-8"), expected_import_text(item)) is None:
            errors.append(f"Imported current model differs from its exact source copy: {repo_path(target)}")
    errors.extend(verify_fixed_integrated_aliases(fixed_plan))
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
    if len(catalog_ids) != 49 or set(catalog_ids) != set(inventory_by_id):
        raise MappingError("G4 requires exactly the frozen 49 catalog and G1 inventory IDs")

    plan = import_plan(catalog, inventory)
    support_plan = support_import_plan()
    fixed_plan = fixed_integrated_alias_plan()
    if require_imports:
        import_errors = verify_imported_files(plan)
        if import_errors:
            raise MappingError("; ".join(import_errors))
    plan_by_scheme = {item["scheme_id"]: item for item in plan}
    fixed_by_scheme = {item["scheme_id"]: item for item in fixed_plan}
    rows: list[dict[str, Any]] = []

    for scheme in catalog_rows:
        if not isinstance(scheme, dict):
            continue
        scheme_id = str(scheme["scheme_id"])
        inventory_row = inventory_by_id[scheme_id]
        entry_type = str(scheme["entry_type"])
        base = {
            "scheme_id": scheme_id,
            "display_name_zh": scheme.get("display_name_zh"),
            "category": scheme.get("category"),
            "entry_type": entry_type,
            "mworks_run_eligible": False,
        }
        if entry_type == "competition_primary_route":
            if scheme_id in BLOCKED_PRIMARY:
                base.update(
                    {
                        "mapping_state": "blocked_missing_current_model",
                        "blocker_code": BLOCKED_PRIMARY[scheme_id]["blocker_code"],
                        "blocker_reason": BLOCKED_PRIMARY[scheme_id]["reason"],
                        "source_candidates_inspected": [repo_path(path) for path in source_candidates(inventory_row)],
                        "next_gate": "Acquire a real implementation artifact before graphical or MIL review.",
                    }
                )
            else:
                item = plan_by_scheme[scheme_id]
                target = item["target_file"]
                if not target.is_file():
                    raise MappingError(f"Import target missing while building map: {target}")
                base.update(
                    {
                        "mapping_state": "resolved_current_model",
                        "current_model_file": repo_path(target),
                        "current_model_class": item["target_model_class"],
                        "current_model_sha256": sha256_file(target),
                        "current_model_role": "graphical_controller_core",
                        "compatibility_decision": "g4_exact_source_copy_with_package_context_only",
                        "source_provenance": {
                            "source_file": repo_path(item["source_file"]),
                            "source_model_class": item["source_model"],
                            "source_sha256": item["source_sha256"],
                            "import_mode": "non_destructive_copy_with_package_context",
                            "source_results_reference_kind": item["source_results_reference_kind"],
                        },
                        "next_gate": "G5 topology review and minimum MWORKS closed-loop gate; this core alone is not a whole-aircraft result.",
                    }
                )
        elif entry_type == "engineering_baseline":
            if scheme_id != "px4ctrl":
                raise MappingError(f"Only px4ctrl may be an engineering baseline: {scheme_id}")
            base.update(
                {
                    "mapping_state": "not_applicable_runtime_baseline",
                    "blocker_code": "runtime_baseline_not_an_mworks_graphical_scheme",
                    "next_gate": "Post-G7 ROS1/Sunray/Gazebo/PX4 baseline verification.",
                }
            )
        elif entry_type == "fixed_integrated_scheme":
            item = fixed_by_scheme.get(scheme_id)
            if item is None:
                raise MappingError(f"Fixed chain lacks current model decision: {scheme_id}")
            target = item["target_file"]
            base.update(
                {
                    "mapping_state": "resolved_current_model",
                    **project_model_record(target, item["target_model_class"]),
                    "current_model_role": "fixed_integrated_whole_aircraft_closed_loop",
                    "compatibility_decision": "g4_non_destructive_formal_alias_of_existing_fixed_chain",
                    "source_provenance": {
                        "source_config": inventory_row.get("model_entry", {}).get("source_config"),
                        "source_file": repo_path(item["source_file"]),
                        "source_sha256": item["source_sha256"],
                        "source_model_class": item["source_model_class"],
                        "import_mode": "formal_alias_extends_existing_project_model",
                    },
                    "next_gate": "G5 reviews the source wrapper's referenced internal controller first, then validates the fixed-chain minimum MWORKS closed loop.",
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
            "top_level_scheme_count": len(rows),
            "mapping_state_counts": dict(sorted(states.items())),
            "graphical_controller_core_import_count": len(plan),
            "graphical_support_import_count": len(support_plan),
            "fixed_integrated_whole_aircraft_count": len(fixed_plan),
            "mworks_run_eligible_count": sum(bool(row["mworks_run_eligible"]) for row in rows),
        },
        "schemes": rows,
    }
