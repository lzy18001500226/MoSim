# ADR: cli/ Refactor — Module Boundaries

- Status: Accepted (v3 — after prior-art review + user review)
- Date: 2026-04-20
- Scope: `cli/` (commander entry, commands, lib)
- Method: Design-Twice → Prior-Art Review → ADR

## Context

`cli/` has grown into a mixed-shape package that is hard to extend:

- `commands/` holds 15+ top-level handlers. Five files mix argument parsing, interactive Clack prompts, orchestration, FS/network I/O, and business logic in a single module:
  - `verify.ts` 562L, `bridge.ts` 488L, `install.ts` 454L, `update.ts` 452L, `doctor.ts` 394L
- `commands/auth.ts` owns per-vendor auth checks (`isClaudeAuthenticated`, `isGeminiAuthenticated`, `isCodexAuthenticated`, `isQwenAuthenticated`) which are consumed by `doctor.ts` and re-exported cross-command — a vendor adapter leaking into a command handler.
- `lib/` is a flat bag of ~30 modules mixing concerns:
  - Vendor adapters: `claude/settings.ts`, `gemini/settings.ts`, plus vendor switches in `vendor-adapter.ts` and `runtime-dispatch.ts`.
  - Domain composers: `agent-composer.ts`, `hooks-composer.ts`, `skills.ts`, `rules.ts`, `agent-config.ts`.
  - Infra: `git.ts`, `github.ts`, `http.ts`, `tarball.ts`, `manifest.ts`, `self-update.ts`, `serena.ts`, `memory.ts`, `workspaces.ts`, `process-signals.ts`.
  - Presentation helpers: `cli-framework.ts`, `graph.ts`, `frontmatter.ts`, `time-window.ts`, `competitors.ts`.
  - Already-sliced subdirs (good): `lib/recap/`, `lib/retro/`; `commands/agent/`, `commands/search/`, `commands/migrations/`.
- Install and update duplicate the same bootstrap sequence (manifest → vendor settings → symlinks → competitor uninstall prompts → Serena project).
- `lib/skills.ts` re-exports `agent-composer`, `hooks-composer`, `vendor-adapter`, `constants/`, `utils/fs-utils` — a god barrel that hides dependencies and blocks tree-shaking.

Constraints:

1. No CLI surface change (`oma <cmd>` contracts frozen).
2. `.agents/` SSOT semantics unchanged.
3. Existing test suite (`bun run test`) must keep passing each phase.
4. Conventional Commits required; commitlint enforces types.
5. Runtime cost neutral (no extra bundle size beyond aliases).

Non-goals: new features, API changes, introducing a DI framework, replacing Commander or Clack, migrating to oclif.

Quality attributes in priority order:

1. Modifiability — add a vendor or command without touching unrelated modules.
2. Testability — business logic reachable without spawning processes or prompting.
3. Onboarding — new contributor locates code by convention other CLIs already use.
4. Runtime footprint — do not regress startup or bundle.

## Prior Art (what other CLIs actually do)

The first draft of this ADR borrowed the frontend "Feature-Sliced Design" label. That is **wrong for CLI** — FSD is a frontend convention and no major CLI uses it. A survey of large CLIs shows convergence on a different, simpler pattern:

| CLI | Framework | Command layout | Shared layout |
|-----|-----------|----------------|---------------|
| Nx (`packages/nx/src/`) | yargs | `command-line/<cmd>/{command-object.ts, <cmd>.ts, utils/, <subfeature>/}` | sibling dirs: `config/`, `daemon/`, `tasks-runner/`, `project-graph/`, `utils/` |
| Vercel CLI (`packages/cli/src/`) | internal | `commands/<cmd>/` | flat `util/` with command-specific subfolders mixed in — acknowledged anti-pattern |
| Supabase CLI (Go, `github.com/supabase/cli`) | cobra | `cmd/` (one file per command) | `internal/<area>/` (Go idiom) |
| Heroku / Salesforce CLI | **oclif** | class-based `src/commands/<topic>/<sub>.ts`, plugin system, lifecycle hooks | `oclif` core handles parsing/help/completion |
| Liran Tal's `nodejs-cli-apps-best-practices` | — | `src/commands/` | `src/services/`, `src/utils/`, `src/configs/` |

