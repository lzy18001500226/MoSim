#!/usr/bin/env python3
"""Regenerate a report copy from the original Word package.

The input DOCX is the complete layout and object baseline. This adapter edits
only the main document XML and field-refresh settings, then copies every
other ZIP entry from the baseline. It deliberately avoids loading and saving
the report through python-docx, which would reserialize the whole package and
can disturb native Word objects.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import re
import tempfile
import zipfile
from pathlib import Path

from lxml import etree


SCRIPT_DIR = Path(__file__).resolve().parent
REPORT_DIR = SCRIPT_DIR.parent
DEFAULT_WORD = REPORT_DIR / "MoSim_仿真分析报告_重构.docx"
DEFAULT_MARKDOWN = REPORT_DIR / "草稿" / "仿真分析报告_重构版.md"
DEFAULT_OUTPUT = REPORT_DIR / "MoSim_仿真分析报告_重构版.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
NS = {"w": W_NS}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REL = f"{{{REL_NS}}}"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
CAPTION_RE = re.compile(
    r"^(?P<kind>[图表])\s*(?P<chapter>\d+)\s*[-—–]\s*"
    r"(?P<sequence>\d+)\s+(?P<title>.+?)\s*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, default=DEFAULT_WORD)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def plain_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace(r"\*", "\x00LITERAL_STAR\x00")
    value = value.replace("**", "").replace("`", "").replace("*", "")
    value = value.replace("\x00LITERAL_STAR\x00", "*")
    value = re.sub(r"\\([\\`_[\]{}()#+.!-])", r"\1", value)
    return re.sub(r"\s+", " ", value).strip()


def markdown_abstract(markdown: Path) -> tuple[str, list[str]]:
    lines = markdown.read_text(encoding="utf-8").splitlines()
    title = next(line[2:].strip() for line in lines if line.startswith("# "))
    start = lines.index("## 摘要") + 1
    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if not line.strip():
            if current:
                paragraphs.append(plain_markdown(" ".join(current)))
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(plain_markdown(" ".join(current)))
    return title, paragraphs


def markdown_section_paragraphs(markdown: Path, heading: str) -> list[str]:
    """Read prose blocks from one Markdown section without importing layout markers."""
    lines = markdown.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration as exc:
        raise ValueError(f"Markdown heading not found: {heading}") from exc

    paragraphs: list[str] = []
    current: list[str] = []
    in_code = False

    def flush() -> None:
        nonlocal current
        if current:
            text = plain_markdown(" ".join(current))
            if text:
                paragraphs.append(text)
            current = []

    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("#"):
            break
        if not stripped or stripped.startswith("!") or stripped.startswith("|"):
            flush()
            continue
        if normalize_caption_text(stripped) is not None:
            flush()
            continue
        if re.match(r"^\d+\.\s+", stripped):
            flush()
            paragraphs.append(plain_markdown(stripped))
            continue
        current.append(stripped)
    flush()
    return paragraphs


def markdown_caption_map(markdown: Path) -> dict[tuple[str, int, int], str]:
    captions: dict[tuple[str, int, int], str] = {}
    for line in markdown.read_text(encoding="utf-8").splitlines():
        normalized = normalize_caption_text(plain_markdown(line.strip()))
        if normalized is None:
            continue
        match = CAPTION_RE.match(normalized)
        assert match is not None
        key = (match.group("kind"), int(match.group("chapter")), int(match.group("sequence")))
        captions[key] = normalized
    return captions


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def direct_paragraphs(body: etree._Element) -> list[etree._Element]:
    return [child for child in body if child.tag == W + "p"]


def find_paragraph(
    body: etree._Element,
    text: str,
    style_id: str | None = None,
) -> etree._Element:
    for paragraph in direct_paragraphs(body):
        if paragraph_text(paragraph) != text:
            continue
        if style_id is not None:
            p_style = paragraph.find("./w:pPr/w:pStyle", namespaces=NS)
            if p_style is None or p_style.get(W + "val") != style_id:
                continue
        return paragraph
    raise ValueError(f"Paragraph not found: {text!r} style={style_id!r}")


def find_paragraph_prefix(body: etree._Element, prefix: str) -> etree._Element:
    for paragraph in direct_paragraphs(body):
        if paragraph_text(paragraph).startswith(prefix):
            return paragraph
    raise ValueError(f"Paragraph prefix not found: {prefix!r}")


def replace_paragraph_prefix(
    body: etree._Element,
    prefix: str,
    text: str,
) -> bool:
    paragraph = find_paragraph_prefix(body, prefix)
    return set_paragraph_text(paragraph, text)


def remove_paragraph(body: etree._Element, paragraph: etree._Element) -> None:
    body.remove(paragraph)


def apply_explicit_caption_updates(
    body: etree._Element,
    updates: dict[str, str],
) -> int:
    changed = 0
    for old, new in updates.items():
        paragraph = find_paragraph(body, old)
        changed += int(set_paragraph_text(paragraph, new))
    return changed


def set_paragraph_text(paragraph: etree._Element, text: str) -> bool:
    if paragraph_text(paragraph) == text:
        return False
    text_nodes = paragraph.xpath(".//w:t", namespaces=NS)
    if not text_nodes:
        run = etree.SubElement(paragraph, W + "r")
        text_node = etree.SubElement(run, W + "t")
        text_nodes = [text_node]
    text_nodes[0].text = text
    if text.startswith(" ") or text.endswith(" "):
        text_nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    else:
        text_nodes[0].attrib.pop("{http://www.w3.org/XML/1998/namespace}space", None)
    for node in text_nodes[1:]:
        node.text = ""
        node.attrib.pop("{http://www.w3.org/XML/1998/namespace}space", None)
    return True


def insert_paragraph_before(
    body: etree._Element,
    anchor: etree._Element,
    text: str,
    template: etree._Element,
) -> etree._Element:
    paragraph = deepcopy(template)
    set_paragraph_text(paragraph, text)
    body.insert(body.index(anchor), paragraph)
    return paragraph


def insert_heading_before(
    body: etree._Element,
    anchor: etree._Element,
    text: str,
    template: etree._Element,
) -> etree._Element:
    paragraph = deepcopy(template)
    set_paragraph_text(paragraph, text)
    set_heading_level(paragraph, "2")
    body.insert(body.index(anchor), paragraph)
    return paragraph


def replace_section_paragraphs(
    body: etree._Element,
    start_heading: etree._Element,
    end_heading: etree._Element,
    texts: list[str],
) -> int:
    """Replace prose paragraphs between headings while leaving tables in place."""
    start_index = body.index(start_heading)
    end_index = body.index(end_heading)
    existing = [
        child for child in list(body)[start_index + 1 : end_index]
        if child.tag == W + "p"
    ]
    if not existing:
        raise ValueError(f"No paragraphs in section {paragraph_text(start_heading)!r}")
    template = existing[0]
    for paragraph in existing:
        body.remove(paragraph)
    insert_index = body.index(end_heading)
    for offset, text in enumerate(texts):
        paragraph = deepcopy(template)
        set_paragraph_text(paragraph, text)
        body.insert(insert_index + offset, paragraph)
    return len(existing) + len(texts)


def add_markdown_figure(
    body: etree._Element,
    relationships_root: etree._Element,
    anchor: etree._Element,
    image_path: Path,
    caption: str,
) -> dict[str, bytes]:
    """Add one source figure by cloning an existing Word image paragraph."""
    image_template = next(
        paragraph
        for paragraph in direct_paragraphs(body)
        if paragraph.xpath(".//w:drawing", namespaces=NS)
    )
    caption_template = find_paragraph_prefix(body, "图1-3")
    blip = image_template.find(f".//{{{A_NS}}}blip")
    if blip is None:
        raise ValueError("Could not find an image relationship in the baseline")
    relationship_id = "rIdMoSimUav14"
    if relationships_root.xpath(
        f"./rel:Relationship[@Id='{relationship_id}']",
        namespaces={"rel": REL_NS},
    ):
        raise ValueError(f"Relationship already exists: {relationship_id}")
    relationship = etree.SubElement(relationships_root, REL + "Relationship")
    relationship.set("Id", relationship_id)
    relationship.set(
        "Type",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
    )
    media_name = "word/media/mosim_uav_toolbox_figure_1_4.png"
    relationship.set("Target", "media/mosim_uav_toolbox_figure_1_4.png")
    image_paragraph = deepcopy(image_template)
    image_blip = image_paragraph.find(f".//{{{A_NS}}}blip")
    assert image_blip is not None
    image_blip.set(f"{{{R_NS}}}embed", relationship_id)
    caption_paragraph = deepcopy(caption_template)
    set_paragraph_text(caption_paragraph, caption)
    body.insert(body.index(anchor), image_paragraph)
    body.insert(body.index(anchor), caption_paragraph)
    return {media_name: image_path.read_bytes()}


def set_heading_level(paragraph: etree._Element, style_id: str) -> None:
    p_pr = paragraph.find("./w:pPr", namespaces=NS)
    if p_pr is None:
        p_pr = etree.Element(W + "pPr")
        paragraph.insert(0, p_pr)
    p_style = p_pr.find("./w:pStyle", namespaces=NS)
    if p_style is None:
        p_style = etree.Element(W + "pStyle")
        p_pr.insert(0, p_style)
    p_style.set(W + "val", style_id)


def normalize_caption_text(text: str) -> str | None:
    match = CAPTION_RE.match(text.strip())
    if not match:
        return None
    return (
        f"{match.group('kind')}{int(match.group('chapter'))}-"
        f"{int(match.group('sequence'))} {match.group('title').strip()}"
    )


def normalize_caption_spacing(body: etree._Element) -> int:
    """Use the report caption contract: 图11-1 Title / 表11-1 Title."""
    changed = 0
    for paragraph in direct_paragraphs(body):
        text = paragraph_text(paragraph)
        normalized = normalize_caption_text(text)
        if normalized is None or not paragraph.xpath(".//w:t", namespaces=NS):
            continue
        if paragraph.xpath(".//w:fldChar | .//w:fldSimple", namespaces=NS):
            continue
        if normalized == text:
            continue
        set_paragraph_text(paragraph, normalized)
        changed += 1
    return changed


def apply_markdown_captions(body: etree._Element, captions: dict[tuple[str, int, int], str]) -> int:
    changed = 0
    for paragraph in direct_paragraphs(body):
        current = paragraph_text(paragraph)
        normalized = normalize_caption_text(current)
        if normalized is None:
            continue
        match = CAPTION_RE.match(normalized)
        assert match is not None
        key = (match.group("kind"), int(match.group("chapter")), int(match.group("sequence")))
        target = captions.get(key)
        if target is not None and target != current:
            changed += int(set_paragraph_text(paragraph, target))
    return changed


def markdown_caption_segments(markdown: Path) -> list[list[str]]:
    """Collect prose between Markdown figure/table captions.

    Caption anchors make this safe for the manual Word layout: a segment is
    synchronized only when the baseline has the same number of prose
    paragraphs between the same anchors. Code blocks, headings, tables, and
    image references are intentionally excluded.
    """
    segments: list[list[str]] = [[]]
    current: list[str] = []
    in_code = False

    def flush() -> None:
        nonlocal current
        if current:
            text = plain_markdown(" ".join(current))
            if text:
                segments[-1].append(text)
            current = []

    for line in markdown.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        caption = normalize_caption_text(plain_markdown(stripped))
        if caption is not None:
            flush()
            segments.append([])
            continue
        if not stripped or stripped.startswith("!") or stripped.startswith("|") or stripped.startswith("#"):
            flush()
            continue
        if re.match(r"^(?:[-*+]\s+|\(?\d+[.)]\s+)", stripped):
            flush()
            segments[-1].append(plain_markdown(stripped))
            continue
        current.append(stripped)
    flush()
    return segments


def paragraph_has_formula_or_field(paragraph: etree._Element) -> bool:
    return bool(
        paragraph.xpath(
            ".//m:oMath|.//m:oMathPara|.//w:fldChar|.//w:fldSimple",
            namespaces={**NS, "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"},
        )
    )


def text_has_formula_markup(text: str) -> bool:
    return bool(re.search(r"(?:\\\\[A-Za-z]|\\\\\(|\\\\\[|\$[^$]+\$)", text))


def synchronize_equal_caption_segments(
    body: etree._Element,
    markdown: Path,
) -> tuple[int, dict[str, int]]:
    source_segments = markdown_caption_segments(markdown)
    target_segments: list[list[etree._Element]] = [[]]
    for paragraph in direct_paragraphs(body):
        text = paragraph_text(paragraph)
        if normalize_caption_text(text) is not None:
            target_segments.append([])
            continue
        p_style = paragraph.find("./w:pPr/w:pStyle", namespaces=NS)
        style_id = p_style.get(W + "val", "") if p_style is not None else ""
        if not text or paragraph.xpath(".//w:drawing|.//w:pict", namespaces=NS):
            continue
        if style_id in {"1", "2", "3"}:
            continue
        target_segments[-1].append(paragraph)

    changed = 0
    equal_segments = 0
    unequal_segments = 0
    skipped_formula = 0
    for source_segment, target_segment in zip(source_segments, target_segments):
        if len(source_segment) != len(target_segment):
            unequal_segments += 1
            continue
        equal_segments += 1
        for source_text, target_paragraph in zip(source_segment, target_segment):
            if text_has_formula_markup(source_text) or paragraph_has_formula_or_field(target_paragraph):
                skipped_formula += 1
                continue
            changed += int(set_paragraph_text(target_paragraph, source_text))
    return changed, {
        "source_segments": len(source_segments),
        "target_segments": len(target_segments),
        "equal_segments": equal_segments,
        "unequal_segments": unequal_segments,
        "skipped_formula_or_field": skipped_formula,
    }


def update_visible_toc(
    document_root: etree._Element,
    replacements: dict[str, str],
    remove_prefixes: tuple[str, ...] = (),
) -> int:
    changed = 0
    for paragraph in document_root.xpath(".//w:sdtContent//w:p", namespaces=NS):
        text_nodes = paragraph.xpath(".//w:t", namespaces=NS)
        if not text_nodes:
            continue
        old = "".join(node.text or "" for node in text_nodes)
        if any(old.startswith(prefix) for prefix in remove_prefixes):
            parent = paragraph.getparent()
            if parent is not None:
                parent.remove(paragraph)
                changed += 1
            continue
        new = old
        for source, target in replacements.items():
            new = new.replace(source, target)
        if new == old:
            continue
        page_number = text_nodes[-1].text or ""
        has_page_number = bool(re.fullmatch(r"\d+", page_number))
        title = new[:-len(page_number)] if has_page_number else new
        if has_page_number:
            text_nodes[0].text = title
            for node in text_nodes[1:-1]:
                node.text = ""
            text_nodes[-1].text = page_number
        else:
            text_nodes[0].text = new
            for node in text_nodes[1:]:
                node.text = ""
        changed += 1
    return changed


def enable_field_refresh(settings_root: etree._Element) -> None:
    node = settings_root.find("./w:updateFields", namespaces=NS)
    if node is None:
        node = etree.Element(W + "updateFields")
        settings_root.insert(0, node)
    node.set(W + "val", "true")


def write_package(
    source: Path,
    output: Path,
    document_xml: bytes,
    settings_xml: bytes,
    relationships_xml: bytes,
    extra_entries: dict[str, bytes],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f"{output.stem}_", suffix=".docx", dir=output.parent, delete=False
    ) as temp:
        temp_path = Path(temp.name)
    try:
        with zipfile.ZipFile(source, "r") as source_zip, zipfile.ZipFile(
            temp_path, "w"
        ) as target_zip:
            for info in source_zip.infolist():
                if info.filename == "word/document.xml":
                    data = document_xml
                elif info.filename == "word/settings.xml":
                    data = settings_xml
                elif info.filename == "word/_rels/document.xml.rels":
                    data = relationships_xml
                else:
                    data = source_zip.read(info.filename)
                target_zip.writestr(info, data)
            for filename, data in extra_entries.items():
                target_zip.writestr(filename, data)
        temp_path.replace(output)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    args = parse_args()
    source = args.word.resolve()
    markdown = args.markdown.resolve()
    output = args.output.resolve()
    if source == output:
        raise ValueError("The output must be a new DOCX; the Word baseline is never overwritten.")
    if not source.exists() or not markdown.exists():
        raise FileNotFoundError(f"Missing input: {source} or {markdown}")

    title, abstract = markdown_abstract(markdown)
    if len(abstract) != 3:
        raise ValueError(f"Expected three abstract paragraphs, got {len(abstract)}")
    abstract_for_word = [abstract[0], abstract[1], abstract[2], ""]

    with zipfile.ZipFile(source, "r") as source_zip:
        document_root = etree.fromstring(source_zip.read("word/document.xml"))
        settings_root = etree.fromstring(source_zip.read("word/settings.xml"))
        relationships_root = etree.fromstring(
            source_zip.read("word/_rels/document.xml.rels")
        )

    body = document_root.find("./w:body", namespaces=NS)
    if body is None:
        raise ValueError("DOCX body is missing")

    paragraphs = direct_paragraphs(body)
    if len(paragraphs) < 6:
        raise ValueError("The Word baseline does not contain the expected title/abstract block")
    changed_paragraphs = int(set_paragraph_text(paragraphs[0], title))
    for paragraph, text in zip(paragraphs[2:6], abstract_for_word, strict=True):
        changed_paragraphs += int(set_paragraph_text(paragraph, text))

    # Synchronize the prose revisions that are present in the current Markdown
    # while retaining the baseline's drawing, table, formula, and pagination XML.
    section_12 = markdown_section_paragraphs(markdown, "### 1.2 MoSim 平台要解决的问题")
    section_13 = markdown_section_paragraphs(markdown, "### 1.3 功能覆盖与工具链对比")
    section_14 = markdown_section_paragraphs(markdown, "### 1.4 主要工作概述")
    section_17 = markdown_section_paragraphs(markdown, "### 1.7 报告阅读说明")
    section_10 = markdown_section_paragraphs(markdown, "## 十、编队控制与自主避障")
    section_103 = markdown_section_paragraphs(markdown, "### 10.3 单机 OpenBlocks 避障")
    section_104 = markdown_section_paragraphs(markdown, "### 10.4 三机 OpenBlocks 可重构编队避障")
    section_112 = markdown_section_paragraphs(markdown, "### 11.2 性能指标与验证结果")
    section_12_chapter = markdown_section_paragraphs(markdown, "## 十二、px4ctrl C99 代码生成与 SIL 验证")
    section_123 = markdown_section_paragraphs(markdown, "### 12.3 50 s SIL 结果")
    section_133 = markdown_section_paragraphs(markdown, "### 13.3 运行时稳态跟踪结果")
    section_134 = markdown_section_paragraphs(markdown, "### 13.4 感知与规划组件原理")
    section_163 = markdown_section_paragraphs(markdown, "### 16.3 已完成工作总结")
    if len(section_12) != 2 or len(section_13) < 8 or len(section_14) < 2:
        raise ValueError("Unexpected Markdown paragraph shape in chapter 1")
    if len(section_17) != 2 or len(section_163) != 10:
        raise ValueError("Unexpected Markdown paragraph shape in chapters 1 or 16")
    if not section_10 or len(section_103) < 8 or len(section_104) < 9:
        raise ValueError("Unexpected Markdown paragraph shape in chapter 10")
    if not section_112 or not section_12_chapter or len(section_123) < 2 or len(section_133) < 2:
        raise ValueError("Unexpected Markdown paragraph shape in chapters 11-13")

    for prefix, text in (
        ("MoSim 的出发点很明确", section_12[0]),
        ("技术选型上", section_12[1]),
         ("围绕\"可审查的物理建模", section_14[0]),
        ("以云纵 150 实机为参照", section_14[1]),
        ("从平台交付视角看", section_14[2] if len(section_14) > 2 else section_14[1]),
    ):
        try:
            paragraph = find_paragraph_prefix(body, prefix)
        except ValueError:
            continue
        changed_paragraphs += int(set_paragraph_text(paragraph, text))

    # The old Word baseline had no visible 1.3 heading and omitted two prose
    # blocks that are now in the Markdown source. Add them around existing image
    # anchors without reconstructing the image run or its relationship.
    first_figure = find_paragraph_prefix(body, "图1-1")
    if not any(paragraph_text(p) == "功能覆盖与工具链对比" for p in direct_paragraphs(body)):
        heading_template = next(
            p for p in direct_paragraphs(body)
            if p.find("./w:pPr/w:pStyle", namespaces=NS) is not None
            and p.find("./w:pPr/w:pStyle", namespaces=NS).get(W + "val") == "2"
        )
        insert_heading_before(body, first_figure, "功能覆盖与工具链对比", heading_template)
        changed_paragraphs += 1
    first_figure = find_paragraph_prefix(body, "图1-1")
    # The baseline placed an older MATLAB-comparison paragraph before the new
    # 1.3 heading. Reuse its styled paragraph for the current Markdown text,
    # then place it under the new heading instead of duplicating it.
    try:
        toolchain_paragraph = find_paragraph(body, section_13[0])
    except ValueError:
        toolchain_paragraph = find_paragraph_prefix(body, "MATLAB UAV Toolbox 的典型界面如下")
        set_paragraph_text(toolchain_paragraph, section_13[0])
    body.remove(toolchain_paragraph)
    body.insert(body.index(first_figure), toolchain_paragraph)
    changed_paragraphs += 1
    first_figure_prose = toolchain_paragraph
    if not any(paragraph_text(p) == section_13[1] for p in direct_paragraphs(body)):
        insert_paragraph_before(body, first_figure, section_13[1], first_figure_prose)
        changed_paragraphs += 1
    for old_caption, text in (
        ("图1-1 MATLAB UAV Toolbox 地面控制站界面", section_13[2]),
        ("图1-2 MATLAB UAV Toolbox 虚幻引擎场景仿真", section_13[3]),
        ("图1-3 MATLAB UAV Toolbox 用户界面与模型管理", section_13[4]),
    ):
        caption = find_paragraph(body, old_caption)
        caption_index = body.index(caption)
        prose = next(
            child
            for child in list(body)[caption_index + 1 :]
            if child.tag == W + "p" and paragraph_text(child).strip()
        )
        changed_paragraphs += int(set_paragraph_text(prose, text))
    chapter_14_heading = find_paragraph(body, "主要工作概述", "2")
    last_existing_figure_prose = find_paragraph(body, section_13[4])
    extra_entries: dict[str, bytes] = {}
    figure_14_caption = markdown_caption_map(markdown).get(
        ("图", 1, 4), "图1-4 MATLAB UAV Package Delivery 官方参考应用中的激光雷达障碍物感知与三维避障示意"
    )
    figure_14_path = REPORT_DIR / "图" / "UAV ToolBox" / "障碍物感知.png"
    if figure_14_path.exists() and not any(
        paragraph_text(p).startswith("图1-4") for p in direct_paragraphs(body)
    ):
        extra_entries.update(
            add_markdown_figure(
                body,
                relationships_root,
                chapter_14_heading,
                figure_14_path,
                figure_14_caption,
            )
        )
        changed_paragraphs += 2
    figure_14_prose = section_13[5]
    if not any(paragraph_text(p) == figure_14_prose for p in direct_paragraphs(body)):
        insert_paragraph_before(body, chapter_14_heading, figure_14_prose, last_existing_figure_prose)
        changed_paragraphs += 1
    for text in section_13[6:8]:
        if not any(paragraph_text(p) == text for p in direct_paragraphs(body)):
            insert_paragraph_before(body, chapter_14_heading, text, last_existing_figure_prose)
            changed_paragraphs += 1

    reading_heading = find_paragraph(body, "报告阅读说明", "2")
    experiment_heading = find_paragraph(body, "实验设计与评价体系", "1")
    changed_paragraphs += replace_section_paragraphs(
        body, reading_heading, experiment_heading, section_17
    )

    old_section_163 = find_paragraph(body, "下一阶段优化方向", "2")
    completed_section_163 = find_paragraph(body, "对工业软件自主化的启示", "2")
    changed_paragraphs += replace_section_paragraphs(
        body,
        old_section_163,
        completed_section_163,
        section_163,
    )
    changed_paragraphs += int(set_paragraph_text(old_section_163, "已完成工作总结"))
    changed_paragraphs += int(
        set_paragraph_text(
            find_paragraph(body, "运行时部署环境", "2"),
            "部署目标环境说明",
        )
    )

    # Chapter 10 was merged in the Markdown source, while the Word baseline
    # still carried the former OpenBlocks chapter as a separate section. Keep
    # its native figures and tables, but bring the visible hierarchy and prose
    # into the merged chapter before applying caption renumbering.
    changed_paragraphs += replace_paragraph_prefix(body, "本章展示 MoSim 从单机位姿控制", section_10[0])
    changed_paragraphs += int(
        set_paragraph_text(
            find_paragraph(body, "三机 Figure8 编队结果", "2"),
            "三机编队 Figure8 结果",
        )
    )
    summary_heading = find_paragraph(body, "多机协同任务小结", "2")
    summary_heading_index = body.index(summary_heading)
    summary_body = next(
        child
        for child in list(body)[summary_heading_index + 1 :]
        if child.tag == W + "p"
    )
    remove_paragraph(body, summary_body)
    remove_paragraph(body, summary_heading)
    changed_paragraphs += 2

    openblocks_heading = find_paragraph(body, "OpenBlocks 障碍地图规划与多机执行", "2")
    changed_paragraphs += int(set_paragraph_text(openblocks_heading, "单机 OpenBlocks 避障"))
    single_openblocks_heading = find_paragraph(body, "单机 OpenBlocks 避障", "3")
    remove_paragraph(body, single_openblocks_heading)
    changed_paragraphs += 1
    three_openblocks_heading = find_paragraph(body, "三机 OpenBlocks 可重构编队避障", "3")
    set_heading_level(three_openblocks_heading, "2")
    changed_paragraphs += 1

    openblocks_intro = find_paragraph_prefix(body, "前两章的参考轨迹由解析式给出")
    changed_paragraphs += int(set_paragraph_text(openblocks_intro, section_103[0]))
    diffplanner_caption = find_paragraph(body, "图11-1 DiffPlanner 单机与三机规划链路")
    diffplanner_image = body[body.index(diffplanner_caption) - 1]
    insert_paragraph_before(body, diffplanner_image, section_103[1], openblocks_intro)
    changed_paragraphs += 1

    for prefix, text in (
        ("下图展示 FAST-LIO 状态估计", section_103[2]),
        ("地图共 7118 个障碍体", section_103[3]),
        ("Results/planning/openblocks_single_uav_px4ctrl_completion", section_103[4]),
        ("该路径记录完成了从障碍地图规划参考", section_103[5]),
        ("水平面轨迹图展示单机沿规划路径", section_103[6]),
        ("高度曲线显示总位置误差", section_103[7]),
        ("本节并列呈现两条三机记录", section_104[0]),
        ("当前 PX4CTRL 记录位于 Results/planning/three_uav_openblocks_px4ctrl_completion", section_104[1]),
        ("三机各自的跟踪指标如表12-2", section_104[2]),
        ("上表按机分列", section_104[3]),
        ("当前 PX4CTRL 记录完成了 304.84 s", section_104[4]),
    ):
        changed_paragraphs += int(replace_paragraph_prefix(body, prefix, text))

    stale_openblocks_summary = find_paragraph_prefix(body, "本章图件对应三条 MWORKS 全机 PX4CTRL")
    remove_paragraph(body, stale_openblocks_summary)
    changed_paragraphs += 1

    # The baseline contains one stale industrial-scene drawing in the former
    # planning section. The same asset is already present in the dedicated
    # Chapter 14 section, so remove only the stale paragraph/caption pair.
    stale_industrial_caption = find_paragraph(
        body,
        "图14-1 FUEL 自主探索任务的体素栅格与运动轨迹",
    )
    stale_index = body.index(stale_industrial_caption)
    stale_image = body[stale_index - 1]
    if stale_image.tag == W + "p" and stale_image.xpath(".//w:drawing", namespaces=NS):
        remove_paragraph(body, stale_image)
    remove_paragraph(body, stale_industrial_caption)
    changed_paragraphs += 2

    stale_controller_caption = find_paragraph(
        body,
        "图6-24 滑模控制族的分类与各变体适用场景",
    )
    stale_controller_index = body.index(stale_controller_caption)
    stale_controller_image = body[stale_controller_index - 1]
    if stale_controller_image.tag == W + "p" and stale_controller_image.xpath(
        ".//w:drawing", namespaces=NS
    ):
        remove_paragraph(body, stale_controller_image)
    remove_paragraph(body, stale_controller_caption)
    changed_paragraphs += 2
    for paragraph in direct_paragraphs(body):
        match = re.match(r"^图6-(?P<number>\d+) (?P<title>.+)$", paragraph_text(paragraph))
        if match is None:
            continue
        number = int(match.group("number"))
        if 25 <= number <= 50:
            changed_paragraphs += int(
                set_paragraph_text(
                    paragraph,
                    f"图6-{number - 1} {match.group('title')}",
                )
            )

    caption_updates = {
        "图1-1 MATLAB UAV Toolbox 地面控制站界面": "图1-1 MATLAB UAV Package Delivery 官方参考应用的工程入口与 QGroundControl 连接配置",
        "图1-2 MATLAB UAV Toolbox 虚幻引擎场景仿真": "图1-2 MATLAB UAV Package Delivery 官方参考应用中的 QGroundControl、Unreal Engine 与 MATLAB 联合仿真视图",
        "图1-3 MATLAB UAV Toolbox 用户界面与模型管理": "图1-3 MATLAB UAV Package Delivery 官方参考应用的 Simulink 顶层模型",
        "图6-11 pid_awff_linear_eso控制器图形模型结构（AWFF-ESO）": "图6-11 pid_awff_linear_eso控制器图形模型结构(AWFF-ESO)",
        "表6-1 48 条控制器的公式位置与源码映射": "表6-2 48 条控制器的公式位置与源码映射登记",
        "图11-1 DiffPlanner 单机与三机规划链路": "图10-9 DiffPlanner 单机与三机规划链路",
        "图11-2 FAST-LIO 定位精度与规划部署边界": "图10-10 FAST-LIO 定位精度与规划部署边界",
        "表11-1 单机 OpenBlocks 场景的跟踪与飞行包线观测": "表10-3 单机 OpenBlocks 场景的跟踪与飞行包线观测",
        "图11-3 单机在 OpenBlocks 障碍地图中的水平面轨迹": "图10-11 单机在 OpenBlocks 障碍地图中的水平面轨迹",
        "图11-4 单机 OpenBlocks 高度通道跟踪": "图10-12 单机 OpenBlocks 高度通道跟踪",
        "图11-5 单机 OpenBlocks 位置误差时程": "图10-13 单机 OpenBlocks 位置误差时程",
        "表11-2 三机 OpenBlocks 编队各机的跟踪误差指标": "表10-4 三机 OpenBlocks 编队各机的跟踪误差指标",
        "表11-3 三机 OpenBlocks 编队的整体间距与队形指标": "表10-5 三机 OpenBlocks 编队的整体间距与队形指标",
        "图11-6 三机在 OpenBlocks 障碍地图中的水平面轨迹": "图10-14 三机在 OpenBlocks 障碍地图中的水平面轨迹",
        "图11-7 三机 OpenBlocks 机间距离时程": "图10-15 三机 OpenBlocks 机间距离时程",
        "图11-8 三机 OpenBlocks 跟踪误差时程": "图10-16 三机 OpenBlocks 跟踪误差时程",
        "图11-9 三机 OpenBlocks 最小避障间隙及其下界": "图10-17 三机 OpenBlocks 最小避障间隙及其下界",
        "图14-1 Unreal Engine 工业场景：化工厂管廊环境": "图14-1 Unreal Engine 工业场景:化工厂管廊环境",
    }
    changed_paragraphs += apply_explicit_caption_updates(body, caption_updates)

    # These paragraphs are already present in the baseline but contain the old
    # chapter references or the pre-restructure wording.
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "(2) P99 延迟",
        "(2) P99 延迟 5.71 ms 远低于 5 ms 控制周期 (200 Hz),为控制计算和通信留有充足裕度",
    )
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "第八至十二章的全部验证",
        section_12_chapter[0],
    )
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "以 wind_hover_20260801_002 的稳态悬停末 8 s",
        section_133[0],
    )
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "其余四条记录的同类指标落在水平 RMSE",
        section_133[1],
    )
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "后续章节中的避障验证",
        section_134[0],
    )

    heading_updates = {
        "指标定义与负样本处理": "实验设计与评价体系",
        "三机编队 Figure8 与 ECBF 安全参考调节": "编队控制与自主避障",
        "px4ctrl C99 代码生成、可移植构建与 SIL 验证": "px4ctrl C99 代码生成与 SIL 验证",
    }
    applied_heading_updates: dict[str, str] = {}
    for old, new in heading_updates.items():
        try:
            paragraph = find_paragraph(body, old, "1")
        except ValueError:
            continue
        if set_paragraph_text(paragraph, new):
            changed_paragraphs += 1
            applied_heading_updates[old] = new

    # Keep the baseline's section order and manual keep-with-next settings.
    normalized_captions = normalize_caption_spacing(body)
    # The stale pre-merge figures were removed and the OpenBlocks captions were
    # renumbered above, so the remaining caption keys are unique and can now be
    # synchronized against Markdown as a final title-level check.
    captions = markdown_caption_map(markdown)
    caption_keys = [key for key in captions]
    if len(caption_keys) != len(set(caption_keys)):
        raise ValueError("Markdown caption keys are not unique")
    markdown_captions = apply_markdown_captions(body, captions)
    synced_caption_segment_paragraphs, caption_segment_stats = synchronize_equal_caption_segments(
        body, markdown
    )
    changed_paragraphs += synced_caption_segment_paragraphs
    # The source keeps the SIL source path and the table introduction in one
    # Markdown paragraph, while the hand-laid Word baseline split that text
    # across two paragraphs. Preserve the spacing paragraph but restore the
    # source wording and the correct post-restructure table reference.
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "第八至十章的全部验证",
        section_12_chapter[0],
    )
    try:
        sil_source = find_paragraph_prefix(
            body,
            "来源:Results/control_platform/px4ctrl_codegen_sil_v1/logs/CLOSED_LOOP_SIL_",
        )
        changed_paragraphs += int(set_paragraph_text(sil_source, section_123[0]))
        split_tail = find_paragraph(body, "RESULT.json。")
        changed_paragraphs += int(set_paragraph_text(split_tail, ""))
    except ValueError:
        pass
    changed_paragraphs += replace_paragraph_prefix(
        body,
        "图形模型与生成 C 代码在同一 50 s ClimbPath",
        section_123[1],
    )
    toc_replacements = {
        **applied_heading_updates,
        "10.3 多机协同任务小结": "10.3 单机 OpenBlocks 避障",
        "十一、 感知与规划组件原理": "十一、 MWORKS Live 实时联合仿真验证",
        "11.1 FAST-LIO 状态估计": "11.1 实时仿真链路架构",
        "11.2 FUEL 自主探索规划器": "11.2 性能指标与验证结果",
        "11.3 Diff-Planner 局部轨迹优化": "11.3 MWORKS Live 连接验证",
        "十三、 px4ctrl C99 代码生成与 SIL 验证": "十二、 px4ctrl C99 代码生成与 SIL 验证",
        "13.1 图形模型到 C 的链路": "12.1 图形模型到 C 的链路",
        "13.2 生成产物与交付": "12.2 生成产物与交付",
        "13.3 50 s SIL 结果": "12.3 50 s SIL 结果",
        "13.4 SIL 一致性公式": "12.4 SIL 一致性公式",
        "13.5 运行时部署环境": "12.5 部署目标环境说明",
        "13.5.1 Gazebo 物理仿真器": "12.5.1 Gazebo 物理仿真器",
        "13.5.2 Unreal Engine 工业场景": "12.5.2 Unreal Engine 工业场景",
        "13.5.3 UE→Gazebo 场景导出链路": "12.5.3 UE→Gazebo 场景导出链路",
        "13.5.4 QGroundControl 地面站": "12.5.4 QGroundControl 地面站",
        "十四、 生成 C99 在 ROS1/Gazebo 的运行时闭环": "十三、 生成 C99 在 ROS1/Gazebo 的运行时闭环",
        "14.1 运行时链路与后端识别": "13.1 运行时链路与后端识别",
        "14.2 生命周期结果": "13.2 生命周期结果",
        "14.3 运行时稳态跟踪结果": "13.3 运行时稳态跟踪结果",
        "14.4 运行时完善方向": "13.5 运行时完善方向",
    }
    toc_changed = update_visible_toc(
        document_root,
        toc_replacements,
        remove_prefixes=(
            "十二、 OpenBlocks 障碍地图规划与多机执行",
            "12.1 单机 OpenBlocks 避障",
            "12.2 三机 OpenBlocks 可重构编队避障",
        ),
    )
    enable_field_refresh(settings_root)

    document_xml = etree.tostring(
        document_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    settings_xml = etree.tostring(
        settings_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    relationships_xml = etree.tostring(
        relationships_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    write_package(
        source,
        output,
        document_xml,
        settings_xml,
        relationships_xml,
        extra_entries,
    )

    final_root = etree.fromstring(document_xml)
    final_body = final_root.find("./w:body", namespaces=NS)
    final_paragraphs = direct_paragraphs(final_body)
    heading_count = sum(
        1 for paragraph in final_paragraphs
        if paragraph.find("./w:pPr/w:pStyle", namespaces=NS) is not None
        and paragraph.find("./w:pPr/w:pStyle", namespaces=NS).get(W + "val") in {"1", "2", "3"}
    )
    table_count = len(final_body.xpath("./w:tbl", namespaces=NS))
    print(f"output={output}")
    print(
        f"direct_paragraphs={len(final_paragraphs)} tables={table_count} "
        f"headings={heading_count} changed_paragraphs={changed_paragraphs} "
        f"applied_heading_updates={len(applied_heading_updates)} "
        f"toc_text_nodes_changed={toc_changed} captions_normalized={normalized_captions} "
        f"captions_from_markdown={markdown_captions} "
        f"synced_caption_segment_paragraphs={synced_caption_segment_paragraphs} "
        f"caption_segment_stats={caption_segment_stats}"
    )


if __name__ == "__main__":
    main()
