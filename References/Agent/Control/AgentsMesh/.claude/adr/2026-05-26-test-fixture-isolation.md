# ADR: Test fixture isolation — `e2e-echo` mock agent out of production

**Date**: 2026-05-26
**Status**: Accepted
**Context**: Audit found that the `e2e-echo` mock agent (used by Playwright + MCP e2e to spin up real Pods without burning LLM credits) was leaking into production through four code paths.

## Problem

`e2e-echo` is a fixture — there is no scenario where a real user should see it in the agent picker, install credentials for it, or launch a Pod against it. Before this ADR, it leaked into production through:

| Layer | Mechanism | Symptom |
|---|---|---|
| Backend migration | `backend/migrations/000127*.up.sql` + 5 successors, `//go:embed *.sql` into the prod binary, `migrate up` applies them unconditionally | Row `agents.slug='e2e-echo'` lands in every DB the binary touches |
| Backend service | `ListBuiltinActive` returned every `is_builtin=true AND is_active=true` row | Front-end agent picker shows e2e-echo to all org members |
| Web bundle | `clients/web/src/components/settings/AgentCredentialsSettings/credentialForms/index.ts` unconditionally imported the e2e-echo form spec | Production webpack bundle ships test-only UI |
| Runner binary | None — `mockagent` is a separate `go_binary` not imported by `runner/cmd/runner`, not in `release_assets` | (already physically isolated) |

The original migration comment (`000127_add_e2e_echo_agent.up.sql`) self-flagged this as TODO: "Frontends … can filter … by `is_internal` once that column is added". This ADR closes that TODO across all four layers in one coordinated change.

## Decision

**Move test fixtures out of the migration pipeline. Treat migrations as schema-only; treat seed scripts as environment-scoped data.**

Concretely:

1. **Migration ≠ Seed.** Test data leaves `backend/migrations/` and lives in `deploy/dev/seed/`. The legacy 6 migrations (`000127`, `000150` – `000154`) keep their version numbers but their `*.up.sql` / `*.down.sql` bodies become single-line stubs (so the `schema_migrations` table on existing DBs stays consistent). A new migration `000155_remove_e2e_echo_from_prod` does a one-shot `DELETE FROM agents WHERE slug='e2e-echo'` to clean any DB that already applied the legacy migrations.

2. **Defense-in-depth via `is_internal` column.** Migration `000156_agents_is_internal` adds `agents.is_internal BOOLEAN NOT NULL DEFAULT false`. The seed marks e2e-echo as `is_internal = true`. `ListBuiltinActive` (the user-facing endpoint) filters `is_internal = false` by default; the runner discovery path (`mcpListRunners` → `ListBuiltinAgentsAll`) always sees the full list because the runner has to launch test pods on dev/e2e backends. Dev / e2e environments flip the user-facing filter back on by exporting `AGENTSMESH_INCLUDE_INTERNAL_AGENTS=true` before booting the backend — `deploy/dev/lib/host_services.sh::start_backend_host` sets it unconditionally. Production never sets the flag, so the test agent stays invisible in the UI even if the seed accidentally runs there.

3. **Front-end build-time gate.** The e2e-echo credential form is registered behind `if (process.env.NEXT_PUBLIC_E2E === "true")` via `require()`. Next.js DefinePlugin inlines the env variable; in production builds `NEXT_PUBLIC_E2E` is the empty string `""`, so webpack dead-code-eliminates both the `if` branch and the `require` call. The form module never enters the prod bundle.

4. **Lint guard against future imports.** ESLint's `no-restricted-imports` blocks any direct `import "./e2e-echo"` from production source paths. The conditional `require` inside `credentialForms/index.ts` is the single sanctioned entry point.

5. **Runner stays as-is.** `runner/internal/agents/mockagent/cmd/e2e-mock-agent/` is already a separate `go_binary` excluded from `release_assets` — no changes needed. If an agentfile says `EXECUTABLE e2e-mock-agent` on a host without the binary on PATH, the runner returns a clear `exec: "e2e-mock-agent": executable file not found in $PATH` error rather than silently failing.

## Consequences

### Positive
- Production DBs no longer carry test fixtures; the `agents` table reflects only real, user-facing options.
- Production web bundle stops shipping test-only UI surfaces (~1 KB form spec, plus future test forms gated the same way).
- `migrations/` directory becomes a clean schema-only contract; new contributors can read it as "what does production look like" without grepping for `e2e-` prefixes.
- The `is_internal` column generalizes — future internal-only agents (e.g. benchmark fixtures, support-debug shims) reuse the same flag.

### Negative / Trade-offs
- **Empty migration stubs are visually noisy.** Six files with single-line bodies live forever. We accept this over the alternative (deleting them and breaking `schema_migrations` ordering on staging DBs).
- **Seed has to live near the dev tooling.** `deploy/dev/seed/e2e_echo.sql` is invoked by `deploy/dev/lib/bootstrap.sh::init_seed`, not by the backend binary itself. CI environments that bypass `dev.sh` must invoke the seed explicitly. We could revisit this by adding `agentsmesh-backend seed e2e` if the friction adds up.
- **Conditional `require()` inside a TS file** is unidiomatic — but it's the only Next.js-supported pattern for build-time dead-code elimination that doesn't require webpack config changes. ESLint rule + ADR pointer document the why.

## Verification

- `bazel test //backend/...` — green; new migration 000155 + 000156 pass migration tests.
- `bazel build //clients/web:image` — extracted image tar contains no `e2e-echo` literal (grep over `.js` chunks).
- `bazel test //clients/web/e2e-playwright:e2e --test_arg=tests/scenarios/env-bundle-end-to-end.spec.ts` — green; dev/e2e build still ships e2e-echo form (via the `NEXT_PUBLIC_E2E=true` lifecycle.sh export).
- `bazel test //clients/web/e2e-playwright:e2e --test_arg=tests/cascade/` — green; `runner-delete-loop-ref-guard.spec.ts` and others that create loops referencing `agentSlug: "e2e-echo"` still work because the seed populates the row.

## Related
- Plan: `/Users/stone/.claude/plans/goofy-doodling-zebra.md`
- Prior ADR: `2026-05-24-service-binding-matrix.md` — establishes the runner crate is already partitioned by use case; the e2e-mock-agent binary fits that taxonomy.
