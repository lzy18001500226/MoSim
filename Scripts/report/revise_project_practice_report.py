#!/usr/bin/env python3
"""Revise the course-practice report from the current full report source.

This is a bounded content migration helper. It keeps the course report's
existing figures, tables, numbering, and section structure, while importing
tagged equations from the full report at the matching implementation topics
and expanding figure/table analysis paragraphs.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "Docs" / "课设" / "项目综合实践III_正文.md"
FULL = ROOT / "Docs" / "报告" / "草稿" / "仿真分析报告_正文骨架.md"

FENCE_RE = re.compile(r"```latex\s*\r?\n(.*?)\r?\n```", re.S)
TAG_RE = re.compile(r"\\tag\{(?P<tag>\d+-\d+[a-z]?)\}")
IMAGE_RE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
CAPTION_RE = re.compile(r"^图\s*\d+-\d+[　 \t]+(?P<title>.+?)\s*[。.]?$")
GENERATED_FORMULA_HEADING_RE = re.compile(
    r"^(?:### 5\.3\.(?:4|10|11|12|13|14) 公式、变量与实现边界|"
    r"#### .+?的公式与变量说明|"
    r"#### px4ctrl 图形化全机基线的公式与变量说明)\s*$"
)
GENERATED_ANALYSIS_MARKERS = (
    "单张图不替代模型检查、有效结果或运行时证据",
    "这能说明图形模型组织和接口关系，但不能由连线本身推出",
    "该统计图用于比较题注所限定的同一任务、同一指标和有效样本",
    "应把误差峰值对应的时间窗与同组轨迹、速度和控制输入对照",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def formula_tag(block: str) -> str:
    match = TAG_RE.search(block)
    if not match:
        raise ValueError("Formula block has no tagged equation number")
    return match.group("tag")


def _is_context_boundary(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or stripped.startswith(("#", "!", "|", "```", "~~~"))
        or stripped.startswith(("图 ", "图　", "表 ", "表　"))
    )


def _neighbor_paragraph(lines: list[str], index: int, direction: int) -> str:
    cursor = index + direction
    while 0 <= cursor < len(lines) and not lines[cursor].strip():
        cursor += direction
    if not 0 <= cursor < len(lines) or _is_context_boundary(lines[cursor]):
        return ""

    if direction < 0:
        end = cursor
        while cursor >= 0 and not _is_context_boundary(lines[cursor]):
            cursor -= 1
        return "\n".join(lines[cursor + 1 : end + 1]).strip()

    start = cursor
    while cursor < len(lines) and not _is_context_boundary(lines[cursor]):
        cursor += 1
    return "\n".join(lines[start:cursor]).strip()


def extract_formula_records(text: str) -> list[tuple[str, str, str, str]]:
    lines = text.splitlines()
    records: list[tuple[str, str, str, str]] = []
    for match in FENCE_RE.finditer(text):
        block = match.group(1).strip()
        start_line = text[: match.start()].count("\n")
        end_line = text[: match.end()].count("\n") - 1
        records.append(
            (
                formula_tag(block),
                f"```latex\n{block}\n```",
                _neighbor_paragraph(lines, start_line, -1),
                _neighbor_paragraph(lines, end_line, 1),
            )
        )
    return records


def extract_formulas(text: str) -> list[tuple[str, str]]:
    return [(tag, block) for tag, block, _before, _after in extract_formula_records(text)]


def strip_generated_formula_content(text: str) -> str:
    """Remove this helper's prior formula insertion so reruns are idempotent."""
    generated_block = re.compile(
        r"^式\((?P<tag>\d+-\d+[a-z]?)\)是[^\n]*\n\n"
        r"^```latex\n.*?^```\n\n"
        r"^式\((?P=tag)\)中的参数应回到同次 Profile、源码或实验记录核对；.*?\n?",
        re.M | re.S,
    )
    text = generated_block.sub("", text)
    text = re.sub(
        r"^" + GENERATED_FORMULA_HEADING_RE.pattern + r"\n?",
        "",
        text,
        flags=re.M,
    )
    return re.sub(r"\n{3,}", "\n\n", text)


