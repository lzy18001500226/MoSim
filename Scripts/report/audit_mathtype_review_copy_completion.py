#!/usr/bin/env python3
"""Build a complete, evidence-bounded MathType review-copy audit.

The authoritative report and the review copy are opened read-only.  This
script joins the 96 completed Equation.DSMT4 checks with fresh visual evidence
for the eight retained OMML formulas, so all 104 display formulas have an
ordered result record.  It deliberately reports outstanding manual work
instead of treating placeholders or visual glyph fallbacks as successful
conversions.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results" / "report_word_layout_20260804"
DEFAULT_SOURCE = ROOT / "Docs" / "报告" / "MoSim_仿真分析报告.docx"
DEFAULT_REVIEW = RESULT_ROOT / "MoSim_仿真分析报告_MathType审阅副本_20260804.docx"
DEFAULT_MANIFEST = RESULT_ROOT / "MATHTYPE_FORMULA_MANIFEST.json"
DEFAULT_CONVERSION = RESULT_ROOT / "MATHTYPE_REVIEW_COPY_CONVERSION_20260804.json"
DEFAULT_CHECKPOINT = RESULT_ROOT / "MATHTYPE_REVIEW_COPY_CONVERSION_20260804.jsonl"
DEFAULT_ACCEPTANCE = RESULT_ROOT / "MATHTYPE_REVIEW_COPY_ACCEPTANCE_20260805_compatible96.json"
DEFAULT_EVIDENCE = RESULT_ROOT / "MATHTYPE_REVIEW_COPY_FINAL_AUDIT_20260805.json"
DEFAULT_QUEUE = RESULT_ROOT / "MATHTYPE_REVIEW_COPY_MANUAL_QUEUE_20260805.md"
DEFAULT_VISUAL_ROOT = RESULT_ROOT / "mathtype_review_final_audit_20260805"
EMF_RENDERER = Path(__file__).resolve().parent / "render_emf_to_png.ps1"
PILOT_VISUAL = (
    RESULT_ROOT
    / "mathtype_conversion_pilot"
    / "mathtype_tex_formula_011_iff_pilot_20260805_visual.json"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_mathtype_report_review_copy as conversion_runner  # noqa: E402
import validate_mathtype_review_copy as validator  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected an object in {path}")
    return payload


def load_manifest(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    formulas = payload.get("formulas")
    if not isinstance(formulas, list) or len(formulas) != 104:
        raise ValueError("Formula manifest must contain exactly 104 entries")
    expected = list(range(1, 105))
    actual = [int(item["formula_id"]) for item in formulas]
    if actual != expected:
        raise ValueError("Formula manifest IDs are not contiguous from 1 through 104")
    return formulas


def formula_lookup(formulas: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(formula["formula_id"]): formula for formula in formulas}


def process_snapshot() -> list[dict[str, Any]]:
    import psutil

    processes: list[dict[str, Any]] = []
    for process in psutil.process_iter(["pid", "name", "create_time", "status"]):
        name = (process.info.get("name") or "").lower()
        if name in {"winword.exe", "mathtype.exe"}:
            processes.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "create_time": process.info.get("create_time"),
                    "status": process.info.get("status"),
                }
            )
    return processes


def clear_clipboard_retry(timeout: float = 15.0) -> None:
    import win32clipboard

    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        opened = False
        try:
            win32clipboard.OpenClipboard()
            opened = True
            win32clipboard.EmptyClipboard()
            return
        except Exception as error:
            last_error = error
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
        time.sleep(0.25)
    raise RuntimeError(f"Could not clear the Windows clipboard: {last_error}")


def read_clipboard_bytes(format_id: int, timeout: float = 15.0) -> bytes:
    import win32clipboard

    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        opened = False
        try:
            win32clipboard.OpenClipboard()
            opened = True
            payload = win32clipboard.GetClipboardData(format_id)
            if isinstance(payload, (bytes, bytearray)) and payload:
                return bytes(payload)
        except Exception as error:
            last_error = error
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
        time.sleep(0.25)
    raise RuntimeError(
        f"Clipboard format {format_id} was not available after {timeout:.1f}s: {last_error}"
    )


def capture_omml_as_emf(range_object, output: Path) -> dict[str, Any]:
    """Capture Word OMML as CF_ENHMETAFILE, which Word publishes reliably."""
    clear_clipboard_retry()
    range_object.CopyAsPicture()
    payload = read_clipboard_bytes(14)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    return {
        "path": relative(output),
        "sha256": sha256_file(output),
        "bytes": output.stat().st_size,
        "clipboard_format": "CF_ENHMETAFILE",
        "status": "captured_emf",
    }


def render_emf_to_png(emf: Path, png: Path) -> dict[str, Any]:
    if not EMF_RENDERER.is_file():
        raise FileNotFoundError(EMF_RENDERER)
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(EMF_RENDERER),
            "-InputPath",
            str(emf),
            "-OutputPath",
            str(png),
            "-Scale",
            "1.0",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30.0,
    )
    if not png.is_file():
        raise RuntimeError(
            "EMF renderer returned without creating PNG: " + completed.stdout[-500:]
        )
    from PIL import Image

    with Image.open(png) as image:
        rgb = image.convert("RGB")
        low, high = rgb.convert("L").getextrema()
        visual = {
            "path": relative(png),
            "sha256": sha256_file(png),
            "bytes": png.stat().st_size,
            "width": rgb.width,
            "height": rgb.height,
            "grayscale_contrast": high - low,
            "status": "captured_nonblank_emf_render",
        }
    if visual["width"] < 4 or visual["height"] < 4 or visual["grayscale_contrast"] < 10:
        raise RuntimeError(f"EMF render is blank or too small: {visual}")
    return visual


def conversion_state(
    checkpoint: Path, formulas: list[dict[str, Any]]
) -> tuple[list[int], list[dict[str, Any]]]:
    records = conversion_runner.read_checkpoint(checkpoint)
    completed = conversion_runner.completed_formula_ids(records)
    unresolved = conversion_runner.manual_placeholder_records(records)
    unresolved_ids = [int(record["formula_id"]) for record in unresolved]
    expected = set(range(2, 105))
    if set(completed) & set(unresolved_ids):
        raise ValueError("A formula cannot be completed and unresolved at the same time")
    if set(completed) | set(unresolved_ids) != expected:
        raise ValueError(
            "Checkpoint does not classify every formula after the preserved MathType formula"
        )
    if len(unresolved) != 8:
        raise ValueError(f"Expected eight retained OMML formulas, found {len(unresolved)}")
    if sorted(unresolved_ids) != [43, 44, 75, 76, 77, 78, 79, 80]:
        raise ValueError(f"Unexpected retained OMML formula IDs: {sorted(unresolved_ids)}")
    formula_ids = set(formula_lookup(formulas))
    if not set(completed).issubset(formula_ids) or not set(unresolved_ids).issubset(formula_ids):
        raise ValueError("Checkpoint contains a formula outside the manifest")
    return completed, sorted(unresolved, key=lambda item: int(item["formula_id"]))


def source_contract(
    source: Path, conversion: dict[str, Any], acceptance: dict[str, Any]
) -> dict[str, Any]:
    facts = validator.inspect_docx(source)
    expected_hash = str(conversion["authoritative_report"]["sha256"])
    if facts["sha256"] != expected_hash:
        raise ValueError("Authoritative report hash no longer matches the conversion baseline")
    if facts["omath_count"] != 103 or facts["mathtype_ole_count"] != 1:
        raise ValueError("Authoritative report object inventory changed")
    if str(acceptance["source"]["sha256"]) != expected_hash:
        raise ValueError("Acceptance evidence refers to a different authoritative source")
    return facts


def review_contract(
    review: Path,
    conversion: dict[str, Any],
    acceptance: dict[str, Any],
    completed_ids: list[int],
    unresolved_records: list[dict[str, Any]],
) -> dict[str, Any]:
    facts = validator.inspect_docx(review)
    expected_hash = str(conversion["output_sha256"])
    if facts["sha256"] != expected_hash:
        raise ValueError("Review copy changed after the recorded conversion")
    if str(acceptance["review_copy"]["sha256"]) != expected_hash:
        raise ValueError("Acceptance evidence refers to a different review copy")
    if facts["omath_count"] != len(unresolved_records):
        raise ValueError("Review copy OMML count does not match retained manual placeholders")
    if facts["mathtype_ole_count"] != 1 + len(completed_ids):
        raise ValueError("Review copy MathType count does not match completed checkpoints")
    if len(facts["formula_tables"]) != 1 + len(completed_ids):
        raise ValueError("Review copy has an unexpected number of MathType formula tables")
    return facts


def acceptance_records(
    acceptance: dict[str, Any], completed_ids: list[int]
) -> dict[int, dict[str, Any]]:
    records = acceptance.get("formula_records")
    if not isinstance(records, list):
        raise ValueError("Existing acceptance has no formula records")
    by_id = {int(record["formula_id"]): record for record in records}
    expected = {1, *completed_ids}
    if set(by_id) != expected:
        raise ValueError("Existing acceptance does not cover exactly the completed MathType formulas")
    return by_id


def capture_retained_omml_visuals(
    review: Path,
    unresolved_records: list[dict[str, Any]],
    visual_root: Path,
) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    import pythoncom

    existing_word = [
        process
        for process in process_snapshot()
        if str(process["name"]).lower() == "winword.exe"
    ]
    if existing_word:
        raise RuntimeError(
            "Final audit requires no pre-existing Word process: " f"{existing_word}"
        )
    if visual_root.exists():
        raise FileExistsError(f"Refusing to overwrite visual evidence: {visual_root}")

    pythoncom.CoInitialize()
    word = None
    document = None
    visuals: dict[int, dict[str, Any]] = {}
    try:
        word, document = validator.open_word_readonly(review)
        omath_count = int(document.OMaths.Count)
        mathtype_count = validator.count_mathtype(document)
        if omath_count != len(unresolved_records) or mathtype_count != 96:
            raise RuntimeError(
                "Fresh Word reopen count mismatch: "
                f"OMML={omath_count}, MathType={mathtype_count}"
            )
        for record in unresolved_records:
            formula_id = int(record["formula_id"])
            native_index = int(record["native_omath_index"])
            if native_index < 1 or native_index > omath_count:
                raise RuntimeError(
                    f"Formula {formula_id:03d} native OMML index {native_index} is invalid"
                )
            equation_range = document.OMaths.Item(native_index).Range
            emf_path = visual_root / "source_emf" / f"formula_{formula_id:03d}.emf"
            png_path = visual_root / "review" / f"formula_{formula_id:03d}.png"
            emf_visual = capture_omml_as_emf(equation_range, emf_path)
            visual = render_emf_to_png(emf_path, png_path)
            visual["source_emf"] = emf_visual
            visual["object_type"] = "OMML"
            visual["native_omath_index"] = native_index
            visuals[formula_id] = visual
        return visuals, {
            "status": "passed_readonly_reopen",
            "omath_count": omath_count,
            "mathtype_ole_count": mathtype_count,
            "preexisting_mathtype_servers": [
                process
                for process in process_snapshot()
                if str(process["name"]).lower() == "mathtype.exe"
            ],
        }
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            word.Quit(False)
        pythoncom.CoUninitialize()


def semantic_queue_entry(formula: dict[str, Any]) -> dict[str, Any]:
    formula_id = int(formula["formula_id"])
    return {
        "formula_id": formula_id,
        "expected_number": formula["expected_number"],
        "source_start_line": formula["source_start_line"],
        "source_end_line": formula["source_end_line"],
        "source_tex_sha256": formula["source_tex_sha256"],
        "queue_status": "manual_semantic_font_review_required",
        "reason": (
            "The installed MathType TeX translator replaced source double-struck "
            "mathbb{1} indicator glyphs with bold 1 in an otherwise editable OLE object."
        ),
        "manual_steps": [
            "Open this Equation.DSMT4 object in MathType from the review copy.",
            "Replace every bold 1 that corresponds to mathbb{1} with the intended double-struck 1 glyph.",
            "Preserve all interval subscripts and the displayed equation number.",
            "Save the review copy and rerun the final audit before accepting the formula semantically.",
        ],
        "completion_check": "Fresh Word reopen reports Equation.DSMT4 and the visual review shows double-struck 1, not bold 1.",
    }


def relation_queue_entry(formula: dict[str, Any], pilot: dict[str, Any]) -> dict[str, Any]:
    return {
        "formula_id": 11,
        "expected_number": formula["expected_number"],
        "source_start_line": formula["source_start_line"],
        "source_end_line": formula["source_end_line"],
        "source_tex_sha256": formula["source_tex_sha256"],
        "queue_status": "manual_relation_symbol_review_required",
        "reason": (
            "The review-copy Equation.DSMT4 object renders the source Longleftrightarrow "
            "as a replacement diamond.  A fresh isolated Texvc iff pilot rendered the same "
            "replacement glyph, so another TeX spelling is not accepted as a repair."
        ),
        "pilot_visual": pilot["visual"],
        "manual_steps": [
            "Open formula (2-11) in MathType from the review copy.",
            "Replace the visible replacement diamond using MathType's relation palette with a bidirectional logical implication arrow.",
            "Keep pass_i, completed_i, both conjunctions, finite(e_T,i), and the 5 m threshold unchanged.",
            "Save the review copy and rerun the final audit before marking visual acceptance passed.",
        ],
        "completion_check": "The visual evidence shows a bidirectional implication arrow and no replacement diamond.",
    }


def rebuild_queue_entry(
    formula: dict[str, Any], record: dict[str, Any]
) -> dict[str, Any]:
    sequence = int(formula["sequence"])
    return {
        "formula_id": int(formula["formula_id"]),
        "expected_number": formula["expected_number"],
        "source_start_line": formula["source_start_line"],
        "source_end_line": formula["source_end_line"],
        "source_tex_sha256": formula["source_tex_sha256"],
        "normalized_tex": record["normalized_tex"],
        "normalized_tex_sha256": record["normalized_tex_sha256"],
        "normalization_warnings": record["normalization_warnings"],
        "native_omath_index": record["native_omath_index"],
        "queue_status": "manual_math_type_rebuild_required",
        "failure": record["failure"],
        "reason": (
            "The bounded MathType TeX route did not create an Equation.DSMT4 object. "
            "The original OMML formula is intentionally retained at this native index."
        ),
        "manual_steps": [
            "Locate the retained OMML formula by its expected number and native_omath_index in the review copy.",
            "Clone an adjacent accepted one-row, two-column MathType equation table at the same location.",
            "Create exactly one Equation.DSMT4 object in the left cell and build the supplied normalized_tex in MathType.",
            "Set the right-cell fields to SEQ Chapter \\c and SEQ Equation \\r "
            f"{sequence} \\* ARABIC so its visible number is ({formula['expected_number']}).",
            "Delete the retained OMML only after the new OLE object has been saved successfully.",
            "Save the review copy and rerun the final audit; this formula must then have zero OMML and one Equation.DSMT4 object.",
        ],
        "completion_check": (
            "Fresh Word reopen reports one Equation.DSMT4 object in a 1x2 formula table, "
            f"zero OMML, and visible number ({formula['expected_number']})."
        ),
    }


def human_visual_status(formula_id: int) -> str:
    if formula_id in {2, 3, 4}:
        return "readable_but_manual_semantic_font_review_required"
    if formula_id == 11:
        return "failed_replacement_relation_glyph_detected"
    return "passed_human_contact_sheet_review_no_blank_or_clipping_detected"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing audit evidence: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_queue_markdown(path: Path, queue: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing manual queue: {path}")
    rows = [
        "# MathType Review Copy Manual Queue",
        "",
        "This queue is generated from the immutable-source final audit. It does not authorize edits to the authoritative report.",
        "",
        "| Formula ID | Display number | Queue status | Source lines | Completion check |",
        "|---:|---|---|---|---|",
    ]
    for item in queue:
        rows.append(
            "| {formula_id} | ({expected_number}) | {queue_status} | {source_start_line}-{source_end_line} | {completion_check} |".format(
                **item
            )
        )
    for item in queue:
        rows.extend(
            [
                "",
                f"## Formula {int(item['formula_id']):03d} ({item['expected_number']})",
                "",
                f"Reason: {item['reason']}",
                "",
                "Required steps:",
                *[f"- {step}" for step in item["manual_steps"]],
            ]
        )
        if "normalized_tex" in item:
            rows.extend(["", "```latex", str(item["normalized_tex"]), "```"])
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    formulas = load_manifest(args.manifest)
    formula_by_id = formula_lookup(formulas)
    conversion = read_json(args.conversion)
    acceptance = read_json(args.acceptance)
    pilot = read_json(PILOT_VISUAL)
    if not pilot.get("authoritative_report_untouched"):
        raise ValueError("Formula 11 relation pilot did not prove the authoritative report untouched")
    if pilot.get("reopen", {}).get("ole_progid") != "Equation.DSMT4":
        raise ValueError("Formula 11 relation pilot has no editable MathType OLE evidence")

    completed_ids, unresolved_records = conversion_state(args.checkpoint, formulas)
    source = source_contract(args.source, conversion, acceptance)
    review = review_contract(
        args.review, conversion, acceptance, completed_ids, unresolved_records
    )
    accepted_by_id = acceptance_records(acceptance, completed_ids)

    converted_records: dict[int, dict[str, Any]] = {}
    for formula_id, existing in accepted_by_id.items():
        formula = formula_by_id[formula_id]
        structure = validator.validate_formula_structure(review, formula)
        visual = deepcopy(existing["visual"])
        visual["status"] = human_visual_status(formula_id)
        visual["human_contact_sheet_review"] = True
        converted_records[formula_id] = {
            "formula_id": formula_id,
            "expected_number": formula["expected_number"],
            "source_start_line": formula["source_start_line"],
            "source_end_line": formula["source_end_line"],
            "source_tex_sha256": formula["source_tex_sha256"],
            "conversion_status": (
                "preexisting_equation_dsmt4_preserved"
                if formula_id == 1
                else "converted_to_equation_dsmt4"
            ),
            "reopen_acceptance": existing["reopen_acceptance"],
            "structure_acceptance": structure,
            "visual": visual,
        }

    retained_visuals: dict[int, dict[str, Any]] = {}
    retained_reopen: dict[str, Any] | None = None
    if args.execute:
        retained_visuals, retained_reopen = capture_retained_omml_visuals(
            args.review, unresolved_records, args.visual_root
        )

    records: list[dict[str, Any]] = []
    unresolved_by_id = {int(record["formula_id"]): record for record in unresolved_records}
    for formula in formulas:
        formula_id = int(formula["formula_id"])
        if formula_id in converted_records:
            records.append(converted_records[formula_id])
            continue
        record = unresolved_by_id[formula_id]
        visual = retained_visuals.get(formula_id)
        records.append(
            {
                "formula_id": formula_id,
                "expected_number": formula["expected_number"],
                "source_start_line": formula["source_start_line"],
                "source_end_line": formula["source_end_line"],
                "source_tex_sha256": formula["source_tex_sha256"],
                "conversion_status": "retained_omml_pending_manual_math_type_rebuild",
                "reopen_acceptance": {
                    "status": "not_passed_pending_manual_conversion",
                    "fresh_word_session": retained_reopen,
                    "object_type": "OMML",
                    "native_omath_index": record["native_omath_index"],
                },
                "structure_acceptance": {
                    "status": "not_passed_pending_manual_conversion",
                    "mathtype_objects": 0,
                    "omath_objects": 1,
                    "native_omath_index": record["native_omath_index"],
                },
                "visual": {
                    "review": visual,
                    "status": "captured_retained_omml_pending_manual_conversion",
                },
            }
        )

    if len(records) != 104 or [item["formula_id"] for item in records] != list(range(1, 105)):
        raise RuntimeError("Final audit did not produce 104 ordered formula records")

    queue = [
        *(semantic_queue_entry(formula_by_id[item]) for item in (2, 3, 4)),
        relation_queue_entry(formula_by_id[11], pilot),
        *(rebuild_queue_entry(formula_by_id[int(item["formula_id"])], item) for item in unresolved_records),
    ]
    queue.sort(key=lambda item: int(item["formula_id"]))

    contact_sheets: list[dict[str, Any]] = []
    if args.execute:
        contact_sheets = validator.build_contact_sheets(formulas, records, args.visual_root)

    status = (
        "review_copy_has_92_full_passes_and_12_explicit_manual_queue_items"
        if args.execute
        else "dry_run_ready_for_final_audit"
    )
    return {
        "schema": "mosim.report.mathtype_review_copy_final_audit.v1",
        "mode": "execute" if args.execute else "dry_run",
        "status": status,
        "claim_boundary": (
            "This audit proves 96 Equation.DSMT4 objects (92 fully accepted after visual review), "
            "eight retained OMML formulas requiring manual rebuild, and four editable-object "
            "semantic/visual repairs. It does not claim all 104 formulas are already accepted MathType objects."
        ),
        "authoritative_report": source,
        "authoritative_report_unchanged": True,
        "review_copy": review,
        "review_copy_reopen_for_retained_omml": retained_reopen,
        "manifest": {
            "path": relative(args.manifest),
            "sha256": sha256_file(args.manifest),
            "formula_count": 104,
        },
        "conversion_evidence": {
            "path": relative(args.conversion),
            "sha256": sha256_file(args.conversion),
            "completed_formula_ids": completed_ids,
            "retained_omml_formula_ids": [int(item["formula_id"]) for item in unresolved_records],
        },
        "existing_accepted_visual_evidence": {
            "path": relative(args.acceptance),
            "sha256": sha256_file(args.acceptance),
            "review_copy_sha256_matched": True,
            "human_contact_sheets_reviewed": True,
        },
        "formula_records": records,
        "contact_sheets": contact_sheets,
        "manual_queue": queue,
        "summary": {
            "formula_count": 104,
            "equation_dsmt4_object_count": 96,
            "fully_accepted_formula_count": 92,
            "editable_math_type_semantic_or_visual_review_count": 4,
            "retained_omml_manual_rebuild_count": 8,
            "manual_queue_count": len(queue),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--conversion", type=Path, default=DEFAULT_CONVERSION)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--acceptance", type=Path, default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--manual-queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--visual-root", type=Path, default=DEFAULT_VISUAL_ROOT)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for attribute in (
        "source",
        "review",
        "manifest",
        "conversion",
        "checkpoint",
        "acceptance",
        "evidence",
        "manual_queue",
        "visual_root",
    ):
        setattr(args, attribute, getattr(args, attribute).resolve())
    for path in (
        args.source,
        args.review,
        args.manifest,
        args.conversion,
        args.checkpoint,
        args.acceptance,
        PILOT_VISUAL,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.source == args.review:
        raise ValueError("The review copy must differ from the authoritative report")
    if args.execute and (args.evidence.exists() or args.manual_queue.exists()):
        raise FileExistsError("Final audit refuses to overwrite evidence or manual queue")
    result = build_audit(args)
    if not args.execute:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    write_json(args.evidence, result)
    write_queue_markdown(args.manual_queue, result["manual_queue"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
