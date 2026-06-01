# Design Spec: Fixed Bottom Input Box

**Issue:** #679
**Designer:** Marquez (CLI UX Designer)
**Date:** 2026-03-05
**Status:** Proposal (Seeking Engineering Review)
**Target Release:** Alpha-2 or Later

---

## Overview

Currently, the Squad CLI input prompt flows linearly with message content — it renders below the message stream without a visual container or fixed position. The Copilot CLI and Claude CLI anchor their input in a squared-off box at the bottom of the terminal, fixed in place as content scrolls above.

**Proposal:** Implement a fixed-position input box at the terminal bottom, styled with a border, that:
- Stays visually anchored during scrolling
- Provides clear visual separation from content above
- Supports all interaction states (idle, typing, processing, error)
- Respects NO_COLOR and accessibility requirements
- Works across terminal sizes (120, 80, 40 columns)

---

## Problem Statement

### Current State
```
┌──────────────────────────┐
│ header + agents          │
├──────────────────────────┤
│ ❯ User message 1         │
│ ▸ Agent response         │
│ ❯ User message 2         │
│ ▸ Agent response         │
└──────────────────────────┘
◆ squad> [cursor]
 Tab completes · ↑↓ history
```

**Issues:**
1. Input blends with message content — no visual hierarchy
2. On narrow terminals, input text wraps inside prompt (confusing)
3. Processing spinner (when disabled) floats without container
4. No affordance that input is a distinct interaction zone

### Target State (Copilot/Claude Style)
```
┌──────────────────────────┐
│ header + agents          │
├──────────────────────────┤
│ ❯ User message 1         │
│ ▸ Agent response         │
│ [scrollable content]     │
│ ▸ Agent response         │
├──────────────────────────┤
│ ◆ squad> [cursor]        │
│ Tab completes ↑↓ history │
└──────────────────────────┘
```

**Benefits:**
1. Clear visual separation via border
2. Fixed position — doesn't scroll away
3. Container feels like a dedicated input zone
4. Space is optimized: header fixed top, input fixed bottom, content scrolls between

---

## ASCII Wireframes

### Wide Terminal (120 columns)

**Idle State:**
```
╔════════════════════════════════════════════════════════════════════╗
║  ___  ___  _   _  _   ___                                          ║
║ / __|/ _ \| | | |/_\ |   \                                         ║
║ \__ \ (_) | |_| / _ \| |) |                                        ║
║ |___/\__\_\\___/_/ \_\___/                                          ║
║ v0.0.1-alpha · Type naturally · @Agent to direct · /help           ║
║ ⚠️  Experimental preview — file issues at github.com/...           ║
╠════════════════════════════════════════════════════════════════════╣
║ ❯ What should we build first?                                      ║
║ ▸ Keaton: I'd suggest starting with...                             ║
║ ❯ Can you refactor the auth module?                                ║
║ ▸ Devon: Sure! Here's my approach...                               ║
║ [... more messages scroll above ...]                               ║
╠════════════════════════════════════════════════════════════════════╣
║ ◆ squad> [cursor]                                                  ║
║ Tab completes · ↑↓ history                                         ║
╚════════════════════════════════════════════════════════════════════╝
```

**Typing State:**
```
╠════════════════════════════════════════════════════════════════════╣
║ ◆ squad> Fix the login validation errors▌                         ║
║ Tab completes · ↑↓ history                                         ║
╚════════════════════════════════════════════════════════════════════╝
```

**Processing State:**
```
╠════════════════════════════════════════════════════════════════════╣
║ ◆ squad ⠙ > [Keaton thinking...]                                  ║
║ [working...]                                                       ║
╚════════════════════════════════════════════════════════════════════╝
```

**Error State (after submission):**
```
╠════════════════════════════════════════════════════════════════════╣
║ ◆ squad> [previous input shown]                                    ║
║ ✖ Error: Couldn't route to agent. Check your connection.           ║
╚════════════════════════════════════════════════════════════════════╝
```

---

### Normal Terminal (80 columns)

