# Run Tests Workflow

> Purpose: run project tests after code, model, scenario, or script changes.

---

## 1. Test Categories

```text
configuration tests
script unit tests
controller interface tests
smoke tests
regression tests
pre-submit tests
```

---

## 2. Configuration Test

Run:

```bash
python scripts/qa_check.py
```

Checks:

```text
required directories
required documents
wrapper scripts
MCP config presence
```

---

## 3. Script Tests

Currently implemented script test:

```text
scripts/qa_check.py
python3 tests/test_metrics.py
python3 tests/test_summary.py
```

Optional script tests when Julia/Syslab is available:

```text
scripts/calc_metrics.jl --self-test
scripts/plot_results.jl tests/fixtures/sample_tracking.csv results/samples/tracking_metrics/figures
```

Use small sample files if available.

---

## 4. Controller Interface Tests

Verify:

```text
input schema
output schema
debug fields
saturation behavior
```

---

## 5. Smoke Tests

Run:

```text
hover_3s_pid
hover_3s_optimized
figure8_short
wind_short
```

---

## 6. Regression Tests

Compare against previous valid metrics.

Default rule:

```text
RMSE must not worsen by more than 20% unless documented.
```

---

## 7. Output

Save test results to:

```text
results/{group}/{scene}/logs/
```
