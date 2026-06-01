# Debug Agent Result — Phase 3 Hardening (T18 + T19)

## Status: completed

**Build**: `bun run --cwd cli build` ✅ (3.29 MB, 1291 modules, zero TS errors)

---

## Summary

Completed T18 (YAML error line numbers + getModelSpec audit) and T19 (SECURITY.md) from the model-preset refactor plan.

---

## T18a — YAML error line numbers

All user-edited YAML config parse sites now surface `file:line:col` from the yaml library's `e.linePos[0]` on `YAMLParseError`.

### Files changed

**`cli/io/runtime-dispatch.ts`** — `loadUserConfig()`
- Split single try-catch into read-catch + parse-catch
- Parse failure throws `ConfigError` with `${canonicalPath}:${line}:${col}` extracted from `e.linePos[0]`

**`cli/platform/agent-config.ts`** — `parseYamlValue()`, `parseOmaConfig()`, `parseCliConfig()`
- Added `yamlErrorPosition(err)` helper that extracts `e.linePos[0]`
- `parseYamlValue(content, filePath?)` now `console.warn`s with location on failure
- `parseOmaConfig` and `parseCliConfig` accept optional `filePath` and forward it
- `readCliConfig()` and `resolveVendor()` pass their resolved config path

**`cli/utils/config.ts`** — `loadOmaConfig()`
- Split read/parse; parse failure emits `console.warn` with `${configPath}:${line}:${col}` (returns null — callers handle gracefully)

**`cli/commands/migrations/008-model-preset.ts`** — oma-config, defaults.yaml, models.yaml parse blocks
- Each of the three parse blocks now catches with position-aware `console.warn`
- All treat malformed YAML as empty (non-fatal for migration path)

### Regression test
`cli/io/runtime-dispatch.test.ts` is being rewritten by qa Phase 3b. Test addition for ConfigError + position is deferred to that agent (noted in `.serena/memories/result-debug-hardening.md`).

---

## T18b — getModelSpec call-site audit

All production call sites verified:

| Call site | userModels forwarded? | Action |
|---|---|---|
| `cli/io/runtime-dispatch.ts:660` | Yes (`config.models`) | No change — already done Phase 1 |
| `cli/commands/doctor/profile.ts:268` | Yes (`config?.models`) | No change — already done Phase 1 |
| `cli/platform/built-in-presets.ts:150` | N/A — module-load integrity assert, no user config in scope | No change needed |

---

## T19 — SECURITY.md

**Created**: `/Users/gracefullight/workspace/oh-my-agent/SECURITY.md`

Content:
- Vulnerability reporting pointer
- `vendors:` / `models:` blocks execute arbitrary binaries — treat config as code
- Don't commit secrets into `oma-config.yaml`
- Review config before running `oma` against untrusted projects
- `.backup-pre-008-*` retention guidance

---

## Acceptance criteria checklist

- [x] All config-load errors include file:line:col
- [x] All getModelSpec callers pass user models from in-scope config (Phase 1 + verified)
- [x] SECURITY.md at repo root with configuration trust section
- [x] `bun run --cwd cli build` passes
