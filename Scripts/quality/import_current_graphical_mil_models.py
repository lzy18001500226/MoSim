#!/usr/bin/env python3
"""Create or verify G4's non-destructive graphical MIL import package.

Use ``--apply`` only after reviewing the static plan.  The command writes new
package-context copies below Models and refuses to overwrite a different file.
It never moves, deletes, or changes a source model below Results or Models.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import (
    CATALOG_PATH,
    CONTROLLERS_ORDER_PATH,
    INVENTORY_PATH,
    MappingError,
    expected_fixed_integrated_alias_text,
    expected_import_text,
    fixed_integrated_alias_plan,
    fixed_integrated_package_file_texts,
    import_equivalence_mode,
    import_plan,
    package_file_texts,
    read_json,
    repo_path,
    support_import_plan,
    verify_imported_files,
    write_utf8_lf,
)


def write_new_or_identical(path: Path, expected: str, apply: bool) -> str:
    if path.is_file():
        current = path.read_text(encoding="utf-8")
        equivalence = import_equivalence_mode(current, expected)
        if equivalence is None:
            raise MappingError(f"Refusing to overwrite non-identical current model file: {repo_path(path)}")
        if apply and equivalence == "exact_source_copy_or_sysplorer_whitespace_only" and current != expected:
            write_utf8_lf(path, expected)
            return "canonicalized_generated_whitespace"
        return "unchanged" if current == expected else equivalence
    if not apply:
        return "missing"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_utf8_lf(path, expected)
    return "created"


def ensure_integrated_chains_package_slot(apply: bool) -> str:
    """Add the generated fixed-chain package next to GraphicalMIL exactly once."""

    if not CONTROLLERS_ORDER_PATH.is_file():
        raise MappingError(f"Controllers package order is missing: {repo_path(CONTROLLERS_ORDER_PATH)}")
    entries = CONTROLLERS_ORDER_PATH.read_text(encoding="utf-8").splitlines()
    if "IntegratedChains" in entries:
        return "unchanged"
    if "GraphicalMIL" not in entries:
        raise MappingError("Controllers/package.order must contain GraphicalMIL before adding IntegratedChains")
    if not apply:
        return "missing"
    entries.insert(entries.index("GraphicalMIL") + 1, "IntegratedChains")
    write_utf8_lf(CONTROLLERS_ORDER_PATH, "\n".join(entries) + "\n")
    return "created"


def write_generated_package_file(
    path: Path, expected: str, previous_generated: set[str], apply: bool
) -> str:
    """Update generated package metadata only from a known prior state.

    A support dependency can legitimately change ``package.order``.  This is
    deliberately narrower than a generic overwrite: the existing file must
    either already equal the new deterministic content or exactly match the
    preceding deterministic package output. A later G4 support import may add
    one dependency after an earlier support import has already been accepted,
    so every strict known predecessor support set is accepted here.
    """

    if not path.is_file():
        if not apply:
            return "missing"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_utf8_lf(path, expected)
        return "created"
    current = path.read_text(encoding="utf-8")
    if current == expected:
        return "unchanged"
    if current in previous_generated:
        if not apply:
            return "requires_known_generated_metadata_update"
        write_utf8_lf(path, expected)
        return "updated_from_known_generated_metadata"
    raise MappingError(f"Refusing to overwrite non-generated package metadata: {repo_path(path)}")


def predecessor_package_file_texts(
    plan: list[dict[str, object]], support_plan: list[dict[str, object]]
) -> list[dict[Path, str]]:
    """Return every strict deterministic predecessor package state.

    Package metadata is allowed to advance only from a previous generated
    support subset. This permits additive dependency repair while refusing
    package files with an unknown origin.
    """

    return [
        package_file_texts(plan, list(subset))
        for size in range(len(support_plan))
        for subset in combinations(support_plan, size)
    ]


def run(apply: bool, check: bool = False) -> dict[str, object]:
    catalog = read_json(CATALOG_PATH)
    inventory = read_json(INVENTORY_PATH)
    plan = import_plan(catalog, inventory)
    support_plan = support_import_plan()
    fixed_plan = fixed_integrated_alias_plan()
    statuses: dict[str, str] = {}
    statuses[repo_path(CONTROLLERS_ORDER_PATH)] = ensure_integrated_chains_package_slot(apply)
    previous_package_candidates = predecessor_package_file_texts(plan, support_plan)
    for path, expected in package_file_texts(plan, support_plan).items():
        previous_generated = {
            candidate[path]
            for candidate in previous_package_candidates
            if path in candidate
        }
        statuses[repo_path(path)] = write_generated_package_file(
            path, expected, previous_generated, apply
        )
    for item in [*support_plan, *plan]:
        target = item["target_file"]
        statuses[repo_path(target)] = write_new_or_identical(target, expected_import_text(item), apply)
    for path, expected in fixed_integrated_package_file_texts(fixed_plan).items():
        statuses[repo_path(path)] = write_new_or_identical(path, expected, apply)
    for item in fixed_plan:
        target = item["target_file"]
        statuses[repo_path(target)] = write_new_or_identical(target, expected_fixed_integrated_alias_text(item), apply)
    errors = verify_imported_files(plan)
    if check:
        errors.extend(
            f"Generated import needs canonicalization or repair: {path} ({status})"
            for path, status in sorted(statuses.items())
            if status != "unchanged"
        )
    return {
        "schema": "mosim.g4.graphical_mil_import.v1",
        "ok": not errors,
        "apply": apply,
        "check": check,
        "primary_import_count": len(plan),
        "support_import_count": len(support_plan),
        "fixed_integrated_alias_count": len(fixed_plan),
        "import_count": len(plan) + len(support_plan),
        "file_statuses": statuses,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Create missing exact copies; refuse non-identical overwrite.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Require every generated import and package file to be present and canonical without writing files.",
    )
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    if args.apply and args.check:
        parser.error("--apply and --check are mutually exclusive")
    try:
        report = run(args.apply, args.check)
    except Exception as exc:
        report = {
            "schema": "mosim.g4.graphical_mil_import.v1",
            "ok": False,
            "apply": args.apply,
            "check": args.check,
            "errors": [str(exc)],
        }
    if args.output_json:
        output = args.output_json if args.output_json.is_absolute() else Path.cwd() / args.output_json
        output.parent.mkdir(parents=True, exist_ok=True)
        write_utf8_lf(output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
