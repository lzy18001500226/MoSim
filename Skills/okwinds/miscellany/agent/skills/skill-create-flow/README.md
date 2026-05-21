# skill-create-flow

Create new high-quality agent skills with a standalone, repeatable workflow (no dependency on other skills). Use when you want to go from a vague skill idea → narrow scope → extract expert frameworks → write SKILL.md + examples/evals/index/changelog artifacts → self-validate with test prompts.

## When to use this skill

This skill is ideal for creating **procedural agent skills** where the value comes from following a structured methodology rather than raw knowledge retrieval. Best-suited skill types include:

- **Methodology-based skills**: Process workflows like debugging, code reviews, writing specs, systematic problem-solving
- **Decision-heavy skills**: Scenarios requiring judgment and expertise (e.g., architecture decisions, UX design, business strategy)
- **Multi-step workflows**: Skills requiring a defined sequence of operations with clear deliverables
- **Quality-focused skills**: Where "excellent vs mediocre" output is distinguishable and process matters

Less ideal for:
- Pure reference/lookup skills (use knowledge retrieval instead)
- Simple one-shot commands (use direct tool invocation instead)
- Skills requiring external dependencies (this flow produces standalone skills)

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
rm -rf "$SKILLS_DIR/skill-create-flow"
cp -R agent/skills/skill-create-flow "$SKILLS_DIR/skill-create-flow"
```

### Option B: symlink

From this repo root:

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/skill-create-flow"
ln -s "$(pwd)/agent/skills/skill-create-flow" "$SKILLS_DIR/skill-create-flow"
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

When prompted, select `skill-create-flow` (repo path: `agent/skills/skill-create-flow`).

Verify / read back:

```bash
npx openskills list
npx openskills read skill-create-flow
```

### Option D: give your tool the GitHub link

Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at this repo and select/target `agent/skills/skill-create-flow`.

### After install

Many tools require a restart / new session to re-scan skills.
