# AgentsMesh 产品调研笔记

基于深度代码调研（backend domain + services + runner + clients/web/src），总结产品的**真正业务模型**。本文档是后续 IA、flow、页面设计的依据。

## 一句话定位

AgentsMesh 是**分布式 AI Agent 工作力调度与协作平台**。用公司的类比：
- Organization = 公司
- Runner = 办公场所（自托管）
- Pod = 员工工位（带终端和工具）
- Agent = 员工职能（Claude Code / Aider / Codex）
- Ticket = 任务分配单
- Channel = 部门协作群
- Mesh = 组织架构拓扑图
- Loop = 重复工作流程（定时/触发）
- Autopilot = 流程管理器（含断路器）

## 核心实体

### 三层架构

**底层（基础设施）**：Runner + Pod
- Runner：自托管 gRPC+mTLS 守护进程，挂在用户基础设施上。一个 Runner 承载 N 个 Pod。
- Pod：immutable 工作单元。一旦创建绑定 Runner + Agent + Repository。有 PTY 终端和隔离 sandbox（git worktree 或 tempdir）。生命周期：`initializing → running → paused/disconnected/orphaned → completed/terminated/error`。支持 perpetual 模式（进程退出自动重启）。

**中层（工作协作）**：Ticket + Channel + Repository
- Ticket：任务单，Kanban 状态 `backlog→todo→in_progress→in_review→done`。1 个 Ticket 可关联 N 个 Pod。可有子 Ticket 树。
- Channel：多 Pod 通信群。N:M 关系（Pod 动态加入/离开）。支持 Pod 和 User 同时发消息。
- Repository：Git 仓库配置，存 clone URL + webhook。Pod clone 时用。
- PodBinding：Pod 间的协作权限（A 观察/控制 B），需审批。

**顶层（自动化编排）**：Loop + AutopilotController
- Loop：可重复任务定义。含 cron、prompt_template、agent、runner、repo 绑定。触发模式：cron / api / manual。执行模式：autopilot（自动迭代）/ direct。沙箱策略：persistent / fresh。
- LoopRun：Loop 的单次执行记录。关联 1 个 Pod。
- AutopilotController：管理 Pod 的迭代循环，含断路器（无进度阈值、错误重复阈值）。状态机：initializing → running → paused / user_takeover / waiting_approval / max_iterations / completed / failed / stopped。

### 横向能力层（扩展与配置）

- Agent：AI 助手的配置模板（Claude Code / Aider / Codex / Custom）。内置 + 组织自定义。含 `agentfile_source`（AgentFile DSL）、`supported_modes`（pty/acp）。
- AgentFile：Pod 配置的自定义 DSL。声明 `ENV / EXECUTABLE / MCP / SKILLS / MODE / CONFIG`。不是持久实体，在创建 Pod 时解析。
- UserAgentCredentialProfile：用户给特定 Agent 存的凭证（API key、base_url 等）。加密存储。Pod 创建时注入环境变量。支持 Runner host 模式（用 Runner 本地环境，不注入凭证）。
- Skill：Agent 的自定义能力包。来源：market / github / upload。在 Pod 启动时加载。
- MCP Server：Model Context Protocol 扩展。stdio 或 http/sse 两种传输。Pod 启动时启动。
- GitProvider：OAuth 凭证（github/gitlab/gitee/ssh）。

### 只读派生实体

- Mesh：**运行时构造，不存 DB**。由 MeshService 从活跃 Pod + PodBinding + Channel + Runner 动态聚合。节点 = Pod，边 = PodBinding，簇 = Channel。

## 关键业务概念

### Pod 是一切的中心

Pod 是**唯一的工作执行单元**。所有其他实体要么是 Pod 的上下文（Ticket/Repository），要么是 Pod 的协作机制（Channel/PodBinding/Mesh），要么是 Pod 的编排层（Loop/Autopilot），要么是 Pod 的配置（Agent/AgentFile/Skill/MCP）。

### 权限的"零信任"设计

- Pod 之间默认**不能互相访问**，必须通过 PodBinding 显式授权（`pod:read` / `pod:write`）
- Credential 从不进数据库记录，只在 Pod 启动时从 UserAgentCredentialProfile 查询并注入 env
- Runner 之间独立（同一 Org 下多个 Runner 互不通信）

### SSOT 设计
- Pod.status 是 Pod 状态的唯一真源
- LoopRun.status 只在 `pod_key=NULL` 时有权威性，一旦关联 Pod 后从 Pod.status 派生
- 避免多处维护导致不一致

### Perpetual & Resume
- Pod 可标记为 "perpetual"：进程清洁退出后自动重启，保持同 pod_key，递增 restart_count
- 新建 Pod 可指定 source_pod_key：恢复前一个 Pod 的会话和沙箱

## 角色与权限

### 4 类角色

| 角色 | 存储 | 范围 | 典型人群 |
|-----|------|------|---------|
| **System Admin** | `users.is_system_admin=true` | 全局（跨 Org） | 平台运维团队 |
| **Org Owner** | `organization_members.role="owner"` | 单 Org 全权 | 创始人 |
| **Org Admin** | `organization_members.role="admin"` | 单 Org 全权（不能删 Org） | Tech Lead |
| **Org Member** | `organization_members.role="member"` | 使用权（创建 Pod/Ticket/Channel） | 开发工程师 |

### 关键权限发现（问题）

- Pod 没有"所有权"概念。任何 Member 能看所有 Pod 的终端内容，**无隐私隔离**。
- Channel 没有成员列表。默认 Org 内所有人可见，**无法做私密频道**。
- API Key Scope 定义了但**未在中间件校验**，scope 形同虚设。
- Ticket 分配无校验，**任何人可分配给任何人**。
- Loop 触发无权限控制，有 API Key 就能触发任何 Loop。

## 资源归属

| 资源 | 归属 |
|-----|------|
| User | Personal（全局唯一） |
| Org/Member | Org |
| Runner | Org（但 visibility 可 private） |
| Pod | Org（但有 created_by 字段） |
| Ticket/Channel/Loop/Repository | Org |
| Git Credential | Personal |
| UserAgentCredentialProfile | Personal（per user + agent） |
| Builtin Agent | Global |
| Custom Agent | Org |

## 工作节奏画像

### 开发者（Org Member）— 每日 2-4 小时
**最频繁**：创建 Pod → 和 Agent 交互 → 看其他 Pod 的输出
**次要**：创建 Ticket / 分配自己 / 状态流转
**少用**：配置 Repository、MCP、Skill

### Tech Lead（Org Admin）— 每日 1-2 小时
**最频繁**：看 Ticket 看板 / 分配任务 / 看 Loop 跑没跑
**次要**：邀请成员 / 创建 Channel / 配置 Webhook
**少用**：删 Repository / 改 Agent 配置

### CEO/Owner（Org Owner）— 每日 30-60 分钟
**最频繁**：看 Billing / 用量
**次要**：邀请/移除成员、改角色
**少用**：删组织、改 SSO

### 平台运维（System Admin）— 每周 2-4 小时
**最频繁**：看 Audit Log / 处理 Support Ticket
**少用**：Promo Code / SSO 配置
