# PRD: Squad CLI Visual Polish

**Status:** Draft
**Author:** Squad Team (coordinated review)
**Date:** 2026-03-01
**Version:** Post-v0.8.6.14-preview

---

## 1. Overview

The Squad CLI is approaching its first public beta. A full-team review of 9 screenshots (see `/images/001.png` through `009.png`) identified **10 improvement areas** ranging from bugs to UX enhancements. This PRD documents each finding and proposes solutions, prioritized for iterative delivery.

## 2. Goals

- Ship a polished alpha-quality CLI that users recognize as "early but intentional"
- Eliminate UX dead zones (blank screens, static spinners during long waits)
- Fix rendering bugs (input duplication)
- Establish a foundation for future UI investment with designers

## 3. Non-Goals (for this PRD)

- Full UI redesign (input box position, layout overhaul)
- Performance optimization of SDK response times
- New features or commands

---

## 4. Findings & Proposed Solutions

### 4.1 — Blank Screen During Loading (P0 — Bug)
**Images:** 003
**Owner:** Cheritto 🖥️ / Marquez 🎨
**Problem:** Between operations, the terminal shows a completely blank screen with zero visual feedback. Users don't know if the CLI is working, frozen, or crashed.
**Proposed Solution:**
- Always render the header banner and agent status bar, even during initial SDK connection.
- Show a skeleton/placeholder UI while waiting for the first response.
- Add a subtle animation or progress indicator during the connecting phase.

### 4.2 — Static Spinner During Long Waits (P0 — UX)
**Images:** 002, 007, 008
**Owner:** Cheritto 🖥️ / Verbal 🧠
**Problem:** The ThinkingIndicator shows "Routing to agent..." for 40–45 seconds. This is the same message the entire time. Competing CLIs (GitHub Copilot CLI, Claude CLI) rotate through interesting messages.
**Proposed Solution:**
- Rotate the activity hint text every ~3 seconds.
- Message categories:
  - **Gerunds:** Fun "-ing" words (Thinking, Analyzing, Considering, Synthesizing...)
  - **Codebase facts:** "Your repo has 47 TypeScript files" / "Last commit was 2 hours ago"
  - **Domain trivia:** Context-aware facts about what the user is building
  - **Useful info:** Dependency status, vulnerability hints
- Phase 1 (ship today): Rotating gerund phrases
- Phase 2: Integrate codebase-aware factoids via lightweight repo analysis
- Phase 3: Domain-aware trivia using project context from `.squad/`

### 4.3 — Input Text Duplication (P0 — Bug)
**Images:** 006
**Owner:** Cheritto 🖥️
**Problem:** User input text appears twice — once in the input prompt area and again duplicated below it. Likely a race condition in the paste detection or input buffering logic.
**Proposed Solution:**
- Audit `InputPrompt.tsx` paste debounce logic (the 10ms `setTimeout` on Enter).
- Add regression test: multi-line paste should not duplicate.
- Check if `valueRef.current` and `bufferRef.current` can conflict during the disabled→enabled transition.

### 4.4 — Empty Space Above Content (P1 — UX)
**Images:** 002, 004
**Owner:** Cheritto 🖥️
**Problem:** After the header, there's a massive empty gap before content appears. The response text is pushed to the bottom of the viewport, leaving most of the screen blank.
**Proposed Solution:**
- Investigate Ink's `Static` component scroll behavior — items may be rendering at the bottom of the terminal viewport.
- Consider a "content starts at top" layout where responses fill from top-down.
- Alternatively, anchor content to the cursor position rather than the viewport bottom.

### 4.5 — Markdown Table Wrapping (P1 — UX)
**Images:** 005, 006
**Owner:** Cheritto 🖥️
**Problem:** Markdown tables rendered in agent responses break awkwardly when lines wrap. Pipe characters (`|`) end up mid-line, and alignment is lost.
**Proposed Solution:**
- Detect table blocks in rendered markdown and apply terminal-width-aware formatting.
- Options: (a) Truncate long cells with `…`, (b) Switch to stacked key-value layout on narrow terminals, (c) Add horizontal scroll hint.
- Short-term: Cap table content width to `terminalWidth - indent - padding`.

