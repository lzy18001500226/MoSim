# Regression Test Workflow

> Purpose: prevent accidental performance degradation.

---

## 1. Goal

Compare new metrics with previous accepted metrics.

---

## 2. Baseline Files

Store accepted metrics under:

```text
results/{group}/{scene}/{experiment}/metrics/baseline/
```

Example:

```text
results/{group}/{scene}/{experiment}/metrics/baseline/figure8_pid_baseline.json
results/{group}/{scene}/{experiment}/metrics/baseline/figure8_nmpc_indi_l1.json
```

---

## 3. Rules

Default rules:

```text
simulation must not fail
position_rmse must not worsen by more than 20%
max_position_error must not worsen by more than 20%
constraint_violation_count must not increase unexpectedly
saturation_ratio should not increase significantly
```

---

## 4. Output

Save regression report to:

```text
results/summaries/regression/regression_report.md
```

---

## 5. If Regression Fails

Do one of:

```text
fix the change
document why degradation is expected
update baseline only after manual approval
remove unsupported report claim
```
