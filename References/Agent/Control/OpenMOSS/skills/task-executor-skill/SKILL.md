---
name: task-executor-skill
description: 任务执行者 Skill — 通过 CLI 工具领取子任务、提交成果、处理返工
---

# Task Executor Skill

你可以使用 `task-cli.py` 工具来与任务系统交互。该工具位于本 Skill 目录下。

## 认证信息

- API_KEY: `<注册后填入>`

## 工作流程

1. 获取规则 → 2. 检查积分 → 3. 查看我的子任务 → 4. 开始执行 → 5. 完成后提交 → 6. 如有返工，查看审查记录后修复再提交

## 可用命令

> 所有命令前缀：`python task-cli.py --key <API_KEY>`

### 规则

```bash
rules                                     # 获取合并后的规则提示词（执行前必须调用）
```

### 子任务操作

```bash
st mine                                   # 查看分配给我的子任务
st available                              # 查看可认领的子任务
st latest <task_id>                       # 快速获取某任务下分配给我的最新子任务
st claim <sub_task_id>                    # 认领一个子任务
st start <sub_task_id> --session <会话ID>  # 标记开始执行（绑定当前会话）
st submit <sub_task_id>                   # 提交成果
st get <sub_task_id>                      # 查看子任务详情
st session <sub_task_id> <会话ID>          # 更新 in_progress 子任务的会话 ID
```

> 📄 列表命令默认返回全部数据。如数据较多，可加 `--page N --page-size M` 分页查看。返回结果包含 `total`（总数）和 `has_more`（是否还有更多）。

### 审查记录（返工时使用）

```bash
review list --sub-task-id <id>            # 查看返工审查明细
review get <review_id>                    # 查看单条审查详情
```

当子任务状态为 `rework` 时，先查看审查记录了解问题，针对性修复后重新 `st start` → `st submit`。

### Agent 查看（只读）

```bash
agents                                    # 查看已注册 Agent（ID、角色、状态、积分）
agents --role reviewer                    # 按角色过滤
```

> ⚠️ 仅供查看团队成员信息。

### 积分

```bash
score me                                  # 查看自己的积分表现
score logs --page 1 --page-size 10        # 查看积分明细（建议分页，避免数据过多）
score leaderboard                         # 积分排行榜
```

> 📄 `score logs` 默认返回全部明细。如数据较多，可加 `--page N --page-size M` 分页查看。

### 通知

```bash
notification                              # 查看通知渠道配置
```

### 日志

```bash
log create "coding" "完成了xxx子任务的开发"
log create "delivery" "交付物：文件路径。内容摘要：做了什么" --sub-task-id <id>
log create "blocked" "遇到问题：具体问题。需要：需要什么帮助" --sub-task-id <id>
log mine                                  # 回顾工作记录（默认最近7天，最多20条）
log mine --action reflection              # 只看自省笔记
log mine --days 30 --limit 50             # 最近30天，最多50条
log list --sub-task-id <id>               # 查看某子任务的所有日志（含其他 Agent 的交接信息）
log list --action delivery                # 查看交付摘要
log list --days 3 --limit 10             # 最近3天，最多10条
```

## 注意事项

- 每次执行前先运行 `rules` 获取最新规则
- 每次唤醒时检查 `score logs`，有扣分则查看 `review list` 分析原因并改进
- 所有产出物必须放在子任务对应的工作目录下
- 提交前确认产出物符合验收标准，争取一次通过审查
- 收到返工（rework）时，先看 `review list` 了解具体问题再修复
- 不要操作不属于自己的子任务
- 完成后将通知发送到配置的渠道（通过 `notification` 查看渠道）
