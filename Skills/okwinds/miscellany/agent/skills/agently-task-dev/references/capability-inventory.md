# Agently 能力清单（以不遗漏为准）

> 目的：把 Agently 的“能力面”列成可勾选的 TODO，作为写 skill 的验收标准与回归基线。
>
> 来源：`docs_for_coding_agent/agently-exmaples/*` 的示例 + 上一级仓库 `agently/` 源码（`AgentlyMain`, `ModelRequest`, `ToolExtension`, `TriggerFlow`, `integrations/chromadb.py` 等）。

---

## A. 初始化与配置（Settings / Debug / 插件）

- [ ] **CAP-SETTINGS-GLOBAL**：全局设置 `Agently.set_settings(...)`（例如 `OpenAICompatible`、`runtime.httpx_log_level`、`debug`）。
- [ ] **CAP-SETTINGS-INSTANCE**：实例级 `agent.set_settings(...)` 覆盖/继承全局设置。
- [ ] **CAP-DEBUG-MAPPING**：`debug=True/False` 的映射（show_model_logs/show_tool_logs/show_trigger_flow_logs/httpx_log_level）。
- [ ] **CAP-DEFAULT-SETTINGS**：理解 `_default_settings.yaml` 的关键项：prompt title mapping、response.streaming_parse、runtime flags、storage.db_url。
- [ ] **CAP-PLUGIN-MGR**：插件体系（PromptGenerator / ResponseParser / ModelRequester / ToolManager）是可替换/可配置的能力面（skill 需要告诉 agent：尽量用默认插件面向用户）。

对应示例：
- `agently-exmaples/step_by_step/01-settings.py`

---

## B. Prompt 体系（Agent / Request / Prompt slots）

- [ ] **CAP-AGENT-VS-REQUEST**：`Agently.create_agent()` 与 `Agently.create_request()` 的差异与使用场景。
- [ ] **CAP-PROMPT-SLOTS**：常用 slot：`system/developer/info/tools/action_results/instruct/examples/input/output/attachment/options/chat_history`。
- [ ] **CAP-QUICK-METHODS**：快捷方法：`.role()/.input()/.info()/.instruct()/.output()/.options()/.attachment()`。
- [ ] **CAP-MAPPINGS**：占位符 mappings（`${var}`）的使用与注意事项。

对应示例：
- `agently-exmaples/step_by_step/02-prompt_methods.py`

---

## C. 结构化输出（Output schema / ensure_keys / retries）

- [ ] **CAP-OUTPUT-SCHEMA**：`.output(schema)` 定义结构化输出（嵌套 dict/list/tuple type+desc）。
- [ ] **CAP-ENSURE-KEYS**：`ensure_keys` + `key_style(dot/slash)` 保证字段齐全。
- [ ] **CAP-RETRIES**：`max_retries` / `raise_ensure_failure` 的容错策略。
- [ ] **CAP-ORDER-MATTERS**：输出字段顺序影响稳定性（CoT-like control 的技巧）。
- [ ] **CAP-DATA-OBJECT**：`get_data_object()`（Pydantic model）用于强类型校验（如可用）。

对应示例：
- `agently-exmaples/step_by_step/03-output_format_control.py`
- `agently-exmaples/step_by_step/05-response_result.py`

---

## D. Streaming（delta / instant / streaming_parse / specific）

- [ ] **CAP-STREAM-DELTA**：`get_generator(type="delta")` / `get_async_generator(type="delta")` 用户可见 token 流。
- [ ] **CAP-STREAM-INSTANT**：`instant` 事件流（结构化字段路径 + delta + is_complete）。
- [ ] **CAP-STREAM-STREAMING-PARSE**：`streaming_parse`（与 `instant` 的兼容/差异，path style dot/slash）。
- [ ] **CAP-STREAM-SPECIFIC**：`specific` 事件过滤（reasoning_delta/delta/tool_calls/done 等）。
- [ ] **CAP-STREAM-CANCEL-LOGS**：`response.cancel_logs()` 或 `$log.cancel_logs` 相关（减少 console 噪音）。

