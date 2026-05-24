# Error Repair Playbook

Use this file whenever a pipeline gate fails or a graphical/modeling result is physically implausible.

## Repair Loop

1. Name the failed step: source, requirement, mapping, parameter, construction, check, translate, simulate, result verification, diagram review, or delivery.
2. Capture the concrete symptom: MCP error, failed variable lookup, NaN/divergence, zero flow, reversed motion, missing temperature response, missing wire, invisible instance, red dashed endpoint, or stretched symbol.
3. Classify the fault.
4. Identify the shortest active failure chain.
5. Apply the smallest meaningful repair.
6. Return to the failed step and rerun its gate.
7. Continue only after the gate passes or a real blocker is documented.

## Fault Classes

| Class | Typical Signal | First Repair Target |
|---|---|---|
| Source/input | Missing model path, ambiguous system target, no success criteria | Return to requirement extraction and mark `to confirm`. |
| Library/dependency | Class missing, wrong TY family, missing medium package | Load or switch to the correct TY system and medium libraries. |
| Component mapping | Wrong component family, system task built from component-design library | Remap through `references/component-map.md`. |
| Medium | Oil/gas package missing or incompatible | Select `TYOilMedia` or `TYGasMedia` and propagate medium consistently. |
| Topology | Unconnected ports, wrong P/T/A/B, missing return or exhaust | Repair the topology table and then `connect(...)`. |
| Capacitor/resistive topology | Direct resistive-resistive or capacitive-capacitive fluid connection, wrong `UseVolume*` side, unsupported nested check item | Apply `references/capacitor-resistive-check.md`, then rerun check/translate/simulate. |
| Parameter | Missing source, illegal value, unit mismatch, wrong initial condition | Repair only the active parameter blocker and record assumptions. |
| Initialization | Conflicting starts, impossible initial state | Relax or align initial states with physical boundaries. |
| Translation | Equation/variable mismatch, unsupported component combination | Remove the smallest incompatible combination or set required switches. |
| Simulation | NaN, divergence, tiny steps, no motion, pressure explosion | Check boundaries, relief/exhaust path, stiffness, input timing, and load direction. |
| Result variable | Target variable missing or wrong path | Query component ports/result info and adjust variable names. |
| Graphical annotation | Invisible instance, missing wires, red dashed lines, stretched symbols | Repair `Placement`, `Line`, `Diagram`, connector anchors, and extents. |

## Domain-Specific Shortcuts

- No motion: check medium, source, return/exhaust, valve state, then load direction.
- Zero flow under commanded actuation: check real `connect(...)`, valve opening state, boundary pressure/flow, and source drive.
- High pressure: check blocked return/exhaust, missing relief path, wrong valve port semantics, and load direction.
- Capacitor-resistive check failure: add or enable one needed volume/capacitive element between resistive elements, insert resistance between capacitive elements, or repair nested subsystem topology.
- Reversed displacement: check actuator chamber connections, load sign, and command polarity.
- No thermal response: check `TYThermalHydraulics`, heat boundary, `useHeatPort`, and temperature variables.
- Pneumatic instability: check gas source, exhaust boundary, `TYGasMedia`, chamber volume, and valve state.
- Diagram not visible: check `Placement` first, then `Diagram`, then export/review.
- Diagram has components but no wires: check whether plain `connect(...)` equations lack `annotation(Line(points=...))`, then repair route points and rerun diagram review.

## Repair Output

For each repair iteration, keep internal notes with:

- failed step
- symptom
- fault class
- root-cause hypothesis
- repair action
- rerun result

Only include these details in the final response when they are useful to the user or when a blocker remains.
