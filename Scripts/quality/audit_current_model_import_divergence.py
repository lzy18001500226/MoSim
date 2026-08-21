#!/usr/bin/env python3
"""Record, without normalizing away, current-model import divergence.

The historical graphical sources remain provenance artifacts.  The project
owned copies may intentionally carry Sunray150 calibration or probe-window
changes, so this audit classifies the current textual delta instead of calling
it an exact import.  It is source evidence only: it does not prove a MWORKS
check, simulation, code generation, or Gazebo behavior.
"""

from __future__ import annotations

import argparse
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

from current_model_entry_map_lib import (  # noqa: E402
    CATALOG_PATH,
    CURRENT_MAP_PATH,
    INVENTORY_PATH,
    ROOT,
    all_import_items,
    approved_graphical_import_variant,
    approved_variant_record,
    direct_graphical_native_equivalence_mode,
    expected_import_text,
    full_profile_runner_plan,
    import_equivalence_mode,
    import_plan,
    read_json,
    repo_path,
    sha256_file,
    support_import_plan,
)


SCHEMA = "mosim.current_model_import_divergence_audit.v1"
OUTPUT_DIR = ROOT / "Results" / "control_platform" / "current_model_import_divergence_20260726"
OUTPUT_JSON = OUTPUT_DIR / "CURRENT_MODEL_IMPORT_DIVERGENCE_AUDIT.json"
OUTPUT_MD = OUTPUT_DIR / "CURRENT_MODEL_IMPORT_DIVERGENCE_AUDIT.md"

