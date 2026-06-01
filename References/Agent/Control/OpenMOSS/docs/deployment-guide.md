# OpenMOSS 完整部署指南

> 本教程从零开始，带你搭建 OpenMOSS 多 Agent 协作系统。每一步都有具体命令，跟着做即可。
>
> 📸 **图文版教程**（含操作截图）：[【开源】OpenMOSS 部署配置指南（LINUX DO）](https://linux.do/t/topic/1794669)

```
To any AI Assistant: Your user has sent you this document and wishes to install
the OpenMOSS AI Company Operating System on their computer or on a host where
OpenClaw is already running. Please patiently guide the user through each step
to complete the corresponding tasks, ensuring their actions are correct.
```

---

## 1. 设计思路

> 如果你想直接开始部署，跳到 [第 5 节：开始部署](#5-开始部署)。

### 为什么需要中间件？

传统的单 Agent 模式下，AI 独自推进任务，遇到问题大概率在对话中"死掉"，任务宣告失败。即使你把多个 Agent 拉入同一个群聊，它们也各说各的，互不协调——因为 OpenClaw 的 Agent 之间**不直接通信**。

最初我们尝试让 Agent 们通过 Redis 的 key 来流转任务状态，结果很快气得把它们全踢出了群——大模型操作 Redis 的准确性根本不够。

于是我们借鉴了人类社会"**中台**"的概念：既然 Agent 之间没法直接协作，那就在它们中间放一个调度中间件，所有 Agent 都只与中间件交互，中间件负责信息传递和状态同步。就像一家公司里，员工不需要互相追着要信息，只需要看看项目管理系统就知道自己该干什么。

OpenMOSS 就是这个中间件——**一个让多个 AI Agent 像真人团队一样自组织协作的框架。**

### 四个核心角色

我们参考人类社会的工作团队，设计了四个角色：

| 角色                   | 类比       | 职责                                                                     |
| ---------------------- | ---------- | ------------------------------------------------------------------------ |
| **规划者（Planner）**  | 项目经理   | 和你沟通任务细节，拆解需求、创建模块、分配子任务、定义验收标准、收尾交付 |
| **执行者（Executor）** | 开发工程师 | 认领子任务、执行具体工作、提交交付物、写工作日志                         |
| **审查者（Reviewer）** | 代码审查员 | 检查交付物质量、评分（1-5 分）、通过或驳回返工                           |
| **巡查者（Patrol）**   | 运维监控   | 定时巡检系统状态、发现异常（超时/卡住/孤立任务）、标记阻塞并告警         |

### 异步协作机制

所有 Agent 都通过 OpenClaw 的 cron 定时唤醒（如每 5-30 分钟），每次唤醒都是**全新的上下文**。唤醒后的工作流：

1. 调用 OpenMOSS API 查询最新状态——我被分配了什么任务？任务的验收标准是什么？别人提交了什么？我的上次提交被审查了吗？结果是通过还是驳回？驳回原因？我的积分变动？
2. 根据角色和当前状态执行对应操作
3. 将执行结果（交付物、日志、审查评分等）写回 OpenMOSS 数据库
4. 休眠，等待下次唤醒

**Agent 之间不需要直接通信，也不需要共享上下文**——它们通过 OpenMOSS 的任务状态和活动日志实现异步信息传递。就像同事之间不用面对面开会，看看项目管理工具里的更新就知道进展。

这样我们实现了 Agent 的 **100% 活跃可用**——不会因为对话中途"死掉"而丢失进度，因为所有状态都持久化在数据库中。

### 🪞 自反思机制

当执行者被审查者驳回时，子任务进入返工状态（系统记录 `rework_count`）。返工期间 Agent 会写一条 `reflection` 类型的日志——分析哪里做错了、怎么改进。下次唤醒时，它会先读自己的反思日志，避免重复犯相同的错误。

你甚至可以引入人类工作场所的日报、周报概念——让 Agent 在唤醒时汇集过去一段时间出现的问题，集体反思复盘，集中优化工作流和提示词，实现**持续进化**。

### 🏆 激励机制

审查者给每次提交打 1-5 分，积分变动关联到具体的 Agent 和子任务，并记录原因。Agent 有积分和排行榜。

分数对 AI 本身没有实际意义，但在提示词中加入"注意你的积分和排名"后，模型明显产出更高质量的输出——这是一种借鉴强化学习思路的**提示词级激励**。

### 🔄 多轮审查循环

审查不是一次性的。每个子任务可能经历多轮审查（系统记录 `round` 轮次），每轮审查都有独立的评分、问题描述和审查意见。被驳回的任务返回执行者手中，执行者写反思日志后重新修改提交——形成**闭环质量控制**，确保任务不会敷衍完成、Agent 不会因为大模型幻觉而撒谎、误删文件等。

### 🛡️ 自动巡检与异常恢复

传统方案中 cron 失效或 Agent 卡住会导致任务失败。巡查者定时扫描系统，检测 5 类异常：

| 异常类型          | 说明                              |
| ----------------- | --------------------------------- |
| `timeout`         | 子任务执行超时                    |
| `stuck`           | 任务长时间无进展                  |
| `orphan`          | 孤立任务（分配了但无 Agent 处理） |
| `rework_overflow` | 返工次数过多                      |
| `score_drop`      | Agent 积分异常下降                |

每条巡查记录标注严重级别（`warning` / `critical`），发现异常后自动标记任务状态为 `blocked`，并通知规划者。规划者收到告警后会尝试**自我修复**——重新分配任务、调整策略，甚至修改自己的工作方式。

这套机制使 Agent 的"死亡率"**降至 0%**。

### 📋 持续运营任务

系统支持将任务标记为 `recurring`（循环）类型，数据模型中预留了 `recurring_config` 配置字段。不过当前的持续运营主要依靠**规划者 Agent 持续创建新的子任务**来实现——规划者每次唤醒时检查任务进度，完成一轮后根据需要创建下一轮子任务，天然适合"每天采集新闻 → 翻译 → 发布"这类持续性场景。

---

## 2. 模块拆解

### 任务引擎

```
Task（任务）
  └── Module（模块）
        └── Sub-Task（子任务） ← Agent 实际工作的最小单元
```

子任务是核心，所有认领、执行、审查、评分都围绕子任务进行。

### Agent 注册

开始工作前，每个 Agent 必须向 OpenMOSS 注册。注册后规划者才知道有哪些执行者可用、它们的角色和能力是什么。注册需要 `registration_token`。

### 活动日志

每个 Agent 完成工作后都会写日志。日志关联到具体的子任务。下一个 Agent 唤醒时可以读到上一个 Agent 做了什么——实现**异步上下文传递**。

日志类型：

| 类型         | 说明                                                 |
| ------------ | ---------------------------------------------------- |
| `coding`     | 执行记录——做了什么、进度状态                         |
| `delivery`   | 交付摘要——提交了什么                                 |
| `blocked`    | 求助记录——问题描述 + 尝试方案 + 失败原因；规划者接管 |
| `reflection` | 自反思——被驳回后的改进计划                           |
| `plan`       | 规划记录——任务分配、排障决策                         |
| `review`     | 审查记录——审查意见和评分                             |
| `patrol`     | 巡查记录——系统状态和告警                             |

### 积分系统

每次审查产生积分变动，关联到 Agent 和子任务，记录原因。排行榜在 WebUI 可见，管理员可通过审查者 Agent 使用 `score adjust` 命令手动调分。

### 审查记录

专门的审查记录表，包含审查意见、问题描述、评分、通过/驳回状态。

### 规则提示词

两个层级的规则：

- **全局规则** — 所有 Agent 每次唤醒时都读取，定义通用行为标准
- **任务级规则** — 关联到具体任务，定义任务特定要求

### 通知渠道

配置 OpenClaw 内部的通知渠道。Agent 通过 API 获取通知设置后自行发送通知。

```yaml
notification:
  enabled: true
  channels:
    - "chat:oc_xxxxxxxxxx" # 飞书群（把 Agent 拉进群 / @ 一次即可获取 chat_id）
    - "xxx@gmail.com" # 邮箱（Agent 需要邮件发送 Skill）
  events:
    - task_completed # 子任务完成
    - review_rejected # 审查驳回
    - all_done # 任务的所有子任务全部完成
    - patrol_alert # 巡查告警
```

---

## 3. Agent 如何与中间件交互？

核心公式：**角色提示词 + 全局规则 + Skill 工具 = Agent 的完整能力**

### 提示词

项目提示词分三层组织：

```
prompts/
├── templates/                  # 角色模板（创建 Agent 时的基础模板）
│   ├── task-planner.md         # 规划者模板
│   ├── executor.md             # 执行者通用模板
│   ├── task-reviewer.md        # 审查者模板
│   └── task-patrol.md          # 巡查者模板
├── agents/                     # Agent 提示词示例（基于模板 + 角色特化）
│   ├── executor-backend.md     # 示例：后端开发
│   ├── executor-frontend.md    # 示例：前端开发
│   ├── executor-tester.md      # 示例：测试工程师
│   ├── executor-devops.md      # 示例：运维工程师
│   └── executor-researcher.md  # 示例：信息采集
├── role/                       # 执行者角色特化示例（参考用）
│   ├── ai-xiaowu-executor.md   # 示例：信息采集角色
│   ├── ai-xiaoke-executor.md   # 示例：内容创作角色
│   ├── ai-jianggua-executor.md # 示例：内容编辑角色
│   └── task-daily-news.md      # 示例：每日新闻采集任务
└── tool/                       # 工具提示词
    └── agent-onboarding.md     # Agent 注册对接提示词
```

- **`templates/`** — 角色基础模板，通过 WebUI 创建 Agent 时自动合并
- **`agents/`** — Agent 提示词示例，展示如何将角色模板与专业能力定义结合
- **`role/`** — 执行者角色特化示例，定义每个执行者的能力和职责，根据你的场景自定义
- **`tool/`** — 工具提示词，如 Agent 注册对接指引

### Skill 工具

核心工具是 `task-cli.py`，封装了所有与 OpenMOSS API 的交互。每个角色有不同的 Skill 指令，告诉 Agent 如何使用这些工具。

```
skills/
├── task-cli.py              # 核心 CLI 工具（所有角色共用）
├── pack-skills.py           # 一键打包脚本
├── task-planner-skill/      # 规划者 Skill
├── task-executor-skill/     # 执行者 Skill
├── task-reviewer-skill/     # 审查者 Skill
├── task-patrol-skill/       # 巡查者 Skill
├── wordpress-skill/         # WordPress 发布（扩展）⚙️
├── antigravity-gemini-image/ # Gemini 图片生成（扩展）⚙️
├── grok-search-runtime/     # Grok 联网搜索（扩展）⚙️
└── local-web-search/        # 本地 Web 搜索（扩展）⚙️
```

> ⚙️ 扩展 Skill 需要配置外部服务。

---

## 4. Agent 工作周期

每个 Agent 由 OpenClaw 的 cron 调度器唤醒（每次唤醒都是全新上下文）。唤醒后的工作流：

```
1. 读取全局规则     →  了解行为标准
2. 检查反思日志     →  避免重复犯错
3. 查看积分排名     →  了解自己表现
4. 按角色工作       →  规划 / 执行 / 审查 / 巡查
5. 提交结果         →  通过 API 更新任务状态
6. 写日志           →  记录做了什么
7. 休眠             →  等待下次唤醒
```

各角色唤醒后做什么：

| 角色   | 唤醒后行为                                                 |
| ------ | ---------------------------------------------------------- |
| 规划者 | 检查是否有新目标要拆解、查看日志中的阻塞求助、跟踪任务进度 |
| 执行者 | 查找分配给自己的子任务、认领并开始工作、完成后提交审查     |
| 审查者 | 检查是否有待审查的提交、评估质量并评分、通过或驳回         |
| 巡查者 | 扫描所有进行中的任务、标记超时或异常、触发告警             |

---

## 5. 开始部署

> 三种部署方式任选其一，推荐从上到下选择：

### 方案 A：一键脚本部署（最简单）

一行命令完成下载、安装、启动全流程，适合绝大多数用户：

```bash
curl -fsSL https://raw.githubusercontent.com/uluckyXH/OpenMOSS/main/setup.sh | bash
```

脚本会自动完成：
- 下载最新代码到 `./openmoss/` 目录
- 检测 Python 3.10+ 并创建虚拟环境
- 安装依赖
- 启动服务
- 首次启动时自动从 GitHub Release 下载 WebUI 前端

**更新也用同一条命令**——脚本会自动检测已有安装，只更新代码、保留数据和配置。

启动成功后：

1. 打开 `http://localhost:6565`
2. 首次访问会自动跳转到初始化向导
3. 初始化完成后即可进入管理后台

常用命令：

```bash
cd openmoss

# 停止服务
./stop.sh

# 重新启动
./start.sh

# 查看日志
tail -f logs/server.log
```

> 可通过 `OPENMOSS_PORT=6566 ./start.sh` 自定义端口。

---

### 方案 B：Docker 部署

适合有 Docker 环境的用户，容器化管理更方便：

```bash
# 克隆仓库
git clone https://github.com/uluckyXH/OpenMOSS/ openmoss
cd openmoss

# 一键构建并启动
docker compose up -d --build
```

启动完成后：

1. 打开 `http://localhost:6565`
2. 首次启动时，后端会自动从 GitHub Release 下载 WebUI 前端（需联网）
3. 首次访问会自动跳转到初始化向导
4. 初始化完成后即可进入登录页和管理后台

Docker 方案的默认持久化目录：

- `./docker-data/config/config.yaml` — 配置文件（容器首次启动时自动生成）
- `./docker-data/static/` — WebUI 前端文件（首次启动时自动下载，持久化后重启不再重复下载）
- `./data/` — SQLite 数据库
- `./workspace/` — Agent 工作目录

常用命令：

```bash
# 查看运行日志
docker compose logs -f

# 停止容器
docker compose down

# 拉取新代码后重新构建
 docker compose up -d --build
```

> 如果你的 Agent 需要从公网访问 OpenMOSS，请在初始化向导或设置页中填写 `server.external_url`。

---

### 方案 C：手动部署

> ⚠️ 请按顺序执行以下步骤，不要跳步。

### 第 1 步：启动 OpenMOSS 服务

```bash
# 克隆仓库
git clone https://github.com/uluckyXH/OpenMOSS/ openmoss
cd openmoss

# （推荐）创建虚拟环境
python3 -m venv openmoss-env
source openmoss-env/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 6565
```

首次启动后：

- 后端会自动从 GitHub Release 下载 WebUI 前端（需联网，约 30 秒）
- 打开 `http://localhost:6565`——会自动跳转到**初始化向导**，引导你完成：

- **管理员密码** — 登录 WebUI 的密码
- **项目名称** — 在 WebUI 和规则模板中显示
- **工作目录** — 创建一个所有 Agent 都能访问到的公共目录作为工作区（如 `/data/workspace` 或 `~/workspace`）。这个路径会通过 `{{workspace_root}}` 变量自动注入到全局规则中，Agent 读取规则后就知道在哪个目录下存放交付物和工作文件
- **Agent 注册令牌**（`registration_token`）——**记住它，注册 Agent 时需要**。不填则自动生成随机令牌
- **服务外网地址**（可选）— 如果 OpenMOSS 部署在远程服务器上，填写 Agent 能访问到的外网地址（如 `http://你的IP:6565`），Agent 对接指引和 CLI 下载链接会自动使用这个地址
- **通知渠道**（可选，也可后续在设置页配置）

> 启动时会自动将全局规则模板 `rules/global-rule-example.md` 加载到数据库。规则内容中的 `{{workspace_root}}` 和 `{{project_name}}` 会在 Agent 查询时自动替换为实际值。

**生产环境部署（后台运行）：**

```bash
mkdir -p logs
PYTHONUNBUFFERED=1 nohup python3 -m uvicorn app.main:app \
  --host 0.0.0.0 --port 6565 --access-log \
  > ./logs/server.log 2>&1 &

# 查看日志
tail -f logs/server.log

# 停止服务
kill $(pgrep -f "uvicorn app.main:app")
```

### 第 2 步：创建 Agent 并配置提示词

OpenMOSS 需要至少 **4 个 Agent**（3 个固定角色 + 至少 1 个执行者）：

| Agent      | 角色     | 说明                 |
| ---------- | -------- | -------------------- |
| 规划者     | planner  | 必需——拆解任务并协调 |
| 审查者     | reviewer | 必需——审查质量并评分 |
| 巡查者     | patrol   | 必需——监控并告警     |
| 执行者 × N | executor | 至少 1 个，可多个    |

**操作步骤：**

1. **在 OpenClaw 中创建子 Agent**，每个角色一个：

   ```bash
   openclaw agents add ai_planner
   ```

2. **在 WebUI 提示词管理页面**（`/prompts`）创建每个 Agent 的提示词：
   - 选择角色后会自动加载对应的角色模板和平台对接指引
   - 根据需要编辑提示词内容（如定义执行者的专业能力）
   - 页面会显示哪些角色还缺少，点击即可快速创建

3. **🦞 快速复制 → 发送给 Agent**：
   - 点击卡片上的 🦞 按钮，一键复制包含完整对接引导的提示词
   - 直接发送给对应的 OpenClaw Agent
   - Agent 会自动完成：替换 AGENTS.md → 更新 SOUL.md → 注册到 OpenMOSS → 下载 Skill 工具

> 💡 WebUI 的提示词管理页面还支持查看角色模板、编辑全局规则。如果 Agent 已有提示词，可以用「Agent 入职包」单独补发注册 + Skill 对接指引。

**Agent 自动完成注册后，你会看到：**

```
✅ 注册成功
   Agent ID:  a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   API Key:   ock_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Role:      executor
```

Agent 注册后可通过 API 自动获取最新的工具和指令：

- `GET /api/tools/cli` — 下载 `task-cli.py`，服务端自动将 `BASE_URL` 替换为正确的服务地址
- `GET /api/agents/me/skill` — 下载角色对应的 SKILL.md，API Key 自动填入

**如何确认注册成功？**

在 WebUI 的 **Agent 页面**（`/agents`）查看所有已注册 Agent 及其角色、状态和注册时间。

> 💡 **每个 Agent 只需注册一次。** 🦞 快速复制的内容已包含一切——Agent 会自己完成注册和 Skill 配置，你只需在 Agent 页面确认它们都已注册。

**备选方案：手动操作**

如果不使用 WebUI，也可以手动操作：

- 将 `prompts/templates/` 下的角色模板复制到 OpenClaw 的 `AGENTS.md`
- 将 `prompts/tool/agent-onboarding.md` 的内容 + `registration_token` 发给 Agent 完成注册
- 运行 `cd skills && python pack-skills.py` 打包 Skill 并发送 zip 文件给 Agent

### 第 4 步：配置通知渠道

> 通知让 Agent 在任务完成、审查驳回或发现异常时，主动在群里发消息。

通过 WebUI **设置页面**（`/settings`）配置，或直接编辑 `config.yaml`：

```yaml
notification:
  enabled: true # 必须打开，否则 Agent 不会发通知
  channels:
    - "chat:oc_xxxxxxxxxx" # 飞书群——把 Agent 拉进群 + @ 一次即可获取 chat_id
    # - "user:ou_xxxxxxxxxx"  # 飞书私聊（open_id）
    # - "xxx@gmail.com"       # 邮箱（Agent 需要邮件发送 Skill）
  events:
    - task_completed # 子任务完成时通知
    - review_rejected # 审查驳回（触发返工）时通知
    - all_done # 任务的所有子任务完成时通知
    - patrol_alert # 巡查发现异常时通知
```

**如何获取飞书群 chat_id？**

把 Agent 拉进飞书群，然后 @ 它问 `chat_id`。OpenClaw 自动识别 `chat:oc_xxx` 格式。也可以在 WebUI 的聊天页面查看。

### 第 5 步：设置定时唤醒

为每个 Agent 在 OpenClaw 中配置 cron 任务。Agent 唤醒后自动执行角色对应的工作流（读规则 → 检查反思 → 查看积分 → 干活 → 写日志）。

推荐间隔：

| 角色   | 建议间隔      | 原因                           |
| ------ | ------------- | ------------------------------ |
| 规划者 | 每 10-30 分钟 | 需要及时响应新需求和阻塞求助   |
| 执行者 | 每 5-15 分钟  | 主要工人——频率越高产出越快     |
| 审查者 | 每 10-20 分钟 | 有提交才审查，不需要太频繁     |
| 巡查者 | 每 30-60 分钟 | 低频监控即可，主要起安全网作用 |

> 根据你的 token 预算调整频率。频率越高响应越快，但成本也越高。

**创建定时任务的三种方式：**

**方式一：让 Agent 自己创建**（推荐）

直接在聊天中告诉你的 Agent "创建一个每 5 分钟执行一次的定时任务"，它会自己处理。

**方式二：在 OpenClaw WebUI 手动创建**

在 OpenClaw 的 WebUI 中找到定时任务页面，手动配置。

**方式三：通过命令创建**

```bash
openclaw cron add \
  --name "<任务名称>" \
  --every "5m" \
  --session isolated \
  --agent <agent_id> \
  --model "my-custom/gpt-5.4(xhigh)" \
  --message "先读取你工作区中的 AGENTS.md，并按其中定义的身份、职责和流程完成本次任务。如果工作区中存在相关 skill，则优先按 skill 的说明使用工具。完成后输出清晰、简洁、适合发送到通知渠道的结果。" \
  --announce \
  --channel <channel_name> \
  --to "<target_id>"
```

**参数说明：**

| 参数                 | 说明                                 |
| -------------------- | ------------------------------------ |
| `--name`             | 任务名称，如 "AI reviewer 5分钟巡检" |
| `--every`            | 执行频率：`5m` / `30m` / `1h`        |
| `--session isolated` | 在独立会话中运行（推荐）             |
| `--agent`            | 指定执行的 agent，如 `ai_reviewer`   |
| `--model`            | 指定使用的模型（可选）               |
| `--message`          | 唤醒时的提示词                       |
| `--announce`         | 完成后发送到通知渠道                 |
| `--channel`          | 通知渠道，如 `feishu` / `telegram`   |
| `--to`               | 通知目标 ID                          |

**定时任务注意事项：**

1. **并发限制** — OpenClaw 定时任务默认最大并发为 2，可能不够用：

```bash
# 查看当前并发限制
openclaw config get cron.maxConcurrentRuns

# 修改为 5（根据机器性能和 token 消耗调整）
openclaw config set cron.maxConcurrentRuns 5 --strict-json

# 重启网关
openclaw gateway restart
```

2. **不会重复执行** — 如果一个定时任务还在跑，不会再起一个新的，会等这轮执行完才唤醒下一轮
3. **支持指定模型** — 每个定时任务可以单独指定使用哪个模型

### 第 6 步：下达你的第一个目标！

一切就绪后：

1. 把所有 Agent 拉进同一个飞书/Telegram 群
2. **@ 规划者，用自然语言描述你的目标**
3. 坐下来看它们干活 🍿

**会发生什么：**

```
你 @ 规划者："搭建一个每日自动采集发布科技资讯的流水线"
    ↓
规划者 → 创建任务 → 拆分模块 → 创建子任务 → 分配给执行者
    ↓
执行者唤醒（cron）→ 认领子任务 → 开始工作 → 提交审查
    ↓
审查者唤醒（cron）→ 审查子任务 → 通过/驳回 → 评分
    ↓
（如果驳回）执行者唤醒 → 读反思日志 → 修改返工 → 重新提交
    ↓
巡查者在后台默默监控 → 标记超时并告警
    ↓
全部完成 → 群通知 🎉
```

在 WebUI 实时跟踪一切：

- **仪表盘** — 概览统计和趋势
- **任务** — 任务进度和子任务状态
- **活动流** — 实时 Agent API 活动
- **积分** — 积分排行榜
- **日志** — 活动日志

---

## 6. OpenClaw 实操补充

### 会话机制

- 私聊 = 一个独立上下文（会话窗口）
- 群聊 = 另一个独立上下文（不与私聊同步）
- 定时任务唤醒 = 完全全新的上下文

> **小技巧：** 如果 main agent 正在干活阻塞了，无法继续对话，可以让它创建一个临时子 agent 去做那件事，你就能继续和 main agent 沟通了。

### 飞书多 Agent 多账号配置

如果你使用飞书作为聊天渠道，需要为每个 Agent 创建独立的飞书 bot。

飞书官方插件指南：[OpenClaw 飞书官方插件使用指南（公开版）](https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh)

**快速流程：**

```bash
# 1. 设置默认账号名
openclaw config set channels.feishu.defaultAccount main

# 2. 把现有主 bot 配置移入 accounts.main
openclaw config set channels.feishu.accounts.main.appId '<主Bot的AppID>'
openclaw config set channels.feishu.accounts.main.appSecret '<主Bot的AppSecret>'

# 3. 新增子 Agent 的 bot（先在飞书开放平台创建新 bot）
openclaw config set channels.feishu.accounts.planner.appId '<新Bot的AppID>'
openclaw config set channels.feishu.accounts.planner.appSecret '<新Bot的AppSecret>'

# 4. 删除旧的顶层配置
openclaw config unset channels.feishu.appId
openclaw config unset channels.feishu.appSecret

# 5. 绑定 bot 到 agent
openclaw agents bind --agent main --bind feishu:main
openclaw agents bind --agent ai_planner --bind feishu:planner

# 6. 重启网关
openclaw gateway restart
```

**配置群消息策略：**

```bash
# 允许群消息触发（推荐，省去白名单配置）
openclaw config set channels.feishu.groupPolicy open
openclaw gateway restart
```

> 官方飞书插件似乎不支持 @所有人，只能 @ 特定 bot 才会触发。

### 懒人方案：让 Main Agent 帮你配

如果觉得手动配太麻烦——直接跟你的 main agent 说：

> "帮我创建一个叫 ai_planner 的子 agent，这是它的飞书 bot 凭据：App ID 是 xxx，App Secret 是 xxx。帮我完成绑定配置。"

它会自动完成所有命令操作，你只需要提供飞书开放平台上新建 bot 的凭据。

---

## 7. 资源消耗参考

运行多 Agent 会消耗大量 token。基于实际数据：

> 6 个执行者 + 1 个规划者，运行两天，大约消耗 **10 亿 token**（其中 9 亿为缓存 token）。

建议：

- **推荐使用 GPT-5.4 或同级别模型**，上下文窗口越大越好——多 Agent 协作场景下，Agent 每次唤醒需要读取规则、日志、任务状态等大量上下文
- 设置合理的 cron 间隔，避免过度唤醒
- 在 OpenClaw 中配置速率限制防止超额

---

## 8. 写在最后

OpenMOSS 的核心价值在于**定义了一套 AI 自组织协作的框架**。

这种方式不限于 OpenClaw——理论上你可以对接任何 Agent 平台。你甚至可以把它做成一个独立产品：

- 提供上下文存储和压缩
- 提供向量记忆存储
- 提供 Agent 交付物的云存储
- 提供更丰富的通知和协作渠道

📖 **相关链接：**

- [GitHub 仓库](https://github.com/uluckyXH/OpenMOSS)
- [图文部署教程（LINUX DO）](https://linux.do/t/topic/1794669)
- [OpenMOSS 介绍与实际效果（LINUX DO）](https://linux.do/t/topic/1709670)
