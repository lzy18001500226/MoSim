from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "report" / "run_mathtype_report_review_copy.py"
OMML_DIALOG_MODULE_PATH = ROOT / "Scripts" / "report" / "pilot_mathtype_convert_omml_dialog.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mathtype_review_copy", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def load_omml_dialog_module():
    spec = importlib.util.spec_from_file_location("mathtype_omml_dialog", OMML_DIALOG_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def test_dry_run_plans_the_full_review_copy_without_word(tmp_path: Path):
    output = tmp_path / "review.docx"
    evidence = tmp_path / "evidence.json"
    checkpoint = tmp_path / "checkpoint.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--output",
            str(output),
            "--evidence",
            str(evidence),
            "--checkpoint",
            str(checkpoint),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    plan = json.loads(result.stdout)

    assert plan["mode"] == "dry_run"
    assert plan["manifest"]["formula_count"] == 104
    assert plan["manifest"]["native_formulas_to_convert"] == 103
    assert plan["authoritative_report"]["omath_count"] == 103
    assert plan["authoritative_report"]["mathtype_ole_count"] == 1
    assert not output.exists()
    assert not evidence.exists()
    assert not checkpoint.exists()


def test_formula_records_cover_every_id_and_expose_review_warnings():
    module = load_module()
    records = module.load_formula_records(module.MANIFEST)

    assert [record["formula_id"] for record in records] == list(range(1, 105))
    assert records[0]["expected_number"] == "2-1"
    assert records[-1]["expected_number"] == "14-1"
    assert all(record["normalized_tex"].startswith(r"\[") for record in records)
    double_struck = [
        record["formula_id"]
        for record in records
        if any("double-struck" in warning for warning in record["normalization_warnings"])
    ]
    assert double_struck == [2, 3, 4]


def test_resume_validation_rejects_noncontiguous_completion(tmp_path: Path):
    module = load_module()
    checkpoint = tmp_path / "checkpoint.jsonl"
    checkpoint.write_text(
        "\n".join(
            json.dumps(record)
            for record in (
                {"formula_id": 2, "status": "saved_checkpoint"},
                {"formula_id": 4, "status": "saved_checkpoint"},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    records = module.read_checkpoint(checkpoint)
    assert module.completed_formula_ids(records) == [2, 4]


def test_processed_formula_ids_include_retained_manual_placeholders():
    module = load_module()
    records = [
        {"formula_id": 2, "status": "saved_checkpoint"},
        {"formula_id": 3, "status": "manual_placeholder"},
        {"formula_id": 4, "status": "saved_checkpoint"},
    ]

    assert module.completed_formula_ids(records) == [2, 4]
    assert module.processed_formula_ids(records) == [2, 3, 4]
    assert module.manual_placeholder_records(records) == [records[1]]


def test_resolved_manual_placeholder_becomes_converted_and_leaves_queue():
    module = load_module()
    records = [
        {"formula_id": 2, "status": "saved_checkpoint"},
        {"formula_id": 3, "status": "manual_placeholder"},
        {"formula_id": 4, "status": "saved_checkpoint"},
        {"formula_id": 3, "status": "manual_placeholder_resolved"},
    ]

    assert module.completed_formula_ids(records) == [2, 3, 4]
    assert module.processed_formula_ids(records) == [2, 3, 4]
    assert module.manual_placeholder_records(records) == []


def test_manual_placeholder_record_keeps_exact_recovery_inputs():
    module = load_module()
    formula = {
        "formula_id": 43,
        "expected_number": "6-11",
        "source_start_line": 1129,
        "source_end_line": 1144,
        "source_tex_sha256": "source-hash",
        "normalized_tex": r"\[x+y\]",
        "normalized_tex_sha256": "normalized-hash",
        "normalization_warnings": ["example warning"],
    }

    record = module.manual_placeholder_record(
        formula,
        "RuntimeError: TeX toggle timed out",
        native_omath_index=1,
    )

    assert record["status"] == "manual_placeholder"
    assert record["formula_id"] == 43
    assert record["normalized_tex"] == r"\[x+y\]"
    assert record["native_omath_index"] == 1
    assert "Equation.DSMT4" in record["manual_action"]


def test_manual_queue_distinguishes_tex_failures_from_word_session_errors():
    module = load_module()
    queue = module.manual_queue_entries(
        [
            {
                "formula_id": 43,
                "status": "manual_placeholder",
                "failure": "RuntimeError: Formula 43 failed at stage wait_for_mathtype_object",
            },
            {
                "formula_id": 68,
                "status": "manual_placeholder",
                "failure": "RuntimeError: Formula 68 failed at stage paste_template",
            },
        ]
    )

    assert queue[0]["queue_status"] == "mathtype_tex_route_failed"
    assert queue[1]["queue_status"] == "retryable_word_session_error"


def test_tex_pilot_variant_is_explicit_and_recorded():
    pilot_path = ROOT / "Scripts" / "report" / "run_mathtype_tex_pilot.py"
    spec = importlib.util.spec_from_file_location("mathtype_tex_pilot", pilot_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        args = type(
            "Args",
            (),
            {"variant": "remove_tight_spacing"},
        )()
        formula = {"source_tex": r"\[x\!+y\]"}
        normalized, warnings = module.conversion_input(args, formula)
    finally:
        sys.modules.pop(spec.name, None)

    assert normalized == r"\[x +y\]"
    assert warnings[-1] == "variant removed TeX negative thin-space commands"


def test_tex_pilot_row_selection_preserves_nested_matrix_rows():
    pilot_path = ROOT / "Scripts" / "report" / "run_mathtype_tex_pilot.py"
    spec = importlib.util.spec_from_file_location("mathtype_tex_pilot", pilot_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        normalized = (
            r"\[\left\{ \begin{array}{l} "
            r"a=\begin{bmatrix}1\\2\end{bmatrix}\\ b=c\\ d=e "
            r"\end{array} \right.\]"
        )
        prefix, rows, suffix = module.outer_array_rows(normalized)
        selected = module.parse_row_indices("1,3", len(rows))
    finally:
        sys.modules.pop(spec.name, None)

    assert prefix + r"\\".join(rows[index - 1] for index in selected) + suffix == (
        r"\[\left\{ \begin{array}{l} "
        r"a=\begin{bmatrix}1\\2\end{bmatrix}\\ d=e "
        r"\end{array} \right.\]"
    )


def test_tex_pilot_row_grouping_keeps_all_rows_in_short_nested_arrays():
    pilot_path = ROOT / "Scripts" / "report" / "run_mathtype_tex_pilot.py"
    spec = importlib.util.spec_from_file_location("mathtype_tex_pilot", pilot_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        grouped = module.group_outer_array_rows(
            r"\[\left\{ \begin{array}{l} a\\ b\\ c\\ d "
            r"\end{array} \right.\]",
            3,
        )
    finally:
        sys.modules.pop(spec.name, None)

    assert grouped == (
        r"\[\left\{ \begin{array}{l} "
        r"\begin{array}{l} a\\ b\\ c \end{array}\\ "
        r"\begin{array}{l} d \end{array} \end{array} \right.\]"
    )


def test_omml_dialog_expected_counts_distinguish_single_and_document_selection():
    module = load_omml_dialog_module()

    assert module.expected_object_counts("native_omml", 8, 96) == (7, 97)
    assert module.expected_object_counts("document_content", 8, 96) == (0, 104)
