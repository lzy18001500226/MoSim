# PRD: Personal Squad Consult Mode

**Author:** James Sturtevant
**Date:** 2026-02-27
**Status:** Implemented
**Wave:** M6 (Personal Squad Enhancement)

---

## Problem Statement

You have a personal squad at your global squad path (resolved via `resolveGlobalSquadPath()` — e.g. `~/.config/squad/.squad` on Linux, `~/Library/Application Support/squad/.squad` on macOS, `%APPDATA%/squad/.squad` on Windows) with agents, skills, and decisions refined over time. You want to use this team on projects you don't own (OSS contributions, client work, temporary collaborations) without:

1. **Polluting the project** — no `.gitignore` changes, no committed `.squad/` folder
2. **Polluting your squad** — no project-specific knowledge bleeding into your global squad

Currently, `squad init` creates a project-owned squad. There's no way to "bring your team" to a project invisibly, work with them, and bring back only the generic learnings.

---

## Solution: Consult Mode

Your team **consults** on a project. They bring their expertise, do the work, learn things. When done, they extract what's reusable and return home. The project never knows Squad was there.

### Key Behaviors

| Aspect | Normal Mode | Consult Mode |
|--------|-------------|--------------|
| Squad location | `.squad/` in project | **Copy** of personal squad into project `.squad/` |
| Git visibility | Committed or `.gitignore` | Invisible via `.git/info/exclude` |
| Writes go to | Project `.squad/` | Project `.squad/` (isolated copy, won't affect personal squad) |
| Agent file | `.github/agents/squad.agent.md` (committed) | `.github/agents/squad.agent.md` (excluded, points to local `.squad/`) |
| After session | Stays in project | Extract generic → personal squad, discard rest |

---

## Commands

### Entry: `squad consult`

```bash
cd ~/projects/their-oss-project
squad consult              # Enter consult mode
squad consult --status     # Check if in consult mode, show pending learnings
squad consult --check      # Dry-run: show what would happen without creating files
```

**Creates:**
```
.squad/                     # Full copy of personal squad
├── config.json             # { "consult": true, "sourceSquad": "<personal squad path>", ... }
├── agents/                 # Copied from personal squad
├── skills/                 # Copied from personal squad
├── decisions.md            # Copied from personal squad
├── scribe-charter.md       # Patched with consult mode extraction instructions
├── sessions/               # Local session history
└── extract/                # Staging area for generic learnings (Scribe writes here)

.github/agents/
└── squad.agent.md          # Points to local .squad/ (also excluded from git)
```

**Also:**
- Appends `.squad/` and `.github/agents/squad.agent.md` to `.git/info/exclude` (git-internal, never visible)
- If project already has committed `.squad/`: **error out**

**Why copy instead of reference?**
- Changes during consult session don't pollute your personal squad
- Session-specific decisions/skills stay isolated until explicitly extracted
- Works offline (no dependency on external path)

### Exit: `squad extract`

```bash
squad extract                    # Review and extract generic learnings
squad extract --dry-run          # Preview what would be extracted (no changes)
squad extract --clean            # Also delete project .squad/ after (prompts for confirmation)
squad extract --clean --yes      # Delete without confirmation
squad extract --accept-risks     # Allow extraction despite license or other risks
```

**Flow:**
1. Read project LICENSE file
2. Warn if copyleft (GPL, AGPL) — license contamination risk
3. Load staged learnings from `.squad/extract/`
4. User selects which learnings to extract
5. Merge selected items to personal squad
6. Log to `<sourceSquad>/consultations/{project}.md`
7. Remove extracted files from `.squad/extract/`

---

## Classification: Scribe-Based

The extraction classification is done by **Scribe** during the session, not by SDK heuristics.

When consult mode is set up, the Scribe charter is patched with extraction instructions:

```markdown
## Consult Mode Extraction

**This squad is in consult mode.** When merging decisions from the inbox, also classify each decision:

### Classification

For each decision in `.squad/decisions/inbox/`:

1. **Generic** (applies to any project) → Copy to `.squad/extract/` with the same filename
   - Signals: "always use", "never use", "prefer X over Y", "best practice", coding standards, patterns that work anywhere
   - These will be extracted to the personal squad via `squad extract`

2. **Project-specific** (only applies here) → Keep in local `decisions.md` only
   - Signals: Contains file paths from this project, references "this project/codebase/repo", mentions project-specific config/APIs/schemas

Generic decisions go to BOTH `.squad/decisions.md` (for this session) AND `.squad/extract/` (for later extraction).
```

**User always has final say.** Scribe proposes by writing to `extract/`, user approves/rejects via `squad extract`. No extraction happens without explicit confirmation.

---

## Extraction Review

Via `squad extract`:

```
📤 Learnings staged for extraction:

⚠️  License: MIT (safe to extract)

Found 3 learning(s) in .squad/extract/:
  [1] use-async-await.md
  [2] validate-inputs.md
  [3] prefer-composition.md

Select learnings to extract (space to toggle, enter to confirm):
❯ ◉ use-async-await.md
  ◉ validate-inputs.md
  ◉ prefer-composition.md

Extract 3 learning(s)? [Y/n]
```

### License Handling

**Permissive licenses (MIT, Apache, BSD, ISC):** Proceed normally with extraction review.

**Copyleft licenses (GPL, AGPL, LGPL):** **Blocked by default.** Extraction refuses unless user explicitly opts in:

```
🚫 License: GPL-3.0 (copyleft)
   Extraction blocked. Patterns from copyleft projects may carry
   license obligations that affect your future work.

   See: https://squad.dev/docs/license-risk

   To proceed anyway: squad extract --accept-risks
```

---

## Technical Design

### Config Schema

Consult mode config in `.squad/config.json`:

```typescript
interface ConsultDirConfig {
  consult: boolean;        // true = consult mode
  sourceSquad: string;     // Path to original personal squad (for extraction)
  projectName: string;     // Name of the project being consulted
  createdAt: string;       // ISO timestamp
}
```

### SDK Types

```typescript
// Result of setupConsultMode()
interface SetupConsultModeResult {
  squadDir: string;           // Path to project .squad/
  personalSquadRoot: string;  // Path to personal squad root
  gitExclude: string;         // Path to git exclude file
  projectName: string;        // Project name (basename)
  dryRun: boolean;            // Whether this was a dry run
  agentFile: string;          // Path to .github/agents/squad.agent.md
  createdFiles: string[];     // List of created file paths (relative to squadDir)
}

// A learning staged by Scribe for extraction
interface StagedLearning {
  filename: string;   // e.g. "use-async-await.md"
  filepath: string;   // Full path to file in extract/
  content: string;    // File content
}

// Result of extraction
interface ExtractionResult {
  extracted: StagedLearning[];  // Learnings extracted to personal squad
  skipped: StagedLearning[];    // Learnings rejected by user
  license: LicenseInfo;
  projectName: string;
  timestamp: string;
  acceptedRisks: boolean;
}
```

### Errors

```typescript
// Thrown when personal squad doesn't exist
class PersonalSquadNotFoundError extends Error {
  constructor() {
    super('No personal squad found.');
    this.name = 'PersonalSquadNotFoundError';
  }
}
```

### Invisibility Mechanism

`.git/info/exclude` is:
- Git-internal exclude file (same syntax as `.gitignore`)
- Lives in `.git/`, so never committed
- Project owner never sees it
- `git status` shows nothing

> **Important:** Do not hard-code `resolve(cwd, '.git/info/exclude')`. In git worktrees
> and submodules, `.git` is a *file* pointing at the real git dir. Use `git rev-parse`
> to resolve the correct path:

```bash
# Resolve the correct exclude path (works with worktrees/submodules)
EXCLUDE_PATH=$(git rev-parse --git-path info/exclude)
echo ".squad/" >> "$EXCLUDE_PATH"
```

---

## Consultation Log

Track all consultations in `<sourceSquad>/consultations/`:

**`<sourceSquad>/consultations/kubernetes-dashboard.md`:**
```markdown
# kubernetes-dashboard

**First consulted:** 2026-02-27
**Last session:** 2026-03-15
**License:** Apache-2.0

## Sessions

### 2026-02-27
- use-async-await.md: "### Always use async/await..."
- validate-inputs.md: "### Validate inputs at API..."

### 2026-03-15
- prefer-composition.md: "### Prefer composition over..."
```

---

## Success Criteria

1. **Invisible by default:** `git status` shows nothing in consult mode
2. **No pollution upstream:** Project `.squad/` never modifies global squad without explicit approval
3. **No pollution downstream:** Project-specific learnings stay in project or are discarded
4. **Audit trail:** `<sourceSquad>/consultations/` tracks what was extracted from where
5. **License safety:** User warned about copyleft extraction risks
6. **Matches InitResult:** `SetupConsultModeResult.createdFiles` array matches `InitResult.createdFiles` pattern

---

## Non-Goals (v1)

- Cross-machine sync of global squad (users can use git or `squad export/import`)
- Consulting on squadified projects (error out for now)
- Automatic extraction (always requires user approval)
- SDK-side heuristic classification (Scribe handles this via LLM during session)

---

## References

- [Personal Squad Guide](../docs/guide/personal-squad.md)
- [SDK Sharing Module](../packages/squad-sdk/src/sharing/)
- [Export Command](../packages/squad-cli/src/cli/commands/export.ts)