SIMULATION_TOKENS = (
    "experiment(",
    "StopTime",
    "StartTime",
    "IntegratorStep",
    "Tolerance",
    "Algorithm=",
    "Algorithm =",
    "Interval=",
    "Interval =",
    "StoreEventValue",
)
OUTPUT_TOKENS = ("OutputInterval",)
CODEGEN_TOKENS = ("CodeGeneration", "Sim_seting", "code_generation")
VISUAL_TOKENS = ("Placement(", "Line(", "Diagram(", "Icon(")
PORT_TOKENS = ("Port.Inport", "Port.Outport", "RealInput", "RealOutput")
PARAMETER_TOKENS = (
    "gravity",
    "mass",
    "inertia",
    "hover",
    "motor",
    "rotor",
    "thrust",
    "lift",
    "gain=",
    "Gain(",
    "Constant(",
    "default_params",
    "params =",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def markdown_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def categories_for_line(line: str) -> set[str]:
    stripped = line.strip()
    if not stripped:
        return {"serialization_only"}
    categories: set[str] = set()
    if stripped.startswith("within "):
        categories.add("package_namespace")
    if any(token in line for token in CODEGEN_TOKENS):
        categories.add("code_generation_metadata")
    if any(token in line for token in SIMULATION_TOKENS):
        categories.add("simulation_configuration")
    if any(token in line for token in OUTPUT_TOKENS):
        categories.add("output_recording_configuration")
    if any(token in line for token in VISUAL_TOKENS):
        categories.add("diagram_layout")
    if "connect(" in line:
        categories.add("connection_topology")
    if any(token in line for token in PORT_TOKENS):
        categories.add("public_interface")
    if any(token in line for token in PARAMETER_TOKENS):
        categories.add("parameter_or_calibration")
    if re.match(r"\s*(model|block|package|extends|import|equation|algorithm|protected|public)\b", line):
        categories.add("model_structure")
    if "annotation(__MWORKS" in line:
        categories.add("mworks_annotation_metadata")
    return categories or {"unclassified_model_content"}


def diff_summary(expected: str, current: str) -> dict[str, Any]:
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
    changed = [
        line[1:]
        for line in lines
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    categories = Counter(
        category for line in changed for category in categories_for_line(line)
    )
    samples = [line if len(line) <= 500 else f"{line[:497]}..." for line in changed if line.strip()][:12]
    return {
        "diff_sha256": sha256_text("\n".join(lines) + "\n"),
        "changed_line_count": len(changed),
        "category_counts": dict(sorted(categories.items())),
        "changed_line_examples": samples,
    }


def current_map_rows() -> dict[str, dict[str, Any]]:
    value = read_json(CURRENT_MAP_PATH)
    rows = value.get("schemes")
    if not isinstance(rows, list) or len(rows) != 49:
        raise ValueError("current_model_entry_map.json must contain 49 scheme rows")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("scheme_id"), str):
            raise ValueError("current_model_entry_map.json contains an invalid scheme row")
        result[str(row["scheme_id"])] = row
    if len(result) != 49:
        raise ValueError("current_model_entry_map.json has duplicate scheme ids")
    return result


def revalidation_flags(
    category_counts: dict[str, int],
    state: str,
    variant: dict[str, Any] | None = None,
) -> dict[str, bool]:
    if variant is not None:
        return dict(variant["required_revalidation"])
    categories = set(category_counts)
    diverged = state == "diverged_from_historical_import"
    return {
        "requires_fresh_model_check": diverged
        and bool(categories & {"model_structure", "connection_topology", "public_interface", "unclassified_model_content"}),
        "requires_fresh_simulation": diverged
        and bool(
            categories
            & {
                "parameter_or_calibration",
                "simulation_configuration",
                "output_recording_configuration",
                "connection_topology",
                "public_interface",
                "model_structure",
                "unclassified_model_content",
            }
        ),
        "requires_adapter_boundary_review": diverged
        and bool(categories & {"connection_topology", "public_interface", "model_structure", "unclassified_model_content"}),
        "requires_fresh_codegen_review": diverged
        and "code_generation_metadata" in categories,
    }


def graphical_route_record(item: dict[str, Any], map_row: dict[str, Any]) -> dict[str, Any]:
    target = item["target_file"]
    source = item["source_file"]
    if not isinstance(target, Path) or not isinstance(source, Path):
        raise ValueError("graphical import item must expose source and target paths")
    if not target.is_file() or not source.is_file():
        raise ValueError(f"missing graphical source or target for {item.get('scheme_id')}")
    current = target.read_text(encoding="utf-8")
    expected = expected_import_text(item)
    exact_mode = import_equivalence_mode(current, expected)
    if exact_mode is None:
        exact_mode = direct_graphical_native_equivalence_mode(item, target)
    variant = None if exact_mode is not None else approved_graphical_import_variant(item, target, expected)
    state = (
        "equivalent_historical_import"
        if exact_mode
        else "approved_project_variant"
        if variant is not None
        else "diverged_from_historical_import"
    )
    summary = diff_summary(expected, current)
    current_hash = sha256_file(target)
    source_hash = sha256_file(source)
    recorded_hash = map_row.get("current_model_sha256")
    provenance = map_row.get("source_provenance")
    recorded_source_hash = provenance.get("source_sha256") if isinstance(provenance, dict) else None
    return {
        "scheme_id": item["scheme_id"],
        "kind": "graphical_controller_core",
        "source_file": repo_path(source),
        "source_sha256": source_hash,
        "current_model_file": repo_path(target),
        "current_model_sha256": current_hash,
        "current_map_current_hash_matches_file": recorded_hash == current_hash,
        "current_map_source_hash_matches_file": recorded_source_hash == source_hash,
        "comparison_state": state,
        "equivalence_mode": exact_mode,
        "delta": summary,
        "approved_project_variant": approved_variant_record(variant) if variant is not None else None,
        "revalidation": revalidation_flags(summary["category_counts"], state, variant),
        "claim_boundary": (
            "This source comparison does not establish controller equivalence, MWORKS model validity, "
            "simulation performance, code generation, or Gazebo behavior."
        ),
    }


def full_profile_runner_record(item: dict[str, Any], map_row: dict[str, Any]) -> dict[str, Any]:
    target = item["target_file"]
    source = item["source_file"]
    if not isinstance(target, Path) or not isinstance(source, Path):
        raise ValueError("full-profile item must expose source and target paths")
    if not target.is_file() or not source.is_file():
        raise ValueError(f"missing full-profile source or target for {item.get('scheme_id')}")
    current = target.read_text(encoding="utf-8")
    state = "current_project_runner"
    summary = diff_summary(current, current)
    current_hash = sha256_file(target)
    source_hash = sha256_file(source)
    recorded_hash = map_row.get("current_model_sha256")
    provenance = map_row.get("source_provenance")
    recorded_source_hash = provenance.get("source_sha256") if isinstance(provenance, dict) else None
    return {
        "scheme_id": item["scheme_id"],
        "kind": "full_profile_whole_aircraft_runner",
        "source_file": repo_path(source),
        "source_sha256": source_hash,
        "current_model_file": repo_path(target),
        "current_model_sha256": current_hash,
        "current_map_current_hash_matches_file": recorded_hash == current_hash,
        "current_map_source_hash_matches_file": recorded_source_hash == source_hash,
        "comparison_state": state,
        "equivalence_mode": "current_runner_declaration_checked",
        "delta": summary,
        "revalidation": {
            "requires_fresh_model_check": True,
            "requires_fresh_simulation": True,
            "requires_adapter_boundary_review": True,
            "requires_fresh_codegen_review": True,
        },
        "claim_boundary": (
            "The current project-owned Runner is bound to the historical source provenance, but this "
            "static record does not prove a fresh MWORKS check or simulation."
        ),
    }


def build_audit() -> dict[str, Any]:
    catalog = read_json(CATALOG_PATH)
    inventory = read_json(INVENTORY_PATH)
    map_rows = current_map_rows()
    primary = import_plan(catalog, inventory)
    graphical_items = all_import_items(primary, support_import_plan())
    graphical: list[dict[str, Any]] = []
    for item in graphical_items:
        scheme_id = item.get("scheme_id")
        if not isinstance(scheme_id, str):
            continue
        graphical.append(graphical_route_record(item, map_rows[scheme_id]))
    full_profiles = [full_profile_runner_record(item, map_rows[str(item["scheme_id"])]) for item in full_profile_runner_plan()]
    routes = [*graphical, *full_profiles]
    if len(graphical) != 41 or len(full_profiles) != 5 or len(routes) != 46:
        raise ValueError("audit must cover exactly 41 graphical and 5 full-profile Runner routes")
    states = Counter(str(row["comparison_state"]) for row in routes)
    category_counts = Counter(
        category
        for row in routes
        for category in row["delta"]["category_counts"]
    )
    map_hash_drift = [
        row["scheme_id"]
        for row in routes
        if not row["current_map_current_hash_matches_file"] or not row["current_map_source_hash_matches_file"]
    ]
    return {
        "schema": SCHEMA,
        "scope": (
            "Current source-to-project import divergence classification for the 46 MWORKS candidate routes. "
            "It is a pre-refactor fact record, not an execution result."
        ),
        "source_current_model_entry_map": repo_path(CURRENT_MAP_PATH),
        "source_current_model_entry_map_sha256": sha256_file(CURRENT_MAP_PATH),
        "summary": {
            "route_count": len(routes),
            "graphical_controller_core_count": len(graphical),
            "full_profile_whole_aircraft_runner_count": len(full_profiles),
            "comparison_state_counts": dict(sorted(states.items())),
            "changed_category_counts": dict(sorted(category_counts.items())),
            "current_map_hash_drift_route_count": len(map_hash_drift),
            "current_map_hash_drift_route_ids": map_hash_drift,
        },
        "routes": routes,
    }


def validate(value: dict[str, Any]) -> None:
    if value.get("schema") != SCHEMA:
        raise ValueError("audit schema is invalid")
    routes = value.get("routes")
    if not isinstance(routes, list) or len(routes) != 46:
        raise ValueError("audit must contain exactly 46 routes")
    identifiers = [row.get("scheme_id") for row in routes if isinstance(row, dict)]
    if len(identifiers) != 46 or len(set(identifiers)) != 46:
        raise ValueError("audit route ids must be complete and unique")
    kinds = Counter(str(row.get("kind")) for row in routes if isinstance(row, dict))
    expected_kinds = Counter(
        {
            "graphical_controller_core": 41,
            "full_profile_whole_aircraft_runner": 5,
        }
    )
    if kinds != expected_kinds:
        raise ValueError(f"unexpected audit route kinds: {dict(kinds)}")


def markdown(value: dict[str, Any]) -> str:
    summary = value["summary"]
    lines = [
        "# Current Model Import Divergence Audit",
        "",
        "This audit records source-to-project textual facts before the Sunray150 refactor. It is not a MWORKS, simulation, code-generation, or Gazebo acceptance record.",
        "",
        f"- Routes: {summary['route_count']} = {summary['graphical_controller_core_count']} graphical cores + {summary['full_profile_whole_aircraft_runner_count']} full-profile Runners.",
        f"- Current-map hash drift routes: {summary['current_map_hash_drift_route_count']}.",
        "",
        "| Route | Kind | Comparison | Categories | Model check | Simulation | Adapter review | Codegen review |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in value["routes"]:
        flags = row["revalidation"]
        categories = ", ".join(row["delta"]["category_counts"].keys()) or "none"
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} | {} | {} | {} |".format(
                row["scheme_id"],
                row["kind"],
                row["comparison_state"],
                markdown_escape(categories),
                str(flags["requires_fresh_model_check"]).lower(),
                str(flags["requires_fresh_simulation"]).lower(),
                str(flags["requires_adapter_boundary_review"]).lower(),
                str(flags["requires_fresh_codegen_review"]).lower(),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed audit outputs match current source facts")
    args = parser.parse_args()
    try:
        value = build_audit()
        validate(value)
        json_text = canonical_json(value)
        md_text = markdown(value)
        if args.check:
            if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
                raise ValueError("audit outputs are missing")
            if OUTPUT_JSON.read_text(encoding="utf-8") != json_text:
                raise ValueError("JSON audit is stale")
            if OUTPUT_MD.read_text(encoding="utf-8") != md_text:
                raise ValueError("Markdown audit is stale")
            print(f"PASS {repo_path(OUTPUT_JSON)}")
            return 0
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_JSON.write_text(json_text, encoding="utf-8")
        OUTPUT_MD.write_text(md_text, encoding="utf-8")
        print(f"WROTE {repo_path(OUTPUT_JSON)}")
        return 0
    except Exception as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
