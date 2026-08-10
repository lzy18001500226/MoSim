"""Clone the accepted MathType table onto one native Word equation in a copy.

This is deliberately a one-equation pilot.  It exercises the layout operation
needed by the later review-copy builder without opening or modifying the
authoritative report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "Results" / "report_word_layout_20260804" / "mathtype_conversion_pilot"
DEFAULT_SOURCE = PILOT_DIR / "source_omml_pilot.docx"
DEFAULT_OUTPUT = PILOT_DIR / "clone_golden_table_formula_002_pilot_20260804.docx"
DEFAULT_EVIDENCE = PILOT_DIR / "clone_golden_table_formula_002_pilot_20260804.json"
DEFAULT_MANIFEST = ROOT / "Results" / "report_word_layout_20260804" / "MATHTYPE_FORMULA_MANIFEST.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_mathtype(document) -> int:
    result = 0
    for index in range(1, document.InlineShapes.Count + 1):
        shape = document.InlineShapes(index)
        try:
            if shape.OLEFormat.ProgID == "Equation.DSMT4":
                result += 1
        except Exception:
            continue
    return result


def find_template_table(document):
    matches = []
    for index in range(1, document.Tables.Count + 1):
        table = document.Tables.Item(index)
        for inline_index in range(1, table.Range.InlineShapes.Count + 1):
            shape = table.Range.InlineShapes.Item(inline_index)
            try:
                if shape.OLEFormat.ProgID == "Equation.DSMT4":
                    matches.append(table)
                    break
            except Exception:
                continue
    if len(matches) != 1:
        raise RuntimeError(f"Expected one golden MathType table, found {len(matches)}")
    return matches[0]


def find_inserted_table(document, insertion_start: int):
    candidates = []
    for index in range(1, document.Tables.Count + 1):
        table = document.Tables.Item(index)
        if abs(int(table.Range.Start) - insertion_start) <= 2:
            candidates.append(table)
    if len(candidates) != 1:
        starts = [int(document.Tables.Item(index).Range.Start) for index in range(1, document.Tables.Count + 1)]
        raise RuntimeError(
            f"Expected one cloned table at {insertion_start}, found {len(candidates)}; table starts={starts}"
        )
    return candidates[0]


def apply_font_variant(
    normalized_tex: str, formula_id: int, variant: str
) -> tuple[str, list[str]]:
    """Apply the reviewed formula-2 font correction to the disposable pilot."""
    if variant == "default" or formula_id != 2:
        return normalized_tex, []
    if variant != "match_first_subformula":
        raise ValueError(f"Unknown formula font variant: {variant}")

    corrected = normalized_tex
    replacements = (
        (r"\mathbf{v}", "v"),
        (r"\mathbf{a}", "a"),
        (r"\mathbf{0}", "0"),
        (r"\mathbf0", "0"),
        (r"\mathbf{1}", "1"),
    )
    changed = []
    for source, target in replacements:
        if source in corrected:
            corrected = corrected.replace(source, target)
            changed.append(f"{source}->{target}")
    return corrected, [
        "formula-2 second and third subformula font commands matched to the first subformula",
        "indicator fallback bold 1 normalized to the first subformula font",
        "font_replacements=" + ",".join(changed),
    ]


def normalize_formula(
    manifest_path: Path, formula_id: int, font_variant: str
) -> tuple[dict[str, object], str, list[str]]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mathtype_tex_compat import normalize_tex_for_mathtype

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    matches = [item for item in manifest["formulas"] if item["formula_id"] == formula_id]
    if len(matches) != 1:
        raise ValueError(f"Manifest contains {len(matches)} entries for formula {formula_id}")
    formula = matches[0]
    normalized, warnings = normalize_tex_for_mathtype(str(formula["source_tex"]))
    corrected, font_warnings = apply_font_variant(normalized, formula_id, font_variant)
    return formula, corrected, [*warnings, *font_warnings]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--formula-id", type=int, default=2)
    parser.add_argument(
        "--font-variant",
        choices=("default", "match_first_subformula"),
        default="match_first_subformula",
    )
    parser.add_argument(
        "--allow-existing-processes",
        action="store_true",
        help="Use an independent Word instance while unrelated desktop apps remain open.",
    )
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.source = args.source.resolve()
    args.output = args.output.resolve()
    args.evidence = args.evidence.resolve()
    args.manifest = args.manifest.resolve()
    if not args.source.is_file() or not args.manifest.is_file():
        raise FileNotFoundError("Source or manifest is missing")
    if args.output.exists() or args.evidence.exists():
        raise FileExistsError("Refusing to overwrite pilot output or evidence")
    formula, tex, warnings = normalize_formula(
        args.manifest, args.formula_id, args.font_variant
    )
    plan = {
        "schema": "mosim.report.clone_mathtype_equation_table_pilot.v1",
        "mode": "execute" if args.execute else "dry_run",
        "source": str(args.source).replace("\\", "/"),
        "source_sha256": sha256_file(args.source),
        "output": str(args.output).replace("\\", "/"),
        "evidence": str(args.evidence).replace("\\", "/"),
        "formula_id": args.formula_id,
        "font_variant": args.font_variant,
        "expected_number": formula["expected_number"],
        "normalized_tex": tex,
        "normalization_warnings": warnings,
        "allowed_actions": [
            "create and modify only the disposable output copy",
            "clone the golden 1-row/2-column MathType table",
            "convert exactly one native Word display equation",
            "save and reopen the pilot output",
        ],
        "forbidden_actions": [
            "open or modify Docs/报告/MoSim_仿真分析报告.docx",
            "batch-convert equations",
            "overwrite an existing pilot or evidence file",
        ],
    }
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    import pythoncom
    import win32com.client

    existing_processes = [
        {"pid": process.info.get("pid"), "name": process.info.get("name")}
        for process in __import__("psutil").process_iter(["pid", "name"])
        if (process.info.get("name") or "").lower() in {"winword.exe", "mathtype.exe"}
    ]
    if existing_processes and not args.allow_existing_processes:
        raise RuntimeError("Pilot requires no pre-existing Word or MathType process")
    plan["preexisting_processes"] = existing_processes

    shutil.copy2(args.source, args.output)
    word = None
    document = None
    reopened = None
    failure: str | None = None
    stage = "initialized"
    result: dict[str, object] = {}
    pythoncom.CoInitialize()
    try:
        stage = "start_word"
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = True
        word.DisplayAlerts = 0
        stage = "open_pilot"
        document = word.Documents.Open(str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=True)
        before_omaths = int(document.OMaths.Count)
        before_mathtype = count_mathtype(document)
        before_tables = int(document.Tables.Count)
        target = document.OMaths.Item(1).Range.Paragraphs.Item(1).Range
        insertion_start = int(target.Start)
        stage = "copy_golden_table"
        template = find_template_table(document)
        template.Range.Copy()
        stage = "paste_golden_table"
        target.Paste()
        cloned = find_inserted_table(document, insertion_start)
        stage = "replace_cloned_cell_content"
        left_cell = cloned.Cell(1, 1)
        left_content = document.Range(int(left_cell.Range.Start), int(left_cell.Range.End) - 1)
        left_content.Delete()
        insertion = document.Range(int(left_cell.Range.Start), int(left_cell.Range.Start))
        insertion.InsertAfter(tex)
        tex_range = document.Range(int(left_cell.Range.Start), int(left_cell.Range.Start) + len(tex))
        tex_range.Select()
        document.Activate()
        word.Activate()
        stage = "tex_toggle"
        word.Run("MathTypeCommands.UILib.MTCommand_TeXToggle")

        stage = "remove_source_omml"
        remaining_omaths_before_cleanup = int(document.OMaths.Count)
        if before_omaths != 1 or remaining_omaths_before_cleanup != 1:
            raise RuntimeError(
                "Expected the source pilot's single OMML object to remain isolated "
                f"until cleanup: before={before_omaths}, "
                f"after_conversion={remaining_omaths_before_cleanup}"
            )
        # Pasting the table at the OMML range leaves the original equation in
        # the surrounding paragraph; remove that source object after the new
        # MathType object has been created in the cloned cell.
        document.OMaths.Item(1).Range.Delete()
        after_omaths = int(document.OMaths.Count)
        after_mathtype = count_mathtype(document)
        after_tables = int(document.Tables.Count)
        stage = "update_equation_field"
        right_cell = cloned.Cell(1, 2)
        cloned_rows = int(cloned.Rows.Count)
        cloned_columns = int(cloned.Columns.Count)
        fields = right_cell.Range.Fields
        if int(fields.Count) != 2:
            raise RuntimeError(
                f"Expected two numbering fields in the cloned table, found {fields.Count}"
            )
        # The disposable golden sample has no chapter heading context, so its
        # chapter continuation field renders as zero when Word exports it.
        # Seed only this pilot's chapter field; the report builder keeps the
        # production `SEQ Chapter \\c` contract under the real heading.
        fields.Item(1).Code.Text = (
            f" SEQ Chapter \\r {formula['chapter']} \\* ARABIC "
        )
        fields.Item(2).Code.Text = (
            f" {formula['equation_field_instruction']} "
        )
        fields.Item(2).Update()
        # Match the report's verified numbering style, rather than inheriting
        # the theme font from the minimal disposable golden sample.
        number_font = right_cell.Range.Font
        number_font.Name = "Times New Roman"
        number_font.NameAscii = "Times New Roman"
        number_font.NameOther = "Times New Roman"
        number_font.NameFarEast = "宋体"
        number_font.Size = 12
        number_font.Bold = False
        number_font.Italic = False
        number_font_contract = {
            "name": str(number_font.Name),
            "name_ascii": str(number_font.NameAscii),
            "name_far_east": str(number_font.NameFarEast),
            "size": float(number_font.Size),
            "bold": bool(number_font.Bold),
            "italic": bool(number_font.Italic),
        }
        field_instructions = [
            str(right_cell.Range.Fields.Item(index).Code.Text).strip()
            for index in range(1, right_cell.Range.Fields.Count + 1)
        ]
        stage = "save_and_reopen"
        document.Save()
        document.Close(False)
        document = None
        reopened = word.Documents.Open(str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=False)
        result = {
            "before_omaths": before_omaths,
            "before_mathtype_objects": before_mathtype,
            "before_tables": before_tables,
            "after_omaths": after_omaths,
            "remaining_omaths_before_cleanup": remaining_omaths_before_cleanup,
            "after_mathtype_objects": after_mathtype,
            "after_tables": after_tables,
            "cloned_table_rows": cloned_rows,
            "cloned_table_columns": cloned_columns,
            "right_cell_field_instructions": field_instructions,
            "right_cell_number_font": number_font_contract,
            "pilot_chapter_field_seeded": True,
            "reopened_omaths": int(reopened.OMaths.Count),
            "reopened_mathtype_objects": count_mathtype(reopened),
            "reopened_tables": int(reopened.Tables.Count),
        }
        if result["after_omaths"] != before_omaths - 1:
            raise RuntimeError(f"Expected one fewer OMML object: {result}")
        if result["after_mathtype_objects"] != before_mathtype + 1:
            raise RuntimeError(f"Expected one more MathType object: {result}")
        if result["after_tables"] != before_tables + 1:
            raise RuntimeError(f"Expected one more table: {result}")
        if result["reopened_omaths"] != result["after_omaths"] or result["reopened_mathtype_objects"] != result["after_mathtype_objects"]:
            raise RuntimeError(f"Saved pilot changed object counts: {result}")
        status = "clone_and_tex_toggle_roundtrip_passed_pending_visual_review"
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        failure = f"stage={stage}; {failure}"
        status = "failed"
    finally:
        if reopened is not None:
            try:
                reopened.Close(False)
            except Exception:
                pass
        if document is not None:
            try:
                document.Close(False)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit(False)
            except Exception:
                pass
        pythoncom.CoUninitialize()
        time.sleep(1.0)

    plan.update(result)
    plan.update(
        {
            "status": status,
            "failure": failure,
            "output_exists": args.output.is_file(),
            "output_sha256": sha256_file(args.output) if args.output.is_file() else None,
            "authoritative_report_touched": False,
        }
    )
    args.evidence.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if failure:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
