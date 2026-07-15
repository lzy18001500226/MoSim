# Fuzzy

Status: BACKLOG.

Layer: usually augmentation or gain scheduling; only a direct fuzzy controller
becomes a nominal controller after a separate design decision.

Replaces: no default control loop in first stage.

Inputs: error, error derivative, controller gains or scheduling variables,
rule base, membership functions, dt.

Outputs: adjusted gains, compensation term or bounded control residual.

PX4 dependency: depends on the host controller; first use should augment PID or
SMC rather than bypass PX4 inner loops.

MWORKS/codegen route: fuzzy rule table -> generated code feasibility check ->
bounded-output wrapper.

Gazebo/Sunray validation: compare against the same base controller with and
without fuzzy scheduling.

Current gate: research/backlog after base controller evidence exists.

Forbidden claims: fuzzy compensation cannot be counted as a new accepted
controller unless it has an isolated profile and A/B metrics.
