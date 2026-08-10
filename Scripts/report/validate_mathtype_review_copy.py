#!/usr/bin/env python3
"""Validate a MathType review copy without modifying either DOCX input.

The converter owns the write path.  This validator opens the authoritative
snapshot and its review copy read-only in fresh Word sessions, records the
per-formula OOXML and Word reopen checks, and captures MathType formula
rasters for later human visual review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "Results" / "report_word_layout_20260804"
DEFAULT_SOURCE = (
    RESULTS / "authoritative_snapshot" / "MoSim_仿真分析报告_pre_mathtype_20260804.docx"
)
DEFAULT_REVIEW = RESULTS / "MoSim_仿真分析报告_MathType审阅副本_20260804.docx"
DEFAULT_MANIFEST = RESULTS / "MATHTYPE_FORMULA_MANIFEST.json"
DEFAULT_EVIDENCE = RESULTS / "MATHTYPE_REVIEW_COPY_ACCEPTANCE_20260804.json"
DEFAULT_VISUAL_ROOT = RESULTS / "MATHTYPE_REVIEW_COPY_VISUAL_20260804"

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
OFFICE_NS = "urn:schemas-microsoft-com:office:office"
NS = {"w": WORD_NS, "m": MATH_NS, "o": OFFICE_NS}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_instruction(value: str) -> str:
    return " ".join(value.split())


def inspect_docx(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path, "r") as archive:
        root = etree.fromstring(archive.read("word/document.xml"))

    tables = root.xpath(".//w:tbl", namespaces=NS)
    formula_tables: list[dict[str, object]] = []
    for index, table in enumerate(tables, start=1):
        mathtype_count = len(
            table.xpath(".//o:OLEObject[@ProgID='Equation.DSMT4']", namespaces=NS)
        )
        omath_count = len(table.xpath(".//m:oMath", namespaces=NS))
        if not mathtype_count and not omath_count:
            continue
        cells = table.xpath("./w:tr[1]/w:tc", namespaces=NS)
        formula_tables.append(
            {
                "table_index": index,
                "rows": len(table.xpath("./w:tr", namespaces=NS)),
                "columns": len(cells),
                "mathtype_objects": mathtype_count,
                "omath_objects": omath_count,
                "field_instructions": [
                    normalize_instruction(value)
                    for value in table.xpath(
                        ".//w:instrText/text()|.//w:fldSimple/@w:instr", namespaces=NS
                    )
                ],
                "right_cell_text": "".join(cells[1].xpath(".//w:t/text()", namespaces=NS))
                if len(cells) == 2
                else "",
            }
        )

    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "omath_count": len(root.xpath(".//m:oMath", namespaces=NS)),
        "mathtype_ole_count": len(
            root.xpath(".//o:OLEObject[@ProgID='Equation.DSMT4']", namespaces=NS)
        ),
        "table_count": len(tables),
        "formula_tables": formula_tables,
    }


def load_formulas(manifest_path: Path) -> list[dict[str, object]]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    formulas = payload.get("formulas")
    if not isinstance(formulas, list) or len(formulas) != 104:
        raise ValueError("Formula manifest must contain exactly 104 entries")
    result: list[dict[str, object]] = []
    for expected_id, formula in enumerate(formulas, start=1):
        if int(formula.get("formula_id", -1)) != expected_id:
            raise ValueError(f"Formula manifest is not contiguous at {expected_id}")
        result.append(
            {
                "formula_id": expected_id,
                "expected_number": str(formula["expected_number"]),
                "chapter": int(formula["chapter"]),
                "sequence": int(formula["sequence"]),
                "suffix": str(formula["suffix"]),
                "source_start_line": int(formula["source_start_line"]),
                "source_end_line": int(formula["source_end_line"]),
                "source_tex": str(formula["source_tex"]),
                "source_tex_sha256": str(formula["source_tex_sha256"]),
            }
        )
    return result


def select_formulas(
    formulas: list[dict[str, object]], formula_ids: str | None
) -> list[dict[str, object]]:
    if formula_ids is None:
        return formulas
    selected: set[int] = set()
    for item in formula_ids.split(","):
        value = item.strip()
        if not value:
            continue
        selected.add(int(value))
    if not selected:
        raise ValueError("--formula-ids must contain at least one formula id")
    if min(selected) < 1 or max(selected) > 104:
        raise ValueError("--formula-ids values must be between 1 and 104")
    return [formula for formula in formulas if int(formula["formula_id"]) in selected]


def expected_fields(formula: dict[str, object]) -> list[str]:
    if int(formula["formula_id"]) == 1:
        return [r"SEQ Chapter \c", r"SEQ Equation \* ARABIC"]
    return [
        r"SEQ Chapter \c",
        f"SEQ Equation \\r {int(formula['sequence'])} \\* ARABIC",
    ]


def validate_formula_structure(
    review_facts: dict[str, object], formula: dict[str, object]
) -> dict[str, object]:
    expected_number = f"({formula['expected_number']})"
    matches = [
        table
        for table in review_facts["formula_tables"]
        if table["right_cell_text"] == expected_number
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Formula {formula['formula_id']:03d} needs exactly one numbered table "
            f"{expected_number}, found {len(matches)}"
        )
    table = matches[0]
    if table["rows"] != 1 or table["columns"] != 2:
        raise RuntimeError(
            f"Formula {formula['formula_id']:03d} table shape is {table['rows']}x{table['columns']}"
        )
    if table["mathtype_objects"] != 1 or table["omath_objects"] != 0:
        raise RuntimeError(
            f"Formula {formula['formula_id']:03d} table object mix is "
            f"MathType={table['mathtype_objects']}, OMML={table['omath_objects']}"
        )
    required_fields = expected_fields(formula)
    if table["field_instructions"] != required_fields:
        raise RuntimeError(
            f"Formula {formula['formula_id']:03d} field codes are "
            f"{table['field_instructions']}, expected {required_fields}"
        )
    return {
        "status": "passed",
        "table_index": table["table_index"],
        "rows": table["rows"],
        "columns": table["columns"],
        "mathtype_objects": table["mathtype_objects"],
        "omath_objects": table["omath_objects"],
        "field_instructions": table["field_instructions"],
        "visible_number": table["right_cell_text"],
    }


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


def count_mathtype(document) -> int:
    count = 0
    for index in range(1, int(document.InlineShapes.Count) + 1):
        shape = document.InlineShapes.Item(index)
        try:
            if shape.OLEFormat.ProgID == "Equation.DSMT4":
                count += 1
        except Exception:
            continue
    return count


def table_visible_number(table) -> str:
    return table.Cell(1, 2).Range.Text.replace("\r", "").replace("\x07", "")


def find_word_table(document, expected_number: str):
    matches = []
    for index in range(1, int(document.Tables.Count) + 1):
        table = document.Tables.Item(index)
        if int(table.Rows.Count) != 1 or int(table.Columns.Count) != 2:
            continue
        if table_visible_number(table) == expected_number:
            matches.append(table)
    if len(matches) != 1:
        raise RuntimeError(
            f"Word reopen expected one table numbered {expected_number}, found {len(matches)}"
        )
    return matches[0]


def clear_clipboard() -> None:
    import win32clipboard

    for _ in range(10):
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
            finally:
                win32clipboard.CloseClipboard()
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("Could not clear the clipboard before visual capture")


def read_clipboard_image(deadline: float):
    """Read Word's PNG clipboard payload without relying on ImageGrab's picker."""
    from io import BytesIO

    from PIL import Image, ImageGrab
    import win32clipboard

    png_format = win32clipboard.RegisterClipboardFormat("PNG")
    last_error: str | None = None
    while time.monotonic() < deadline:
        opened = False
        try:
            win32clipboard.OpenClipboard()
            opened = True
            payload = win32clipboard.GetClipboardData(png_format)
            if isinstance(payload, bytes) and payload:
                with Image.open(BytesIO(payload)) as image:
                    return image.convert("RGB").copy()
        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass

        try:
            candidate = ImageGrab.grabclipboard()
            if candidate is not None and hasattr(candidate, "save"):
                return candidate.convert("RGB")
        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"
        time.sleep(0.2)
    raise RuntimeError(
        "Could not read a raster from the Windows clipboard"
        + (f" ({last_error})" if last_error else "")
    )


def capture_range_as_png(range_object, output: Path) -> dict[str, object]:
    from PIL import Image

    clear_clipboard()
    range_object.CopyAsPicture()
    image = read_clipboard_image(time.monotonic() + 20.0)
    low, high = image.convert("L").getextrema()
    contrast = high - low
    if image.width < 4 or image.height < 4 or contrast < 10:
        raise RuntimeError(
            f"Formula visual capture is blank for {output.name}: "
            f"size={image.size}, contrast={contrast}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG")
    return {
        "path": str(output.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_file(output),
        "bytes": output.stat().st_size,
        "width": image.width,
        "height": image.height,
        "grayscale_contrast": contrast,
        "status": "captured_nonblank",
    }


def word_pid(word) -> int | None:
    try:
        import win32process

        return int(win32process.GetWindowThreadProcessId(int(word.Hwnd))[1])
    except Exception:
        return None


def open_word_readonly(path: Path):
    import win32com.client

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    word.ScreenUpdating = False
    document = word.Documents.Open(
        str(path), ReadOnly=True, AddToRecentFiles=False, Visible=False
    )
    return word, document


def reopen_source(source: Path) -> dict[str, object]:
    import pythoncom

    pythoncom.CoInitialize()
    word = None
    document = None
    try:
        word, document = open_word_readonly(source)
        if int(document.OMaths.Count) != 103 or count_mathtype(document) != 1:
            raise RuntimeError("Authoritative snapshot failed its Word reopen object-count check")
        return {
            "status": "passed",
            "word_pid": word_pid(word),
            "omath_count": int(document.OMaths.Count),
            "mathtype_ole_count": count_mathtype(document),
        }
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            word.Quit(False)
        pythoncom.CoUninitialize()


def capture_review_visuals(
    review: Path,
    formulas: list[dict[str, object]],
    visual_root: Path,
    allow_partial: bool,
) -> tuple[dict[int, dict[str, object]], dict[str, object]]:
    import pythoncom

    pythoncom.CoInitialize()
    word = None
    document = None
    visuals: dict[int, dict[str, object]] = {}
    try:
        word, document = open_word_readonly(review)
        omath_count = int(document.OMaths.Count)
        mathtype_count = count_mathtype(document)
        if not allow_partial and (omath_count != 0 or mathtype_count != 104):
            raise RuntimeError(
                "Review copy failed Word reopen object-count check: "
                f"OMML={omath_count}, MathType={mathtype_count}"
            )
        for formula in formulas:
            formula_id = int(formula["formula_id"])
            table = find_word_table(document, f"({formula['expected_number']})")
            if int(table.Range.InlineShapes.Count) != 1:
                raise RuntimeError(
                    f"Formula {formula_id:03d} review table has "
                    f"{table.Range.InlineShapes.Count} inline shapes"
                )
            shape = table.Range.InlineShapes.Item(1)
            if shape.OLEFormat.ProgID != "Equation.DSMT4":
                raise RuntimeError(
                    f"Formula {formula_id:03d} Word OLE ProgID is {shape.OLEFormat.ProgID!r}"
                )
            visual = capture_range_as_png(
                shape.Range,
                visual_root / "review" / f"formula_{formula_id:03d}.png",
            )
            visual["ole_progid"] = "Equation.DSMT4"
            visual["table_start"] = int(table.Range.Start)
            visuals[formula_id] = visual
        return visuals, {
            "status": "passed",
            "word_pid": word_pid(word),
            "omath_count": omath_count,
            "mathtype_ole_count": mathtype_count,
        }
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            word.Quit(False)
        pythoncom.CoUninitialize()


def image_fit(image, max_width: int, max_height: int):
    copy = image.convert("RGB")
    copy.thumbnail((max_width, max_height))
    return copy


def build_contact_sheets(
    formulas: list[dict[str, object]],
    records: list[dict[str, object]],
    visual_root: Path,
) -> list[dict[str, object]]:
    from PIL import Image, ImageDraw, ImageFont

    by_id = {int(record["formula_id"]): record for record in records}
    columns = 3
    rows = 3
    panel_width = 650
    panel_height = 270
    font = ImageFont.load_default()
    output_dir = visual_root / "contact_sheets"
    output_dir.mkdir(parents=True, exist_ok=True)
    sheets: list[dict[str, object]] = []
    page_size = columns * rows
    for page_index, start in enumerate(range(0, len(formulas), page_size), start=1):
        group = formulas[start : start + page_size]
        canvas = Image.new("RGB", (columns * panel_width, rows * panel_height), "white")
        draw = ImageDraw.Draw(canvas)
        for offset, formula in enumerate(group):
            record = by_id[int(formula["formula_id"])]
            column = offset % columns
            row = offset // columns
            x = column * panel_width
            y = row * panel_height
            draw.rectangle((x, y, x + panel_width - 1, y + panel_height - 1), outline="black")
            draw.text(
                (x + 8, y + 8),
                f"{int(formula['formula_id']):03d} ({formula['expected_number']})",
                fill="black",
                font=font,
            )
            review_path = ROOT / str(record["visual"]["review"]["path"])
            with Image.open(review_path) as review_image:
                review_fit = image_fit(review_image, panel_width - 24, panel_height - 48)
            review_x = x + (panel_width - review_fit.width) // 2
            content_y = y + 48 + (panel_height - 48 - review_fit.height) // 2
            canvas.paste(review_fit, (review_x, content_y))
        output = output_dir / f"sheet_{page_index:02d}.png"
        canvas.save(output, "PNG")
        sheets.append(
            {
                "sheet": page_index,
                "formula_ids": [int(formula["formula_id"]) for formula in group],
                "path": str(output.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(output),
                "bytes": output.stat().st_size,
            }
        )
    return sheets


def normalized_warnings(formula: dict[str, object]) -> tuple[str, list[str]]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from mathtype_tex_compat import normalize_tex_for_mathtype

        return normalize_tex_for_mathtype(str(formula["source_tex"]))
    finally:
        sys.path.pop(0)


def manual_queue(formulas: list[dict[str, object]]) -> list[dict[str, object]]:
    queue: list[dict[str, object]] = []
    for formula in formulas:
        normalized_tex, warnings = normalized_warnings(formula)
        if not any("double-struck" in warning for warning in warnings):
            continue
        queue.append(
            {
                "formula_id": formula["formula_id"],
                "expected_number": formula["expected_number"],
                "source_start_line": formula["source_start_line"],
                "source_end_line": formula["source_end_line"],
                "source_tex_sha256": formula["source_tex_sha256"],
                "normalized_tex": normalized_tex,
                "normalization_warnings": warnings,
                "status": "manual_semantic_font_review_required",
                "reason": (
                    "The installed MathType TeX translator rejects the source double-struck "
                    "indicator glyph and used bold 1 as a compatibility fallback."
                ),
                "manual_action": (
                    "Open this Equation.DSMT4 object in MathType and replace each bold 1 "
                    "indicator with the intended double-struck glyph, then save and rerun "
                    "the per-formula visual/reopen acceptance."
                ),
            }
        )
    return queue


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def build_plan(args: argparse.Namespace, selected: list[dict[str, object]]) -> dict[str, object]:
    source_facts = inspect_docx(args.source)
    review_facts = inspect_docx(args.review)
    if source_facts["omath_count"] != 103 or source_facts["mathtype_ole_count"] != 1:
        raise ValueError("Authoritative snapshot structure changed before validation")
    return {
        "schema": "mosim.report.mathtype_review_copy_acceptance.v1",
        "mode": "execute" if args.execute else "dry_run",
        "source": source_facts,
        "review_copy": review_facts,
        "manifest": {
            "path": str(args.manifest.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(args.manifest),
            "formula_count": 104,
            "selected_formula_ids": [int(formula["formula_id"]) for formula in selected],
        },
        "evidence": str(args.evidence.relative_to(ROOT)).replace("\\", "/"),
        "visual_root": str(args.visual_root.relative_to(ROOT)).replace("\\", "/"),
        "allow_partial": args.allow_partial,
        "allowed_actions": [
            "open the source snapshot and review copy read-only in new Word processes",
            "copy formula renderings to task-owned evidence PNG files",
            "write acceptance JSON and contact sheets below Results",
        ],
        "forbidden_actions": [
            "save, update fields, modify, or overwrite either DOCX input",
            "attach to a pre-existing Word process",
            "terminate, restart, or automate a pre-existing MathType process",
        ],
    }


def execute(
    args: argparse.Namespace, plan: dict[str, object], selected: list[dict[str, object]]
) -> dict[str, object]:
    before_processes = process_snapshot()
    existing_word = [
        process for process in before_processes if str(process["name"]).lower() == "winword.exe"
    ]
    if existing_word:
        raise RuntimeError(f"Validator requires no pre-existing Word process: {existing_word}")
    if args.evidence.exists() or args.visual_root.exists():
        raise FileExistsError(
            "Validator refuses to overwrite existing acceptance evidence or visual root"
        )

    source_reopen = reopen_source(args.source)
    review_visuals, review_reopen = capture_review_visuals(
        args.review, selected, args.visual_root, args.allow_partial
    )
    review_facts = inspect_docx(args.review)
    records: list[dict[str, object]] = []
    for formula in selected:
        formula_id = int(formula["formula_id"])
        records.append(
            {
                "formula_id": formula_id,
                "expected_number": formula["expected_number"],
                "source_start_line": formula["source_start_line"],
                "source_end_line": formula["source_end_line"],
                "source_tex_sha256": formula["source_tex_sha256"],
                "reopen_acceptance": {
                    "status": "passed",
                    "fresh_word_session": review_reopen,
                    "ole_progid": review_visuals[formula_id]["ole_progid"],
                },
                "structure_acceptance": validate_formula_structure(review_facts, formula),
                "visual": {
                    "review": review_visuals[formula_id],
                    "status": "nonblank_raster_ready_for_human_review",
                },
            }
        )
    sheets = build_contact_sheets(selected, records, args.visual_root)
    queue = manual_queue(selected)
    result: dict[str, object] = dict(plan)
    result.update(
        {
            "status": "all_selected_formula_reopen_and_structure_checks_passed_pending_human_visual_review",
            "source_reopen": source_reopen,
            "review_reopen": review_reopen,
            "source_unchanged": sha256_file(args.source) == plan["source"]["sha256"],
            "review_copy_after_validation": inspect_docx(args.review),
            "formula_records": records,
            "contact_sheets": sheets,
            "manual_semantic_review_queue": queue,
            "preexisting_mathtype_servers": [
                process
                for process in before_processes
                if str(process["name"]).lower() == "mathtype.exe"
            ],
            "remaining_word_mathtype_processes": process_snapshot(),
        }
    )
    write_json(args.evidence, result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--visual-root", type=Path, default=DEFAULT_VISUAL_ROOT)
    parser.add_argument("--formula-ids", default=None)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    args.source = args.source.resolve()
    args.review = args.review.resolve()
    args.manifest = args.manifest.resolve()
    args.evidence = args.evidence.resolve()
    args.visual_root = args.visual_root.resolve()
    for path in (args.source, args.review, args.manifest):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.source == args.review:
        raise ValueError("Source and review inputs must be different files")
    formulas = load_formulas(args.manifest)
    selected = select_formulas(formulas, args.formula_ids)
    plan = build_plan(args, selected)
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(execute(args, plan, selected), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
