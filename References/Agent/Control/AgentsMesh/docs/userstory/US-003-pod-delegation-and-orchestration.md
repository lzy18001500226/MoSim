# US-003: Pod 委托与多 Agent 协作

| 属性 | 值 |
|------|-----|
| **状态** | Draft |
| **作者** | AgentsMesh Team |
| **创建日期** | 2026-01-16 |
| **角色** | 开发者 / 架构师 |

---

## 1. 概述

### 1.1 用户故事

**作为** 一名开发者，
**我希望** 主 Pod (Supervisor) 能够创建并委托任务给子 Pod (Worker)，
**以便** 实现复杂任务的分解、并行处理和智能协调，让多个 AI Agent 协同完成工作。

### 1.2 价值主张

- **任务分解**: 复杂任务自动拆分为可并行的子任务
- **专业分工**: 不同 Agent 擅长不同领域（前端/后端/测试）
- **智能协调**: Supervisor 监督进度，动态调整策略
- **效率提升**: 多 Agent 并行工作，缩短交付时间

---

## 2. 核心概念

### 2.1 角色定义

| 角色 | 说明 |
|------|------|
| **Supervisor Pod** | 主控 Pod，负责任务分解、委托、监督和汇总 |
| **Worker Pod** | 执行 Pod，接收 Supervisor 委托的具体任务 |
| **Channel** | 多 Pod 通信空间，支持消息传递和状态同步 |

### 2.2 委托模式

```
┌─────────────────────────────────────────────────────────────────┐
│                        Channel (协作空间)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────────────┐                                          │
│    │  Supervisor Pod │                                          │
│    │  (Claude Code)  │                                          │
│    └────────┬────────┘                                          │
│             │                                                   │
│             │ delegate / monitor / instruct                     │
│             │                                                   │
│    ┌────────┴────────┬─────────────────┐                        │
│    ▼                 ▼                 ▼                        │
│ ┌──────────┐   ┌──────────┐   ┌──────────┐                      │
│ │Worker Pod│   │Worker Pod│   │Worker Pod│                      │
│ │ Frontend │   │ Backend  │   │  Testing │                      │
│ └──────────┘   └──────────┘   └──────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 前置条件

| 条件 | 说明 |
|------|------|
| 用户已登录 | 拥有有效的 AgentsMesh 账户 |
| Runner 资源充足 | 有足够的 Runner 支撑多 Pod 运行 |
| Channel 已创建 | 多 Pod 协作需要在 Channel 中进行 |
| Agent 配置就绪 | Supervisor 和 Worker 使用的 Agent 已配置 |

---

## 4. 用户流程

### 4.1 整体流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 创建 Channel │ ──► │启动Supervisor│ ──► │ 任务分解    │ ──► │ 委托 Worker │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  任务完成   │ ◄── │  结果汇总   │ ◄── │  监督指挥   │ ◄── │ Worker 执行 │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 4.2 详细步骤

#### Step 1: 创建 Channel（协作空间）

1. 进入项目 Channel 页面
2. 点击「创建 Channel」
3. 配置 Channel：
   - **名称**: 描述协作目标
   - **类型**: 选择「多 Agent 协作」模式
   - **关联仓库**: 选择目标代码仓库
   - **参与者**: 配置允许的 Agent 类型

**Channel 配置示例:**
```yaml
channel:
  name: "用户认证模块开发"
  type: multi_agent
  repository: myorg/myproject
  branch: feature/user-auth

  agents:
    supervisor:
      type: claude-code
      role: coordinator
    workers:
      - type: claude-code
        role: backend
      - type: claude-code
        role: frontend
      - type: aider
        role: testing
```

#### Step 2: 启动 Supervisor Pod

1. 在 Channel 中启动 Supervisor Pod
2. 向 Supervisor 描述总体任务目标
3. Supervisor 分析任务并制定执行计划

**用户输入示例:**
```
请实现完整的用户认证模块，包括：
1. 后端 API（登录、注册、密码重置）
2. 前端页面（登录表单、注册表单）
3. 单元测试和集成测试

要求：
- 使用 JWT 认证
- 密码需要加密存储
- 支持邮箱验证
```

**Supervisor 分析输出:**
```
任务分析完成，我将把这个任务分解为 3 个子任务：

