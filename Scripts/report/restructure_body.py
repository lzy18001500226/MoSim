# -*- coding: utf-8 -*-
"""Plan-A restructure of Docs/报告/仿真分析报告_正文骨架.md.

Reorders chapters into five logical parts, renumbers headings to the
一、/ 1.1 / 1.1.1 convention, and merges the micro-chapters.
Structural only: no prose is rewritten here.
"""
import io
import re
import sys

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'

# 1-indexed inclusive line ranges of the pre-restructure file.
BLOCKS = {
    'HEAD':     (1, 6),
    'ABSTRACT': (7, 48),
    'S1':       (49, 130),
    'S2':       (131, 147),
    'S3':       (148, 244),
    'S4':       (245, 317),
    'S5':       (318, 371),
    'S6':       (372, 904),
    'S7':       (905, 911),
    'S8H':      (912, 913),
    'S8_1':     (914, 960),
    'S8_2':     (961, 974),
    'S8_3':     (975, 999),
    'S8_4':     (1000, 1018),
    'S9H':      (1019, 1025),
    'S9_1':     (1026, 1098),
    'S9_2':     (1099, 1169),
    'S10':      (1170, 1689),
    'S11':      (1690, 1941),
    'S12':      (1942, 2064),
    'S13H':     (2065, 2070),
    'S13_1':    (2071, 2160),
    'S14':      (2161, 2172),
    'S15':      (2173, 2184),
    'S16':      (2185, 2192),
    'S17':      (2193, 2262),
}

CN = ['', '一', '二', '三', '四', '五', '六', '七', '八',
      '九', '十', '十一', '十二', '十三', '十四', '十五', '十六']

LINES = io.open(SRC, encoding='utf-8').read().split('\n')


def body(key, drop_h2=False):
    a, b = BLOCKS[key]
    out = LINES[a - 1:b]
    if drop_h2:
        i = 0
        while i < len(out) and not out[i].startswith('## '):
            i += 1
        if i < len(out):
            j = i + 1
            while j < len(out) and out[j].strip() == '':
                j += 1
            out = out[:i] + out[j:]
    while out and out[-1].strip() == '':
        out.pop()
    return out


def renum(lines, mapping):
    res = []
    for l in lines:
        m = re.match(r'^(#{3,4})\s+(\d+(?:\.\d+)*)\s+(.*)$', l)
        if m and m.group(2) in mapping:
            l = '%s %s %s' % (m.group(1), mapping[m.group(2)], m.group(3))
        res.append(l)
    return res


def h2(n, title):
    return ['## %s、%s' % (CN[n], title), '']


O = []
O += body('HEAD')
O += ['']
O += body('ABSTRACT')
O += ['']

# 一、研究背景
O += h2(1, '研究背景与平台战略意义')
O += body('S1', drop_h2=True)
O += ['']

# 二、评价体系（S2 + S9 + S7 合并）
O += h2(2, '评价体系：可审计实验链、指标定义与负样本处理')
O += ['本章先把全文所有判定所依据的证据链、实验 Profile、指标定义与失败处理规则',
      '集中给出。第七章起的全部结果均按本章口径判读，后续章节不再重复声明判据。',
      '']
O += ['### 2.1 可审计实验链', '']
O += body('S2', drop_h2=True)
O += ['']
O += ['### 2.2 实验 Profile', '']
O += body('S9H', drop_h2=True)
O += ['']
O += renum(body('S9_1'), {'9.1': '2.3'})
O += ['']
O += renum(body('S9_2'), {'9.2': '2.4'})
O += ['']
O += ['### 2.5 负样本处理原则', '']
O += body('S7', drop_h2=True)
O += ['']

# 三～六、平台构建
O += h2(3, '云纵150参照虚拟机体与参数 Profile')
O += body('S3', drop_h2=True)
O += ['']
O += h2(4, '统一控制器接口')
O += body('S4', drop_h2=True)
O += ['']
O += h2(5, 'Official PID 工程基线')
O += body('S5', drop_h2=True)
O += ['']
O += h2(6, '控制器目录与实现状态')
O += body('S6', drop_h2=True)
O += ['']

# 七～九、仿真结果
M10 = {'10.%d' % i: '7.%d' % i for i in range(1, 7)}
M10.update({'10.6.%d' % i: '7.6.%d' % i for i in range(1, 7)})
O += h2(7, 'ClimbPath 50 s 名义基线筛查')
O += renum(body('S10', drop_h2=True), M10)
O += ['']

