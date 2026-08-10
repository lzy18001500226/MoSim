#!/usr/bin/env python3
"""Prepare deterministic MathML inputs for the report's MathType equations.

This tool is deliberately Word-free. It parses the display equations from the
report Markdown, validates their chapter-local tags, converts them to
Presentation MathML with Pandoc, and records the manually accepted equation
table geometry from a small golden DOCX pilot. The resulting manifest is the
input contract for a later, disposable Word/MathType OLE insertion pilot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from collections import OrderedDict
from pathlib import Path

from lxml import etree, html

from extract_report_formulas import Formula, parse_source


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "Docs" / "报告" / "草稿" / "仿真分析报告_正文骨架.md"
DEFAULT_GOLDEN = (
    ROOT
    / "Results"
    / "report_word_layout_20260804"
    / "mathtype_conversion_pilot"
    / "source_omml_pilot.docx"
)
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "report_word_layout_20260804"
    / "MATHTYPE_FORMULA_MANIFEST.json"
)

DISPLAY_OPEN = r"\["
DISPLAY_CLOSE = r"\]"
EXPECTED_DISPLAY_FORMULA_COUNT = 108
TAG_RE = re.compile(
    r"\\tag\{(?P<chapter>\d+)-(?P<sequence>\d+)(?P<suffix>[a-z]?)\}"
)
MATHML_NS = "http://www.w3.org/1998/Math/MathML"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
OFFICE_NS = "urn:schemas-microsoft-com:office:office"
VML_NS = "urn:schemas-microsoft-com:vml"
NS = {"w": WORD_NS, "o": OFFICE_NS, "v": VML_NS}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_field_instruction(value: str) -> str:
    return " ".join(value.split())


def find_pandoc(explicit: Path | None = None) -> Path:
    candidates = [
        explicit,
        Path(found) if (found := shutil.which("pandoc")) else None,
        Path(r"D:\Dev\Anaconda3\Library\bin\pandoc.exe"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("Pandoc was not found; pass --pandoc explicitly.")


def pandoc_version(pandoc: Path) -> str:
    result = subprocess.run(
        [str(pandoc), "--version"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.splitlines()[0].strip()


def display_math_body(
    formula: Formula, formula_id: int
) -> tuple[str, int, int, str, str, str]:
    text = formula.body.strip()
    if not (text.startswith(DISPLAY_OPEN) and text.endswith(DISPLAY_CLOSE)):
        raise ValueError(
            f"Display formula at line {formula.start_line} lacks \\[...\\] delimiters"
        )

    tag_matches = list(TAG_RE.finditer(text))
    if len(tag_matches) > 1:
        raise ValueError(
            f"Display formula at line {formula.start_line} contains multiple chapter tags"
        )
    if tag_matches:
        tag_match = tag_matches[0]
        chapter = int(tag_match.group("chapter"))
        sequence = int(tag_match.group("sequence"))
        suffix = tag_match.group("suffix")
        numbering_provenance = "source_tag"
    else:
        raise ValueError(
            f"Display formula {formula_id:03d} at line {formula.start_line} has no source tag"
        )
    expected_number = f"{chapter}-{sequence}{suffix}"

    body = text[len(DISPLAY_OPEN) : -len(DISPLAY_CLOSE)]
    body = TAG_RE.sub("", body).strip()
    if r"\tag" in body:
        raise ValueError(
            f"Unsupported residual tag syntax at line {formula.start_line}"
        )
    return body, chapter, sequence, suffix, expected_number, numbering_provenance


def validate_numbering(records: list[dict[str, object]]) -> dict[str, object]:
    sequences: OrderedDict[int, list[tuple[int, str]]] = OrderedDict()
    previous_chapter = -1
    seen_numbers: set[str] = set()
    for record in records:
        chapter = int(record["chapter"])
        sequence = int(record["sequence"])
        suffix = str(record["suffix"])
        number = str(record["expected_number"])
        if chapter < previous_chapter:
            raise ValueError(f"Equation chapter order regressed at {number}")
        if number in seen_numbers:
            raise ValueError(f"Duplicate equation number {number}")
        previous_chapter = chapter
        seen_numbers.add(number)
        sequences.setdefault(chapter, []).append((sequence, suffix))

    result: dict[str, object] = {}
    for chapter, labels in sequences.items():
        numeric_values = sorted({sequence for sequence, _suffix in labels})
        expected = list(range(1, max(numeric_values) + 1))
        if numeric_values != expected:
            raise ValueError(
                f"Chapter {chapter} numeric equation bases are {numeric_values}, expected {expected}"
            )
        suffixed_labels: list[str] = []
        for sequence in numeric_values:
            suffixes = sorted(
                suffix
                for value, suffix in labels
                if value == sequence and suffix
            )
            expected_suffixes = [chr(ord("a") + index) for index in range(len(suffixes))]
            if suffixes != expected_suffixes:
                raise ValueError(
                    f"Chapter {chapter} equation {sequence} suffixes are {suffixes}, "
                    f"expected {expected_suffixes}"
                )
            suffixed_labels.extend(f"{chapter}-{sequence}{suffix}" for suffix in suffixes)

        source_numeric_order = [sequence for sequence, _suffix in labels]
        strictly_increasing = all(
            current > previous
            for previous, current in zip(
                source_numeric_order, source_numeric_order[1:]
            )
        )
        result[str(chapter)] = {
            "formula_count": len(labels),
            "numeric_sequence_max": max(numeric_values),
            "suffixed_labels": suffixed_labels,
            "source_order_monotonic": source_numeric_order
            == sorted(source_numeric_order),
            "source_order_strictly_increasing": strictly_increasing,
            "requires_explicit_sequence_reset": not strictly_increasing,
        }
    return result


def build_pandoc_input(records: list[dict[str, object]]) -> str:
    blocks: list[str] = []
    for record in records:
        blocks.extend(
            [
                f"FORMULA {int(record['formula_id']):03d}",
                "",
                "$$",
                str(record["math_body"]),
                "$$",
                "",
            ]
        )
    return "\n".join(blocks)


def convert_to_mathml(
    pandoc: Path, records: list[dict[str, object]]
) -> tuple[list[str], list[str]]:
    result = subprocess.run(
        [
            str(pandoc),
            "--from=markdown+tex_math_dollars",
            "--to=html",
            "--mathml",
        ],
        input=build_pandoc_input(records),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    wrapper = html.fragment_fromstring(result.stdout, create_parent="div")
    math_nodes = wrapper.xpath(".//*[local-name()='math']")
    if len(math_nodes) != len(records):
        raise ValueError(
            f"Pandoc produced {len(math_nodes)} MathML nodes for {len(records)} formulas"
        )

    serialized: list[str] = []
    for index, node in enumerate(math_nodes, start=1):
        value = etree.tostring(node, encoding="unicode", method="xml")
        parsed = etree.fromstring(value.encode("utf-8"))
        if etree.QName(parsed).localname != "math":
            raise ValueError(f"Formula {index:03d} did not produce a MathML root")
        if parsed.get("display") != "block":
            raise ValueError(f"Formula {index:03d} did not produce display MathML")
        serialized.append(value)

    warnings = [line for line in result.stderr.splitlines() if line.strip()]
    return serialized, warnings


def mathml_structure(mathml: str) -> dict[str, int]:
    root = etree.fromstring(mathml.encode("utf-8"))
    counts: dict[str, int] = {}
    for node in root.iter():
        local_name = etree.QName(node).localname
        counts[local_name] = counts.get(local_name, 0) + 1
    return dict(sorted(counts.items()))


def inspect_golden_layout(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path, "r") as archive:
        document_xml = archive.read("word/document.xml")
        relationships_xml = archive.read("word/_rels/document.xml.rels")
    root = etree.fromstring(document_xml)
    relationships = etree.fromstring(relationships_xml)

    matching_tables = root.xpath(
        "//w:tbl[.//o:OLEObject[@ProgID='Equation.DSMT4']]", namespaces=NS
    )
    if len(matching_tables) != 1:
        raise ValueError(
            f"Golden pilot must contain one MathType equation table, found {len(matching_tables)}"
        )
    table = matching_tables[0]
    cells = table.xpath("./w:tr[1]/w:tc", namespaces=NS)
    if len(cells) != 2:
        raise ValueError("Golden equation table must be one row by two columns")

    field_instructions = [
        normalize_field_instruction(value)
        for value in table.xpath(".//w:instrText/text()", namespaces=NS)
    ]
    required_fields = [r"SEQ Chapter \c", r"SEQ Equation \* ARABIC"]
    if field_instructions != required_fields:
        raise ValueError(
            f"Golden field instructions are {field_instructions}, expected {required_fields}"
        )

    borders = {
        etree.QName(node).localname: node.get(f"{{{WORD_NS}}}val")
        for node in table.xpath("./w:tblPr/w:tblBorders/*", namespaces=NS)
    }
    if not borders or any(value != "none" for value in borders.values()):
        raise ValueError(f"Golden equation table is not borderless: {borders}")

    ole_objects = table.xpath(
        ".//o:OLEObject[@ProgID='Equation.DSMT4']", namespaces=NS
    )
    if len(ole_objects) != 1:
        raise ValueError("Golden equation table must contain one Equation.DSMT4 object")

    relationship_targets = {
        item.get("Id"): item.get("Target") for item in relationships
    }
    relationship_id = ole_objects[0].get(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    )
    if not relationship_id or not relationship_targets.get(relationship_id, "").startswith(
        "embeddings/"
    ):
        raise ValueError("Golden MathType object is not backed by an embedded OLE payload")

    def word_value(node, xpath: str, attribute: str = "val") -> str | None:
        result = node.xpath(xpath, namespaces=NS)
        return result[0].get(f"{{{WORD_NS}}}{attribute}") if result else None

    table_text = "".join(table.xpath(".//w:t/text()", namespaces=NS))
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_bytes(path.read_bytes()),
        "table_rows": 1,
        "table_columns": 2,
        "table_style_id": word_value(table, "./w:tblPr/w:tblStyle"),
        "table_width_twips": int(
            word_value(table, "./w:tblPr/w:tblW", "w") or 0
        ),
        "column_widths_twips": [
            int(node.get(f"{{{WORD_NS}}}w"))
            for node in table.xpath("./w:tblGrid/w:gridCol", namespaces=NS)
        ],
        "borders": borders,
        "cell_vertical_alignment": [
            word_value(cell, "./w:tcPr/w:vAlign") for cell in cells
        ],
        "paragraph_alignment": [
            word_value(cell, "./w:p[1]/w:pPr/w:jc") for cell in cells
        ],
        "field_instructions": field_instructions,
        "cached_number_text": table_text[-5:] if table_text.endswith(")") else table_text,
        "mathtype_progid": ole_objects[0].get("ProgID"),
        "embedded_object_target": relationship_targets[relationship_id],
    }


def build_manifest(source: Path, golden: Path, pandoc: Path) -> dict[str, object]:
    source_bytes = source.read_bytes()
    display, inline = parse_source(source_bytes.decode("utf-8"))
    if len(display) != EXPECTED_DISPLAY_FORMULA_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_DISPLAY_FORMULA_COUNT} display formulas, found {len(display)}"
        )

    formula_records: list[dict[str, object]] = []
    for formula_id, formula in enumerate(display, start=1):
        (
            body,
            chapter,
            sequence,
            suffix,
            expected_number,
            numbering_provenance,
        ) = display_math_body(formula, formula_id)
        formula_records.append(
            {
                "formula_id": formula_id,
                "source_start_line": formula.start_line,
                "source_end_line": formula.end_line,
                "section": formula.section,
                "chapter": chapter,
                "sequence": sequence,
                "suffix": suffix,
                "expected_number": expected_number,
                "numbering_provenance": numbering_provenance,
                "equation_field_instruction": (
                    f"SEQ Equation \\r {sequence} \\* ARABIC"
                ),
                "source_tex": formula.body,
                "math_body": body,
                "source_tex_sha256": sha256_bytes(formula.body.encode("utf-8")),
            }
        )

    chapter_counts = validate_numbering(formula_records)
    mathml_values, pandoc_warnings = convert_to_mathml(pandoc, formula_records)
    for record, mathml in zip(formula_records, mathml_values, strict=True):
        record["mathml"] = mathml
        record["mathml_sha256"] = sha256_bytes(mathml.encode("utf-8"))
        record["mathml_structure"] = mathml_structure(mathml)

    golden_layout = inspect_golden_layout(golden)
    if golden_layout["cached_number_text"] != "(2-1)":
        raise ValueError(
            "Golden equation sample no longer has the expected cached number (2-1)"
        )

    return {
        "schema": "mosim.report.mathtype_formula_manifest.v1",
        "source": {
            "path": str(source.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(source_bytes),
            "sha256": sha256_bytes(source_bytes),
            "display_formula_count": len(display),
            "inline_formula_count": len(inline),
        },
        "conversion": {
            "engine": "pandoc_presentation_mathml",
            "pandoc_version": pandoc_version(pandoc),
            "pandoc_warnings": pandoc_warnings,
            "word_or_mathtype_invoked": False,
            "intended_ole_clipboard_formats": [
                "MathML Presentation",
                "MathML",
                "application/mathml+xml",
            ],
        },
        "numbering_contract": {
            "chapter_field": r"SEQ Chapter \c",
            "golden_equation_field": r"SEQ Equation \* ARABIC",
            "remaining_equation_field_template": (
                r"SEQ Equation \r <numeric-sequence> \* ARABIC"
            ),
            "suffix_strategy": "append_source_tag_suffix_as_literal_text",
            "reason_for_explicit_sequence_reset": (
                "Chapter 3 source tags are non-monotonic; chapter 8 repeats "
                "numeric base 5 for suffixed labels. The source also includes "
                "a/b sublabels. "
                "document-order auto-increment cannot reproduce them."
            ),
            "visible_pattern": "(<chapter>-<equation>)",
            "chapters": chapter_counts,
            "inferred_numbering": [],
        },
        "golden_layout": golden_layout,
        "formulas": formula_records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pandoc", type=Path, default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare the deterministic manifest with --output without writing it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    golden = args.golden.resolve()
    output = args.output.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if not golden.is_file():
        raise FileNotFoundError(golden)

    manifest = build_manifest(source, golden, find_pandoc(args.pandoc))
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not output.is_file():
            raise FileNotFoundError(output)
        if output.read_text(encoding="utf-8") != rendered:
            raise ValueError(f"Manifest is stale: {output}")
        print(f"manifest_current={output}")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"manifest={output}")
    print(f"display_formulas={len(manifest['formulas'])}")
    print(f"chapter_formula_counts={manifest['numbering_contract']['chapters']}")
    print(f"pandoc_warnings={len(manifest['conversion']['pandoc_warnings'])}")
    print("word_or_mathtype_invoked=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