Consistent signal across these: **one folder per command** (or tight command group) at the top, with **shared capabilities as sibling top-level folders**, not nested under a catch-all `shared/` or `lib/`. Nx is the closest analogue to our situation (TypeScript, many commands, command-owned subfeatures, non-class-based framework).

Sources reviewed:

- https://github.com/nrwl/nx/tree/master/packages/nx/src/command-line — command slices (`release/`, `migrate/`, `generate/`, etc.)
- https://github.com/vercel/vercel/tree/main/packages/cli/src — `commands/` + heavy `util/`
- https://github.com/supabase/cli — Go `cmd/` + `internal/`
- https://oclif.io — Heroku/Salesforce framework
- https://github.com/lirantal/nodejs-cli-apps-best-practices — Liran Tal's community list
- https://blog.logrocket.com/node-js-project-architecture-best-practices/ — LogRocket Node architecture guide (2026)
- https://betterstack.com/community/guides/scaling-nodejs/commander-explained/ — Better Stack Commander guide

## Options

### Option A — Classic Layered (commands → services → domain/adapters → infra)

```
cli/
  cli.ts
  commands/<cmd>/{index,prompts}.ts      # parse args, UI only
  services/<cmd>.service.ts              # business flow
  domain/{agents,skills,hooks,rules,manifest,frontmatter}/
  adapters/
    vendors/{claude,gemini,codex,qwen,antigravity}/{auth,settings,dispatch}.ts
    github/  serena/  tarball/  mcp-bridge/  fs/
  infra/{cli-framework,process-signals,http,time-window}.ts
  utils/
```

Pros: mirrors `.agents/rules/backend.md` (router → service → repository), pure `domain/` trivially testable.

Cons: most "services" are command-specific — pairing every command with a matching `services/<cmd>.service.ts` creates ghost abstractions and breaks colocation; four top-level layers for a CLI with ~15 commands; diverges from CLI prior art.

### Option B — Command-Slice (Nx-style; our recommendation)

```
cli/
  bin/
  cli.ts                                 # composition root (Commander wiring)
  commands/
    install/   {command.ts, install.ts, ui.ts, internal/}
    update/    {command.ts, update.ts, ui.ts, internal/}
    verify/    {command.ts, verify.ts, ui.ts, internal/}
    doctor/    {command.ts, doctor.ts, ui.ts}
    bridge/    {command.ts, bridge.ts, internal/}
    agent/     {command.ts, spawn.ts, parallel.ts, status.ts, review.ts, common.ts}
    search/    (already slice-shaped; keep)
    retro/ recap/ memory/ auth-status/ star/ stats/ cleanup/ export/ link/ visualize/
  vendors/                                # sibling, not nested under shared/
    claude/{auth,settings}.ts
    gemini/{auth,settings}.ts
    codex/{auth}.ts
    qwen/{auth}.ts
    antigravity/…
    index.ts                              # Vendor registry + types
  platform/                               # SSOT installer (was scattered across lib/)
    agent-composer.ts
    hooks-composer.ts
    rules.ts
    skills-installer.ts
    vendor-adapter.ts
    manifest.ts
  io/                                     # external I/O adapters
    github.ts
    tarball.ts
    serena.ts
    mcp-bridge.ts                         # extracted from commands/bridge.ts
    http.ts
    git.ts
  cli-kit/                                # framework/presentation wrappers
    cli-framework.ts
    clack.ts / picocolors.ts wrappers
    process-signals.ts
    time-window.ts
    frontmatter.ts
  types/   constants/   utils/
  dashboard/                              # stays (web + terminal dashboards)
  scripts/                                # generate-manifest, install.sh, etc.
```

Per-slice convention (borrowed from Nx `command-object.ts`):

