# Skill Review Checklist (Deep)

Use this when the user asks for a *comprehensive* audit or when the skill will be widely deployed.

## A) Inventory & Structure

- [ ] Skill root contains `SKILL.md`.
- [ ] YAML frontmatter has only `name` and `description`.
- [ ] `scripts/`, `references/`, `assets/` are used appropriately (not everything dumped in SKILL.md).
- [ ] No unexpected binaries or opaque blobs.
- [ ] Large files are justified and navigable (TOC, selective load guidance).

## B) Trigger & Discoverability

- [ ] Description includes concrete trigger phrases / symptoms.
- [ ] Description avoids being so broad it triggers everywhere.
- [ ] “When NOT to use” guidance exists (or is recommended).
- [ ] Collision analysis: overlap with adjacent skills and likely prompt ambiguity.

## C) Behavioral Contract

- [ ] Clear inputs required from user.
- [ ] Clear outputs/deliverables (files, formats, artifacts).
- [ ] Preconditions and assumptions explicitly stated.
- [ ] Degree-of-freedom is appropriate (guardrails where fragile).
- [ ] “Verification” steps exist (tests, lint, dry-run).

## D) Bundled Scripts (If Any)

- [ ] Scripts are readable, small, and do one thing well.
- [ ] Defensive flags: `set -euo pipefail` (bash), timeouts, safe temp dirs.
- [ ] No hidden network calls unless explicitly required.
- [ ] No destructive defaults; destructive ops require explicit confirmation.
- [ ] Output is deterministic and parseable when helpful.

## E) Tool/Command Usage

- [ ] All commands are shown with safe defaults.
- [ ] Any required credentials are referenced safely (env vars, secret stores; no copy/paste tokens).
- [ ] Paths are parameterized; avoids writing into global/system dirs by default.
- [ ] “Dry-run” or “preview” exists where possible.

## F) Network & External Content

- [ ] Any browsing/fetching content is treated as untrusted.
- [ ] Prompt-injection mitigations exist (summarize → extract facts → decide; don’t execute copied commands blindly).
- [ ] External deps are pinned where possible; registries are trusted.

## G) Security / Privacy / Safety

- [ ] Data classification guidance exists (what can/can’t be shared).
- [ ] Redaction guidance exists for logs and config.
- [ ] Clear boundaries: what the agent may execute vs must ask before doing.
- [ ] Supply chain provenance is captured or recommended.

## H) Correctness & Examples

- [ ] Examples are internally consistent (imports, ids, API usage).
- [ ] Edge cases are acknowledged.
- [ ] “Common mistakes” section exists or is recommended.
- [ ] If guidance is time-sensitive, it includes dates or version constraints.

## I) Maintainability

- [ ] Minimal duplication between SKILL.md and references.
- [ ] Keywords for search are present in description and headings.
- [ ] Update process is suggested (how to evolve the skill safely).

