# -*- coding: utf-8 -*-
"""Insert a caption line under every uncaptioned figure in chapters 7-9.

Captions carry the controller's measured value so each line is informative
rather than boilerplate. Figure numbers stay as 'xx' per the user's
instruction to defer numbering.
"""
import io
import json
import re

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
MET = json.load(io.open('Docs/报告/审计/atlas_metrics.json', encoding='utf-8'))

# figure-file suffix -> (what it shows, which metric to cite)
KIND = {
    'trajectory_xy':   ('水平面轨迹跟踪', 'rmse'),
    'altitude_z':      ('高度通道跟踪', None),
    'position_error':  ('位置误差时程', 'term'),
    'control_input':   ('控制输入时程', None),
    'trajectory_3d':   ('三维轨迹', None),
    'velocity':        ('速度分量时程', None),
    'attitude':        ('姿态角时程', None),
}


def fmt(v):
    return '%.3f' % v if isinstance(v, (int, float)) else None


def caption(path):
    m = re.search(r'figures/第1[01]章/(?:([^/]+)/)?([^/]+)\.png$', path)
    if not m:
        return None
    ctrl, stem = m.group(1), m.group(2)
    if ctrl not in MET or MET.get(ctrl) is None or stem not in KIND:
        return None
    what, metric = KIND[stem]
    v = MET[ctrl]
    tail = ''
    if metric == 'rmse' and fmt(v['rmse']):
        tail = '，位置 RMSE %s m' % fmt(v['rmse'])
    elif metric == 'term' and fmt(v['term']):
        tail = '，终端误差 %s m' % fmt(v['term'])
    return '图 xx　`%s` ClimbPath 50 s %s%s' % (ctrl, what, tail)


L = io.open(SRC, encoding='utf-8').read().split('\n')
out = []
added = skipped = 0
for i, l in enumerate(L):
    out.append(l)
    s = l.strip()
    if not s.startswith('!['):
        continue
    nxt = L[i + 1].strip() if i + 1 < len(L) else ''
    nxt2 = L[i + 2].strip() if i + 2 < len(L) else ''
    if nxt.startswith('图 ') or nxt2.startswith('图 '):
        continue
    m = re.match(r'!\[[^\]]*\]\(([^)]+)\)', s)
    cap = caption(m.group(1)) if m else None
    if cap:
        out += ['', cap]
        added += 1
    else:
        skipped += 1
        if skipped <= 14:
            print('SKIP %s' % (m.group(1) if m else s)[:96])

text = '\n'.join(out)
text = re.sub(r'\n{4,}', '\n\n\n', text)
print('')
print('captions added %d, skipped %d' % (added, skipped))
import sys
if '--write' in sys.argv:
    io.open(SRC, 'w', encoding='utf-8', newline='\n').write(text)
    print('WRITTEN')
