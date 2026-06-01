# Proposal: Reliable Init Flow

**Author:** Keaton (Lead)
**Date:** 2026-02-28
**Status:** Draft — for Brady's review
**Context:** PRs #637–#640 iteratively patched init. Brady flagged fragility.

---

## Problem

The init/onboarding flow has been built incrementally across four PRs. It works for the happy path but has multiple entry points, a race condition, an unabortable session, and two completely divergent casting flows (CLI vs. agent prompt). A new user shouldn't have to discover the right incantation.

---

## Current Entry Paths (7 total)

### Path 1: `squad` — no .squad/ exists
**File:** `cli-entry.ts:654–677`
Shows welcome text: "Get started → squad init". Clean dead end.
**Verdict: ✅ Solid.**

### Path 2: `squad init` — no prompt
**File:** `cli-entry.ts:690–722` → `init.ts:runInit()`
Scaffolds `.squad/` with an empty team.md roster. No `.init-prompt`. Final message tells user to run `squad init "prompt"` or start a Copilot session.
**Verdict: ⚠️ Creates a half-state.** User has `.squad/` but no team. They have to know to do something else. Running `squad` next puts them in a shell with an empty roster and no auto-cast trigger.

### Path 3: `squad init "prompt"` — with prompt
**File:** `cli-entry.ts:706–721` → `init.ts:runInit({ prompt })`
Same scaffold as Path 2, plus writes `.squad/.init-prompt`. Message: "Run squad to cast your team."
**Verdict: ✅ Good — sets up deferred casting.**

### Path 4: `squad` — .squad/ exists, empty roster, .init-prompt exists
**File:** `shell/index.ts:896–912`
Shell starts. After Ink renders, `setTimeout(100)` checks for `.init-prompt` and empty roster. If both conditions met AND `shellApi` is set, triggers `handleInitCast`.
**Verdict: ⚠️ Race condition.** `shellApi` is set in `onReady` callback. At 100ms, it may not be set yet. If the check fails, auto-cast silently does nothing. The user sees an empty shell with no team and no explanation of what went wrong.

### Path 5: In REPL, no team, user types a message
**File:** `shell/index.ts:handleDispatch():752–769`
Checks team.md → if exists but empty roster → `handleInitCast(parsed)`. Uses the user's message as the cast prompt.
**Verdict: ⚠️ Works but fragile.** If the user types "hello" or "what can you do?" instead of describing their project, the LLM gets a garbage prompt and casts a random team.

### Path 6: `/init` command in REPL
**File:** `commands.ts:handleInit():212–225`
Prints instructions: "Just type what you want to build." Does NOT trigger casting.
**Verdict: ⚠️ Misleading.** A command called `/init` that doesn't initialize anything. Users expect it to do something.

### Path 7: squad.agent.md Init Mode (Copilot extension)
**File:** `templates/squad.agent.md:23–91`
Completely separate 2-phase casting flow: propose team → wait for confirmation → create files. Reads git user.name, runs full casting algorithm with universe resonance scoring.
**Verdict: ✅ Rich but divergent.** This is the "good" init flow — it asks the user, confirms before creating, runs the full casting algorithm. But it shares zero code with the CLI flow.

---

## Identified Bugs and Failure Modes

### 🔴 Bug: Ctrl+C during casting doesn't abort the init session
`handleInitCast()` creates a local `initSession` variable (line 631). `handleCancel()` (line 578) only aborts `coordinatorSession` and entries in `agentSessions`. The init session isn't in either map. Ctrl+C during casting clears the processing UI state, but the abandoned SDK session continues running until timeout.

### 🔴 Bug: Auto-cast race condition
`setTimeout(100)` at line 905 fires before `shellApi` is guaranteed to be set. The guard `if (storedPrompt && shellApi)` silently swallows the failure. No retry. No user feedback.

### 🟡 Issue: `/init` is a no-op
The `/init` REPL command just prints "type what you want to build." If the user is in the REPL with an empty roster, typing `/init` should either (a) trigger casting from the next message, or (b) actually run casting with an interactive prompt.

### 🟡 Issue: .init-prompt orphan
Running `squad init "new prompt"` after a team already exists writes `.init-prompt`, but the auto-cast check only fires when the roster is empty. The file sits there forever, unused.

### 🟡 Issue: No cast confirmation in CLI flow
The CLI path (`handleInitCast`) sends a prompt to the LLM, gets back an `INIT_TEAM:` block, parses it, and creates all team files — no confirmation step. The agent prompt path (squad.agent.md) explicitly stops and waits for user approval. CLI users get no say in who's on their team.

### 🟡 Issue: Two divergent casting flows
`buildInitModePrompt()` (coordinator.ts) is a bare-minimum prompt: "propose 4-5 agents, use INIT_TEAM: format." The squad.agent.md Init Mode is rich: resonance scoring, universe selection algorithm, git user detection, 2-phase confirmation. Same product, two completely different experiences depending on how you got here.

### 🟢 Non-issue: `squad init` then `squad init "prompt"` (idempotency)
The scaffold is idempotent — all file writes check `if (!existsSync)`. Running init twice doesn't break anything. The `.init-prompt` write is unconditional (correct — it should overwrite).

---

