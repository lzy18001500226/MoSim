# 无 Skill 基线（RED）记录

时间：2026-02-03  
目的：在“未加载本 skill”时，让一个 Coding Agent 在压力场景下给出方案，观察典型失误，用于反向驱动 skill 内容（TDD：RED→GREEN→REFACTOR）。

---

## 基线任务（对应压力场景 A）

要求（摘要）：
- 用 **Agently** 实现：Search→选 3 URL→并发 Browse→结构化总结
- 同时支持两类 streaming：用户 `delta` token + UI `instant`（结构化字段事件）
- 必须说明 env/proxy/key 与 fallback

---

## 观察到的典型失败模式（RED）

### 1) “绕开 Agently 能力”，改写成自研脚手架

基线输出倾向于：
- 自己引入 `duckduckgo-search`、`httpx`、`trafilatura`、`beautifulsoup4` 等堆栈；
- 自己设计 events JSONL；
- 自己实现 search/browse/summarize 模块；
而不是优先使用仓库已经提供且在 `agently-exmaples/step_by_step/07-tools.py`、`06-streaming.py` 中演示过的：
- `agently.builtins.tools.Search` / `Browse`
- `response.get_(async_)generator(type="delta"/"instant")`
- `TriggerFlow.get_runtime_stream(...)`

这会导致：无法“全面发挥 Agently 的所有能力”，也偏离用户要求的“主要依据 repo 文档+源码”。

### 2) 伪造/猜测 Agently API（高风险）

基线输出包含明显“猜 API 名称”的片段，例如：
```py
import Agently  # noqa: N812

agent = Agently.Agent()
...
async for chunk in agent.stream(...):
```

但在本仓库示例中，正确入口是：
- `from agently import Agently`
- `agent = Agently.create_agent()`
- `agent.input(...).get_generator(...)` / `get_async_generator(...)`

这类错误会导致用户按文档执行时直接报错。

### 3) 没有使用 Agently 的“结构化输出 + ensure_keys + instant streaming parse”

基线输出虽然声称支持 UI 结构化事件，但实现方式是“先拼 full_text 再 json.loads”，并用 `emit("summary.field", ...)` 推送字段；没有利用 Agently 的：
- `.output(schema)` 直接定义结构化 schema
- `ensure_keys` 提升结构稳定性
- `instant` / `streaming_parse` 在生成时按 path/wildcard_path 实时拿到字段节点

### 4) 与 repo 示例约定不一致（env/proxy）

基线输出更多使用标准 `HTTP_PROXY/HTTPS_PROXY`，而 repo 的示例工具类还常见：
- `Search(proxy="http://127.0.0.1:55758", backend="google", region="us-en")`

（这不一定错，但 skill 应该统一说明两类 proxy：Agently 内置 Search 的 proxy 与通用 HTTP 代理的区别。）

---

## 结论：Skill（GREEN）必须补齐的内容

为使测试从 RED 变 GREEN，这个 skill 需要：
1) 强制优先使用 repo 已有能力（Search/Browse、streaming、TriggerFlow、KB、configure prompt、MCP）。
2) 给出“版本差异最小化”的写法：围绕 `Agently.create_agent()`、`OpenAICompatible`、`.output()/ensure_keys`、`get_(async_)generator()` 的稳定 API 面。
3) 明确“不要自己重造轮子”的判断规则：什么时候用内置工具，什么时候才自研抓取/解析。
4) 提供可回归的检查表：实现是否覆盖了 capability-inventory 的每一项。

