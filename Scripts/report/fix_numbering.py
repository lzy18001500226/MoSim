"""
Phase 4: 修复子节编号，使其与新的父章编号一致。
原§10的子节 → 现§八 (如 ### 10.x → 无需，已删除10.1)
原§11的子节 → 现§九
原§8的子节 → 现§十
原§12的子节 → 现§十二
原§9的子节 → 现§十三
原§13的子节 → 现§十四
原§14的子节 → 现§十五
原§15的子节 → 现§十六
原§16的子节 → 现§十七

Approach: renumber ### X.Y headings based on which ## parent they fall under.
"""
import re, io

SRC = 'Docs/报告/仿真分析报告_正文骨架.md'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# Build map: for each line, determine which ## chapter it's in
# ## chapters get arabic numbers 0(摘要),1,2,...17
ch_num = 0  # current chapter number (0=摘要, 1=一, 2=二, etc)
ch_map = {}  # line_idx -> chapter_number

for i, l in enumerate(lines):
    if re.match(r'^## ', l):
        # Determine chapter number from title
        m = re.match(r'^## (摘要|一|二|三|四|五|六|七|八|九|十(?:一|二|三|四|五|六|七)?)', l)
        if m:
            cn_map = {'摘要':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,
                      '八':8,'九':9,'十':10,'十一':11,'十二':12,'十三':13,
                      '十四':14,'十五':15,'十六':16,'十七':17}
            ch_num = cn_map.get(m.group(1), ch_num)

    # Fix ### X.Y headings - renumber X to match current chapter
    hm = re.match(r'^(#{3,4})\s+(\d+)\.(\d+(?:\.\d+)?)\s+(.*)', l)
    if hm:
        hashes = hm.group(1)
        old_major = hm.group(2)
        sub = hm.group(3)
        title = hm.group(4)
        lines[i] = f'{hashes} {ch_num}.{sub} {title}'

io.open(SRC, 'w', encoding='utf-8').write('\n'.join(lines))
print('Phase 4 done: sub-section numbers realigned.')
