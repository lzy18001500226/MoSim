# MoSim 文件整理审查方案

Request ID: `DOCSECRETARY-FILE-ORGANIZATION-REVIEW-20260608-001`

本轮只做项目文件整理审查和低风险移动；不做 agent 迁移，不改 CoAgent 架构，不创建/迁移/重命名可见线程，不派发下游任务，不触碰 MWORKS/ROS2/UE live 运行态。

## 本轮已执行的低风险整理

已将 `Results` 根目录下 75 个旧 `tmp_*` 临时清单移动到：

```text
Results/tmp/git_reference_intake_20260601/
```

移动依据：

- 文件名均为 `tmp_*`。
- 不在 Git 跟踪中。
- 已被当前忽略规则忽略。
- 在 `AGENTS.md`、`Docs/`、`CoAgent/`、`Scripts/`、`PROGRESS.md` 中零引用。
- 内容类型是 2026-06-01 左右 Git/References 分批整理临时清单或 rollout 临时列表。

保留在 `Results` 根目录的文件：

- `Results/README.md`：目录说明。
- `Results/人工审核清单.csv`：正式证据入口，有多处项目文档/脚本引用。
- `Results/file_organization_review/legacy_agent_project_lists/tmp_agent_projects_list.txt`：已被 Git 跟踪，本轮不移动。

## 分类方案

### 1. 任务与通信包

当前保留：

```text
Results/agent_packets/
Results/agent_packets/returns/
Results/agent_packets/blockers/
Results/agent_packets/notifications/
Results/agent_packets/reviews/
Results/agent_packets/summaries/
Results/agent_packets/closeouts/
Results/agent_packets/manual/
```

处理建议：

- `returns/`、`blockers/`、`notifications/` 等子目录继续保持不动。
- `Results/agent_packets/` 根部仍有 225 个 JSON 和 25 个 YAML 任务包；现有工作流会直接引用 `Results/agent_packets/<request_id>.json|yaml`，不建议本轮移动。
- 后续如要整理任务包，可先新增 `Results/agent_packets/tasks/`，再修改模板、checker、workflow 和历史引用策略；不能直接批量移动。

### 2. CoAgent 运行与巡检证据

当前保留：

```text
Results/coagent_gateway/
Results/coagent_transport/
Results/coagent_status/
Results/coagent_automation/
Results/coagent_bootstrap/
Results/coagent_doctor/
Results/coagent_miniloop/
Results/coagent_thread_health/
```

处理建议：

- 这些目录多数被 patrol、gateway、transport、doctor 或状态恢复流程引用，先保持目录级稳定。
- `coagent_transport/` 文件量较大，适合后续按日期或 request_id 做只读归档方案，但需先确认 transport/recovery 工具是否硬编码路径。
- `coagent_gateway/` 作为邮件/历史网关证据保留；WeChat 生产路径已停用，但旧证据不在本轮移动。

### 3. MWORKS 证据

当前保留：

```text
Results/mworks_background_capture/
Results/mworks_foreground_capture/
Results/mworks_gui_incidents/
Results/mworks_gui_sentinel/
Results/mworks_window_management/
Results/mworks_window_patrol/
Results/mworks_model_hygiene/
Results/mworks_dynamics_upgrade/
Results/mworks_trace_consumption/
```

处理建议：

- 这些目录按用途已经基本分类，不进行跨目录移动。
- `mworks_model_hygiene/` 是近期模型整理与图形审核证据主目录，当前仍活跃，不归档。
- GUI 截图/窗口证据目录保留现状，避免破坏巡检或审核引用。

### 4. ROS2 / UE 运行证据

当前保留：

```text
Results/ros2_runtime/
Results/unreal_experiment_console/
Results/unreal_scene_mapping/
Results/unreal_scene_review/
Results/unreal/
```

处理建议：

- `ros2_runtime/`、`unreal_experiment_console/`、`unreal_scene_mapping/` 都是当前 P0 runtime/source-static 证据目录，不移动。
- 已知有部分 staged runtime output 警告，这是既有状态；本轮不回滚、不清理、不重排。
- Sunray/PBR 用户已冻结，相关目录只作为历史/审核证据保留。

### 5. 文档缓存

当前保留：

```text
Docs/Cache/session_memory_migration/
```

处理建议：

- 该目录是旧会话迁移后的 cache-first 证据入口，结构清晰，保持不动。
- 不读取 raw Codex session JSONL 或旧聊天 dump。

### 6. 临时文件和可清理候选

已整理：

```text
Results/tmp/git_reference_intake_20260601/
```

后续候选：

- `Results/tmp/` 内 9733+ 文件需要单独按来源分类；本轮不深挖、不清理。
- `Results/agent_runtime/`、`Results/native_result_cache/`、`Results/official/` 体积较大，可能包含正式运行/官方证据，不作为低风险整理对象。

## 不移动清单

本轮明确不移动：

- 当前 active ledger。
- 当前 return/blocker packet。
- `Results/agent_packets/returns/` 与 `Results/agent_packets/blockers/`。
- `Results/agent_packets/` 根部任务包。
- `Results/人工审核清单.csv`。
- 所有 MWORKS/ROS2/UE 业务证据目录。
- 任何 staged runtime output。
- 任何业务源码、模型文件、脚本行为、MCP 配置、hook 配置。

## 后续人工审核项

1. 是否批准将 `Results/agent_packets/` 根部任务包迁到 `Results/agent_packets/tasks/`。批准前需要同步 workflow、schema/checker 和历史路径兼容策略。
2. 是否对 `Results/coagent_transport/` 做日期归档。批准前需要确认 transport/recovery 工具不依赖平铺路径。
3. 是否对 `Results/tmp/` 做第二轮来源分类。建议单独任务处理，避免误删运行证据。
4. 是否保留或归档已跟踪的 `Results/file_organization_review/legacy_agent_project_lists/tmp_agent_projects_list.txt`。因为它已被 Git 跟踪，本轮不移动。