┌─────────────────────────────────────────────────────────────┐
│ 子任务 1: 后端 API 开发                                      │
│ - 实现 /api/auth/login 端点                                 │
│ - 实现 /api/auth/register 端点                              │
│ - 实现 /api/auth/reset-password 端点                        │
│ - JWT token 生成与验证                                       │
│ - 预计工作量: 中等                                           │
├─────────────────────────────────────────────────────────────┤
│ 子任务 2: 前端页面开发                                       │
│ - 登录表单组件                                               │
│ - 注册表单组件（含邮箱验证）                                  │
│ - 密码重置流程页面                                           │
│ - 预计工作量: 中等                                           │
├─────────────────────────────────────────────────────────────┤
│ 子任务 3: 测试用例编写                                       │
│ - 后端 API 单元测试                                          │
│ - 前端组件测试                                               │
│ - 端到端集成测试                                             │
│ - 预计工作量: 轻量（依赖前两个任务完成）                       │
└─────────────────────────────────────────────────────────────┘

我将创建 2 个 Worker Pod 并行处理后端和前端任务，
测试任务待前两个完成后再启动。

是否继续？
```

#### Step 3: Supervisor 委托创建 Worker Pod

1. Supervisor 调用 AgentsMesh API 创建 Worker Pod
2. 系统分配 Runner 并启动 Worker
3. Supervisor 向 Worker 发送任务指令

**委托消息流:**
```
Supervisor                 Backend                   Runner
    │                         │                         │
    │── create_worker_pod ───►│                         │
    │   {task: "backend"}     │                         │
    │                         │── create_pod ──────────►│
    │                         │◄── pod_created ─────────│
    │◄── worker_created ──────│                         │
    │                         │                         │
    │── delegate_task ───────►│                         │
    │   {pod_id, instructions}│── forward_message ─────►│
    │                         │                         │
```

**Supervisor 委托指令示例:**
```
[委托给 Worker-Backend]

你的任务是实现用户认证后端 API，具体要求：

1. 在 backend/internal/api/rest/v1/ 下创建 auth.go
2. 实现以下端点:
   - POST /api/v1/auth/login
   - POST /api/v1/auth/register
   - POST /api/v1/auth/reset-password

3. 技术要求:
   - 使用 JWT (github.com/golang-jwt/jwt)
   - 密码使用 bcrypt 加密
   - 返回格式遵循现有 API 规范

4. 完成后请汇报:
   - 创建/修改的文件列表
   - 关键设计决策
   - 需要前端配合的接口契约

开始工作吧！
```

#### Step 4: Worker 执行与状态上报

1. Worker Pod 接收任务后自主工作
2. 定期向 Supervisor 上报进度
3. 遇到问题时请求 Supervisor 指导

**Worker 状态上报:**
```
[Worker-Backend 进度报告]

当前状态: 进行中 (60%)

已完成:
✓ 创建 auth.go 文件结构
✓ 实现 login 端点
✓ 实现 register 端点
✓ JWT token 生成逻辑

进行中:
→ 实现 reset-password 端点

待处理:
○ 邮件发送集成
○ 单元测试

问题:
⚠️ 邮件服务配置需要确认，是使用 SMTP 还是 SendGrid？

请指示。
```

#### Step 5: Supervisor 监督与指挥

1. Supervisor 实时接收 Worker 状态
2. 根据进度调整执行策略
3. 解答 Worker 的问题和疑虑
4. 协调多 Worker 之间的依赖

**Supervisor 指挥示例:**
```
[Supervisor 指令]

@Worker-Backend:
邮件服务使用 SMTP，配置从环境变量读取：
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD

继续完成 reset-password 端点。

@Worker-Frontend:
后端 login API 已完成，接口契约如下：
POST /api/v1/auth/login
Request: { email: string, password: string }
Response: { token: string, user: {...} }

