"""
重构报告章节顺序 + 修复断行 + 合并孤立子节 + 修复枚举格式
按讨论定稿的大纲执行：
  摘要 → 一 → 二 → 三 → 四(合并4.1) → 五(合并5.1) → 六(改标题) → 七
  → 八(原§10 px4ctrl,合并10.1/10.1.1) → 九(原§11 SIL)
  → 十(原§8 七场景,合并8.1.1) → 十一(拆出编队/ECBF)
  → 十二(原§12 Gazebo) → 十三(原§9 OpenBlocks)
  → 十四(原§13) → 十五(原§14) → 十六(原§15) → 十七(原§16)
"""
import re, io, shutil, sys

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
BAK = SRC + '.prerestructure_v2.bak'
shutil.copy2(SRC, BAK)

lines = io.open(SRC, encoding='utf-8').readlines()

# --- Identify chapter boundaries (0-indexed line numbers) ---
ch_starts = []
for i, l in enumerate(lines):
    if re.match(r'^## ', l):
        ch_starts.append(i)
ch_starts.append(len(lines))

def get_chapter(idx):
    """Return lines for the idx-th chapter (0-based among ## headings)"""
    return lines[ch_starts[idx]:ch_starts[idx+1]]

# Current chapter indices (0-based):
# 0: 摘要
# 1: 一 背景
# 2: 二 评价体系
# 3: 三 机体
# 4: 四 接口
# 5: 五 PID
# 6: 六 目录
# 7: 七 筛查
# 8: 八 七场景+编队+ECBF
# 9: 九 OpenBlocks
# 10: 十 px4ctrl图形
# 11: 十一 SIL
# 12: 十二 Gazebo
# 13: 十三 感知规划
# 14: 十四 显示层
# 15: 十五 可复现
# 16: 十六 结论

# New order: 0,1,2,3,4,5,6,7, 10,11, 8, 12, 9, 13,14,15,16
new_order = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 8, 12, 9, 13, 14, 15, 16]

# Chinese number mapping for new chapter titles
CN_NUMS = ['摘要','一','二','三','四','五','六','七','八','九',
           '十','十一','十二','十三','十四','十五','十六','十七']

# New titles (index 0=摘要 keeps as-is)
NEW_TITLES = {
    0: None,  # keep 摘要
    1: None,  # keep
    2: None,  # keep
    3: None,  # keep
    4: '统一控制器接口与 FormalRunner 执行边界',
    5: None,  # keep
    6: '8 族 46 条控制器的图形化建模与统一实现',
    7: None,  # keep
    8: None,  # keep (px4ctrl title already good)
    9: None,  # keep (SIL title already good)
    10: None, # keep (七场景 title)
    11: None, # keep (Gazebo)
    12: None, # keep (OpenBlocks)
    13: None, # keep
    14: None, # keep
    15: None, # keep
    16: None, # keep
}

print(f'Chapters found: {len(ch_starts)-1}')
print(f'New order: {new_order}')
print(f'Backup saved to: {BAK}')

# --- Assemble new document ---
new_lines = lines[:ch_starts[0]]  # everything before first ##

for new_idx, old_idx in enumerate(new_order):
    ch = list(get_chapter(old_idx))

    # Rename ## heading with new number
    old_heading = ch[0]
    if new_idx == 0:
        # 摘要 stays as-is
        pass
    else:
        cn = CN_NUMS[new_idx]
        custom_title = NEW_TITLES.get(new_idx)
        if custom_title:
            ch[0] = f'## {cn}、{custom_title}\n'
        else:
            # Extract the part after 、 from old heading
            m = re.match(r'^## \S+、(.+)$', old_heading.strip())
            if m:
                ch[0] = f'## {cn}、{m.group(1)}\n'
            # else keep as-is (摘要)

    new_lines.extend(ch)

# --- Write intermediate result ---
io.open(SRC, 'w', encoding='utf-8').writelines(new_lines)
print(f'Phase 1 done: chapters reordered. Total lines: {len(new_lines)}')
