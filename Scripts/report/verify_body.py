# -*- coding: utf-8 -*-
"""Integrity check for Docs/报告/仿真分析报告_正文骨架.md."""
import io
import os
import re

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
BASE = os.path.dirname(SRC)
L = io.open(SRC, encoding='utf-8').read().split('\n')

refs = []
for i, l in enumerate(L, 1):
    for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', l):
        refs.append((i, m.group(1)))
broken = [(i, r) for i, r in refs if not os.path.exists(os.path.join(BASE, r))]
print('image refs      %d' % len(refs))
print('broken refs     %d' % len(broken))
for i, r in broken[:12]:
    print('   L%-5d %s' % (i, r))

on_disk = set()
for root, _, files in os.walk(os.path.join(BASE, 'figures')):
    for f in files:
        if f.lower().endswith(('.png', '.svg')):
            p = os.path.relpath(os.path.join(root, f), BASE).replace('\\', '/')
            on_disk.add(p)
used = set(r.replace('\\', '/') for _, r in refs)
print('figures on disk %d' % len(on_disk))
print('unreferenced    %d' % len(on_disk - used))

cap = sum(1 for l in L if re.match(r'^表 ', l.strip()))
figcap = sum(1 for l in L if re.match(r'^图 ', l.strip()))
heads = [(i, l) for i, l in enumerate(L, 1) if l.startswith('| ')]
tbl = 0
prev = -5
for i, _ in heads:
    if i - prev > 2:
        tbl += 1
    prev = i
print('tables          %d  (captions %d)' % (tbl, cap))
print('figure captions %d' % figcap)

adj_img = 0
for i in range(len(L) - 2):
    a, b = L[i].strip(), L[i + 2].strip()
    if a.startswith('![') and b.startswith('![') and L[i + 1].strip() == '':
        adj_img += 1
print('adjacent images %d' % adj_img)
