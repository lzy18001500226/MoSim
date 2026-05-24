# Produce MWORKS Simulation Evidence

> Purpose: create a complete, labeled evidence bundle for a simulation or controller comparison.

## Use When

Use this workflow for:

```text
official example reproduction
controller comparison
disturbance/fault scenario validation
formation or planning scenario validation
report figure and metric generation
demo-video evidence preparation
```

## Inputs

```text
experiment_id
model_name
scenario YAML
controller config
stop_time
required variables
evidence source label
```

Valid source labels:

```text
source=MWORKS_MCP
source=MWORKS_GUI
```

Do not use `source=offline_script` for report evidence. Script-generated
reference data may be useful during design, but it must not enter the formal
simulation evidence bundle unless the official model is run through MWORKS.

## Procedure

1. Resolve model context with `workflows/resolve_model_context.md` if the target component or interface is unclear.
2. Run `check_model`.
3. Run the smallest simulation that validates the claim.
4. Read required variables through `result_manager`.
5. Export raw CSV under `results/{group}/{scene}/{experiment}/raw/`.
6. Compute metrics under `results/{group}/{scene}/{experiment}/metrics/` or `results/{group}/{scene}/{experiment}/logs/`.
7. Run `scripts/evaluate_result_quality.py <scenario> --write-metrics`.
8. Generate figures or replay assets under `results/{group}/{scene}/{experiment}/figures/`, `results/{group}/{scene}/{experiment}/replay/`, `results/{group}/{scene}/{experiment}/replay_html/`, or `docs/figures/`.
9. Update `docs/simulation_report.md` only when `quality_status=pass` or when the limitation is explicitly documented.

Project entrypoints:

```bash
# One scenario
python3 scripts/run_mworks_scenario.py scenarios/official/example1_pid_baseline.yaml

# Batch, without overwriting completed metrics
python3 scripts/run_mworks_batch.py --skip-existing scenarios/official/*.yaml

# Batch plan only, no MCP calls
python3 scripts/run_mworks_batch.py --dry-run scenarios/official/*.yaml
```

## Required Evidence Bundle

```text
scenario/config path
controller/config path
MCP log or manual run note
raw CSV path
metrics path
figure/replay path
source label
pass/fail summary
```

## Acceptance

Pass if:

1. Evidence source is explicitly labeled.
2. Raw result has `time` and key state/reference columns.
3. Metrics can be reproduced from the raw result.
4. `quality_status=pass` for full-performance claims.
5. `quality_status=smoke_only` is used only for automation-chain validation.
6. `quality_status=needs_iteration` is preserved as evidence but not treated as completed controller performance.
7. Claims in docs do not mix offline demo evidence with real MWORKS simulation evidence.
8. Git diff contains no large temporary result dumps.

`check_model ok` and `simulate_model ok` mean the run executed. They do not mean
the controller is good. If the quality gate reports `needs_iteration`, keep the
result, inspect the failed metric, retune or revise the controller, then rerun the
same scenario until the result passes or the limitation is documented.

## Failure Handling

| Failure | Action |
|---|---|
| result variable missing | inspect available variables and update `docs/index/variable_mapping.md` |
| simulation unstable | save as failed evidence and compare against baseline |
| MCP error | save JSONL/log output and reduce to smoke case |
| generated artifact too large | keep summary/metrics; ignore or relocate raw bulky output |