对应示例：
- `agently-exmaples/step_by_step/06-streaming.py`

---

## E. Response/Result 消费（text/data/meta/extra）

- [ ] **CAP-RESULT-TEXT**：`response.result.get_text()` / `async_get_text()`
- [ ] **CAP-RESULT-DATA**：`get_data()` / `async_get_data()`（parsed/original/all）
- [ ] **CAP-RESULT-META**：`get_meta()`（tokens/model 等）
- [ ] **CAP-RESULT-EXTRA**：`full_result_data["extra"]`（例如工具调用日志 tool_logs）
- [ ] **CAP-CONCURRENCY**：`asyncio.gather` 并发多个请求（同一 agent 多请求）

对应示例：
- `agently-exmaples/step_by_step/05-response_result.py`
- `agently-exmaples/step_by_step/07-tools.py`（extra/tool_logs）

---

## F. Tools 工具与自动工具调用（ToolExtension / built-in tools）

- [ ] **CAP-TOOLS-REGISTER**：`@agent.tool_func` / `agent.register_tool(...)` 注册工具。
- [ ] **CAP-TOOLS-USE**：`agent.use_tools([...])`（用函数名或 tool 名字字符串）。
- [ ] **CAP-TOOLS-BUILTIN-SEARCH**：`agently.builtins.tools.Search`（ddgs>=9.10.0，proxy/backend/region/news/wikipedia/arxiv）。
- [ ] **CAP-TOOLS-BUILTIN-BROWSE**：`agently.builtins.tools.Browse`（httpx+bs4 简单抽取，proxy/headers）。
- [ ] **CAP-TOOLS-MULTI-STAGE**：Search→挑 URL→并发 Browse→总结 的分阶段范式。
- [ ] **CAP-TOOLS-AUTO-JUDGE**：ToolExtension 的 request_prefix：模型可先判断是否需要 tool、自动调用并写入 `action_results`。
- [ ] **CAP-TOOLS-LOGS**：tool_logs 进入 result.extra（以及 runtime.show_tool_logs 的 console 输出）。

对应示例：
- `agently-exmaples/step_by_step/07-tools.py`

---

## G. MCP（把外部工具接入 ToolManager）

- [ ] **CAP-MCP-USE**：`agent.use_mcp(...)` / `async_use_mcp(...)` 接入 stdio MCP server（ToolManager 层实现）。
- [ ] **CAP-MCP-PATHING**：MCP server 路径选择与工程组织（避免示例中 path 缺失问题）。

对应示例：
- `agently-exmaples/step_by_step/10-mcp.py`（注意该文件在本 repo 内路径有坑）
- 真实 server：仓库根目录 `examples/mcp/cal_mcp_server.py`

---

## H. Configure Prompt（YAML/JSON Prompt 模板）

- [ ] **CAP-CONFIGURE-PROMPT-YAML**：`agent.load_yaml_prompt(path_or_content, mappings, prompt_key_path)`
- [ ] **CAP-CONFIGURE-PROMPT-JSON**：`agent.load_json_prompt(...)`（json5 支持）
- [ ] **CAP-CONFIGURE-PROMPT-ALIAS**：`.alias` 机制（映射到 agent 方法）
- [ ] **CAP-CONFIGURE-PROMPT-ROUNDTRIP**：`get_yaml_prompt()` / `get_json_prompt()` 做 roundtrip

对应示例：
- `agently-exmaples/step_by_step/04-configure_prompt.py`

---

## I. AutoFunc（把“函数签名 + docstring”变成 LLM 函数）

- [ ] **CAP-AUTOFUNC**：`agent.auto_func(func)`：读取 docstring 作为 instruct；读取返回类型注解作为 output schema；支持 sync/async。
- [ ] **CAP-AUTOFUNC-LIMITS**：不能装饰 generator/async generator。

对应源码：
- `agently/builtins/agent_extensions/AutoFuncExtension.py`

---

