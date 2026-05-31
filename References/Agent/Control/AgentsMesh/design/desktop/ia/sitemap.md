# AgentsMesh 信息架构（IA）重新设计

## 当前 IA 的问题

调研发现的核心问题（摘自 `research/product-model.md` 和 Explore agent 报告）：

1. **平铺 8 个主导航**（Workspace/Tickets/Channels/Mesh/Loops/Repositories/Runners/Settings）没有分组，新用户面对"盘点型"菜单不知道从哪开始
2. **Repositories/Runners/Agents 是基础设施**，却和 Workspace/Tickets 平级，混淆"我在干活"和"我在配置"
3. **侧栏交互模式不统一**：Workspace 和 Tickets 有搜索+创建，Channels/Runners 啥都没有
4. **Loop 没有创建入口**（侧栏无 + 按钮，只能通过 CommandPalette）
5. **Pod 日志 3+ 条路径**（Workspace 打开 / Runners 详情 / Ticket 侧栏），用户不知哪条是"正式"路径
6. **Mesh 只读**，节点点了没反应，价值不清
7. **Settings 用 query param 混合 personal/organization**，视觉上一个页面两种上下文容易迷失
8. **Pod 归属模糊**：数据库有 created_by，但 UI 上任何人看所有 Pod，"我的工作"和"团队工作"没区分
9. **CommandPalette 搜索不全**：只搜 pods/tickets/repos，漏掉 channels/loops/runners/members
10. **移动端"More"菜单**偷偷藏功能（Loops/Repos/Runners）

## 设计原则

**Pod 为中心** — 产品的核心动作是"派 Agent 干活"。其他一切要么是 Pod 的上下文（Ticket/Repo），要么是协作机制（Channel/Mesh），要么是编排层（Loop/Autopilot），要么是配置（Runner/Agent/Member）。

**三层分类**：
- **Work** — 日常产出（Workspace、Tickets、Loops）
- **Collab** — 协作与可见（Channels、Mesh）
- **Config** — 配置与管理（Settings 下的一切：People、Infrastructure、Billing）

**每个功能唯一入口** — 消除"多路径通往同一页面"的冗余。

**个人 vs 组织明确分离** — Settings 首页顶部 Tabs，不再用 query param 混合。

**CommandPalette 作为跨资源搜索** — `Cmd+K` 能搜到任何资源，是新用户的救生圈。

## 新的顶层导航

### ActivityBar（左侧垂直图标栏，仅 5 个主图标 + Settings + 用户菜单）

```
┌────────────────────────────────────────────────────────────┐
│ [Org Avatar] ← 点击打开 org 切换 popover（取代品牌 logo）    │
├────────────────────────────────────────────────────────────┤
│  Work                                                      │
│    [>_] Workspace    ← 主工作区（Pod 列表 + 终端）         │
│    [🎫] Tickets      ← 任务看板（ticket 图标）             │
│    [↻]  Loops        ← 自动化流程                          │
│    [▦]  Blocks       ← 知识图谱 + 指示器（Block Store）     │
│                                                            │
│  Collab                                                    │
│    [#]  Channels     ← 协作通信（hashtag，Slack 传统）     │
│    [⚘]  Mesh         ← 组织拓扑（可交互）                  │
├────────────────────────────────────────────────────────────┤
│    [⚙]  Settings                                           │
│    [?]  Help                                               │
│    [👤] User menu                                          │
└────────────────────────────────────────────────────────────┘
```

**顶部是组织 Avatar + Org 切换**，不是 AgentsMesh 品牌 logo。理由：
- Electron 的 dock 图标 + 窗口标题栏已经承载品牌标识，App 内重复是浪费
- 组织上下文是多租户产品里最高频查看的信息，放在最显眼的左上角最合理
- Sidebar 原有的 `Dev Organization / dev-org / ⌵` 整行删除，垂直空间让给 Pod 列表
- 点击 Avatar 打开 popover：当前 org 详情 + 其他 org 列表 + "Create org / Accept invite"

**移出主导航的页面**（都归到 Settings > Organization）：
- Repositories → Settings > Organization > Code
- Runners → Settings > Organization > Infrastructure
- Agents → Settings > Organization > Agents
- Members → Settings > Organization > People

### 为什么不把 Runners/Repositories 放主导航？

用户**不会每天查看 Runner 状态**；那是首次安装 + 偶尔排障的配置项。日常工作中 Runner 只是 Pod 创建时的一个下拉选项。Repository 同理——配置一次，多次复用。