**Idle State:**
```
╔════════════════════════════════════════════════════════════════╗
║  ___  ___  _   _  _   ___                                      ║
║ / __|/ _ \| | | |/_\ |   \                                     ║
║ \__ \ (_) | |_| / _ \| |) |                                    ║
║ |___/\__\_\\___/_/ \_\___/                                      ║
║ v0.0.1-alpha · Type naturally · @Agent · /help                 ║
║ ⚠️  Experimental — github.com/bradygaster/squad              ║
╠════════════════════════════════════════════════════════════════╣
║ ❯ What should we build first?                                  ║
║ ▸ Keaton: Let's start with the auth...                         ║
║ ❯ Refactor login?                                              ║
║ ▸ Devon: I'll tackle that...                                   ║
║ [... scrollable ...]                                           ║
╠════════════════════════════════════════════════════════════════╣
║ ◆ squad> [cursor]                                              ║
║ Tab · ↑↓ history                                               ║
╚════════════════════════════════════════════════════════════════╝
```

**Typing (wrapped if necessary):**
```
╠════════════════════════════════════════════════════════════════╣
║ ◆ squad> Fix the login validation issue and refactor           ║
║ the password hashing logic▌                                    ║
║ Tab · ↑↓ history                                               ║
╚════════════════════════════════════════════════════════════════╝
```

---

### Compact Terminal (40 columns)

**Idle State:**
```
╔════════════════════════════════╗
║  SQUAD v0.0.1-alpha            ║
║ Type naturally · @Agent · /help║
╠════════════════════════════════╣
║ ❯ What should we build?        ║
║ ▸ Keaton: Let's start...       ║
║ ❯ Refactor login?              ║
║ ▸ Devon: Sure...               ║
╠════════════════════════════════╣
║ sq> [cursor]                   ║
║ Tab · history                  ║
╚════════════════════════════════╝
```

**Multi-line Input (wrapping):**
```
╠════════════════════════════════╣
║ sq> Fix the login               ║
║ validation and refactor         ║
║ the password logic▌             ║
║ Tab · history                   ║
╚════════════════════════════════╝
```

---

## Visual Hierarchy & Layout

### Component Nesting

```
<Box flexDirection="column">
  {/* Static: header stays at top */}
  <Static>
    {/* Header + agent panel */}
  </Static>

  {/* Dynamic: content scrolls */}
  {/* MessageStream + Separator */}

  {/* Fixed: input box stays at bottom */}
  <FixedInputBox>
    <Box borderStyle="round" borderColor="cyan">
      <InputPrompt />
      <HintText />
    </Box>
  </FixedInputBox>
</Box>
```

### Box Styling

| State | Border | Text Color | Background |
|-------|--------|-----------|-----------|
| Idle | Cyan round box | Cyan prompt + hint | (transparent) |
| Typing | Cyan round box | Cyan cursor visible | (transparent) |
| Processing | Cyan round box | Cyan spinner | (transparent) |
| Error | Red/yellow border? | Cyan prompt + error msg | (transparent) |
| NO_COLOR | ASCII `─` ─ `─` | Default text | (transparent) |

### Spacing

- **Top padding:** 1 line (separates input box from content)
- **Box padding:** `paddingX={1}` (inside the border)
- **Hint text:** Shown below input when idle (dimColor)
- **Processing text:** Shown below prompt when disabled (cyan)
- **Error messages:** Can appear below input box (separate message or inline)

---

## Interaction States

### 1. **Idle**
```
┌────────────────────────────────────┐
│ ◆ squad> [cursor]                  │
│ Tab completes · ↑↓ history         │
└────────────────────────────────────┘
```
- Prompt visible, cursor blinking
- Hint text dimmed below
- User can type, press Tab for completion, use ↑/↓ for history

### 2. **Typing**
```
┌────────────────────────────────────┐
│ ◆ squad> User types here▌          │
│ [hint text appears only if empty]  │
└────────────────────────────────────┘
```
- Cursor moves as user types
- Hint text only shows if input is empty (current behavior)
- Text can wrap to next line in the box (not extending outside)

### 3. **Processing (Disabled)**
```
┌────────────────────────────────────┐
│ ◆ squad ⠙ > [Keaton thinking...]  │
│ [working...]                       │
└────────────────────────────────────┘
```
- Spinner visible (Braille/ASCII based on NO_COLOR)
- Activity hint shows what agent is working (from `activityHint` prop)
- User cannot type, but `/` commands are allowed (existing behavior)
- "working..." label or buffer display if user started typing before process began

### 4. **Error (Post-Submit)**
Option A: **Error as system message above box**
```
┌────────────────────────────────────┐
│ ✖ Error: Connection failed         │
├────────────────────────────────────┤
│ ◆ squad> [cursor]                  │
│ Tab completes · ↑↓ history         │
└────────────────────────────────────┘
```
Error is added to the message stream above.

