# ai-agent-prd

"Write comprehensive PRDs for AI Agent products—covering agent identity, capability architecture (skills, tools, memory, RAG, workflows), behavior specifications, safety guardrails, and evaluation frameworks. Use when: designing conversational agents, autonomous agents, copilots, multi-agent systems, or any LLM-powered agentic application. Triggers: 'AI agent PRD', 'agent product requirements', 'design AI agent', 'agent capability spec', 'LLM agent requirements', '智能体PRD', '智能体需求文档', '对话机器人PRD', '多智能体系统需求'. Anti-triggers: '传统PRD（非智能体）', '只润色提示词/只写Prompt', '只写用户故事/验收标准但不涉及工具调用、记忆或RAG'."

## 包含内容

- `SKILL.md`
- `scripts/`（可选）
- `references/`（可选）
- `assets/`（可选）

## 用法

### 生成 Agent PRD 骨架（Markdown）

在技能目录中执行：

```bash
bash scripts/generate_agent_prd_skeleton.sh ./docs/agent-prd "Customer Support Agent"
```

说明：

- 生成器会往输出目录写入一组 `.md` 文件；建议使用新的/空目录，避免覆盖已有内容。
- 使用 `references/` 中的模板与清单（例如 `references/agent-prd-template.md`）来补全 PRD。

## 安装

> 安装 skill 的本质是：让你的编码工具 / Agent 运行器能发现这个目录里的 `SKILL.md`（通常是放进某个 `skills/` 目录，或使用工具内置的“从 Git 安装”能力）。

### 方式 A：复制安装

在仓库根目录执行：

把 `SKILLS_DIR` 改成你的工具会扫描的 skills 目录（示例：`~/.codex/skills`、`~/.claude/skills`、`~/.config/opencode/skills` 等）：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/ai-agent-prd"
cp -R agent/skills/ai-agent-prd "$SKILLS_DIR/ai-agent-prd"
```

### 方式 B：软链接安装

在仓库根目录执行：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/ai-agent-prd"
ln -s "$(pwd)/agent/skills/ai-agent-prd" "$SKILLS_DIR/ai-agent-prd"
```

### 方式 C：用 openskills 从 GitHub/Git 安装

先准备 openskills：

- 需要 Node.js（建议 18+）。
- 不想安装：直接用 `npx openskills ...`（会自动下载并运行）。
- 想全局安装：`npm i -g openskills`（或 `pnpm add -g openskills`）。

从**可 clone 的仓库 URL** 安装（不要用 GitHub 的 `.../tree/...` 子目录链接）：

```bash
npx openskills install https://github.com/okwinds/miscellany
```

安装时选择 `ai-agent-prd`（仓库内路径：`agent/skills/ai-agent-prd`）。

验证/读取：

```bash
npx openskills list
npx openskills read ai-agent-prd
```

### 方式 D：直接给工具一个 GitHub 链接

不少编码工具支持“从 GitHub/Git URL 安装/加载 skill”。如果你的工具支持，指向本仓库并选择/定位到 `agent/skills/ai-agent-prd`。

### 安装完成后

不少工具需要重启/新开会话，才会重新扫描 skills。
