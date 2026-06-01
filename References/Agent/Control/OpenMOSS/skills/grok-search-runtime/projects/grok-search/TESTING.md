# grok-search — 测试与验收

## 1. 基础可用性
```bash
/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --query "Sam Altman 在 X 最新发了什么？请给出原文和链接" \
  --mode stateless
```
**验收**：输出为可解析 JSON，且 `sources` >= 2、每条含 `url/published_at/quote`。

## 2. 降级触发（模拟）
- 临时把 `--api-key` 改为无效值，确保 primary 失败后会尝试 fallback。
- 观察 `error` 或 `fallback_reason` 字段（加 `--with-meta`）。

```bash
/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --query "测试降级" \
  --api-key "bad-key" \
  --with-meta
```

## 3. 上下文回归
```bash
/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --thread-id "user:123" \
  --query "OpenAI CEO 最近在 X 发了什么？" \
  --mode auto

/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --thread-id "user:123" \
  --query "继续补充他最新一条的原文" \
  --mode auto
```
**验收**：第二次调用能带上上下文（见 `meta.context.include_context`）。
