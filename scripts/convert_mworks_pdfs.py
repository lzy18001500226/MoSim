#!/usr/bin/env python3
"""
Convert high-value MWORKS PDF documents into Markdown for agent lookup.

MinerU MCP is the preferred converter for final high-fidelity Markdown. This
script is the local fallback path: it uses PyMuPDF text extraction so Codex can
search official training materials even when the MinerU cloud endpoint is not
reachable.

Usage:
    uv run --with pymupdf python scripts/convert_mworks_pdfs.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import hashlib
import re

import fitz  # type: ignore[import-not-found]


SOURCE_ROOT = Path("MWORKS高校星火计划资料包")
OUTPUT_ROOT = Path("docs/mworks/converted")


@dataclass(frozen=True)
class PdfTarget:
    topic: str
    output_name: str
    source: str
    priority: str
    note: str


TARGETS = [
    PdfTarget(
        "sysplorer",
        "Syslab与Sysplorer双向集成_2024a.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/07-MWORKS.Syslab和MWORKS.Sysplorer双向集成(2024a)/01-MWORKS.Syslab和MWORKS.Sysplorer双向集成.pdf",
        "P0",
        "Syslab/Sysplorer 双向数据、仿真与 API 集成流程。",
    ),
    PdfTarget(
        "sysplorer",
        "Syslab与Sysplorer双向集成_2025b.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/Syslab与Sysplorer双向集成.pdf",
        "P0",
        "较新版本的 Syslab/Sysplorer 集成材料。",
    ),
    PdfTarget(
        "sysplorer",
        "Modelica语法详解_模型行为描述.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/05-Modelica语法详解/04-Modelica语法详解-模型行为描述.pdf",
        "P0",
        "Modelica 方程、算法、事件等模型行为表达。",
    ),
    PdfTarget(
        "sysplorer",
        "Modelica语法详解_模型重用.md",
        "培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/05-Modelica语法详解/09-Modelica语法详解-模型重用.pdf",
        "P0",
        "继承、替换、参数化和可复用模型结构。",
    ),
    PdfTarget(
        "syslab",
        "MWORKS.Syslab控制系统工具箱.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/01-控制系统工具箱应用/01-2024a/MWORKS.Syslab控制系统工具箱.pdf",
        "P1",
        "控制系统建模、时域/频域分析、PID 与状态反馈。",
    ),
    PdfTarget(
        "syslab",
        "MWORKS.Syslab控制系统工具箱APP.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/02-控制系统设计与分析APP/01-2024a/MWORKS.Syslab控制系统工具箱APP(应用程序).pdf",
        "P1",
        "控制系统设计与分析 APP 操作流程。",
    ),
    PdfTarget(
        "optimization",
        "MWORKS.Sysplorer参数估计工具箱应用.md",
        "培训课程配套材料/01-官网课程配套材料/05-基于模型的设计优化/02-参数估计工具箱应用/01-2023b/MWORKS.Sysplorer参数估计工具箱应用.pdf",
        "P1",
        "模型参数估计、仿真对齐和优化流程。",
    ),
    PdfTarget(
        "control",
        "Syslab系统辨识工具箱.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/03-控制系统之系统辨识工具箱/01-2024b/Syslab控制系统之系统辨识工具箱.pdf",
        "P1",
        "辨识流程，可用于模型不确定性和控制器整定支撑。",
    ),
    PdfTarget(
        "control",
        "Syslab鲁棒控制工具箱.md",
        "培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/04-鲁棒控制工具箱应用/01-2024b/Syslab控制系统之鲁棒控制工具箱.pdf",
        "P1",
        "鲁棒控制分析和设计方法。",
    ),
    PdfTarget(
        "api",
        "MWORKS.Sysplorer外部接口_外部函数.md",
        "培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/02-MWORKS.Sysplorer外部接口-外部函数(C、C++、Fortran)/01-2023b/MWORKS.Sysplorer外部接口-外部函数(C、C++、Fortran).pdf",
        "P2",
        "外部函数接口，后续联动 C/C++ 或外部算法时参考。",
    ),
    PdfTarget(
        "api",
        "MWORKS.Sysplorer工具箱运行脚本_Python.md",
        "培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/03-MWORKS.Sysplorer工具箱运行脚本（Python）/01-2024a/MWORKS.Sysplorer工具箱运行脚本（Python）.pdf",
        "P2",
        "Sysplorer Python 脚本运行和自动化接口。",
    ),
    PdfTarget(
        "api",
        "MWORKS.Syslab外部函数调用.md",
        "培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/01-MWORKS.Syslab外部函数调用/01-2023a/MWORKS.Syslab外部函数调用.pdf",
        "P2",
        "Syslab 调用 Python/C/外部函数的参考。",
    ),
    PdfTarget(
        "challenge",
        "智能无人系统应用挑战赛_无人车避障竞赛规则.md",
        "培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/01-第一期/无人车避障3.0竞赛规则.pdf",
        "P1",
        "挑战赛规则和评价方式参考。",
    ),
    PdfTarget(
        "challenge",
        "智能无人系统应用挑战赛_专项培训一.md",
        "培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/01-第一期/智能无人系统应用挑战赛-无人车避障赛道专项培训（一）.pdf",
        "P1",
        "智能无人系统场景、模型和控制展示参考。",
    ),
    PdfTarget(
        "challenge",
        "智能无人系统应用挑战赛_专项培训二.md",
        "培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/02-第二期/无人车避障赛道专项培训（二）.pdf",
        "P1",
        "路径规划、避障和展示流程参考。",
    ),
]


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[int, str]:
    doc = fitz.open(path)
    pages: list[str] = []
    for index, page in enumerate(doc, start=1):
        text = clean_text(page.get_text("text"))
        if text:
            pages.append(f"## Page {index}\n\n```text\n{text}\n```")
        else:
            pages.append(f"## Page {index}\n\n> No extractable text found on this page.")
    return doc.page_count, "\n\n".join(pages)


def write_markdown(target: PdfTarget) -> dict[str, str]:
    source = SOURCE_ROOT / target.source
    output = OUTPUT_ROOT / target.topic / target.output_name
    output.parent.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        output.write_text(
            "\n".join(
                [
                    f"# {target.output_name.removesuffix('.md')}",
                    "",
                    f"- Source: `{source.as_posix()}`",
                    "- Converted by: `local PyMuPDF fallback`",
                    f"- Conversion date: `{date.today().isoformat()}`",
                    "- Review status: `missing source`",
                    f"- Priority: `{target.priority}`",
                    "",
                    "Source PDF was not found.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return {"source": target.source, "output": output.as_posix(), "status": "missing"}

    page_count, body = extract_pdf(source)
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:12]
    title = target.output_name.removesuffix(".md")
    output.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"- Source: `{source.as_posix()}`",
                "- Converted by: `local PyMuPDF fallback`",
                f"- Conversion date: `{date.today().isoformat()}`",
                "- Review status: `unchecked; MinerU retry recommended`",
                f"- Priority: `{target.priority}`",
                f"- Source SHA1: `{digest}`",
                f"- Pages: `{page_count}`",
                f"- Notes: {target.note}",
                "",
                "> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {"source": target.source, "output": output.as_posix(), "status": "converted", "pages": str(page_count)}


def write_index(results: list[dict[str, str]]) -> None:
    index_path = OUTPUT_ROOT / "转换索引.md"
    lines = [
        "# MWORKS PDF 转换索引",
        "",
        f"- Generated: `{date.today().isoformat()}`",
        "- Preferred converter: `MinerU MCP`",
        "- Current batch converter: `local PyMuPDF fallback`",
        "- Review note: 重要 API、公式、表格和代码块仍需结合 MCP 官方文档或原 PDF 复核。",
        "",
        "| Status | Topic | Pages | Markdown | Source |",
        "|---|---|---:|---|---|",
    ]
    by_output = {r["output"]: r for r in results}
    for target in TARGETS:
        output = (OUTPUT_ROOT / target.topic / target.output_name).as_posix()
        result = by_output.get(output, {})
        lines.append(
            "| "
            + " | ".join(
                [
                    result.get("status", "unknown"),
                    target.topic,
                    result.get("pages", "-"),
                    f"`{output}`",
                    f"`{target.source}`",
                ]
            )
            + " |"
        )
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    results = [write_markdown(target) for target in TARGETS]
    write_index(results)
    converted = sum(1 for r in results if r["status"] == "converted")
    missing = sum(1 for r in results if r["status"] == "missing")
    print(f"Converted PDFs: {converted}")
    print(f"Missing PDFs: {missing}")
    print(f"Index: {OUTPUT_ROOT / '转换索引.md'}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
