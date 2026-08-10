r"""Extract every mathematical formula occurrence from the report source.

The generated Markdown is deliberately source-oriented: display formulas keep
their original LaTeX delimiters and tags, while inline formulas keep their
original ``\(...\)`` delimiters.  The report itself is never rewritten.
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Docs" / "报告" / "草稿" / "仿真分析报告_正文骨架.md"
OUTPUT = ROOT / "Docs" / "报告" / "草稿" / "仿真分析报告_正文公式LaTeX汇总.md"

FENCE_RE = re.compile(r"^\s*```\s*(?P<language>[^`\s]*)\s*$")
HEADING_RE = re.compile(r"^\s*(?P<marks>#{1,6})\s+(?P<text>.+?)\s*$")
INLINE_RE = re.compile(r"\\\((?:.|\n)*?\\\)", flags=re.DOTALL)
OUTSIDE_DISPLAY_RE = re.compile(r"\\\[(?:.|\n)*?\\\]", flags=re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
TAG_RE = re.compile(r"\\tag\{([^{}]+)\}")


@dataclass(frozen=True)
class Formula:
    start_line: int
    end_line: int
    section: str
    body: str


def _section_path(stack: list[str]) -> str:
    return " > ".join(stack) if stack else "（未归属章节）"


def _mask_inline_code(line: str) -> str:
    return INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), line)


def parse_source(text: str) -> tuple[list[Formula], list[Formula]]:
    lines = text.splitlines()
    display: list[Formula] = []
    clean_lines: list[str] = []
    heading_stack: list[str] = []
    current_section = "（未归属章节）"
    in_fence = False
    fence_language = ""
    fence_start = 0
    fence_body: list[str] = []
    fence_section = current_section

    for line_no, line in enumerate(lines, start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            if not in_fence:
                in_fence = True
                fence_language = fence_match.group("language").lower()
                fence_start = line_no
                fence_body = []
                fence_section = current_section
            else:
                if fence_language in {"latex", "tex"}:
                    display.append(
                        Formula(
                            start_line=fence_start,
                            end_line=line_no,
                            section=fence_section,
                            body="\n".join(fence_body).rstrip(),
                        )
                    )
                in_fence = False
                fence_language = ""
                fence_body = []
            clean_lines.append("")
            continue

        if in_fence:
            if fence_language in {"latex", "tex"}:
                fence_body.append(line)
            clean_lines.append("")
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group("marks"))
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(heading_match.group("text").strip())
            current_section = _section_path(heading_stack)
        clean_lines.append(line)

    clean_text = "\n".join(_mask_inline_code(line) for line in clean_lines)

    # Any display delimiter outside a fenced LaTeX block is still a display
    # formula and must be included rather than silently treated as prose.
    for match in OUTSIDE_DISPLAY_RE.finditer(clean_text):
        start_line = clean_text.count("\n", 0, match.start()) + 1
        end_line = clean_text.count("\n", 0, match.end()) + 1
        section = _section_for_line(clean_lines, start_line)
        display.append(
            Formula(
                start_line=start_line,
                end_line=end_line,
                section=section,
                body=match.group(0).rstrip(),
            )
        )

    display.sort(key=lambda item: (item.start_line, item.end_line))

    inline: list[Formula] = []
    for match in INLINE_RE.finditer(clean_text):
        start_line = clean_text.count("\n", 0, match.start()) + 1
        end_line = clean_text.count("\n", 0, match.end()) + 1
        inline.append(
            Formula(
                start_line=start_line,
                end_line=end_line,
                section=_section_for_line(clean_lines, start_line),
                body=match.group(0).rstrip(),
            )
        )

    return display, inline


def _section_for_line(lines: list[str], line_no: int) -> str:
    stack: list[str] = []
    for line in lines[:line_no]:
        match = HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group("marks"))
        stack = stack[: level - 1]
        stack.append(match.group("text").strip())
    return _section_path(stack)


def _group_by_section(items: list[Formula]) -> OrderedDict[str, list[Formula]]:
    groups: OrderedDict[str, list[Formula]] = OrderedDict()
    for item in items:
        groups.setdefault(item.section, []).append(item)
    return groups


def _location(item: Formula) -> str:
    if item.start_line == item.end_line:
        return f"正文第 {item.start_line} 行"
    return f"正文第 {item.start_line}-{item.end_line} 行"


def _append_formula(lines: list[str], item: Formula, index: int, kind: str) -> None:
    tag_match = TAG_RE.search(item.body)
    tag = f"，{tag_match.group(0)}" if tag_match else ""
    lines.append(f"#### {kind} {index:03d}{tag}（{_location(item)}）")
    lines.append("")
    lines.append("```latex")
    lines.extend(item.body.splitlines())
    lines.append("```")
    lines.append("")


def build_markdown(display: list[Formula], inline: list[Formula]) -> str:
    lines = [
        "# 仿真分析报告正文公式 LaTeX 汇总",
        "",
        "> 来源：`Docs/报告/草稿/仿真分析报告_正文骨架.md`。本文件只做公式提取，未改动正文。",
        "> 显示公式保留正文原始的 `\\[...\\]` 定界符和 `\\tag{...}`；行内公式保留原始的 `\\(...\\)` 定界符。",
        "> 复制到 MathType 时，复制对应 `latex` 代码块中的内容，不要复制外围 Markdown 围栏。每条记录的章节和行号仅用于定位。",
        "",
        f"- 显示公式：{len(display)} 条",
        f"- 行内公式：{len(inline)} 条",
        f"- 公式出现位置合计：{len(display) + len(inline)} 条",
        "",
        "## 一、显示公式",
        "",
    ]

    display_index = 0
    for section, items in _group_by_section(display).items():
        lines.append(f"### {section}")
        lines.append("")
        for item in items:
            display_index += 1
            _append_formula(lines, item, display_index, "显示公式")

    lines.extend(["## 二、行内公式", ""])
    inline_index = 0
    for section, items in _group_by_section(inline).items():
        lines.append(f"### {section}")
        lines.append("")
        for item in items:
            inline_index += 1
            _append_formula(lines, item, inline_index, "行内公式")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the existing formula index does not exactly match the source.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    text = source.read_text(encoding="utf-8")
    display, inline = parse_source(text)
    rendered = build_markdown(display, inline)
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            print(f"formula index is out of sync: {output}")
            return 2
        print(f"formula index is synchronized: {output}")
    else:
        output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"source={source}")
        print(f"output={output}")
    print(f"display_formulas={len(display)}")
    print(f"inline_formulas={len(inline)}")
    print(f"total_occurrences={len(display) + len(inline)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
