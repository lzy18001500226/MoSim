# Copy Review Spec — Issue #668

**Requested by:** Brady
**Prepared by:** Marquez (CLI UX Designer)
**Scope:** All user-facing text in the Squad CLI shell
**Goal:** Tighten verbose copy, improve clarity, reduce jargon

---

## Summary of Issues

Brady flagged 5 key areas where copy needs work:

1. **Jargon:** Terms like "routing" exposed to users
2. **Length:** Version strings and status messages too long
3. **Redundancy:** Roster displayed multiple times; duplicate headers
4. **Truncation:** Status messages exceed 80 chars; hard to read
5. **Dead zones:** Users see nothing during processing; need more feedback

This spec provides concrete rewrites for every user-facing string in:
- `packages/squad-cli/src/cli/shell/index.ts`
- `packages/squad-cli/src/cli/shell/components/App.tsx`
- `packages/squad-cli/src/cli/shell/components/MessageStream.tsx`
- `packages/squad-cli/src/cli/shell/components/InputPrompt.tsx`
- `packages/squad-cli/src/cli/shell/components/AgentPanel.tsx`
- `packages/squad-cli/src/cli/shell/components/ThinkingIndicator.tsx`
- `packages/squad-cli/src/cli/shell/coordinator.ts`
- `packages/squad-cli/src/cli/shell/commands.ts`

---

## Copy Review Table

