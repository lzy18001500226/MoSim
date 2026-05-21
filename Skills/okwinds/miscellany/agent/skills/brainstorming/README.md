# brainstorming

"Turn vague ideas into a validated design/spec through structured brainstorming. Use before any creative work (new features, UI/components, behavior changes, refactors) and whenever a user asks to brainstorm, define requirements, propose approaches, or write a design doc."

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
rm -rf "$SKILLS_DIR/brainstorming"
cp -R agent/skills/brainstorming "$SKILLS_DIR/brainstorming"
```

### Option B: symlink

From this repo root:

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/brainstorming"
ln -s "$(pwd)/agent/skills/brainstorming" "$SKILLS_DIR/brainstorming"
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

When prompted, select `brainstorming` (repo path: `agent/skills/brainstorming`).

Verify / read back:

```bash
npx openskills list
npx openskills read brainstorming
```

### Option D: give your tool the GitHub link

Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at this repo and select/target `agent/skills/brainstorming`.

### After install

Many tools require a restart / new session to re-scan skills.
