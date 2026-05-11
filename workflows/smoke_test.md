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
results/smoke/{scene}/{controller}/raw/smoke_{scene}_{controller}.csv
results/smoke/{scene}/{controller}/metrics/smoke_{scene}_{controller}.json
```

## 6. Real Sysplorer MCP Smoke

Use this project script to prove that the official model can be loaded,
checked, simulated, and read through Sysplorer MCP:

```bash
python3 scripts/run_mworks_scenario.py scenarios/smoke/example1_pid_mcp_smoke.yaml
```

Expected outputs:

```text
results/smoke/example1_mcp/pid_baseline_smoke/logs/sysplorer_example1_pid_mcp_smoke_20260509.jsonl
results/smoke/example1_mcp/pid_baseline_smoke/raw/mworks_mcp_example1_pid_smoke.csv
results/smoke/example1_mcp/pid_baseline_smoke/metrics/mworks_mcp_example1_pid_smoke.json
results/smoke/example1_mcp/pid_baseline_smoke/metrics/mworks_mcp_example1_pid_smoke.csv
results/smoke/example1_mcp/pid_baseline_smoke/figures/
results/smoke/example1_mcp/pid_baseline_smoke/replay/mworks_mcp_example1_pid_smoke.json
results/smoke/example1_mcp/pid_baseline_smoke/replay_html/mworks_mcp_example1_pid_smoke.html
```

This is real `source=MWORKS_MCP` smoke evidence, but it is still only a
0-1 s run. Do not copy it into `official_example*_pid_baseline` paths.
