"""Loader for the error taxonomy defined in error_taxonomy_analysis.md.

This module reads the canonical taxonomy markdown at import time and
provides helpers that return Template-safe text for embedding into
prompt strings in ``prompts.py``.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_MD_PATH = Path(__file__).parent / "error_taxonomy_analysis.md"

# ── Regex patterns for parsing ──────────────────────────────────────────────

# Matches a top-level category heading like "## 1. Selection Errors"
_CATEGORY_HEADING_RE = re.compile(r"^## (\d+)\.\s")
# Matches the summary decision table start
_SUMMARY_TABLE_RE = re.compile(r"^## Summary Decision Table", re.MULTILINE)
# Matches "---" separators
_SEPARATOR_RE = re.compile(r"^---\s*$", re.MULTILINE)


def _load_raw_md() -> str:
    """Read the taxonomy markdown file."""
    return _MD_PATH.read_text(encoding="utf-8")


def escape_for_template(text: str) -> str:
    """Escape ``$`` → ``$$`` so *text* is safe inside a ``string.Template``."""
    return text.replace("$", "$$")


# ── Section extraction ───────────────────────────────────────────────────────


def _split_into_categories(md_text: str) -> dict[int, str]:
    """Split the markdown into a dict mapping category number → full text.

    Each value includes the ``## N. …`` heading through to (but not
    including) the next ``## M. …`` heading or the summary table.
    """
    categories: dict[int, str] = {}
    lines = md_text.splitlines(keepends=True)

    current_cat: int | None = None
    current_lines: list[str] = []

    for line in lines:
        m = _CATEGORY_HEADING_RE.match(line)
        if m:
            if current_cat is not None:
                categories[current_cat] = "".join(current_lines).rstrip("\n")
            current_cat = int(m.group(1))
            current_lines = [line]
            continue

        if _SUMMARY_TABLE_RE.match(line) or (
            _SEPARATOR_RE.match(line) and current_cat is not None
        ):
            # End of the last category before the summary table / separator
            if current_cat is not None:
                categories[current_cat] = "".join(current_lines).rstrip("\n")
                current_cat = None
                current_lines = []
            continue

        if current_cat is not None:
            current_lines.append(line)

    if current_cat is not None:
        categories[current_cat] = "".join(current_lines).rstrip("\n")

    return categories


def _extract_summary_table(md_text: str) -> str:
    """Return the full summary decision table (header + all rows)."""
    m = _SUMMARY_TABLE_RE.search(md_text)
    if not m:
        raise ValueError("Summary Decision Table not found in taxonomy .md")
    return md_text[m.start() :].rstrip("\n")


def _summary_table_rows_for_categories(table_text: str, start: int, end: int) -> str:
    """Filter summary table to only rows whose error code starts with
    categories in [start, end].  Keeps the header + separator rows.
    """
    lines = table_text.splitlines()
    kept: list[str] = []
    for line in lines:
        # Always keep header and separator lines
        if line.startswith("|:") or line.startswith("| Error Code"):
            kept.append(line)
            continue
        # Check if the row belongs to a category in range
        m = re.match(r"\|\s*(\d+)\.", line)
        if m:
            cat = int(m.group(1))
            if start <= cat <= end:
                kept.append(line)
        # Table title line
        elif line.startswith("## Summary"):
            kept.append(line)
    return "\n".join(kept)


# ── Public API (cached) ─────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def extract_categories(start: int, end: int) -> str:
    """Return the taxonomy text for categories *start* through *end*.

    The result is raw markdown (NOT Template-escaped). Call
    ``escape_for_template()`` before embedding in a Template string.
    """
    md = _load_raw_md()
    cats = _split_into_categories(md)
    sections = []
    for i in range(start, end + 1):
        if i in cats:
            sections.append(cats[i])
    return "\n\n".join(sections)


@lru_cache(maxsize=1)
def extract_summary_table(start: int, end: int) -> str:
    """Return the summary decision table filtered to categories [start, end].

    Raw markdown, NOT Template-escaped.
    """
    md = _load_raw_md()
    full_table = _extract_summary_table(md)
    return _summary_table_rows_for_categories(full_table, start, end)


def _postprocess_category_6_for_prompt(text: str) -> str:
    """Replace the static action-space list in category 6 with Template vars.

    The .md has a concrete list of actions; the prompt needs
    ``$action_space`` and ``$action_definitions_text`` so they can be
    filled at runtime per solver configuration.
    """
    # Replace the static preamble sentence about action space
    text = re.sub(
        r"The agent's action space includes GUI actions \([^)]+\), "
        r"browser navigation \([^)]+\), "
        r"and utility actions \([^)]+\)\.",
        "The agent's action space is: [$action_space].",
        text,
    )

    # Append action definitions reference after the 6.1 description.
    # The .md 6.1 ends with "...or parameters that fail schema validation (...)"
    # We inject the Template var after the 6.1 bullet.
    text = re.sub(
        r"(\*\*6\.1 Invalid invocation\*\*.*?)"  # match 6.1 bullet
        r"((?=\n- \*\*6\.2))",  # lookahead to 6.2 start
        r"\1 The valid actions and their accepted arguments are:\n$action_definitions_text\n",
        text,
        flags=re.DOTALL,
    )
    return text


@lru_cache(maxsize=1)
def get_taxonomy_for_failure_prompt() -> tuple[str, str]:
    """Return ``(taxonomy_text, summary_table)`` for the failure-analysis prompt.

    Categories 1-6.  Category 6 is post-processed to contain
    ``$action_space`` and ``$action_definitions_text`` Template vars.
    The calibration note from the .md is prepended.

    **Important:** the returned strings are already ``$$``-escaped
    *except* for the intentional ``$action_space`` and
    ``$action_definitions_text`` Template variables.
    """
    cats_text = extract_categories(1, 6)
    summary = extract_summary_table(1, 6)

    # Escape $ for Template safety *first*, then inject Template vars
    cats_escaped = escape_for_template(cats_text)
    summary_escaped = escape_for_template(summary)

    # Post-process category 6 to inject Template vars (these must NOT be escaped)
    cats_escaped = _postprocess_category_6_for_prompt(cats_escaped)

    # Downgrade ## headings to ### for embedding inside a prompt that uses ## for its own structure
    cats_escaped = re.sub(r"^## (\d+\.)", r"### \1", cats_escaped, flags=re.MULTILINE)

    # Prepend calibration note
    calibration = (
        "Each top-level category contains numbered sub-categories, "
        'with an "Other" catch-all for errors \\\n'
        "that don't fit existing sub-categories.\n\n"
        "**Calibration:** Not every imperfection is a failure. Only flag issues that "
        "materially affected \\\n"
        "task completion, correctness, or user trust. Do not over-classify minor or cosmetic \\\n"
        "discrepancies as errors. When in doubt, err on the side of not flagging."
    )
    cats_final = calibration + "\n\n" + cats_escaped

    return cats_final, summary_escaped


@lru_cache(maxsize=1)
def get_taxonomy_for_task_classification() -> str:
    """Return taxonomy text for task-classification prompts (categories 7-8).

    Returns ``$$``-escaped text ready to embed in Template strings.
    """
    cats_text = extract_categories(7, 8)
    return escape_for_template(cats_text)


def extract_subcategory_bullets(category_num: int) -> str:
    """Return only the ``- **N.M …**`` bullet lines for a single category.

    Useful when the prompt provides its own framing/preamble and only needs
    the sub-category definitions from the .md.  Result is raw markdown
    (NOT Template-escaped).
    """
    md = _load_raw_md()
    cats = _split_into_categories(md)
    if category_num not in cats:
        raise ValueError(f"Category {category_num} not found in taxonomy .md")
    text = cats[category_num]
    bullets = []
    for line in text.splitlines():
        if re.match(r"^- \*\*\d+\.\d+", line):
            bullets.append(line)
    return "\n".join(bullets)
