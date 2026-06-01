# grok-search — 使用说明

## 1. 目录结构

```
projects/grok-search/
  ├─ DESIGN.md
  ├─ USAGE.md
  ├─ TESTING.md
  ├─ internal/ (shim)
  │   └─ context.py
  └─ scripts/grok_search.py

skills/grok-search/
  ├─ SKILL.md
  └─ scripts/grok_search_cli.py  # skill 入口（委托到 project 脚本）

工具层：
```

tools/grok_search/
├─ **init**.py
└─ context.py # 上下文回顾模块（内部）

```

```

## 2. 环境变量（推荐）

```
GROK_BASE_URL=https://api.example.com
GROK_API_KEY=***
GROK_MODEL=grok-4.20-beta
GROK_FALLBACK_MODEL=grok-4.1-thinking
GROK_TIMEOUT=1200
```

> 当前环境 **GAPI 就是 Grok**：`.env` 中 `GAPI_CUSTOM_BASE_URL / GAPI_CUSTOM_API_KEY` 作为 Grok base/key（等同于 `GROK_*`）。

## 3. Keychain（macOS，可选）

```
security add-generic-password -U -s openclaw-grok -a base-url -w
security add-generic-password -U -s openclaw-grok -a api-key -w
security add-generic-password -U -s openclaw-grok -a model -w
```

## 4. Skill 入口（推荐）

```bash
/usr/bin/python3 ~/.openclaw/workspace/skills/grok-search/scripts/grok_search_cli.py \
  --query "Sam Altman 在 X 最新发了什么？请给出原文和链接" \
  --mode stateless
```

> 该入口是轻量包装，参数与 project 脚本一致。

## 5. 基本用法（无上下文）

```bash
/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --query "Sam Altman 在 X 最新发了什么？请给出原文和链接" \
  --mode stateless
```

## 6. 带上下文（可追问）

```bash
/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --thread-id "user:123" \
  --query "OpenAI CEO 最近在 X 发了什么？" \
  --mode auto
```

## 7. 自定义提示词

```bash
/usr/bin/python3 ~/.openclaw/workspace/projects/grok-search/scripts/grok_search.py \
  --query "..." \
  --system-prompt "<你的系统提示词>"
```

## 8. 输出格式

默认输出 **模型 JSON 结果**；加 `--with-meta` 返回包含 `meta` 的封装输出。

```
{
  "sources": [...],
  "claims": [...],
  "answer": "...",
  "unknowns": [...],
  "confidence": 0.0
}
```