请开始实现登录表单，并对接此 API。
```

**多 Worker 协调:**
```
┌─────────────────────────────────────────────────────────────┐
│ Supervisor 监控面板                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Worker-Backend   ████████████████░░░░  80%  API 开发中      │
│ Worker-Frontend  ████████████░░░░░░░░  60%  登录表单完成    │
│ Worker-Testing   ░░░░░░░░░░░░░░░░░░░░  等待中 (依赖未就绪)  │
│                                                             │
│ 依赖关系:                                                    │
│ Testing ──depends──► Backend (80%)                          │
│ Testing ──depends──► Frontend (60%)                         │
│                                                             │
│ 预计 Worker-Testing 将在 10 分钟后启动                       │
└─────────────────────────────────────────────────────────────┘
```

#### Step 6: 结果汇总与交付

1. 所有 Worker 完成任务后向 Supervisor 汇报
2. Supervisor 审查各 Worker 的工作成果
3. 合并代码变更，解决冲突
4. 生成最终交付报告

**Supervisor 汇总报告:**
```
[任务完成报告]

═══════════════════════════════════════════════════════════════
                    用户认证模块开发 - 完成
═══════════════════════════════════════════════════════════════

执行摘要:
- 总耗时: 45 分钟 (并行执行)
- 串行预估: 2 小时
- 效率提升: 62%

Worker 贡献:
┌─────────────┬──────────┬─────────────────────────────────────┐
│ Worker      │ 状态     │ 交付物                               │
├─────────────┼──────────┼─────────────────────────────────────┤
│ Backend     │ ✓ 完成   │ auth.go, jwt.go, 3 个 API 端点       │
│ Frontend    │ ✓ 完成   │ LoginForm.tsx, RegisterForm.tsx     │
│ Testing     │ ✓ 完成   │ auth.test.ts, 15 个测试用例 (全通过) │
└─────────────┴──────────┴─────────────────────────────────────┘

代码变更:
- 新增文件: 8 个
- 修改文件: 3 个
- 新增代码: 856 行
- 测试覆盖率: 87%

已创建 Pull Request: #142
分支: feature/user-auth → main

建议 Review 重点:
1. JWT 过期时间配置 (backend/internal/config/auth.go:25)
2. 密码强度验证规则 (backend/internal/service/auth.go:78)
3. 前端表单验证逻辑 (clients/web/src/components/LoginForm.tsx:45)

═══════════════════════════════════════════════════════════════
```

---

## 5. 通信协议

### 5.1 消息类型

| 消息类型 | 方向 | 说明 |
|----------|------|------|
| `create_worker` | Supervisor → Backend | 请求创建 Worker Pod |
| `delegate_task` | Supervisor → Worker | 委托具体任务 |
| `status_report` | Worker → Supervisor | 进度状态上报 |
| `request_guidance` | Worker → Supervisor | 请求指导/决策 |
| `instruction` | Supervisor → Worker | 回复指导/指令 |
| `task_complete` | Worker → Supervisor | 任务完成通知 |
| `terminate_worker` | Supervisor → Backend | 请求终止 Worker |

### 5.2 消息格式

```json
{
  "type": "delegate_task",
  "from": "pod_supervisor_123",
  "to": "pod_worker_456",
  "channel_id": "channel_789",
  "payload": {
    "task_id": "task_001",
    "title": "实现后端认证 API",
    "instructions": "...",
    "context": {
      "repository": "myorg/myproject",
      "branch": "feature/user-auth",
      "files_to_modify": ["backend/internal/api/rest/v1/auth.go"]
    },
    "constraints": {
      "timeout_minutes": 30,
      "max_file_changes": 10
    }
  },
  "timestamp": "2026-01-16T10:30:00Z"
}
```

---

## 6. 系统架构

### 6.1 组件交互

```
┌─────────────────────────────────────────────────────────────────┐
│                           Web UI                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Channel View │  │ Pod Monitor  │  │ Task Board   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │ WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Backend                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Channel Svc  │  │  Pod Svc     │  │ Message Hub  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────┬───────────────────────────────────┘
                              │ WebSocket
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Runner A │   │ Runner A │   │ Runner B │
        │Supervisor│   │ Worker 1 │   │ Worker 2 │
        └──────────┘   └──────────┘   └──────────┘
```

### 6.2 数据流

```
1. 用户创建任务
   User ──► Web ──► Backend ──► DB (Channel, Task)

2. Supervisor 分析并委托
   Supervisor Pod ──► Backend API ──► 创建 Worker Pod

3. Worker 执行并上报
   Worker Pod ──► Backend ──► Supervisor Pod
                    │
                    └──► Web UI (实时更新)

4. 结果汇总
   Workers ──► Supervisor ──► Backend ──► 合并代码 ──► 创建 PR
