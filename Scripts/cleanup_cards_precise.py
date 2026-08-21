#!/usr/bin/env python3
"""精确清理PPT大纲中的小卡片，保留台词中的正常叙述"""

import re

# 读取文件
with open(r"C:\Users\HP\Desktop\MoSim\Docs\报告\PPT\答辩PPT大纲.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 标记需要删除的行
to_delete = []
i = 0
while i < len(lines):
    line = lines[i]

    # 检测"**数字卡片**"或"**关键标注**"或"**关键标注框**"开头的段落
    if re.match(r'^\*\*(数字卡片|关键标注框?)\*\*', line):
        # 标记当前行删除
        to_delete.append(i)
        i += 1

        # 删除后续空行
        while i < len(lines) and lines[i].strip() == '':
            to_delete.append(i)
            i += 1

        # 如果是表格形式，删除整个表格
        if i < len(lines) and lines[i].startswith('|'):
            while i < len(lines) and (lines[i].startswith('|') or lines[i].strip() == ''):
                to_delete.append(i)
                i += 1
        # 如果是列表形式，删除整个列表
        elif i < len(lines) and lines[i].startswith('- '):
            while i < len(lines) and (lines[i].startswith('- ') or lines[i].strip() == ''):
                to_delete.append(i)
                i += 1

        # 删除列表/表格后的空行
        while i < len(lines) and lines[i].strip() == '':
            to_delete.append(i)
            i += 1
    else:
        i += 1

# 创建清理后的内容
cleaned_lines = [line for idx, line in enumerate(lines) if idx not in to_delete]

# 写回文件
with open(r"C:\Users\HP\Desktop\MoSim\Docs\报告\PPT\答辩PPT大纲.md", "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print(f"Removed {len(to_delete)} lines containing small cards")
print(f"Original: {len(lines)} lines")
print(f"Cleaned: {len(cleaned_lines)} lines")
