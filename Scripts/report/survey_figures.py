# -*- coding: utf-8 -*-
"""Per-chapter survey of figure captions and stacking."""
import io
import re

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
L = io.open(SRC, encoding='utf-8').read().split('\n')

chap = '(前言)'
stat = {}
order = []
for i, l in enumerate(L, 1):
    m = re.match(r'^## (.+)$', l)
    if m:
        chap = m.group(1)[:34]
        if chap not in stat:
            stat[chap] = {'img': 0, 'cap': 0, 'stack': 0}
            order.append(chap)
        continue
    if chap not in stat:
        stat[chap] = {'img': 0, 'cap': 0, 'stack': 0}
        order.append(chap)
    s = l.strip()
    if s.startswith('!['):
        stat[chap]['img'] += 1
        nxt = L[i].strip() if i < len(L) else ''
        nxt2 = L[i + 1].strip() if i + 1 < len(L) else ''
        if nxt.startswith('图 ') or nxt2.startswith('图 '):
            stat[chap]['cap'] += 1
        else:
            stat[chap]['stack'] += 1

print('%-36s %5s %5s %6s' % ('chapter', 'img', 'cap', 'nocap'))
tot = [0, 0, 0]
for c in order:
    d = stat[c]
    if d['img']:
        print('%-36s %5d %5d %6d' % (c, d['img'], d['cap'], d['stack']))
        tot[0] += d['img']
        tot[1] += d['cap']
        tot[2] += d['stack']
print('%-36s %5d %5d %6d' % ('TOTAL', tot[0], tot[1], tot[2]))
