# Skill Review Report (Self-Audit)

## 1) Snapshot

- Skill name: `skill-review-audit`
- Skill path: `agent/skills/skill-review-audit`
- Source/provenance: copied from local skill directory (`~/.claude/skills/skill-review-audit`) on 2026-01-31
- Files: 8 files total (`scripts/` + `references/` present; no `assets/`)
- Intended environment: any agent runner that can read Markdown; optional Bash for `scripts/scan_skill.sh` (uses `find`, `du`, `sort`, `head`, `sed`; `rg` is optional)

## 2) What It Does

- Primary purpose: provides a structured workflow and templates to audit an AI agent “skill” directory for scope, triggers, tools/side-effects, and risks.
- Supported tasks:
  - Inventory a skill directory (tree, file sizes, provenance hints)
  - Evaluate triggers (frontmatter)
  - Map commands/tooling and side effects
  - Assess security/privacy/safety/supply-chain risks
  - Produce a written report using a template
- Inputs it expects: a skill name/path, target agent environment + constraints, and intended usage context.
- Outputs it produces: a written audit report (template provided); optionally heuristic scan output from `scripts/scan_skill.sh`.
- Assumptions/dependencies: basic Markdown literacy; if using the script, a POSIX-ish shell + common CLI tools.

## 3) What It Does NOT Do (Or Should Not Be Used For)

- Explicit non-goals:
  - Does not automatically “fix” skills; it guides a review and can suggest changes.
  - Does not guarantee a skill is safe—only helps assess and document risks.
- Missing limitations (recommended additions):
  - Treat scan outputs as sensitive; avoid pasting unredacted logs/config publicly.

## 4) Trigger Audit (Frontmatter)

- Trigger quality notes: specific (“review / interpret / audit an AI agent skill”), with clear objects of interest (`SKILL.md`, scripts, references, assets).
- False positives: may trigger for generic “review my prompt/tooling” requests that are not about skills.
- False negatives: could miss requests phrased as “validate this skill before install” unless the runner’s trigger matcher keys off the description’s second clause.
- Recommended rewrite (if any): optional—add “validate before installing/deploying” earlier in the description for stronger matching.

## 5) Tooling & Side-Effects Map

| Action | Where in skill | Side effects | Permissions | Risk | Safer alternative |
|---|---|---|---|---|---|
| Run `scripts/scan_skill.sh <dir>` | `scripts/scan_skill.sh` | Reads files and prints matching lines/file names | FS read | Output may include sensitive strings if shared | Run on a sanitized copy; redact output before sharing |
| Preview provenance files (first 120 lines) | `scripts/scan_skill.sh` | Prints file contents | FS read | Accidental secrets disclosure | Manually inspect locally; avoid sharing previews |
| Read templates/taxonomies | `references/` | None | FS read | Low | N/A |

## 6) Risks (Security / Privacy / Safety / Supply Chain)

| Risk | Category | Severity | Likelihood | Evidence | Mitigation |
|---|---|---|---|---|---|
| Accidental disclosure when sharing scan output | Privacy & data handling | Medium | Possible | `scan_skill.sh` prints previews and heuristic matches | Warn users to redact; avoid printing secret-like matching lines (implemented) |
| Overconfidence in “audit” result | Safety & integrity | Low | Possible | Skill is a framework, not a validator | Encourage verification and uncertainty markers |

## 7) Quality Review

- Correctness issues: none found (script is read-only; workflow is internally consistent).
- Completeness gaps: could add a short “When NOT to use” / “Redaction” callout earlier (partially addressed via note).
- UX / clarity issues: README now includes a concrete usage example for the script.
- Maintainability issues: minimal; content is cleanly split into `references/`.

## 8) Recommendations (Prioritized)

1. P0: Keep “treat output as sensitive” warnings prominent (done in `SKILL.md` + README).
2. P1: Continue improving `scan_skill.sh` to minimize leaking secrets (done by printing only filenames for secret-like patterns).
3. P2: Consider adding an explicit “When NOT to use” section (e.g., when the target environment forbids reading local files or when outputs can’t be shared safely).

## 9) Suggested Skill Diffs (Optional)

- Proposed changes (high level): additional redaction guidance and safer scan defaults.
- Files to edit: `agent/skills/skill-review-audit/SKILL.md`, `agent/skills/skill-review-audit/scripts/scan_skill.sh`, `agent/skills/skill-review-audit/README.md`, `agent/skills/skill-review-audit/README.zh-CN.md`.
