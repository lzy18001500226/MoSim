"""
Phase 6: 第二轮重构
- 合并§八(px4ctrl图形)+§九(SIL) → 新§八 "px4ctrl 图形化设计与 MWORKS 全机验证"
- §十(七场景) → 新§九
- §十一(编队) → 新§十
- §十三(OpenBlocks) → 新§十一 (上移到代码生成前)
- §十二(Gazebo) 拆分: 代码生成部分→新§十二, Gazebo运行→新§十三
- §十四→十四, §十五→十五, §十六→十六, §十七→十七 (不变)
"""
import re, io

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# Find chapter boundaries
ch_starts = []
for i, l in enumerate(lines):
    if re.match(r'^## ', l):
        ch_starts.append(i)
ch_starts.append(len(lines))

def get_ch(idx):
    return lines[ch_starts[idx]:ch_starts[idx+1]]

# Current chapters (0-indexed):
# 0: 摘要
# 1: 一 背景
# 2: 二 评价体系
# 3: 三 机体
# 4: 四 接口
# 5: 五 PID
# 6: 六 目录
# 7: 七 筛查
# 8: 八 px4ctrl图形 (L2114)
# 9: 九 SIL (L2165)
# 10: 十 七场景 (L2200)
# 11: 十一 编队 (L2312)
# 12: 十二 Gazebo (L2423)
# 13: 十三 OpenBlocks (L2475)
# 14: 十四 感知规划 (L2577)
# 15: 十五 显示层 (L2658)
# 16: 十六 可复现 (L2678)
# 17: 十七 结论 (L2690)

# Step 1: Build new chapter blocks

# Chapters 0-7 stay in place
pre = lines[:ch_starts[8]]

# New §八 = old§八 + old§九 merged, new title
ch8_old = get_ch(8)
ch9_old = get_ch(9)
# Replace §八 title
new_ch8_title = '## 八、px4ctrl 图形化设计与 MWORKS 全机验证\n'
ch8_old[0] = new_ch8_title
# Remove the bridge paragraph I added earlier about "第七章完成了..."
# since we'll rewrite it
# Renumber §九's sub-sections to 8.x (continuing from 8.3)
# First find max subsection in old§八
max_sub_in_8 = 0
for l in ch8_old:
    m = re.match(r'^### 8\.(\d+)', l)
    if m:
        max_sub_in_8 = max(max_sub_in_8, int(m.group(1)))

# Renumber §九 sub-sections: 9.x → 8.(x + max_sub_in_8)
ch9_merged = []
for l in ch9_old:
    if re.match(r'^## ', l):
        # Skip the ## heading of old §九, we're merging
        continue
    m = re.match(r'^(#{3,4})\s+9\.(\d+)\s+(.*)', l)
    if m:
        hashes = m.group(1)
        sub = int(m.group(2))
        title = m.group(3)
        new_sub = sub + max_sub_in_8
        ch9_merged.append(f'{hashes} 8.{new_sub} {title}')
    else:
        ch9_merged.append(l)

merged_ch8 = ch8_old + ch9_merged

# New §九 = old§十 (七场景), renumber 10.x → 9.x
ch10_old = get_ch(10)
new_ch9 = []
for l in ch10_old:
    if re.match(r'^## ', l):
        new_ch9.append('## 九、Official PID 与 px4ctrl 七场景对比与灵敏度验证')
    else:
        m = re.match(r'^(#{3,4})\s+10\.(\d+)\s+(.*)', l)
        if m:
            new_ch9.append(f'{m.group(1)} 9.{m.group(2)} {m.group(3)}')
        else:
            new_ch9.append(l)

# New §十 = old§十一 (编队), renumber 11.x → 10.x
ch11_old = get_ch(11)
new_ch10 = []
for l in ch11_old:
    if re.match(r'^## ', l):
        new_ch10.append('## 十、三机编队 Figure8 与 ECBF 安全参考调节')
    else:
        m = re.match(r'^(#{3,4})\s+11\.(\d+)\s+(.*)', l)
        if m:
            new_ch10.append(f'{m.group(1)} 10.{m.group(2)} {m.group(3)}')
        else:
            new_ch10.append(l)