M11 = {'11.%d' % i: '8.%d' % i for i in range(1, 4)}
M11.update({'11.1.1': '8.1.1', '11.3.1': '8.3.1',
            '11.3.2': '8.3.2', '11.3.3': '8.3.3'})
O += h2(8, '七场景、灵敏度、三机编队与 ECBF 安全')
O += renum(body('S11', drop_h2=True), M11)
O += ['']

O += h2(9, 'OpenBlocks 障碍地图避障（MWORKS 拓展验证）')
O += renum(body('S12', drop_h2=True), {'12.1': '9.1', '12.2': '9.2'})
O += ['']

# 十～十四、从图形模型到运行时
O += h2(10, '图形化重建与代码导出')
O += renum(body('S8_1'), {'8.1': '10.1', '8.1.1': '10.1.1'})
O += ['']
O += renum(body('S8_2'), {'8.2': '10.2'})
O += ['']
O += ['### 10.3 生成产物与交付', '']
O += body('S14', drop_h2=True)
O += ['']

O += h2(11, 'SIL 数值等价链')
O += renum(body('S8_3'), {'8.3': '11.1'})
O += ['']
O += renum(body('S8_4'), {'8.4': '11.2'})
O += ['']

O += ['@@C99_CHAPTER@@', '']

O += h2(13, '感知与规划组件状态')
O += renum(body('S13_1'), {'13.1': '13.0__TMP'})
O += ['']

O += h2(14, '显示层与验收边界')
O += body('S13H', drop_h2=True)
O += ['']

O += h2(15, '可复现性、已知限制与交付审计')
O += ['### 15.1 可复现性与已知限制', '']
O += body('S15', drop_h2=True)
O += ['']
O += ['### 15.2 交付审计说明', '']
O += body('S16', drop_h2=True)
O += ['']

M17 = {'17.%d' % i: '16.%d' % i for i in range(1, 5)}
M17.update({'17.2.%d' % i: '16.2.%d' % i for i in range(1, 4)})
O += h2(16, '结论与展望')
O += renum(body('S17', drop_h2=True), M17)
O += ['']

# ---- cross-reference fixes (prose only; image paths must survive) ----
XREF = [
    ('第 10 章', '第七章'), ('第 11 章', '第八章'), ('第 12 章', '第九章'),
    ('第 3 章', '第三章'), ('第 5 章', '第五章'), ('第 4 章', '第四章'),
    ('第 6 章', '第六章'), ('第 8 章', '第十章'), ('第 9 章', '第二章'),
    ('第 7 章', '§2.5'), ('第10.4节', '第 7.4 节'),
    ('§10.1', '§7.1'), ('§10.4', '§7.4'), ('§10.5', '§7.5'),
    ('§10.6', '§7.6'), ('§11.3', '§8.3'), ('§11.2', '§8.2'),
    ('§11.1', '§8.1'), ('§9.2', '§2.4'), ('§9.1', '§2.3'),
    ('§8.3', '§11.1'), ('§8.4', '§11.2'), ('§8.1', '§10.1'),
    ('表 8-1', '表 11-1'),
]

# promote the three component paragraphs of old 13.1 into 13.1/13.2/13.3
COMP = [('**FUEL。**', '### 13.1 FUEL 规划器', 'FUEL 规划器的'),
        ('**Diff-Planner。**', '### 13.2 Diff-Planner', 'Diff-Planner '),
        ('**FAST-LIO。**', '### 13.3 FAST-LIO', 'FAST-LIO ')]

out = []
for l in O:
    if re.match(r'^### 13\.0__TMP\s', l):
        continue
    for a, b in XREF:
        if a in l and 'figures/' not in l and '](' not in l:
            l = l.replace(a, b)
    for tag, head, lead in COMP:
        if l.startswith(tag):
            out += [head, '']
            l = lead + l[len(tag):].lstrip()
            break
    out.append(l)

text = '\n'.join(out)
text = re.sub(r'\n{4,}', '\n\n\n', text)
if not text.endswith('\n'):
    text += '\n'
io.open(SRC, 'w', encoding='utf-8', newline='\n').write(text)
print('written lines=%d' % len(text.split('\n')))