def source_chapter(tag: str) -> int:
    return int(tag.split("-", 1)[0])


def route_formula_groups(full: str) -> dict[str, list[tuple[str, str, str, str]]]:
    lines = full.splitlines()
    groups: dict[str, list[tuple[str, str]]] = {}
    current_route: str | None = None
    current: list[str] = []

    def flush() -> None:
        nonlocal current_route, current
        if current_route is not None:
            groups[current_route] = extract_formula_records("\n".join(current))
        current_route = None
        current = []

    for line in lines:
        heading = re.match(r"^####\s+(.+?)\s*$", line)
        if heading:
            flush()
            current_route = heading.group(1).strip().split("（", 1)[0].strip()
            continue
        if current_route is not None:
            current.append(line)
    flush()
    return {key: value for key, value in groups.items() if value}


def prose_for_formula(tag: str, topic: str) -> str:
    return (
        f"式({tag})是{topic}在本报告中的核心计算关系。先明确它的输入、状态量和输出量，"
        "再沿公式右侧到左侧的计算顺序理解各个支路；向量表示同一坐标系下的多轴量，"
        "带下标 k 的量表示离散采样点，带点号的量表示连续时间导数，sat 表示工程限幅。"
        f"在实现上，式({tag})的输出还要经过统一 Adapter、执行器动态和公共 Plant，"
        "因此它说明算法如何产生控制量，不单独证明某次仿真已经通过性能判据。"
    )


def render_formula_group(
    records: list[tuple[str, str, str, str]], topic: str
) -> str:
    chunks: list[str] = []
    for tag, block, before, after in records:
        if before:
            chunks.append(before)
        else:
            chunks.append(prose_for_formula(tag, topic))
        chunks.append(block)
        if after:
            chunks.append(after)
        chunks.append(
            f"变量与边界说明：式({tag})中的粗体量按本节坐标系表示向量或矩阵；"
            "若出现下标 k，则表示离散采样点，具体增益、时间常数、质量、惯量、限幅和采样周期"
            "以本段给出的 Profile、源码或同次实验记录为准。该式说明实现结构，不能单独把局部图形或数值"
            "升级为全链路性能结论。"
        )
    return "\n\n".join(chunks)


def replace_formula_fences(text: str) -> str:
    return FENCE_RE.sub("", text)


def insert_before(text: str, anchor: str, payload: str) -> str:
    if payload.strip() in text:
        return text
    index = text.find(anchor)
    if index < 0:
        raise ValueError(f"Anchor not found: {anchor}")
    return text[:index] + payload.rstrip() + "\n\n" + text[index:]


def family_for_route(route: str) -> str:
    route = route.lower()
    if route in {"official pid", "official_pid"}:
        return "工程基线"
    if route == "px4ctrl":
        return "图形化全机基线"
    if any(key in route for key in ("pid", "awff", "eso", "fopid")):
        return "PID 与扰动补偿族"
    if any(key in route for key in ("lqr", "lqi", "lqg", "h2", "hinf", "pole")):
        return "线性与鲁棒状态反馈族"
    if any(key in route for key in ("backstepping", "linearization", "passivity", "mrac", "ndi")):
        return "非线性与自适应族"
    if "smc" in route:
        return "滑模控制族"
    if any(key in route for key in ("mpc", "ilqr", "mppi", "nmpc")):
        return "预测与优化族"
    if any(key in route for key in ("se3", "dfbc")):
        return "几何与微分平坦族"
    if any(key in route for key in ("rl", "neural")):
        return "学习控制族"
    return "统一控制器路线"


def route_analysis(title: str) -> str:
    route = title.replace("控制器图形模型", "").strip()
    family = family_for_route(route)
    return (
        f"该图把 {route} 的输入、核心计算支路、限幅/补偿环节和输出端口放在同一张图中，"
        f"可沿信号方向核对它属于{family}并最终落到哪一种统一输出边界。"
        "阅读时应重点检查误差或参考量是否进入主控制支路、增强项是否在输出前汇合，以及输出是否经过公共 Adapter；"
        "这能说明图形模型组织和接口关系，但不能由连线本身推出闭环稳定性、跟踪精度或运行时部署成功。"
    )