但 Workspace 侧栏会**有 Runner 连接状态指示**（顶部小徽章），让运行时信息可见但不喧宾夺主。

## 统一的侧栏模式

每个主模块（Workspace/Tickets/Loops/Channels/Mesh）的侧栏遵循同一骨架：

```
┌─────────────────────────────────┐
│ [Org ▼]   [Collapse ◀]          │ ← OrgSwitcher + 折叠按钮
├─────────────────────────────────┤
│ 🔍 Search... (⌘K 全局搜索)      │ ← 页面内搜索框
│ [+ New]  [Filter ▼]  [↻]        │ ← 创建 CTA + 过滤器 + 刷新
├─────────────────────────────────┤
│ Filters (collapsible)           │
│  □ Status: Active (12)          │
│  □ Priority: High (3)           │
├─────────────────────────────────┤
│ Group 1                    (5)  │ ← 分组标题 + 数量
│   · Item A (状态点)             │
│   · Item B                      │
│ Group 2                    (3)  │
│   · Item C                      │
├─────────────────────────────────┤
│ View: [List] [Board]   Sort ▼   │ ← 视图切换 + 排序
└─────────────────────────────────┘
```

**好处**：用户学一次会五次。每个页面都能用同样的键盘快捷键（J/K/Enter/Cmd+K/Cmd+N）。

## 每个模块的具体结构

### Workspace（/[org]/workspace）

**左侧栏**：Pod 列表，顶部有 3 个 scope tabs：
- **Mine** — 我创建的活跃 Pod（`running` / `initializing`，`created_by = me`）
- **Others** — 别人创建的、我能看到的活跃 Pod（`running` / `initializing`，`created_by ≠ me`）
- **Completed** — 已结束的 Pod（`terminated` / `failed` / `paused` / `completed` / `error`，全组织范围）

Tab 不带数字计数（避免视觉噪点）。列表内按状态优先级 + `created_at` 降序。

**搜索框支持 token 语法**（取代多余的 filter popover）：
```
agent:codex          按 agent slug 过滤
mode:acp | mode:pty  按交互模式
repo:demo-api        按 repository slug
ticket:DEV-1         按关联 ticket
running | idle       按状态（裸关键词）
```
多个 token 空格分隔做 AND。

**没有常驻 Refresh 按钮** — realtime 订阅 + 断线横幅 "Retry now" 已覆盖；真想强制刷新，sidebar 底部 `⋯` overflow 菜单里有入口。

**注意**：当前代码实现里 filter key 是 `mine | org | completed`，`org` 的过滤只按状态而不排除"我自己的"——落地时需要改为 `others` 并加上 `created_by ≠ me` 条件。

**主区**：
- 无 Pod 时：Onboarding 引导（创建第一个 Pod）
- 有 Pod 时：多 pane 终端 + Bottom panel（5 tabs：activity/channels/autopilot/delivery/info）
- 顶部 PageHeader：面包屑 + 快速 actions（断线时显示红色横幅）

**快捷键**：
- `Cmd+N` 新建 Pod
- `Cmd+W` 关闭当前 Pod
- `Cmd+T` 新 pane
- `J/K` 在 Pod 列表间移动

### Tickets（/[org]/tickets）

**侧栏**：没有 Mine/Others/Completed tabs —— Ticket 是团队共享任务单，"谁创建"不是日常过滤维度。直接用 filter sections：
- **Priority**（Urgent / High / Medium / Low / None）
- **Repository**（每个 repo + 未关联）
- **Labels**（彩色 chip + 计数）
- **Assignee**（我 / 其他人 / 未分配）

搜索框支持 `priority:high` / `label:bug` / `repo:demo-api` / `assignee:@me` 等 token。

Status 过滤由 Kanban 的 5 列承担（Backlog/Todo/In Progress/In Review/Done）；List 视图才需要单独 Status filter section。

**主区**：
- PageHeader：title + description + `[Board | List]` 视图切换 + Export
- **Board** 视图：5 列 Kanban，每列头显示状态点 + 名称 + 计数 + `+` 快速新建
- **Ticket 详情页顶部大号 [Spawn Pod] 按钮**，自动带入 repo/branch/last-used agent
- Ticket 卡片显示"N pods running"—— Pod-Ticket 双向可见
- Done 列默认折叠为汇总卡片（"12 shipped · View archive →"），防止看板过载

### Blocks（/[org]/blocks）— 新增核心能力

