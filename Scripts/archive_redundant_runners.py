#!/usr/bin/env python3
"""
归档冗余的 Runner 文件和目录
移动到 E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners/
"""
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
ARCHIVE_DIR = Path('E:/刘致远18001500226/MoSim_Archive/legacy_experiment_runners')
EXPERIMENT_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Experiment'

# 创建归档目录
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("MoSim Runner 冗余文件归档")
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# 归档计数
archived_dirs = 0
archived_files = 0

# 1. 归档重复的家族目录
redundant_dirs = [
    'LinearRobustStateFeedback',
    'NonlinearAdaptive',
    'OptimizationPredictive'
]

print("\n[1] 归档重复的家族目录")
print("-"*80)
for dirname in redundant_dirs:
    src = EXPERIMENT_DIR / dirname
    if src.exists():
        dst = ARCHIVE_DIR / dirname
        try:
            shutil.move(str(src), str(dst))
            runner_count = len(list(dst.rglob('*Runner.mo')))
            print(f"[OK] {dirname:30s} -> 归档 ({runner_count} 个 Runner)")
            archived_dirs += 1
        except Exception as e:
            print(f"[ERROR] {dirname}: {e}")
    else:
        print(f"[SKIP] {dirname}: 不存在")

# 2. 归档 PidFamily 冗余文件
print("\n[2] 归档 PidFamily 冗余文件")
print("-"*80)
pidfamily_redundant = [
    'OfficialPidGraphicalRunner.mo',
    'OfficialPidFamilyRunner.mo',
    'FopidGraphicalRunner.mo'
]

pidfamily_dir = EXPERIMENT_DIR / 'PidFamily'
for filename in pidfamily_redundant:
    src = pidfamily_dir / filename
    if src.exists():
        dst = ARCHIVE_DIR / 'PidFamily_redundant' / filename
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dst))
            print(f"[OK] PidFamily/{filename}")
            archived_files += 1
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
    else:
        print(f"[SKIP] {filename}: 不存在")

# 3. 归档 AwffControllers 冗余文件
print("\n[3] 归档 AwffControllers 冗余文件")
print("-"*80)
awff_redundant = ['AwffPidGraphicalRunner.mo']

awff_dir = EXPERIMENT_DIR / 'AwffControllers'
for filename in awff_redundant:
    src = awff_dir / filename
    if src.exists():
        dst = ARCHIVE_DIR / 'AwffControllers_redundant' / filename
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dst))
            print(f"[OK] AwffControllers/{filename}")
            archived_files += 1
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
    else:
        print(f"[SKIP] {filename}: 不存在")

# 4. 归档 Templates/Official
print("\n[4] 归档 Templates/Official")
print("-"*80)
templates_official = EXPERIMENT_DIR / 'Templates/Official'
if templates_official.exists():
    dst = ARCHIVE_DIR / 'Templates_Official'
    try:
        shutil.move(str(templates_official), str(dst))
        mo_count = len(list(dst.rglob('*.mo')))
        print(f"[OK] Templates/Official -> 归档 ({mo_count} 个文件)")
        archived_dirs += 1
    except Exception as e:
        print(f"[ERROR] Templates/Official: {e}")
else:
    print("[SKIP] Templates/Official: 不存在")

# 5. 验证清理结果
print("\n" + "="*80)
print("清理结果验证")
print("="*80)

# 统计当前 Runner 数量
remaining_runners = list(EXPERIMENT_DIR.rglob('*Runner.mo'))
print(f"\n剩余 Runner 文件数: {len(remaining_runners)}")

# 按目录分类统计
from collections import defaultdict
runner_by_dir = defaultdict(int)
for runner in remaining_runners:
    family = runner.parent.name
    runner_by_dir[family] += 1

print("\n按目录统计:")
for family in sorted(runner_by_dir.keys()):
    count = runner_by_dir[family]
    print(f"  {family:30s} {count:2d} 个")

# 总结
print("\n" + "="*80)
print("归档总结")
print("="*80)
print(f"归档目录数: {archived_dirs}")
print(f"归档单个文件数: {archived_files}")
print(f"归档目标: {ARCHIVE_DIR}")
print(f"\n预期剩余 Runner: 48 个 + 3 个三机编队 = 51 个")
print(f"实际剩余 Runner: {len(remaining_runners)} 个")

if len(remaining_runners) == 51:
    print("\n[OK] Runner 数量正确！")
elif len(remaining_runners) == 48:
    print("\n[OK] Runner 数量正确（不含三机编队）！")
else:
    print(f"\n[WARNING] Runner 数量不符合预期")

print("\n归档完成！")
