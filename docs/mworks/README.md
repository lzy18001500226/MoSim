# MWORKS 资料库索引

本目录用于存放从 `MWORKS高校星火计划资料包` 中筛选、索引和转换出来的项目相关资料，供 Codex/Agent 后续查询。

## 主要入口

| 文件 | 作用 |
|---|---|
| `scan/scan_summary.md` | 扫描摘要、分类统计和下一步建议 |
| `scan/relevant_index.md` | 按相关性排序的资料清单 |
| `scan/relevant_files.csv` | 机器可读索引，便于脚本二次处理 |
| `scan/categories/sysplorer_modeling.md` | Sysplorer、Modelica、建模仿真相关资料 |
| `scan/categories/syslab_analysis.md` | Syslab、Julia、指标计算、绘图相关资料 |
| `scan/categories/quadrotor_uav.md` | 智能无人系统、挑战赛、无人车/无人机相关资料 |
| `extracted/` | 从 `.mo/.jl/.py/.m/.txt/.csv` 等文件生成的 Markdown 摘录 |

## 使用建议

Codex 查询资料时优先顺序：

```text
1. docs/mworks/scan/scan_summary.md
2. docs/mworks/scan/relevant_index.md
3. docs/mworks/scan/categories/*.md
4. docs/mworks/extracted/*.md
5. 原始资料包中的 PDF 或模型文件
```

## PDF 说明

当前环境未检测到 `pdftotext`、`pypdf`、`PyPDF2`、`pdfplumber` 或 `fitz`，因此 PDF 目前主要生成索引条目和待转换 Markdown 占位。后续如安装 PDF 文本提取工具，可重新运行：

```bash
python scripts/scan_mworks_docs.py --top 180 --extract-limit 120
```

脚本会自动尝试提取 PDF 前 5 页文本。

