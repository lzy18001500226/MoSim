# Pre-Submit Check

> Active checklist for task closeout and competition-package review. Detailed
> artifact procedures are archived at
> `Docs/Cache/workflow_history/release/pre_submit_detail.md` and
> are loaded only for a named final-package gate.

## 1. Goal
Close only claims with reproducible evidence and a publishable task slice; this checklist does not grant final acceptance.

## 2. Required Deliverables
For final submission, verify the required models, source, scenarios, results, metrics, figures, report, manual, video, and project entry documents in the archived detail reference.

## 3. MCP Check
For an MWORKS or Syslab claim, verify required MCP tools and stop for login, license, authorization, or unknown GUI blockers.

## 4. Directory Check
Keep artifacts in declared project paths and run the targeted quality checker; use `python Scripts/quality/qa_check.py` for package-level review.

### Per-Task Git Closeout Gate
- Inspect only task-owned tracked and untracked paths.
- Run targeted tests plus credential-like-content and large-file checks.
- Stage only reviewed paths, inspect the staged list, and run `git diff --cached --check`.
- Commit, push, and verify upstream synchronization before reporting completion.
- Unrelated dirty paths, reference imports, and generated backlogs do not waive this gate.
- Ignore only verified generated-cache classes or exact risks; do not use ignores to hide ordinary source, documents, scripts, configs, or small assets.
- Treat a Windows reparse link whose target is outside the repository as a publication blocker. Do not follow, replace, or forge it in the Git index.
- Treat repeated untracked directory segments such as `Scripts/X/Scripts/X/` as a path-cycle and ownership blocker. Do not commit, ignore, delete, or move the tree until its canonical source is identified.
- Treat an observed background `git diff` or `git ls-files` process with no `.git/index.lock` as read-only inventory, not an index writer. Before staging, committing, or pushing, block on an index lock or an observed Git writer command; preserve background readers and recheck the exact candidate paths after publication.
- Preserve third-party snapshot whitespace as evidence instead of rewriting it. A verified public-test-vector Gitleaks false positive may use only a path-and-pattern-scoped temporary allowlist.

## 5. Required Experiment Check
An experiment needs its declared source/configuration, completed run, fresh result, and owning-workflow evidence boundary.

## 6. Metrics Check
Metrics must be reproducible from named raw results and retain failed, blocked, and out-of-scope classifications.

## 7. Candidate Evidence Manifest Check
`Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json` is a `review_candidate_not_final_acceptance`, not final PMO acceptance.

## 8. Figure Check
Each report figure needs a traceable source result and truthful caption-level claim boundary.

## 9. Report Check
Do not promote static, offline, or review evidence into runtime or final-acceptance claims.

## 10. Video Check
Video is review evidence only and cannot replace run, metric, and evidence records.

## 11. Code Review Check
Run the applicable source, contract, and documentation checks before staging.

## 12. Final Pass Criteria
Final packaging requires the explicit human approval and acceptance packet described in `Docs/Cache/workflow_history/release/pre_submit_detail.md`.
