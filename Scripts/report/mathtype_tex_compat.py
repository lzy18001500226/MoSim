"""Normalize report display TeX for the MathType Word add-in route."""

from __future__ import annotations

import re


def _rewrite_aligned_blocks(text: str, warnings: list[str]) -> str:
    """Map aligned rows to MathType's array syntax without touching nested cells."""
    token_re = re.compile(r"\\(begin|end)\{([^{}]+)\}|&")
    output: list[str] = []
    cursor = 0
    environments: list[str] = []
    changed = False
    for match in token_re.finditer(text):
        output.append(text[cursor : match.start()])
        token = match.group(0)
        if token == "&":
            if environments and environments[-1] == "aligned":
                changed = True
            else:
                output.append(token)
        else:
            action, name = match.group(1), match.group(2)
            if action == "begin":
                environments.append(name)
                if name == "aligned":
                    output.append(r"\begin{array}{l}")
                    changed = True
                else:
                    output.append(token)
            else:
                if not environments or environments[-1] != name:
                    raise ValueError(f"Unbalanced TeX environment: {name}")
                environments.pop()
                if name == "aligned":
                    output.append(r"\end{array}")
                    changed = True
                else:
                    output.append(token)
        cursor = match.end()
    output.append(text[cursor:])
    if environments:
        raise ValueError(f"Unclosed TeX environment: {environments[-1]}")
    if changed:
        warnings.append("aligned blocks normalized to array rows")
    return "".join(output)


def normalize_tex_for_mathtype(source_tex: str) -> tuple[str, list[str]]:
    """Return one display formula in the syntax accepted by MathType Toggle TeX."""
    text = source_tex.strip()
    if text.startswith(r"\[") and text.endswith(r"\]"):
        text = text[2:-2].strip()
    else:
        raise ValueError("Expected a \\[...\\] display formula")

    warnings: list[str] = []
    text, count = re.subn(r"\\tag\{[^{}]*\}", "", text)
    if count:
        warnings.append("equation tag removed before MathType insertion")

    text = _rewrite_aligned_blocks(text, warnings)

    replacements = (
        (r"\\operatorname\*?\{([^{}]+)\}", r"\\mathrm{\1}", "operatorname mapped to mathrm"),
        (r"\\(mathbf|boldsymbol|mathrm|mathcal|mathbb)\s+([A-Za-z0-9])", r"\\\1{\2}", "spaced style command braced"),
        (r"\\(bar|hat|tilde|vec|dot|ddot)\s+([A-Za-z0-9])", r"\\\1{\2}", "spaced accent command braced"),
    )
    for pattern, replacement, warning in replacements:
        text, count = re.subn(pattern, replacement, text)
        if count:
            warnings.append(warning)

    if r"\mathbb{1}" in text:
        text = text.replace(r"\mathbb{1}", r"\mathbf{1}")
        warnings.append(
            "double-struck mathbb{1} mapped to bold 1 because the installed "
            "translator rejects the indicator glyph"
        )

    text, count = re.subn(r"(?<=\d)(?=\\mathbf\{1\})", r"\\cdot ", text)
    if count:
        warnings.append("explicit multiplication dots inserted before numeric indicator products")

    text = re.sub(r"\s+", " ", text).strip()
    if r"\begin{aligned}" in text:
        raise ValueError("MathType input still contains unsupported aligned syntax")
    return r"\[" + text + r"\]", warnings