**本质**：团队的**通用结构化数据层 + 知识图谱**。不是"又一个功能"，是底层骨架。
- `Block` — 类型化数据单元（type + data），人和 Agent 都能读写
- `Ref` — 有语义的边（nest / mention / embed / depends_on / tag…），构图
- `View` / `Summary` — 对其他 block 的聚合查询（filters / group_by / aggregate → table / kanban / timeline / metric）
- `block_type_def` — **指示器即代码**：团队可以动态定义新类型（OKR / Metric / Incident…）无需后端部署
- **Op 日志** — ACID 单源事实，时间旅行 + 冲突消解
- **实时** — agent / 人改 block → WebSocket → 所有聚合视图自动重算

**UI 结构**（master-detail）：
- **左 Sidebar**：Workspace 切换 + Pages 树（nest 父子结构，拖拽排序）+ 搜索 `Cmd+K`
- **主区**：文档编辑器（Notion 风，斜杠菜单）渲染当前选中 page 的 nest 子树
- **特殊 block 类型的行为**：
  - `view` 块 — 渲染成表格 / 看板 / 时间线（根据 ViewSpec）
  - `summary` 块 — 渲染成 KPI 卡片（count / avg / sum）
  - 其他 block（task / code / image / embed…）inline 渲染

**和现有模块的关系**：
- **Pod** → 运行时产生 Block（输出、tool call、决策痕迹），可查询、可聚合
- **Ticket** → Ticket 自身保持，但可以在 Block 文档里 `embed` Ticket 视图（团队 OKR 仪表板引用 ticket 进度）
- **Channel** → Channel 消息可以 `mention` Block，把讨论和结构化数据绑定
- **Agent MCP** → `createBlock / updateBlock / addRef / memory.retrieve` 等工具对 agent 开放

**权限**：workspace 级隔离 + block 级 ACL（meta.acl 字段）。

**菜单位置**：ActivityBar 第 4 个图标（`▦`），在 Work 组，排在 Loops 之后。

**左侧栏**：按"Enabled / Disabled / Archived"分组，顶部加 `[+ New Loop]` 按钮（修复调研痛点 #4）

**主区**：Loop 列表卡片 + 详情页（cron 表达式用日历选择器）

### Channels（/[org]/channels）

**左侧栏**：按**活跃度分组**（不按字母）
- `Active` — 最近有消息（前几小时）
- `Linked` — 显式关联 Ticket / Repository
- `Quiet` — 长期无动静
- 未读用小红点，不展示未读数

搜索 + [+ New Channel] 在顶部；底部有 "Browse archived →" 链接。

**Channel Header** 单行承载全部上下文：`# name · N pods · N members · Linked to TICKET · repo`

**消息流**——**Pod 和 User 在消息层面等位**：
- User 消息：圆形 avatar + role badge（owner / member）
- Pod 消息：方形 avatar + `pod-xxx` mono key + `agent · mode` badge
- Pod tool call：灰色卡片嵌入消息流（`🔧 read_file src/auth.ts`）
- System 消息：居中灰色（`joined / left / linked`）

**Composer**：placeholder 直接教学 `use @ to mention a pod or member, / for commands`；`⌘⏎ to send`。

**右侧 Members rail**：PODS + MEMBERS + **LINKED**（关联 Ticket 卡 + Repo 卡，一键跳转）。这比当前实现的隐藏关联更好——用户总是看得见这个 channel 在为什么任务服务。

**未来改进**（代码层面）：Channel 需要 `visibility = public | private` 字段，当前默认全组织可见（调研发现的痛点）。

### Mesh（/[org]/mesh）

**左侧栏**：过滤器（Runner / Agent 类型 / 状态）

**主区**：拓扑图
- **点击 Pod 节点** → 打开该 Pod 终端（跳 Workspace）
- **点击 Channel 集群** → 进入该 Channel
- **点击 Runner** → Runner 详情（Settings > Infrastructure）
- 实时动画：消息流动、Pod 状态变化

这修复痛点 #5（Mesh 只读）。

### Settings（/[org]/settings）

**顶部 Tabs（不再用 query param）**：

```
[Personal]  |  [Organization]
```

**Personal** 左侧菜单：
- Profile（头像、名字、邮箱）
- Credentials
  - Git providers (GitHub/GitLab OAuth)
  - Agent credentials (Claude/Aider API keys)
- Notifications
- Appearance（主题、语言）
- Keyboard shortcuts

**Organization** 左侧菜单（可能受权限限制）：
- General（名字、logo、slug）
- People（Members + Invitations，原 Members）
- Infrastructure
  - Runners
  - Code（Repositories + Git Provider 连接）
