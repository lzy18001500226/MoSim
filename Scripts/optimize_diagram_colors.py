#!/usr/bin/env python3
"""
优化手绘图配色
将浅色背景的方框替换为更专业的配色方案
"""

from PIL import Image
import numpy as np
import sys
from pathlib import Path

def rgb_distance(c1, c2):
    """计算RGB颜色距离"""
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def replace_color_range(img_array, target_color, new_color, tolerance=30):
    """
    替换指定颜色范围

    Args:
        img_array: numpy array (H, W, 3 or 4)
        target_color: (R, G, B) 要替换的目标颜色
        new_color: (R, G, B) 新颜色
        tolerance: 容差范围
    """
    result = img_array.copy()

    # 处理RGB或RGBA
    if result.shape[2] == 4:
        rgb = result[:, :, :3]
        alpha = result[:, :, 3]
    else:
        rgb = result
        alpha = None

    # 计算每个像素与目标颜色的距离
    distances = np.sqrt(np.sum((rgb - np.array(target_color)) ** 2, axis=2))

    # 创建mask：距离小于tolerance的像素
    mask = distances < tolerance

    # 替换颜色
    rgb[mask] = new_color

    if alpha is not None:
        result[:, :, :3] = rgb
    else:
        result = rgb

    return result

def optimize_diagram_8(input_path, output_path):
    """
    优化图8：Profile Config + Controller Core + Adapter + Plant

    原配色：
    - 浅蓝色 (Profile Config)
    - 浅绿色 (Sysblock Controller Core)
    - 浅橙色 (Adapter)
    - 蓝色 (Plant)
    - 浅紫色 (Output Collection, Unified Evaluation Metrics)
    - 浅粉色 (Fault Injection)

    新配色（深色主题，专业感）：
    - Profile Config: #1E2761 (深蓝)
    - Controller Core: #2C5F2D (深绿)
    - Adapter: #B85042 (深橙/赭石)
    - Plant: #065A82 (深蓝绿)
    - Output/Metrics: #6D2E46 (深紫莓)
    - Fault Injection: #990011 (深红)
    """
    img = Image.open(input_path)
    img_array = np.array(img)

    # 定义颜色映射
    color_map = [
        # (原颜色近似RGB, 新颜色RGB, 容差, 描述)
        ((173, 216, 230), (30, 39, 97), 40, "Profile Config: 浅蓝 → 深蓝"),  # 浅蓝 → #1E2761
        ((144, 238, 144), (44, 95, 45), 40, "Controller Core: 浅绿 → 深绿"),  # 浅绿 → #2C5F2D
        ((255, 218, 185), (184, 80, 66), 40, "Adapter: 浅橙 → 赭石"),  # 浅橙 → #B85042
        ((135, 206, 250), (6, 90, 130), 35, "Plant: 蓝色 → 深蓝绿"),  # 蓝色 → #065A82
        ((221, 160, 221), (109, 46, 70), 40, "Output/Metrics: 浅紫 → 深紫莓"),  # 浅紫 → #6D2E46
        ((255, 182, 193), (153, 0, 17), 40, "Fault Injection: 浅粉 → 深红"),  # 浅粉 → #990011
    ]

    result = img_array.copy()

    for old_color, new_color, tolerance, desc in color_map:
        print(f"  替换: {desc}")
        result = replace_color_range(result, old_color, new_color, tolerance)

    # 保存
    Image.fromarray(result).save(output_path)
    print(f"✓ 已保存: {output_path}")

def optimize_diagram_9(input_path, output_path):
    """
    优化图9：七场景卡片墙
    原配色应该是多个浅色卡片，统一为深色卡片
    """
    img = Image.open(input_path)
    img_array = np.array(img)

    # 场景卡片配色（7+1个卡片，使用深色渐变）
    color_map = [
        # 假设原图有多种浅色背景
        ((255, 240, 245), (30, 39, 97), 40, "卡片1: 浅粉 → 深蓝"),  # #1E2761
        ((240, 248, 255), (44, 95, 45), 40, "卡片2: 浅蓝 → 深绿"),  # #2C5F2D
        ((255, 250, 240), (6, 90, 130), 40, "卡片3: 浅橙 → 深蓝绿"),  # #065A82
        ((245, 255, 250), (109, 46, 70), 40, "卡片4: 浅绿 → 深紫莓"),  # #6D2E46
        ((255, 245, 238), (184, 80, 66), 40, "卡片5: 浅橙 → 赭石"),  # #B85042
        ((248, 248, 255), (54, 69, 79), 40, "卡片6: 浅灰蓝 → 炭灰"),  # #36454F
        ((255, 253, 208), (153, 0, 17), 40, "卡片7: 浅黄 → 深红"),  # #990011
    ]

    result = img_array.copy()

    for old_color, new_color, tolerance, desc in color_map:
        print(f"  替换: {desc}")
        result = replace_color_range(result, old_color, new_color, tolerance)

    Image.fromarray(result).save(output_path)
    print(f"✓ 已保存: {output_path}")

