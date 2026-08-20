"""Compute the transitive class closure reachable from a Modelica root class.

Purpose: the Golden runner is the frozen deliverable baseline. Anything outside
its dependency closure is a deletion candidate. This script produces that
closure so the candidate list rests on reachability, not on simulation history.

Usage:
    python golden_closure.py [--root FQN] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import deque
from dataclasses import dataclass

MODEL_ROOT = "Models/MoSimQuadrotorModel"
LIB_PREFIX = "MoSimQuadrotorModel"
DEFAULT_ROOT = "MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner"

CLASS_KINDS = r"(?:model|block|function|record|package|connector|type|partial\s+model|partial\s+block)"
WITHIN_RE = re.compile(r"^\s*within\s+([\w.]+)\s*;", re.M)
DEF_RE = re.compile(r"^\s*" + CLASS_KINDS + r"\s+([A-Z]\w*)", re.M)
# Any dotted reference into the library, e.g. MoSimQuadrotorModel.Control.Foo.Bar
REF_RE = re.compile(r"\b" + LIB_PREFIX + r"(?:\.[A-Za-z_]\w*)+")
EXTENDS_RE = re.compile(r"^\s*extends\s+([\w.]+)", re.M)
IMPORT_RE = re.compile(r"^\s*import\s+(?:\w+\s*=\s*)?([\w.]+)", re.M)
CLASS_START_RE = re.compile(
    r"^\s*((?:partial\s+)?(?:model|block|function|record|package|connector))\s+([A-Za-z_]\w*)\b"
)
CLASS_END_RE = re.compile(r"^\s*end\s+([A-Za-z_]\w*)\s*;")
COMPONENT_REF_RE = re.compile(
    r"^\s*(" + LIB_PREFIX + r"(?:\.[A-Za-z_]\w*)+)\s+[A-Za-z_]\w*\b",
    re.M,
)


def norm(path: str) -> str:
    return path.replace(os.sep, "/")


def build_index() -> tuple[dict[str, str], dict[str, str]]:
    """Return (fqn -> file) and (file -> text) for every class in the library."""
    fqn_to_file: dict[str, str] = {}
    file_text: dict[str, str] = {}

    for dirpath, _dirnames, filenames in os.walk(MODEL_ROOT):
        for name in filenames:
            if not name.endswith(".mo"):
                continue
            path = norm(os.path.join(dirpath, name))
            text = open(path, encoding="utf-8", errors="replace").read()
            file_text[path] = text

            within = WITHIN_RE.search(text)
            pkg = within.group(1) if within else None

            if name == "package.mo":
                leaf = os.path.basename(dirpath)
                base = f"{pkg}.{leaf}" if pkg else LIB_PREFIX
            else:
                stem = name[:-3]
                base = f"{pkg}.{stem}" if pkg else stem

            fqn_to_file.setdefault(base, path)

            # Classes embedded inside this file (package.mo carries most of them).
            for match in DEF_RE.finditer(text):
                embedded = match.group(1)
                if embedded == os.path.basename(base):
                    continue
                fqn_to_file.setdefault(f"{base}.{embedded}", path)

    return fqn_to_file, file_text


def refs_in(text: str) -> set[str]:
    """Every library FQN mentioned by this file, from any syntactic position."""
    found = set(REF_RE.findall(text))
    for pattern in (EXTENDS_RE, IMPORT_RE):
        for match in pattern.finditer(text):
            target = match.group(1)
            if target.startswith(LIB_PREFIX):
                found.add(target)
    return found


@dataclass(eq=False)
class ClassNode:
    fqn: str
    path: str
    kind: str
    start_line: int
    end_line: int | None = None
    parent: "ClassNode | None" = None


def file_base(path: str, text: str) -> str:
    """Return the legacy index's canonical FQN for one Modelica source file."""

    within = WITHIN_RE.search(text)
    package = within.group(1) if within else None
    if os.path.basename(path) == "package.mo":
        leaf = os.path.basename(os.path.dirname(path))
        return f"{package}.{leaf}" if package else LIB_PREFIX
    stem = os.path.basename(path)[:-3]
    return f"{package}.{stem}" if package else stem


