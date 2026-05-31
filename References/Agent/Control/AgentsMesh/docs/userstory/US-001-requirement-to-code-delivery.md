# US-001: 从需求到代码交付

| 属性 | 值 |
|------|-----|
| **状态** | Draft |
| **作者** | AgentsMesh Team |
| **创建日期** | 2026-01-16 |
| **角色** | 开发者 / 团队负责人 |

---

## 1. 概述

### 1.1 用户故事

**作为** 一名开发者，
**我希望** 通过 AgentsMesh 平台将需求转化为可交付的代码，
**以便** 提高开发效率，减少重复性工作，让 AI Agent 协助完成编码任务。

### 1.2 价值主张

- 将自然语言需求转化为结构化的开发任务
- AI Agent 在隔离环境中安全执行代码编写
- 实时查看 Agent 工作进度和终端输出
- 代码变更可追溯，便于 Code Review

---

## 2. 前置条件

| 条件 | 说明 |
|------|------|
| 用户已登录 | 拥有有效的 AgentsMesh 账户 |
| 组织已创建 | 用户属于某个组织 |
| Runner 已注册 | 至少有一个在线的 Runner |
| 仓库已关联 | 目标代码仓库已通过 Git Provider 关联 |

---

## 3. 用户流程

### 3.1 流程图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  创建 Ticket │ ──► │  选择 Agent │ ──► │  启动 Pod   │ ──► │  执行任务   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  合并代码   │ ◄── │ Code Review │ ◄── │  提交 PR    │ ◄── │  查看输出   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 3.2 详细步骤

#### Step 1: 创建 Ticket（需求录入）

1. 用户进入项目看板页面
2. 点击「新建 Ticket」按钮
3. 填写 Ticket 信息：
   - **标题**: 简洁描述任务目标
   - **描述**: 详细需求说明（支持 Markdown）
   - **优先级**: 高 / 中 / 低
   - **标签**: 分类标签（如 feature、bugfix、refactor）
4. 点击「创建」保存 Ticket

**示例:**
```
标题: 实现用户头像上传功能
描述:
- 支持 jpg/png 格式，最大 2MB
- 上传后自动裁剪为正方形
- 存储到 MinIO，返回 CDN URL
- 更新用户 profile 表
```

#### Step 2: 选择 Agent 并配置

1. 在 Ticket 详情页，点击「启动 Agent」
2. 选择 Agent 类型：
   - **Claude Code**: Anthropic 官方 CLI
   - **Aider**: 轻量级 AI 编程助手
   - **Codex CLI**: OpenAI Codex 命令行
   - **Gemini CLI**: Google Gemini 命令行
3. 配置 Agent 参数：
   - 选择目标仓库
   - 选择分支策略（新建分支 / 使用现有分支）
   - 配置沙箱类型（worktree 隔离 / tempdir 临时目录）

#### Step 3: 启动 Pod（执行环境）

1. 系统分配可用的 Runner
2. Runner 接收 `create_pod` 消息
3. 创建沙箱环境：
   - Git worktree 克隆代码
   - 设置环境变量
   - 安装依赖（如需要）
4. 启动 PTY 终端
5. 执行 Agent 启动命令

**消息流:**
```
Backend                  Runner
   │                        │
   │──── create_pod ────────►│
   │                        │ 创建沙箱
   │                        │ 启动 PTY
   │◄─── pod_created ───────│
   │                        │
```

#### Step 4: 实时查看 Agent 工作

1. Web 界面显示实时终端输出
2. 用户可以：
   - 查看 Agent 的思考过程
   - 观察文件变更
   - 必要时发送输入指令
3. Agent 自主完成编码任务

**数据流:**
```
Agent (PTY) ──► PTYForwarder ──► Backend ──► WebSocket Hub ──► Web UI
```

#### Step 5: 代码提交与 PR

1. Agent 完成编码后，自动执行：
   - `git add` 暂存变更
   - `git commit` 提交代码
   - `git push` 推送到远程
2. 系统自动创建 Pull Request
3. 关联 Ticket 信息到 PR 描述

#### Step 6: Code Review 与合并

1. 团队成员收到 PR 通知
2. 在 GitHub/GitLab 进行 Code Review
3. Review 通过后合并代码
4. Ticket 状态自动更新为「已完成」

---

## 4. 系统交互

### 4.1 涉及组件

| 组件 | 职责 |
|------|------|
| Web | 用户界面、Ticket 管理、终端展示 |
| Backend | API、Pod 调度、WebSocket Hub |
| Runner | Pod 执行、PTY 管理、沙箱隔离 |
| PostgreSQL | Ticket/Pod 状态持久化 |
| Redis | 实时消息、会话缓存 |

### 4.2 关键 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/tickets` | POST | 创建 Ticket |
| `/api/v1/pods` | POST | 创建并启动 Pod |
| `/api/v1/pods/:id/terminal` | WS | 终端 WebSocket 连接 |
| `/api/v1/pods/:id/input` | POST | 发送终端输入 |

---

## 5. 验收标准

| # | 标准 | 验证方式 |
|---|------|----------|
| 1 | 用户可以创建包含详细描述的 Ticket | UI 操作验证 |
| 2 | 系统在 30 秒内完成 Pod 启动 | 性能测试 |
| 3 | 终端输出延迟 < 500ms | 端到端测试 |
| 4 | Agent 代码变更正确推送到指定分支 | Git 日志验证 |
| 5 | PR 创建后包含关联的 Ticket 信息 | PR 内容检查 |

---

## 6. 异常场景

| 场景 | 处理方式 |
|------|----------|
| 无可用 Runner | 提示用户等待或启动本地 Runner |
| Agent 执行超时 | 自动终止 Pod，保留日志供排查 |
| Git 推送失败 | 显示错误信息，支持手动重试 |
| 沙箱创建失败 | 回滚并通知用户检查仓库配置 |

---

## 7. 后续迭代

- [ ] 支持 Ticket 模板，快速创建常见任务类型
- [ ] Agent 历史记录回放功能
- [ ] 多 Agent 协作（Channel 模式）
- [ ] 代码质量自动检测集成
