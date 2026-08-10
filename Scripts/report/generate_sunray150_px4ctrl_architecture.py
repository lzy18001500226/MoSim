"""Render the report-side Sunray150 px4ctrl system relationship diagram.

This is a documentation asset derived from the current formal MWORKS chain:
Px4CtrlFormalRunner -> Px4CtrlAttitudeThrustAdapter ->
OfflineAttitudeRateAllocator -> Sunray150Assembly.  It intentionally does not
claim to be a screenshot of the legacy AWFF graphical architecture model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "Docs" / "报告" / "图" / "云纵150" / "架构图.png"
AIRFRAME_IMAGE = ROOT / "Docs" / "报告" / "图" / "云纵150" / "Sunray150-正.png"

WIDTH = 2560
HEIGHT = 1380

NAVY = "#16324F"
BLUE = "#2F6FB4"
BLUE_LIGHT = "#EAF3FF"
GREEN = "#267A5B"
GREEN_LIGHT = "#E9F7F0"
ORANGE = "#BB6A2D"
ORANGE_LIGHT = "#FFF2E7"
PURPLE = "#7851A9"
PURPLE_LIGHT = "#F4EEFC"
GRAY = "#5D6B78"
GRAY_LIGHT = "#F2F5F7"
LINE = "#91A3B5"
BACKGROUND = "#F8FAFC"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc")
        if bold
        else ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf")
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def center_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    left, top, right, bottom = box
    draw.multiline_text(
        ((left + right) / 2, (top + bottom) / 2),
        text,
        font=text_font,
        fill=fill,
        anchor="mm",
        align="center",
        spacing=7,
    )


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: str,
    outline: str,
    radius: int = 24,
    width: int = 4,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    *,
    fill: str = LINE,
    width: int = 8,
) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")
    x0, y0 = points[-2]
    x1, y1 = points[-1]
    size = 18
    if abs(x1 - x0) >= abs(y1 - y0):
        direction = 1 if x1 > x0 else -1
        triangle = [(x1, y1), (x1 - direction * size, y1 - size), (x1 - direction * size, y1 + size)]
    else:
        direction = 1 if y1 > y0 else -1
        triangle = [(x1, y1), (x1 - size, y1 - direction * size), (x1 + size, y1 - direction * size)]
    draw.polygon(triangle, fill=fill)


def bullet(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    *,
    fill: str = GRAY,
) -> None:
    x, y = origin
    draw.ellipse((x, y + 10, x + 10, y + 20), fill=fill)
    draw.text((x + 24, y), text, font=text_font, fill=fill)


def render(output: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    title_font = font(58, bold=True)
    subtitle_font = font(30)
    group_font = font(29, bold=True)
    block_title_font = font(38, bold=True)
    block_body_font = font(25)
    small_font = font(22)
    tag_font = font(24, bold=True)

    draw.rectangle((0, 0, WIDTH, 142), fill=NAVY)
    draw.text((86, 42), "Sunray150 px4ctrl 系统模型关系", font=title_font, fill="white")
    draw.text(
        (90, 105),
        "MWORKS FormalRunner 主线：参考轨迹、100 Hz 采样、px4ctrl、控制分配、机体与反馈闭环",
        font=subtitle_font,
        fill="#D9E7F5",
    )

    rounded_box(draw, (92, 200, 555, 778), fill=BLUE_LIGHT, outline=BLUE, radius=30)
    draw.text((132, 238), "任务与参考", font=group_font, fill=BLUE)
    rounded_box(draw, (136, 300, 510, 464), fill="white", outline=BLUE, radius=18, width=3)
    center_text(draw, (158, 318, 488, 436), "Trajectory\nClimbPath / 场景参考", block_title_font, NAVY)
    rounded_box(draw, (136, 548, 510, 702), fill="#F6FBFF", outline=BLUE, radius=18, width=3)
    center_text(draw, (158, 566, 488, 684), "100 Hz 采样边界\nposition / velocity / acceleration", block_body_font, NAVY)
    arrow(draw, [(323, 464), (323, 548)], fill=BLUE, width=6)

    rounded_box(draw, (694, 200, 1370, 778), fill=GREEN_LIGHT, outline=GREEN, radius=30)
    draw.text((736, 238), "px4ctrl 控制层", font=group_font, fill=GREEN)
    rounded_box(draw, (742, 300, 1322, 474), fill="white", outline=GREEN, radius=18, width=3)
    center_text(draw, (766, 318, 1298, 456), "Px4CtrlAttitudeThrust\nAdapter", block_title_font, GREEN)
    draw.text((792, 505), "原始图形外环", font=block_title_font, fill=NAVY)
    draw.text(
        (792, 555),
        "PX4CTRL_Original_OuterLoop_Graphical_Sysblock",
        font=block_body_font,
        fill=GRAY,
    )
    bullet(draw, (792, 620), "位置/速度参考 + 位置/速度反馈", small_font)
    bullet(draw, (792, 662), "输出：姿态参考 + 集体推力增量", small_font)
    bullet(draw, (792, 704), "当前整机闭环使用 Equation Bridge", small_font)

    rounded_box(draw, (1510, 310, 1892, 668), fill=ORANGE_LIGHT, outline=ORANGE, radius=30)
    draw.text((1552, 348), "控制分配", font=group_font, fill=ORANGE)
    rounded_box(draw, (1554, 412, 1848, 564), fill="white", outline=ORANGE, radius=18, width=3)
    center_text(draw, (1574, 428, 1828, 546), "OfflineAttitudeRate\nAllocator", block_title_font, ORANGE)
    center_text(draw, (1540, 588, 1862, 646), "ATTITUDE_THRUST → rotor_command[4]", small_font, NAVY)

    rounded_box(draw, (2002, 200, 2468, 778), fill=PURPLE_LIGHT, outline=PURPLE, radius=30)
    draw.text((2044, 238), "Sunray150 物理机体", font=group_font, fill=PURPLE)
    rounded_box(draw, (2050, 300, 2420, 620), fill="white", outline="#B89DD6", radius=18, width=3)
    if AIRFRAME_IMAGE.exists():
        airframe = Image.open(AIRFRAME_IMAGE).convert("RGBA")
        airframe.thumbnail((310, 280), Image.Resampling.LANCZOS)
        airframe_x = 2235 - airframe.width // 2
        airframe_y = 315 + (280 - airframe.height) // 2
        image.paste(airframe, (airframe_x, airframe_y), airframe)
    center_text(draw, (2070, 630, 2400, 672), "Sunray150Assembly", block_title_font, PURPLE)
    center_text(draw, (2070, 684, 2400, 744), "四旋翼执行器 + 机体动力学\n输出 position[3]、attitude[3]", small_font, NAVY)

    arrow(draw, [(555, 624), (624, 624), (624, 490), (694, 490)], fill=BLUE)
    draw.text((565, 575), "采样参考", font=small_font, fill=BLUE)
    arrow(draw, [(1370, 490), (1510, 490)], fill=GREEN)
    draw.text((1378, 446), "姿态参考 + 推力", font=small_font, fill=GREEN)
    arrow(draw, [(1892, 490), (2002, 490)], fill=ORANGE)
    draw.text((1890, 446), "四路旋翼命令", font=small_font, fill=ORANGE)

    rounded_box(draw, (680, 942, 1935, 1118), fill=GRAY_LIGHT, outline=GRAY, radius=28)
    draw.text((726, 976), "机体反馈与闭环边界", font=group_font, fill=NAVY)
    bullet(draw, (730, 1033), "position[3] 经采样后回送 px4ctrl 的 position_mea", block_body_font, fill=NAVY)
    bullet(draw, (730, 1072), "attitude[3] 同时进入 px4ctrl 与 OfflineAttitudeRateAllocator", block_body_font, fill=NAVY)
    arrow(draw, [(2235, 778), (2235, 1030), (1935, 1030)], fill=PURPLE, width=7)
    arrow(draw, [(680, 1030), (620, 1030), (620, 730), (694, 730)], fill=GRAY, width=7)
    draw.text((2000, 928), "position / attitude", font=small_font, fill=PURPLE)

    rounded_box(draw, (92, 1186, 2468, 1300), fill="#EEF4FA", outline="#C4D4E4", radius=20, width=2)
    draw.text((130, 1216), "图示依据", font=tag_font, fill=NAVY)
    draw.text(
        (130, 1260),
        "MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner；该图为当前 px4ctrl MWORKS 模型关系示意，不是旧 AWFF 图形模型截图。",
        font=small_font,
        fill=GRAY,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the px4ctrl Sunray150 report architecture diagram.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
