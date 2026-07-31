"""
Phase 2: 修复断行 — 将同段落的多行合并为单行。
规则：
- 代码块内不动
- 公式块 \\[...\\] 内不动
- 表格行(|开头)不动
- 标题行(#开头)不动
- 图片行(!开头)不动
- 图题行(图 xx)不动
- 空行是段落分隔符
- 其余连续非空行合并为一行
"""
import re, io

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

out = []
in_code = False
in_math = False
para_buf = []

def flush_para():
    global para_buf
    if para_buf:
        out.append(''.join(para_buf))
        para_buf = []

for line in lines:
    stripped = line.strip()

    # Toggle code block
    if stripped.startswith('```'):
        flush_para()
        in_code = not in_code
        out.append(line)
        continue

    if in_code:
        flush_para()
        out.append(line)
        continue

    # Detect math block start/end
    if stripped == '\\[':
        flush_para()
        in_math = True
        out.append(line)
        continue
    if stripped == '\\]':
        in_math = False
        out.append(line)
        continue
    if in_math:
        out.append(line)
        continue

    # Special lines that should NOT be merged
    is_special = (
        not stripped or  # empty line
        stripped.startswith('#') or  # heading
        stripped.startswith('|') or  # table
        stripped.startswith('!') or  # image
        stripped.startswith('>') or  # blockquote
        re.match(r'^(图|表)\s*(xx|[0-9])', stripped) or  # caption
        re.match(r'^\\\(', stripped) or  # inline math on own line
        stripped.startswith('---')  # hr
    )

    if is_special:
        flush_para()
        out.append(line)
    else:
        # Accumulate paragraph
        para_buf.append(stripped)

flush_para()

io.open(SRC, 'w', encoding='utf-8').write('\n'.join(out))

# Stats
total = len(out)
print(f'Phase 2 done: line wrapping fixed. Total lines: {total}')
