# MCP Safety Checklist（工具接入的“默认安全”基线）

目的：把 “`agent.use_mcp(...)` = 运行外部代码” 这件事落到可执行检查表，降低供应链/权限/数据泄露风险。

适用范围：
- 任何 stdio MCP server（Python/Node/Go/二进制都算）
- 任何把 MCP 暴露给 LLM 自动调用（ToolManager）的场景

---

## 1) 允许列表（Allowlist）是默认

最低要求：
- 工程里维护一个**允许列表**（路径/仓库/版本），只允许列表内的 server 被接入。
- 不接受“用户粘贴一个 `mcp_server.py` 就运行”的模式。

建议写法（示例，按你项目实际调整）：
- `mcp_servers/README.md`：列出 server 名称、用途、来源、版本、运行命令
- `MCP_ALLOWLIST = {...}`：在代码里用常量控制可用工具集合

---

## 2) 来源与版本（Provenance & Pinning）

检查项：
- [ ] 来源明确（repo URL / 维护者 / commit 或 release）
- [ ] 版本固定（git commit hash / tag / lockfile）
- [ ] 依赖固定（Node: lockfile；Python: requirements/uv.lock/poetry.lock）

风险提示：
- `pip install -U`、`npm install latest` 这类浮动依赖，不适合 MCP server。

---

## 3) 权限与隔离（Least Privilege）

检查项：
- [ ] 最小权限运行（不要 sudo）
- [ ] 只给必要的文件权限（读写目录最小化）
- [ ] 明确网络策略（能否联网？能访问哪些域名？）
- [ ] 明确环境变量策略（哪些 env 会传给 server？默认不传 secrets）

建议：
- 优先在容器/沙箱/受限用户下运行 MCP server。

---

## 4) 数据与隐私（Data Handling）

检查项：
- [ ] 明确 server 可能接触到的敏感数据：prompt、代码、日志、文件内容
- [ ] 日志不打印 secrets（API key/token/cookie）
- [ ] 不要求用户“粘贴完整配置/完整私钥/完整日志”到对话里

---

## 5) 工具面收敛（Tool Surface Area）

检查项：
- [ ] 工具数量尽量小（按阶段启用：Search → Browse → Summarize）
- [ ] 每个 tool 的 schema 清晰（参数类型、必填项、限制）
- [ ] 为危险工具加额外 guardrail（确认、allowlist、只读模式）

---

## 6) 运行时守护（Runtime Guardrails）

建议：
- 超时：每次 tool call 有最大执行时间
- 限流：并发上限、重试策略
- 输出规范：对外输出必须是 JSON envelope（避免 repr 污染）

---

## 7) 复审与回归（Review & Regression）

最低要求（推荐加入 CI）：
- [ ] MCP server 的启动命令可重复
- [ ] 基础“握手/列工具/调用一次”可回归
- [ ] 若 server 升级：必须更新 allowlist 版本，并过一次 review

