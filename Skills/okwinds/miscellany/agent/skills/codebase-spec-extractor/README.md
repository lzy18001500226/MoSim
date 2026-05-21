# Codebase Spec Extractor (`codebase-spec-extractor`)

Extract complete, replicable engineering specifications from existing codebases. The goal is implementation-grade documentation that can be used to rebuild behavior without access to the original code (even with a different tech stack).

## What's included

- `SKILL.md`
- `scripts/`
- `references/`

## Installation

> Installing a skill means your coding tool / agent runner can discover the `SKILL.md` inside it (typically via a `skills/` directory, or via a built-in “install from Git” feature).

### Option A: copy

From this repo root:

Set `SKILLS_DIR` to whatever skills folder your tool scans (examples: `~/.codex/skills`, `~/.claude/skills`, `~/.config/opencode/skills`, etc):

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/codebase-spec-extractor"
cp -R agent/skills/codebase-spec-extractor "$SKILLS_DIR/codebase-spec-extractor"
```

### Option B: symlink

From this repo root:

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/codebase-spec-extractor"
ln -s "$(pwd)/agent/skills/codebase-spec-extractor" "$SKILLS_DIR/codebase-spec-extractor"
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

When prompted, select `codebase-spec-extractor` (repo path: `agent/skills/codebase-spec-extractor`).

Verify / read back:

```bash
npx openskills list
npx openskills read codebase-spec-extractor
```

### Option D: give your tool the GitHub link

Many coding tools can install/load skills directly from a GitHub/Git URL. If yours supports it, point it at this repo and select/target `agent/skills/codebase-spec-extractor`.

### After install

Many tools require a restart / new session to re-scan skills.

## Usage

Note: the scripts in this skill are **helpers to find gaps and broken links**. They are heuristic checks and do not “prove” completeness or behavioral equivalence.

From the skill directory:

```bash
# 1) Quick project scan (type, stack, structure)
bash scripts/discover_project.sh <project_root> > discovery.md

# 2) Build an element inventory (files/modules worth documenting)
bash scripts/inventory_elements.sh <project_root> > inventory.md

# 3) Create a spec/ skeleton directory
bash scripts/generate_skeleton.sh spec

# 4) Code → Spec: heuristic gap finding
bash scripts/verify_coverage.sh <project_root> spec > coverage.md

# 5) Spec → Code: validate Source anchors (recommended)
# Add lines like: `Source: path/to/file.ext` to your spec markdown first.
bash scripts/verify_implementation.sh spec <project_root> > spec_to_code.md
```