## Assessment: Is It Working End-to-End?

**The golden path works:** `squad init "Build a React app"` → `squad` → auto-cast fires → team created → message re-dispatched.

**The fragile paths:**
1. `squad init` (no prompt) → `squad` → empty shell, no auto-cast, user confused
2. Auto-cast race condition → silent failure → empty shell
3. User types non-descriptive first message → garbage cast
4. Ctrl+C during casting → orphaned session

**Bottom line:** It works if the user follows the exact right sequence. It fails silently if they don't.

---

## Proposed Golden Path

**One reliable flow. Every other entry point funnels into it.**

```
User runs squad          ──→ No .squad/?  ──→ "Run squad init to get started"
                               ↓ yes
                          Has roster?    ──→ yes → normal REPL
                               ↓ no
                          Has .init-prompt? ──→ yes → auto-cast (with confirmation)
                               ↓ no
                          Show: "Describe your project to cast a team"
                               ↓ user types
                          handleInitCast → show proposal → confirm → create
```

### Minimal Changes Required (in priority order)

#### P0: Fix the bugs
1. **Fix the race condition.** Replace `setTimeout(100)` with a proper callback. After `shellApi` is set in `onReady`, check for auto-cast conditions there. No timing guesses.

2. **Wire Ctrl+C to abort init session.** Store the `initSession` reference somewhere `handleCancel` can reach it (e.g., a module-level `let activeInitSession`).

3. **Clean up .init-prompt on shell start if roster exists.** One line: if roster has entries and `.init-prompt` exists, delete it.

#### P1: Make the empty-roster state reliable
4. **When user enters REPL with empty roster and no .init-prompt:** Show a clear system message: "No team cast yet. Describe your project and I'll assemble a team." Don't silently wait for them to figure it out. This is already partly there in the banner (`rosterAgents.length === 0 ? "Send a message to get started"`) but it should be more explicit about what happens next.

5. **Make `/init` actually useful.** Two options:
   - **(a) Minimal:** `/init` triggers the same flow as typing a message with an empty roster — prompt the user to describe their project, next message becomes the cast prompt.
   - **(b) Better:** `/init "prompt"` triggers casting directly from the REPL, same as `squad init "prompt"` from the CLI but without leaving the shell.

#### P2: Add confirmation before casting
6. **Show the proposed team before creating files.** The `formatCastSummary` function already exists. After parsing the proposal, display it and ask "Look good? (Y/n)" before calling `createTeam`. This matches the squad.agent.md flow and prevents garbage casts from bad prompts.

   *Trade-off:* This adds friction to the auto-cast-on-shell-start path. Option: skip confirmation only when the prompt came from `.init-prompt` (the user explicitly provided it via `squad init "prompt"`), confirm when the prompt is a freeform REPL message.

#### P3: Align the two casting flows (future)
7. **Long-term:** The CLI casting engine (`buildInitModePrompt` + `parseCastResponse`) should converge with the squad.agent.md Init Mode logic. The agent prompt has better casting (resonance scoring, proper universe selection). The CLI prompt is a thin stub. Two options:
   - Move the casting intelligence into the CLI code (preferred — deterministic, testable)
   - Accept divergence and document which flow produces better results

   *This is a larger effort and shouldn't block the P0/P1 fixes.*

---

## What NOT to Do

- **Don't merge the CLI and agent prompt flows right now.** They serve different contexts (terminal REPL vs. Copilot extension). Alignment is a P3 goal.
- **Don't add more entry points.** The problem is already too many paths. Consolidate, don't expand.
- **Don't require init before shell.** The REPL should handle "no team" gracefully, not refuse to start. The current `handleInitCast` approach (cast from REPL) is the right pattern — it just needs the bugs fixed and the UX polished.

---

## Estimated Effort

| Priority | Items | Effort |
|----------|-------|--------|
| P0 | Race condition fix, Ctrl+C abort, .init-prompt cleanup | ~2 hours |
| P1 | Empty-roster messaging, `/init` improvement | ~2 hours |
| P2 | Cast confirmation step | ~3 hours |
| P3 | Casting flow alignment | 1–2 days (separate PR) |

P0+P1 can ship in a single PR. P2 can follow immediately. P3 is a separate effort.

---

## Files Involved

| File | What changes |
|------|-------------|
| `packages/squad-cli/src/cli/shell/index.ts` | Race condition fix (move auto-cast to onReady), Ctrl+C abort wiring, .init-prompt cleanup |
| `packages/squad-cli/src/cli/shell/commands.ts` | `/init` command behavior |
| `packages/squad-cli/src/cli/shell/components/App.tsx` | Empty-roster banner messaging |
| `packages/squad-cli/src/cli/shell/coordinator.ts` | (P2) Cast confirmation flow |
| `packages/squad-cli/src/cli/core/init.ts` | No changes needed |
| `packages/squad-cli/src/cli/core/cast.ts` | No changes needed |

---

*Brady — this is my read. The bones are good. The patching across #637–#640 built the right primitives (Init Mode prompt, cast parser, auto-cast trigger, REPL dispatch gating). But the wiring between them has gaps. P0 fixes are surgical. P1 makes it feel solid. P2 makes it feel right. Your call on scope.*

— Keaton
