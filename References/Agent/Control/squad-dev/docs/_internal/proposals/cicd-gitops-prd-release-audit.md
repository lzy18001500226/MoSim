# Release & GitOps Audit — CI/CD PRD Input

**Author:** Trejo (Release Manager)
**Date:** 2026-03-07
**Purpose:** Comprehensive audit of release and GitOps state to inform CI/CD improvement PRD
**Related:** Drucker is auditing CI/CD pipelines separately

---

## Executive Summary

The GitOps and release infrastructure is **fragile and inconsistent**, with multiple critical gaps exposed by the v0.8.22 disaster. The current state has:

- ✅ **Working:** Manual release process with comprehensive runbook, automated npm publish workflow with retry logic, main branch protection
- 🟡 **Fragile:** Version management on dev branch, branch naming inconsistencies (insider vs insiders), multiple overlapping workflows, bump-build.mjs still runs during `npm ci` despite CI=true check
- ❌ **Missing:** Automated semver validation, pre-publish checklists in CI, dev branch protection, tag verification gates, preview branch (referenced in workflows but doesn't exist)

**Priority recommendation:** P0 fixes for semver validation and bump-build suppression, P1 for branch hygiene and workflow consolidation.

---

## 1. Branching Model Audit

### Current State

**Three-branch model (documented):**
- `dev` — Primary development branch (all PRs target dev)
- `insiders` — Early-access channel (auto-synced from dev)
- `main` — Stable releases (merged from dev, tagged)

**Actual branches found:**
```
dev                 ✅ Active, 5 commits ahead of main
main                ✅ Active, 5 commits ahead of dev (post-v0.8.22 docs)
insiders            ✅ Active, last commit 3 days ago (v0.8.20 era)
insider             ⚠️ Stale, 5 days old, incompatible with workflows
feature/squad-streams  ⚠️ Feature branch, status unknown
Multiple squad/* branches (local and remote) ⚠️ Stale issue branches
```

**Branch protection:**
- `main`: ✅ Protected (requires 1 approval, "Squad Main Guard" status check, conversation resolution)
- `dev`: ❌ **NOT PROTECTED** (404 from GitHub API)

### Pain Points

1. **dev branch unprotected** — Anyone can force-push or commit directly to dev, bypassing PR review and CI checks
2. **Branch naming inconsistency** — Both `insider` and `insiders` exist; workflows reference `insider`, but active development uses `insiders`
3. **Stale branches accumulating** — Multiple merged squad/* branches not cleaned up (squad/195, squad/223, squad/228, etc.)
4. **Divergent histories** — main has 5 commits not in dev (post-release documentation), dev has 5 commits not in main (unreleased work)
5. **No preview branch** — `squad-promote.yml` and `squad-preview.yml` reference a `preview` branch that doesn't exist; unclear if this is planned or abandoned architecture

### Proposed Improvements

**P0 — Protect dev branch:**
- Enable branch protection on `dev` with same rules as `main` (1 approval, status checks, conversation resolution)
- Rationale: dev is the integration branch — direct commits bypass code review and introduce risk

**P1 — Resolve insider/insiders naming:**
- Audit usage: workflows use `insider`, team uses `insiders`
- Choose one canonical name (recommend `insiders` to match npm dist-tag convention)
- Delete the unused branch and update all workflow references
- Rationale: Naming inconsistency causes confusion and potential workflow failures

**P1 — Preview branch decision:**
- **Option A:** Implement preview branch as documented in squad-promote.yml (dev → preview → main gate with forbidden path stripping)
- **Option B:** Remove preview branch references from workflows if not part of the release model
- Rationale: Workflows reference a branch that doesn't exist; this is either incomplete implementation or dead code

**P2 — Stale branch cleanup:**
- Automate stale branch deletion after PR merge (GitHub Action or bot)
- Manual cleanup of current stale branches: `squad/195`, `squad/223`, `squad/228`, `squad/237`, `pr-189`, `feature/squad-streams`
- Rationale: Reduces clutter, prevents accidental rebasing onto wrong branches

**P2 — Divergent history resolution:**
- Establish policy: main should NEVER have commits not in dev (main is a subset of dev history)
- Current divergence is documentation-only (v0.8.22 retro artifacts) — safe to merge main → dev to reunify
- Future: Enforce via branch protection (main can only receive merges from dev, no direct commits)

---

## 2. Version State Audit

### Current State

**main branch (v0.8.22 — last stable release):**
```
package.json                          → "0.8.22"
packages/squad-sdk/package.json       → "0.8.22"
packages/squad-cli/package.json       → "0.8.22"
```

**dev branch (v0.8.23-preview.1 — next development cycle):**
```
package.json                          → "0.8.23-preview.1"
packages/squad-sdk/package.json       → "0.8.23-preview.1"
packages/squad-cli/package.json       → "0.8.23-preview.1"
```

**npm registry (live):**
```
@bradygaster/squad-sdk@latest         → 0.8.22  ✅
@bradygaster/squad-cli@latest         → 0.8.22  ✅

Dist-tags:
  SDK: latest: 0.8.22, preview: 0.8.17-preview, insider: 0.6.0-alpha.0
  CLI: latest: 0.8.22, preview: 0.8.17-preview, insider: 0.6.0-alpha.0
```

### Assessment

✅ **main branch versions are correct** — All 3 package.json files show 0.8.22, matching the git tag and GitHub Release
✅ **dev branch versions are correct** — Post-release bump to 0.8.23-preview.1 was executed per runbook
✅ **npm registry matches main** — Both packages show 0.8.22 as `latest` dist-tag
⚠️ **Stale dist-tags** — `preview` still points to 0.8.17-preview (pre-disaster), `insider` points to 0.6.0-alpha.0 (ancient)

### Pain Points

1. **No automated version sync validation** — Nothing verifies that all 3 package.json files have matching versions before release
2. **Stale dist-tags confuse users** — `preview` tag hasn't been updated since 0.8.17, users trying preview builds get old versions
3. **No version bump enforcement** — Post-release dev bump is manual (checklist item), but not enforced or automated

### Proposed Improvements

**P0 — Pre-release version consistency check:**
- Add CI job that runs before tag creation: verify all 3 package.json versions match
- Fail the release workflow if versions diverge
- Rationale: Version mismatch was a failure mode in v0.8.22 incident (fixed manually but not systematically)

**P1 — Automate post-release dev bump:**
- After successful release, bot automatically opens PR to bump dev to next preview version
- Or: squad-release.yml dispatches a workflow that updates dev branch directly (requires force-push or admin bypass)
- Rationale: Reduces manual steps, ensures dev never forgets to bump version

**P1 — Dist-tag hygiene:**
- Define dist-tag update policy:
  - `latest` → updated on stable release (currently working)
  - `preview` → updated when dev branch publishes to npm (if we implement dev → npm publishing)
  - `insider` → updated when insiders branch publishes (if we implement insiders → npm publishing)
- Audit and deprecate stale preview/insider versions if channels are abandoned
- Rationale: Stale dist-tags mislead users; either keep them fresh or remove them

**P2 — Semver validation in CI:**
- Add CI job that validates version format with `semver.valid()` on every commit to main/dev
- Fail CI if version is not valid semver (prevents 4-part versions from being committed)
- Rationale: v0.8.22 disaster root cause — 4-part version (0.8.21.4) was committed without validation

---

## 3. Tag Hygiene Audit

### Current State

**Total tags:** 33 (v0.1.0 → v0.8.22)

**Tag patterns:**
- Standard releases: `v0.8.22`, `v0.8.21`, `v0.8.20`, etc. ✅
- Insider builds: `v0.4.0-insider+57cdae2`, `v0.6.0-alpha.0-insider+222b219` ✅
- Preview builds: `v0.8.6.15-preview-insider+5664fd0` ⚠️ (4-part version, invalid semver)
- Invalid tag: `v0.8.2` (should be `v0.8.20` based on release history)

**Tag → Commit mapping:**
```
v0.8.22  → 05573c7 (main branch, correct)
v0.8.21  → bf86a32 (main branch, correct)
v0.8.20  → 96e9056 (insiders branch, correct)
```

### Pain Points

1. **Invalid semver tag exists** — `v0.8.6.15-preview-insider+5664fd0` is a 4-part version (pre-#692 fix); npm would mangle this
2. **Ambiguous tag v0.8.2** — Could be typo for v0.8.20, or an abandoned version; no corresponding GitHub Release
3. **No tag validation gate** — Nothing prevents pushing invalid semver tags (e.g., v0.8.21.4 from the v0.8.22 disaster was tagged before being caught)

### Proposed Improvements

**P0 — Semver tag validation:**
- Add pre-push hook or CI check: validate tag format before allowing push
- Only allow `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-prerelease` (no 4-part versions)
- Rationale: Invalid tags break npm publish; v0.8.22 disaster had invalid tag v0.8.21.4

**P1 — Tag audit and cleanup:**
- Delete invalid tag `v0.8.6.15-preview-insider+5664fd0` (4-part version, pre-#692 fix)
- Clarify or delete ambiguous tag `v0.8.2` (no release notes, unclear purpose)
- Document tag naming conventions in CONTRIBUTING.md
- Rationale: Stale/invalid tags pollute the release history and confuse users

**P2 — Tag → Release linking validation:**
- CI job: verify every tag has a corresponding GitHub Release
- Or: Enforce that GitHub Releases create tags (not manual git tag push)
- Rationale: Tags without releases are invisible to users relying on GitHub UI

---

## 4. GitHub Releases Audit

### Current State

**Last 10 releases:**
```
v0.8.22  ✅ Published 22 minutes ago (Latest)
v0.8.21  ✅ Published 32 minutes ago
v0.8.20  ✅ Published 3 days ago
v0.8.19  ✅ Published 3 days ago
v0.8.18  ✅ Published 3 days ago
v0.5.4   ✅ Published 7 days ago
v0.5.3   ✅ Published 8 days ago
v0.5.2-insider+234b2a6  ⚠️ Pre-release (insider build)
v0.5.2   ✅ Published 15 days ago
v0.5.1   ⚠️ Pre-release (Ralph Local Watchdog)
```

**Release workflow:**
- `squad-release.yml` triggers on push to `main`, creates tag + GitHub Release automatically
- `publish.yml` triggers on `release: published` event, publishes to npm
- Manual fallback: `gh workflow run publish.yml -f version=X.Y.Z`

### Assessment

✅ **No draft releases** — All releases are published (v0.8.22 disaster lesson learned)
✅ **Automated release creation** — squad-release.yml handles tag + release creation on main push
✅ **Pre-release tags work** — Insider builds correctly marked as pre-release
⚠️ **Release notes quality** — v0.8.22 uses `--generate-notes` (auto-generated), not manually curated

### Pain Points

1. **No release readiness gate** — squad-release.yml creates releases on ANY push to main, even if version wasn't bumped or CHANGELOG wasn't updated
   - **Wait, there IS a gate:** squad-release.yml line 28 checks that version exists in CHANGELOG.md before releasing — BUT this failed on the last 3 runs (see logs: test failures, not CHANGELOG failures)
2. **Test failures block releases** — squad-release.yml runs tests before release, but tests are currently failing (8/8 fail due to ESM `require()` misuse)
3. **CHANGELOG validation gate broken** — Currently checking for `## [VERSION]` in CHANGELOG.md, but test failures happen first so this gate never runs
4. **No rollback automation** — If a release is botched, manual rollback procedure required (see `.squad/skills/release-process/SKILL.md`)

### Proposed Improvements

**P0 — Fix failing tests:**
- 8 test files use `require('node:test')` in ESM context (should be `import`)
- Tests block all releases to main — must fix immediately
- Rationale: Broken tests mean no releases can ship, even emergency hotfixes

**P0 — Separate test gate from release gate:**
- Move tests to a separate required status check ("Squad Tests")
- squad-release.yml should only validate version/CHANGELOG/tag state, not run tests
- Rationale: Test failures shouldn't block release automation if tests are already green on dev (redundant check)

**P1 — Tag existence check:**
- squad-release.yml line 43-51 checks if tag exists and skips release if it does ✅
- BUT: This doesn't prevent accidentally pushing main without bumping version (tag won't exist, but version is stale)
- Add check: fail if package.json version already published to npm (prevents re-releasing same version)
- Rationale: Prevents accidental re-release of same version (idempotency gate)

**P2 — Manual release notes curation:**
- Replace `--generate-notes` with manual release notes from CHANGELOG.md
- Extract the `## [VERSION]` section from CHANGELOG.md and use as release body
- Rationale: Auto-generated notes are low-quality; CHANGELOG.md is already curated

**P2 — Automated rollback procedure:**
- Add `gh workflow run rollback.yml -f version=X.Y.Z` that:
  1. Deprecates npm packages with message
  2. Deletes GitHub Release
  3. Deletes git tag
  4. Opens PR to revert version bump on main
- Rationale: Rollback is currently 9 manual steps (see SKILL.md); automation reduces MTTR

---

## 5. Release Process Gaps (Post-Kobayashi)

### Kobayashi's Failures (v0.8.22 Disaster)

**Full retrospective:** `.squad/decisions/inbox/keaton-v0822-retrospective.md`

**What went wrong:**
1. ❌ Invalid semver (0.8.21.4 — 4-part version) committed without validation → npm mangled to 0.8.2-1.4
2. ❌ Draft release created (doesn't trigger `release: published` event) → publish.yml never ran
3. ❌ Wrong NPM_TOKEN type (User token with 2FA) → CI failed with EOTP errors 5+ times
4. ❌ bump-build.mjs ran 4 times during debugging → mutated version from 0.8.21 → 0.8.21.4
5. ❌ No retry logic in verify steps → npm propagation delay caused false 404 failures

**What was fixed:**
- ✅ Comprehensive release runbook created (`.squad/skills/release-process/SKILL.md`)
- ✅ Retry logic added to verify steps in publish.yml (5 attempts, 15s interval)
- ✅ Trejo (Release Manager) and Drucker (CI/CD Engineer) created to replace Kobayashi (separation of concerns)
- ✅ Draft release mistake documented and prevented via `--draft=false` in runbook
- ✅ NPM_TOKEN type verification step added to runbook

**What's still missing (automation gaps):**
- ❌ **No automated semver validation** — Nothing stops 4-part versions from being committed
- ❌ **No pre-publish checklist enforcement** — NPM_TOKEN type, branch state, tag state all manual checks
- ❌ **No tag verification before release creation** — squad-release.yml checks tag existence but not tag format validity
- ❌ **bump-build.mjs still runs** — Even with `CI=true` check, it ran during `npm ci` in this audit (produced 0.8.22.1)
- ❌ **No rollback procedure automation** — Rollback is 9 manual steps per SKILL.md

### Proposed Improvements

**P0 — Automated semver validation:**
- Pre-commit hook: validate package.json versions with `semver.valid()` before allowing commit
- CI job on dev/main: fail if any package.json version is invalid semver
- squad-release.yml: fail if tag doesn't match `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-prerelease` format
- Rationale: Root cause of v0.8.22 disaster; must be prevented at multiple layers

**P0 — Fix bump-build.mjs suppression:**
- Current check: `process.env.CI === 'true'` OR `process.env.SKIP_BUILD_BUMP === '1'`
- Problem: `CI=true` is set but bump-build.mjs still ran during this audit (saw "Build 1: 0.8.22 → 0.8.22.1" in npm ci output)
- **Root cause investigation needed:** Why did CI check fail? Is `process.env.CI` not set during npm prepare script?
- Fix: Test actual CI environment variables in squad-ci.yml and squad-release.yml, adjust check accordingly
- Rationale: bump-build.mjs creating 4-part versions was a failure mode in v0.8.22

**P1 — Pre-publish checklist CI job:**
- Add `pre-release-checks.yml` workflow that validates:
  1. All 3 package.json versions match
  2. Version is valid semver (semver.valid() check)
  3. Version exists in CHANGELOG.md with release notes
  4. Tag doesn't already exist (git ls-remote)
  5. Version not already published to npm (npm view)
- Make this a required status check on main branch
- Rationale: Automates manual checklist from SKILL.md, prevents human error

**P1 — NPM_TOKEN type validation in CI:**
- Can't check token type without npm CLI authenticated, but can add a smoke test:
  - Run `npm whoami` in publish.yml before publish attempt
  - If it requires OTP, fail with error message: "NPM_TOKEN is a User token (requires 2FA). Create an Automation token instead."
- Rationale: Wrong token type caused 5 failed publish attempts in v0.8.22

**P2 — Rollback automation workflow:**
- Create `rollback.yml` workflow (workflow_dispatch):
  - Inputs: version to roll back
  - Steps: deprecate npm packages, delete GitHub Release, delete tag, open revert PR
  - Manual trigger only (no automatic rollback)
- Rationale: Reduces MTTR from 6+ hours (v0.8.22) to minutes

---

## 6. package-lock.json State

### Current State

**Tested:** `npm ci` on main branch
**Result:** ⚠️ **Works but triggers bump-build.mjs**

**Output:**
```
npm ci
npm warn deprecated glob@10.5.0
> @bradygaster/squad@0.8.22 prepare
> npm run build

> @bradygaster/squad@0.8.22 prebuild
> node scripts/bump-build.mjs

Build 1: 0.8.22 → 0.8.22.1  ⚠️ VERSION MUTATED
```

**Files modified after npm ci:**
- package.json (version 0.8.22 → 0.8.22.1)
- packages/squad-sdk/package.json (version 0.8.22 → 0.8.22.1)
- packages/squad-cli/package.json (version 0.8.22 → 0.8.22.1)

### Assessment

⚠️ **package-lock.json is valid** — npm ci succeeds, dependencies install
❌ **npm ci is NOT idempotent** — Mutates package.json versions via prebuild script
❌ **CI=true check ineffective** — bump-build.mjs ran despite `CI=true` being set (npm scripts run in CI environment)

### Pain Points

1. **npm ci triggers version mutation** — `prebuild` script runs `bump-build.mjs`, which increments build number
2. **CI environment variable not respected** — bump-build.mjs checks `process.env.CI === 'true'`, but this isn't preventing execution
3. **Developers can't run npm ci without modifying files** — Fresh clone + npm ci = dirty working tree

### Proposed Improvements

**P0 — Fix bump-build.mjs CI detection:**
- **Hypothesis:** `process.env.CI` is not set during npm lifecycle scripts (prepare, prebuild)
- **Test:** Add debug logging to bump-build.mjs: `console.log('CI env:', process.env.CI, 'NODE_ENV:', process.env.NODE_ENV)`
- **Fix options:**
  1. Check `process.env.NODE_ENV === 'production'` (set in publish.yml during release builds)
  2. Check `process.env.GITHUB_ACTIONS === 'true'` (GitHub-specific)
  3. Move bump-build.mjs out of `prebuild` script, call it explicitly in dev builds only (not in `prepare` lifecycle)
- Rationale: Version mutation during CI is a critical reliability issue (caused v0.8.22 disaster)

**P1 — Separate dev build from release build:**
- Create two npm scripts:
  - `npm run build:dev` — runs bump-build.mjs, then esbuild (for local development)
  - `npm run build:release` — skips bump-build.mjs, runs esbuild only (for CI/CD and releases)
- Update squad-ci.yml and publish.yml to use `build:release`
- Rationale: Explicit separation eliminates ambiguity about when versions should increment

**P2 — Document prebuild behavior:**
- Add comment to package.json `prebuild` script explaining bump-build.mjs behavior
- Add section to CONTRIBUTING.md: "Why does npm ci modify package.json?"
- Rationale: Reduces confusion for new contributors

---

## 7. Workflow Audit

### Current State

**14 active workflows found:**
```
publish.yml                       ✅ Publishes to npm on GitHub Release
squad-release.yml                 ⚠️ Creates releases on main push (currently blocked by test failures)
squad-insider-release.yml         ✅ Creates insider releases on insider branch push
squad-insider-publish.yml         ⚠️ Publishes insider builds (unclear if this runs)
squad-publish.yml                 ⚠️ Duplicate of publish.yml? (same ID 241445655)
squad-promote.yml                 ⚠️ References preview branch (doesn't exist)
squad-preview.yml                 ⚠️ Validates preview branch (doesn't exist)
squad-ci.yml                      ✅ Runs tests on PRs and dev/insider pushes
squad-docs.yml                    ✅ Builds/deploys docs
squad-heartbeat.yml               ✅ Ralph monitoring
squad-issue-assign.yml            ✅ Auto-assigns issues
squad-label-enforce.yml           ✅ Enforces label conventions
squad-triage.yml                  ✅ PR/issue triage automation
sync-squad-labels.yml             ✅ Syncs labels across repos
```

**Overlapping workflows:**
- `publish.yml` (ID 241445653) — Active, triggers on `release: published`
- `squad-publish.yml` (ID 241445655) — Active, same workflow? Possible duplicate or renamed file
- `.github/workflows/squad-publish.yml.deprecated` — Deprecated file exists, suggests rename happened

### Pain Points

1. **Duplicate/renamed workflows** — publish.yml and squad-publish.yml may be duplicates (same workflow ID suggests rename)
2. **Dead workflows** — squad-promote.yml and squad-preview.yml reference a `preview` branch that doesn't exist
3. **Unclear insider publish flow** — squad-insider-release.yml creates GitHub Releases, but does squad-insider-publish.yml publish to npm? If so, to which dist-tag?
4. **No workflow documentation** — No README or diagram showing which workflows run when and their dependencies

### Proposed Improvements

**P1 — Audit and deduplicate workflows:**
- Confirm whether `publish.yml` and `squad-publish.yml` are duplicates
- If duplicate, delete one and update references
- Check `.deprecated` file history to understand what changed
- Rationale: Duplicate workflows waste CI resources and cause confusion

**P1 — Preview branch decision (revisited):**
- **If preview branch is planned:** Create the branch, document the dev → preview → main flow
- **If preview branch is abandoned:** Delete squad-promote.yml and squad-preview.yml
- Rationale: Workflows referencing non-existent branches are dead code

**P1 — Document workflow architecture:**
- Create `.github/workflows/README.md` with:
  - Workflow dependency graph (which workflows trigger which)
  - Branch → workflow mapping (what runs on push to each branch)
  - Release flow diagram (dev → insiders, dev → main → npm)
- Rationale: Onboarding and troubleshooting require understanding the automation flow

**P2 — Insider publish flow clarification:**
- Document: Does squad-insider-publish.yml run? If so, when and to which npm dist-tag?
- If insider builds should publish to npm `@insider` tag, ensure workflow is wired correctly
- If insider builds are GitHub Release-only (no npm), delete squad-insider-publish.yml
- Rationale: Unclear publish flow leads to stale dist-tags (insider tag still points to 0.6.0-alpha.0)

---

## 8. Branch Protection Rules

### Current State

**main branch protection:**
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Squad Main Guard"]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "required_approving_review_count": 1
  },
  "required_conversation_resolution": true,
  "enforce_admins": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

**dev branch protection:**
```
404 Branch not protected
```

### Assessment

✅ **main is protected** — Requires 1 approval, status checks, conversation resolution
❌ **dev is NOT protected** — Direct commits and force pushes allowed
⚠️ **Admin bypass enabled** — `enforce_admins: false` means admins can bypass all rules

### Pain Points

1. **dev branch unprotected** — Primary integration branch has no protections; direct commits bypass review
2. **Admin bypass risk** — Admins can force-push to main, breaking release history
3. **No commit signing required** — Commits can be spoofed
4. **No CODEOWNERS enforcement** — No automatic reviewer assignment for critical paths

### Proposed Improvements

**P0 — Protect dev branch:**
- Apply same protection rules as main:
  - Require 1 approval for PRs
  - Require "Squad CI" status check (tests must pass)
  - Require conversation resolution
  - Disable force pushes and deletions
- Rationale: dev is the integration branch; unprotected dev = unreviewed code in main

**P1 — Enforce admin rules:**
- Enable `enforce_admins: true` on both main and dev
- Rationale: Even admins should follow the process (emergency bypass via GitHub UI if needed)

**P2 — Add additional status checks:**
- main: Require "Squad Tests" + "Squad Main Guard" (currently only Main Guard)
- dev: Require "Squad CI" (tests)
- Rationale: Redundant test runs catch flaky tests and ensure green before merge

**P2 — Require commit signing:**
- Enable `required_signatures: true` on main and dev
- Rationale: Prevents commit spoofing (security best practice)

**P2 — Add CODEOWNERS:**
- Create `.github/CODEOWNERS` with:
  - `.squad/` → @bradygaster (team structure is product owner domain)
  - `.github/workflows/` → Drucker (CI/CD engineer, but this is fictional — map to Brady)
  - `packages/*/package.json` → Trejo (release manager — version changes require review)
- Rationale: Auto-assign reviewers for critical paths

---

## Summary & Priorities

### P0 (Ship Blockers — Fix Immediately)
1. **Fix failing tests** — 8 tests fail due to ESM `require()` misuse; blocks all releases
2. **Protect dev branch** — Unprotected primary integration branch is a risk
3. **Fix bump-build.mjs suppression** — CI check ineffective; versions mutate during npm ci
4. **Automated semver validation** — Pre-commit hook + CI check to prevent 4-part versions

### P1 (Fragile Foundations — Fix Soon)
1. **Resolve insider/insiders naming** — Workflows inconsistent with branch name
2. **Preview branch decision** — Either implement or delete dead workflows
3. **Pre-publish checklist CI job** — Automate manual checklist from SKILL.md
4. **Dist-tag hygiene** — Stale preview/insider tags mislead users
5. **Branch protection on dev** — Same rules as main
6. **Workflow deduplication** — Audit publish.yml vs squad-publish.yml overlap

### P2 (Technical Debt — Address Later)
1. **Stale branch cleanup** — Automate or manual cleanup of merged branches
2. **Tag audit and cleanup** — Delete invalid semver tags
3. **Rollback automation** — Reduce MTTR with automated rollback workflow
4. **Workflow documentation** — Architecture diagram and flow README
5. **CODEOWNERS file** — Auto-assign reviewers for critical paths
6. **Commit signing** — Require GPG/SSH signatures on protected branches

---

## Next Steps

**For Brady:**
- Review priorities and confirm P0/P1 scope
- Decide on preview branch architecture (implement or remove)
- Decide on insider/insiders naming (workflows vs branch)

**For Drucker (CI/CD Engineer):**
- Fix failing tests (ESM require → import)
- Implement pre-publish checklist CI job
- Fix bump-build.mjs CI detection
- Add semver validation to squad-ci.yml and squad-release.yml

**For Trejo (Release Manager):**
- Execute stale tag cleanup (delete v0.8.6.15-preview-insider+5664fd0, clarify v0.8.2)
- Document branch protection requirements for dev
- Update release runbook with CI automation references

---

**End of Audit**
