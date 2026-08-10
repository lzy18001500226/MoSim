"""Run one bounded, disposable TeX-to-MathType conversion pilot.

The authoritative report is never opened.  The pilot starts an independent
Word instance, converts one native equation in the golden sample through the
MathType TeX-toggle command, saves, reopens, and records structural evidence.
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
DEFAULT_GOLDEN = PILOT_DIR / "source_omml_pilot.docx"
DEFAULT_OUTPUT = PILOT_DIR / "mathtype_tex_formula_002_pilot_20260804.docx"
DEFAULT_EVIDENCE = PILOT_DIR / "mathtype_tex_formula_002_pilot_20260804.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def mathtype_count(document) -> int:
    count = 0
    for index in range(1, document.InlineShapes.Count + 1):
        shape = document.InlineShapes(index)
        try:
            if shape.OLEFormat.ProgID == "Equation.DSMT4":
                count += 1
        except Exception:
            continue
    return count


def load_formula(manifest_path: Path, formula_id: int) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    matches = [item for item in manifest["formulas"] if item["formula_id"] == formula_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one formula {formula_id}, found {len(matches)}")
    return matches[0]


def outer_array_rows(normalized: str) -> tuple[str, list[str], str]:
    """Split the reviewed outer array without splitting nested matrix rows."""
    prefix = r"\[\left\{ \begin{array}{l} "
    suffix = r" \end{array} \right.\]"
    if not normalized.startswith(prefix) or not normalized.endswith(suffix):
        raise ValueError("row selection requires the reviewed outer array wrapper")

    body = normalized[len(prefix) : -len(suffix)]
    rows: list[str] = []
    cursor = 0
    index = 0
    nested_environments = 0
    while index < len(body):
        if body.startswith(r"\begin{", index):
            end = body.find("}", index + len(r"\begin{"))
            if end < 0:
                raise ValueError("Unclosed TeX begin environment during row selection")
            nested_environments += 1
            index = end + 1
            continue
        if body.startswith(r"\end{", index):
            end = body.find("}", index + len(r"\end{"))
            if end < 0 or nested_environments <= 0:
                raise ValueError("Unbalanced TeX environment during row selection")
            nested_environments -= 1
            index = end + 1
            continue
        if body.startswith(r"\\", index) and nested_environments == 0:
            rows.append(body[cursor:index])
            index += 2
            cursor = index
            continue
        index += 1
    if nested_environments != 0:
        raise ValueError("Unclosed nested TeX environment during row selection")
    rows.append(body[cursor:])
    return prefix, rows, suffix


def parse_row_indices(value: str, row_count: int) -> list[int]:
    """Parse a comma-separated, non-repeating sequence of one-based row IDs."""
    pieces = [item.strip() for item in value.split(",")]
    if not pieces or any(not item for item in pieces):
        raise ValueError("--row-indices must be a comma-separated list of row IDs")
    try:
        indices = [int(item) for item in pieces]
    except ValueError as error:
        raise ValueError("--row-indices contains a non-integer row ID") from error
    if any(index < 1 or index > row_count for index in indices):
        raise ValueError(f"--row-indices must stay between 1 and {row_count}")
    if len(set(indices)) != len(indices):
        raise ValueError("--row-indices must not repeat a row ID")
    return indices


def group_outer_array_rows(normalized: str, group_size: int) -> str:
    """Nest short arrays so each MathType TeX table stays within a row budget."""
    prefix, rows, suffix = outer_array_rows(normalized)
    if group_size < 1:
        raise ValueError("--group-rows must be positive")
    if group_size >= len(rows):
        raise ValueError(
            f"--group-rows must be smaller than the {len(rows)} outer array rows"
        )
    groups = [
        r"\begin{array}{l} "
        + r"\\ ".join(
            row.strip() for row in rows[start : start + group_size]
        )
        + r" \end{array}"
        for start in range(0, len(rows), group_size)
    ]
    return prefix + r"\\ ".join(groups) + suffix


def conversion_input(args: argparse.Namespace, formula: dict[str, object]) -> tuple[str, list[str]]:
    from mathtype_tex_compat import normalize_tex_for_mathtype

    normalized, warnings = normalize_tex_for_mathtype(str(formula["source_tex"]))
    variant = args.variant or "default"
    if variant == "remove_tight_spacing":
        normalized = normalized.replace(r"\!", " ")
        warnings = [*warnings, "variant removed TeX negative thin-space commands"]
    elif variant == "plain_sat":
        normalized = normalized.replace(r"\mathrm{sat}", "sat")
        warnings = [*warnings, "variant replaced mathrm{sat} with plain sat text"]
    elif variant == "remove_piecewise_wrapper":
        normalized = normalized.replace(r"\left\{ \begin{array}{l}", r"\begin{array}{l}")
        normalized = normalized.replace(r"\end{array} \right.", r"\end{array}")
        warnings = [*warnings, "variant removed the outer left-brace array wrapper"]
    elif variant == "boldsymbol_to_mathbf":
        normalized = normalized.replace(r"\boldsymbol{\zeta}", r"\mathbf{\zeta}")
        warnings = [*warnings, "variant mapped boldsymbol zeta to mathbf zeta"]
    elif variant == "drop_zeta_bold":
        normalized = normalized.replace(r"\boldsymbol{\zeta}", r"\zeta")
        warnings = [*warnings, "variant removed bold formatting from zeta"]
    elif variant == "zeta_to_z_diagnostic":
        normalized = normalized.replace(r"\zeta", "z")
        warnings = [*warnings, "diagnostic variant replaced zeta with Latin z"]
    elif variant == "none":
        pass
    elif variant != "default":
        raise ValueError(f"Unknown TeX pilot variant: {variant}")
    keep_rows = getattr(args, "keep_rows", None)
    row_indices = getattr(args, "row_indices", None)
    group_rows = getattr(args, "group_rows", None)
    active_row_options = sum(
        option is not None for option in (keep_rows, row_indices, group_rows)
    )
    if active_row_options > 1:
        raise ValueError("only one row-selection or row-grouping option may be used")
    if active_row_options:
        if variant != "default":
            raise ValueError("row selection or grouping requires the default TeX variant")
        prefix, rows, suffix = outer_array_rows(normalized)
    if keep_rows is not None:
        if keep_rows < 1 or keep_rows > len(rows):
            raise ValueError(f"--keep-rows must be between 1 and {len(rows)}")
        normalized = prefix + r"\\".join(rows[:keep_rows]) + suffix
        warnings = [*warnings, f"diagnostic variant kept only the first {keep_rows} array row(s)"]
    elif row_indices is not None:
        selected = parse_row_indices(row_indices, len(rows))
        normalized = prefix + r"\\".join(rows[index - 1] for index in selected) + suffix
        warnings = [
            *warnings,
            "diagnostic variant kept outer array row(s) "
            + ",".join(str(index) for index in selected),
        ]
    elif group_rows is not None:
        normalized = group_outer_array_rows(normalized, group_rows)
        warnings = [
            *warnings,
            f"diagnostic variant grouped outer array rows in sets of {group_rows}",
        ]
    return normalized, warnings


def build_plan(args: argparse.Namespace, formula: dict[str, object]) -> dict[str, object]:
    normalized, warnings = conversion_input(args, formula)
    return {
        "schema": "mosim.report.mathtype_tex_pilot.v1",
        "mode": "execute" if args.execute else "dry_run",
        "formula_id": args.formula_id,
        "expected_number": formula["expected_number"],
        "manifest": str(args.manifest).replace("\\", "/"),
        "manifest_sha256": sha256_file(args.manifest),
        "golden_pilot": str(args.golden).replace("\\", "/"),
        "golden_pilot_sha256": sha256_file(args.golden),
        "output": str(args.output).replace("\\", "/"),
        "evidence": str(args.evidence).replace("\\", "/"),
        "conversion": {
            "engine": "MathTypeCommands.UILib.MTCommand_TeXToggle",
            "variant": args.variant or "default",
            "input": normalized,
            "source_tex_sha256": hashlib.sha256(str(formula["source_tex"]).encode()).hexdigest(),
            "normalization_warnings": warnings,
        },
        "allowed_actions": [
            "start one independent pilot-owned Word instance",
            "open and modify only the disposable golden pilot copy",
            "convert exactly one native equation through the MathType add-in",
            "save and reopen the disposable output",
        ],
        "forbidden_actions": [
            "open or modify the authoritative report",
            "attach to an existing Word process",
            "perform a multi-formula batch",
            "accept unknown dialogs or repair prompts",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formula-id", type=int, default=2)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument(
        "--variant",
        choices=(
            "default",
            "none",
            "remove_tight_spacing",
            "plain_sat",
            "remove_piecewise_wrapper",
            "boldsymbol_to_mathbf",
            "drop_zeta_bold",
            "zeta_to_z_diagnostic",
        ),
        default="default",
    )
    parser.add_argument("--allow-existing-mathtype-server", action="store_true")
    parser.add_argument("--keep-rows", type=int, default=None)
    parser.add_argument(
        "--row-indices",
        default=None,
        help="comma-separated one-based outer-array rows for an isolation pilot",
    )
    parser.add_argument(
        "--group-rows",
        type=int,
        default=None,
        help="maximum rows per nested array for a single-object compatibility pilot",
    )
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def run(args: argparse.Namespace, plan: dict[str, object]) -> dict[str, object]:
    import pythoncom
    import win32com.client
    before_processes = process_snapshot()
    existing_word = [item for item in before_processes if str(item["name"]).lower() == "winword.exe"]
    existing_mathtype = [item for item in before_processes if str(item["name"]).lower() == "mathtype.exe"]
    if existing_word:
        raise RuntimeError(f"Pilot requires no pre-existing Word process: {existing_word}")
    if existing_mathtype and not args.allow_existing_mathtype_server:
        raise RuntimeError(
            "A pre-existing MathType OLE server was found; pass "
            "--allow-existing-mathtype-server for this disposable pilot."
        )
    shutil.copy2(args.golden, args.output)
    word = None
    document = None
    reopened = None
    status = "failed"
    failure: str | None = None
    word_pid: int | None = None
    initial_omaths = None
    initial_mathtype = None
    final_omaths = None
    final_mathtype = None
    reopened_omaths = None
    reopened_mathtype = None
    caught_error: Exception | None = None
    pythoncom.CoInitialize()
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = True
        word.DisplayAlerts = 0
        document = word.Documents.Open(
            str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=True
        )
        try:
            import win32process

            word_pid = int(win32process.GetWindowThreadProcessId(int(word.Hwnd))[1])
        except Exception:
            word_pid = None

        initial_omaths = int(document.OMaths.Count)
        initial_mathtype = mathtype_count(document)
        if initial_omaths != 1 or initial_mathtype != 1:
            raise RuntimeError(
                f"Golden pilot precondition failed: omaths={initial_omaths}, mathtype={initial_mathtype}"
            )

        formula_text = str(plan["conversion"]["input"])
        equation_range = document.OMaths(1).Range.Duplicate
        start = int(equation_range.Start)
        equation_range.Delete()
        insertion_range = document.Range(start, start)
        insertion_range.InsertAfter(formula_text)
        target = document.Range(start, start + len(formula_text))
        target.Select()
        document.Activate()
        word.Activate()
        word.Run("MathTypeCommands.UILib.MTCommand_TeXToggle")

        final_omaths = int(document.OMaths.Count)
        final_mathtype = mathtype_count(document)
        if final_omaths != 0 or final_mathtype != initial_mathtype + 1:
            raise RuntimeError(
                f"TeX toggle did not produce one new MathType object: omaths={final_omaths}, mathtype={final_mathtype}"
            )
        document.Save()
        document.Close(False)
        document = None

        reopened = word.Documents.Open(
            str(args.output), ReadOnly=False, AddToRecentFiles=False, Visible=False
        )
        reopened_omaths = int(reopened.OMaths.Count)
        reopened_mathtype = mathtype_count(reopened)
        if reopened_omaths != 0 or reopened_mathtype != final_mathtype:
            raise RuntimeError(
                f"Reopened pilot changed object counts: omaths={reopened_omaths}, mathtype={reopened_mathtype}"
            )
        status = "tex_toggle_roundtrip_passed_pending_visual_review"
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        caught_error = error
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

    after_processes = process_snapshot()
    evidence = dict(plan)
    evidence.update(
        {
            "status": status,
            "failure": failure,
            "pilot_word_pid": word_pid,
            "initial_omaths": initial_omaths,
            "initial_mathtype_objects": initial_mathtype,
            "final_omaths": final_omaths,
            "final_mathtype_objects": final_mathtype,
            "reopened_omaths": reopened_omaths,
            "reopened_mathtype_objects": reopened_mathtype,
            "output_exists": args.output.is_file(),
            "output_bytes": args.output.stat().st_size if args.output.is_file() else 0,
            "output_sha256": sha256_file(args.output) if args.output.is_file() else None,
            "authoritative_report_touched": False,
            "remaining_word_mathtype_processes": after_processes,
            "preexisting_mathtype_servers": existing_mathtype,
        }
    )
    args.evidence.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if caught_error is not None:
        raise caught_error
    return evidence


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    args = parse_args()
    args.manifest = args.manifest.resolve()
    args.golden = args.golden.resolve()
    args.output = args.output.resolve()
    args.evidence = args.evidence.resolve()
    for path in (args.manifest, args.golden):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.output.exists() or args.evidence.exists():
        raise FileExistsError("Refusing to overwrite an existing pilot output or evidence file")
    formula = load_formula(args.manifest, args.formula_id)
    plan = build_plan(args, formula)
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    evidence = run(args, plan)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise
