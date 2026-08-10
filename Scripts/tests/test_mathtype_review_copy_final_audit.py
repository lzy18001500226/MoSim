from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "report" / "audit_mathtype_review_copy_completion.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mathtype_final_audit", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        sys.modules.pop(spec.name, None)


def test_human_visual_status_preserves_open_semantic_and_visual_exceptions():
    module = load_module()

    assert module.human_visual_status(1).startswith("passed_")
    assert module.human_visual_status(2) == "readable_but_manual_semantic_font_review_required"
    assert module.human_visual_status(4) == "readable_but_manual_semantic_font_review_required"
    assert module.human_visual_status(11) == "failed_replacement_relation_glyph_detected"


def test_rebuild_queue_carries_exact_equation_number_contract():
    module = load_module()
    formula = {
        "formula_id": 43,
        "expected_number": "6-11",
        "sequence": 11,
        "source_start_line": 1129,
        "source_end_line": 1144,
        "source_tex_sha256": "source-hash",
    }
    record = {
        "native_omath_index": 1,
        "normalized_tex": r"\[x+y\]",
        "normalized_tex_sha256": "normalized-hash",
        "normalization_warnings": ["example"],
        "failure": "RuntimeError: timeout",
    }

    queue = module.rebuild_queue_entry(formula, record)

    assert queue["formula_id"] == 43
    assert queue["queue_status"] == "manual_math_type_rebuild_required"
    assert "SEQ Equation \\r 11 \\* ARABIC" in " ".join(queue["manual_steps"])
    assert queue["completion_check"].endswith("visible number (6-11).")
