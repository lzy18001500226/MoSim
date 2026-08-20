from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree


BASE = Path(__file__).resolve().parents[1]
INPUT_DOCX = BASE / "MoSim_仿真分析报告_重构对齐版_补图修复.docx"
OUTPUT_DOCX = BASE / "MoSim_仿真分析报告_重构对齐版_补图修复_px4ctrl.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def q(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.itertext()).replace("\n", " ").strip()


def set_paragraph_text(paragraph: etree._Element, text: str) -> None:
    ppr = paragraph.find(q(W_NS, "pPr"))
    template_run = paragraph.find(q(W_NS, "r"))
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    if template_run is None:
        template_run = etree.Element(q(W_NS, "r"))
    else:
        template_run = copy.deepcopy(template_run)
        for node in list(template_run.findall(f".//{q(W_NS, 't')}")):
            parent = node.getparent()
            parent.remove(node)
    run_text = etree.SubElement(template_run, q(W_NS, "t"))
    run_text.set(q(XML_NS, "space"), "preserve")
    run_text.text = text
    paragraph.append(template_run)


def refresh_paragraph_ids(paragraph: etree._Element, next_id: int) -> int:
    paragraph.set(q(W14_NS, "paraId"), f"{next_id:08X}")
    paragraph.set(q(W14_NS, "textId"), f"{next_id + 1:08X}")
    return next_id + 2


def refresh_picture_ids(paragraph: etree._Element, next_id: int) -> int:
    for node in paragraph.iter():
        local = etree.QName(node).localname
        if local in {"docPr", "cNvPr"} and "id" in node.attrib:
            node.set("id", str(next_id))
            next_id += 1
    return next_id


def set_caption(paragraph: etree._Element, number: int, description: str) -> None:
    instruction = paragraph.find(f".//{q(W_NS, 'instrText')}")
    if instruction is None:
        raise ValueError("caption does not contain a SEQ field")
    instruction.text = f" SEQ Figure \\r {number} \\* ARABIC "

    after_instruction = False
    cached_number = None
    for node in paragraph.iter():
        if node is instruction:
            after_instruction = True
            continue
        if after_instruction and node.tag == q(W_NS, "t"):
            cached_number = node
            break
    if cached_number is None:
        raise ValueError("caption SEQ field has no cached result")
    cached_number.text = str(number)

    end_run = None
    for run in paragraph.findall(q(W_NS, "r")):
        for field_char in run.findall(q(W_NS, "fldChar")):
            if field_char.get(q(W_NS, "fldCharType")) == "end":
                end_run = run
                break
        if end_run is not None:
            break
    if end_run is None:
        raise ValueError("caption SEQ field has no end marker")

    children = list(paragraph)
    end_index = children.index(end_run)
    description_template = next(
        (copy.deepcopy(child) for child in children[end_index + 1:] if child.tag == q(W_NS, "r")),
        copy.deepcopy(end_run),
    )
    for node in list(description_template.findall(f".//{q(W_NS, 't')}")):
        node.getparent().remove(node)
    description_text = etree.SubElement(description_template, q(W_NS, "t"))
    description_text.set(q(XML_NS, "space"), "preserve")
    description_text.text = f" {description}"
    for child in children[end_index + 1:]:
        paragraph.remove(child)
    paragraph.append(description_template)


def next_hex_id(root: etree._Element, local_name: str) -> int:
    values = []
    for node in root.iter():
        for attribute, value in node.attrib.items():
            if etree.QName(attribute).localname == local_name:
                try:
                    values.append(int(value, 16))
                except ValueError:
                    pass
    return (max(values) + 1) if values else 1