## J. KeyWaiter（按 key 完成触发回调/并发）

- [ ] **CAP-KEYWAITER-GET**：`agent.get_key_result(key)` / `async_get_key_result`：等某个 output key 完成即返回。
- [ ] **CAP-KEYWAITER-WAIT-KEYS**：`wait_keys(keys)` / `async_wait_keys(keys)`：流式产出 `(path, value)`。
- [ ] **CAP-KEYWAITER-HANDLERS**：`when_key(key, handler)` + `start_waiter()`：key 完成触发回调（并发 gather）。

对应源码：
- `agently/builtins/agent_extensions/KeyWaiterExtension.py`

---

## K. Chat History / Chat Session（历史管理与会话录制）

- [ ] **CAP-CHAT-HISTORY-BASIC**：`set_chat_history/add_chat_history/reset_chat_history`（Agent.py）。
- [ ] **CAP-CHAT-SESSION-ACTIVATE**：`activate_chat_session(chat_session_id)`（自动维护 session chat_history）。
- [ ] **CAP-CHAT-SESSION-RECORD**：record_input_paths / record_output_paths + mode（first/all）把关键输入输出写入 session runtime。

对应示例：
- `agently-exmaples/step_by_step/08-chat_history.py`

对应源码：
- `agently/builtins/agent_extensions/ChatSessionExtension.py`（默认 Agent 未混入，属于可选扩展）

---

## L. Knowledge Base（ChromaDB integration）

- [ ] **CAP-KB-CHROMA-COLLECTION**：`ChromaCollection(collection_name, embedding_agent=...)`。
- [ ] **CAP-KB-ADD**：`.add([{document, metadata, id?}])` + embedding_function（可由 agent 提供）。
- [ ] **CAP-KB-QUERY**：`.query(query, top_n, where, where_document, distance)`。
- [ ] **CAP-KB-QUERY-EMBEDDINGS**：`.query_embeddings({query: embedding})`。

对应示例：
- `agently-exmaples/step_by_step/09-knowledge_base.py`

---

## M. TriggerFlow（工作流编排 / 并发 / 分支 / runtime stream）

- [ ] **CAP-TF-BASICS**：`TriggerFlow().to(handler).end()`，`start()/start_execution()`。
- [ ] **CAP-TF-WHEN**：`when(event)` 触发分支。
- [ ] **CAP-TF-BRANCHING**：if/when/match_case 等分支过程（见 process）。
- [ ] **CAP-TF-CONCURRENCY**：`batch/for_each` 并发与限流。
- [ ] **CAP-TF-DATA-RUNTIME**：`TriggerFlowEventData.get_runtime_data/set_runtime_data` 维护执行期状态。
- [ ] **CAP-TF-DATA-FLOW**：`flow_data`（全局） vs `runtime_data`（执行期）及其差异/风险。
- [ ] **CAP-TF-RUNTIME-STREAM**：`put_into_stream/stop_stream` + `get_runtime_stream(timeout=None)` 推进 UI/服务。
- [ ] **CAP-TF-BLUEPRINT**：`TriggerFlowBluePrint` 的 save/load（可复用 flow 结构）。
- [ ] **CAP-TF-SIDE-BRANCH**：side_branch + `____` 分隔。
- [ ] **CAP-TF-RESULT**：`set_result`、`wait_for_result` 的语义（如何让 flow 输出稳定）。

对应示例：
- `agently-exmaples/step_by_step/11-triggerflow-*`
- `agently-exmaples/step_by_step/12-auto_loop.py`
- `agently-exmaples/step_by_step/13-auto_loop_fastapi/*`

---

## N. 附件/多模态（Attachment / rich_content）

- [ ] **CAP-ATTACHMENT**：`.attachment(...)` slot 触发 OpenAICompatible 的 `rich_content=True`（用于 VLM/多模态请求）。

对应源码：
- `agently/core/Agent.py`（attachment 方法）
- `agently/builtins/plugins/ModelRequester/OpenAICompatible.py`（检测 attachment）

