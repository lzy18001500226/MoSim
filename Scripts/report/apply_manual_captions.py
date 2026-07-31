# -*- coding: utf-8 -*-
"""Insert hand-authored captions under the 60 aggregate figures.

Also guarantees a blank line before each image so that families whose four
figures currently sit on consecutive lines are separated.
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions_manual import CAP

P = 'Docs/报告/仿真分析报告_正文骨架.md'
IMG = re.compile(r'^!\[[^\]]*\]\(([^)]+)\)\s*$')

src = io.open(P, encoding='utf-8').read().split('\n')
out, hit, miss = [], [], []

for l in src:
    m = IMG.match(l)
    if not m:
        out.append(l)
        continue
    path = m.group(1).replace('\\', '/')
    cap = None
    for k, v in CAP.items():
        if path.endswith(k):
            cap = v
            break
    if cap is None:
        out.append(l)
        miss.append(path)
        continue
    if out and out[-1].strip():
        out.append('')
    out.append(l)
    out.append('')
    out.append(cap)
    hit.append(path)

if '--write' in sys.argv:
    io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))

print('captioned %d' % len(hit))
print('table entries unused: %d' % (len(CAP) - len(set(
    k for k in CAP for p in hit if p.endswith(k)))))
