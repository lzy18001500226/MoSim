# 用户手册

本文档记录项目安装、配置、运行仿真和复现实验的步骤。当前为骨架版本，后续随模型和脚本实现逐步补充截图、参数表和常见问题。

## 1. 环境要求

```text
MWORKS.Sysplorer 2026
MWORKS.Sysblock 2026
MWORKS.Syslab 2026
Codex MCP: syslab, sysplorer_mcp
Python 3
Julia / Syslab 运行环境
```

## 2. 快速检查

在项目根目录运行：

```bash
python scripts/qa_check.py
```

## 3. 基本运行流程

```text
1. 选择场景 scene_id
2. 选择控制器 controller_id
3. 使用 Sysplorer/MCP 打开模型
4. 执行 check_model
5. 执行 simulate_model
6. 使用 result_manager 导出结果
7. 使用 Syslab 计算 metrics 和 figures
8. 保存 summary、mcp_log 和视频素材
```

详细流程见：

```text
workflows/run_simulation.md
workflows/calc_metrics.md
workflows/pre_submit_check.md
Design/08_仿真指标与自动评估.md
```

## 4. 结果目录

```text
results/raw/       原始仿真结果
results/metrics/   指标表、健康度评分
results/figures/   图表和报告素材
```

