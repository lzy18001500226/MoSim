---
name: mworks-test-quality
description: Create, run, and review project tests and quality gates for the MWORKS quadrotor project. Use when adding tests, running smoke/regression checks, reviewing code or model changes, validating scenarios/controllers/scripts, checking pre-submit readiness, or translating MATLAB testing/code-review skills to Python/Julia/MWORKS workflows.
---

# MWORKS Test Quality

Use tests and review to protect the reproducible simulation loop.

## Primary Workflows

```text
workflows/code_review.md
workflows/run_tests.md
workflows/regression_test.md
workflows/build_sysblock_graphical_controller.md
workflows/pre_submit_check.md
scripts/qa_check.py
```

## Test Strategy

| Change | Minimum Check |
|---|---|
| docs/index/workflow only | `git diff --check`, link/path sanity |
| Python script | `python3 -m py_compile`, relevant pytest |
| scenario/controller config | `python3 scripts/qa_check.py` |
| metrics logic | unit tests + known raw CSV regression |
| MWORKS department task | activation sentinel/background screenshot gate first; static file-only work records `live_mworks_touched=false` and `mworks_window_evidence_touched=true` |
| MWORKS model change | activation sentinel/background screenshot gate + phase screenshots after load/check and simulate/plot/animation + `check_model` + shortest useful targeted simulation |
| graphical Sysblock controller | activation sentinel/background screenshot gate + phase screenshots during/after layout review + missing-wire/layout inspection + `scripts/check_sysblock_graphics.py` + targeted MCP `check_model` |
| report claim | raw result + metrics + figure/replay evidence |

## Review Checklist

1. Paths stay inside the project.
2. Interfaces match `Design/02_模型接口与运行流程.md`.
3. Evidence labels distinguish `MWORKS_MCP`, `MWORKS_GUI`, and `offline_script`.
4. Metrics can be reproduced from raw data.
5. Failed simulations remain visible.
6. No secret, token, credential, or accidental large temporary output is staged.
7. Existing baseline evidence is not silently overwritten.
8. MWORKS department task and return/blocker packets pass `Scripts/quality/check_mworks_live_gate.py --expect department`; static-only department work explicitly states both `live_mworks_touched=false` and `mworks_window_evidence_touched=true`.
9. MWORKS department packets do not only return screenshot paths. They must show that the department read the sentinel JSON/capture manifest or inspected screenshot/window-title metadata, wrote a concrete `activation_state_observation`, and classified `license_state`.
10. Any demo, login, activation, authorization, mixed, unavailable, unknown, or GUI-error-report `license_state` is returned as `status=blocked`, not accepted as a completed MWORKS task.
11. Any `live_mworks_touched=true` return includes `mworks_phase_screenshots` and `mworks_phase_observations`. R1 observations must cover the live simulation/control phases actually run; R2 observations must cover visible wiring/layout quality and wrong-window/license/error-dialog checks.
12. The activation sentinel is an all-window gate. Any relevant MWORKS/Sysplorer/Syslab window in demo, login/activation, authorization-failed, GUI-error, mixed, or visible unknown state blocks the whole MWORKS task; a clean education-mode window elsewhere does not override it. Hidden Qt/browser-proxy/helper windows with no license/error text are risk evidence, not standalone authorization-loss proof.
13. MWORKS model/simulation/layout tasks declare and produce real engineering outputs such as `.mo`/`package.mo`, `check_model`, `SimulateModel`, native result/`.msr`, metrics, diagram/layout screenshots, or wiring observations. JSON packets, ledgers, and progress notes are control-plane evidence only and do not count as completion unless the task is explicitly diagnostic/rule-sync/preflight-only.
14. Any activation/license/login/authorization/GUI-error blocker is treated as a P0 MWORKS infrastructure incident and PMO sends both sparse WeChat and sparse email alert. A task may not keep trying solver/model changes while that incident is open.

## Agent-Aware Quality Gate

For broad tasks, split quality work from implementation when it can run in
parallel. The quality/Git agent may own only:

```text
git status and diff review
large-file scan
secret-pattern scan
targeted tests or static checks
commit and push for explicit staged paths
```

Split by scale as well as by type. If a task includes many downloaded
repositories, many result folders, or many model families, use multiple
read-only mapper/research agents plus one Git/quality agent instead of one
oversized agent. Typical split:

```text
UE/rendering references
planning/trajectory references
perception/mapping references
skills/workflow references
Git/quality and large-file gate
```

The main agent stays responsible for merging conclusions into project-owned
rules and workflows. If a coordination mistake is found, update `AGENTS.md`,
`workflows/`, or this skill before continuing.

For broad workflow/tooling changes, maintain a capability coverage map:

```text
capability
  -> project rule or workflow doc
  -> script/tool/skill implementation
  -> example or evidence artifact
  -> test/check or manual review gate
```

Do not mark a workflow capability complete if it has only prose and no
repeatable check, evidence example, or manual review gate.

MWORKS live-dispatch quality gate:

```text
python Scripts/quality/check_mworks_live_gate.py <task_packet.json> --kind task --expect department
python Scripts/quality/check_mworks_live_gate.py <return_or_blocker.json> --kind return --expect department
```

Use `--expect live` only for non-department compatibility packets that truly
touch live MWORKS. For MWORKS R1/R2 department dispatches, use
`--expect department` even when the business slice is static file organization,
because the department must still return activation sentinel, background
screenshot, `activation_state_observation`, license state, no-click pledge,
window-evidence flag, and live-touch classification.

For non-department static-only MWORKS compatibility tasks:

```text
python Scripts/quality/check_mworks_live_gate.py <packet.json> --kind return --expect static
```

For external skill/workflow audits, check that the process followed the user's
requested cadence. If the user asked for `学习+更新文档三遍` or equivalent, the
quality review must find:

```text
Round 1 source slice + doc patch
Round 2 source slice + doc patch
Round 3 source slice + doc patch
changed paths summary
do-not-adopt guardrails
unresolved doc risks
```

Reject a one-shot audit that reads all sources first and patches once. The
evidence should point to local source paths, not external web pages or runtime
claims.

Use this consistency gate for orchestration documentation changes:

```text
event schema has terminal states and pending states
resume guidance reads ledger before chat memory
WAL/event locator comes from terminal run state or an explicit artifact ref
UI/SSE/GUI streams are review surfaces, not audit truth
capability coverage maps each adopted pattern to docs and a validation gate
do-not-adopt list blocks unrelated runtimes, UIs, providers, and credentials
stale ledger recovery says how to continue when an agent disappears
```

It must not edit controller/model/scene logic unless explicitly assigned a
narrow fix. Its return should include:

```text
scope checked
files staged
checks run
large-file/secret scan result
commit hash
push result or exact failure
residual risk
```

Do not stage whole downloaded reference repositories, external skill packs, or
RflySim/UE asset trees as a side effect of normal Git automation.

Exception: when the user explicitly asks to track a reference repository, the
Git/quality agent may stage that exact tree after checking:

```text
no file over 100 MB remains unignored
50-100 MB files are allowed only if the user has allowed them
no nested .git directories are staged
no tokens, private keys, or credentials are staged
generated build/runtime folders are ignored or intentionally excluded
```

## Floating-Point Rules

Use tolerances for numeric checks. Prefer deterministic fixtures and seeded random generators.

## Git Rule

Stage only files relevant to the current task. If the worktree has unrelated changes, ignore them unless they affect the task.
