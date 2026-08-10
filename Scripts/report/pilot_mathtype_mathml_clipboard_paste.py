#!/usr/bin/env python3
"""Exercise Word's MathML clipboard route on one disposable MathType pilot.

The authoritative report is never opened.  This pilot copies a small golden
document, replaces its one native Word display equation by pasting the selected
manifest formula as the registered ``MathML Presentation`` clipboard format,
then records whether Word creates an ``Equation.DSMT4`` object after any
MathType paste-choice dialog has been resolved.
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
DEFAULT_MANIFEST = ROOT / "Results" / "report_word_layout_20260804" / "MATHTYPE_FORMULA_MANIFEST.json"
DEFAULT_SOURCE = PILOT_DIR / "source_omml_pilot.docx"
DEFAULT_OUTPUT = PILOT_DIR / "mathml_clipboard_formula_043_20260805.docx"
DEFAULT_EVIDENCE = PILOT_DIR / "mathml_clipboard_formula_043_20260805.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


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
            if str(shape.OLEFormat.ProgID) == "Equation.DSMT4":
                count += 1
        except Exception:
            continue
    return count


def load_formula(manifest: Path, formula_id: int) -> dict[str, object]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    matches = [
        item for item in payload["formulas"] if int(item["formula_id"]) == formula_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Manifest contains {len(matches)} entries for formula {formula_id}")
    formula = matches[0]
    if not isinstance(formula.get("mathml"), str) or not formula["mathml"].startswith("<math"):
        raise ValueError(f"Formula {formula_id} does not provide a MathML root")
    return formula


def build_mathml_presentation_payload(mathml: str) -> str:
    """Wrap a manifest MathML root in the clipboard representation MathType documents."""
    value = mathml.strip()
    if not value.startswith("<math") or not value.endswith("</math>"):
        raise ValueError("MathML payload must be one complete math element")
    return "<?xml version='1.0' encoding='UTF-8'?><html>" + value + "</html>"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_mathml_clipboard(payload: str) -> dict[str, object]:
    """Publish both documented MathML formats, retrying only clipboard contention."""
    import pywintypes
    import win32clipboard
    import win32con

    presentation = win32clipboard.RegisterClipboardFormat("MathML Presentation")
    mathml = win32clipboard.RegisterClipboardFormat("MathML")
    encoded = payload.encode("utf-8") + b"\0"
    deadline = time.monotonic() + 15.0
    last_error: str | None = None
    while time.monotonic() < deadline:
        opened = False
        try:
            win32clipboard.OpenClipboard()
            opened = True
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(presentation, encoded)
            win32clipboard.SetClipboardData(mathml, encoded)
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, payload)
            return {
                "mathml_presentation_format": presentation,
                "mathml_format": mathml,
                "payload_utf8_bytes": len(encoded),
                "clipboard_set": True,
            }
        except pywintypes.error as error:
            last_error = f"{type(error).__name__}: {error}"
            time.sleep(0.2)
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
    raise RuntimeError("Could not set MathML clipboard data" + (f" ({last_error})" if last_error else ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formula-id", type=int, default=43)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def build_plan(args: argparse.Namespace, formula: dict[str, object]) -> dict[str, object]:
    payload = build_mathml_presentation_payload(str(formula["mathml"]))
    return {
        "schema": "mosim.report.mathtype_mathml_clipboard_pilot.v1",
        "mode": "execute" if args.execute else "dry_run",
        "formula_id": int(formula["formula_id"]),
        "expected_number": str(formula["expected_number"]),
        "source": display_path(args.source),
        "source_sha256": sha256_file(args.source),
        "manifest": display_path(args.manifest),
        "manifest_sha256": sha256_file(args.manifest),
        "output": display_path(args.output),
        "evidence": display_path(args.evidence),
        "clipboard": {
            "format": "MathML Presentation",
            "payload_utf8_bytes": len(payload.encode("utf-8")) + 1,
            "restore_original_ole_clipboard": True,
        },
        "allowed_actions": [
            "require zero pre-existing Word processes",
            "copy and modify only the disposable pilot output",
            "temporarily publish MathML to the clipboard and restore its prior OLE data object",
            "paste one formula at the pilot insertion point",
            "choose only a known MathType paste option after visual inspection",
            "save and reopen only the pilot output",
        ],
        "forbidden_actions": [
            "open, save, update, or overwrite the authoritative report",
            "attach to, close, restart, or terminate a pre-existing Word or MathType process",
            "overwrite a pre-existing pilot output or evidence file",
            "accept a repair, compatibility, overwrite, or unknown dialog",
            "perform a multi-formula batch",
        ],
    }


def execute(args: argparse.Namespace, plan: dict[str, object]) -> dict[str, object]:
    import pythoncom
    import win32com.client

    before = process_snapshot()
    existing_word = [item for item in before if str(item["name"]).lower() == "winword.exe"]
    if existing_word:
        raise RuntimeError(f"Pilot requires no pre-existing Word process: {existing_word}")

    shutil.copy2(args.source, args.output)
    word = None
    document = None
    backup_clipboard = None
    clipboard_restored = False
    status = "failed"
    failure: str | None = None
    result: dict[str, object] = {}
    pythoncom.CoInitialize()
    try:
        backup_clipboard = pythoncom.OleGetClipboard()
        payload = build_mathml_presentation_payload(
            json.loads(args.manifest.read_text(encoding="utf-8"))["formulas"][
                int(plan["formula_id"]) - 1
            ]["mathml"]
        )
        result["clipboard"] = set_mathml_clipboard(payload)

        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = True
        word.DisplayAlerts = 0
        document = word.Documents.Open(
            str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=True
        )
        before_omaths = int(document.OMaths.Count)
        before_mathtype = count_mathtype(document)
        if before_omaths != 1 or before_mathtype != 1:
            raise RuntimeError(
                "Golden pilot precondition failed: "
                f"omaths={before_omaths}, mathtype={before_mathtype}"
            )

        target = document.OMaths.Item(1).Range.Duplicate
        insertion_start = int(target.Start)
        target.Delete()
        insertion = document.Range(insertion_start, insertion_start)
        insertion.Select()
        document.Activate()
        word.Activate()
        result["status_before_paste"] = "mathml_clipboard_ready_waiting_for_paste_return"
        write_json(args.evidence, {**plan, **result})
        word.Selection.Paste()

        after_omaths = int(document.OMaths.Count)
        after_mathtype = count_mathtype(document)
        result.update(
            {
                "before_omaths": before_omaths,
                "before_mathtype_objects": before_mathtype,
                "after_omaths": after_omaths,
                "after_mathtype_objects": after_mathtype,
            }
        )
        document.Save()
        document.Close(False)
        document = None
        reopened = word.Documents.Open(
            str(args.output), ReadOnly=True, AddToRecentFiles=False, Visible=False
        )
        try:
            result["reopened_omaths"] = int(reopened.OMaths.Count)
            result["reopened_mathtype_objects"] = count_mathtype(reopened)
        finally:
            reopened.Close(False)
        if (
            result["after_omaths"] != 0
            or result["after_mathtype_objects"] != 2
            or result["reopened_omaths"] != 0
            or result["reopened_mathtype_objects"] != 2
        ):
            raise RuntimeError(
                "MathML clipboard paste did not create one persistent Equation.DSMT4 object: "
                f"{result}"
            )
        status = "mathml_clipboard_roundtrip_passed_pending_visual_review"
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
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
        if backup_clipboard is not None:
            try:
                pythoncom.OleSetClipboard(backup_clipboard)
                clipboard_restored = True
            except Exception as error:
                result["clipboard_restore_failure"] = f"{type(error).__name__}: {error}"
        pythoncom.CoUninitialize()
        time.sleep(1.0)

    result.update(
        {
            "status": status,
            "failure": failure,
            "clipboard_restored": clipboard_restored,
            "output_exists": args.output.is_file(),
            "output_sha256": sha256_file(args.output) if args.output.is_file() else None,
            "authoritative_report_touched": False,
            "preexisting_mathtype_servers": [
                item for item in before if str(item["name"]).lower() == "mathtype.exe"
            ],
            "remaining_word_mathtype_processes": process_snapshot(),
        }
    )
    evidence = {**plan, **result}
    write_json(args.evidence, evidence)
    if failure:
        raise RuntimeError(failure)
    return evidence


def main() -> int:
    args = parse_args()
    for attribute in ("manifest", "source", "output", "evidence"):
        setattr(args, attribute, getattr(args, attribute).resolve())
    for path in (args.manifest, args.source):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.output.exists() or args.evidence.exists():
        raise FileExistsError("Pilot output or evidence file already exists")
    formula = load_formula(args.manifest, args.formula_id)
    plan = build_plan(args, formula)
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(execute(args, plan), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