def add_analysis(title: str, existing: str) -> str:
    lower = title.lower()
    if "控制器图形模型" in title:
        return route_analysis(title)
    if "姿态角" in title:
        return (
            f"{existing.rstrip('。')}。图中的滚转、俯仰和偏航通道应与同一记录的水平/三维轨迹、位置误差、"
            "速度分量和四路控制输入按时间对齐阅读：姿态峰值通常对应轨迹转弯、爬升或误差快速变化的窗口。"
            "该图描述姿态响应形态，不能单独证明控制器性能或姿态安全裕度已经通过。"
        )
    if "位置误差" in title or "误差" in title:
        return (
            f"{existing.rstrip('。')}。应把误差峰值对应的时间窗与同组轨迹、速度和控制输入对照，区分起步/转弯瞬态、"
            "稳态偏差和持续发散三种形态；末端数值还需回到有效性状态和指标文件核对。"
        )
    if "控制输入" in title or "控制能量" in title:
        return (
            f"{existing.rstrip('。')}。同时观察四路输入是否同步变化、是否出现持续限幅或高频切换，并与姿态和误差曲线的"
            "同一时间段互证；这里的控制量/控制能量是执行器命令层指标，不等同于电池能耗或独立的鲁棒性证明。"
        )
    if "高度" in title or "高度通道" in title:
        return (
            f"{existing.rstrip('。')}。应将 Z 通道的爬升、超调、回落和稳态段与水平面轨迹及位置误差共同解读，"
            "因为总位置误差可能由垂向通道主导，也可能由水平转弯造成；图中趋势仍需由同次指标记录确认。"
        )
    if "速度" in title:
        return (
            f"{existing.rstrip('。')}。速度峰值的位置应与参考轨迹变化率、位置误差峰值和控制输入过渡相对应；"
            "若末段速度没有回到参考变化率附近，位置误差的累积会在后续时程中放大。"
        )
    if "水平面轨迹" in title or "三维轨迹" in title or "轨迹" in title:
        return (
            f"{existing.rstrip('。')}。实际轨迹与参考轨迹的重合程度应结合误差时程、速度变化和姿态动作判断，"
            "不能只凭二维投影或视图缩放把局部遮挡误认为精确跟踪；图件也不替代原始结果和统一门限。"
        )
    if "雷达" in title or "箱线" in title or "直方" in title or "排名" in title or "达标" in title:
        return (
            f"{existing.rstrip('。')}。该统计图用于比较题注所限定的同一任务、同一指标和有效样本，"
            "应同时查看样本数、失败/超时记录和指标定义；分布差异是当前记录的比较结果，不是对未运行路线或其他场景的外推。"
        )
    if "界面" in title or "Studio" in title or "助手" in title or "工具链" in title or "数据流" in title:
        return (
            f"{existing.rstrip('。')}。图中可核对入口、数据流或显示职责是否与正文描述一致，"
            "但界面状态和截图只属于操作/结构证据，正式仿真、运行时生命周期和性能结论仍以同次记录为准。"
        )
    return (
        f"{existing.rstrip('。')}。该图应与同组的输入、状态和结果记录一起阅读，先确认图中对象和数据来源，"
        "再判断它能支持的结论范围；单张图不替代模型检查、有效结果或运行时证据。"
    )


