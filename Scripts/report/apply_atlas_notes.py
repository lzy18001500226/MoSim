# -*- coding: utf-8 -*-
"""Insert per-controller analysis after each bold name in the 7.6 atlas."""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atlas_notes import NOTE

P = 'Docs/报告/仿真分析报告_正文骨架.md'
NAME = re.compile(r'^\*\*([a-z0-9_]+)(?: \([^)]*\))?\*\*\s*$')
W = 40  # wrap width in CJK chars


def wrap(t):
    out, cur = [], ''
    for ch in t:
        cur += ch
        if len(cur) >= W and ch in '。；，':
            out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    return out


L = io.open(P, encoding='utf-8').read().split('\n')
out, done = [], []
for l in L:
    out.append(l)
    m = NAME.match(l)
    if m and m.group(1) in NOTE:
        out.append('')
        out.extend(wrap(NOTE[m.group(1)]))
        done.append(m.group(1))

if '--write' in sys.argv:
    io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('notes inserted %d / table %d' % (len(done), len(NOTE)))
print('unused:', sorted(set(NOTE) - set(done)))
