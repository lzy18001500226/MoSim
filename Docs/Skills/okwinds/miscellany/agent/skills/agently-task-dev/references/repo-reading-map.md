# Repo 阅读导航（从任务目标到文件）

> 目的：让 Coding Agent 在需要“核对能力实现细节”时，能快速定位到本仓库的权威来源（示例/源码）。

---

## 最快上手：docs_for_coding_agent（强烈推荐先看）

目录：`docs_for_coding_agent/agently-exmaples/step_by_step/`

- 基础配置/Prompt：`01-settings.py`、`02-prompt_methods.py`
- 结构化输出：`03-output_format_control.py`
- Prompt 模板（YAML/JSON）：`04-configure_prompt.py`
- Response/Result：`05-response_result.py`
- Streaming：`06-streaming.py`
- Tools：`07-tools.py`
- Chat history：`08-chat_history.py`
- Knowledge base（Chroma）：`09-knowledge_base.py`
- MCP：`10-mcp.py`（注意 path 坑，真实 server 在 `examples/mcp/`）
- TriggerFlow：`11-triggerflow-01_basics.py` ~ `11-triggerflow-12_dive_deep.py`
- Auto Loop（脚本）：`12-auto_loop.py`
- Auto Loop（服务化 FastAPI）：`13-auto_loop_fastapi/`
- 常见坑：`14-common_pitfalls.md`

---

## 源码核对：agently 包（能力的“事实来源”）

- 入口与 Agent 组合：`agently/base.py`
  - Agent 默认混入：ToolExtension / KeyWaiterExtension / AutoFuncExtension / ConfigurePromptExtension
- ModelRequest / Response / Streaming：`agently/core/ModelRequest.py`
- OpenAICompatible 适配层：`agently/builtins/plugins/ModelRequester/OpenAICompatible.py`
- 内置工具：`agently/builtins/tools/Search.py`、`agently/builtins/tools/Browse.py`
- ToolExtension（含 tool 自动判断与 tool_logs）：`agently/builtins/agent_extensions/ToolExtension.py`
- ConfigurePrompt：`agently/builtins/agent_extensions/ConfigurePromptExtension.py`
- KeyWaiter：`agently/builtins/agent_extensions/KeyWaiterExtension.py`
- AutoFunc：`agently/builtins/agent_extensions/AutoFuncExtension.py`
- TriggerFlow：`agently/core/TriggerFlow/*`
- KB：`agently/integrations/chromadb.py`
- ChatSession（可选扩展，不在默认 Agent）：`agently/builtins/agent_extensions/ChatSessionExtension.py`

