# Architecture Recommendation — Backend Stack Manifest Unification

**Date**: 2026-04-23
**Decision type**: Recommendation (structural SSOT)
**Owner**: repo maintainer
**Status**: Proposed

## Problem

`cli/commands/verify/verify.ts` hardcodes Python-only checks (`py_compile`, `uv run pytest`, f-string SQL grep) even though `oma-backend` supports three variants (python, node, rust). The check `checkSqlInjection` was silently broken for 5 years (fixed in PR #265).

Stack declarations live in `.agents/skills/oma-backend/variants/{lang}/tech-stack.md` as prose, which is unusable as an executable contract. `oma-backend/SKILL.md:72` already declares a `stack/stack.yaml` slot that was never filled.

## Constraints

- Direct-to-main development (no PR review gate) — blast radius must be minimized.
- `oma update` migration logic in `cli/bin/cli.js:1351` already assumes a `stack.yaml` with a `language` field exists in consumer repos. New schema must be backward-compatible.
- Frontend/mobile skills use a different layout (single `resources/tech-stack.md`, no variants) — transforming them is out of scope.

## Options Considered

| Option | Scope | Blast radius | SSOT coherence | Fit for direct-main |
|--------|-------|--------------|----------------|---------------------|
| A — Backend variants gain `stack.yaml`, keep `tech-stack.md` | S | S | partial (roles split) | yes |
| B — A + remove `tech-stack.md` + update PM/workflow/shared refs | M | M | asymmetric (backend yaml, frontend/mobile md) | marginal |
| C — Migrate frontend and mobile to variants layout + `stack.yaml` | XL | XL | full | no |

## Why B is rejected

B looks like a moderate middle ground but produces the worst long-term state: backend becomes yaml-driven while frontend and mobile remain markdown-driven. Cross-skill references like `oma-pm/resources/error-playbook.md` become half-valid. The half-migrated state tends to calcify as permanent tech debt.

## Why C is rejected

Full unification is orthogonal to the immediate pain (verify CLI). Frontend and mobile do not have variant directories at all, so C is a structural transformation rather than a format change. Running this direct to main with no PR review is high risk.

## Recommendation: Option A with explicit role contract

`stack.yaml` and `tech-stack.md` coexist with distinct roles:

| File | Role | Consumer |
|------|------|----------|
| `stack.yaml` | SSOT, structured, executable contract | `oma verify`, agent structured lookup |
| `tech-stack.md` | Narrative, human-readable reference | developer reference |

This is the `package.json` + `README.md` pattern — coexistence is not duplication when roles differ.

## Scope

In scope:
- Add `stack.yaml` to `variants/{python,node,rust}/`
- Refactor `cli/commands/verify/verify.ts` to dispatch from `stack.yaml::verify`
- Add variant fixture tests under `cli/__tests__/verify/`
- Update `oma-backend/SKILL.md:67-73` to document the role split

Out of scope (follow-up tickets):
- Frontend and mobile migration to variants layout
- Removal of `tech-stack.md`
- `stack-set.md` workflow update
- `oma-pm/error-playbook.md` path corrections
- YAML-to-MD render tooling

## Risks

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | YAML and MD drift over time | Later: CI check or render script (non-goal now) |
| R2 | New YAML schema conflicts with `oma update`'s `language: <lang>` output | Schema includes `language` as required root field |
| R3 | Missing `stack.yaml` breaks existing consumers | `verify.ts` gracefully skips when file absent |

## Validation Steps

1. New `stack.yaml` files validate against JSON Schema.
2. `bun run test` for `cli/__tests__/verify/` covers all three variants with pass and fail fixtures.
3. Running `oma verify backend` against a sample Python project still detects the f-string SQL pattern (regression guard for PR #265's fix).
4. Running `oma verify backend` against a sample Node project runs `tsc --noEmit` and Prisma raw-query grep.
5. Running `oma verify backend` against a sample Rust project runs `cargo check` and SQLx raw-query grep.

## Hand-off

Next step is implementation via `/plan` or direct execution. The task list already captures the sequence (TaskList #1-#8).
