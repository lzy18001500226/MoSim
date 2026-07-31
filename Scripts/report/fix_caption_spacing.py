# -*- coding: utf-8 -*-
"""Ensure a blank line follows every figure caption line."""
import io, re, sys

P = 'Docs/报告/仿真分析报告_正文骨架.md'
CAP = re.compile(r'^图 [x0-9\-]+　')

L = io.open(P, encoding='utf-8').read().split('\n')
out, n = [], 0
for i, l in enumerate(L):
    out.append(l)
    if CAP.match(l) and i + 1 < len(L) and L[i+1].strip():
        out.append('')
        n += 1

if '--write' in sys.argv:
    io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('blank lines inserted after captions: %d' % n)
