# Hostile QA Session Report — First 30 Seconds

**Date:** 2026-02-24
**Agent:** Waingro (Hostile QA)
**Mission:** Product love sprint — test first-time user journey and file issues for every moment that isn't delightful

## Scope

Tested the critical first 30 seconds of user experience:
1. `squad --help` (discovery phase)
2. `squad init` (setup phase) — *skipped, covered by issue #387*
3. `squad` (first launch)
4. First message — *skipped, requires SDK, covered by issue #397*

## Issues Filed

### P1 Blockers (3)

**#417 — Root cli.js defaults to init instead of shell**
- **Problem:** Root `cli.js` bundle is stale (v0.6.0-alpha.0), contradicts documented behavior
- **Impact:** First-time users who run `node cli.js` get init ceremony instead of shell
- **Evidence:** Lines 1963-1967 in cli.js show `if (!cmd || cmd === "init")` — wrong
- **Reproduction:** `node cli.js` (no args) → runs init ceremony, not shell

**#424 — Help wall of text drowns impatient users**
- **Problem:** `squad --help` returns 44 lines, 16 commands
- **Impact:** User needs 2 commands (init, shell) but must scan through scrub-emails, aspire, plugin marketplace
- **Evidence:** Measured 44 lines, 1331ms render time (Node.js startup floor)
- **Fix:** Split into quick help (≤10 lines) and extended (`--all`)

**#427 — Shell launch has 2-4 seconds of dead air**
- **Problem:** Running `squad` (no args) produces 2-4 seconds of silence before welcome banner
- **Impact:** "Is this working?" anxiety, bailout risk increases every second
- **Evidence:** Reproduced with stopwatch, measured 2+ seconds to first visual output
- **Fix:** Add `◆ Loading squad...` spinner before Ink render

### P2 Issues (2)

**#429 — Version format inconsistent**
- Root cli.js: `squad 0.6.0-alpha.0`
- Proper entry: `0.8.5.1`
- Blocked by #417 (stale bundle)

**#431 — Empty/whitespace args show help**
- Current behavior is defensive (prevents shell launch from accidental empty args)
- Technically correct, low priority edge case

## Test Coverage

**Tested successfully:**
- ✅ Help command: measured line count (44), render time (1331ms)
- ✅ Version command: bare number format (correct per CLI conventions)
- ✅ Invalid command: friendly error with exit code 1
- ✅ Empty/whitespace args: shows abbreviated help (defensive)
- ✅ Status with no .squad: graceful "none" with hint
- ✅ Unicode handling: piped emoji/CJK/Hebrew works correctly
- ✅ Root vs proper entry point divergence: confirmed stale bundle

**Not tested (out of scope):**
- ❌ Interactive shell behavior (requires user input simulation)
- ❌ Agent message dispatch (requires SDK connection, long-running)
- ❌ Concurrent multi-agent routing
- ❌ Race conditions with rapid input
- ❌ Memory leaks over extended sessions

## Key Findings

1. **The root bundle is a landmine** — v0.6.0-alpha.0 vs v0.8.5.1, wrong behavior
2. **Help is overwhelming** — 44 lines to find 2 essential commands
3. **Dead air creates anxiety** — 2-4 seconds of silence before first feedback
4. **Error handling is good** — friendly messages, proper exit codes, remediation hints
5. **Edge cases are solid** — empty args, unicode, invalid commands all handled gracefully

## Reproduction Artifacts

Created `test-fixtures/hostile-qa-first-30-seconds.ps1`:
- Automated test script demonstrating all 5 issues
- Measures timing, line counts, version formats
- Run: `.\test-fixtures\hostile-qa-first-30-seconds.ps1`
- Output: Color-coded pass/fail for each test

## Decision Document

Filed `.squad/decisions/inbox/waingro-first-30-seconds-ux.md`:
- Proposes 3 UX standards for first 30 seconds
- No stale entry points (single source of truth)
- Help respects impatient users (≤10 lines default)
- No dead air exceeding 1 second (show progress within 500ms)

## Fix Priority

1. **#417** — Regenerate/remove root cli.js (highest impact)
2. **#427** — Add loading spinner to shell launch (user psychology)
3. **#424** — Tier help output (discovery experience)

## Success Metrics

**Before:**
- 3 P1 blockers in first 30 seconds
- Help: 44 lines
- Shell launch: 2-4s dead air
- Root entry: runs wrong command

**After (when fixed):**
- Help: ≤10 lines (quick), full help with `--all`
- Shell launch: <1s to first feedback
- Single entry point, always correct behavior
- Zero P1 blockers in first 30 seconds

## Related Issues (Already Open)

These were filed earlier (2025-07-25) and remain open:
- #387 — Init ceremony animations waste 2+ seconds
- #395 — Help is 50 lines (now updated to #424 with exact count)
- #397 — Cold SDK connection on first message (5-10s dead air)
- #399 — Welcome banner typewriter blocks UI (500ms)
- #401 — Input dropped during processing

## Tools Used

- PowerShell stopwatch for timing measurements
- `gh issue create` for filing GitHub issues
- `Measure-Object -Line` for counting help output
- Manual testing with various edge cases (unicode, empty args, invalid commands)

## Verdict

**The first 30 seconds have 3 P1 blockers that create bailout risk.**

The proper entry point (`packages/squad-cli/dist/cli-entry.js`) works well. The root bundle is the problem. Fix the stale bundle, add loading feedback, and tier the help output to eliminate friction.

Edge case handling, error messages, and unicode support are all solid. The happy path works — it's the entry experience that needs polish.