def class_nodes(
    fqn_to_file: dict[str, str], file_text: dict[str, str]
) -> dict[str, ClassNode]:
    """Parse class spans so a package file does not donate all child refs."""

    parsed: list[ClassNode] = []
    for path, text in file_text.items():
        base = file_base(path, text)
        stack: list[ClassNode] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            declaration = CLASS_START_RE.match(line)
            if declaration:
                name = declaration.group(2)
                if stack:
                    fqn = f"{stack[-1].fqn}.{name}"
                elif name == base.rsplit(".", maxsplit=1)[-1]:
                    fqn = base
                else:
                    within = WITHIN_RE.search(text)
                    prefix = within.group(1) if within else ""
                    fqn = f"{prefix}.{name}" if prefix else name
                node = ClassNode(
                    fqn=fqn,
                    path=path,
                    kind=declaration.group(1),
                    start_line=line_number,
                    parent=stack[-1] if stack else None,
                )
                parsed.append(node)
                stack.append(node)

            ending = CLASS_END_RE.match(line)
            if ending:
                for index in range(len(stack) - 1, -1, -1):
                    if stack[index].fqn.rsplit(".", maxsplit=1)[-1] == ending.group(1):
                        stack[index].end_line = line_number
                        del stack[index:]
                        break

    return {
        node.fqn: node
        for node in parsed
        if node.end_line is not None and node.fqn in fqn_to_file
    }


def node_direct_text(node: ClassNode, nodes: dict[str, ClassNode], file_text: dict[str, str]) -> str:
    """Return a class's own source without direct child definitions."""

    assert node.end_line is not None
    lines = file_text[node.path].splitlines()
    own = list(lines[node.start_line - 1 : node.end_line])
    for child in nodes.values():
        if child.parent is not node or child.end_line is None:
            continue
        start = child.start_line - node.start_line
        end = child.end_line - node.start_line
        own[start : end + 1] = [""] * (end - start + 1)
    return "\n".join(own)


def annotation_spans(text: str) -> list[tuple[int, int]]:
    """Locate balanced Modelica annotation blocks without parsing their payload."""

    spans: list[tuple[int, int]] = []
    for match in re.finditer(r"\bannotation\s*\(", text):
        start = match.start()
        index = match.end() - 1
        depth = 0
        while index < len(text):
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
                if depth == 0:
                    spans.append((start, index + 1))
                    break
            index += 1
    return spans