Option B: **Error inline (red border)**
```
┌ ✖ Error ─────────────────────────────┐
│ ◆ squad> [previous input]            │
│ Connection failed. Check network.    │
└────────────────────────────────────────┘
```
Border turns red/yellow, error message shown in box.

**Recommendation:** Option A (error as system message). Keeps InputPrompt component simple, doesn't require error state prop.

### 5. **NO_COLOR Mode**
```
sq [working...]
[previous input]

sq> [cursor]
Tab · history
```
- Use ASCII `─` instead of box-drawing
- Use `[working...]` instead of spinner
- All styling removed, text only
- Box structure preserved but plain

---

## Technical Feasibility Analysis

### Alt Screen Buffer (Capabilities & Tradeoffs)

Ink 6 can render to an **alternate screen buffer** (ANSI `\x1B[?1049h`), which some CLIs use for full-screen TUIs. This would:

**Pros:**
- Complete screen control — fixed footer is trivial
- Familiar to users (like `vim`, `less`, `nano`)
- Cleaner visual separation

**Cons:**
- **Requires explicit alt-buffer mode** — not default in Ink
- **Loss of scrollback history** — user can't scroll up after exit
- **Incompatible with streaming philosophy** — Squad emphasizes live message flow, not "full screen then exit"
- **Cold SDK startup visual** — whole screen white until first agent responds (bad UX during 3-5 second wait)
- **Escape sequence issues** — some terminals may not support alt buffer (older SSH clients, constrained environments)

**Verdict:** ❌ **NOT recommended for Squad.**

Alt-buffer is right for text editors and dashboards, but Squad is a streaming conversation tool. Users want scrollback, message history, and the ability to reference past context. Alt-buffer doesn't fit.

### Fixed Positioning Within Standard Buffer

Ink's `Static` component already solves "fixed at top" for the header. For fixed-at-bottom:

**Option 1: Reverse Box layout**
```tsx
<Box flexDirection="column-reverse">
  <InputPrompt /> {/* renders last → appears at bottom */}
  {/* messages and header above */}
</Box>
```
**Status:** ✅ Possible, but breaks natural scroll order. Messages render bottom-up. Confusing.

**Option 2: Custom position tracking**
Monitor terminal height and manually position input box. Use `marginTop` to push content up.
```tsx
const terminalHeight = useTerminalHeight?.(); // doesn't exist in Ink
const contentHeight = calculateMessageHeight(messages);
const inputMarginTop = Math.max(0, terminalHeight - contentHeight - 3);
<Box marginTop={inputMarginTop}><InputPrompt /></Box>
```
**Status:** ❌ Ink doesn't expose terminal height. Ink only exposes width.

**Option 3: Use Ink's `Static` for input box too**
```tsx
<Static items={[{kind: 'header'}, ..., {kind: 'footer'}]}>
  {item => item.kind === 'footer' ? <InputPrompt /> : ...}
</Static>
```
**Status:** ✅ Possible. Static items render once and stay pinned. Multiple Static components can render independently — one for header, one for footer.

### Recommended Implementation Path

**Phase 1 (MVP):** Render InputPrompt in a bordered `<Box>` with padding. No alt-buffer.
```tsx
<Box marginTop={1} borderStyle="round" borderColor="cyan">
  <InputPrompt />
  <HintText />
</Box>
```
- ✅ Visually separates input from content
- ✅ Same linear scroll model (users can scroll past it with `less` / paging)
- ✅ No terminal capability detection needed
- ✅ Works with Ink 6 as-is

**Phase 2 (Polish):** Refactor to use Static positioning if Ink adds height APIs.
- Conditional: only if users report scrolling issues

**Phase 3 (Advanced, future):** Optional alt-buffer mode behind feature flag (for power users).
- `--fullscreen` flag to enter alt-buffer mode if desired
- Default stays traditional scrollback

---

## NO_COLOR & Accessibility

### NO_COLOR Compliance
The fixed input box must degrade gracefully:

**Color Mode:**
```
╔════════════════════════════════════╗
│ ◆ squad> [cursor]                  │
│ Tab completes · ↑↓ history         │
╚════════════════════════════════════╝
```

**NO_COLOR Mode:**
```
─────────────────────────────────────
sq> [cursor]
Tab · history
─────────────────────────────────────
```

