# ai-agent-prd

"Write comprehensive PRDs for AI Agent products—covering agent identity, capability architecture (skills, tools, memory, RAG, workflows), behavior specifications, safety guardrails, and evaluation frameworks. Use when: designing conversational agents, autonomous agents, copilots, multi-agent systems, or any LLM-powered agentic application. Triggers: 'AI agent PRD', 'agent product requirements', 'design AI agent', 'agent capability spec', 'LLM agent requirements', '智能体PRD', '智能体需求文档', '对话机器人PRD', '多智能体系统需求'. Anti-triggers: '传统PRD（非智能体）', '只润色提示词/只写Prompt', '只写用户故事/验收标准但不涉及工具调用、记忆或RAG'."

## What's included

- `SKILL.md`
- `scripts/` (optional)
- `references/` (optional)
- `assets/` (optional)

## Usage

### Generate an Agent PRD skeleton (Markdown)

From the skill directory:

```bash
bash scripts/generate_agent_prd_skeleton.sh ./docs/agent-prd "Customer Support Agent"
```

Notes:

- The generator writes a set of `.md` files into the output directory; use a new/empty folder to avoid overwrites.
- Use the templates and checklists in `references/` (e.g. `references/agent-prd-template.md`) to fill in the PRD.

## Installation

> Installing a skill means your coding tool / agent runner can discover the `SKILL.md` inside it (typically via a `skills/` directory, or via a built-in “install from Git” feature).

### Option A: copy

From this repo root:

Set `SKILLS_DIR` to whatever skills folder your tool scans (examples: `~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`, etc):

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/ai-agent-prd"
cp -R agent/skills/ai-agent-prd "$SKILLS_DIR/ai-agent-prd"
```

### Option B: symlink

From this repo root:

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/ai-agent-prd"
ln -s "$(pwd)/agent/skills/ai-agent-prd" "$SKILLS_DIR/ai-agent-prd"
```

### Option C: install from GitHub/Git via openskills

Prereqs for openskills:

- Requires Node.js (18+ recommended).
- No install needed if you use `npx openskills ...` (it will download and run).
- Optional global install: `npm i -g openskills` (or `pnpm add -g openskills`).

Install from a cloneable repo URL (do **not** use a GitHub `.../tree/...` subdirectory link):

```bash
npx openskills install https://github.com/okwinds/miscellany
```

When prompted, select `ai-agent-prd` (repo path: `agent/skills/ai-agent-prd`).

Verify / read back:

```bash
npx openskills list
npx openskills read ai-agent-prd
```

### Option D: give your tool the GitHub link

Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at this repo and select/target `agent/skills/ai-agent-prd`.

### After install

Many tools require a restart / new session to re-scan skills.