- `command.ts` — Commander registration + argument parsing. No logic.
- `<cmd>.ts` — business flow. No Clack, no `process.exit`, no direct argv access.
- `ui.ts` (optional) — Clack/picocolors interactive prompts only.
- `internal/` — slice-private helpers not exported outside the folder.

Rules:

1. `commands/<x>` must not import from `commands/<y>`. Shared code moves to `vendors/`, `platform/`, `io/`, or `cli-kit/`.
2. `vendors/<vendor>/` owns everything vendor-specific; other packages iterate via the `Vendor` registry.
3. `platform/` is the only package that writes vendor files from `.agents/` SSOT.
4. `lib/skills.ts` god-barrel is deleted; callers import from the real module.
5. Tests colocate with the unit under test.

Pros:

- Matches Nx's large-CLI layout (closest analogue in TS ecosystem).
- Colocation: one command = one folder; deleting a command means deleting one directory.
- `service.ts`-style pure flow file exists per command (as `<cmd>.ts`) without inventing a parallel `services/` tier — keeps `.agents/rules/backend.md` spirit (no business logic in route handlers) while avoiding ghost abstractions.
- Sibling shared folders (`vendors/`, `platform/`, `io/`, `cli-kit/`) keep names short and discoverable — no `shared/shared/x/y/z.ts` deep paths.
- Lint boundary (`no-restricted-imports`) prevents cross-slice coupling.

Cons:

- `platform/` still concentrates SSOT-installer complexity — may need its own follow-up ADR.
- Contributors must internalize "shared logic goes in a sibling dir, not in another slice".
- Churn: ~80 files move.

### Option C — Migrate to oclif

Replace Commander + hand-rolled structure with oclif (class-per-command, plugin system, auto-docs, completion).

Pros: zero bikeshedding, scales to hundreds of commands, used by Salesforce/Heroku/Shopify.

Cons: huge rewrite; current `describe` JSON introspection, `addOutputOptions`, `resolveJsonMode`, and Clack-based prompts all break; oclif's plugin model solves problems we do not have (no third-party plugins planned); violates "no runtime change" constraint; Bun compatibility not a primary oclif target.

Rejected — disproportionate cost for a single-repo CLI.

## Decision

**Adopt Option B (Command-Slice, Nx-style).** Option A rejected as over-layered for this CLI size. Option C rejected as out of scope.

Rationale:

1. Nx is the closest TS-ecosystem analogue (many commands, command-private subfeatures, non-class framework) and its layout is proven at scale.
2. Sibling top-level shared folders (`vendors/`, `platform/`, `io/`, `cli-kit/`) are easier to navigate than a catch-all `shared/` or `lib/`.
3. The per-slice `{command.ts, <cmd>.ts, ui.ts}` split captures the router/service separation `.agents/rules/backend.md` asks for, without inventing a `services/` ghost tier.
4. Migration is incremental; each phase ships green without a big-bang rewrite.

## Migration Plan (phased; each phase is one PR)

Each phase must ship green: `bun run test`, `bun run lint`, `bun run build`. Commit type `refactor(cli): …`.