def expand_figure_analysis(text: str) -> str:
    lines = text.splitlines()
    output = list(lines)
    for index, line in enumerate(lines):
        image = IMAGE_RE.match(line.strip())
        if not image:
            continue
        caption_index = index + 1
        while caption_index < len(lines) and not lines[caption_index].strip():
            caption_index += 1
        if caption_index >= len(lines) or not CAPTION_RE.match(lines[caption_index].strip()):
            continue
        analysis_index = caption_index + 1
        while analysis_index < len(lines) and not lines[analysis_index].strip():
            analysis_index += 1
        if analysis_index >= len(lines):
            continue
        analysis = lines[analysis_index].strip()
        if analysis.startswith(("#", "!", "```", "|")):
            continue
        if any(marker in analysis for marker in GENERATED_ANALYSIS_MARKERS):
            continue
        title = CAPTION_RE.match(lines[caption_index].strip()).group("title")
        output[analysis_index] = add_analysis(title, analysis)
    return "\n".join(output)


def expand_table_analysis(text: str) -> str:
    lines = text.splitlines()
    output = list(lines)
    table_titles = {
        "功能性需求": "表 3-1 将系统目标、实现入口和验收证据放在同一行中，读者可以沿每一行从需求追到证据，而不是把功能按钮本身当成验收结果。表中尤其区分了配置、模型检查、正式仿真、代码交付和运行时记录的责任边界，因此后文的结论应按证据类型回读。",
        "非功能性需求": "表 3-2 的重点是把质量属性转换为可检查的工程措施，并同时保留当前边界。可追溯性、可复现性和性能可测量性依赖配置、原始结果和指标的共同存在，不能由界面可用性或单次截图代替。",
        "代表性结果": "表 5-1 汇总的是同一任务和指标口径下的代表性记录，前三项是有效 A/B 对比，后三项是 MWORKS 内 SIL 差异。它把性能比较、代码等价性和运行时事实分开，读者不能把任一行单独外推为全部控制器或 Gazebo/PX4 性能通过。",
        "测试环境": "表 6-1 把正式模型、独立运行时、后处理和显示辅助环境分开列出，并为每一类指定权威输出。这样的分层避免用 TyPlot 图或 Studio 窗口替代 MWORKS 结果，也避免把 ROS 记录反向写成所有模型路线的结论。",
        "设计测试用例": "表 6-2 按测试对象列出预期结果和证据类型，覆盖静态检查、配置、正式仿真、SIL、构建和运行时。用例通过只表示该用例的证据成立，仍需结合失败分类和适用范围解释总体结论。",
        "测试用例执行": "表 6-3 既保留通过数量，也保留无效和阻塞数量，因而能看出项目当前完成度而不是只看成功记录。尤其是电机故障注入和运行时记录只证明同次动作与生命周期事实，不能直接替换抗扰或容错性能试验。",
        "缺陷修复": "表 6-4 将风险、处置和复核证据对应起来，说明修复是否落到代码、配置、构建或结果分类层。后续维护时应沿证据列复查，而不是只依据修复描述判断缺陷已经关闭。",
        "人员与沟通管理": "表 7-1 记录每位成员的任务边界和答辩职责，贡献比例保留为提交前按实际情况填写。分工表用于说明协作责任，不等同于对某个运行结果的个人性能背书。",
        "进度管理": "表 7-2 按需求、模型接口、实验、代码运行时和质量交付排列阶段输出，体现项目从设计到证据的依赖顺序。后续补实验时，应优先补齐阶段输出和结果清单，而不是只更新叙述。",
        "风险管理": "表 7-3 将高风险状态与处置动作绑定，尤其强调授权、超时、路径漂移和证据误读等会阻止强结论的情况。风险项的存在不代表项目失败，而是要求报告保留边界并在条件满足后重新验证。",
        "软件维护": "表 8-1 按改正性、适应性、完善性和预防性维护组织后续工作，既覆盖代码和接口，也覆盖配置、结果归档和证据分类。维护方向的优先级应以尚未形成完整结果的实验和运行时边界为依据。",
    }
    for index, line in enumerate(lines):
        match = re.match(r"^表\s*\d+-\d+[　 \t]+(?P<title>.+?)\s*$", line.strip())
        if not match:
            continue
        title = match.group("title").rstrip("。.")
        analysis_index = index + 1
        while analysis_index < len(lines) and not lines[analysis_index].strip():
            analysis_index += 1
        if analysis_index < len(lines) and lines[analysis_index].startswith("|"):
            analysis_index += 1
            while analysis_index < len(lines) and (lines[analysis_index].startswith("|") or not lines[analysis_index].strip()):
                analysis_index += 1
        if analysis_index >= len(lines):
            continue
        if lines[analysis_index].startswith("表中的对应关系") and title in table_titles:
            output[analysis_index] = table_titles[title]
    return "\n".join(output)