def optimize_diagram_11(input_path, output_path):
    """
    优化图11：MWORKS实时外环与WSL2数据流
    """
    img = Image.open(input_path)
    img_array = np.array(img)

    color_map = [
        ((173, 216, 230), (30, 39, 97), 40, "MWORKS外环: 浅蓝 → 深蓝"),
        ((144, 238, 144), (44, 95, 45), 40, "WSL2: 浅绿 → 深绿"),
        ((255, 218, 185), (184, 80, 66), 40, "数据流: 浅橙 → 赭石"),
        ((221, 160, 221), (6, 90, 130), 40, "组件块: 浅紫 → 深蓝绿"),
    ]

    result = img_array.copy()

    for old_color, new_color, tolerance, desc in color_map:
        print(f"  替换: {desc}")
        result = replace_color_range(result, old_color, new_color, tolerance)

    Image.fromarray(result).save(output_path)
    print(f"✓ 已保存: {output_path}")

def optimize_diagram_15(input_path, output_path):
    """
    优化图15：Gazebo五类任务性能对比
    """
    img = Image.open(input_path)
    img_array = np.array(img)

    color_map = [
        ((173, 216, 230), (30, 39, 97), 40, "任务块1: 浅蓝 → 深蓝"),
        ((144, 238, 144), (44, 95, 45), 40, "任务块2: 浅绿 → 深绿"),
        ((255, 218, 185), (184, 80, 66), 40, "任务块3: 浅橙 → 赭石"),
        ((221, 160, 221), (6, 90, 130), 40, "任务块4: 浅紫 → 深蓝绿"),
        ((255, 182, 193), (109, 46, 70), 40, "任务块5: 浅粉 → 深紫莓"),
    ]

    result = img_array.copy()

    for old_color, new_color, tolerance, desc in color_map:
        print(f"  替换: {desc}")
        result = replace_color_range(result, old_color, new_color, tolerance)

    Image.fromarray(result).save(output_path)
    print(f"✓ 已保存: {output_path}")

def optimize_diagram_17(input_path, output_path):
    """
    优化图17：FUEL自主探索架构
    """
    img = Image.open(input_path)
    img_array = np.array(img)

    color_map = [
        ((173, 216, 230), (30, 39, 97), 40, "感知层: 浅蓝 → 深蓝"),
        ((144, 238, 144), (44, 95, 45), 40, "规划层: 浅绿 → 深绿"),
        ((255, 218, 185), (184, 80, 66), 40, "控制层: 浅橙 → 赭石"),
        ((221, 160, 221), (6, 90, 130), 40, "FUEL核心: 浅紫 → 深蓝绿"),
    ]

    result = img_array.copy()

    for old_color, new_color, tolerance, desc in color_map:
        print(f"  替换: {desc}")
        result = replace_color_range(result, old_color, new_color, tolerance)

    Image.fromarray(result).save(output_path)
    print(f"✓ 已保存: {output_path}")

def main():
    base_dir = Path(__file__).parent.parent / "Docs" / "报告" / "PPT" / "手绘图"

    diagrams = [
        (8, optimize_diagram_8),
        (9, optimize_diagram_9),
        (11, optimize_diagram_11),
        (15, optimize_diagram_15),
        (17, optimize_diagram_17),
    ]

    for num, optimize_func in diagrams:
        input_path = base_dir / f"{num}.png"
        output_path = base_dir / f"{num}.png"  # 覆盖原文件

        print(f"\n处理图{num}:")
        if not input_path.exists():
            print(f"  ✗ 文件不存在: {input_path}")
            continue

        optimize_func(str(input_path), str(output_path))

    print("\n✓ 所有图片配色优化完成")

if __name__ == "__main__":
    main()