| Phase | Action | Scope | Risk |
|-------|--------|-------|------|
| 0 | Add single `tsconfig` path alias (`@cli/*` → `cli/*`), Biome cross-slice import rule forbidding `commands/<x>` ↔ `commands/<y>`, and a short `cli/ARCHITECTURE.md` pointing to this ADR. | tooling | none |
| 1 | Create `vendors/{claude,gemini,codex,qwen,antigravity}/`. Move `lib/claude/settings.ts`, `lib/gemini/settings.ts`, and `is*Authenticated` from `commands/auth.ts`. Export a `Vendor` registry from `vendors/index.ts`. | vendor adapters | low |
| 2 | Create `platform/`. Move `lib/{agent-composer, hooks-composer, rules, vendor-adapter, skills, agent-config, manifest}` into it; split `skills.ts` into `skills-installer.ts` + `constants-re-export`; drop barrel re-exports. | SSOT installer | medium |
| 3 | Create `io/` and `cli-kit/`. Move `lib/{github, tarball, serena, http, git, self-update}` into `io/`; extract MCP-HTTP bridge logic from `commands/bridge.ts` into `io/mcp-bridge.ts`. Move `lib/{cli-framework, process-signals, time-window, frontmatter, competitors, graph}` into `cli-kit/`. | infra | medium |
| 4 | Slice **all five** large commands into `commands/<install\|update\|verify\|doctor\|bridge>/{command.ts, <cmd>.ts, ui.ts}`. Each `<cmd>.ts` caps at ~250L and has zero Clack/picocolors imports. Ship one command per PR (5 PRs total); suggested order — lowest risk first: `doctor` → `verify` → `bridge` → `install` → `update`. | commands | highest; ship one command per PR |
| 5 | Move remaining light commands (`star`, `visualize`, `export`, `link`, `stats`, `cleanup`, `recap`, `retro`, `memory`, `agent`, `auth-status`) into `commands/<name>/` slices. `search/` already slice-shaped — rename if needed. Delete `lib/` once empty. | commands | low |
| 6 | Remove temporary path aliases if desired; verify `bun run build` emits same entrypoints; update `cli/README.md` and `cli/CLAUDE.md`. | cleanup | low |

Rollback: each phase is a single PR; revert if tests or downstream `oma` consumers break.

## Consequences

Positive:

- Adding a vendor is a single folder drop under `vendors/<new>/` plus one registry line.
- Adding a command is one folder under `commands/<new>/` with a 2-3 file skeleton.
- `install` and `update` stop duplicating bootstrap: both call the same functions in `platform/` and `vendors/*`.
- `<cmd>.ts` files are pure and trivially testable; Clack prompts no longer block unit tests.
- Sibling top-level shared folders avoid `shared/shared/x/y/z` nesting seen in some FSD-inspired repos.
- Lint boundary rule prevents cross-slice coupling regressing over time.
- Layout matches Nx — easier onboarding for contributors familiar with that ecosystem.

Negative / Risks:

- Phase 4 (large-command slicing) carries real regression risk. Mitigation: per-command PR, retain existing tests, add missing tests for install/update bootstrap flow before splitting.
- Churn: ~80 files move; reviewers should scan the ADR first.
- `platform/` still concentrates complexity; a follow-up ADR may split it further once usage stabilizes.
- Sibling folders at repo root increase top-level count (from 2 to 6-7 folders under `cli/`). Acceptable: mirrors Nx `src/` which has 20+.

## Validation

- `bun run test` keeps passing each phase.
- `bun run lint` — ESLint `no-restricted-imports` catches any `commands/<x>` → `commands/<y>` import.
- `bun run build` — emitted binary size deviates by less than 5%.
- Manual smoke: `oma doctor`, `oma install --help`, `oma update --ci`, `oma agent:spawn`, `oma bridge`.
- File-size guard: after Phase 4, no file in `commands/` exceeds 300 lines; no file in `platform/`, `vendors/`, `io/`, `cli-kit/` exceeds 400 lines. Add a CI check later if desired.

## Alternatives Considered (summary)

- **Status quo + targeted split of large files**: cheapest, but leaves vendor leakage and install/update duplication. Rejected — does not address root cause.
- **Option A (classic layered)**: cleaner textbook layering, but creates service ghosts for commands that have no meaningful business logic. Rejected in favor of Option B.
- **Option C (migrate to oclif)**: out of scope and violates "no runtime change" constraint. Rejected.
- **FSD-lite labeling (v1 draft of this ADR)**: FSD is a frontend convention; no CLI in the survey uses that name. Rejected to avoid misleading terminology — the chosen layout is a CLI command-slice pattern (Nx-style), not FSD.

## Follow-ups

- After Phase 4, revisit whether `platform/` needs its own ADR for internal boundaries.
- Evaluate moving `dashboard/` and `terminal-dashboard.ts` into `commands/dashboard/` in Phase 5.
- Consider tagging each `commands/<name>/` with an OWNERS or CODEOWNERS entry once the monorepo adopts it.
- Re-evaluate oclif in 1-2 years if plugin support or third-party CLI extensions become a requirement.
