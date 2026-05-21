---
description: "Start Loopback iteration loop in current session"
argument-hint: "PROMPT [--max-iterations N] [--completion-promise TEXT] [--dry-run]"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/setup-loopback.sh:*)"]
hide-from-slash-command-tool: "true"
---

# Loopback Command

如果你不确定该怎么传参/怎么把“完成标准”写成可停止的契约，先运行一次轻量向导（不会创建状态文件、不会启动循环）：

```text
/loopback --guide
```

默认会先进入向导模式（如环境不支持交互，则降级为“步骤概览 + 契约预检”）；如需跳过向导：加 `--no-wizard`。

Execute the setup script to initialize the Loopback state file (it will also launch the driver unless `--dry-run` or `--no-run` is set):

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/setup-loopback.sh" $ARGUMENTS
```

Please work on the task. When you try to complete, the Loopback system will check for completion conditions:
- If `--max-iterations` is reached, the loop stops
- If `--completion-promise` is detected in your output, the loop stops
- Otherwise, the SAME PROMPT will be fed back for the next iteration

By default Loopback reuses the same Codex session across iterations (similar to Ralph Loop).
Use `--fresh-session` if you want each iteration to start a new session.

You'll see your previous work in files and git history, allowing you to iterate and improve.

CRITICAL RULE: If a completion promise is set, you may ONLY output it when the statement is completely and unequivocally TRUE. Do not output false promises to escape the loop, even if you think you're stuck or should exit for other reasons. The loop is designed to continue until genuine completion.
