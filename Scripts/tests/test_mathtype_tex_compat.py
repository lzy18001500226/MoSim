from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts" / "report"))

from mathtype_tex_compat import normalize_tex_for_mathtype


def test_aligned_markers_are_removed_but_nested_case_markers_remain():
    source = r"\[\left\{\begin{aligned}&x=\begin{cases}0,&t<1\\1,&t\ge1\end{cases}\\&y=2\end{aligned}\right.\tag{2-1}\]"

    normalized, warnings = normalize_tex_for_mathtype(source)

    assert r"\begin{aligned}" not in normalized
    assert r"\begin{array}{l}" in normalized
    assert r"\begin{cases}0,&t<1" in normalized
    assert "equation tag removed" in " ".join(warnings)


def test_mathbb_indicator_has_explicit_warning():
    normalized, warnings = normalize_tex_for_mathtype(r"\[\mathbb{1}_{[0,1)}(t)\]")

    assert r"\mathbf{1}" in normalized
    assert any("mathbb{1}" in warning for warning in warnings)


def test_spaced_accent_command_is_braced_for_the_mathtype_translator():
    normalized, warnings = normalize_tex_for_mathtype(r"\[\bar Q+\hat x\]")

    assert r"\bar{Q}" in normalized
    assert r"\hat{x}" in normalized
    assert any("accent command" in warning for warning in warnings)


def test_unwrapped_input_is_rejected():
    with pytest.raises(ValueError, match="display formula"):
        normalize_tex_for_mathtype(r"x+y")