**Implementation:**
```tsx
const noColor = isNoColor();

return (
  <Box borderStyle={noColor ? undefined : 'round'} borderColor={noColor ? undefined : 'cyan'}>
    <Text color={noColor ? undefined : 'cyan'} bold>{narrow ? 'sq>' : '◆ squad>'}</Text>
    <Text>{value}</Text>
    <Text color={noColor ? undefined : 'cyan'} bold>▌</Text>
    {!value && <Text dimColor>{getHintText(messageCount, narrow)}</Text>}
  </Box>
);
```

### Terminal Width Adaptation

| Width | Prompt | Hint | Border |
|-------|--------|------|--------|
| ≥100 | `◆ squad>` | Full text | `╔═══╗` box-drawing |
| 61-99 | `◆ squad>` | Abbreviated | Box-drawing |
| ≤60 | `sq>` | Minimal | Box-drawing or `─` line |

### Keyboard Navigation
- ✅ Tab completion already works
- ✅ ↑/↓ history already works
- ✅ Ctrl+C exit already works
- ✅ Slash commands work during processing

No changes needed for a11y.

---

## Copy Review

### Prompts & Labels
- **Idle:** `◆ squad>` (consistent with brand mark)
- **Hint:** `Tab completes · ↑↓ history` (imperative, scannable)
- **Processing:** `[Keaton thinking...]` (agent name + action)
- **Error:** "Connection failed. Try: (1) check network (2) squad doctor"

**Standards:**
- Short, direct verbs (no "ing" forms where possible)
- No jargon ("routing to agent" OK, "orchestrating" not OK)
- Punctuation: period at end of full sentences, colon for labels

### Validation
- ✅ All prompts ≤60 characters
- ✅ Hints ≤40 characters
- ✅ Error messages start with remediation verb (Check, Run, Try)

---

## Implementation Phasing

### Phase 1 — Box Styling (Week 1)
**Files to change:**
- `packages/squad-cli/src/cli/shell/components/InputPrompt.tsx` — Wrap in `<Box borderStyle="round">`, add `marginTop={1}`
- `packages/squad-cli/src/cli/shell/components/App.tsx` — Update layout comments

**What ships:**
- Visual box around input prompt
- Same interaction model (no behavior changes)
- Works at all terminal widths

**Testing:**
- Manual: run `squad` and verify box renders
- Test: assert that input box has border in color mode, no border in NO_COLOR

**Acceptance:**
- [ ] InputPrompt renders with `borderStyle="round"` in color mode
- [ ] NO_COLOR mode has no border
- [ ] Box width matches content width (80 char limit)

### Phase 2 — Hint Text Polish (Week 1)
**Files to change:**
- `packages/squad-cli/src/cli/shell/components/InputPrompt.tsx` — Move hint text into box, add padding

**What ships:**
- Hint text ("Tab completes") now appears inside the box
- Better visual containment

**Testing:**
- Manual: verify hint text placement at different widths
- Test: assert hint text is dimColor and only shows when input is empty

**Acceptance:**
- [ ] Hint text appears inside box with `marginTop={1}`
- [ ] Hint text is dimColor (matches current behavior)
- [ ] Width-adaptive hints work at 40/80/120 columns

### Phase 3 — Error State Refinement (Week 2, optional)
**Files to change:**
- `packages/squad-cli/src/cli/shell/components/App.tsx` — Add error message handling below input box
- `packages/squad-cli/src/cli/shell/commands.ts` — Standardize error output (prefix with `✖`)

**What ships:**
- Errors appear as system messages above input box
- Consistent error formatting

**Testing:**
- Manual: trigger error (e.g., bad @agent mention)
- Test: assert error message role is 'system' and appears above input box

**Acceptance:**
- [ ] Error messages appear above input box (not inline)
- [ ] Error messages start with `✖` prefix
- [ ] Input box remains interactive after error

### Phase 4 — Static Positioning (Future)
**Precondition:** Ink adds `useTerminalHeight()` or similar.

**Files to change:**
- `packages/squad-cli/src/cli/shell/components/App.tsx` — Refactor to use Static for footer

**What ships:**
- Input box stays visible even as messages scroll
- True fixed-bottom positioning

**Testing:**
- Manual: send 50+ messages, verify input box doesn't scroll off
- Test: assert Static items have correct keys

**Acceptance:**
- [ ] Input box is in Static footer
- [ ] No visual layout shift during message flow

---

