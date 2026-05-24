#!/usr/bin/env python3
"""
Scan the local MWORKS resource package and build Markdown indexes for Codex.

The script is intentionally conservative:
- It scores files by project relevance.
- It can use a lightweight PDF first-page preview to catch documents whose
  filename is vague but whose content is relevant.
- It writes scan indexes only by default.
- It can optionally extract text-like files into Markdown snippets, but this is
  disabled by default because the snippets are noisy and largely superseded by
  curated `Docs/Mworks/converted/` outputs.
- It lists PDF files for later conversion.

Usage:
    python Scripts/Docs/scan_mworks_docs.py
    python Scripts/Docs/scan_mworks_docs.py --top 120
    python Scripts/Docs/scan_mworks_docs.py --extract-snippets --extract-limit 80
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from typing import Iterable


DEFAULT_SOURCE = Path("MWORKS高校星火计划资料包")
DEFAULT_OUTPUT = Path("Docs/Mworks")

TEXT_EXTS = {
    ".txt",
    ".md",
    ".mo",
    ".jl",
    ".py",
    ".m",
    ".csv",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".c",
    ".cpp",
    ".h",
}

PDF_EXTS = {".pdf"}
SKIP_EXTS = {".mp4", ".avi", ".mov", ".flv", ".zip", ".rar", ".7z", ".dll", ".so", ".pyc"}

KEYWORDS = {
    "quadrotor": 40,
    "四旋翼": 40,
    "无人机": 36,
    "uav": 32,
    "mworks.sysplorer": 30,
    "sysplorer": 28,
    "mworks.syslab": 28,
    "syslab": 26,
    "sysblock": 24,
    "modelica": 24,
    "控制系统": 24,
    "控制": 16,
    "控制器": 16,
    "pid": 22,
    "mpc": 20,
    "nmpc": 20,
    "鲁棒控制": 24,
    "系统辨识": 22,
    "状态反馈": 18,
    "根轨迹": 16,
    "参数估计": 20,
    "路径规划": 22,
    "避障": 20,
    "编队": 18,
    "轨迹": 18,
    "飞行": 14,
    "优化": 18,
    "仿真": 16,
    "模型": 14,
    "可视化": 12,
    "三维": 12,
    "mcp": 12,
    "julia": 12,
    "matlab": 10,
    "接口": 10,
    "api": 10,
    "智能无人系统": 30,
    "挑战赛": 18,
}

CATEGORY_RULES = [
    ("quadrotor_uav", ["四旋翼", "无人机", "uav", "智能无人系统", "quadrotor"]),
    ("sysplorer_modeling", ["sysplorer", "modelica", ".mo", "建模", "模型"]),
    ("syslab_analysis", ["syslab", "julia", ".jl", "指标", "绘图", "数据"]),
    ("control_algorithm", ["控制", "pid", "mpc", "nmpc", "优化", "鲁棒"]),
    ("planning_formation", ["路径", "轨迹", "规划", "编队", "避障"]),
    ("mcp_api", ["mcp", "api", "接口", "开放架构"]),
    ("installation_training", ["安装", "基础功能", "快速入门", "培训"]),
]


@dataclass
class FileRecord:
    path: Path
    rel: str
    ext: str
    size: int
    score: int
    category: str
    matched: list[str]
    path_matched: list[str]
    content_matched: list[str]
    preview_chars: int
    review_reason: str


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def classify(search_text: str) -> str:
    lowered = search_text.lower()
    for category, words in CATEGORY_RULES:
        if any(word.lower() in lowered for word in words):
            return category
    return "other"


def keyword_score(text: str, scale: float = 1.0) -> tuple[int, list[str]]:
    haystack = normalize_text(text)
    score = 0
    matched: list[str] = []
    for keyword, weight in KEYWORDS.items():
        if keyword.lower() in haystack:
            score += max(1, int(weight * scale))
            matched.append(keyword)
    return score, matched


def score_file(
    path: Path,
    source: Path,
    *,
    scan_pdf_preview: bool,
    pdf_preview_pages: int,
    pdf_preview_max_chars: int,
) -> FileRecord:
    rel = path.relative_to(source).as_posix()
    ext = path.suffix.lower()
    path_score, path_matched = keyword_score(rel)
    content_score = 0
    content_matched: list[str] = []
    preview_chars = 0

    if ext in TEXT_EXTS:
        ext_score = 8
    elif ext in PDF_EXTS:
        ext_score = 6
    elif ext in SKIP_EXTS:
        ext_score = -30
    else:
        ext_score = 0

    if scan_pdf_preview and ext in PDF_EXTS:
        preview = extract_pdf_text(path, pdf_preview_max_chars, pages=pdf_preview_pages)
        preview_chars = len(preview)
        content_score, content_matched = keyword_score(preview, scale=0.65)

    size = path.stat().st_size
    size_score = 0
    if size > 100 * 1024 * 1024:
        size_score -= 50
    elif size > 50 * 1024 * 1024:
        size_score -= 15

    matched = sorted(set(path_matched + content_matched), key=lambda item: item.lower())
    score = path_score + content_score + ext_score + size_score
    category = classify(f"{rel} {' '.join(matched)}")
    if path_matched and content_matched:
        review_reason = "path+pdf_preview"
    elif content_matched:
        review_reason = "pdf_preview"
    elif path_matched:
        review_reason = "path"
    else:
        review_reason = "extension"
    return FileRecord(
        path,
        rel,
        ext,
        size,
        score,
        category,
        matched,
        path_matched,
        content_matched,
        preview_chars,
        review_reason,
    )


def safe_slug(text: str, max_len: int = 90) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", text, flags=re.UNICODE).strip("_")
    if len(slug) > max_len:
        digest = hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:8]
        slug = f"{slug[:max_len]}_{digest}"
    return slug or "file"


def read_text(path: Path, max_chars: int) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "gbk", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    return text[:max_chars]


def extract_pdf_text(path: Path, max_chars: int, pages: int = 5) -> str:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            result = subprocess.run(
                [pdftotext, "-f", "1", "-l", str(pages), str(path), "-"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=30,
            )
            if result.stdout:
                return result.stdout.decode("utf-8", errors="replace")[:max_chars]
        except Exception:
            pass

    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
            reader_cls = getattr(module, "PdfReader")
            reader = reader_cls(str(path))
            chunks = []
            for page in reader.pages[:pages]:
                chunks.append(page.extract_text() or "")
            return "\n".join(chunks)[:max_chars]
        except Exception:
            continue

    try:
        fitz = __import__("fitz")
        doc = fitz.open(str(path))
        chunks = []
        for index in range(min(pages, doc.page_count)):
            chunks.append(doc[index].get_text("text") or "")
        return "\n".join(chunks)[:max_chars]
    except Exception:
        pass

    return ""


def markdown_escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_table(records: Iterable[FileRecord], out_path: Path) -> None:
    rows = list(records)
    lines = [
        "# MWORKS 资料相关性索引",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "| Score | Category | Evidence | Size MB | Ext | File | Matched |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for r in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r.score),
                    markdown_escape_cell(r.category),
                    markdown_escape_cell(r.review_reason),
                    f"{r.size / 1024 / 1024:.2f}",
                    markdown_escape_cell(r.ext or "-"),
                    markdown_escape_cell(r.rel),
                    markdown_escape_cell(", ".join(r.matched)),
                ]
            )
            + " |"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_category_indexes(records: list[FileRecord], output: Path) -> None:
    category_dir = output / "scan" / "categories"
    category_dir.mkdir(parents=True, exist_ok=True)
    by_category: dict[str, list[FileRecord]] = {}
    for r in records:
        by_category.setdefault(r.category, []).append(r)

    for category, rows in sorted(by_category.items()):
        write_table(rows, category_dir / f"{category}.md")


def write_csv(records: list[FileRecord], out_path: Path) -> None:
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "score",
                "category",
                "size_bytes",
                "extension",
                "path",
                "matched",
                "path_matched",
                "content_matched",
                "preview_chars",
                "review_reason",
            ]
        )
        for r in records:
            writer.writerow(
                [
                    r.score,
                    r.category,
                    r.size,
                    r.ext,
                    r.rel,
                    ";".join(r.matched),
                    ";".join(r.path_matched),
                    ";".join(r.content_matched),
                    r.preview_chars,
                    r.review_reason,
                ]
            )


def write_pdf_review(records: list[FileRecord], output: Path) -> None:
    pdfs = [r for r in records if r.ext in PDF_EXTS]
    lines = [
        "# PDF 内容预览复核",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "本文件用于判断 `relevant_files.csv` 是否只依赖路径名。`Evidence=pdf_preview` 表示路径名不明显，但 PDF 首页文本命中了项目关键词。",
        "",
        "| Score | Category | Evidence | Preview Chars | Size MB | File | Content Matched |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    for r in pdfs:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r.score),
                    markdown_escape_cell(r.category),
                    markdown_escape_cell(r.review_reason),
                    str(r.preview_chars),
                    f"{r.size / 1024 / 1024:.2f}",
                    markdown_escape_cell(r.rel),
                    markdown_escape_cell(", ".join(r.content_matched) or "-"),
                ]
            )
            + " |"
        )
    (output / "scan" / "pdf_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def extract_records(records: list[FileRecord], output: Path, limit: int, max_chars: int) -> list[dict[str, str]]:
    extracted_dir = output / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[dict[str, str]] = []

    for r in records[:limit]:
        text = ""
        mode = ""
        if r.ext in TEXT_EXTS and r.size <= 5 * 1024 * 1024:
            text = read_text(r.path, max_chars)
            mode = "text"
        elif r.ext in PDF_EXTS:
            text = extract_pdf_text(r.path, max_chars)
            mode = "pdf_text" if text else "pdf_index_only"

        if not text and r.ext not in PDF_EXTS:
            continue

        slug = safe_slug(r.rel)
        out_file = extracted_dir / f"{slug}.md"
        body = [
            f"# {r.path.name}",
            "",
            f"- Source: `{r.rel}`",
            f"- Category: `{r.category}`",
            f"- Score: `{r.score}`",
            f"- Size: `{r.size / 1024 / 1024:.2f} MB`",
            f"- Extract mode: `{mode}`",
            "",
        ]
        if text:
            body.extend(["## Extracted Text", "", "```text", text.rstrip(), "```", ""])
        else:
            body.extend(
                [
                    "## Note",
                    "",
                    "PDF text extraction is not available in the current environment. Use this file as an index entry and convert the source PDF later.",
                    "",
                ]
            )
        out_file.write_text("\n".join(body), encoding="utf-8")
        extracted.append({"source": r.rel, "markdown": out_file.relative_to(output).as_posix(), "mode": mode})

    return extracted


def write_summary(records: list[FileRecord], extracted: list[dict[str, str]], output: Path, source: Path) -> None:
    counts: dict[str, int] = {}
    for r in records:
        counts[r.category] = counts.get(r.category, 0) + 1

    lines = [
        "# MWORKS 资料扫描摘要",
        "",
        f"- Source: `{source}`",
        f"- Total relevant files: `{len(records)}`",
        f"- Extracted markdown files: `{len(extracted)}`",
        "",
        "## Category Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            "## Main Outputs",
            "",
            "- `Docs/Mworks/scan/relevant_index.md`: ranked relevant file index",
            "- `Docs/Mworks/scan/relevant_files.csv`: machine-readable index",
            "- `Docs/Mworks/scan/pdf_review.md`: PDF first-page text relevance review",
            "- `Docs/Mworks/scan/categories/`: category indexes",
            "- `Docs/Mworks/converted/`: curated PDF/API conversion outputs",
            "",
            "## Recommended Next Steps",
            "",
            "1. Review `scan/categories/quadrotor_uav.md`, `control_algorithm.md`, `sysplorer_modeling.md`, and `syslab_analysis.md` first.",
            "2. Convert high-value PDFs with MinerU precise API or `Scripts/Docs/convert_mworks_pdfs.py` when needed.",
            "3. Keep noisy snippet extraction disabled unless a one-off local search task needs it.",
            "4. Update `Docs/Index/doc_index.md` after promoting topic documents.",
            "",
        ]
    )
    (output / "scan" / "scan_summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top", type=int, default=160)
    parser.add_argument("--extract-limit", type=int, default=100)
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--min-score", type=int, default=10)
    parser.add_argument("--pdf-preview-pages", type=int, default=5)
    parser.add_argument("--pdf-preview-max-chars", type=int, default=12000)
    parser.add_argument(
        "--no-pdf-preview",
        action="store_true",
        help="Skip lightweight PDF text preview and score paths only.",
    )
    parser.add_argument(
        "--extract-snippets",
        action="store_true",
        help="Generate Docs/Mworks/extracted Markdown snippets. Disabled by default to keep the repo lean.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source
    output = args.output
    if not source.exists():
        raise SystemExit(f"Source directory not found: {source}")

    scan_dir = output / "scan"
    scan_dir.mkdir(parents=True, exist_ok=True)

    records = [
        score_file(
            path,
            source,
            scan_pdf_preview=not args.no_pdf_preview,
            pdf_preview_pages=args.pdf_preview_pages,
            pdf_preview_max_chars=args.pdf_preview_max_chars,
        )
        for path in source.rglob("*")
        if path.is_file()
    ]
    records = [r for r in records if r.score >= args.min_score]
    records.sort(key=lambda r: (r.score, -r.size), reverse=True)
    records = records[: args.top]

    write_table(records, scan_dir / "relevant_index.md")
    write_csv(records, scan_dir / "relevant_files.csv")
    write_pdf_review(records, output)
    write_category_indexes(records, output)
    extracted: list[dict[str, str]] = []
    if args.extract_snippets:
        extracted = extract_records(records, output, args.extract_limit, args.max_chars)
    write_summary(records, extracted, output, source)

    print(f"Relevant files: {len(records)}")
    print(f"Extracted markdown files: {len(extracted)}")
    print(f"Summary: {scan_dir / 'scan_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
