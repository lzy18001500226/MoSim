# -*- coding: utf-8 -*-
"""Replace 口径 with context-appropriate neutral terms; fix stale 三层/五层."""
import io, sys

P = 'Docs/报告/仿真分析报告_正文骨架.md'

# (line_no, old, new) -- line-anchored so each site gets the right term
EDITS = [
 (26,   '口径定义、逐条明细与换算关系见',      '计数基准定义、逐条明细与换算关系见'),
 (95,   '是两个不同口径，',                    '是两个不同的计数基准，'),
 (134,  '均按本章口径判读',                    '均按本章判据判读'),
 (1013, '与 §7.1 三层口径不一致的数字',        '与 §7.1 五层计数基准不一致的数字'),
 (1092, '达标的五层口径定义',                  '达标的五层计数基准定义'),
 (1094, '| 口径 | 数量 | 定义 |',              '| 计数基准 | 数量 | 定义 |'),
 (1102, '三层口径不可相加成 48：',             '五层计数基准不可相加成 48：'),
 (1103, '口径权威文件为',                      '计数基准权威文件为'),
 (1106, '上表按口径分层，',                    '上表按计数基准分层，'),
 (1161, '口径权威见',                          '计数基准权威见'),
 (1370, '归一化口径相对早期版本',              '归一化方式相对早期版本'),
 (1415, '只作为口径完整性的占位证据',          '只作为族覆盖完整性的占位证据'),
 (2128, '图件清单与口径注记见',                '图件清单与统计范围注记见'),
 (2356, '存在两种不同口径，',                  '存在两种不同的统计范围，'),
 (2357, '硬约束激活口径下',                    '按硬约束激活统计时，'),
 (2362, '一律采用 56 样本口径',                '一律采用 56 样本统计范围'),
]

L = io.open(P, encoding='utf-8').read().split('\n')
ok, bad = 0, []
for n, a, b in EDITS:
    if a in L[n-1]:
        L[n-1] = L[n-1].replace(a, b)
        ok += 1
    else:
        bad.append(n)

if '--write' in sys.argv:
    io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))

print('applied %d/%d' % (ok, len(EDITS)))
print('missed lines:', bad)
print('remaining 口径:', sum(l.count('口径') for l in L))
