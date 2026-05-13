# Build Sysblock Graphical Controller Workflow

> Purpose: create or repair a graphical Sysblock controller that is useful for review and matches the simulated controller behavior.

## 1. Inputs

Required:

```text
controller_id
graphical model name
equation/reference model name
input ports
output ports
target scenario or model-check case
expected behavior elements
```

Expected behavior elements include limiters, filters, delays, switches, fault-estimation paths, allocation paths, and debug outputs that affect simulation.

## 2. Modeling Rule

Use official Sysplorer/Sysblock APIs for topology. Prefer:

```text
call_code(mode="run_script")
ModelingPy.NewModel(name, "Sysblock")
ModelingPy.OpenModel(name)
ModelingPy.AddComponent(type, model, name, x, y)
ModelingPy.ConnectPort(model, src_port, dst_port)
ModelingPy.SetModelParamValue(model, block, param, value)
```

Do not rely on hand-written `.mo` text as the primary way to create Sysblock topology. Text edits are acceptable only for small generated-metadata repair followed by `check_model`.

## 3. Build Sequence

1. Resolve the controller interface and replacement location.
2. Query concrete library blocks and ports when uncertain.
3. Build the smallest runnable graphical chain.
4. Add behavior blocks: saturation, filtering, delay/discrete state, switch/mode logic, products, allocation, and debug outputs.
5. Wire all visible paths with `ConnectPort`.
6. Run static graphical checks.
7. Run Sysplorer MCP `load_file/check_model`.
8. Run targeted simulation only after structure is correct.
9. Compare behavior against the equation/reference model or scenario metrics.
10. Save evidence under `results/model_checks/` or the relevant scenario result folder.

## 4. Required Gates

```bash
python3 scripts/check_sysblock_graphics.py
python3 scripts/check_graphical_sysblock_mcp.py
```

For targeted work, a narrower MCP check is acceptable if it records:

```text
model file
model name
check_model result
simulate_model result when used
log path
behavior-equivalence conclusion
```

## 5. Acceptance

Accept the graphical controller only when:

1. The user can open it and see meaningful topology and wires.
2. Child blocks are not empty wrapper shells.
3. `structure_ok=true`.
4. `behavior_equivalence_ok=true` or the remaining gap is explicitly marked.
5. The related simulation claim clearly states whether it uses graphical full-plant simulation or equation-bridge simulation.

## 6. Failure Policy

If Sysplorer/Sysblock rejects mixed graphical embedding, do not claim the graphical controller is useless. Keep:

```text
graphical controller = design/review/time-behavior artifact
equation bridge = temporary full-plant integration artifact
```

Both must be tracked until the platform limitation is resolved.
