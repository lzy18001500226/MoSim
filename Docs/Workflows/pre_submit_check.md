# Pre-Submit Check

> Active checklist for task closeout and competition-package review. Detailed
> artifact procedures are archived at `Docs/Cache/pre_submit_detail.md` and
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
Final packaging requires the explicit human approval and acceptance packet described in `Docs/Cache/pre_submit_detail.md`.
