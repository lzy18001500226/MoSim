#!/usr/bin/env python3
"""Plan a MathType review-copy conversion and retain the legacy route only
when explicitly requested.

The authoritative report is an immutable input.  This runner converts one
formula at a time, saves after every successful formula, and emits a JSONL
checkpoint so a stopped run can resume from the next unconverted formula.

The historical execution path uses Word selection plus
``MathTypeCommands.UILib.MTCommand_TeXToggle``.  It is intentionally blocked
by default because it can bring foreground plaintext entry to the user's
desktop.  Use ``run_mathtype_report_mathml_backend.ps1`` for the hidden OLE
MathML path.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import zipfile

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "Docs" / "报告" / "MoSim_仿真分析报告.docx"
MANIFEST = ROOT / "Results" / "report_word_layout_20260804" / "MATHTYPE_FORMULA_MANIFEST.json"
OUTPUT = (
    ROOT
    / "Results"
    / "report_word_layout_20260804"
    / "MoSim_仿真分析报告_MathType审阅副本_20260804.docx"
)
EVIDENCE = (
    ROOT
    / "Results"
    / "report_word_layout_20260804"
    / "MATHTYPE_REVIEW_COPY_CONVERSION_20260804.json"
)
CHECKPOINT = (
    ROOT
    / "Results"
    / "report_word_layout_20260804"
    / "MATHTYPE_REVIEW_COPY_CONVERSION_20260804.jsonl"
)

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
OFFICE_NS = "urn:schemas-microsoft-com:office:office"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": WORD_NS, "m": MATH_NS, "o": OFFICE_NS}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_instruction(value: str) -> str:
    return " ".join(value.split())


def inspect_docx(path: Path) -> dict[str, object]:
    """Read the OOXML facts used to protect source and review-copy contracts."""
    with zipfile.ZipFile(path, "r") as archive:
        root = etree.fromstring(archive.read("word/document.xml"))

    omaths = root.xpath(".//m:oMath", namespaces=NS)
    oles = root.xpath(".//o:OLEObject[@ProgID='Equation.DSMT4']", namespaces=NS)
    tables = root.xpath(".//w:tbl", namespaces=NS)
    formula_tables = [
        table
        for table in tables
        if table.xpath(".//m:oMath|.//o:OLEObject[@ProgID='Equation.DSMT4']", namespaces=NS)
    ]
    formula_table_contracts: list[dict[str, object]] = []
    for table in formula_tables:
        cells = table.xpath("./w:tr[1]/w:tc", namespaces=NS)
        field_instructions = [
            normalize_instruction(value)
            for value in table.xpath(".//w:instrText/text()|.//w:fldSimple/@w:instr", namespaces=NS)
        ]
        formula_table_contracts.append(
            {
                "rows": len(table.xpath("./w:tr", namespaces=NS)),
                "columns": len(cells),
                "mathtype_objects": len(
                    table.xpath(".//o:OLEObject[@ProgID='Equation.DSMT4']", namespaces=NS)
                ),
                "omath_objects": len(table.xpath(".//m:oMath", namespaces=NS)),
                "field_instructions": field_instructions,
                "right_cell_text": "".join(cells[1].xpath(".//w:t/text()", namespaces=NS))
                if len(cells) == 2
                else "",
            }
        )
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "omath_count": len(omaths),
        "mathtype_ole_count": len(oles),
        "table_count": len(tables),
        "formula_table_count": len(formula_tables),
        "formula_table_contracts": formula_table_contracts,
    }


def load_formula_records(manifest_path: Path) -> list[dict[str, object]]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from mathtype_tex_compat import normalize_tex_for_mathtype
    finally:
        sys.path.pop(0)

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    formulas = payload.get("formulas")
    if not isinstance(formulas, list) or len(formulas) != 104:
        raise ValueError("MathType manifest must contain exactly 104 display formulas")

    records: list[dict[str, object]] = []
    for expected_id, formula in enumerate(formulas, start=1):
        if int(formula.get("formula_id", -1)) != expected_id:
            raise ValueError(f"Manifest formula order is not contiguous at {expected_id}")
        normalized, warnings = normalize_tex_for_mathtype(str(formula["source_tex"]))
        records.append(
            {
                "formula_id": expected_id,
                "expected_number": str(formula["expected_number"]),
                "chapter": int(formula["chapter"]),
                "sequence": int(formula["sequence"]),
                "suffix": str(formula["suffix"]),
                "source_start_line": int(formula["source_start_line"]),
                "source_end_line": int(formula["source_end_line"]),
                "source_tex_sha256": str(formula["source_tex_sha256"]),
                "normalized_tex": normalized,
                "normalized_tex_sha256": sha256_text(normalized),
                "normalization_warnings": warnings,
            }
        )
    return records


def process_snapshot() -> list[dict[str, object]]:
    import psutil

    result: list[dict[str, object]] = []
    for process in psutil.process_iter(["pid", "name", "create_time", "status"]):
        name = (process.info.get("name") or "").lower()
        if name in {"winword.exe", "mathtype.exe"}:
            result.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "create_time": process.info.get("create_time"),
                    "status": process.info.get("status"),
                }
            )
    return result


def processes_named(processes: list[dict[str, object]], name: str) -> list[dict[str, object]]:
    return [process for process in processes if str(process["name"]).lower() == name]


def count_mathtype(document) -> int:
    count = 0
    for index in range(1, document.InlineShapes.Count + 1):
        shape = document.InlineShapes.Item(index)
        try:
            if shape.OLEFormat.ProgID == "Equation.DSMT4":
                count += 1
        except Exception:
            continue
    return count


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
    if len(matches) < 1:
        raise RuntimeError("Review copy has no MathType table to clone")
    return matches[0]


def find_inserted_table(document, insertion_start: int):
    candidates = []
    for index in range(1, document.Tables.Count + 1):
        table = document.Tables.Item(index)
        if abs(int(table.Range.Start) - insertion_start) <= 2:
            candidates.append(table)
    if len(candidates) != 1:
        starts = [
            int(document.Tables.Item(index).Range.Start)
            for index in range(1, document.Tables.Count + 1)
        ]
        raise RuntimeError(
            f"Expected one cloned equation table at {insertion_start}; table starts={starts}"
        )
    return candidates[0]


def configure_number(document, table, formula: dict[str, object]) -> dict[str, object]:
    """Set the explicit sequence reset and optional source suffix in a cloned table."""
    right_cell = table.Cell(1, 2)
    fields = right_cell.Range.Fields
    if int(fields.Count) != 2:
        raise RuntimeError(f"Equation number cell needs two fields, found {fields.Count}")
    fields.Item(1).Code.Text = " SEQ Chapter \\c "
    fields.Item(2).Code.Text = (
        f" SEQ Equation \\r {int(formula['sequence'])} \\* ARABIC "
    )
    for index in range(1, int(fields.Count) + 1):
        fields.Item(index).Update()

    suffix = str(formula["suffix"])
    if suffix:
        # A Word table cell range ends in a paragraph mark plus an end-cell
        # marker. Insert the literal suffix just before that paragraph mark.
        insertion = document.Range(
            int(right_cell.Range.End) - 2, int(right_cell.Range.End) - 2
        )
        insertion.Text = suffix
    visible_text = right_cell.Range.Text.replace("\r", "").replace("\x07", "")
    return {
        "field_instructions": [
            normalize_instruction(fields.Item(index).Code.Text)
            for index in range(1, int(fields.Count) + 1)
        ],
        "visible_text": visible_text,
    }


def convert_next_formula(
    document, word, template, formula: dict[str, object], native_omath_index: int = 1
) -> dict[str, object]:
    """Replace one remaining native display equation with a MathType table."""
    stage = "count_before"
    try:
        before_omaths = int(document.OMaths.Count)
        before_mathtype = count_mathtype(document)
        before_tables = int(document.Tables.Count)
        if before_omaths <= 0:
            raise RuntimeError("No native display equation remains for conversion")

        stage = "locate_native_equation"
        if native_omath_index < 1 or native_omath_index > before_omaths:
            raise RuntimeError(
                f"Native equation index {native_omath_index} is outside 1..{before_omaths}"
            )
        target = document.OMaths.Item(native_omath_index).Range.Paragraphs.Item(1).Range
        insertion_start = int(target.Start)
        stage = "copy_template"
        template.Range.Copy()
        stage = "paste_template"
        target.Paste()
        stage = "locate_cloned_table"
        cloned = find_inserted_table(document, insertion_start)
        if int(cloned.Rows.Count) != 1 or int(cloned.Columns.Count) != 2:
            raise RuntimeError("Cloned equation table is not one row by two columns")

        stage = "configure_number"
        number_contract = configure_number(document, cloned, formula)
        left_cell = cloned.Cell(1, 1)
        left_content = document.Range(
            int(left_cell.Range.Start), int(left_cell.Range.End) - 1
        )
        stage = "insert_tex"
        left_content.Delete()
        insertion = document.Range(int(left_cell.Range.Start), int(left_cell.Range.Start))
        normalized_tex = str(formula["normalized_tex"])
        insertion.InsertAfter(normalized_tex)
        tex_range = document.Range(
            int(left_cell.Range.Start), int(left_cell.Range.Start) + len(normalized_tex)
        )
        stage = "invoke_mathtype_tex_toggle"
        tex_range.Select()
        document.Activate()
        word.Activate()
        word.Run("MathTypeCommands.UILib.MTCommand_TeXToggle")

        stage = "wait_for_mathtype_object"
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            after_omaths = int(document.OMaths.Count)
            after_mathtype = count_mathtype(document)
            if after_omaths == before_omaths - 1 and after_mathtype == before_mathtype + 1:
                break
            time.sleep(0.25)
        else:
            after_omaths = int(document.OMaths.Count)
            after_mathtype = count_mathtype(document)
            raise RuntimeError(
                "MathType TeX toggle timed out for formula "
                f"{formula['formula_id']}: omaths={after_omaths}, mathtype={after_mathtype}"
            )

        stage = "validate_number_and_table"
        after_tables = int(document.Tables.Count)
        if after_tables != before_tables + 1:
            raise RuntimeError(
                f"Formula {formula['formula_id']} did not add exactly one equation table"
            )
        expected_visible = f"({formula['expected_number']})"
        if number_contract["visible_text"] != expected_visible:
            raise RuntimeError(
                f"Formula {formula['formula_id']} number is {number_contract['visible_text']!r}, "
                f"expected {expected_visible!r}"
            )
        stage = "save_review_copy"
        document.Save()
        return {
            "formula_id": formula["formula_id"],
            "expected_number": formula["expected_number"],
            "source_start_line": formula["source_start_line"],
            "source_end_line": formula["source_end_line"],
            "source_tex_sha256": formula["source_tex_sha256"],
            "normalized_tex_sha256": formula["normalized_tex_sha256"],
            "normalization_warnings": formula["normalization_warnings"],
            "before_omaths": before_omaths,
            "after_omaths": after_omaths,
            "native_omath_index": native_omath_index,
            "before_mathtype_objects": before_mathtype,
            "after_mathtype_objects": after_mathtype,
            "before_tables": before_tables,
            "after_tables": after_tables,
            "number": number_contract,
            "status": "saved_checkpoint",
        }
    except Exception as error:
        raise RuntimeError(
            f"Formula {formula['formula_id']} failed at stage {stage}: {error}"
        ) from error


def append_checkpoint(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_checkpoint(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"Resume requires checkpoint file: {path}")
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid checkpoint line {line_number}: {error}") from error
    return records


def completed_formula_ids(records: list[dict[str, object]]) -> list[int]:
    completed = [
        int(record["formula_id"])
        for record in records
        if record.get("status") in {"saved_checkpoint", "manual_placeholder_resolved"}
        and "formula_id" in record
    ]
    return sorted(set(completed))


def manual_placeholder_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    resolved = {
        int(record["formula_id"])
        for record in records
        if record.get("status") == "manual_placeholder_resolved" and "formula_id" in record
    }
    return [
        record
        for record in records
        if record.get("status") == "manual_placeholder"
        and "formula_id" in record
        and int(record["formula_id"]) not in resolved
    ]


def processed_formula_ids(records: list[dict[str, object]]) -> list[int]:
    processed = [
        int(record["formula_id"])
        for record in records
        if record.get("status")
        in {"saved_checkpoint", "manual_placeholder", "manual_placeholder_resolved"}
        and "formula_id" in record
    ]
    return sorted(set(processed))


def manual_placeholder_record(
    formula: dict[str, object], failure: str, native_omath_index: int
) -> dict[str, object]:
    return {
        "formula_id": formula["formula_id"],
        "expected_number": formula["expected_number"],
        "source_start_line": formula["source_start_line"],
        "source_end_line": formula["source_end_line"],
        "source_tex_sha256": formula["source_tex_sha256"],
        "normalized_tex": formula["normalized_tex"],
        "normalized_tex_sha256": formula["normalized_tex_sha256"],
        "normalization_warnings": formula["normalization_warnings"],
        "native_omath_index": native_omath_index,
        "failure": failure,
        "status": "manual_placeholder",
        "reason": (
            "The bounded MathType TeX conversion did not produce an Equation.DSMT4 "
            "object. The review copy intentionally retains the original OMML formula "
            "at this position while later formulas continue in order."
        ),
        "manual_action": (
            "Open this exact formula in the review copy, replace the retained OMML "
            "formula with one Equation.DSMT4 object, preserve the displayed equation "
            "number, save, then rerun its per-formula reopen, structure, and visual acceptance."
        ),
    }


def manual_queue_entries(records: list[dict[str, object]]) -> list[dict[str, object]]:
    """Expose queue classifications without changing append-only checkpoint history."""
    queue: list[dict[str, object]] = []
    for record in records:
        entry = dict(record)
        failure = str(entry.get("failure", ""))
        if "wait_for_mathtype_object" in failure or "MathType TeX toggle" in failure:
            entry["queue_status"] = "mathtype_tex_route_failed"
            entry["reason"] = (
                "The bounded MathType TeX route did not create Equation.DSMT4. "
                "The original OMML formula remains in the review copy at this position."
            )
            entry["manual_action"] = (
                "Open this exact retained formula in the review copy, create one "
                "Equation.DSMT4 object manually, preserve the displayed equation number, "
                "save, then rerun its per-formula reopen, structure, and visual acceptance."
            )
        else:
            entry["queue_status"] = "retryable_word_session_error"
            entry["reason"] = (
                "The runner failed before the MathType TeX conversion stage, so this is "
                "not evidence that the formula is TeX-incompatible. The original OMML "
                "formula remains in place for a fresh-session retry."
            )
            entry["manual_action"] = (
                "Retry this exact retained formula once from a fresh runner-owned Word "
                "session before manual MathType entry; then run its per-formula reopen, "
                "structure, and visual acceptance."
            )
        queue.append(entry)
    return queue


def build_plan(args: argparse.Namespace, formulas: list[dict[str, object]]) -> dict[str, object]:
    source = inspect_docx(args.source)
    if source["omath_count"] != 103 or source["mathtype_ole_count"] != 1:
        raise ValueError(
            "Authoritative report must contain 103 native display equations and one MathType equation"
        )
    if source["formula_table_count"] != 1:
        raise ValueError("Authoritative report must contain exactly one MathType template table")
    normalized_warning_counts: dict[str, int] = {}
    for formula in formulas:
        for warning in formula["normalization_warnings"]:
            normalized_warning_counts[warning] = normalized_warning_counts.get(warning, 0) + 1
    return {
        "schema": "mosim.report.mathtype_review_copy_conversion.v1",
        "mode": "execute" if args.execute else "dry_run",
        "authoritative_report": source,
        "manifest": {
            "path": str(args.manifest.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(args.manifest),
            "formula_count": len(formulas),
            "existing_mathtype_formula_id": 1,
            "native_formulas_to_convert": 103,
            "normalization_warning_counts": normalized_warning_counts,
        },
        "output": str(args.output).replace("\\", "/"),
        "evidence": str(args.evidence).replace("\\", "/"),
        "checkpoint": str(args.checkpoint).replace("\\", "/"),
        "stop_after_formula_id": args.stop_after,
        "repair_manual_formula_id": args.repair_manual_formula,
        "resume": args.resume,
        "allow_existing_mathtype_server": args.allow_existing_mathtype_server,
        "max_transient_retries": args.max_transient_retries,
        "continue_on_incompatibility": args.continue_on_incompatibility,
        "allowed_actions": [
            "copy the authoritative report to a new review output",
            "replace one native display equation at a time in that review output",
            "save a review-output checkpoint after every successful conversion",
            "reopen only the review output for final structural verification",
        ],
        "forbidden_actions": [
            "open, save, modify, or overwrite the authoritative report",
            "skip a failed formula without retaining its exact original OMML position and manual queue record",
            "overwrite an existing review output without --resume",
            "attach to a pre-existing Word process",
            "terminate, restart, or automate a pre-existing MathType process",
        ],
    }


def validate_resume_document(path: Path, completed: list[int]) -> None:
    facts = inspect_docx(path)
    expected_completed = 1 + len(completed)
    if facts["omath_count"] != 104 - expected_completed:
        raise RuntimeError(
            f"Resume copy has {facts['omath_count']} OMML objects, expected {104 - expected_completed}"
        )
    if facts["mathtype_ole_count"] != expected_completed:
        raise RuntimeError(
            f"Resume copy has {facts['mathtype_ole_count']} MathType objects, expected {expected_completed}"
        )


def write_evidence(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def manual_queue_entry(
    formula: dict[str, object] | None, failure: str | None
) -> list[dict[str, object]]:
    if formula is None or failure is None:
        return []
    category = (
        "potential_tex_toggle_incompatibility"
        if "MathType TeX toggle" in failure
        else "conversion_interruption_requires_human_review"
    )
    return [
        {
            "formula_id": formula["formula_id"],
            "expected_number": formula["expected_number"],
            "source_start_line": formula["source_start_line"],
            "source_end_line": formula["source_end_line"],
            "source_tex_sha256": formula["source_tex_sha256"],
            "normalized_tex_sha256": formula["normalized_tex_sha256"],
            "normalization_warnings": formula["normalization_warnings"],
            "failure": failure,
            "status": category,
            "manual_action": (
                "Open the matching formula in a disposable MathType review copy, "
                "complete or repair this one conversion manually, save it, then rerun "
                "the structural, reopen, and visual acceptance for this formula."
            ),
        }
    ]


def execute(args: argparse.Namespace, plan: dict[str, object], formulas: list[dict[str, object]]) -> dict[str, object]:
    before_processes = process_snapshot()
    existing_word = processes_named(before_processes, "winword.exe")
    existing_mathtype = processes_named(before_processes, "mathtype.exe")
    if existing_word:
        raise RuntimeError(
            "Review-copy conversion requires no pre-existing Word process: "
            f"{existing_word}"
        )
    if existing_mathtype and not args.allow_existing_mathtype_server:
        raise RuntimeError(
            "A pre-existing MathType OLE server was found. Re-run only with "
            "--allow-existing-mathtype-server after recording the authorization: "
            f"{existing_mathtype}"
        )

    if args.resume:
        if not args.output.is_file():
            raise FileNotFoundError(f"Resume output does not exist: {args.output}")
        checkpoint_records = read_checkpoint(args.checkpoint)
        completed = completed_formula_ids(checkpoint_records)
        processed = processed_formula_ids(checkpoint_records)
        expected_processed = list(range(2, (processed[-1] if processed else 1) + 1))
        if processed != expected_processed:
            raise RuntimeError(f"Checkpoint processing is not contiguous: {processed}")
        if not set(completed).issubset(processed):
            raise RuntimeError("Checkpoint converted formulas are not all processed formulas")
        manual_records = manual_placeholder_records(checkpoint_records)
        validate_resume_document(args.output, completed)
    else:
        for path in (args.output, args.evidence, args.checkpoint):
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite existing review artifact: {path}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.source, args.output)
        append_checkpoint(
            args.checkpoint,
            {
                "event": "created_review_copy",
                "source_sha256": sha256_file(args.source),
                "output_sha256": sha256_file(args.output),
                "preserved_existing_formula_id": 1,
            },
        )
        completed = []
        processed = []
        manual_records = []

    manual_ids = {int(record["formula_id"]) for record in manual_records}
    next_formula_id = (processed[-1] + 1) if processed else 2
    if (
        args.repair_manual_formula is None
        and args.stop_after is not None
        and args.stop_after < next_formula_id
    ):
        raise ValueError("--stop-after must not precede the next unconverted formula")

    import pythoncom
    import win32com.client

    word = None
    document = None
    item_records: list[dict[str, object]] = []
    manual_placeholders_this_run: list[dict[str, object]] = []
    recovered_transient_errors: list[dict[str, object]] = []
    failure: str | None = None
    active_formula: dict[str, object] | None = None
    status = "failed"
    pythoncom.CoInitialize()
    try:
        def open_edit_session():
            session_word = win32com.client.DispatchEx("Word.Application")
            session_word.Visible = False
            session_word.DisplayAlerts = 0
            session_word.ScreenUpdating = False
            session_document = session_word.Documents.Open(
                str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=False
            )
            return session_word, session_document, find_template_table(session_document)

        def close_edit_session(session_word, session_document) -> None:
            if session_document is not None:
                session_document.Close(False)
            if session_word is not None:
                session_word.Quit(False)

        repair_formula_id = args.repair_manual_formula
        if repair_formula_id is not None:
            if repair_formula_id not in manual_ids:
                raise RuntimeError(
                    f"Formula {repair_formula_id} is not an unresolved manual placeholder"
                )
            formula_sequence = [formulas[repair_formula_id - 1]]
        else:
            formula_sequence = formulas[next_formula_id - 1 :]

        word, document, template = open_edit_session()
        for formula in formula_sequence:
            active_formula = formula
            formula_retries: list[dict[str, object]] = []
            record = None
            final_failure: str | None = None
            native_omath_index = (
                1 + sum(manual_id < int(formula["formula_id"]) for manual_id in manual_ids)
                if repair_formula_id is not None
                else len(manual_ids) + 1
            )
            for attempt in range(args.max_transient_retries + 1):
                try:
                    record = convert_next_formula(
                        document,
                        word,
                        template,
                        formula,
                        native_omath_index=native_omath_index,
                    )
                    break
                except Exception as error:
                    failure_text = f"{type(error).__name__}: {error}"
                    if attempt >= args.max_transient_retries:
                        final_failure = failure_text
                        break
                    formula_retries.append(
                        {
                            "attempt": attempt + 1,
                            "failure": failure_text,
                            "recovery": "closed current runner-owned Word session without saving pending edits",
                        }
                    )
                    close_edit_session(word, document)
                    word = None
                    document = None
                    validate_resume_document(
                        args.output, completed_formula_ids(read_checkpoint(args.checkpoint))
                    )
                    time.sleep(2.0)
                    word, document, template = open_edit_session()
            if record is None:
                if repair_formula_id is not None:
                    raise RuntimeError(final_failure or "Manual placeholder retry failed without detail")
                if not args.continue_on_incompatibility:
                    raise RuntimeError(final_failure or "Formula conversion failed without detail")
                close_edit_session(word, document)
                word = None
                document = None
                validate_resume_document(
                    args.output, completed_formula_ids(read_checkpoint(args.checkpoint))
                )
                record = manual_placeholder_record(
                    formula,
                    final_failure or "Formula conversion failed without detail",
                    native_omath_index,
                )
                if formula_retries:
                    record["transient_retries"] = formula_retries
                    recovered_transient_errors.extend(
                        [{"formula_id": formula["formula_id"], **entry} for entry in formula_retries]
                    )
                append_checkpoint(args.checkpoint, record)
                item_records.append(record)
                manual_placeholders_this_run.append(record)
                manual_records.append(record)
                manual_ids.add(int(formula["formula_id"]))
                if args.stop_after is not None and int(formula["formula_id"]) >= args.stop_after:
                    status = "partial_checkpoint_ready"
                    break
                word, document, template = open_edit_session()
                continue
            if formula_retries:
                record["transient_retries"] = formula_retries
                recovered_transient_errors.extend(
                    [{"formula_id": formula["formula_id"], **entry} for entry in formula_retries]
                )
            if repair_formula_id is not None:
                record["status"] = "manual_placeholder_resolved"
                record["resolved_manual_placeholder"] = True
            append_checkpoint(args.checkpoint, record)
            item_records.append(record)
            if repair_formula_id is not None:
                manual_records = [
                    item
                    for item in manual_records
                    if int(item["formula_id"]) != repair_formula_id
                ]
                manual_ids.remove(repair_formula_id)
                status = "manual_placeholder_repaired_pending_final_reopen"
                break
            if args.stop_after is not None and int(formula["formula_id"]) >= args.stop_after:
                status = "partial_checkpoint_ready"
                break
        else:
            status = (
                "all_compatible_formulas_converted_pending_final_reopen"
                if manual_ids
                else "all_formulas_converted_pending_final_reopen"
            )
        if document is not None:
            document.Close(False)
            document = None
        if word is not None:
            word.Quit(False)
            word = None

        # Final acceptance is from a fresh Word process, not the process that
        # performed the edits.
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        document = word.Documents.Open(
            str(args.output), ReadOnly=True, AddToRecentFiles=False, Visible=False
        )
        reopened = {
            "omath_count": int(document.OMaths.Count),
            "mathtype_ole_count": count_mathtype(document),
            "table_count": int(document.Tables.Count),
        }
        document.Close(False)
        document = None
        word.Quit(False)
        word = None
        if status in {
            "all_formulas_converted_pending_final_reopen",
            "all_compatible_formulas_converted_pending_final_reopen",
            "manual_placeholder_repaired_pending_final_reopen",
        }:
            if status == "manual_placeholder_repaired_pending_final_reopen":
                expected_mathtype = 1 + len(
                    completed_formula_ids(read_checkpoint(args.checkpoint))
                )
                expected_omaths = 104 - expected_mathtype
            else:
                expected_omaths = len(manual_ids)
                expected_mathtype = 104 - expected_omaths
            if (
                reopened["omath_count"] != expected_omaths
                or reopened["mathtype_ole_count"] != expected_mathtype
            ):
                raise RuntimeError(f"Final Word reopen count mismatch: {reopened}")
            status = (
                "manual_placeholder_repaired_pending_visual_review"
                if status == "manual_placeholder_repaired_pending_final_reopen"
                else (
                    "all_compatible_formulas_converted_pending_visual_review"
                    if manual_ids
                    else "all_formulas_converted_pending_visual_review"
                )
            )
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        status = "blocked_at_current_formula"
    finally:
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
        time.sleep(2.0)

    result: dict[str, object] = dict(plan)
    result.update(
        {
            "status": status,
            "failure": failure,
            "manual_formula_queue": [
                *manual_queue_entries(manual_records),
                *manual_queue_entry(active_formula, failure),
            ],
            "recovered_transient_errors": recovered_transient_errors,
            "converted_this_run": [
                record
                for record in item_records
                if record.get("status")
                in {"saved_checkpoint", "manual_placeholder_resolved"}
            ],
            "manual_placeholders_this_run": manual_placeholders_this_run,
            "completed_formula_ids": completed_formula_ids(read_checkpoint(args.checkpoint)),
            "processed_formula_ids": processed_formula_ids(read_checkpoint(args.checkpoint)),
            "manual_placeholder_formula_ids": sorted(manual_ids),
            "output_exists": args.output.is_file(),
            "output_sha256": sha256_file(args.output) if args.output.is_file() else None,
            "output_structure": inspect_docx(args.output) if args.output.is_file() else None,
            "authoritative_report_unchanged": sha256_file(args.source)
            == plan["authoritative_report"]["sha256"],
            "preexisting_mathtype_servers": existing_mathtype,
            "remaining_word_mathtype_processes": process_snapshot(),
        }
    )
    write_evidence(args.evidence, result)
    if failure:
        raise RuntimeError(failure)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=REPORT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--stop-after", type=int, default=None)
    parser.add_argument(
        "--repair-manual-formula",
        type=int,
        default=None,
        help="retry one retained manual placeholder from a fresh Word session",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--allow-existing-mathtype-server", action="store_true")
    parser.add_argument("--max-transient-retries", type=int, default=1)
    parser.add_argument(
        "--continue-on-incompatibility",
        action="store_true",
        help="retain a failed formula as OMML and continue with an explicit manual queue record",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--allow-foreground-legacy",
        action="store_true",
        help=(
            "Explicitly opt into the deprecated Word-selection/TeX-toggle path; "
            "this can disrupt foreground desktop use."
        ),
    )
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    args.source = args.source.resolve()
    args.manifest = args.manifest.resolve()
    args.output = args.output.resolve()
    args.evidence = args.evidence.resolve()
    args.checkpoint = args.checkpoint.resolve()
    if args.source == args.output:
        raise ValueError("Output must be a new review copy, never the authoritative report")
    if not args.source.is_file() or not args.manifest.is_file():
        raise FileNotFoundError("Source report or formula manifest is missing")
    if args.stop_after is not None and not 2 <= args.stop_after <= 104:
        raise ValueError("--stop-after must be between 2 and 104")
    if args.repair_manual_formula is not None:
        if not args.resume:
            raise ValueError("--repair-manual-formula requires --resume")
        if not 2 <= args.repair_manual_formula <= 104:
            raise ValueError("--repair-manual-formula must be between 2 and 104")
        if args.stop_after is not None:
            raise ValueError("--repair-manual-formula cannot be combined with --stop-after")
    if args.max_transient_retries < 0:
        raise ValueError("--max-transient-retries must be non-negative")

    if args.execute and not args.allow_foreground_legacy:
        raise RuntimeError(
            "Foreground MathType TeX-toggle execution is disabled by default to "
            "protect desktop use. Run Scripts/report/run_mathtype_report_mathml_backend.ps1 "
            "with explicit source, manifest, output, and audit paths instead."
        )

    formulas = load_formula_records(args.manifest)
    plan = build_plan(args, formulas)
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    result = execute(args, plan, formulas)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
