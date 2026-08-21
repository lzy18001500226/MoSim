#!/usr/bin/env python3
"""清理恢复的P30-P47页面中的所有小卡片"""

import re

# 读取文件
with open(r"C:\Users\HP\Desktop\MoSim\Docs\报告\PPT\答辩PPT大纲.md", "r", encoding="utf-8") as f:
    content = f.read()

# 定义需要删除的模式
patterns_to_remove = [
    # 数字卡片（包含表格）- 更宽松的匹配
    r'\*\*数字卡片\*\*[^\n]*\n\n\|[^\|]+\|[^\n]*\n\|[^\n]+\n(?:\|[^\n]+\n)*\n',

    # 关键标注框（列表形式）
    r'\*\*关键标注框\*\*[^\n]*\n\n(?:- [^\n]+\n)+\n',

    # 关键标注（列表形式）
    r'\*\*关键标注\*\*[^\n]*\n\n(?:- [^\n]+\n)+\n',

    # 内联的"  - 关键标注框："到下一个列表项
    r'  - 关键标注框[^:]*：\n(?:    - [^\n]+\n)+',

    # 内联的"  - 关键标注："到下一个列表项
    r'  - 关键标注：\n(?:    - [^\n]+\n)+',
]

# 应用所有删除模式
cleaned = content
for pattern in patterns_to_remove:
    cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE)

# 写回文件
with open(r"C:\Users\HP\Desktop\MoSim\Docs\报告\PPT\答辩PPT大纲.md", "w", encoding="utf-8") as f:
    f.write(cleaned)

print("Batch cleanup completed")
print(f"Original length: {len(content)} chars")
print(f"Cleaned length: {len(cleaned)} chars")
print(f"Removed: {len(content) - len(cleaned)} chars")
