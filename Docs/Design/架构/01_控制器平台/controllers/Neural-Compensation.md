# Neural Compensation

Status: BACKLOG / research candidate.

Layer: augmentation or bounded residual module, not a first-stage nominal
controller.

Replaces: no control loop by default.

Inputs: selected state, tracking error, reference, disturbance features or
diagnostic features; exact feature set must be fixed per profile.

Outputs: bounded compensation term, gain schedule or residual command.

PX4 dependency: depends on host controller and SafetySupervisor.

MWORKS/codegen route: only allowed after model format, inference runtime,
fixed-size tensors and fallback behavior are defined.

Gazebo/Sunray validation: A/B against host controller under disturbance and
parameter mismatch.

Current gate: research/backlog.

Forbidden claims: no end-to-end neural policy is allowed in the first-stage
control baseline.
