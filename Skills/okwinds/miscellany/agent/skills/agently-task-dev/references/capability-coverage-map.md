# Capability Coverage Map（CAP-* → skill 落点）

目的：把 `capability-inventory.md` 的每个 CAP-* 映射到“应该看哪里/怎么验收”，让能力覆盖变成可执行 checklist。

说明：
- 这是“索引”，不是重复讲解。细节见对应 reference 或 `SKILL.md` 章节。
- 不要求每个任务都用到全部 CAP-*；但要求“用不到的要说明原因与替代方案”，并能通过回归测试证明交付没问题。

---

## A. Settings / Debug / 插件

- `CAP-SETTINGS-GLOBAL` / `CAP-SETTINGS-INSTANCE` / `CAP-DEBUG-MAPPING` / `CAP-DEFAULT-SETTINGS` / `CAP-PLUGIN-MGR`
  - 参考：`references/settings-and-prompt-structure.md`
  - 验收：能解释全局/实例覆盖关系；debug 不污染用户输出；配置可通过 env 切换

---

## B. Prompt 体系（slots/mappings）

- `CAP-AGENT-VS-REQUEST` / `CAP-PROMPT-SLOTS` / `CAP-QUICK-METHODS` / `CAP-MAPPINGS`
  - 参考：`references/settings-and-prompt-structure.md`
  - 验收：prompt 不靠拼字符串；上下文通过 `info`/`instruct`/`output` 结构化传递

---

## C. 结构化输出（schema/ensure_keys）

- `CAP-OUTPUT-SCHEMA` / `CAP-ENSURE-KEYS` / `CAP-RETRIES` / `CAP-ORDER-MATTERS` / `CAP-DATA-OBJECT`
  - 参考：`SKILL.md` Step 2；`references/testing-strategy.md`；`references/settings-and-prompt-structure.md`（顺序建议）
  - 验收：离线 stub 下 ensure_keys 可稳定通过；字段类型正确

---

## D. Streaming（delta/instant/specific）

- `CAP-STREAM-DELTA` / `CAP-STREAM-INSTANT` / `CAP-STREAM-STREAMING-PARSE` / `CAP-STREAM-SPECIFIC` / `CAP-STREAM-CANCEL-LOGS`
  - 参考：`SKILL.md` Step 3；`references/streaming-ux-playbook.md`；`references/advanced-integrations.md`
  - 验收：SSE/终端流式可工作；delta 不含 repr；每条 SSE `data:` 可 `json.loads`

---

## E. Response/Result 消费

- `CAP-RESULT-*` / `CAP-CONCURRENCY`
  - 参考：`references/response-result-cheatsheet.md`
  - 验收：不重复请求；并发时可控；能拿到 meta/extra（如 tool_logs）

---

## F. Tools（内置与自定义）

- `CAP-TOOLS-*`
  - 参考：`SKILL.md` Step 4；`references/common-pitfalls.md`
  - 验收：分阶段启用工具；tool schema 清晰；必要时可从 extra/tool_logs 审计

---

## G. MCP

- `CAP-MCP-USE` / `CAP-MCP-PATHING`
  - 参考：`SKILL.md` Step 9；`references/advanced-integrations.md`
  - 验收：路径可复现；CI/部署环境不靠手工路径

---

## H. Configure Prompt

- `CAP-CONFIGURE-PROMPT-*`
  - 参考：`references/configure-prompt-guide.md`
  - 验收：prompt 可文件化管理；roundtrip 可用；关键模板有回归测试

---

## I/J. AutoFunc / KeyWaiter

- `CAP-AUTOFUNC*` / `CAP-KEYWAITER*`
  - 参考：`SKILL.md` Step 5/6；`references/response-result-cheatsheet.md`
  - 验收：能把函数签名转成结构化输出；能按 key 完成触发处理

---

## K. Chat History / Chat Session

- `CAP-CHAT-HISTORY-*` / `CAP-CHAT-SESSION-*`
  - 参考：`references/advanced-integrations.md`；`references/common-pitfalls.md`
  - 验收：history 不泄露；session 记录策略明确且有回归测试（如启用）

---

## L. Knowledge Base（Chroma）

- `CAP-KB-*`
  - 参考：`SKILL.md` Step 8；`references/common-pitfalls.md`（不要每次重建）
  - 验收：embedding/chat agent 分离；add/query 可回归

---

## M. TriggerFlow

- `CAP-TF-*`（包括 blueprint/side_branch/runtime stream/result）
  - 参考：`SKILL.md` Step 7/10；`references/advanced-integrations.md`；`references/streaming-ux-playbook.md`
  - 验收：能终止（stop_stream/max_steps）；runtime_data 不泄漏；服务化时协议边界干净

---

## N. Attachment

- `CAP-ATTACHMENT`
  - 参考：`references/advanced-integrations.md`
  - 验收：多模态输入路径明确；回归测试验证“链路正确”

