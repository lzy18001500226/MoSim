"""
Phase 5:
1. 拆分§十：10.3编队/ECBF → 独立为§十一
2. 原§十一(Gazebo)→§十二, 原§十二(OpenBlocks)→§十三,
   原§十三→§十四, 原§十四→§十五, 原§十五→§十六, 原§十六→§十七
3. 更新§十标题为 "Official PID 与 px4ctrl 七场景对比与灵敏度验证"
"""
import re, io

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# Find line of ### 10.3
split_line = None
for i, l in enumerate(lines):
    if re.match(r'^### 10\.3', l):
        split_line = i
        break

if split_line is None:
    print("ERROR: ### 10.3 not found")
    exit(1)

# Find the ## 十 heading to fix its title
ch10_line = None
for i, l in enumerate(lines):
    if l.startswith('## 十、'):
        ch10_line = i
        break

# Fix §十 title
lines[ch10_line] = '## 十、Official PID 与 px4ctrl 七场景对比与灵敏度验证'

# Find ## 十一 (current, which is Gazebo runtime)
ch11_line = None
for i, l in enumerate(lines):
    if l.startswith('## 十一、'):
        ch11_line = i
        break

# Insert new ## 十一 heading before the 10.3 content
# But first we need to: take lines from split_line to ch11_line,
# make them a new chapter "十一"

# Approach:
# 1. Extract the 10.3 block (from split_line to ch11_line-1)
# 2. Remove it from its current position
# 3. Insert it as a new ## 十一 chapter
# 4. Renumber all subsequent chapters

# Also need to remove the bridge paragraph at the start of §十 that mentions
# "三个方向" since we're splitting

# Step 1: Build new chapter content for 十一
formation_lines = lines[split_line:ch11_line]
# Change ### 10.3 to the chapter intro, and #### to ###
new_ch11 = ['## 十一、三机编队 Figure8 与 ECBF 安全参考调节', '']
for fl in formation_lines:
    if re.match(r'^### 10\.3', fl):
        # Skip this heading, use content after it as intro
        continue
    elif re.match(r'^#### 10\.3\.(\d)', fl):
        # Promote to ### 11.x
        m = re.match(r'^#### 10\.3\.(\d+)\s+(.*)', fl)
        if m:
            new_ch11.append(f'### 11.{m.group(1)} {m.group(2)}')
        else:
            new_ch11.append(fl)
    else:
        new_ch11.append(fl)

# Step 2: Remove 10.3 block from original position
remaining = lines[:split_line] + lines[ch11_line:]

# Step 3: Find where to insert new §十一 (before current §十一 which is now at a new position)
# After removal, find ## 十一 in remaining
insert_pos = None
for i, l in enumerate(remaining):
    if l.startswith('## 十一、'):
        insert_pos = i
        break

# Insert new chapter before old §十一
final = remaining[:insert_pos] + new_ch11 + remaining[insert_pos:]

# Step 4: Renumber chapters from old §十一 onwards
# Old十一→十二, 十二→十三, 十三→十四, 十四→十五, 十五→十六, 十六→十七
remap = {'十一':'十二', '十二':'十三', '十三':'十四', '十四':'十五', '十五':'十六', '十六':'十七'}

# Also renumber their sub-sections
sub_remap = {'11':'12', '12':'13', '13':'14', '14':'15', '15':'16', '16':'17'}

# Find the start of new §十一 formation chapter - skip past it
new_ch11_end = insert_pos + len(new_ch11)

for i in range(new_ch11_end, len(final)):
    l = final[i]
    # Renumber ## headings
    m = re.match(r'^## (十一|十二|十三|十四|十五|十六)、(.*)', l)
    if m:
        old_cn = m.group(1)
        if old_cn in remap:
            final[i] = f'## {remap[old_cn]}、{m.group(2)}'
        continue
    # Renumber ### sub-sections
    m = re.match(r'^(#{3,4})\s+(\d+)\.(\S+)\s+(.*)', l)
    if m:
        hashes = m.group(1)
        major = m.group(2)
        sub = m.group(3)
        title = m.group(4)
        if major in sub_remap:
            final[i] = f'{hashes} {sub_remap[major]}.{sub} {title}'

io.open(SRC, 'w', encoding='utf-8').write('\n'.join(final))
print(f'Phase 5 done. Total lines: {len(final)}')
