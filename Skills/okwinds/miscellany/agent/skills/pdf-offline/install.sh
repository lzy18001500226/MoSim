#!/bin/bash
# PDF 技能依赖安装脚本

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS="$SKILL_DIR/requirements.txt"

echo "=================================================="
echo "PDF 技能依赖安装"
echo "=================================================="
echo ""

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

echo "检测到 Python 版本: $(python3 --version)"
echo ""

# 检查 pip3
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到 pip3，请先安装 pip"
    exit 1
fi

echo "开始安装依赖..."
echo ""

# 升级 pip
pip3 install --upgrade pip

# 安装 Python 依赖
pip3 install pypdf
pip3 install pdfplumber
pip3 install reportlab
pip3 install PyPDF2

echo ""
echo "=================================================="
echo "检查可选依赖..."
echo "=================================================="
echo ""

# 检查可选的系统级工具
if command -v pdftoppm &> /dev/null; then
    echo "✓ 已找到 pdftoppm (Poppler)"
else
    echo "⚠ 未找到 pdftoppm"
    echo "  如需 PDF 转图片功能，请安装 poppler-utils:"
    echo "  - macOS: brew install poppler"
    echo "  - Linux: sudo apt-get install poppler-utils"
fi

if command -v soffice &> /dev/null; then
    echo "✓ 已找到 soffice (LibreOffice)"
else
    echo "⚠ 未找到 soffice"
    echo "  如需 Office 转 PDF 功能，请安装 LibreOffice:"
    echo "  - macOS: brew install --cask libreoffice"
    echo "  - Linux: sudo apt-get install libreoffice"
fi

echo ""
echo "=================================================="
echo "安装成功！"
echo "=================================================="
echo ""
echo "已安装的 Python 依赖:"
pip3 list | grep -E "(pypdf|pdfplumber|reportlab|PyPDF2)" || true
echo ""
echo "使用方法："
echo "  读取 PDF:      python3 $SKILL_DIR/doc_utils.py read <文件路径>"
echo "  创建 PDF:      python3 $SKILL_DIR/doc_utils.py write <输出路径> <文本内容>"
echo "  从 JSON 创建:  python3 $SKILL_DIR/doc_utils.py write_json <输出路径> <JSON>"
echo "  合并 PDF:      python3 $SKILL_DIR/doc_utils.py merge <输出路径> <输入1> <输入2> ..."
echo "  分割 PDF:      python3 $SKILL_DIR/doc_utils.py split <输入路径> <输出前缀>"
echo "  填写表单:      python3 $SKILL_DIR/doc_utils.py fill_form <模板> <输出> <JSON>"
echo ""
