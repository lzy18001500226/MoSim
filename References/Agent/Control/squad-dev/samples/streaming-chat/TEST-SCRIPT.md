# TEST-SCRIPT: streaming-chat

Manual test walkthrough for the streaming-chat MVP Summit demo.

---

## Prerequisites

- Node.js ≥ 20
- Run `npm install` in `samples/streaming-chat/`
- For live mode: authenticated with GitHub Copilot (`gh auth login`)

---

## Test 1 — Demo Mode Startup

```bash
SQUAD_DEMO_MODE=true npx tsx index.ts
```

**Expected:**
- [x] Banner displays: `🎬 Squad Streaming Chat · MVP Summit`
- [x] Cast shows 3 agents with colored bullets: McManus (cyan), Kobayashi (magenta), Fenster (yellow)
- [x] Message: `Running in demo mode — responses are simulated`
- [x] Prompt appears: `◆ you >`

---

## Test 2 — Backend Routing

Type: `How should I design the API endpoints?`

**Expected:**
- [x] Header shows: `McManus (Backend)` in cyan
- [x] Response streams word-by-word (visible character-at-a-time output)
- [x] Response is backend-themed (mentions Express, API, etc.)
- [x] Prompt reappears after response completes

---

## Test 3 — Frontend Routing

Type: `Build me a nice UI layout`

**Expected:**
- [x] Header shows: `Kobayashi (Frontend)` in magenta
- [x] Response streams word-by-word
- [x] Response is frontend-themed (mentions CSS, components, etc.)

---

## Test 4 — Tester Routing

Type: `I need more test coverage`

**Expected:**
- [x] Header shows: `Fenster (Tester)` in yellow
- [x] Response streams word-by-word
- [x] Response is test-themed (mentions coverage, mocks, etc.)

---

## Test 5 — Default Routing

Type: `What do you think?`

**Expected:**
- [x] Falls through to McManus (Backend) as default
- [x] Response streams normally

---

## Test 6 — Quit Command

Type: `/quit`

**Expected:**
- [x] Displays: `👋 Goodbye!`
- [x] Process exits cleanly (exit code 0)

---

## Test 7 — Empty Input

Press Enter without typing anything.

**Expected:**
- [x] Prompt reappears immediately (no error)

---

## Test 8 — Graceful Copilot Fallback (no SQUAD_DEMO_MODE)

```bash
npx tsx index.ts
```

**Expected (without Copilot auth):**
- [x] Shows: `⚠ Could not connect to Copilot: ...`
- [x] Shows: `Falling back to demo mode`
- [x] Chat works normally in demo mode

---

## Test 9 — Unit Tests

```bash
npx vitest run
```

**Expected:**
- [x] All tests pass
- [x] Tests cover: routing, demo responses, pipeline wiring, agent casting
