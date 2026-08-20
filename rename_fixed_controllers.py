#!/usr/bin/env python3
"""批量重命名 fixed_ 前缀的控制器文件和类名"""
import re
from pathlib import Path

# 重命名映射
RENAME_MAP = {
    'FixedAwffPid': 'AwffPid',
    'FixedAwffL1Indi': 'AwffL1Indi',
    'FixedAwffL1Residual': 'AwffL1Residual',
    'FixedLinearMpcL1Indi': 'LinearMpcL1Indi',
    'FixedQpNmpcL1IndiCbf': 'QpNmpcL1IndiCbf',
}

BASE_DIR = Path('.')
MODELS_DIR = BASE_DIR / 'Models' / 'MoSimQuadrotorModel'

def rename_in_file(file_path: Path):
    """在文件内容中替换类名"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for old_name, new_name in RENAME_MAP.items():
            # 替换 within 语句
            content = re.sub(rf'\bwithin\s+MoSimQuadrotorModel\.Control\.IntegratedChains\.{old_name}\b',
                           f'within MoSimQuadrotorModel.Control.IntegratedChains.{new_name}',
                           content)
            content = re.sub(rf'\bwithin\s+MoSimQuadrotorModel\.Experiment\.IntegratedChains\.{old_name}\b',
                           f'within MoSimQuadrotorModel.Experiment.IntegratedChains.{new_name}',
                           content)
            
            # 替换 model 声明
            content = re.sub(rf'\bmodel\s+{old_name}', f'model {new_name}', content)
            
            # 替换类引用
            content = re.sub(rf'\b{old_name}Core\b', f'{new_name}Core', content)
            content = re.sub(rf'\b{old_name}GraphicalRunner\b', f'{new_name}GraphicalRunner', content)
            content = re.sub(rf'\b{old_name}FamilyRunner\b', f'{new_name}FamilyRunner', content)
            content = re.sub(rf'\bControl\.IntegratedChains\.{old_name}\.', 
                           f'Control.IntegratedChains.{new_name}.', content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            print(f"UPDATED {file_path}")
            return True
        return False
    except Exception as e:
        print(f"ERROR {file_path}: {e}")
        return False

def rename_directory(old_dir: Path, new_name: str):
    """重命名目录"""
    if old_dir.exists():
        new_dir = old_dir.parent / new_name
        old_dir.rename(new_dir)
        print(f"DIR: {old_dir} -> {new_dir}")
        return new_dir
    return None

def rename_file(old_file: Path, new_name: str):
    """重命名文件"""
    if old_file.exists():
        new_file = old_file.parent / new_name
        old_file.rename(new_file)
        print(f"FILE: {old_file.name} -> {new_name}")
        return new_file
    return old_file

# 收集所有需要处理的.mo文件
mo_files = list(MODELS_DIR.rglob('*.mo'))
print(f"Found {len(mo_files)} .mo files")
print()

# 第一步：重命名文件内容
print("=== Step 1: Update file contents ===")
updated_count = 0
for mo_file in mo_files:
    if rename_in_file(mo_file):
        updated_count += 1
print(f"Updated {updated_count} files\n")

# 第二步：重命名目录
print("=== Step 2: Rename directories ===")
for old_name, new_name in RENAME_MAP.items():
    # Control/IntegratedChains 下的目录
    old_dir = MODELS_DIR / 'Control' / 'IntegratedChains' / old_name
    rename_directory(old_dir, new_name)

print()

# 第三步：重命名文件
print("=== Step 3: Rename files ===")
for old_name, new_name in RENAME_MAP.items():
    # Core 文件
    core_dir = MODELS_DIR / 'Control' / 'IntegratedChains' / new_name
    if core_dir.exists():
        old_core = core_dir / f'{old_name}Core.mo'
        rename_file(old_core, f'{new_name}Core.mo')
    
    # GraphicalRunner 文件
    runner_dir = MODELS_DIR / 'Experiment' / 'IntegratedChains'
    old_runner = runner_dir / f'{old_name}GraphicalRunner.mo'
    rename_file(old_runner, f'{new_name}GraphicalRunner.mo')
    
    # FamilyRunner 文件
    for family in ['PidFamily', 'OptimizationPredictive']:
        family_dir = MODELS_DIR / 'Experiment' / family
        old_family = family_dir / f'{old_name}FamilyRunner.mo'
        rename_file(old_family, f'{new_name}FamilyRunner.mo')
    
    # Template 文件
    template_dir = MODELS_DIR / 'Experiment' / 'Templates' / 'IntegratedChains'
    old_template = template_dir / f'{old_name}.mo'
    rename_file(old_template, f'{new_name}.mo')

print("\nDone!")