- Agents
  - Built-in agents（只读列表）
  - Custom agents
  - MCP servers
  - Skills
- Billing & Usage
- API Keys
- Audit Log（admin only）
- Danger zone（删除组织）

## 全局交互元素

### CommandPalette (Cmd+K)

扩展搜索范围，支持跨资源跳转：
- Pods / Tickets / Channels / Loops / Runners / Repositories / Members
- 动作（Create pod / Invite member / Open settings）
- 最近访问（Recent）
- 键盘导航（↑↓ / Enter / Esc）

### Breadcrumb

所有详情页顶部都有：`Workspace > pod-abc-123` / `Tickets > DEV-1 Implement JWT auth`
一次点击回列表。

### 连接状态

顶部一个**细条**（仅在异常时显示）：
- 正常：不显示
- 重连中：黄色 "Reconnecting..."
- 断开 >30s：红色 "Connection lost. [Retry]"
- Runner 离线 / 证书将过期：同一横幅组件承载（不再单独小挂件）

**Runner 状态不常驻 Workspace**。理由：
- 普通 Member 不需要关心底层基础设施
- Runner 异常会反映到：① 顶部异常横幅 ② Pod pane header 的状态点 ③ Pod 创建失败错误
- 常驻徽章和这些信号重复，属于噪音

**Runner 容量/版本/连接信息只在 2 处出现**：
- Pod 创建 Modal 选 Runner 下拉时，每行显示 `5/10 pods · v1.8.2`
- `Settings > Organization > Infrastructure > Runners` 列表和详情页

### 通知 Toast

- 成功：绿色短暂 toast
- 错误：红色 toast 带"详情"按钮
- 需要操作（autopilot 等批准）：持续型 toast 带 Accept/Reject

## 权限可见性规则

基于调研的角色表：

| 功能区 | Owner | Admin | Member |
|--------|-------|-------|--------|
| Workspace / Tickets / Loops / Channels / Mesh | ✓ | ✓ | ✓ |
| Settings > Personal | ✓ | ✓ | ✓（仅自己） |
| Settings > Org > General | ✓ | ✓ | 只读 |
| Settings > Org > People | ✓ | ✓ | 只读 |
| Settings > Org > Infrastructure（Runners/Code） | ✓ | ✓ | 只读 |
| Settings > Org > Agents | ✓ | ✓ | 只读 |
| Settings > Org > Billing | ✓ | 只读 | 不可见 |
| Settings > Org > API Keys | ✓ | ✓ | 不可见 |
| Settings > Org > Audit Log | ✓ | ✓ | 不可见 |

**侧栏菜单项动态隐藏**（不是灰显），避免 Member 看到一堆"不能点"的项。

## 对比表：旧 IA vs 新 IA

| 场景 | 旧 IA | 新 IA |
|-----|-------|------|
| 首次打开 | 8 个平铺菜单，不知道看哪 | 5 个工作菜单 + Settings，分成 Work/Collab 两组 |
| Runner 配置 | 单独顶级菜单 | 藏到 Settings > Org > Infra（首次 onboarding 单独引导） |
| Loop 创建 | 侧栏无按钮，只能 Cmd+K | 侧栏顶部 `[+ New Loop]` |
| Pod 日志 | 3+ 入口 | Workspace 是唯一入口；Ticket/Runner 只显示链接跳过去 |
| Mesh 价值 | 只读装饰 | 可点击跳转 + 实时消息动画 |
| 个人 vs 组织设置 | 同页面 query param 混合 | 顶部 Tab 分离 |
| Pod "所有权" | 看起来共享 | 引入"My Pods" / "All Pods" 过滤（Workspace 侧栏） |

## 操作流畅性关键改进

1. **Ticket → Pod 一键化**：Ticket 详情页显眼 "Spawn Pod"，自动带入 repository + branch
2. **Workspace 侧栏显示运行时状态**：Runner 连接状态、Pod 总数、LoadAvg 徽章
3. **命令面板触手可及**：任何页面 `Cmd+K` 聚焦搜索，不需专门去某个菜单
4. **Breadcrumb + Back**：每个详情页回退一次点击
5. **Mesh 作为"地图"**：点 Pod 去干活、点 Channel 去聊天、点 Runner 去配置
6. **断线不隐身**：顶部红色横幅 + Toast + 自动重连进度
7. **创建流程进度可见**：Pod 创建有 step-by-step 进度（生成 sandbox → 启动 agent → 准备 relay），不再"转圈等"
