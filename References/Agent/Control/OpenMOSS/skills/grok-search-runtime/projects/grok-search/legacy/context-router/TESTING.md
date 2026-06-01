# 测试与验收（最小测试 + 回归）（LEGACY）

> 已并入 grok-search；本文件仅作历史参考。
> 目标：验证 CLI flow 基本可用，以及 prune 的 TTL 行为（ttl=0 / ttl=1）。
> 注意：使用临时 DB 路径，避免影响默认 `data/context.db`。

## 0. 前置条件
- 在 OpenClaw workspace 根目录执行。
- Python 3 可用（示例使用 `/usr/bin/python3`）。
- CLI 路径：`skills/context-router/scripts/context_router_cli.py`

建议在命令中显式传入 `--db <临时路径>`，不依赖 `CONTEXT_DB_PATH`。

---

## 1. 最小测试（CLI flow，含 ttl=0）
直接运行内置示例脚本（自带临时 DB）：

```bash
/usr/bin/python3 skills/context-router/examples/minimal_cli_flow.py
```

**预期/检查点：**
- 输出包含 `route → build → record → get → prune` 五段 JSON。
- `route` 返回 `task_id`、`include_context`、`reason` 等字段。
- `record` 返回 `{"ok": true}`。
- `get` 的 `snapshot.messages` 至少包含用户/助手两条消息。
- `prune` 使用 `ttl=0`，脚本已 `sleep(1)`，`deleted` 应 ≥ 1。

---

## 2. 最小测试：prune ttl=1
> 验证：**小于 1 秒不删**，**超过 1 秒后可删**。

示例（手动流程，复制 `task_id` 即可）：

```bash
TMPDIR=$(mktemp -d)
DB="$TMPDIR/context.db"
CLI="/usr/bin/python3 skills/context-router/scripts/context_router_cli.py"
THREAD="test:user:ttl1"
TEXT="继续这个问题"

# 1) route
$CLI route --thread-id "$THREAD" --user-text "$TEXT" --mode auto --db "$DB"
# 记录输出里的 task_id

# 2) record
$CLI record --thread-id "$THREAD" --task-id "<task_id>" \
  --user-text "$TEXT" --assistant-text "ok" --db "$DB"

# 3) ttl=1 立即 prune（通常应为 0）
$CLI prune --ttl-seconds 1 --db "$DB"

# 4) 等待 2 秒，再 prune（应 ≥ 1）
sleep 2
$CLI prune --ttl-seconds 1 --db "$DB"
```

**预期/检查点：**
- 第一次 `prune` 的 `deleted` 通常为 `0`（记录仍在 TTL 内）。
- 休眠后再次 `prune`，`deleted` 应 ≥ 1。

---

## 3. 回归检查点（功能性）
- **CLI 可用**：`context_router_cli.py` 能正常运行并输出 JSON。
- **route**：
  - 新线程默认 `reason=new_task`；显式 `--task-id` 时为 `explicit_task_id`。
  - `include_context` 在非续谈词 + auto 模式下通常为 `false`。
- **build**：无快照时 `messages` 应为空数组 `[]`。
- **record/get**：`record` 后 `get` 可读取到包含用户/助手消息的 snapshot。
- **prune**：`ttl=0` + 等待 1 秒能删；`ttl=1` 立即不删、等待后可删。

---

## 4.（可选）简易 Smoke 脚本
如需一键验证，可将以下脚本保存为 `smoke_context_router.sh` 执行：

```bash
#!/usr/bin/env bash
set -euo pipefail
CLI="/usr/bin/python3 skills/context-router/scripts/context_router_cli.py"
TMPDIR=$(mktemp -d)
DB="$TMPDIR/context.db"
THREAD="smoke:user:1"
TEXT="继续这个问题"

route_json=$($CLI route --thread-id "$THREAD" --user-text "$TEXT" --mode auto --db "$DB")
TASK_ID=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["task_id"])' "$route_json")

$CLI build --thread-id "$THREAD" --task-id "$TASK_ID" --db "$DB" >/dev/null
$CLI record --thread-id "$THREAD" --task-id "$TASK_ID" --user-text "$TEXT" --assistant-text "ok" --db "$DB" >/dev/null
$CLI get --thread-id "$THREAD" --task-id "$TASK_ID" --db "$DB" >/dev/null

sleep 1
$CLI prune --ttl-seconds 0 --db "$DB"
$CLI prune --ttl-seconds 1 --db "$DB"
```

> 该脚本只做基本连通性与 TTL 行为验证，不依赖任何测试框架。
