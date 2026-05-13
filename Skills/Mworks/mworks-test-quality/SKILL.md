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
| MWORKS model change | `check_model` + shortest useful targeted simulation |
| graphical Sysblock controller | `scripts/check_sysblock_graphics.py` + targeted MCP `check_model` |
| report claim | raw result + metrics + figure/replay evidence |

## Review Checklist

1. Paths stay inside the project.
2. Interfaces match `Design/02_模型接口与运行流程.md`.
3. Evidence labels distinguish `MWORKS_MCP`, `MWORKS_GUI`, and `offline_script`.
4. Metrics can be reproduced from raw data.
5. Failed simulations remain visible.
6. No secret, token, credential, or accidental large temporary output is staged.
7. Existing baseline evidence is not silently overwritten.

## Floating-Point Rules

Use tolerances for numeric checks. Prefer deterministic fixtures and seeded random generators.

## Git Rule

Stage only files relevant to the current task. If the worktree has unrelated changes, ignore them unless they affect the task.
