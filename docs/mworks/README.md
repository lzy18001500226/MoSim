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
| `converted/转换索引.md` | 高价值 PDF 转换索引 |
| `converted/sysplorer/` | Sysplorer、Modelica、Syslab/Sysplorer 集成资料 |
| `converted/syslab/` | Syslab 控制系统工具箱资料 |
| `converted/control/` | 系统辨识、鲁棒控制资料 |
| `converted/optimization/` | 参数估计与优化资料 |
| `converted/api/` | 外部接口、脚本和函数调用资料 |
| `converted/challenge/` | 智能无人系统挑战赛规则与培训资料 |

## 使用建议

Codex 查询资料时优先顺序：

```text
1. docs/mworks/scan/scan_summary.md
2. docs/mworks/scan/relevant_index.md
3. docs/mworks/scan/categories/*.md
4. docs/mworks/converted/转换索引.md
5. docs/mworks/converted/**/*.md
6. 原始资料包中的 PDF 或模型文件
```

## PDF 说明

已将第一批 P0/P1/P2 高价值 PDF 转换到 `docs/mworks/converted/`。当前 15 份目标文档均已通过 MinerU 精准解析生成 Markdown，并同步保存各自的 `_images/` 图片目录。

转换结果可用于关键词检索、流程定位、截图查看和 Agent 实现参考，但以下内容仍需结合原 PDF 或 MCP 官方文档复核：

- API 名称、函数参数和命令大小写；
- 公式、表格、代码块；
- 截图中的菜单路径和图形化操作步骤；
- 需要高保真版式的报告素材。

重新扫描资料包：

```bash
python scripts/scan_mworks_docs.py --top 180
```

默认不再生成 `docs/mworks/extracted/`，因为该目录主要是自动扫描碎片，和 `converted/` 重复且噪声较多。如确实需要临时摘录文本文件，可显式运行：

```bash
python scripts/scan_mworks_docs.py --top 180 --extract-snippets --extract-limit 120
```

重新生成 PDF Markdown 兜底转换：

```bash
uv run --with pymupdf python scripts/convert_mworks_pdfs.py --method pymupdf
```

使用 MinerU 精准解析逐个转换重点 PDF：

```bash
uv run --with pymupdf --with requests python scripts/convert_mworks_pdfs.py --method mineru --priority P0
```

MinerU 转换只从环境变量 `MINERU_API_TOKEN` 读取 Token，不要把 Token 写入仓库文件。若下载结果 zip 失败，可加：

```bash
--continue-on-download-error
```

脚本会把 URL 写入 `docs/mworks/tmp/mineru/pending_downloads.md`，后续可手动下载后用 `--import-mineru-result` 导入。
