# Streaming UX Playbook（通用：快反馈 + 高性能 + 可回归）

目标：让用户“**尽快看到可感知的反馈**”（低 TTFC：time-to-first-character / time-to-first-change），同时避免把服务端/浏览器拖垮（事件风暴、频繁 DOM 更新、重复生成）。

> 本 playbook 是通用方法论，不绑定“写文章/大纲/段落”这类特定业务。你可以把它应用到任何“列表+逐项生成”“长文本生成”“多步工作流”场景。

---

## 1) 选择哪种流式：`instant` vs `delta`（决策树）

### 你要“结构化字段 + 用户可见流式”同时成立 → 优先 `instant`
- 典型：你要边生成边把字段放进 UI（标题/步骤/解释/最终结果），同时还要机器能理解字段。
- 做法：把用户可见文本放在 schema 的某个字段里，然后用 `instant` 取字段增量（delta）。

### 你要“最像打字机的 token 级” → 用 `delta`
- 典型：聊天式回复、长文逐字吐。
- 优点：体验最像 ChatGPT。
- 缺点：如果你的任务强依赖 schema，token 级阶段可能很难保持严格结构（通常做“先 token 流 → 最后再结构化校验/总结”）。

### Provider 本身不稳定/不流式 → 用“前端平滑 + 最终稿覆盖”
- 即使 provider 只会大块输出，你仍可：
  - 服务端发较粗粒度 delta
  - 前端用打字机动画把 burst 变得更顺滑
  - 最终用 `final`/`item_final` 覆盖纠偏

---

## 2) 事件协议（可复用的最小规范）

### 2.1 SSE envelope（固定外壳）
建议每条 SSE 的 `data:` 都是一条 JSON（单行、无换行，便于解析）：

```json
{ "type": "<event_type>", "data": { ... }, "seq": 123 }
```

推荐字段（可选但很实用）：
- `seq`：递增序号（客户端可检测乱序/丢包）
- `ts`：毫秒时间戳（排查卡顿）
- `trace_id`：把一次请求的所有事件串起来

### 2.2 通用的“逐项生成”事件族
适用于：列表项、章节、步骤、分块内容、每个子任务。

- `item_start`: `{ "index": 0, "label": "..." }`
- `item_delta`: `{ "index": 0, "delta": "..." }`
- `item_final`: `{ "index": 0, "text": "..." }`

关键原则：
- `item_delta` 是 **纯文本增量**（delta），不要混入 event 对象 repr、dict repr、日志行。
- `item_final` 是 **最终定稿**（服务端认为最可靠的版本）。客户端用它覆盖/纠偏，保证一致性。

### 2.3 工作流进度事件
适用于：TriggerFlow / 多步请求 / RAG pipeline。

- `status`: `"start" | "retrieval" | "planning" | "writing" | "checking" | "done" | ...`
- 规则：**先发 status 再做耗时动作**（降低“空白等待感”）。

---

## 3) 服务端实现要点（性能与正确性）

### 3.1 不要把“事件对象”当字符串拼到正文里
在 `instant` 流里，chunk 可能是：
- dict（partial data）
- 事件对象（常见字段：`path` / `wildcard_path` / `delta` / `value` / `full_data`）

强约束：
- 不要 `str(event)` 当正文增量（会把 `path='...'` 之类混进 UI）。
- 对 `delta/value/full_data` 做 **类型守卫**（str/dict/list）。
- 对“流式转发层”（例如把 TriggerFlow runtime stream 变成 SSE）也做类型守卫：
  - runtime stream **可能产出原生对象（dict/list/自定义对象）**，不要直接 `str(line)` 就塞进 SSE。
  - 只转发你定义的**单行 JSON envelope**（包含 `type`），其余丢弃或转为内部日志（不要污染用户通道）。

### 3.2 delta 提取策略（通用）
推荐实现一个“提取纯文本 delta”的函数：
- 情况 A：event 自带 `delta` 且路径命中目标字段 → 直接用
- 情况 B：event 给的是 growing full string（`value`）→ 用 prefix-diff 计算 delta
- 情况 C：`value/full_data` 是 dict/list → 只提你需要的字段，不要 `str(dict)`

### 3.3 节流/批处理（必须）
如果按 token 每次 `send()`：
- 连接数上来后，CPU 会被 JSON dump + ASGI send + flush 吃掉
- 浏览器也会被频繁 DOM 更新拖慢

建议做两级平滑：
- **服务端 batch**：累计到 `N` 字符或 `T` ms 才发一次 `item_delta`
- **前端 drain**：每帧吐 `K` 字符（rAF）把 burst 平滑成“打字机”

推荐“起始默认值”（请保留可配置，不要写死）：
- 服务端：`N=20~50 chars`，`T=30~80ms`
- 前端：`K=6~12 chars/frame`（60fps 下约 360~720 chars/s）

### 3.4 避免“双重生成”导致同一段两版文本
常见坑：
1) 你一边做流式，一边因为“取不到最终结果”又 fallback `.start()` 再跑一遍
2) 于是同一段出现两版内容（且略有差异）

通用做法：
- 用 `streaming_succeeded` 标记：只有当流式阶段完全没产出时才 fallback。
- 或者：流式期间同时累计 full text（基于 delta 聚合），最终直接以聚合结果作为 `item_final`。

### 3.5 SSE header 与代理缓冲
如果前面有 Nginx/网关，可能会缓冲 SSE。常见做法（按平台选择）：
- `Cache-Control: no-cache`
- `Connection: keep-alive`
- `X-Accel-Buffering: no`（Nginx）

---

## 4) 前端实现要点（不卡顿、不乱、好纠偏）

### 4.1 不要每个 delta 都重建 DOM
推荐：
- 为每个 index 维护一个 entry：`{ textBuffer, pendingText, finalized }`
- delta 只追加到 `pendingText`
- rAF 循环每帧从 `pendingText` 取 `K` 字符追加到 `textBuffer` 并更新一次 text node

### 4.2 `item_final` 到达后要“覆盖并冻结”
避免：
- final 到了还继续吃 delta（会把 UI 搞乱）
- 或者 final 另外新建一段（导致重复显示）

建议：
- `item_final` 用覆盖策略：`textBuffer = finalText; pendingText = ""`
- 把该 index 标记 finalized，忽略后续 delta

### 4.3 段间卡顿的 UX 处理
只要你发 `item_start`：
- UI 立刻出占位卡片 + spinner（用户有即时反馈）
- 后续 delta 再填充内容

---

## 5) 回归测试建议（通用、可复用、不过拟合）

### 5.1 离线 stub（必须）
离线测试不追求“写得好”，只追求“链路正确 + 协议正确 + 不回归”：
- 若出现 `item_delta`：
  - `delta` 必须是字符串
  - `delta` 不得包含明显的 repr 垃圾（如 `wildcard_path=`, `full_data=`, `path=` 等）
- 若出现 `item_final`：
  - 同一 `index` 的 final 不应重复（最多一次）
- 对 list 流式：
  - `index` 应递增或可比较（避免乱序导致 UI 乱）
 - 对 SSE：
   - 每条 `data:` 必须是可 `json.loads` 的 JSON（禁止 Python repr/非 JSON 垃圾进入用户通道）

### 5.2 真模型集成（可选）
只做“结构与连通性”断言：
- 能拿到至少一个 delta 或 final
- 最终结果存在且非空
- 不做逐字匹配（避免模型波动导致测试不稳定）
