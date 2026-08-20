#!/usr/bin/env python3
"""
一键准备OpenBlocks动态仿真 - 规划、转MAT、准备就绪

这个脚本实现了你要求的"规划与仿真一起进行"：
1. 运行A*规划生成新的CSV轨迹
2. 转换CSV为MAT格式（MWORKS CombiTimeTable可直接读取）
3. 提示用户在Sysplorer中打开使用动态参考的模型

使用方法：
    python Scripts/planning/prepare_dynamic_simulation.py

然后在Sysplorer中：
    1. 打开提示的模型路径
    2. CheckModel（可选）
    3. SimulateModel - MAT文件会在仿真时自动加载最新规划结果
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANNING_SCRIPT = ROOT / "Scripts/planning/plan_open_blocks_three_uav.py"
MAT_EXPORT_SCRIPT = ROOT / "Scripts/planning/export_planning_to_mat.py"

# 动态参考模型路径（使用CombiTimeTable读MAT文件）
DYNAMIC_MODELS = {
    "px4ctrl_single": "Models/MoSimQuadrotorModel/Guidance/Planning/Sunray150PlanningOpenBlocksPx4CtrlSysblockDynamicClosedLoop.mo",
    "px4ctrl_three": "Models/MoSimQuadrotorModel/Guidance/Planning/Sunray150PlanningOpenBlocksPx4CtrlThreeUavDynamicClosedLoop.mo",
}


def run_step(description: str, command: list[str]) -> bool:
    """运行一个步骤，打印状态"""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"{'='*60}")

    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        print(f"\n❌ FAILED: {description}")
        return False

    print(f"\n✓ DONE: {description}")
    return True


def main():
    print("OpenBlocks动态仿真准备工具")
    print("=" * 60)
    print("功能：每次运行都重新规划，MAT文件在仿真时自动加载")
    print("不再需要手动更新.mo文件中的硬编码航点\n")

    # Step 1: 运行A*规划
    if not run_step(
        "A* 三机规划 (生成新CSV)",
        [sys.executable, str(PLANNING_SCRIPT)]
    ):
        return 1

    # Step 2: 转换为MAT格式
    if not run_step(
        "转换CSV为MAT格式 (MWORKS CombiTimeTable格式)",
        [sys.executable, str(MAT_EXPORT_SCRIPT)]
    ):
        return 1

    # Step 3: 提示用户下一步操作
    print("\n" + "=" * 60)
    print("✓ 准备完成！MAT文件已就绪")
    print("=" * 60)
    print("\n下一步在Sysplorer中操作：")
    print("\n【选项1】单机Px4Ctrl动态仿真：")
    print(f"  打开: {DYNAMIC_MODELS['px4ctrl_single']}")
    print("  运行: CheckModel → SimulateModel")
    print(f"  数据源: 自动从MAT文件读取UAV1轨迹")

    print("\n【选项2】三机Px4Ctrl动态仿真：")
    print(f"  打开: {DYNAMIC_MODELS['px4ctrl_three']}")
    print("  运行: CheckModel → SimulateModel")
    print(f"  数据源: 自动从MAT文件读取UAV1/UAV2/UAV3轨迹")

    print("\n注意：")
    print("- 动态参考模型使用CombiTimeTable，每次仿真时自动读取最新MAT文件")
    print("- 如需重新规划，直接再次运行本脚本即可")
    print("- MAT文件位置: Results/planning/three_uav_open_blocks_mworks_20260720/mat/")

    return 0


if __name__ == '__main__':
    sys.exit(main())
