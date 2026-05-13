# Add Controller Workflow

> Purpose: add a new controller without breaking baseline models or result pipelines.

---

## 1. Goal

Add a controller module such as:

```text
improved_pid
pid_indi
nmpc_indi
nmpc_indi_l1
nmpc_indi_l1_safe
```

---

## 2. Required Interface

Controller input:

```text
time
dt
state
reference
params
disturbance_estimate
```

Controller output:

```text
thrust
attitude_ref
torque
motor_cmd
debug
```

---

## 3. Procedure

1. Create controller folder under `controllers/`.
2. Define parameters in a config file.
3. Implement the control step.
4. Add logging/debug outputs.
5. Integrate into Sysblock/Sysplorer model.
6. Run controller interface test.
7. Run hover smoke test.
8. Run figure8 short test.
9. Compare with PID baseline.
10. Update documentation.

For Sysblock controllers, follow `workflows/build_sysblock_graphical_controller.md`.
Do not treat hand-written `.mo` files as verified graphical models unless the
latest file has passed the graphical gates and Sysplorer MCP `load_file/check_model`.
If a new block diagram is needed, create or repair it through MWORKS.Sysblock
GUI/API so generated binding metadata and internal configuration are present.

For graphical Sysblock controllers, also run the project contract check:

```bash
python3 scripts/check_sysblock_graphics.py
python3 scripts/check_graphical_sysblock_mcp.py
```

The graphical controller is not only a screenshot artifact. Accept it as a
simulation counterpart only when both gates pass:

```text
structure_ok = true
behavior_equivalence_ok = true
```

`structure_ok` requires ports, block placements, `connect(...)` statements, and
visible `annotation(Line(...))` connections. `behavior_equivalence_ok` requires
the diagram to expose the expected time and nonlinear behavior, including
Saturation, DeadZone, UnitDelay or DiscreteTimeIntegrator, Switch/state-machine
logic, and Product/allocation blocks where the controller design uses them.
After both static gates pass, run real MCP `load_file/check_model/simulate_model`.

Project rule:

```text
Every reported Sysblock simulation needs a corresponding graphical Sysblock
model. Equation-form Sysblock files may be used as temporary full-plant
integration bridges only when the current mixed Sysplorer/Sysblock compiler
blocks graphical embedding; they do not remove the requirement to maintain the
behavior-equivalent graphical controller.
```

---

## 4. Required Tests

```text
controller interface test
hover 3s smoke test
figure8 short smoke test
metric calculation test
```

---

## 5. Required Documentation

Document:

```text
controller structure
input/output interface
main parameters
tuning rules
known limitations
comparison results
```

---

## 6. Safety Rules

1. Preserve official PID baseline.
2. Do not overwrite baseline model.
3. Add saturation and limit checks.
4. Log controller debug variables.
5. If controller fails, provide fallback mode.
6. If `check_model` fails because of license, variable/equation count, or
   missing Sysblock metadata, record the failure log and mark the scenario as
   pending instead of using old or offline results.
7. Existing successful evidence logs must not be overwritten by failed reruns;
   write failed rerun logs to a separate `.running` or diagnostic file.
