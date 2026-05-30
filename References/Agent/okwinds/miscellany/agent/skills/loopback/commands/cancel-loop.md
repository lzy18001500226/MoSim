---
description: "Cancel active Loopback loop"
allowed-tools: ["Bash(test -f .codex/loopback.local.md:*)", "Bash(rm .codex/loopback.local.md)", "Read(.codex/loopback.local.md)"]
hide-from-slash-command-tool: "true"
---

# Cancel Loopback

To cancel the Loopback loop:

1. Check if `.codex/loopback.local.md` exists using Bash: `test -f .codex/loopback.local.md && echo "EXISTS" || echo "NOT_FOUND"`

2. **If NOT_FOUND**: Say "未找到活动的 Loopback 循环。"

3. **If EXISTS**:
   - 读取 `.codex/loopback.local.md` 获取 `iteration:` 字段中的当前迭代次数
   - 使用 Bash 删除文件: `rm .codex/loopback.local.md`
   - 报告: "已取消 Loopback 循环 (当前迭代次数: N)"，其中 N 是迭代值

Note:
- 如果你正在运行 `scripts/codex-loopback-wrapper.sh`，删除状态文件会让 wrapper 在下一次检查时退出（视为取消）。
