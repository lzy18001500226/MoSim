#!/usr/bin/env python3
"""Run an observable MathType native-OMML conversion pilot.

The command is intentionally limited to an output copy of the review document.
It writes a session marker before calling MathType so a blocked ConvertEqns
dialog can be inspected without confusing the pilot-owned Word process with
an unrelated desktop session.  A pilot can select either one retained OMML
formula or the full disposable document content; the latter keeps the dialog
on its existing "current selection" option while exercising all retained OMML
formulas in one output copy.
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
DEFAULT_SOURCE = (
    ROOT
    / "Results"
    / "report_word_layout_20260804"
    / "MoSim_仿真分析报告_MathType审阅副本_20260804.docx"
)
DEFAULT_MANIFEST = ROOT / "Results" / "report_word_layout_20260804" / "MATHTYPE_FORMULA_MANIFEST.json"
DEFAULT_OUTPUT = PILOT_DIR / "omml_convert_dialog_formula_043_20260805.docx"
DEFAULT_SESSION = PILOT_DIR / "omml_convert_dialog_formula_043_20260805_session.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process_snapshot() -> list[dict[str, object]]:
    import psutil

    processes: list[dict[str, object]] = []
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


def count_mathtype(document) -> int:
    count = 0
    for index in range(1, int(document.InlineShapes.Count) + 1):
        shape = document.InlineShapes.Item(index)
        try:
            if str(shape.OLEFormat.ProgID) == "Equation.DSMT4":
                count += 1
        except Exception:
            continue
    return count


def expected_object_counts(
    selection_scope: str, before_omaths: int, before_mathtype: int
) -> tuple[int, int]:
    if selection_scope == "native_omml":
        return before_omaths - 1, before_mathtype + 1
    if selection_scope == "document_content":
        return 0, before_mathtype + before_omaths
    raise ValueError(f"Unsupported selection scope: {selection_scope}")


def select_conversion_range(document, selection_scope: str, native_omath_index: int):
    if selection_scope == "native_omml":
        target = document.OMaths.Item(native_omath_index).Range.Duplicate
    elif selection_scope == "document_content":
        target = document.Content.Duplicate
    else:
        raise ValueError(f"Unsupported selection scope: {selection_scope}")
    return target, {
        "scope": selection_scope,
        "start": int(target.Start),
        "end": int(target.End),
    }


def write_session(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_formula(manifest: Path, formula_id: int) -> dict[str, object]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    formulas = [item for item in payload["formulas"] if int(item["formula_id"]) == formula_id]
    if len(formulas) != 1:
        raise ValueError(f"Manifest has {len(formulas)} entries for formula {formula_id}")
    return formulas[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--formula-id", type=int, default=43)
    parser.add_argument("--native-omath-index", type=int, default=1)
    parser.add_argument(
        "--selection-scope",
        choices=("native_omml", "document_content"),
        default="native_omml",
        help="Keep MathType on current selection while selecting one OMML or all document content.",
    )
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for attribute in ("source", "manifest", "output", "session"):
        setattr(args, attribute, getattr(args, attribute).resolve())
    if not args.source.is_file() or not args.manifest.is_file():
        raise FileNotFoundError("Source review copy or formula manifest is missing")
    if args.output.exists() or args.session.exists():
        raise FileExistsError("Pilot output or session marker already exists")
    formula = load_formula(args.manifest, args.formula_id)
    before = process_snapshot()
    preexisting_word = [item for item in before if str(item["name"]).lower() == "winword.exe"]
    if preexisting_word:
        raise RuntimeError(f"Pilot requires no pre-existing Word process: {preexisting_word}")

    session: dict[str, object] = {
        "schema": "mosim.report.mathtype_omml_convert_dialog_pilot.v1",
        "mode": "execute" if args.execute else "dry_run",
        "formula_id": args.formula_id,
        "expected_number": formula["expected_number"],
        "native_omath_index": args.native_omath_index,
        "selection_scope": args.selection_scope,
        "source": str(args.source.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256_before": sha256_file(args.source),
        "output": str(args.output.relative_to(ROOT)).replace("\\", "/"),
        "manifest": str(args.manifest.relative_to(ROOT)).replace("\\", "/"),
        "command": "MathTypeCommands.UILib.MTCommand_ConvertEqns",
        "preexisting_word_processes": preexisting_word,
        "preexisting_mathtype_servers": [
            item for item in before if str(item["name"]).lower() == "mathtype.exe"
        ],
        "authoritative_report_touched": False,
        "status": "prepared",
    }
    write_session(args.session, session)
    if not args.execute:
        print(json.dumps(session, ensure_ascii=False, indent=2))
        return 0

    import pythoncom
    import win32com.client
    shutil.copy2(args.source, args.output)
    word = None
    document = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = True
        word.DisplayAlerts = 0
        document = word.Documents.Open(
            str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=True
        )
        launched_word = [
            item
            for item in process_snapshot()
            if str(item["name"]).lower() == "winword.exe"
            and item["pid"] not in {process["pid"] for process in before}
        ]
        if len(launched_word) != 1:
            raise RuntimeError(
                "Could not identify exactly one pilot-owned Word process: "
                f"{launched_word}"
            )
        session["pilot_word_pid"] = int(launched_word[0]["pid"])
        session["before_omaths"] = int(document.OMaths.Count)
        session["before_mathtype_objects"] = count_mathtype(document)
        session["before_tables"] = int(document.Tables.Count)
        if (
            args.selection_scope == "native_omml"
            and (args.native_omath_index < 1 or args.native_omath_index > int(document.OMaths.Count))
        ):
            raise ValueError("--native-omath-index is outside the review copy OMML range")
        expected_omaths, expected_mathtype = expected_object_counts(
            args.selection_scope,
            int(session["before_omaths"]),
            int(session["before_mathtype_objects"]),
        )
        session["expected_after_omaths"] = expected_omaths
        session["expected_after_mathtype_objects"] = expected_mathtype
        selection_range, selection_contract = select_conversion_range(
            document, args.selection_scope, args.native_omath_index
        )
        session["selection"] = selection_contract
        selection_range.Select()
        document.Activate()
        word.Activate()
        session["status"] = "convert_command_started_waiting_for_return"
        write_session(args.session, session)
        word.Run(str(session["command"]))
        session["after_omaths"] = int(document.OMaths.Count)
        session["after_mathtype_objects"] = count_mathtype(document)
        session["after_tables"] = int(document.Tables.Count)
        document.Save()
        session["conversion_applied"] = (
            session["after_omaths"] == expected_omaths
            and session["after_mathtype_objects"] == expected_mathtype
        )
        session["status"] = (
            "convert_command_applied_expected_object_delta"
            if session["conversion_applied"]
            else "convert_command_returned_without_expected_object_delta"
        )
    except Exception as error:
        session["status"] = "failed"
        session["failure"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        session["source_sha256_after"] = sha256_file(args.source)
        session["source_unchanged"] = (
            session["source_sha256_after"] == session["source_sha256_before"]
        )
        session["output_exists"] = args.output.is_file()
        session["output_sha256"] = sha256_file(args.output) if args.output.is_file() else None
        write_session(args.session, session)
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

    print(json.dumps(session, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