```

---

## 7. API 接口

### 7.1 Supervisor 可用 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/channels/:id/pods` | POST | 在 Channel 中创建 Worker Pod |
| `/api/v1/channels/:id/messages` | POST | 发送消息给指定 Pod |
| `/api/v1/pods/:id/status` | GET | 查询 Worker Pod 状态 |
| `/api/v1/pods/:id/terminate` | POST | 终止 Worker Pod |
| `/api/v1/channels/:id/summary` | GET | 获取 Channel 任务汇总 |

### 7.2 MCP 工具集成

Supervisor Pod 通过 MCP (Model Context Protocol) 调用 AgentsMesh 能力：

```typescript
// MCP 工具定义
{
  name: "agentsmesh_create_worker",
  description: "创建一个 Worker Pod 来执行子任务",
  parameters: {
    task_title: string,
    task_description: string,
    agent_type: "claude-code" | "aider" | "codex",
    working_directory: string,
    timeout_minutes: number
  }
}

{
  name: "agentsmesh_send_instruction",
  description: "向 Worker Pod 发送指令",
  parameters: {
    worker_pod_id: string,
    instruction: string,
    priority: "normal" | "high" | "urgent"
  }
}

{
  name: "agentsmesh_get_worker_status",
  description: "获取 Worker Pod 的当前状态和进度",
  parameters: {
    worker_pod_id: string
  }
}
```

---

## 8. 验收标准

| # | 标准 | 验证方式 |
|---|------|----------|
| 1 | Supervisor 可成功创建 Worker Pod | API 集成测试 |
| 2 | Worker 可接收并执行委托任务 | 端到端测试 |
| 3 | 状态上报延迟 < 2 秒 | 性能测试 |
| 4 | Supervisor 可实时查看所有 Worker 状态 | UI 验证 |
| 5 | Worker 完成后正确通知 Supervisor | 消息流验证 |
| 6 | Supervisor 可正确汇总多 Worker 结果 | 功能测试 |
| 7 | 单个 Worker 失败不影响其他 Worker | 故障注入测试 |

---

## 9. 异常处理

| 场景 | 处理方式 |
|------|----------|
| Worker 创建失败 | Supervisor 收到错误，可选择重试或调整策略 |
| Worker 执行超时 | 自动终止，Supervisor 决定是否重新委托 |
| Worker 断连 | 标记为 unknown，Supervisor 可创建替代 Worker |
| Supervisor 断连 | Worker 继续执行，结果暂存待 Supervisor 恢复 |
| 多 Worker 代码冲突 | Supervisor 负责解决冲突或指定优先级 |
| Runner 资源不足 | 排队等待或提示用户启动更多 Runner |

---

## 10. 使用场景示例

### 场景 1: 全栈功能开发

```
任务: 实现商品评论功能

Supervisor 分解:
├── Worker-Backend: 评论 API (CRUD)
├── Worker-Frontend: 评论组件 + 页面
└── Worker-Testing: 测试用例

执行时间: 30 分钟 (并行) vs 90 分钟 (串行)
```

### 场景 2: Bug 修复 + 测试

```
任务: 修复登录超时问题并添加回归测试

Supervisor 分解:
├── Worker-Debug: 定位问题 + 修复代码
└── Worker-Testing: 编写回归测试 (依赖修复完成)

执行时间: 15 分钟
```

### 场景 3: 代码重构

```
任务: 将 utils 模块拆分为独立包

Supervisor 分解:
├── Worker-1: 拆分 string-utils
├── Worker-2: 拆分 date-utils
├── Worker-3: 拆分 validation-utils
└── Worker-4: 更新所有 import 路径

执行时间: 20 分钟 (并行) vs 60 分钟 (串行)
```

---

## 11. 后续迭代

- [ ] 动态 Worker 扩缩容：根据任务量自动调整 Worker 数量
- [ ] Worker 能力标签：匹配最适合的 Agent 执行特定类型任务
- [ ] 任务优先级队列：Supervisor 智能调度高优任务
- [ ] 跨 Channel 协作：多个 Supervisor 协调更大规模任务
- [ ] 成本优化：根据任务复杂度选择不同规格的 Agent
- [ ] 学习与复用：记录成功的任务分解模式供后续参考
