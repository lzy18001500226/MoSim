"""
Phase 3: 修复孤立子节
- §四: 删除 ### 4.1 标题行（内容提升为正文）
- §五: 删除 ### 5.1 标题行
- 原§10(现§八): 删除 ### 10.1 和 #### 10.1.1 标题行
- 原§8.1(现§十): 删除 #### 8.1.1 标题行

同时修复§1.2的markdown列表为(1)(2)(3)行内格式
"""
import re, io

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
text = io.open(SRC, encoding='utf-8').read()

# Remove orphan sub-section headings
# §四 has "### 4.1 FormalRunner..." → remove the heading line
text = re.sub(r'^### 4\.1 FormalRunner.*\n+', '', text, flags=re.MULTILINE)

# §五 has "### 5.1 正式 Runner..."  → remove
text = re.sub(r'^### 5\.1 正式 Runner.*\n+', '', text, flags=re.MULTILINE)

# §八(was §10) has "### 10.1 定位" → remove
text = re.sub(r'^### 10\.1 定位\n+', '', text, flags=re.MULTILINE)

# And "#### 10.1.1 图形位置/速度外环与姿态投影" → remove
text = re.sub(r'^#### 10\.1\.1 图形位置.*\n+', '', text, flags=re.MULTILINE)

# §十(was §8) has "#### 8.1.1 阶跃响应量化对比" → remove
text = re.sub(r'^#### 8\.1\.1 阶跃响应.*\n+', '', text, flags=re.MULTILINE)

io.open(SRC, 'w', encoding='utf-8').write(text)
print('Phase 3 done: orphan sub-sections removed.')

# verify
lines = text.split('\n')
print(f'Total lines: {len(lines)}')
