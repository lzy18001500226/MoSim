# Smoke Test Workflow

> Purpose: quickly verify that a controller/model/scenario can run without major failures.

---

## 1. Recommended Smoke Tests

```text
hover_3s_pid
hover_3s_improved_pid
hover_3s_nmpc_indi
figure8_short_pid
figure8_short_nmpc_indi_l1
wind_short_nmpc_indi_l1
```

---

## 2. Pass Conditions

```text
simulation finishes
result file exists
time exists
x/y/z exist
no NaN values
z remains non-negative
motor commands are not all zero
position error is finite
```

---

## 3. Fail Conditions

```text
simulation crashes
model check fails
result file missing
NaN in state variables
altitude negative
motor commands all zero
position error infinite
```

---

## 4. Recommended Duration

```text
3 to 5 seconds
```

Do not use long scenes for smoke tests.

---

## 5. Output

Save:

```text
results/raw/smoke_{scene}_{controller}.csv
results/metrics/smoke_{scene}_{controller}.json
```
