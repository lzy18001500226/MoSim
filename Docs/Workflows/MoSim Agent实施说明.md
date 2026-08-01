# MoSim Agent 实施说明

## 当前实现（Codex CLI）

Model Studio 的第四栏现已使用仓库内源码构建的 Codex CLI：

```text
Model Studio (Julia/TyAppDesigner)
  -> agent_integration.jl
  -> 127.0.0.1:8765
  -> codex_cli_agent_server.py
  -> src/Agent/codex-main/codex-rs/target/release/codex
  -> 用户已登录的 GPT Provider
```

服务按用户首次提问启动，且只能绑定 `127.0.0.1`。它只接受项目构建出的
Codex 二进制；未构建时，Studio 回退到本地指引并显示构建与登录提示。实际权威
配置为 `Config/control_platform/model_studio_codex_cli_v1.toml`，构建说明和
许可证信息位于 `src/Agent/README.md`。

Codex CLI 不包含 GPT 模型权重。用户须在自己的 `CODEX_HOME` 完成 `codex login`
及 Provider 配置，不能将凭据放在项目、Studio 字段、日志或环境变量转发链中。
Bridge 会移除常见 API-key 环境变量后再启动 `codex exec`，从而避免模型通过只读
shell 查询继承到的密钥。

## 运行边界

Bridge 用 `codex exec --ignore-user-config --sandbox read-only -c 'approval_policy="never"'`
运行，并将子进程 stdin 关闭，避免 Codex 等待追加输入；系统提示词和沙箱共同限制为只读项目分析。它不得修改文件、启动
CheckModel/仿真/代码生成/编译，也不得发送 QGC、Gazebo、PX4、ROS、MAVROS、
飞控或电机命令。MWORKS、QGC 和 Gazebo/PX4 的执行与证据仍由用户在原生工具中
完成；模型可打开、静态源码或 UI 状态不能替代仿真或运行时结论。

旧的 `mworks_analysis_agent_server.py`、30 个直连 Responses 工具以及
`model_studio_agent_v1.toml` 仅保留为迁移测试材料，Studio 不再启动它们。

## 离线核对

```powershell
python Scripts\agent\codex_cli_agent_server.py --health
python -m unittest Scripts.agent.tests.test_codex_cli_agent_server
```

构建本身依赖 Rust 工具链；本机当前未检测到 `cargo`，因此本次只完成源码、脚本和
离线桥接合同验证，未将“Windows 二进制已构建”写入交付结论。

## 历史设计输入
