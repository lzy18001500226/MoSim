# 面向复杂任务场景的四旋翼无人机自适应鲁棒位姿控制与智能仿真验证系统

本项目面向 A8 四旋翼无人机位姿控制系统设计优化赛题，基于 MWORKS.Sysplorer、Sysblock 和 Syslab 构建可复现的仿真验证工程。

核心闭环：

```text
复杂任务场景
→ 可跟踪轨迹规划
→ 自适应鲁棒位姿控制
→ 安全/故障降级
→ 编队协同
→ Syslab/MCP 自动评估
→ 三维回放、报告和视频素材
```

## 快速入口

| 内容 | 路径 |
|---|---|
| Agent 操作规范 | `AGENTS.md` |
| 设计文档总览 | `Design/README.md` |
| 用户手册 | `docs/user_manual.md` |
| 仿真分析报告 | `docs/simulation_report.md` |
| 文档索引 | `docs/index/doc_index.md` |
| API 索引 | `docs/index/api_index.md` |
| 工作流索引 | `docs/index/workflow_index.md` |
| 预提交检查 | `workflows/pre_submit_check.md` |

## 目录约定

```text
controllers/   控制器模块和参数
planners/      路径规划与轨迹生成模块
scenarios/     场景和扰动配置
scripts/       指标、绘图、批量实验脚本
docs/          用户手册、报告、索引和图件
workflows/     可复现操作流程
tests/         单元测试、烟雾测试和回归测试
results/       仿真结果和报告素材，按实际输出创建子目录
references/    外部资料和官方原始资料包
```

不要为了占位提前创建空目录；只有放入配置、脚本、模型、结果或说明文件时再创建对应目录。官方 MWORKS 原始资料包统一放在 `references/MWORKS高校星火计划资料包/`，Agent 查询时优先使用 `docs/mworks/converted/` 和索引文件。

## 当前实现主线

```text
P0：官方 PID baseline + 改进 PID + 数据导出 + 指标计算 + 三维回放素材
P1-A：MPC/NMPC-INDI-L1 主控制链路 + 扰动识别 + 模式切换
P1-B：Safety Filter + 电机故障注入 + 容错/降级策略
P2：可跟踪性感知路径规划 + 三机协同任务 + 健康度评分 + MCP 批量评估
```

## QA 检查

```bash
python scripts/qa_check.py
```

`qa_check.py` 只检查工程骨架、关键文档和 MCP wrapper 可见性，不验证 MWORKS 模型正确性。