# New §十一 = old§十三 (OpenBlocks), renumber 13.x → 11.x
ch13_old = get_ch(13)
new_ch11 = []
for l in ch13_old:
    if re.match(r'^## ', l):
        new_ch11.append('## 十一、OpenBlocks 障碍地图避障（MWORKS 拓展验证）')
    else:
        m = re.match(r'^(#{3,4})\s+13\.(\d+)\s+(.*)', l)
        if m:
            new_ch11.append(f'{m.group(1)} 11.{m.group(2)} {m.group(3)}')
        else:
            new_ch11.append(l)

# New §十二 and §十三: split old§十二 (Gazebo)
# old§十二 contains: 12.1 运行时链路与识别, 12.2 正向任务结果, 12.3 反向风扰补偿, 12.4 未通过记录
# Code generation part is in old§八's ### 8.2 and ### 8.3 already
# So old§十二 is purely Gazebo runtime. But we need a separate "code generation" chapter.
# Actually looking at the content:
# - old§八 has: px4ctrl公式(8.1 implicit) + 8.2图形模型到C链路 + 8.3生成产物与交叉编译
# - old§九 has: 9.1 50s SIL对比 + 9.2 SIL一致性公式
#
# For the new structure:
# - New§八 should have: px4ctrl设计+公式+SIL验证 (keep 8.2/8.3 about code gen? NO)
# - New§十二 should have: code generation (8.2 + 8.3 content)
#
# Actually, let me re-read what 8.2 and 8.3 contain...
# Looking at the line numbers: 8.2 starts at L2132, 8.3 at L2145, §九 starts at L2165
# So 8.2 and 8.3 are very short sections about the code generation pipeline
# They should move to the new §十二

# Let's find the exact lines of 8.2 and 8.3 within merged_ch8
split_at = None
for idx, l in enumerate(merged_ch8):
    if re.match(r'^### 8\.2 ', l):
        split_at = idx
        break

if split_at:
    # merged_ch8[:split_at] = new §八 (design + SIL)
    # merged_ch8[split_at:] = content for new §十二 (code generation)
    codegen_content = merged_ch8[split_at:]
    merged_ch8 = merged_ch8[:split_at]

    # Build new §十二
    new_ch12 = ['## 十二、px4ctrl C99 代码生成与交叉编译', '']
    for l in codegen_content:
        m = re.match(r'^(#{3,4})\s+8\.(\d+)\s+(.*)', l)
        if m:
            hashes = m.group(1)
            sub = int(m.group(2)) - 1  # 8.2→12.1, 8.3→12.2, etc
            new_ch12.append(f'{hashes} 12.{sub} {m.group(3)}')
        else:
            new_ch12.append(l)
else:
    new_ch12 = ['## 十二、px4ctrl C99 代码生成与交叉编译', '',
                '（代码生成内容待从§八拆入）']

# Also move SIL sub-sections numbering: they were renumbered to 8.4, 8.5
# SIL should stay in §八 as it validates the model, not the deployment
# Keep merged_ch8 as-is (it has design + SIL)

# New §十三 = old§十二 (Gazebo runtime), renumber 12.x → 13.x
ch12_old = get_ch(12)
new_ch13 = []
for l in ch12_old:
    if re.match(r'^## ', l):
        new_ch13.append('## 十三、生成 C99 在 ROS1/Gazebo 的运行时闭环')
    else:
        m = re.match(r'^(#{3,4})\s+12\.(\d+)\s+(.*)', l)
        if m:
            new_ch13.append(f'{m.group(1)} 13.{m.group(2)} {m.group(3)}')
        else:
            new_ch13.append(l)

# §十四 = old§十四 (感知规划), renumber 14.x stays 14.x
ch14_old = get_ch(14)
# §十五 = old§十五, §十六 = old§十六, §十七 = old§十七
ch15_old = get_ch(15)
ch16_old = get_ch(16)
ch17_old = get_ch(17)

# Assemble
final = pre + merged_ch8 + new_ch9 + new_ch10 + new_ch11 + new_ch12 + new_ch13 + ch14_old + ch15_old + ch16_old + ch17_old

io.open(SRC, 'w', encoding='utf-8').write('\n'.join(final))
print(f'Phase 6 done. Total lines: {len(final)}')
PY