| File | Location | Current | Proposed | Rationale |
|------|----------|---------|----------|-----------|
| index.ts | line 142 | `◆ Loading Squad shell...` | `◆ Loading Squad...` | Shorter, still clear. "Shell" is technical jargon. |
| index.ts | line 135–137 | `✗ Squad shell requires an interactive terminal (TTY).\n  Piped or redirected stdin is not supported.\n  Tip: Run 'squad --preview' for non-interactive usage.` | `✗ Squad needs an interactive terminal.\n  Redirect or pipe not supported.\n  Try: squad --preview for non-interactive mode` | More human. "TTY" is jargon. Shorter, actionable. |
| App.tsx | line 51 | `const EXIT_WORDS = new Set(['exit', 'quit', 'q']);` | *(no change)* | Already concise and correct. |
| App.tsx | line 166 | `Press Ctrl+C again to exit.` | *(no change)* | Clear and direct. |
| App.tsx | line 234 | `SDK not connected. Try: (1) squad doctor to check setup, (2) check your internet connection, (3) restart the shell to reconnect.` | `SDK disconnected. Try: squad doctor, check internet, or restart.` | 3× shorter. Removes numbered list. Same remediation. |
| App.tsx | line 230 | `'  Just type what you need — Squad routes your message to the right agent.'` (in /help) | *(no change)* | This is good. Present tense, human-readable. |
| InputPrompt.tsx | line 20 | `return narrow ? ' Tab · ↑↓ history' : ' Tab completes · ↑↓ history';` | `return narrow ? ' Tab · ↑↓' : ' Tab for help · ↑↓ for history';` | More specific: "Tab for help" vs "Tab completes" (help is broader). "↑↓ for history" removes ambiguity. |
| InputPrompt.tsx | line 22 | `return narrow ? ' /status · /clear · /export' : ' /status · /clear · /export';` | `return narrow ? ' /status · /help' : ' /status · /help · /clear';` | More discoverable: first-run users need /help. Narrow mode gets only essentials. |
| AgentPanel.tsx | line 68 | `No agents active. Send a message to start. /help for commands.` | `No agents yet. Send a message to wake them.` | Warmer, shorter. "Wake them" is more human than "start." Removes redundant /help hint (already in header). |
| AgentPanel.tsx | line 189 | `▸ {name} is {activity}` (agent activity feed) | *(no change)* | Good as-is. Specific, present tense. |
| MessageStream.tsx | line 103 | `${atMatch[1]} is thinking...` | *(no change)* | Clear and direct. |
| ThinkingIndicator.tsx | line 26–41 | `THINKING_PHRASES` array includes generic labels like "Routing to agent", "Analyzing your request", "Reviewing project context" | Review phrases for brevity & clarity. Keep "Routing to agent" but tighten others: "Analyzing request" (not "your request"), "Checking context" (not "Reviewing project context"), "Weighing options" (not "Evaluating options") | Phrases cycle every 3s — each must be ultra-scannable. Shorter = visible at a glance. Remove possessives ("your") to stay impersonal & focused. |
| ThinkingIndicator.tsx | line 46 | `'Connecting to GitHub Copilot...'` | `'Connecting...'` | "GitHub Copilot" is product name, not user-facing context. Three dots unnecessary (already have spinner). |
| ThinkingIndicator.tsx | line 47 | `'Routing to agent...'` | *(no change)* | This one is good. Concise, accurate. |
| ThinkingIndicator.tsx | line 48 | `'Thinking...'` | *(no change)* | Good as-is. |
| commands.ts | line 72–77 | `/status` output: `Squad Status\n-----------\nTeam:     {count} agent(s)...\nRoot:     {path}\nMessages: {count}` | Tighten header "Team" label to show active count prominently: `` `Team: 3 agents (1 active)` `` on one line, max 60 chars. | Status output is a wall of text. Lead with the most relevant info (active count). One-line layout easier to scan. |
| commands.ts | line 79–84 | `/status` "Working:" section | `'  Working:'` + agent list | No change here. Already tidy. |
| commands.ts | line 160 | `'No team members yet.'` | `'No agents connected.'` | Team members are discoverable from team.md. "Not connected" is more accurate for what's shown here. |
| commands.ts | line 163 | `'Team Members:\n'` | `'Your Team:\n'` | One word saved. More warm. "Your" builds ownership. |
| commands.ts | line 177 | `/sessions` output: `Saved Sessions (X total)` | *(no change)* | Good as-is. |
| commands.ts | line 189 | `/resume` error: `No session found matching "{prefix}". Try /sessions to list.` | `No session found. Try: /sessions` | Shorter error. Removes user input echo (can be confusing if ID is long). |
| commands.ts | line 197 | `/resume` success: `✓ Restored session {id} ({count} messages)` | `✓ Restored {id} ({count} msgs)` | "msgs" is casual but saves 5 chars per line in narrow terminals. Still clear. |
| commands.ts | line 121–131 | `/help` compact layout | Current: `'How it works:', '  Just type what you need — Squad routes your message to the right agent.', ...` | Change intro to: `'How it works:', '  Type what you need. @Agent to direct. /help for commands.'` — one line instead of two. | Compact mode must fit in ≤60 cols. Current intro wraps awkwardly. Tighten to one sentence. |
| commands.ts | line 143–153 | `/help` normal layout | Same as compact but with more detail | Keep the details but ensure no line > 60 chars in compact mode. | Easier to scan if all lines are predictable length. |
| commands.ts | line 229–238 | `/init` help output | Current multi-line guidance | Tighten to: `'Cast your team by typing what you want to build.\n\nExample: "Build a React app with Node backend"\n\nTeam file: {path}'` | 3× shorter. Removes explanation of "what coordinator does" (users don't need to know internals). Focus on the action. |
| coordinator.ts | line 43–85 | `buildInitModePrompt()` system message | "You are the Squad Coordinator in Init Mode..." | No user-facing change (internal prompt). ✓ | This is internal LLM instruction, not user-facing. Skip. |

---

## Tone Guidelines for Implementation

**Kovash and Cheritto:** Apply these rules when implementing copy changes.

### ✓ DO

1. **Use active voice, present tense**
   - ✓ "Send a message to start" (not "A message can be sent to initiate")
   - ✓ "No agents connected" (not "Agents are not currently connected")

2. **Max 80 chars per status line**
   - All status output should be scannable in one visual sweep
   - Use line breaks strategically, not to avoid wrapping

3. **No internal process language**
   - ✗ "Routing", "dispatching", "spawning", "forking"
   - ✓ "Connecting", "waking", "starting", "preparing"

4. **Error messages: what + what-to-do**
   - ✗ "Connection failed"
   - ✓ "SDK disconnected. Try: squad doctor"

5. **Success messages: past tense, brief**
   - ✗ "Your session has been successfully restored and is ready to accept input"
   - ✓ "✓ Restored session"

6. **Avoid possessives ("your") in cycling labels**
   - Labels that rotate every few seconds should be impersonal
   - ✗ "Analyzing *your* request"
   - ✓ "Analyzing request"

7. **Keep command hints minimal**
   - AgentPanel, InputPrompt hints should not duplicate header hints
   - One source of truth for affordances (header > component defaults)

8. **Emoji usage: consistent, sparring**
   - ✓ ✓ (success), ✗ (error), ◆ (brand), ▸ (pointer)
   - ✗ Don't add new emoji without design review

### ✗ DON'T

1. Use technical jargon ("TTY", "SDK", "CLI", "shell") in user-facing messages
   - Exception: "Squad CLI" is the product name. "Squad shell" is not.

2. Explain system internals
   - ✗ "Coordinator is routing your message"
   - ✓ "Connecting to your team"

3. Use placeholder phrases
   - ✗ "Hmm, /{cmd}?" — too cute
   - ✓ "Unknown command: {cmd}. Try /help"

4. Bury calls-to-action
   - If a message requires user action, put it first: "Try X" not "X might work"

5. Exceed 80 chars without good reason
   - Some messages (errors with context) may exceed this, but default is brief

---

## Dead Zones — Places Needing More Feedback

These are moments where users see nothing or insufficient feedback:

### 1. **Cold SDK connection (0–3 seconds)**
- **Current:** ThinkingIndicator shows "Routing to agent..." only when `processing=true`
- **Issue:** SDK initialization is silent. User sees prompt but no activity.
- **Fix:** Show "Connecting..." immediately on `/help`, `/status`, or `/init` commands before SDK responds
- **Owner:** Cheritto (SDK integration in shell lifecycle)

### 2. **First message processing (3–7 seconds)**
- **Current:** Spinner cycles, ThinkingIndicator shows hints, but they're small and optional
- **Issue:** On slow networks, spinner alone doesn't convince user something is happening
- **Fix:** Ensure ThinkingIndicator always visible + pair with agent activity hint ("Keaton analyzing...")
- **Owner:** Cheritto (ThinkingIndicator component)

### 3. **Narrow terminal mode (≤60 cols)**
- **Current:** InputPrompt hints reduce to bare essentials: `Tab · ↑↓`
- **Issue:** New users on narrow terminals don't know Tab does anything
- **Fix:** Proposed: `Tab for help · ↑↓ for history` (still fits narrow but explains affordances)
- **Owner:** Kovash (InputPrompt hints)

### 4. **Agent list when registry empty**
- **Current:** AgentPanel shows "No agents active. Send a message to start."
- **Issue:** Doesn't tell user how to build a team if this is first run
- **Fix:** Check if team.md exists. If not, suggest: "No agents yet. Type what you want to build, or run: /init"
- **Owner:** Cheritto (AgentPanel empty state)

### 5. **Error recovery paths**
- **Current:** Some errors say "Try X" but user doesn't know what "X" does
- **Issue:** "squad doctor" is assumed to be known, but first-run users won't have heard of it
- **Fix:** Always include brief explanation: "Try: squad doctor (diagnoses setup issues)"
- **Owner:** Kovash/Cheritto (wherever commands.ts errors appear in shell)

### 6. **Session restore feedback**
- **Current:** `/resume <id>` shows `✓ Restored {id} ({count} msgs)` but doesn't say what happens next
- **Issue:** User restored a session. Can they just start typing? Is there a briefing?
- **Fix:** After restore, show: `✓ Restored 8 msgs. Continue here or /clear to start fresh.`
- **Owner:** Kovash (handleResume in commands.ts)

---

## Copy Rules Summary

**Short checklist for code review:**

- [ ] Max 80 chars per line in status/error output
- [ ] No "routing", "dispatching", "spawning" in user-facing text
- [ ] Every error includes at least one "Try: X" remediation
- [ ] Success messages use past tense ("Restored", not "Restoring")
- [ ] Emoji consistent across components (◆ brand, ✓ success, ✗ error, ▸ pointer)
- [ ] No duplicate affordance hints (header = source of truth)
- [ ] Cycling labels (ThinkingIndicator) ≤4 words, no possessives
- [ ] Command-not-found error friendly, not cute
- [ ] Empty states actionable (mention /init, /help, or next step)
- [ ] Dead zones filled with feedback within 500ms

---

## Files to Change

### Priority 1 (Quick wins)
1. `commands.ts` — Tighten help output, /status, error messages
2. `ThinkingIndicator.tsx` — Shorten phrases, remove "GitHub Copilot"
3. `AgentPanel.tsx` — Improve empty state message

### Priority 2 (Moderate effort)
1. `InputPrompt.tsx` — Improve hint text for narrow & normal modes
2. `App.tsx` — Tighten SDK error message

### Priority 3 (Strategic improvements)
1. `index.ts` — TTY error message rewrite
2. Coordinator integration — Add "Connecting..." feedback during init mode

---

## Sign-Off

**Design by:** Marquez
**For implementation by:** Kovash (REPL), Cheritto (TUI)
**Review by:** Brady

This spec is actionable. Each proposed change includes rationale. Implement in priority order.
