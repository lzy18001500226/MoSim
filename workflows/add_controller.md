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
