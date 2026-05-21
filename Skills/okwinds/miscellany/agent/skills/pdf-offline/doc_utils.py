#!/usr/bin/env python3
"""
PDF 处理工具脚本
支持 PDF 文件的读取、写入、合并、分割等操作
"""

import sys
import json
import argparse
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent


def _install_hint() -> str:
    return f"bash {SKILL_DIR / 'install.sh'}"


def read_pdf(file_path):
    """读取 PDF 文件文本内容"""
    try:
        from pypdf import PdfReader
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print(f"请运行: {_install_hint()}")
        return None

    file_path = Path(file_path)
    if not file_path.exists():
        print(f"错误: 文件不存在 - {file_path}")
        return None

    try:
        reader = PdfReader(file_path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            pages.append({
                "page": i + 1,
                "content": text
            })

        result = {
            "file": str(file_path),
            "total_pages": len(pages),
            "pages": pages
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        print(f"错误: 读取 PDF 失败 - {e}")
        return None


def write_pdf(file_path, text, title="PDF Document"):
    """创建简单 PDF 文档"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.units import inch
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print(f"请运行: {_install_hint()}")
        return False

    file_path = Path(file_path)

    try:
        c = canvas.Canvas(str(file_path))
        page_width, page_height = c._pagesize

        # 设置字体 - 优先尝试中文字体
        font_name = "Helvetica"
        font_loaded = False

        # 尝试加载常见的中文字体
        chinese_fonts = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\msyh.ttc",  # Windows (微软雅黑)
            "C:\\Windows\\Fonts\\simhei.ttf",  # Windows (黑体)
        ]

        for font_path in chinese_fonts:
            if Path(font_path).exists():
                try:
                    pdfmetrics.registerFont(TTFont('Chinese', font_path))
                    font_name = 'Chinese'
                    font_loaded = True
                    break
                except:
                    continue

        # 页面边距
        margin = 0.75 * inch
        content_width = page_width - 2 * margin
        line_height = 24 if font_loaded else 14
        y = page_height - margin - 40

        # 设置标题
        c.setFont(font_name, 24 if font_loaded else 16)
        c.drawString(margin, y, title)
        y -= 50

        # 绘制分隔线
        c.setLineWidth(1)
        c.line(margin, y, page_width - margin, y)
        y -= 30

        # 设置正文字体
        c.setFont(font_name, 12 if font_loaded else 10)

        # 文本换行处理
        max_chars_per_line = int(content_width / (7 if font_loaded else 5))

        lines = text.split('\n')
        for line in lines:
            # 处理长行换行
            if len(line) > max_chars_per_line:
                for i in range(0, len(line), max_chars_per_line):
                    chunk = line[i:i + max_chars_per_line]
                    if y < margin:
                        c.showPage()
                        y = page_height - margin - 40
                        c.setFont(font_name, 12 if font_loaded else 10)
                    c.drawString(margin, y, chunk)
                    y -= line_height
            else:
                if y < margin:
                    c.showPage()
                    y = page_height - margin - 40
                    c.setFont(font_name, 12 if font_loaded else 10)
                c.drawString(margin, y, line)
                y -= line_height

        c.save()
        print(f"成功: 已创建 PDF 文件 - {file_path}")
        return True
    except Exception as e:
        print(f"错误: 写入 PDF 失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def write_pdf_from_json(file_path, json_data):
    """从 JSON 数据创建结构化 PDF 文档"""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print(f"请运行: {_install_hint()}")
        return False

    file_path = Path(file_path)

    try:
        # 尝试加载中文字体
        font_loaded = False
        chinese_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
        ]

        for font_path in chinese_fonts:
            if Path(font_path).exists():
                try:
                    pdfmetrics.registerFont(TTFont('Chinese', font_path, subfontIndex=0))
                    font_loaded = True
                    break
                except:
                    continue

        # 创建文档
        doc = SimpleDocTemplate(
            str(file_path),
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.5 * inch
        )

        elements = []
        styles = getSampleStyleSheet()

        if font_loaded:
            # 创建中文样式
            styles.add(ParagraphStyle(
                name='ChineseTitle',
                fontName='Chinese',
                fontSize=18,
                leading=22,
                spaceAfter=12,
                alignment=1
            ))
            styles.add(ParagraphStyle(
                name='ChineseHeading',
                fontName='Chinese',
                fontSize=14,
                leading=18,
                spaceAfter=6
            ))
            styles.add(ParagraphStyle(
                name='ChineseNormal',
                fontName='Chinese',
                fontSize=10,
                leading=14,
                spaceAfter=3
            ))
            title_style = styles['ChineseTitle']
            heading_style = styles['ChineseHeading']
            normal_style = styles['ChineseNormal']
        else:
            title_style = styles['Title']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']

        # 解析 JSON 数据
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # 添加标题
        if 'title' in json_data:
            elements.append(Paragraph(json_data['title'], title_style))
            elements.append(Spacer(1, 0.2 * inch))

        # 添加内容
        if 'content' in json_data:
            content = json_data['content']
            if isinstance(content, str):
                # 简单文本
                for line in content.split('\n'):
                    if line.strip():
                        elements.append(Paragraph(line, normal_style))
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        elements.append(Paragraph(item, normal_style))
                    elif isinstance(item, dict):
                        if 'heading' in item:
                            elements.append(Paragraph(item['heading'], heading_style))
                        if 'text' in item:
                            if isinstance(item['text'], list):
                                for line in item['text']:
                                    elements.append(Paragraph(line, normal_style))
                            else:
                                elements.append(Paragraph(item['text'], normal_style))
                        if 'table' in item:
                            table_data = item['table']
                            table = Table(table_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 12),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.1 * inch))

        doc.build(elements)
        print(f"成功: 已创建结构化 PDF 文件 - {file_path}")
        return True
    except Exception as e:
        print(f"错误: 写入 PDF 失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def merge_pdfs(output_path, input_paths):
    """合并多个 PDF 文件"""
    try:
        from pypdf import PdfMerger
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print(f"请运行: {_install_hint()}")
        return False

    try:
        merger = PdfMerger()
        for path in input_paths:
            path = Path(path)
            if path.exists():
                merger.append(str(path))
            else:
                print(f"警告: 文件不存在 - {path}")

        merger.write(str(output_path))
        merger.close()
        print(f"成功: 已合并 {len(input_paths)} 个文件到 {output_path}")
        return True
    except Exception as e:
        print(f"错误: 合并 PDF 失败 - {e}")
        return False


def split_pdf(input_path, output_prefix, pages=None):
    """分割 PDF 文件"""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print(f"请运行: {_install_hint()}")
        return False

    input_path = Path(input_path)
    if not input_path.exists():
        print(f"错误: 文件不存在 - {input_path}")
        return False

    try:
        reader = PdfReader(str(input_path))

        if pages:
            # 提取指定页面
            writer = PdfWriter()
            for page_num in pages:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])

            output_path = f"{output_prefix}_pages.pdf"
            with open(output_path, "wb") as output:
                writer.write(output)
            print(f"成功: 已提取页面 {pages} 到 {output_path}")
        else:
            # 每页单独保存
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                output_path = f"{output_prefix}_{i + 1}.pdf"
                with open(output_path, "wb") as output:
                    writer.write(output)

            print(f"成功: 已分割为 {len(reader.pages)} 个文件")

        return True
    except Exception as e:
        print(f"错误: 分割 PDF 失败 - {e}")
        return False


def fill_pdf_form(template_path, output_path, field_values):
    """填写 PDF 表单"""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print(f"请运行: {_install_hint()}")
        return False

    template_path = Path(template_path)
    if not template_path.exists():
        print(f"错误: 文件不存在 - {template_path}")
        return False

    try:
        reader = PdfReader(str(template_path))
        writer = PdfWriter()
        writer.append(reader)

        if isinstance(field_values, str):
            field_values = json.loads(field_values)

        if len(writer.pages) > 0:
            writer.update_page_form_field_values(writer.pages[0], field_values)

        writer.write(str(output_path))
        print(f"成功: 已填写表单并保存到 {output_path}")
        return True
    except Exception as e:
        print(f"错误: 填写表单失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="PDF 处理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 读取命令
    read_cmd = subparsers.add_parser("read", help="读取 PDF 文件")
    read_cmd.add_argument("file", help="PDF 文件路径")

    # 写入命令（简单文本）
    write_cmd = subparsers.add_parser("write", help="创建简单 PDF 文件")
    write_cmd.add_argument("file", help="输出 PDF 文件路径")
    write_cmd.add_argument("text", help="文本内容")
    write_cmd.add_argument("--title", default="PDF Document", help="PDF 标题")

    # 从 JSON 创建 PDF
    write_json_cmd = subparsers.add_parser("write_json", help="从 JSON 数据创建 PDF")
    write_json_cmd.add_argument("file", help="输出 PDF 文件路径")
    write_json_cmd.add_argument("data", help="JSON 数据")

    # 合并命令
    merge_cmd = subparsers.add_parser("merge", help="合并多个 PDF 文件")
    merge_cmd.add_argument("output", help="输出 PDF 文件路径")
    merge_cmd.add_argument("inputs", nargs="+", help="输入 PDF 文件路径（可多个）")

    # 分割命令
    split_cmd = subparsers.add_parser("split", help="分割 PDF 文件")
    split_cmd.add_argument("input", help="输入 PDF 文件路径")
    split_cmd.add_argument("prefix", help="输出文件前缀")
    split_cmd.add_argument("--pages", help="指定页面（如：1,3,5）")

    # 填写表单命令
    fill_cmd = subparsers.add_parser("fill_form", help="填写 PDF 表单")
    fill_cmd.add_argument("template", help="模板 PDF 文件路径")
    fill_cmd.add_argument("output", help="输出 PDF 文件路径")
    fill_cmd.add_argument("fields", help="表单字段值（JSON 格式）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 执行对应命令
    if args.command == "read":
        read_pdf(args.file)
    elif args.command == "write":
        write_pdf(args.file, args.text, args.title)
    elif args.command == "write_json":
        write_pdf_from_json(args.file, args.data)
    elif args.command == "merge":
        merge_pdfs(args.output, args.inputs)
    elif args.command == "split":
        pages = None
        if args.pages:
            pages = [int(p.strip()) for p in args.pages.split(',')]
        split_pdf(args.input, args.prefix, pages)
    elif args.command == "fill_form":
        fill_pdf_form(args.template, args.output, args.fields)


if __name__ == "__main__":
    main()
