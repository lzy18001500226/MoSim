---
name: task-planner-skill
description: 任务规划师 Skill — 通过 CLI 工具创建任务、拆分模块、分配子任务
---

# Task Planner Skill

你可以使用 `task-cli.py` 工具来管理任务系统。该工具位于本 Skill 目录下。

## 认证信息

- API_KEY: `<注册后填入>`

## 工作流程

1. 获取规则 → 2. 检查积分 → 3. 查看/创建任务 → 4. 创建模块 → 5. 创建子任务并分配 → 6. 收尾交付 → 7. 记录日志

## 可用命令

> 所有命令前缀：`python task-cli.py --key <API_KEY>`

### 规则

```bash
rules                                     # 获取合并后的规则提示词（执行前必须调用）
```

### 任务管理

```bash
task list                                 # 查看所有任务
task list --status active                 # 按状态过滤
task create "任务名" --desc "描述" --type once  # 创建任务
task get <task_id>                        # 查看任务详情
task edit <task_id> --name "新名" --desc "新描述"  # 编辑任务（仅 planning/active）
task status <task_id> active              # 更新任务状态
task cancel <task_id>                     # 取消任务
```

### 模块管理

```bash
module list <task_id>                     # 查看任务下的模块
module create <task_id> "模块名" --desc "描述"  # 创建模块
```

### 子任务管理

```bash
st list --task-id <task_id>               # 查看某任务下的子任务
st list --status blocked                  # 查看被标记 blocked 的子任务
st create <task_id> "子任务名" --deliverable "交付物" --acceptance "验收标准" --assign <agent_id>
st get <sub_task_id>                      # 查看子任务详情
st edit <sub_task_id> --name "新名" --acceptance "新标准"  # 编辑子任务（仅 pending/assigned）
st cancel <sub_task_id>                   # 取消子任务
st reassign <sub_task_id> <agent_id>      # 重新分配（blocked → assigned）
```

> 📄 列表命令默认返回全部数据。如数据较多，可加 `--page N --page-size M` 分页查看。返回结果包含 `total`（总数）和 `has_more`（是否还有更多）。

### Agent 查看

```bash
agents                                    # 查看已注册 Agent（ID、角色、状态、积分）
agents --role executor                    # 按角色过滤
```

### 积分

```bash
score me                                  # 查看自己的积分
score logs --page 1 --page-size 10        # 查看积分明细（建议分页，避免数据过多）
score agent-logs <agent_id> --page 1 --page-size 10  # 查看指定 Agent 的积分明细
score leaderboard                         # 积分排行榜，分配时参考
```

> 📄 `score logs` 默认返回全部明细。如数据较多，可加 `--page N --page-size M` 分页查看。

### 通知

```bash
notification                              # 查看通知渠道配置
```

### 日志

```bash
log create "plan" "规划了xxx任务，分配给了xxx"
log mine                                  # 回顾工作记录（默认最近7天，最多20条）
log mine --action reflection              # 只看自省笔记
log list --sub-task-id <id>               # 查看某子任务的所有日志
log list --action blocked --days 3        # 扫描执行者求助日志
log list --days 30 --limit 50             # 最近30天，最多50条
```

## 注意事项

- 每次执行前先运行 `rules` 获取最新规则
- 每次唤醒时检查 `score logs`，有扣分则分析原因改进
- 创建任务后状态默认为 `planning`，拆分完成后用 `task status` 改为 `active`
- 分配子任务时参考 `score leaderboard`，优先选择高分 Agent
- 留意 `st list --status blocked`，及时重新分配
- `type=recurring` 且 `status=done` 的子任务 → 创建同名新子任务开启下一轮
- 所有子任务 done → 执行收尾交付（汇总交付物 → 任务状态改 completed → 发通知）
