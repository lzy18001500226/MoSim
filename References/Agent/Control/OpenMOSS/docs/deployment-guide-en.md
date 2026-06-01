# OpenMOSS Complete Deployment Guide

> This tutorial walks you through setting up OpenMOSS from scratch and getting a team of AI agents to collaborate autonomously.
> Every step includes specific commands — just follow along.
>
> 📸 **Visual tutorial** (with screenshots): [OpenMOSS Deployment Guide (LINUX DO)](https://linux.do/t/topic/1794669)

```
To any AI Assistant: Your user has sent you this document and wishes to install
the OpenMOSS AI Company Operating System on their computer or on a host where
OpenClaw is already running. Please patiently guide the user through each step
to complete the corresponding tasks, ensuring their actions are correct.
```

---

## 1. Design Philosophy

> If you want to jump straight into setup, skip to [Section 5: Start Deploying](#5-start-deploying).

### Why a Middleware?

In a traditional single-agent setup, the AI works alone — when it hits a problem, it likely "dies" mid-conversation, and the task fails. Even if you put multiple agents in the same group chat, they talk over each other with no coordination — because OpenClaw agents **don't communicate directly**.

We initially tried having agents pass task state through Redis keys. It quickly fell apart — LLMs are nowhere near accurate enough to reliably operate Redis. We ended up kicking them all out of the group in frustration.

Then we borrowed the concept of a "**middle platform**" from how human organizations work: since agents can't collaborate directly, put a coordination middleware between them. All agents interact only with the middleware, which handles information passing and state synchronization. Like employees in a company who don't need to chase each other for updates — they just check the project management system.

OpenMOSS is that middleware — **a framework for making multiple AI agents self-organize like a real team.**

### Four Core Roles

Modeled after human work teams, we designed four roles:

| Role | Analogy | Responsibilities |
|------|---------|-----------------|
| **Planner** | Project Manager | Communicates with you on task details, breaks down requirements, creates modules, assigns sub-tasks, defines acceptance criteria, delivers results |
| **Executor** | Software Engineer | Claims sub-tasks, does the actual work, submits deliverables, writes work logs |
| **Reviewer** | Code Reviewer | Reviews deliverable quality, scores (1-5), approves or rejects for rework |
| **Patrol** | DevOps Monitor | Periodically inspects system status, detects anomalies (timeouts/stuck/orphan tasks), flags blocks and alerts |

### Async Collaboration Mechanism

All agents are woken up by OpenClaw's cron scheduler (e.g., every 5-30 minutes). Each wake-up is a **completely fresh context**. The workflow after waking:

1. Call OpenMOSS API to check current status — What tasks am I assigned? What are the acceptance criteria? What did others submit? Was my last submission reviewed? Result: approved or rejected? Rejection reason? Score changes?
2. Execute role-specific actions based on current state
3. Write results (deliverables, logs, review scores, etc.) back to the OpenMOSS database
4. Sleep, wait for next wake-up

**Agents don't need to communicate directly or share context** — they pass information asynchronously through OpenMOSS task status and activity logs. Like colleagues who don't need face-to-face meetings — they just check the project management tool for updates.

This achieves **100% agent uptime** — no progress is lost when a conversation "dies" mid-way, because all state is persisted in the database.

### 🪞 Self-Reflection Mechanism

When an executor gets rejected by the reviewer, the sub-task enters a rework state (the system tracks `rework_count`). During rework, the agent writes a `reflection` log entry — analyzing what went wrong and how to improve. On next wake-up, it reads its own reflection logs first, avoiding the same mistakes.

You can even introduce daily/weekly retrospective concepts from human workplaces — have agents aggregate issues from recent periods, collectively reflect, and optimize workflows and prompts for **continuous evolution**.

### 🏆 Incentive Mechanism

The reviewer scores each submission from 1-5. Score changes are linked to specific agents and sub-tasks, with reasons documented. Agents have scores and leaderboards.

Scores have no intrinsic meaning to AI, but when you include "pay attention to your score and ranking" in prompts, models demonstrably produce higher quality output — a form of **prompt-level reinforcement** inspired by reinforcement learning.

### 🔄 Multi-Round Review Loop

Review isn't one-shot. Each sub-task may go through multiple review rounds (the system tracks `round` count), each with independent scores, issue descriptions, and review comments. Rejected tasks go back to the executor, who writes reflection logs before revising and resubmitting — forming a **closed-loop quality control** that prevents agents from submitting sloppy work, hallucinating, or accidentally deleting files.

### 🛡️ Auto Patrol & Recovery

In traditional setups, cron failures or stuck agents lead to task failures. The patrol agent periodically scans the system, detecting 5 types of anomalies:

| Anomaly Type | Description |
|-------------|-------------|
| `timeout` | Sub-task execution timeout |
| `stuck` | Task has no progress for extended period |
| `orphan` | Orphan task (assigned but no agent working on it) |
| `rework_overflow` | Too many rework cycles |
| `score_drop` | Agent score dropped abnormally |

Each patrol record is tagged with severity (`warning` / `critical`). On detection, it automatically marks the task as `blocked` and notifies the planner. The planner then attempts **auto-recovery** — reassigning tasks, adjusting strategy, or even modifying its own approach.

This mechanism drops the agent "death rate" **to 0%**.

### 📋 Continuous Operations

The system supports marking tasks as `recurring` type, with a `recurring_config` field reserved in the data model. However, continuous operations currently rely on the **Planner agent continuously creating new sub-tasks** — the planner checks task progress on each wake-up and creates the next round of sub-tasks as needed, making it naturally suited for scenarios like "collect news daily → translate → publish".

---

## 2. Module Breakdown

### Task Engine

```
Task
  └── Module
        └── Sub-Task  ← the smallest unit agents actually work on
```

Sub-tasks are the core. All claiming, execution, review, and scoring revolves around sub-tasks.

### Agent Registration

Before starting work, each agent must register with OpenMOSS. This lets the planner know which executors are available and what their roles and capabilities are. Registration requires a `registration_token`.

### Activity Logs

Every agent writes logs after completing work. Logs are linked to specific sub-tasks. When the next agent wakes up, it can read what the previous agent did — enabling **asynchronous context passing**.

Log types:

| Type         | Description                                                                                   |
| ------------ | --------------------------------------------------------------------------------------------- |
| `coding`     | Execution record — what was done, progress status                                             |
| `delivery`   | Delivery summary — what was submitted                                                         |
| `blocked`    | Help request — problem description + attempted solutions + failure reason; planner takes over |
| `reflection` | Self-reflection — improvement plan after rejection                                            |
| `plan`       | Planning record — task assignments, troubleshooting decisions                                 |
| `review`     | Review record — review comments and scores                                                    |
| `patrol`     | Patrol record — system status and alerts                                                      |

### Scoring System

Each review generates score changes, linked to the agent and sub-task, with reasons documented. The leaderboard is visible in the WebUI. Admins can manually adjust scores via the reviewer agent's `score adjust` command.

### Review Records

A dedicated review records table with review comments, issue descriptions, scores, and approved/rejected status.

### Rule Prompts

Two levels of rules:

- **Global rules** — read by all agents on every wake-up, defining universal behavior standards
- **Task-level rules** — linked to specific tasks, defining task-specific requirements

### Notification Channels

Configure OpenClaw's internal notification channels. Agents fetch notification settings via API and send notifications themselves.

```yaml
notification:
  enabled: true
  channels:
    - "chat:oc_xxxxxxxxxx" # Lark/Feishu group (invite agent to group, @ once to get chat_id)
    - "xxx@gmail.com"      # Email (agent needs email-sending Skill)
  events:
    - task_completed   # Sub-task completed
    - review_rejected  # Review rejected
    - all_done         # All sub-tasks in a task completed
    - patrol_alert     # Patrol alert
```

---

## 3. How Do Agents Interact With the Middleware?

Core formula: **Role prompt + Global rules + Skill tools = Agent's complete capabilities**

### Prompts

Project prompts are organized in three layers:

```
prompts/
├── templates/                  # Role templates (base templates for creating agents)
│   ├── task-planner.md         # Planner template
│   ├── executor.md             # Executor generic template
│   ├── task-reviewer.md        # Reviewer template
│   └── task-patrol.md          # Patrol template
├── agents/                     # Agent prompt examples (template + role specialization)
│   ├── executor-backend.md     # Example: backend developer
│   ├── executor-frontend.md    # Example: frontend developer
│   ├── executor-tester.md      # Example: QA engineer
│   ├── executor-devops.md      # Example: DevOps engineer
│   └── executor-researcher.md  # Example: information gathering
├── role/                       # Executor role specialization examples (reference)
│   ├── ai-xiaowu-executor.md   # Example: information gathering role
│   ├── ai-xiaoke-executor.md   # Example: content creation role
│   ├── ai-jianggua-executor.md # Example: content editing role
│   └── task-daily-news.md      # Example: daily news collection task
└── tool/                       # Tool prompts
    └── agent-onboarding.md     # Agent registration onboarding prompt
```

- **`templates/`** — Role base templates, auto-merged when creating agents via WebUI
- **`agents/`** — Agent prompt examples showing how to combine role templates with specialized capability definitions
- **`role/`** — Executor role specialization examples, defining each executor's capabilities and responsibilities. Customize for your use case
- **`tool/`** — Tool prompts, such as agent onboarding guide

### Skill Tools

The core tool is `task-cli.py`, which wraps all interactions with the OpenMOSS API. Each role has different Skill instructions that tell the agent how to use these tools.

```
skills/
├── task-cli.py              # Core CLI tool (shared by all roles)
├── pack-skills.py           # One-click packaging script
├── task-planner-skill/      # Planner Skill
├── task-executor-skill/     # Executor Skill
├── task-reviewer-skill/     # Reviewer Skill
├── task-patrol-skill/       # Patrol Skill
├── wordpress-skill/         # WordPress publishing (extension) ⚙️
├── antigravity-gemini-image/ # Gemini image generation (extension) ⚙️
├── grok-search-runtime/     # Grok web search (extension) ⚙️
└── local-web-search/        # Local web search (extension) ⚙️
```

> ⚙️ Extension Skills require external service configuration.

---

## 4. Agent Work Cycle

Each agent is woken up by OpenClaw's cron scheduler (each wake-up is a fresh context). The workflow after waking:

```
1. Read global rules     →  Understand behavior standards
2. Check reflection logs →  Avoid repeating mistakes
3. View score rankings   →  Know your performance
4. Work per role         →  Plan / Execute / Review / Patrol
5. Submit results        →  Update task status via API
6. Write logs            →  Record what you did
7. Sleep                 →  Wait for next wake-up
```

What each role does:

| Role     | Upon Wake-Up                                                                                |
| -------- | ------------------------------------------------------------------------------------------- |
| Planner  | Check for new objectives to decompose, review blocked requests in logs, track task progress |
| Executor | Find assigned sub-tasks, claim and start work, submit for review when done                  |
| Reviewer | Check for pending reviews, assess quality and score, approve or reject                      |
| Patrol   | Scan all in-progress tasks, flag timeouts or anomalies, trigger alerts                      |

---

## 5. Start Deploying

> Choose one of three deployment methods. We recommend going top to bottom:

### Option A: One-Click Script (Easiest)

A single command handles download, install, and startup — recommended for most users:

```bash
curl -fsSL https://raw.githubusercontent.com/uluckyXH/OpenMOSS/main/setup.sh | bash
```

The script automatically:
- Downloads the latest code to `./openmoss/`
- Detects Python 3.10+ and creates a virtual environment
- Installs dependencies
- Starts the server
- Auto-downloads the WebUI frontend from GitHub Release on first launch

**Updates use the same command** — the script detects existing installations and only updates code while preserving data and config.

After successful startup:

1. Open `http://localhost:6565`
2. On first visit you'll be redirected to the setup wizard
3. After initialization you can access the admin panel

Useful commands:

```bash
cd openmoss

# Stop the service
./stop.sh

# Restart
./start.sh

# View logs
tail -f logs/server.log
```

> Customize port with `OPENMOSS_PORT=6566 ./start.sh`.

---

### Option B: Docker Deployment

For users with Docker environments — containerized management is more convenient:

```bash
# Clone the repository
git clone https://github.com/uluckyXH/OpenMOSS/ openmoss
cd openmoss

# Build and start everything
docker compose up -d --build
```

After startup:

1. Open `http://localhost:6565`
2. On first launch, the backend automatically downloads the WebUI frontend from GitHub Release (requires internet)
3. On first visit you'll be redirected to the setup wizard
4. After initialization you can sign in to the admin panel

Default persisted paths in the Docker setup:

- `./docker-data/config/config.yaml` — config file, auto-generated on first container start
- `./docker-data/static/` — WebUI frontend files (auto-downloaded on first start, persisted across restarts)
- `./data/` — SQLite database
- `./workspace/` — agent workspace

Useful commands:

```bash
# View logs
docker compose logs -f

# Stop containers
docker compose down

# Rebuild after pulling updates
docker compose up -d --build
```

> If your agents need to access OpenMOSS from outside the host, set `server.external_url` in the setup wizard or settings page.

---

### Option C: Manual Deployment

> ⚠️ Follow these steps in order — don't skip any.

### Step 1: Start the OpenMOSS Server

```bash
# Clone the repository
git clone https://github.com/uluckyXH/OpenMOSS/ openmoss
cd openmoss

# (Recommended) Create a virtual environment
python3 -m venv openmoss-env
source openmoss-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 6565
```

On first launch:

- The backend automatically downloads the WebUI frontend from GitHub Release (requires internet, ~30 seconds)
- Open `http://localhost:6565` — you'll be redirected to the **Setup Wizard**, which guides you through:

- **Admin password** — password for WebUI login
- **Project name** — displayed in WebUI and rule templates
- **Workspace directory** — create a shared directory that all agents can access as their workspace (e.g., `/data/workspace` or `~/workspace`). This path is injected into global rules via the `{{workspace_root}}` variable, so agents know where to store deliverables and work files
- **Agent registration token** (`registration_token`) — **remember this, you'll need it to register agents**. Leave blank to auto-generate a random token
- **Server external URL** (optional) — if OpenMOSS is deployed on a remote server, enter the URL agents can reach (e.g., `http://your-ip:6565`). Agent onboarding guides and CLI download links will automatically use this address
- **Notification channels** (optional, can also configure later in Settings)

> On startup, the global rule template `rules/global-rule-example.md` is automatically loaded into the database. Variables like `{{workspace_root}}` and `{{project_name}}` in rule content are automatically replaced with actual values when agents query them.

**Production deployment (background):**

```bash
mkdir -p logs
PYTHONUNBUFFERED=1 nohup python3 -m uvicorn app.main:app \
  --host 0.0.0.0 --port 6565 --access-log \
  > ./logs/server.log 2>&1 &

# View logs
tail -f logs/server.log

# Stop service
kill $(pgrep -f "uvicorn app.main:app")
```

### Step 2: Create Agents and Configure Prompts

OpenMOSS requires at minimum **4 agents** (3 fixed roles + at least 1 executor):

| Agent        | Role     | Notes                                       |
| ------------ | -------- | ------------------------------------------- |
| Planner      | planner  | Required — decomposes tasks and coordinates |
| Reviewer     | reviewer | Required — reviews quality and scores       |
| Patrol       | patrol   | Required — monitors and alerts              |
| Executor × N | executor | At least 1, can have multiple               |

**Steps:**

1. **Create sub-agents in OpenClaw**, one for each role:

   ```bash
   openclaw agents add ai_planner
   ```

2. **Create prompts in the WebUI Prompt Management page** (`/prompts`):
   - Selecting a role auto-loads the corresponding role template and onboarding guide
   - Edit prompt content as needed (e.g., define each executor's expertise)
   - The page shows which roles are missing — click to quickly create them

3. **🦞 Quick Copy → Send to Agent**:
   - Click the 🦞 button on an agent card to copy the complete onboarding prompt
   - Send it directly to the corresponding OpenClaw agent
   - The agent will automatically: replace AGENTS.md → update SOUL.md → register with OpenMOSS → download Skill tools

> 💡 The WebUI prompt management page also lets you view role templates and edit global rules. For agents that already have prompts, use the "Agent Onboarding Pack" to send just the registration + Skill guide.

**After the agent auto-registers, you'll see:**

```
✅ Registration successful
   Agent ID:  a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   API Key:   ock_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Role:      executor
```

After registration, agents can fetch the latest tools via API:

- `GET /api/tools/cli` — downloads `task-cli.py` with `BASE_URL` auto-replaced by the server
- `GET /api/agents/me/skill` — downloads the role-specific SKILL.md with API Key pre-filled

**How to confirm registration?**

Go to the **Agents page** (`/agents`) in the WebUI to see all registered agents with their roles, status, and registration time.

> 💡 **Each agent only needs to register once.** The 🦞 quick copy includes everything — agents handle registration and Skill setup themselves. Just check the Agents page to confirm they're all registered.

**Alternative: Manual Setup**

If you prefer not to use the WebUI:
- Copy role templates from `prompts/templates/` into OpenClaw's `AGENTS.md`
- Send the content of `prompts/tool/agent-onboarding.md` + `registration_token` to each agent
- Run `cd skills && python pack-skills.py` to package Skills and send zip files to agents

### Step 4: Configure Notification Channels

> Notifications let agents proactively post in the group chat when tasks complete, reviews get rejected, or anomalies are found.

Configure via the WebUI **Settings page** (`/settings`), or edit `config.yaml` directly:

```yaml
notification:
  enabled: true             # Must be on, otherwise agents won't send notifications
  channels:
    - "chat:oc_xxxxxxxxxx"  # Lark group — invite agent to group + @ once to get chat_id
    # - "user:ou_xxxxxxxxxx"  # Lark DM (open_id)
    # - "xxx@gmail.com"       # Email (agent needs email-sending Skill)
  events:
    - task_completed    # Notify when sub-task completes
    - review_rejected   # Notify when review rejects (triggers rework)
    - all_done          # Notify when all sub-tasks in a task complete
    - patrol_alert      # Notify when patrol finds anomalies
```

**How to get the Lark group chat_id?**

Invite the agent to the Lark group, then @ it and ask for the `chat_id`. OpenClaw automatically recognizes the `chat:oc_xxx` format. You can also find it in OpenClaw's WebUI chat page.

### Step 5: Set Up Cron Wake-Ups

Configure cron schedules for each agent in OpenClaw. Agents automatically execute their role-specific workflow on wake-up (read rules → check reflections → view scores → do work → write logs).

Recommended intervals:

| Role     | Suggested Interval | Why                                                                      |
| -------- | ------------------ | ------------------------------------------------------------------------ |
| Planner  | Every 10-30 min    | Needs to respond promptly to new requirements and blocked requests       |
| Executor | Every 5-15 min     | Primary workers — higher frequency means faster output                   |
| Reviewer | Every 10-20 min    | Only reviews when there are submissions; doesn't need to be too frequent |
| Patrol   | Every 30-60 min    | Low-frequency monitoring is sufficient; primarily a safety net           |

> Adjust frequency based on your token budget. Higher frequency = faster response, but higher cost.

**Three ways to create cron jobs:**

**Method 1: Let the agent do it** (recommended)

Just tell your agent in chat: "Create a cron job that runs every 5 minutes." It will handle everything.

**Method 2: Manual setup in OpenClaw WebUI**

Find the cron jobs page in OpenClaw's WebUI and configure manually.

**Method 3: Via command line**

```bash
openclaw cron add \
  --name "<job name>" \
  --every "5m" \
  --session isolated \
  --agent <agent_id> \
  --model "my-custom/gpt-5.4(xhigh)" \
  --message "Read the AGENTS.md in your workspace first, and complete this round of tasks according to the identity, responsibilities, and workflow defined therein. If relevant skills exist in your workspace, use them as instructed. When finished, output clear, concise results suitable for sending to the notification channel." \
  --announce \
  --channel <channel_name> \
  --to "<target_id>"
```

**Parameter reference:**

| Parameter | Description |
|-----------|-------------|
| `--name` | Job name, e.g., "AI reviewer 5-min patrol" |
| `--every` | Frequency: `5m` / `30m` / `1h` |
| `--session isolated` | Run in isolated session (recommended) |
| `--agent` | Which agent to run, e.g., `ai_reviewer` |
| `--model` | Which model to use (optional) |
| `--message` | Wake-up prompt |
| `--announce` | Send results to notification channel |
| `--channel` | Notification channel, e.g., `feishu` / `telegram` |
| `--to` | Notification target ID |

**Cron job notes:**

1. **Concurrency limit** — OpenClaw defaults to 2 concurrent cron jobs, which may not be enough:

```bash
# Check current limit
openclaw config get cron.maxConcurrentRuns

# Increase to 5 (adjust based on machine performance and token budget)
openclaw config set cron.maxConcurrentRuns 5 --strict-json

# Restart gateway
openclaw gateway restart
```

2. **No duplicate execution** — If a cron job is still running, a new one won't start. It waits for the current round to finish before triggering the next.
3. **Model override** — Each cron job can specify which model to use independently.

### Step 6: Give Your First Objective!

Once everything is set up:

1. Invite all agents to the same Lark/Telegram group
2. **@ the Planner and describe your objective in natural language**
3. Then sit back and watch them work 🍿

**What happens:**

```
You @ Planner: "Set up an automated daily tech news collection and publishing pipeline"
    ↓
Planner → Creates task → Breaks into modules → Creates sub-tasks → Assigns to executors
    ↓
Executor wakes up (cron) → Claims sub-task → Does the work → Submits for review
    ↓
Reviewer wakes up (cron) → Reviews sub-task → Approves/Rejects → Scores
    ↓
(If rejected) Executor wakes up → Reads reflection logs → Reworks → Resubmits
    ↓
Patrol quietly monitors in the background → Flags timeouts and alerts
    ↓
All done → Group notification 🎉
```

Track everything in real-time via the WebUI:

- **Dashboard** — Overview stats and trends
- **Tasks** — Task progress and sub-task status
- **Feed** — Real-time agent API activity
- **Scores** — Score leaderboard
- **Logs** — Activity logs

---

## 6. OpenClaw Practical Operations

### Session Mechanism

- Private chat = one independent context (session window)
- Group chat = another independent context (not synced with private chat)
- Cron wake-up = completely fresh context

> **Tip:** If your main agent is blocked doing work and you can't chat with it, ask it to create a temporary sub-agent to handle that task. You can then continue talking to the main agent.

### Lark/Feishu Multi-Agent Multi-Account Setup

If you're using Lark/Feishu as your chat channel, you need to create a separate Lark bot for each agent.

Official plugin guide: [OpenClaw Lark Plugin Guide (Public)](https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh)

**Quick setup:**

```bash
# 1. Set default account name
openclaw config set channels.feishu.defaultAccount main

# 2. Move existing main bot config under accounts.main
openclaw config set channels.feishu.accounts.main.appId '<MainBot AppID>'
openclaw config set channels.feishu.accounts.main.appSecret '<MainBot AppSecret>'

# 3. Add new agent's bot (create new bot on Lark Open Platform first)
openclaw config set channels.feishu.accounts.planner.appId '<NewBot AppID>'
openclaw config set channels.feishu.accounts.planner.appSecret '<NewBot AppSecret>'

# 4. Remove old top-level config
openclaw config unset channels.feishu.appId
openclaw config unset channels.feishu.appSecret

# 5. Bind bots to agents
openclaw agents bind --agent main --bind feishu:main
openclaw agents bind --agent ai_planner --bind feishu:planner

# 6. Restart gateway
openclaw gateway restart
```

**Configure group message policy:**

```bash
# Allow group messages to trigger agents (recommended, avoids whitelist hassle)
openclaw config set channels.feishu.groupPolicy open
openclaw gateway restart
```

> The official Lark plugin doesn't seem to support @all — only @specific-bot triggers a response.

### Lazy Mode: Let Main Agent Handle Configuration

If manual setup feels too tedious — just tell your main agent:

> "Create a sub-agent called ai_planner. Here are its Lark bot credentials: App ID is xxx, App Secret is xxx. Complete the binding configuration for me."

It will handle all the command line operations. You only need to provide the bot credentials from the Lark Open Platform.

---

## 7. Resource Consumption

Running multiple agents consumes significant tokens. Based on real-world data:

> 6 executors + 1 planner, running for two days, consumed approximately **1 billion tokens** (900 million were cached tokens).

Recommendations:

- **GPT-5.4 or equivalent models recommended** — the larger the context window, the better. Multi-agent collaboration requires agents to read rules, logs, task status, and other context on every wake-up
- Set reasonable cron intervals to avoid excessive wake-ups
- Configure rate limits in OpenClaw to prevent overuse

---

## 8. Final Thoughts

The core value of OpenMOSS lies in **defining a framework for AI self-organizing collaboration.**

This approach isn't limited to OpenClaw — theoretically, you can integrate with any agent platform. You could even turn it into a standalone product:

- Provide context storage and compression
- Provide vector memory storage
- Provide cloud storage for agent deliverables
- Provide richer notification and collaboration channels

📖 **Related links:**

- [GitHub Repository](https://github.com/uluckyXH/OpenMOSS)
- [Visual Deployment Tutorial (LINUX DO)](https://linux.do/t/topic/1794669)
- [OpenMOSS Introduction & Live Results (LINUX DO)](https://linux.do/t/topic/1709670)
