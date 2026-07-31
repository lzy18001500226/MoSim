# -*- coding: utf-8 -*-
"""Map each atlas controller in chapter 7 to its measured G3 metrics."""
import io
import json
import os
import re

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
G3 = ('Results/control_platform/phase2_full_48_climbpath/'
      'g3_repair/G3_STATUS.json')
CAT = ('Results/control_platform/phase2_full_48_climbpath/'
       'g3_repair/G3_CATALOG_48_CURRENT_STATUS.json')

rows = {r['controller_id']: r
        for r in json.load(io.open(G3, encoding='utf-8'))['rows']}
cat = {r['scheme_id']: r
       for r in json.load(io.open(CAT, encoding='utf-8'))['rows']}

L = io.open(SRC, encoding='utf-8').read().split('\n')
seen = []
for l in L:
    for m in re.finditer(r'!\[[^\]]*\]\(figures/第10章/([^/]+)/', l):
        d = m.group(1)
        if d not in seen:
            seen.append(d)

print('atlas dirs %d' % len(seen))
out = {}
for d in seen:
    r = rows.get(d) or cat.get(d)
    if r:
        out[d] = {
            'rmse': r.get('position_rmse_m'),
            'term': r.get('terminal_position_error_norm_m'),
            'status': r.get('status'),
            'zh': cat.get(d, {}).get('display_name_zh'),
            'cat': cat.get(d, {}).get('category'),
        }
    else:
        out[d] = None

for d in seen:
    v = out[d]
    if v is None:
        print('  %-42s NO-MATCH' % d)
    else:
        print('  %-42s %-5s rmse=%-9s term=%-9s %s' % (
            d, v['status'],
            ('%.3f' % v['rmse']) if v['rmse'] is not None else '-',
            ('%.3f' % v['term']) if v['term'] is not None else '-',
            v['zh'] or ''))

os.makedirs('Docs/报告/审计', exist_ok=True)
json.dump(out, io.open('Docs/报告/审计/atlas_metrics.json', 'w',
                       encoding='utf-8'), ensure_ascii=False, indent=2)
