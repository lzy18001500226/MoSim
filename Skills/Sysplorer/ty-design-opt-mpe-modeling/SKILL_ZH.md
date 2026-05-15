> 本文件仅用于中文审核参考，实际任务执行请调用 SKILL.md

# DesignOptMpe - 参数设计、估计与优化

## Frontmatter 对照

- `name`: `ty-design-opt-mpe-modeling`
- `description`: 在 Sysplorer 内通过 DesignOptMpe 做参数设计、MPE 参数估计、优化与标定脚本、`run_script` 实验循环。不要用于与 DesignOptMpe 无关的 ModelingPy 通用 API 查询（请用 `get_api_document`），也不要用于纯 Modelica / Sysblock 建模范式任务（请先用 `ty-sysplorer-modeling-rules` 再进入领域技能）。
- `metadata.short-description`: DesignOptMpe parameter design, MPE, and optimization guidance
- `metadata.version`: `1.0.0`
- `metadata.managed-by`: `sysplorer-mcp`

## 适用范围

- **适用**：需要在 Sysplorer 内使用 DesignOptMpe Python 模块的 DesignOpt / MPE / 参数估计 / 优化任务，包括实验循环，以及与 Sysplorer 模型集成的任务。
- **不适用**：与 DesignOptMpe 无关的 ModelingPy 表层 API 查询（请用 `get_api_document`）；纯 Modelica / Sysblock 建模执行任务（请使用领域技能和 `modeling_path_router`）。

## 硬性规则

1. **会话优先**：任何会触碰 Sysplorer 的 `run_script` 之前，先执行 `session_manager(action="health" | "ensure")`。
2. **禁止**在脚本或工具中调用 `ClearAll` 或 `ChangeDirectory`；需要卸载时使用 `model_manager(action="unload")`。
3. DesignOptMpe **不**通过主 `Help()` 命名空间提供文档；应在 `run_script` 中使用 `import` + `ListFunctions()` / `help()`，并结合 `references/` 中的语料文本，以及语料库 `design_opt_mpe_api` 上的 `resources_retrieval`。

## 工具分工

| 需求 | 工具 / 动作 |
|------|-------------|
| Sysplorer 就绪检查 | `session_manager` |
| 执行估计 / 优化代码 | `call_code`（`mode="run_script"`） |
| 长文档、FAQ、API 表 | `resources_retrieval`，`sources` 包含 `design_opt_mpe_api` |
| 模型打开 / 保存 / 卸载 | `model_manager` |
| 检查 / 翻译 / 仿真受影响模型 | `check_model`、`translate_model`、`simulate_model` |

## 执行闭环

1. **澄清目标**：区分参数估计、设计探索还是优化；确认输入，如测量数据、参数边界等。
2. **拉取参考资料**：快速阅读 `references/参数估计使用说明.md` 了解操作流程；阅读 `DesignOptMpe.md` 了解 API 顺序；查看 demo notes 获取可运行示例。
3. **最小脚本**：导入模块，复现最小失败案例，并打印结构化状态。
4. **迭代**：使用 `call_code` 的 stdout/stderr 迭代调试；只有在最小闭环稳定后再扩大范围。

## RAG 提示

调用 `resources_retrieval(action="corpora")` 确认部署清单中 `design_opt_mpe_api` 的路径；当需要超出本技能内容的全文检索时，使用返回的索引路径执行 `action="search"`。
