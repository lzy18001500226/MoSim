# Code Review Workflow

> Purpose: automatically review project changes for correctness, reproducibility, and report readiness.

---

## 1. Review Scope

Review changes in:

```text
controllers/
planners/
scenarios/
scripts/
QuadrotorModel/
docs/
workflows/
tests/
```

---

## 2. Checklist

Check:

1. Directory structure is respected.
2. Controller interfaces remain compatible.
3. Scenario config fields are complete.
4. Results are saved under `results/`.
5. Figures are saved under `docs/figures/` or `results/{group}/{scene}/{experiment}/figures/`.
6. Metrics are saved under `results/{group}/{scene}/{experiment}/metrics/`.
7. No unnecessary absolute paths are introduced.
8. MCP workflows are followed.
9. Model changes are backed up.
10. Scripts have clear input/output.
11. Report claims are backed by data.
12. Non-original code is marked.

## 2.1 Delivery Level

Use delivery level to size the review and required checks:

| Level | Scope | Minimum Review |
|---|---|---|
| L0 | Docs/index only | Link/path sanity and diff check |
| L1 | Small script/workflow fix | Focused static check or script compile |
| L2 | New controller, scenario, or evidence workflow | Task contract, tests, docs, evidence bundle |
| L3 | High-risk model/runtime/Git/import change | Rollback plan, failure-path test, artifact/secret/large-file gate |

Do not apply an L0 review to an L3 import or simulation-runtime change.

---

## 3. Common Problems

| Problem | Fix |
|---|---|
| Hard-coded user path | Use config variable |
| Missing result file | Re-run simulation |
| Missing metrics | Run calc_metrics |
| Missing figure | Run plot workflow |
| Unclear controller interface | Update controller docs |
| Broken baseline | Restore PID baseline |
| Unsupported claim | Remove claim or add experiment |

---

## 4. Output Format

Review output should be PR-style and evidence-first. Findings lead the review,
ordered by severity. Each finding should identify the file/line or artifact
that proves the risk.

```text
Scope analyzed
Blocking findings
Warnings
Missing tests or missing simulation evidence
File/line or artifact evidence
Smallest recommended fix
Residual risk
Documentation updates needed
```

Do not replace a review with a summary. If no issues are found, say that
clearly and still state the remaining test/evidence gap.

---

## 5. Pass Criteria

Pass if:

```text
no blocking interface break
baseline preserved
required outputs exist
metrics and figures align
documentation updated
```
