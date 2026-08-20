#!/usr/bin/env python3
"""Keep inline figures, their captions, and the following analysis together."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def qn(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def paragraph_text(paragraph) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS)).strip()


def set_keep_with_next(paragraph) -> None:
    properties = paragraph.find(qn("pPr"))
    if properties is None:
        properties = etree.Element(qn("pPr"))
        paragraph.insert(0, properties)
    if properties.find(qn("keepNext")) is None:
        properties.append(etree.Element(qn("keepNext")))


def clear_keep_with_next(paragraph) -> None:
    properties = paragraph.find(qn("pPr"))
    if properties is None:
        return
    keep_next = properties.find(qn("keepNext"))
    if keep_next is not None:
        properties.remove(keep_next)


def bind_context(document_xml: bytes) -> tuple[bytes, int]:
    root = etree.fromstring(document_xml)
    body = root.find(".//w:body", namespaces=NS)
    if body is None:
        raise ValueError("word/document.xml has no body")
    children = list(body)
    figures = 0
    for index, child in enumerate(children):
        if child.tag != qn("p") or not child.xpath(".//w:drawing", namespaces=NS):
            continue
        if index + 1 >= len(children):
            raise ValueError(f"Figure paragraph {index + 1} has no caption paragraph")
        caption = children[index + 1]
        caption_text = paragraph_text(caption)
        if caption.tag != qn("p") or not caption_text.startswith("图"):
            raise ValueError(
                f"Figure paragraph {index + 1} is not followed by a figure caption: {caption_text!r}"
            )
        set_keep_with_next(child)
        clear_keep_with_next(caption)
        if index:
            lead_in = children[index - 1]
            if lead_in.tag == qn("p") and paragraph_text(lead_in):
                set_keep_with_next(lead_in)
        figures += 1
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True), figures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    target = args.docx.resolve()
    if not target.is_file():
        raise FileNotFoundError(target)

    with zipfile.ZipFile(target, "r") as source:
        document_xml, figures = bind_context(source.read("word/document.xml"))
        with tempfile.NamedTemporaryFile(delete=False, dir=target.parent, suffix=".docx") as handle:
            temporary = Path(handle.name)
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as output:
            for item in source.infolist():
                data = document_xml if item.filename == "word/document.xml" else source.read(item.filename)
                output.writestr(item, data)
    try:
        shutil.copystat(target, temporary)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)

    print(f"Bound {figures} inline figure-caption-analysis groups in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
