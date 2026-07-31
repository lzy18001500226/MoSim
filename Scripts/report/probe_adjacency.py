# -*- coding: utf-8 -*-
"""Report unreferenced figures and true image-adjacency pairs."""
import io
import os
import re

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
BASE = os.path.dirname(SRC)
L = io.open(SRC, encoding='utf-8').read().split('\n')

refs = [(i, m.group(1)) for i, l in enumerate(L, 1)
        for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', l)]
used = set(r.replace(os.sep, '/') for _, r in refs)

disk = set()
for root, _, fs in os.walk(os.path.join(BASE, 'figures')):
    for f in fs:
        if f.lower().endswith(('.png', '.svg')):
            rel = os.path.relpath(os.path.join(root, f), BASE)
            disk.add(rel.replace(os.sep, '/'))

un = sorted(disk - used)
print('unreferenced %d (svg %d)' % (un.__len__(),
                                    sum(1 for x in un if x.endswith('.svg'))))
for x in un[:12]:
    print('   ' + x)

img = [i for i, l in enumerate(L, 1) if l.strip().startswith('![')]
pairs = []
for a, b in zip(img, img[1:]):
    if all(L[k - 1].strip() == '' for k in range(a + 1, b)):
        pairs.append((a, b))
print('')
print('true adjacent image pairs %d' % len(pairs))
print('first 10 %s' % (pairs[:10],))