def without_annotations(text: str) -> str:
    chars = list(text)
    for start, end in annotation_spans(text):
        for index in range(start, end):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def without_comments_and_strings(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return re.sub(r'"(?:\\.|[^"\\])*"', '""', text)


def append_edge(
    edges: dict[tuple[str, str, str, str], dict[str, str]],
    source: str,
    target: str,
    strength: str,
    kind: str,
    source_file: str,
) -> None:
    if source != target:
        edges.setdefault(
            (source, target, strength, kind),
            {
                "source": source,
                "target": target,
                "strength": strength,
                "kind": kind,
                "source_file": source_file,
            },
        )


def classified_edges(
    fqn_to_file: dict[str, str], file_text: dict[str, str]
) -> tuple[list[dict[str, str]], dict[str, list[str]]]:
    """Classify class references without treating package navigation as runtime use."""

    nodes = class_nodes(fqn_to_file, file_text)
    edges: dict[tuple[str, str, str, str], dict[str, str]] = {}
    unresolved: dict[str, set[str]] = {"strong": set(), "weak": set()}

    def add_ref(source: ClassNode, ref: str, strength: str, kind: str) -> None:
        target = resolve(ref, fqn_to_file)
        if target is None:
            unresolved[strength].add(ref)
            return
        append_edge(edges, source.fqn, target, strength, kind, source.path)

    for node in nodes.values():
        direct = node_direct_text(node, nodes, file_text)
        annotations = "\n".join(direct[start:end] for start, end in annotation_spans(direct))
        code = without_comments_and_strings(without_annotations(direct))
        code = re.sub(r"^\s*within\s+[\w.]+\s*;\s*$", "", code, flags=re.M)
        extends = set(EXTENDS_RE.findall(code))
        imports = set(IMPORT_RE.findall(code))
        components = set(COMPONENT_REF_RE.findall(code))
        for ref in set(REF_RE.findall(code)) | extends | imports:
            if not ref.startswith(LIB_PREFIX):
                continue
            if ref in extends:
                add_ref(node, ref, "strong", "extends")
            elif ref in components:
                add_ref(node, ref, "strong", "component_declaration")
            elif ref in imports:
                add_ref(node, ref, "strong", "imported_model_reference")
            else:
                add_ref(node, ref, "strong", "direct_model_reference")
        for ref in REF_RE.findall(annotations):
            add_ref(node, ref, "weak", "annotation_reference")

    for node in nodes.values():
        if not node.path.endswith("/package.mo") or node.fqn != file_base(node.path, file_text[node.path]):
            continue
        order_path = os.path.join(os.path.dirname(node.path), "package.order")
        if not os.path.isfile(order_path):
            continue
        with open(order_path, encoding="utf-8", errors="replace") as handle:
            for raw_name in handle:
                name = raw_name.strip()
                if not name or name.startswith("#"):
                    continue
                add_ref(node, f"{node.fqn}.{name}", "weak", "package_order")

    serializable_unresolved = {
        strength: sorted(values) for strength, values in unresolved.items()
    }
    return sorted(edges.values(), key=lambda edge: (edge["source"], edge["target"], edge["kind"])), serializable_unresolved


def traverse_edges(root: str, fqn_to_file: dict[str, str], edges: list[dict[str, str]], strength: str | None) -> tuple[set[str], set[str]]:
    """Traverse all edges or one reference-strength stratum."""

    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        if strength is not None and edge["strength"] != strength:
            continue
        adjacency.setdefault(edge["source"], []).append(edge["target"])

    reached = {root}
    files: set[str] = set()
    queue = deque([root])
    while queue:
        current = queue.popleft()
        files.add(fqn_to_file[current])
        for target in adjacency.get(current, []):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return reached, files


def weak_only_entries(
    weak_only_classes: set[str],
    strong_classes: set[str],
    baseline_classes: set[str],
    fqn_to_file: dict[str, str],
    edges: list[dict[str, str]],
) -> list[dict[str, object]]:
    """List each baseline-only class and its classified immediate inbound edges."""

    incoming: dict[str, dict[tuple[str, str, str, str], dict[str, str]]] = {}
    for edge in edges:
        if edge["target"] not in weak_only_classes:
            continue
        source = edge["source"]
        if source in strong_classes:
            source_scope = "strong_closure"
        elif source in baseline_classes:
            source_scope = "baseline_weak_only"
        else:
            source_scope = "outside_baseline"
        key = (source, edge["source_file"], edge["strength"], edge["kind"])
        incoming.setdefault(edge["target"], {})[key] = {
            "source_fqn": source,
            "source_file": edge["source_file"],
            "strength": edge["strength"],
            "kind": edge["kind"],
            "source_scope": source_scope,
        }
    entries: list[dict[str, object]] = []
    for fqn in sorted(weak_only_classes):
        sources = sorted(
            incoming.get(fqn, {}).values(),
            key=lambda item: (
                item["source_fqn"],
                item["strength"],
                item["kind"],
            ),
        )
        entries.append(
            {
                "fqn": fqn,
                "file": fqn_to_file[fqn],
                "unique_inbound_sources": sources,
                "weak_inbound_sources": [
                    source for source in sources if source["strength"] == "weak"
                ],
            }
        )
    return entries


def read_baseline(path: str, root: str, fqn_to_file: dict[str, str], file_text: dict[str, str]) -> dict[str, object]:
    with open(path, encoding="utf-8") as handle:
        baseline = json.load(handle)
    required = {"root", "closure_classes", "closure_files", "indexed_class_count", "indexed_file_count"}
    missing = sorted(required - set(baseline))
    if missing:
        raise SystemExit("baseline closure is missing fields: " + ", ".join(missing))
    if baseline["root"] != root:
        raise SystemExit("baseline closure root does not match --root")
    if baseline["indexed_class_count"] != len(fqn_to_file) or baseline["indexed_file_count"] != len(file_text):
        raise SystemExit("baseline closure index counts no longer match current model sources")
    return baseline


def resolve(ref: str, fqn_to_file: dict[str, str]) -> str | None:
    """Map a reference to a defined class, trimming trailing member accesses."""
    parts = ref.split(".")
    while len(parts) > 1:
        candidate = ".".join(parts)
        if candidate in fqn_to_file:
            return candidate
        parts.pop()
    return None


def closure(root: str, fqn_to_file: dict[str, str], file_text: dict[str, str]):
    if root not in fqn_to_file:
        raise SystemExit(f"root class not found in index: {root}")

    reached: set[str] = set()
    files: set[str] = set()
    edges: list[tuple[str, str]] = []
    unresolved: set[str] = set()

    queue = deque([root])
    reached.add(root)

    while queue:
        current = queue.popleft()
        path = fqn_to_file[current]
        files.add(path)
        for ref in refs_in(file_text[path]):
            target = resolve(ref, fqn_to_file)
            if target is None:
                unresolved.add(ref)
                continue
            if target == current:
                continue
            edges.append((current, target))
            if target not in reached:
                reached.add(target)
                queue.append(target)

    return reached, files, edges, unresolved


def payload_for_closure(
    root: str,
    fqn_to_file: dict[str, str],
    file_text: dict[str, str],
    reached: set[str],
    files: set[str],
    unresolved: set[str],
) -> dict[str, object]:
    """Build the legacy --out schema without changing any existing fields."""

    all_files = set(file_text)
    outside_files = sorted(all_files - files)
    outside_classes = sorted(set(fqn_to_file) - reached)
    by_area: dict[str, int] = {}
    for path in outside_files:
        rel = path[len(MODEL_ROOT) + 1 :]
        area = "/".join(rel.split("/")[:2]) if "/" in rel else rel
        by_area[area] = by_area.get(area, 0) + 1
    return {
        "root": root,
        "indexed_class_count": len(fqn_to_file),
        "indexed_file_count": len(all_files),
        "closure_class_count": len(reached),
        "closure_file_count": len(files),
        "closure_classes": sorted(reached),
        "closure_files": sorted(files),
        "outside_files": outside_files,
        "outside_classes": outside_classes,
        "outside_files_by_area": by_area,
        "unresolved_refs": sorted(unresolved),
    }


def edge_counts(edges: list[dict[str, str]]) -> dict[str, int]:
    return {
        "total": len(edges),
        "strong": sum(edge["strength"] == "strong" for edge in edges),
        "weak": sum(edge["strength"] == "weak" for edge in edges),
    }


def write_payload(path: str, payload: dict[str, object]) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print(f"\nwrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--out", default="")
    parser.add_argument(
        "--strong-only",
        action="store_true",
        help="traverse only strong edges; requires --baseline",
    )
    parser.add_argument(
        "--baseline",
        default="",
        help="existing ordinary closure JSON used only for strong-only comparison",
    )
    args = parser.parse_args()

    fqn_to_file, file_text = build_index()
    if args.strong_only:
        if not args.baseline:
            parser.error("--strong-only requires --baseline")
        baseline = read_baseline(args.baseline, args.root, fqn_to_file, file_text)
        edges, unresolved_by_strength = classified_edges(fqn_to_file, file_text)
        reached, files = traverse_edges(args.root, fqn_to_file, edges, "strong")
        baseline_classes = set(baseline["closure_classes"])
        baseline_files = set(baseline["closure_files"])
        if not reached <= baseline_classes or not files <= baseline_files:
            raise SystemExit(
                "strong-only result is not a subset of the supplied ordinary closure"
            )

        weak_only_classes = baseline_classes - reached
        weak_only_files = baseline_files - files
        payload = payload_for_closure(
            args.root,
            fqn_to_file,
            file_text,
            reached,
            files,
            set(unresolved_by_strength["strong"]),
        )
        payload.update(
            {
                "reference_strength": "strong_only",
                "baseline_path": norm(args.baseline),
                "baseline_closure_class_count": len(baseline_classes),
                "baseline_closure_file_count": len(baseline_files),
                "strong_closure_class_count": len(reached),
                "strong_closure_file_count": len(files),
                "weak_only_class_count": len(weak_only_classes),
                "weak_only_file_count": len(weak_only_files),
                "weak_only_classes": sorted(weak_only_classes),
                "weak_only_files": sorted(weak_only_files),
                "weak_only_entries": weak_only_entries(
                    weak_only_classes,
                    reached,
                    baseline_classes,
                    fqn_to_file,
                    edges,
                ),
                "reference_edge_counts": edge_counts(edges),
                "reference_edges": edges,
                "unresolved_refs_by_strength": unresolved_by_strength,
            }
        )
        print(f"root                : {args.root}")
        print(f"indexed classes     : {len(fqn_to_file)}")
        print(f"indexed .mo files   : {len(file_text)}")
        print(f"strong classes      : {len(reached)}")
        print(f"strong .mo files    : {len(files)}")
        print(f"weak-only classes   : {len(weak_only_classes)}")
        print(f"weak-only .mo files : {len(weak_only_files)}")
        print(f"strong unresolved   : {len(unresolved_by_strength['strong'])}")
        if args.out:
            write_payload(args.out, payload)
        return

    reached, files, _edges, unresolved = closure(args.root, fqn_to_file, file_text)
    payload = payload_for_closure(
        args.root, fqn_to_file, file_text, reached, files, unresolved
    )
    print(f"root                : {args.root}")
    print(f"indexed classes     : {len(fqn_to_file)}")
    print(f"indexed .mo files   : {len(file_text)}")
    print(f"closure classes     : {payload['closure_class_count']}")
    print(f"closure files       : {payload['closure_file_count']}")
    print(f"outside classes     : {len(payload['outside_classes'])}")
    print(f"outside files       : {len(payload['outside_files'])}")
    print(f"unresolved refs     : {len(unresolved)}")
    print("\noutside files by area:")
    for area, count in sorted(
        payload["outside_files_by_area"].items(), key=lambda kv: -kv[1]
    ):
        print(f"  {count:4d}  {area}")

    if args.out:
        classified, unresolved_by_strength = classified_edges(fqn_to_file, file_text)
        payload.update(
            {
                "reference_edge_counts": edge_counts(classified),
                "reference_edges": classified,
                "unresolved_refs_by_strength": unresolved_by_strength,
            }
        )
        write_payload(args.out, payload)


if __name__ == "__main__":
    main()