## Design Decisions Log

### Decision: Why No Alt-Buffer?
**Date:** 2026-03-05
**Context:** Copilot/Claude use alt-buffer for fixed input.
**Decision:** Don't use alt-buffer for MVP.
**Rationale:**
1. Squad is streaming-first, not full-screen-first
2. Users value scrollback history (past context)
3. Alt-buffer breaks on some terminals (SSH, web-based)
4. Same visual effect achievable with `borderStyle="round"` in standard buffer
5. Simpler to ship, easier to test

### Decision: Border Style = "round"
**Date:** 2026-03-05
**Context:** Could use `single`, `double`, `round`, or custom.
**Decision:** Use `round` (╔═╗╚═╝╠═╣).
**Rationale:**
1. Matches header border style (consistency)
2. Softer visual feel than `double`
3. Clearly distinct from message separators (`─────`)
4. NO_COLOR fallback is clean

### Decision: Error Messages as System Messages
**Date:** 2026-03-05
**Context:** Could inline errors in box or show above.
**Decision:** Errors appear as system messages above input box.
**Rationale:**
1. Keeps InputPrompt component focused (no error state prop)
2. Errors are historical (user needs to see/understand what happened)
3. Matches current architecture (App handles errors)
4. User can scroll back to see error in context

---

## Wireframe Summary

| Width | State | Appearance |
|-------|-------|-----------|
| 120 | Idle | `╔═══════════╗ ◆ squad> ▌ ╚═══════════╝` |
| 80 | Typing | `╔═══════╗ ◆ squad> text text text▌ ╚═══════╝` |
| 40 | Processing | `╔═════╗ sq ⠙ > [agent...] ╚═════╝` |
| Any | NO_COLOR | `─────── sq> [text] ───────` |

---

## Success Metrics

1. **Visual clarity:** Input box is obviously a separate zone (border is visible and intentional)
2. **Terminal compatibility:** Works at 40, 80, 120 columns without layout breaks
3. **Accessibility:** NO_COLOR mode degrades gracefully (no color loss)
4. **Performance:** No frame drops or render slowdown vs. current InputPrompt
5. **User feedback:** Testers say "input feels more grounded" or "I know where to type"

---

## Open Questions for Engineering Review

1. **Ink Static limitations:** Can we use Static for both header and footer simultaneously without double-rendering?
2. **Render order:** Does `marginTop` on InputPrompt interfere with Ink's layout calculations?
3. **Performance:** Any perf implications of adding `borderStyle="round"` to InputPrompt?
4. **NO_COLOR detection:** Does `isNoColor()` work correctly in all test environments?
5. **Multi-line input:** How should long input (wrap to 2+ lines) behave inside the box?

---

## References

- [Ink Box component](https://github.com/vadimdemedes/ink#box)
- [Ink Static component](https://github.com/vadimdemedes/ink#static)
- [Copilot CLI Input](https://github.com/github/copilot-cli) — reference for fixed-box UX
- Claude CLI — reference for aesthetic
- Related UX audit: `.squad/agents/marquez/history.md` (Feb 2026)

---

## Appendix: Alternative Approaches Considered

### Alt 1: Inline Border (No Box Container)
```
◆ squad> [cursor]
────────────────────────────
```
- ❌ Weak visual hierarchy
- ❌ Border sits below input (confusing)
- ❌ Doesn't match target (Copilot/Claude have boxes)

### Alt 2: Underline Instead of Box
```
┌────────────────────────────┐
│ ◆ squad> [cursor]          │
└────────────────────────────┘
```
vs. just underline:
```
◆ squad> [cursor]
─────────────────────────────
```
- ❌ Underline alone is weaker (less containment feel)
- ✅ Uses less vertical space
- **Verdict:** Box is stronger UX, worth the line

### Alt 3: Highlight Background Color
```
◆ squad> [cursor]
(dark gray or subtle background)
```
- ❌ NO_COLOR compatibility issue (can't show color difference)
- ❌ Looks like selection/highlight
- **Verdict:** Border is better (works in NO_COLOR)

### Alt 4: Multiple Input Zones (Top + Bottom)
One prompt at top (near header), one at bottom.
- ❌ Confusing (which one is active?)
- ❌ Violates "single place to type" affordance
- **Verdict:** Single input zone at bottom, as proposed.

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-03-05 | Marquez | Initial proposal — ASCII wireframes, feasibility analysis, phasing plan |