### 4.6 — No Experimental/Alpha Banner (P0 — Ship Blocker)
**Images:** All
**Owner:** McManus 📣 / Marquez 🎨
**Problem:** Nothing in the CLI communicates that this is an early release. Users need to know "here there be dragons."
**Proposed Solution:**
- Add a line in the header box: `⚠️  Experimental preview — file issues at github.com/bradygaster/squad`
- Use dim/yellow styling to be visible but not distracting.
- Remove or update this once the CLI reaches stable.

### 4.7 — Input Box Redesign (P2 — Future)
**Images:** 009
**Owner:** Marquez 🎨 / Cheritto 🖥️
**Problem:** Brady noted he'd prefer the input box squared off and bottom-anchored, similar to GitHub Copilot CLI and Claude CLI. Not a today problem, but flagged for future design work.
**Proposed Solution:**
- Research Copilot CLI and Claude CLI input affordances.
- Prototype a bottom-pinned input box with squared borders.
- Consider Ink's `Box` with `borderStyle="single"` or `"classic"`.
- Needs designer input before implementation.

### 4.8 — Separator Line Styling (P2 — Polish)
**Images:** 005, 006, 009
**Owner:** Redfoot 🎨
**Problem:** Turn separators are plain repeated `─` characters. They're functional but could be more expressive.
**Proposed Solution:**
- Options: gradient fade-out separators, thin/thick alternation, or subtle color.
- Keep it minimal — separators should recede, not attract attention.
- Respect NO_COLOR: use plain `---` in accessibility mode.

### 4.9 — Color Contrast / Accessibility (P1 — Accessibility)
**Images:** 005
**Owner:** Nate ♿
**Problem:** Dim text (`dimColor`) may be hard to read on some terminals, especially for users with low vision. The team table's "What They Do For You" column uses standard dim text.
**Proposed Solution:**
- Audit all `dimColor` usage against WCAG contrast guidelines for terminal themes (dark and light).
- Provide higher-contrast alternatives for critical information.
- Test with popular terminal themes: default dark, Solarized, Dracula, One Dark.
- Ensure NO_COLOR mode is fully functional and readable.

### 4.10 — Response Duration Prominence (P2 — Polish)
**Images:** 007, 008
**Owner:** Marquez 🎨
**Problem:** The response duration `(42.2s)` and `(45.9s)` are shown but very subtle (dimColor). For an alpha, making timing visible helps set user expectations.
**Proposed Solution:**
- Make duration slightly more prominent for long responses (>10s).
- Consider color-coding: green (<5s), yellow (5-30s), red (>30s).
- Add timing breakdown if available (SDK connection + routing + generation).

---

## 5. Priority Matrix

| Priority | Issue | Ship Blocker? |
|----------|-------|---------------|
| P0 | 4.6 Experimental banner | ✅ Yes |
| P0 | 4.2 Rotating wait messages | ✅ Yes |
| P0 | 4.1 Blank screen during loading | No (next sprint) |
| P0 | 4.3 Input text duplication | No (bug, next sprint) |
| P1 | 4.4 Empty space above content | No |
| P1 | 4.5 Markdown table wrapping | No |
| P1 | 4.9 Color contrast | No |
| P2 | 4.7 Input box redesign | No (needs design) |
| P2 | 4.8 Separator styling | No |
| P2 | 4.10 Duration prominence | No |

## 6. Success Criteria

- [ ] CLI displays experimental banner on every launch
- [ ] Wait spinner rotates messages every ~3 seconds
- [ ] Public beta published to npm
- [ ] GitHub issues created for all P0–P2 items
- [ ] No regressions in existing functionality

## 7. Future Considerations

- **Designer collaboration:** Brady expressed interest in working with designers. The input box redesign (4.7), separator styling (4.8), and overall layout should be designer-led.
- **Codebase-aware wait messages:** Phase 2 of rotating messages should analyze the user's repo and surface relevant facts during wait time.
- **Domain trivia:** Phase 3 could use the project's `.squad/` context to generate fun facts about the user's domain (e.g., Tetris history for a Tetris game).
