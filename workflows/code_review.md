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
5. Figures are saved under `docs/figures/` or `results/{group}/{scene}/figures/`.
6. Metrics are saved under `results/metrics/`.
7. No unnecessary absolute paths are introduced.
8. MCP workflows are followed.
9. Model changes are backed up.
10. Scripts have clear input/output.
11. Report claims are backed by data.
12. Non-original code is marked.

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

Review output should include:

```text
Summary
Blocking issues
Warnings
Suggested fixes
Tests to run
Files that need documentation updates
```

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