def main() -> None:
    if OUTPUT_DOCX.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {OUTPUT_DOCX}")

    source_images = {
        "core": BASE / "图" / "控制器" / "PX4Ctrl" / "core.png",
        "mapper": BASE / "图" / "控制器" / "PX4Ctrl" / "mapper.png",
        "single": BASE / "图" / "控制器" / "PX4Ctrl" / "单机.png",
    }
    for path in source_images.values():
        if not path.is_file():
            raise FileNotFoundError(path)

    parser = etree.XMLParser(remove_blank_text=False)
    with zipfile.ZipFile(INPUT_DOCX, "r") as zin:
        document_root = etree.fromstring(zin.read("word/document.xml"), parser)
        rels_root = etree.fromstring(zin.read("word/_rels/document.xml.rels"), parser)
        body = document_root.find(q(W_NS, "body"))
        if body is None:
            raise ValueError("document.xml has no w:body")

        caption_8_1 = next(
            p for p in body if p.tag == q(W_NS, "p") and "px4ctrl图形化位置/速度外环模型结构" in paragraph_text(p)
        )
        image_8_1 = list(body)[list(body).index(caption_8_1) - 1]
        if image_8_1.tag != q(W_NS, "p") or image_8_1.find(f".//{q(A_NS, 'blip')}") is None:
            raise ValueError("could not locate existing figure 8-1 image paragraph")
        preceding = list(body)[list(body).index(image_8_1) - 1]

        caption_8_4 = next(
            p for p in body if p.tag == q(W_NS, "p") and "控制算法家族技术路线总览与px4ctrl外环定位" in paragraph_text(p)
        )
        image_template = copy.deepcopy(image_8_1)
        caption_template = copy.deepcopy(caption_8_1)
        text_template = copy.deepcopy(preceding)

        set_paragraph_text(
            preceding,
            "上述外环在 Modelica 侧的图形模型结构按三个层次展示：控制核心实现位置/速度误差到期望姿态/推力的转换，映射器完成坐标变换与信号桥接，单机整体模型组织完整的闭环链路。",
        )

        relationships = list(rels_root)
        relationship_template = next(iter(relationships))
        existing_relationship_numbers = [
            int(element.get("Id")[3:])
            for element in rels_root
            if element.get("Id", "").startswith("rId") and element.get("Id")[3:].isdigit()
        ]
        next_relationship_number = max(existing_relationship_numbers, default=0) + 1
        relationship_ids = [
            (f"rId{next_relationship_number}", "media/image490.png"),
            (f"rId{next_relationship_number + 1}", "media/image491.png"),
            (f"rId{next_relationship_number + 2}", "media/image492.png"),
        ]
        for relationship_id, target in relationship_ids:
            relationship = copy.deepcopy(relationship_template)
            relationship.set("Id", relationship_id)
            relationship.set("Target", target)
            rels_root.append(relationship)

        blip_8_1 = image_8_1.find(f".//{q(A_NS, 'blip')}")
        blip_8_1.set(q(R_NS, "embed"), relationship_ids[0][0])
        set_caption(caption_8_1, 1, "px4ctrl 控制核心 Sysblock 图形化模型")

        next_para_id = next_hex_id(document_root, "paraId")
        next_picture_id = next_hex_id(document_root, "id")
        next_para_id = refresh_paragraph_ids(caption_8_1, next_para_id)

        def new_text(text: str) -> etree._Element:
            nonlocal next_para_id
            paragraph = copy.deepcopy(text_template)
            set_paragraph_text(paragraph, text)
            next_para_id = refresh_paragraph_ids(paragraph, next_para_id)
            return paragraph

        def new_image(relationship_id: str) -> etree._Element:
            nonlocal next_para_id, next_picture_id
            paragraph = copy.deepcopy(image_template)
            blip = paragraph.find(f".//{q(A_NS, 'blip')}")
            blip.set(q(R_NS, "embed"), relationship_id)
            next_para_id = refresh_paragraph_ids(paragraph, next_para_id)
            next_picture_id = refresh_picture_ids(paragraph, next_picture_id)
            return paragraph

        def new_caption(number: int, description: str) -> etree._Element:
            nonlocal next_para_id
            paragraph = copy.deepcopy(caption_template)
            set_caption(paragraph, number, description)
            next_para_id = refresh_paragraph_ids(paragraph, next_para_id)
            return paragraph

        insert_at = list(body).index(caption_8_1) + 1
        additions = [
            new_text("映射器层：控制核心输出的姿态指令与推力指令需经过映射器转换为统一的 ATTITUDE_THRUST 边界格式。下图展示四元数转换、角度归一化和推力缩放等工程细节。"),
            new_image(relationship_ids[1][0]),
            new_caption(2, "px4ctrl 映射器信号桥接结构"),
            new_text("单机整体模型：完整的 px4ctrl 单机模型将控制核心、映射器与公共姿态环、Plant 组织在统一的 Modelica 顶层模型中。下图展示从轨迹参考输入、经控制器计算到执行器输出的完整闭环链路。"),
            new_image(relationship_ids[2][0]),
            new_caption(3, "px4ctrl 单机整体模型闭环结构"),
        ]
        for addition in additions:
            body.insert(insert_at, addition)
            insert_at += 1

        set_caption(caption_8_4, 4, "控制算法家族技术路线总览与 px4ctrl 外环定位")

        document_bytes = etree.tostring(document_root, xml_declaration=True, encoding="UTF-8", standalone="yes")
        rels_bytes = etree.tostring(rels_root, xml_declaration=True, encoding="UTF-8", standalone="yes")

        with zipfile.ZipFile(OUTPUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                if info.filename == "word/document.xml":
                    zout.writestr(info, document_bytes)
                elif info.filename == "word/_rels/document.xml.rels":
                    zout.writestr(info, rels_bytes)
                else:
                    zout.writestr(info, zin.read(info.filename))
            for name, path in zip(
                ("word/media/image490.png", "word/media/image491.png", "word/media/image492.png"),
                (source_images["core"], source_images["mapper"], source_images["single"]),
            ):
                zout.writestr(name, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)

    result = {
        "output": str(OUTPUT_DOCX),
        "input": str(INPUT_DOCX),
        "inserted": [
            {"figure": "图8-1", "source": str(source_images["core"]), "relationship": relationship_ids[0][0]},
            {"figure": "图8-2", "source": str(source_images["mapper"]), "relationship": relationship_ids[1][0]},
            {"figure": "图8-3", "source": str(source_images["single"]), "relationship": relationship_ids[2][0]},
        ],
        "preserved": "图8-4 算法家族技术路线总览",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
