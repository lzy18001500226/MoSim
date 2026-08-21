#!/usr/bin/env python3
"""
最终综合清理脚本：
1. 删除剩余的"关键标注框"
2. 删除所有台词中的公式
3. 统计每页的视觉内容
4. 检查手绘图的prompt状态
"""

import re
from pathlib import Path

def clean_remaining_annotations(content: str) -> str:
    """删除剩余的关键标注框"""
    lines = content.split('\n')
    result = []
    skip_next = False

    for i, line in enumerate(lines):
        # 跳过"关键标注框（右侧）："及其内容
        if '关键标注框（右侧）：' in line or '关键标注：' in line:
            skip_next = True
            continue

        # 跳过标注框内容行（以✅开头）
        if skip_next and line.strip().startswith('✅'):
            continue
        else:
            skip_next = False
            result.append(line)

    return '\n'.join(result)

def remove_formulas_from_speeches(content: str) -> str:
    """删除所有台词中的LaTeX公式和数学符号"""
    lines = content.split('\n')
    result = []
    in_speech = False

    for line in lines:
        if '**台词**' in line:
            in_speech = True
            result.append(line)
            continue

        # 检测是否离开台词段落（遇到下一个markdown标题）
        if in_speech and line.strip().startswith('#'):
            in_speech = False

        if in_speech:
            # 移除LaTeX公式：$...$, $$...$$, \(...\), \[...\]
            cleaned = re.sub(r'\$\$[^$]+\$\$', '[公式已删除]', line)
            cleaned = re.sub(r'\$[^$]+\$', '[公式已删除]', cleaned)
            cleaned = re.sub(r'\\\([^)]+\\\)', '[公式已删除]', cleaned)
            cleaned = re.sub(r'\\\[[^\]]+\\\]', '[公式已删除]', cleaned)

            # 移除常见数学符号模式
            cleaned = re.sub(r'[∇∂∫∑∏√±×÷≤≥≈≠]', '', cleaned)

            # 清理连续的空格
            cleaned = re.sub(r'\s+', ' ', cleaned)

            result.append(cleaned)
        else:
            result.append(line)

    return '\n'.join(result)

def analyze_visual_content(content: str) -> dict:
    """统计每页的视觉内容"""
    pages = {}
    current_page = None

    for line in content.split('\n'):
        # 检测页码标题（匹配中文冒号和英文冒号）
        match = re.match(r'^###\s+P(\d+)[：:]', line)
        if match:
            current_page = int(match.group(1))
            pages[current_page] = {
                'has_figure': False,
                'has_table': False,
                'has_screenshot': False,
                'has_prompt': False
            }

        if current_page:
            if '**图' in line or '手绘图' in line or '流程图' in line or '架构图' in line:
                pages[current_page]['has_figure'] = True
            if '**表' in line or '| ' in line:  # Markdown table
                pages[current_page]['has_table'] = True
            if '截图' in line or 'screenshot' in line.lower():
                pages[current_page]['has_screenshot'] = True
            if 'PPT-' in line and 'prompt' in line.lower():
                pages[current_page]['has_prompt'] = True

    return pages

def main():
    import sys
    import io

    # 强制使用UTF-8输出
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    ppt_path = Path(r"C:\Users\HP\Desktop\MoSim\Docs\报告\PPT\答辩PPT大纲.md")

    print("正在读取PPT大纲...")
    content = ppt_path.read_text(encoding='utf-8')

    print("\n第一步：删除剩余的关键标注框...")
    content = clean_remaining_annotations(content)

    print("第二步：删除所有台词中的公式...")
    content = remove_formulas_from_speeches(content)

    print("\n第三步：分析每页视觉内容...")
    pages = analyze_visual_content(content)

    missing_visual = []
    missing_prompt = []

    for page_num in sorted(pages.keys()):
        info = pages[page_num]
        has_any_visual = info['has_figure'] or info['has_table'] or info['has_screenshot']

        if not has_any_visual:
            missing_visual.append(page_num)

        if info['has_figure'] and not info['has_prompt']:
            missing_prompt.append(page_num)

    print(f"\n[OK] 共分析 {len(pages)} 页")
    print(f"[OK] 有视觉内容的页面: {len(pages) - len(missing_visual)} 页")

    if missing_visual:
        print(f"\n[WARN] 缺少视觉内容的页面 ({len(missing_visual)}页): {missing_visual}")
    else:
        print("\n[OK] 所有页面都有视觉内容")

    if missing_prompt:
        print(f"\n[WARN] 需要手绘但缺prompt的页面 ({len(missing_prompt)}页): {missing_prompt}")
    else:
        print("\n[OK] 所有需要手绘的图都有prompt")

    print("\n正在保存清理后的文件...")
    ppt_path.write_text(content, encoding='utf-8')
    print("[OK] 保存完成")

    # 生成详细报告
    print("\n" + "="*60)
    print("页面视觉内容详细报告")
    print("="*60)
    for page_num in sorted(pages.keys()):
        info = pages[page_num]
        visual_types = []
        if info['has_figure']:
            visual_types.append('图')
        if info['has_table']:
            visual_types.append('表')
        if info['has_screenshot']:
            visual_types.append('截图')

        status = '[OK]' if visual_types else '[MISS]'
        prompt_status = '[OK]' if not info['has_figure'] or info['has_prompt'] else '[WARN]'

        visual_str = '+'.join(visual_types) if visual_types else '无'
        print(f"P{page_num:02d}: {status} {visual_str:15s} {prompt_status}")

if __name__ == '__main__':
    main()
