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
    TEMPLATES_ORDER_PATH,
    INVENTORY_PATH,
    MappingError,
    approved_graphical_import_variant,
    expected_fixed_integrated_alias_text,
    expected_import_text,
    direct_graphical_native_equivalence_mode,
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


def write_new_or_identical(
    path: Path, expected: str, apply: bool, item: dict[str, object] | None = None
) -> str:
    if path.is_file():
        current = path.read_text(encoding="utf-8")
        equivalence = import_equivalence_mode(current, expected)
        if equivalence is None:
            if item is not None:
                native_mode = direct_graphical_native_equivalence_mode(item, path)
                if native_mode is not None:
                    return native_mode
                if approved_graphical_import_variant(item, path, expected) is not None:
                    return "approved_project_variant"
                # A prior G5 checker version accidentally used its topology
                # whitespace normalizer when writing generated imports. Accept
                # only that exact whitespace-only state here so --apply can
                # restore the source-derived visual layout without accepting
                # any declaration, port, equation, or annotation change.
                if indentation_only_import_equivalence(current, expected):
                    if apply:
                        write_utf8_lf(path, expected)
                    return "restored_from_topology_whitespace_only_import"
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


def indentation_only_import_equivalence(current: str, expected: str) -> bool:
    """Detect a generated import that differs solely in non-semantic layout whitespace."""

    def normalize(text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip(" \t") for line in text.split("\n")]
        return "\n".join(line for line in lines if line)

    return normalize(current) == normalize(expected)


def ensure_integrated_chains_package_slot(apply: bool) -> str:
    """Ensure the fixed-chain package is registered under Experiment.Templates."""

    if not TEMPLATES_ORDER_PATH.is_file():
        raise MappingError(f"Experiment templates order is missing: {repo_path(TEMPLATES_ORDER_PATH)}")
    entries = TEMPLATES_ORDER_PATH.read_text(encoding="utf-8").splitlines()
    if "IntegratedChains" in entries:
        return "unchanged"
    if not apply:
        return "missing"
    entries.append("IntegratedChains")
    write_utf8_lf(TEMPLATES_ORDER_PATH, "\n".join(entries) + "\n")
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
    if path.name == "package.order":
        current_entries = [entry for entry in current.splitlines() if entry]
        expected_entries = [entry for entry in expected.splitlines() if entry]
        # A G5 direct-graphical batch may add new model names to an existing
        # handoff package order. Treat it as a safe predecessor only when it
        # contains no duplicate or unknown entry. This permits canonicalizing
        # a verified additive prefix while still refusing to erase an
        # unrecognized user or executable model name.
        if (
            len(current_entries) == len(set(current_entries))
            and all(entry in expected_entries for entry in current_entries)
        ):
            if not apply:
                return "requires_known_additive_package_order_update"
            write_utf8_lf(path, expected)
            return "updated_from_known_additive_package_order"
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


def select_primary_plan(
    full_plan: list[dict[str, object]], scheme_ids: list[str] | None
) -> list[dict[str, object]]:
    """Return a validated primary-model subset for a narrowly scoped import.

    G5 batches may add a few direct graphical replacements while older,
    already-reviewed imports have MWORKS-native serialization differences.  A
    scoped import must never turn those unrelated files into an overwrite or
    check precondition for the new batch.
    """

    if not scheme_ids:
        return full_plan
    requested = set(scheme_ids)
    known = {str(item["scheme_id"]) for item in full_plan}
    unknown = sorted(requested - known)
    if unknown:
        raise MappingError(f"Unknown graphical primary scheme ID(s): {', '.join(unknown)}")
    return [item for item in full_plan if str(item["scheme_id"]) in requested]


def select_support_plan(
    full_support_plan: list[dict[str, object]], support_ids: list[str] | None
) -> list[dict[str, object]]:
    """Select named support imports without broadening a bounded G5 repair."""

    if not support_ids:
        return []
    requested = set(support_ids)
    known = {str(item["support_id"]) for item in full_support_plan}
    unknown = sorted(requested - known)
    if unknown:
        raise MappingError(f"Unknown graphical support ID(s): {', '.join(unknown)}")
    return [item for item in full_support_plan if str(item["support_id"]) in requested]


