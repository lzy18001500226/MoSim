# agently-task-dev

Use only when the user explicitly wants to build with the Agently framework (mentions Agently/agently/OpenAICompatible/TriggerFlow/ToolExtension/ChromaCollection, or says “用 Agently 做/用 agently 做”). Deliver runnable code plus regression tests validating schema/ensure_keys and streaming (delta/instant/streaming_parse), with optional tools (Search/Browse/MCP), TriggerFlow orchestration, KB (ChromaDB), and serviceization (SSE/WS/HTTP). Do not use for generic streaming/testing questions that are not about Agently, or for prompt-only writing without tests/structure.

## What's included

- `SKILL.md`
- `scripts/` (optional)
- `references/` (optional)
- `assets/` (optional)

## Installation

> Installing a skill means your coding tool / agent runner can discover the `SKILL.md` inside it (typically via a `skills/` directory, or via a built-in “install from Git” feature).

### Option A: copy

From this repo root:

Set `SKILLS_DIR` to whatever skills folder your tool scans (examples: `~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`, etc):

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/agently-task-dev"
cp -R agent/skills/agently-task-dev "$SKILLS_DIR/agently-task-dev"
```

### Option B: symlink

From this repo root:

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/agently-task-dev"
ln -s "$(pwd)/agent/skills/agently-task-dev" "$SKILLS_DIR/agently-task-dev"
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

When prompted, select `agently-task-dev` (repo path: `agent/skills/agently-task-dev`).

Verify / read back:

```bash
npx openskills list
npx openskills read agently-task-dev
```

### Option D: give your tool the GitHub link

Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at this repo and select/target `agent/skills/agently-task-dev`.

### After install

Many tools require a restart / new session to re-scan skills.
