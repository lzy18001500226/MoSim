# MoSim Agent 实施说明

## 当前实现

Model Studio 的第四栏现已接入本机只读 Agent：

```text
Model Studio (Julia/TyAppDesigner)
  -> agent_integration.jl
  -> 127.0.0.1:8765
  -> mworks_analysis_agent_server.py
  -> OpenAI Responses-compatible API + allowlisted read-only project tools
```

服务按用户首次提问启动，绑定到 `127.0.0.1`，密钥仅由启动 Studio 的
进程环境变量 `MOSIM_OPENAI_API_KEY` 提供。项目配置
`Config/control_platform/model_studio_agent_v1.toml` 不含密钥，记录端点、
模型、推理强度和只读限额。模型服务不可用或未设置密钥时，第四栏保留原有
本地指引，不会阻断其余 Studio 工作区。

## 已实现的工具边界

当前后端有 30 个实际可调用的只读工具，覆盖 Studio 上下文、FormalRunner
路由、七场景 Profile、控制器实现映射、G3 门禁和运行记录、MWORKS 文档、
Modelica 静态依赖、CSV 指标、代码生成交付目录和工作流推荐。每个工具只读取
项目内的 `Docs/`、`Config/`、限定 `Results/`、`Models/` 与
`src/control/codegen/` 路径。

其中轨迹图、对比图、热力图和报告图导出工具只校验输入并返回人工交接数据；
它们不会生成文件。求解器/MCP 诊断也只解读既有运行记录，不连接实时会话。

它不实现历史设计稿中的“自动执行工作流”或“运行/导出/部署”能力，也不把
模型可打开、静态源码或 UI 状态升级为仿真或运行时结论。MWORKS、QGC 和
Gazebo/PX4 仍需由用户在对应原生工具中确认和执行。

## 与初稿的关系

`MoSim Agent架构设计文档.md` 和 `MoSim Agent执行任务指令.md` 中的 Claude
示例、30 个规划工具和 Genie/Stipple 片段是初始设计输入，不是当前源码。
当前 Studio 已是 TyAppDesigner 应用，因此实施采用现有 UI、OpenAI
Responses-compatible API 和可离线测试的 Python 标准库回退服务。后续增加
工具前必须先补充实际数据源、路径白名单、单元测试和不执行边界。

## 模型配置

`model_studio_agent_v1.toml` 保留 `model`、`review_model` 与
`model_reasoning_effort`，用于集中管理供应方设置。当前版本只发送一轮主模型
请求；不会在未提示的情况下自动发起二次审查请求，因此 `review_model` 仅为未来
明确授权的审查流程预留。密钥始终只从 `MOSIM_OPENAI_API_KEY` 或兼容回退环境变量
读取，不进入仓库、请求日志或 Studio 配置文件。
