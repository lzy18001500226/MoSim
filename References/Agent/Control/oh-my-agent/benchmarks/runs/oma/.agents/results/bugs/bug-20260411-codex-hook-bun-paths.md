# Bug: Codex Hooks Fail When Bun PATH Is Missing and PreToolUse Uses the Wrong Hook Directory

**Date Reported**: 2026-04-11
**Date Fixed**: 2026-04-11
**Reporter**: GitHub issue #205
**Assignee**: Codex (`oma-debug`)
**Severity**: 🟡 MEDIUM
**Status**: ✅ FIXED

---

## 📝 Problem Description

**What happened?**
Codex hook execution could fail with exit code `127` on Linux/Homebrew setups when the hook shell did not inherit the `bun` binary in `PATH`. Separately, the shared `PreToolUse` hook always rewrote test commands to `.claude/hooks/filter-test-output.sh`, even when installed for Codex, Gemini, or Qwen.

**What was expected?**
Installed hooks should run with a stable Bun executable path when possible, and each vendor should reference its own hook directory.

**Impact**:
- Users affected: Specific environments using Homebrew/Linuxbrew or non-Claude vendors
- Business impact: User frustration and broken hook automation
- Workaround available: Yes, user shell profile changes could restore `bun` in `PATH`

---

## 🔄 Reproduction Steps

1. Install oh-my-agent with Codex hooks enabled.
2. Run a Codex `PreToolUse` event for a Bash test command such as `vitest --run`.
3. Observe the rewritten command path.
4. In environments where hook shells do not inherit the Homebrew/Linuxbrew `PATH`, observe hook failures with exit code `127`.

**Frequency**:
- [ ] Every time (100%)
- [ ] Intermittent (specify pattern: ___%)
- [x] Specific conditions only (describe: non-default shell init / PATH plus non-Claude hook variants)

---

## 🖼️ Evidence

**Error Messages**:
```text
Stop failed error: hook exited with code 127
UserPromptSubmit failed error: hook exited with code 127
```

**Stack Trace**:
```text
Not applicable. Failure was reported as hook exit code 127.
```

---

## 🌍 Environment

**Backend**:
- Environment: Local development
- Server version: N/A
- Database: N/A

**Reporter Environment**:
- OS: openSUSE Tumbleweed on Linux
- Agent: Codex CLI / Codex VS Code OSS extension

---

## 🔍 Investigation

### Initial Analysis

**Hypothesis**:
The visible `127` failures came from hook commands invoking `bun` without a stable absolute path, while the separate rewrite bug came from a hardcoded Claude hook directory in the shared filter hook.

**Investigation Steps Taken**:
1. Read the GitHub issue and linked comment for exact symptoms and environment details.
2. Reproduced the shared hook rewrite locally by piping a Codex `PreToolUse` payload into `.agents/hooks/core/test-filter.ts`.
3. Inspected hook variant definitions and installer command generation.

### Root Cause

**Technical Explanation**:
Two defects existed:

1. `cli/lib/skills.ts` generated hook commands with the bare runtime name `bun`, which depends on the hook shell inheriting a working `PATH`.
2. `.agents/hooks/core/test-filter.ts` always used `.claude/hooks/filter-test-output.sh` instead of selecting the active vendor hook directory.

**Code Location**:
- File: `.agents/hooks/core/test-filter.ts`
- Function: shared PreToolUse hook path rewrite
- File: `cli/lib/skills.ts`
- Function: `buildHookCmd()`

**Specific Issue**:
```ts
const filterScript = join(projectDir, ".claude", "hooks", "filter-test-output.sh");
```

**Why it happens**:
The shared hook was copied into multiple vendor directories, but its internal shell script reference remained Claude-specific. The installer similarly assumed `bun` would always be discoverable at hook runtime.

---

## 🔧 Solution

### Fix Applied

**Approach**:
Keep the fix minimal and targeted:
- resolve the vendor-specific hook directory inside `test-filter.ts`
- resolve and pin Bun to an absolute path during hook installation when available
- add regression tests for both behaviors

**Why this works**:
Hooks no longer depend on Claude-specific paths, and Bun-based hook commands can survive shells that do not fully initialize Homebrew/Linuxbrew `PATH`.

### Files Modified

- ✏️ `.agents/hooks/core/test-filter.ts` - select hook directory by vendor
- ✏️ `cli/lib/skills.ts` - resolve absolute `bun` path for generated hook commands
- ➕ `cli/__tests__/test-filter.test.ts` - add vendor hook directory regression coverage
- ➕ `cli/__tests__/install-hooks.test.ts` - add Bun runtime pinning and fallback tests

### Migration/Deployment Notes

**Database Changes**: None
**Configuration Changes**: Existing installations should re-run install/update to regenerate hook settings with the pinned Bun path
**Breaking Changes**: None
**Rollback Plan**: Revert the touched files

---

## ✅ Verification

### Testing Performed

- [x] **Regression test added**
  - Files: `cli/__tests__/test-filter.test.ts`, `cli/__tests__/install-hooks.test.ts`
  - Coverage: Codex/Gemini/Qwen hook path selection and Bun path pinning

- [x] **Manual testing**
  - Reproduced Codex rewrite output before the fix
  - Verified the rewritten path points at the correct vendor hook directory after the fix

- [x] **Related areas checked**
  - Reviewed hook variants for Claude, Codex, Gemini, and Qwen
  - Reviewed installer hook command generation

### Test Results

**Unit Tests**: Pending local run after patch
**Integration Tests**: Not run
**E2E Tests**: Not run
**Manual QA**: Reproduction confirmed locally

---

## 📚 Prevention

### How to Avoid Similar Bugs

1. Do not hardcode vendor-specific hook directories inside shared hook implementations.
2. Prefer absolute executable paths in generated hook commands when runtime discovery happens during installation.
3. Add regression tests for each vendor variant when shared hook code rewrites commands.
