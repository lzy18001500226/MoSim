"""Generate the Golden-closure deletion inventory and frozen-layout proposal.

This is a static analysis tool. It reads the already-approved ordinary closure
and the strong-only closure; it does not alter Modelica sources, package.order,
configuration, calibration, or MWORKS state.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT_PATH = REPO_ROOT / "Models" / "MoSimQuadrotorModel"
RESULT_ROOT = REPO_ROOT / "Results" / "model_library_refactor"
CLOSURE_DIR = RESULT_ROOT / "20260811_golden_closure"
BASELINE_PATH = CLOSURE_DIR / "GOLDEN_CLOSURE.json"
STRONG_PATH = CLOSURE_DIR / "GOLDEN_CLOSURE_STRONG.json"
OUTPUT_DIR = RESULT_ROOT / "20260811_deletion_plan"
DELETION_OUTPUT = OUTPUT_DIR / "DELETION_CANDIDATES.md"
LAYOUT_OUTPUT = OUTPUT_DIR / "TARGET_LAYOUT.md"

ROOT_FQN = "MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner"
EXPECTED_BASELINE_OUTSIDE_FILES = 490
SKIP_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}
SKIP_SUFFIXES = {
    ".7z",
    ".bin",
    ".dll",
    ".doc",
    ".docx",
    ".exe",
    ".gif",
    ".jpg",
    ".jpeg",
    ".msr",
    ".pdf",
    ".png",
    ".pyc",
    ".pyd",
    ".so",
    ".zip",
}
MAX_TEXT_BYTES = 8 * 1024 * 1024

sys.path.insert(0, str(Path(__file__).resolve().parent))
from golden_closure import (  # noqa: E402
    build_index,
    classified_edges,
    file_base,
    resolve,
)


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_text_files(root: Path, suffixes: set[str] | None = None) -> Iterable[Path]:
    """Walk one explicit root only; never walk the whole repository."""

    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        for filename in sorted(filenames):
            path = Path(dirpath) / filename
            if suffixes is not None and path.suffix.lower() not in suffixes:
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_TEXT_BYTES:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "\0" not in text:
                yield path


def make_fqn_pattern(fqns: Iterable[str]) -> re.Pattern[str]:
    ordered = sorted(set(fqns), key=lambda value: (-len(value), value))
    escaped = "|".join(re.escape(fqn) for fqn in ordered)
    return re.compile(r"(?<![A-Za-z0-9_.])(" + escaped + r")(?![A-Za-z0-9_.])")


def literal_reference_index(
    pattern: re.Pattern[str],
    roots: dict[str, tuple[Path, set[str] | None]],
) -> dict[str, dict[str, list[dict[str, object]]]]:
    """Return FQN -> source area -> literal textual references with line numbers."""

    found: dict[str, dict[str, list[dict[str, object]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for area, (root, suffixes) in roots.items():
        for path in iter_text_files(root, suffixes):
            rel = norm(path.relative_to(REPO_ROOT))
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line_number, line in enumerate(lines, start=1):
                for match in pattern.finditer(line):
                    found[match.group(1)][area].append(
                        {"path": rel, "line": line_number, "fqn": match.group(1)}
                    )
    return found


def package_order_actions(
    fqn_to_file: dict[str, str], candidate_files: set[str]
) -> dict[str, list[dict[str, object]]]:
    """Find exact package.order lines that must change if a candidate is deleted."""

    package_to_fqn: dict[str, str] = {}
    for fqn, path in fqn_to_file.items():
        if not path.endswith("/package.mo"):
            continue
        directory = Path(path).parent.name
        if fqn.rsplit(".", maxsplit=1)[-1] == directory:
            package_to_fqn[path] = fqn

    actions: dict[str, list[dict[str, object]]] = defaultdict(list)
    for order_path in MODEL_ROOT_PATH.rglob("package.order"):
        package_path = norm(order_path.parent.relative_to(REPO_ROOT) / "package.mo")
        parent_fqn = package_to_fqn.get(package_path)
        if parent_fqn is None:
            continue
        for line_number, raw in enumerate(
            order_path.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            item = raw.strip()
            if not item or item.startswith("#"):
                continue
            target = resolve(f"{parent_fqn}.{item}", fqn_to_file)
            if target is None:
                continue
            target_file = fqn_to_file[target]
            if target_file in candidate_files:
                actions[target_file].append(
                    {
                        "path": norm(order_path.relative_to(REPO_ROOT)),
                        "line": line_number,
                        "item": item,
                        "fqn": target,
                    }
                )
    return actions


def strong_inbound_index(
    edges: list[dict[str, str]],
    fqn_to_file: dict[str, str],
    candidate_files: set[str],
    strong_files: set[str],
) -> dict[str, list[dict[str, object]]]:
    """Keep only real model edges for classification; weak navigation stays reported."""

    inbound: dict[str, list[dict[str, object]]] = defaultdict(list)
    for edge in edges:
        target_file = fqn_to_file.get(edge["target"])
        source_file = fqn_to_file.get(edge["source"])
        if target_file not in candidate_files or source_file is None:
            continue
        if source_file in candidate_files:
            source_scope = "baseline_outside"
        elif source_file in strong_files:
            source_scope = "strong_closure"
        else:
            source_scope = "baseline_retained_or_weak_only"
        inbound[target_file].append(
            {
                "source_fqn": edge["source"],
                "source_file": source_file,
                "target_fqn": edge["target"],
                "strength": edge["strength"],
                "kind": edge["kind"],
                "source_scope": source_scope,
            }
        )
    return inbound


def strongly_connected_components(
    nodes: set[str], edges: dict[str, set[str]]
) -> list[set[str]]:
    """Tarjan SCCs over candidate files using strong Modelica references only."""

    next_index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[set[str]] = []

    def visit(node: str) -> None:
        nonlocal next_index
        indices[node] = next_index
        lowlink[node] = next_index
        next_index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(edges.get(node, set())):
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] != indices[node]:
            return
        component: set[str] = set()
        while True:
            target = stack.pop()
            on_stack.remove(target)
            component.add(target)
            if target == node:
                break
        components.append(component)

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return components


def compact_references(records: list[dict[str, object]]) -> str:
    if not records:
        return "none"
    unique = {
        (str(record["path"]), int(record["line"]), str(record["fqn"]))
        for record in records
    }
    return "; ".join(
        f"`{path}:L{line}` `{fqn}`" for path, line, fqn in sorted(unique)
    )


def compact_model_edges(records: list[dict[str, object]]) -> str:
    if not records:
        return "none"
    unique = {
        (
            str(record["source_file"]),
            str(record["source_fqn"]),
            str(record["strength"]),
            str(record["kind"]),
            str(record["source_scope"]),
        )
        for record in records
    }
    return "; ".join(
        f"`{path}` `{fqn}` ({strength}/{kind}/{scope})"
        for path, fqn, strength, kind, scope in sorted(unique)
    )


def compact_actions(actions: list[dict[str, object]]) -> str:
    if not actions:
        return "none"
    return "; ".join(
        f"remove `{action['path']}:L{action['line']}` item `{action['item']}`"
        for action in sorted(actions, key=lambda value: (value["path"], value["line"]))
    )


def render_tree(fqns: Iterable[str]) -> list[str]:
    tree: dict[str, dict[str, object]] = {}
    for fqn in sorted(fqns):
        node = tree
        for part in fqn.split(".")[1:]:
            node = node.setdefault(part, {})  # type: ignore[assignment]

    lines: list[str] = ["MoSimQuadrotorModel"]

    def add_children(node: dict[str, dict[str, object]], prefix: str) -> None:
        children = sorted(node)
        for index, name in enumerate(children):
            last = index == len(children) - 1
            lines.append(prefix + ("`-- " if last else "|-- ") + name)
            add_children(node[name], prefix + ("    " if last else "|   "))

    add_children(tree, "")
    return lines


def write_deletion_plan(
    candidates: list[dict[str, object]],
    baseline: dict[str, object],
    strong: dict[str, object],
) -> None:
    counts: dict[str, int] = defaultdict(int)
    for candidate in candidates:
        counts[str(candidate["tier"])] += 1
    if sum(counts.values()) != EXPECTED_BASELINE_OUTSIDE_FILES:
        raise RuntimeError("candidate tier counts do not equal the required 490 files")

    lines = [
        "# Golden Closure Deletion Candidates",
        "",
        "Status: analysis only. This document does not authorize deletion, moves, package.order edits, calibration changes, or Git actions.",
        "",
        "## Scope And Counting Rule",
        "",
        f"- Frozen root: `{ROOT_FQN}`",
        f"- Ordinary frozen closure input: {baseline['closure_file_count']} files / {baseline['closure_class_count']} classes.",
        f"- Strong-only closure input: {strong['strong_closure_file_count']} files / {strong['strong_closure_class_count']} classes.",
        "- This H inventory intentionally classifies the ordinary closure's fixed 490 outside files. The 48 weak-only files found by G are reported in the strong-closure JSON and its MWORKS reversible-check packet; they are not silently added here, so the mandated total remains 490.",
        "- Literal reference scans are restricted to Models, Config, Scripts, and src. Modelica category decisions use classified strong edges; package.order maintenance is shown as a related edit, not as a strong dependency.",
        "",
        "| Tier | Meaning | File count |",
        "|---|---|---:|",
        f"| A | Direct candidate: no Config/Scripts/src literal FQN pin and no inbound strong edge from another baseline-outside file. | {counts['A']} |",
        f"| B | Configuration-coupled candidate: one or more Config/Scripts/src literal FQN pins. | {counts['B']} |",
        f"| C | Cluster candidate: member of a nontrivial SCC of baseline-outside strong Modelica references. | {counts['C']} |",
        f"| D | Defer: retained/weak-only strong inbound edge or non-cyclic baseline-outside inbound edge requires an ordered review. | {counts['D']} |",
        f"| Total | Fixed ordinary-closure outside population. | {sum(counts.values())} |",
        "",
        "## Candidates",
        "",
    ]
    for tier in ("A", "B", "C", "D"):
        lines.extend([f"## Tier {tier}", ""])
        tier_candidates = [candidate for candidate in candidates if candidate["tier"] == tier]
        if not tier_candidates:
            lines.extend(["No files meet this tier's definition.", ""])
            continue
        for index, candidate in enumerate(tier_candidates, start=1):
            lines.extend(
                [
                    f"### {tier}-{index:03d} `{candidate['file']}`",
                    "",
                    f"- Class FQN(s): {', '.join(f'`{fqn}`' for fqn in candidate['fqns'])}",
                    "- Inbound detail:",
                    f"  - Models: {candidate['models_text']}",
                    f"  - Config: {candidate['config_text']}",
                    f"  - Scripts: {candidate['scripts_text']}",
                    f"  - src: {candidate['src_text']}",
                    f"- Strong Modelica inbound edges: {candidate['strong_edges_text']}",
                    f"- Tier basis: {candidate['basis']}",
                    f"- Coupled changes required before a deletion: {candidate['actions_text']}",
                    "",
                ]
            )
    DELETION_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_layout_plan(
    strong: dict[str, object],
    fqn_to_file: dict[str, str],
    literal_refs: dict[str, dict[str, list[dict[str, object]]]],
) -> None:
    fqns = sorted(strong["closure_classes"])
    files = sorted(strong["closure_files"])
    lines = [
        "# Target Layout Proposal For The Strong Golden Closure",
        "",
        "Status: proposal only. No file move, FQN change, package split, Environment domain, or Experiment.Runners removal is authorized by this document.",
        "",
        "## Frozen Scope",
        "",
        f"- Frozen root: `{ROOT_FQN}`",
        f"- Included only: {len(files)} strong-closure files and {len(fqns)} direct strong-closure classes.",
        "- Excluded: every class and file outside that strong closure. No target position is reserved for them.",
        "- `Experiment.Runners` remains. The frozen root and every FQN reached by it remain unchanged.",
        "- No `Environment` domain is introduced.",
        "",
        "## Logical Depth Rule",
        "",
        "The post-freeze physical convention is exactly three directory levels below `Models/MoSimQuadrotorModel`: `Domain/Family/Leaf.mo`. This makes ownership visible without the current 2-5 level variation. It is a future rule only: applying it now would change a frozen FQN or require splitting embedded classes, so this proposal records no approved migration.",
        "",
        "## Strong Closure View",
        "",
        "```text",
        *render_tree(fqns),
        "```",
        "",
        "## FQN Move Prevention Ledger",
        "",
        "Every row is intentionally `do not move`. The before and after FQNs are equal because a changed FQN would alter the frozen baseline or one of its required dependencies. Config/Scripts figures are exact literal-reference line counts from the bounded scan, not a runtime acceptance claim.",
        "",
        "| Current FQN | Source file | Proposed FQN | Config refs | Scripts refs | Decision |",
        "|---|---|---|---:|---:|---|",
    ]
    for fqn in fqns:
        refs = literal_refs.get(fqn, {})
        lines.append(
            "| "
            + f"`{fqn}` | `{fqn_to_file[fqn]}` | `{fqn}` | "
            + f"{len(refs.get('Config', []))} | {len(refs.get('Scripts', []))} | do not move: frozen-closure FQN |"
        )
    lines.extend(
        [
            "",
            "## Non-Migration Constraints",
            "",
            "- Do not split embedded classes as part of this proposal.",
            "- Do not add imports to Graphical/PID/OfficialPidCoreSysblock.mo; it remains a closure-out deletion candidate under the H inventory.",
            "- Any future physical move needs a new approved closure, explicit FQN migration map, and a fresh MWORKS check. This document makes no such change.",
            "",
        ]
    )
    LAYOUT_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    os.chdir(REPO_ROOT)
    baseline = read_json(BASELINE_PATH)
    strong = read_json(STRONG_PATH)
    if baseline["root"] != ROOT_FQN or strong["root"] != ROOT_FQN:
        raise RuntimeError("closure artifact root does not match the frozen runner")
    candidate_files = set(baseline["outside_files"])
    if len(candidate_files) != EXPECTED_BASELINE_OUTSIDE_FILES:
        raise RuntimeError("ordinary closure outside-file count is not the required 490")
    if len(set(strong["closure_files"])) != int(strong["strong_closure_file_count"]):
        raise RuntimeError("strong closure file list/count mismatch")

    fqn_to_file, file_text = build_index()
    if len(file_text) != int(baseline["indexed_file_count"]):
        raise RuntimeError("model file index no longer matches the frozen baseline")
    if len(fqn_to_file) != int(baseline["indexed_class_count"]):
        raise RuntimeError("class index no longer matches the frozen baseline")

    candidate_fqns_by_file: dict[str, list[str]] = defaultdict(list)
    for fqn, path in fqn_to_file.items():
        if path in candidate_files:
            candidate_fqns_by_file[path].append(fqn)
    missing_fqns = sorted(candidate_files - set(candidate_fqns_by_file))
    if missing_fqns:
        raise RuntimeError("candidate files have no indexed FQN: " + ", ".join(missing_fqns))

    strong_files = set(strong["closure_files"])
    all_scanned_fqns = set(fqn_to_file)
    literal_refs = literal_reference_index(
        make_fqn_pattern(all_scanned_fqns),
        {
            "Models": (MODEL_ROOT_PATH, {".mo"}),
            "Config": (REPO_ROOT / "Config", None),
            "Scripts": (REPO_ROOT / "Scripts", None),
            "src": (REPO_ROOT / "src", None),
        },
    )
    edges, _unresolved = classified_edges(fqn_to_file, file_text)
    inbound_edges = strong_inbound_index(edges, fqn_to_file, candidate_files, strong_files)
    order_actions = package_order_actions(fqn_to_file, candidate_files)

    adjacency: dict[str, set[str]] = defaultdict(set)
    for target_file, records in inbound_edges.items():
        for record in records:
            if record["strength"] != "strong":
                continue
            source_file = str(record["source_file"])
            if source_file in candidate_files and source_file != target_file:
                adjacency[source_file].add(target_file)
    components = strongly_connected_components(candidate_files, adjacency)
    cluster_for_file: dict[str, set[str]] = {}
    for component in components:
        has_self_loop = any(node in adjacency.get(node, set()) for node in component)
        if len(component) > 1 or has_self_loop:
            for member in component:
                cluster_for_file[member] = component

    candidates: list[dict[str, object]] = []
    for path in sorted(candidate_files):
        fqns = sorted(candidate_fqns_by_file[path])
        area_refs: dict[str, list[dict[str, object]]] = defaultdict(list)
        for fqn in fqns:
            for area, records in literal_refs.get(fqn, {}).items():
                area_refs[area].extend(record for record in records if record["path"] != path)
        model_edges = inbound_edges.get(path, [])
        external_refs = area_refs["Config"] + area_refs["Scripts"] + area_refs["src"]
        outside_inbound = [
            record
            for record in model_edges
            if record["strength"] == "strong"
            and record["source_scope"] == "baseline_outside"
            and record["source_file"] != path
        ]
        retained_inbound = [
            record
            for record in model_edges
            if record["strength"] == "strong"
            and record["source_scope"] != "baseline_outside"
        ]
        if external_refs:
            tier = "B"
            basis = "literal FQN pin outside Models requires a synchronized Config/Scripts/src edit"
        elif path in cluster_for_file:
            tier = "C"
            members = ", ".join(f"`{member}`" for member in sorted(cluster_for_file[path]))
            basis = "nontrivial strong-reference SCC; delete only as the cluster: " + members
        elif outside_inbound:
            tier = "D"
            basis = "strong inbound reference from another baseline-outside file is not a mutual SCC; review deletion order"
        elif retained_inbound:
            tier = "D"
            basis = "strong inbound reference from a retained or weak-only baseline file; do not delete without a new closure review"
        else:
            tier = "A"
            basis = "no external literal pin and no inbound strong edge from another baseline-outside file"

        actions = list(order_actions.get(path, []))
        for record in area_refs["Config"] + area_refs["Scripts"] + area_refs["src"]:
            actions.append(
                {
                    "path": record["path"],
                    "line": record["line"],
                    "item": record["fqn"],
                    "fqn": record["fqn"],
                }
            )
        candidates.append(
            {
                "tier": tier,
                "file": path,
                "fqns": fqns,
                "models_text": compact_references(area_refs["Models"]),
                "config_text": compact_references(area_refs["Config"]),
                "scripts_text": compact_references(area_refs["Scripts"]),
                "src_text": compact_references(area_refs["src"]),
                "strong_edges_text": compact_model_edges(model_edges),
                "basis": basis,
                "actions_text": compact_actions(actions),
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_deletion_plan(candidates, baseline, strong)
    write_layout_plan(strong, fqn_to_file, literal_refs)
    counts: dict[str, int] = defaultdict(int)
    for candidate in candidates:
        counts[str(candidate["tier"])] += 1
    print("candidate files:", len(candidates))
    print("tiers:", dict(sorted(counts.items())))
    print("strong files:", len(strong_files))
    print("wrote:", norm(DELETION_OUTPUT.relative_to(REPO_ROOT)))
    print("wrote:", norm(LAYOUT_OUTPUT.relative_to(REPO_ROOT)))


if __name__ == "__main__":
    main()