def run(
    apply: bool,
    check: bool = False,
    scheme_ids: list[str] | None = None,
    support_ids: list[str] | None = None,
) -> dict[str, object]:
    catalog = read_json(CATALOG_PATH)
    inventory = read_json(INVENTORY_PATH)
    full_plan = import_plan(catalog, inventory)
    selected_support = select_support_plan(support_import_plan(), support_ids)
    # A support-only repair must not unexpectedly import every primary model.
    plan = [] if support_ids and not scheme_ids else select_primary_plan(full_plan, scheme_ids)
    scoped_import = bool(scheme_ids or support_ids)
    full_support_plan = support_import_plan()
    # A scoped G5 repair remains limited to its named primary cores, but it
    # must carry any formal shared component those cores instantiate.  Without
    # that dependency the generated wrapper can load while CheckModel fails.
    requested_scheme_ids = set(scheme_ids or [])
    requested_scheme_ids.update(
        scheme_id
        for item in selected_support
        for scheme_id in item["required_by_scheme_ids"]
    )
    support_plan = (
        [
            item
            for item in full_support_plan
            if (
                requested_scheme_ids.intersection(item["required_by_scheme_ids"])
                or str(item["support_id"]) in set(support_ids or [])
            )
        ]
        if scoped_import
        else full_support_plan
    )
    fixed_plan = [] if scoped_import else fixed_integrated_alias_plan()
    statuses: dict[str, str] = {}
    if not scoped_import:
        statuses[repo_path(TEMPLATES_ORDER_PATH)] = ensure_integrated_chains_package_slot(apply)
    previous_package_candidates = predecessor_package_file_texts(full_plan, full_support_plan)
    expected_package_files = package_file_texts(full_plan, full_support_plan)
    if scoped_import:
        scoped_package_orders = {
            Path(item["target_file"]).parent / "package.order"
            for item in [*plan, *support_plan]
        }
        expected_package_files = {
            path: expected
            for path, expected in expected_package_files.items()
            if path in scoped_package_orders
        }
    for path, expected in expected_package_files.items():
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
        statuses[repo_path(target)] = write_new_or_identical(
            target, expected_import_text(item), apply, item
        )
    if fixed_plan:
        for path, expected in fixed_integrated_package_file_texts(fixed_plan).items():
            statuses[repo_path(path)] = write_new_or_identical(path, expected, apply)
        for item in fixed_plan:
            target = item["target_file"]
            statuses[repo_path(target)] = write_new_or_identical(
                target, expected_fixed_integrated_alias_text(item), apply
            )
    errors = verify_imported_files(
        plan,
        support_plan=support_plan,
        fixed_plan=fixed_plan,
        expected_package_files=expected_package_files,
        require_control_order=not scoped_import,
    )
    if check:
        accepted_native_serialization = {
            "unchanged",
            "exact_source_copy_or_sysplorer_whitespace_only",
            # G5 layout repair is accepted by the source-integrity checker but
            # remains subject to the separate native graphical-review gate.
            "g5_visual_metadata_only",
            "audited_sysplorer_native_direct_graphical_serialization",
            "approved_project_variant",
        }
        errors.extend(
            f"Generated import needs canonicalization or repair: {path} ({status})"
            for path, status in sorted(statuses.items())
            if status not in accepted_native_serialization
        )
    return {
        "schema": "mosim.g4.graphical_mil_import.v1",
        "ok": not errors,
        "apply": apply,
        "check": check,
        "scope_scheme_ids": sorted(scheme_ids) if scheme_ids else None,
        "scope_support_ids": sorted(support_ids) if support_ids else None,
        "available_primary_import_count": len(full_plan),
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
    parser.add_argument(
        "--scheme-id",
        action="append",
        metavar="SCHEME_ID",
        help=(
            "Limit model writes and verification to one primary scheme. May be repeated; "
            "only the affected family package.order is updated."
        ),
    )
    parser.add_argument(
        "--support-id",
        action="append",
        metavar="SUPPORT_ID",
        help=(
            "Limit model writes and verification to one named graphical support import. "
            "May be repeated; this never imports unrelated primary controller cores."
        ),
    )
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    if args.apply and args.check:
        parser.error("--apply and --check are mutually exclusive")
    try:
        report = run(args.apply, args.check, args.scheme_id, args.support_id)
    except Exception as exc:
        report = {
            "schema": "mosim.g4.graphical_mil_import.v1",
            "ok": False,
            "apply": args.apply,
            "check": args.check,
            "scope_scheme_ids": sorted(args.scheme_id) if args.scheme_id else None,
            "scope_support_ids": sorted(args.support_id) if args.support_id else None,
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