def main() -> None:
    course = read(COURSE)
    full = read(FULL)
    full_formulas = extract_formulas(full)
    if len(full_formulas) < 100:
        raise ValueError(f"Unexpected full-report formula count: {len(full_formulas)}")
    groups = route_formula_groups(full)

    course = replace_formula_fences(course)
    course = expand_figure_analysis(course)
    course = expand_table_analysis(course)

    chapter_groups: dict[int, list[tuple[str, str]]] = {}
    for tag, block in full_formulas:
        chapter_groups.setdefault(source_chapter(tag), []).append((tag, block))

    # General equations are placed at the corresponding system boundary.
    anchors = [
        (2, "### 5.2.1 统一任务配置示例", "场景、指标与有效性判定"),
        (3, "### 5.3 48 条控制器路线的统一实现", "云纵150机体、坐标与公共动力学"),
        (4, "#### 5.1.1 统一输出边界", "统一输出边界与采样语义"),
        (10, "![图 5-329 三机 Figure8 场景与规划轨迹]", "三机编队与安全参考调节"),
        (11, "![图 5-332 FAST-LIO 局部地图与点云状态]", "感知与规划组件"),
        (12, "![图 5-333 单机 OpenBlocks 水平面轨迹]", "OpenBlocks 障碍地图与多机执行"),
        (13, "## 6. 软件测试", "代码生成与 SIL 一致性"),
        (14, "## 6. 软件测试", "ROS1/Gazebo 运行时闭环"),
    ]
    for chapter, anchor, topic in anchors:
        payload = f"### 5.3.{chapter} 公式、变量与实现边界\n\n"
        payload += render_formula_group(chapter_groups.get(chapter, []), topic)
        course = insert_before(course, anchor, payload)

    # Route-specific formula blocks remain adjacent to their graph and route.
    for route, records in groups.items():
        if route not in course:
            continue
        if route in {"official_pid", "official_pid_yaw_authority_mapped"}:
            continue
        caption_pattern = re.compile(
            rf"^!\[.*?{re.escape(route)}.*?控制器图形模型.*?\]\\(" if False else "x"
        )
        # Find the image whose following caption names the route.
        lines = course.splitlines()
        image_anchor = None
        for idx, line in enumerate(lines):
            if not line.startswith("!["):
                continue
            j = idx + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and route in lines[j] and "控制器图形模型" in lines[j]:
                image_anchor = line
                break
        if image_anchor is None:
            continue
        payload = f"#### {route} 的公式与变量说明\n\n"
        payload += render_formula_group(records, f"{route}（{family_for_route(route)}）")
        course = insert_before(course, image_anchor, payload)

    # Official PID and px4ctrl have source sections with names that differ
    # from the course captions, so bind their groups explicitly.
    for anchor, records, topic in [
        ("![图 5-10 Official PID 控制器图形模型]", groups.get("official_pid", []), "Official PID 工程基线"),
        ("![图 5-57 px4ctrl 控制器图形模型]", chapter_groups.get(8, []), "px4ctrl 图形化全机基线"),
    ]:
        if records:
            payload = f"#### {topic}的公式与变量说明\n\n" + render_formula_group(records, topic)
            course = insert_before(course, anchor, payload)

    # Remove temporary placeholder comments after all equation groups are in.
    course = re.sub(r"\n?<!-- 公式回填：.*?-->\n?", "\n", course)
    write(COURSE, course)
    print(f"full_formula_count={len(full_formulas)}")
    print(f"route_formula_groups={len(groups)}")
    print(f"course_bytes={COURSE.stat().st_size}")


if __name__ == "__main__":
    main()
