# ANFIS

Status: RESEARCH / intelligent augmentation candidate.

Layer: neuro-fuzzy scheduler or compensator. It is not a first-stage standalone
flight controller.

Replaces: no safety-critical loop. It may tune PID/SMC/MPC parameters or output
a bounded residual behind SafetySupervisor.

Inputs: selected tracking errors, error derivatives, operating condition,
bounded normalization profile, frozen rule/network parameters, dt and enable.

Outputs: gain schedule, compensation term or bounded residual with explicit
limits and fallback status.

PX4 dependency: must run behind the same adapter and safety limits as the base
controller.

MWORKS/codegen route: offline training or design -> fixed inference artifact ->
bounded generated/core wrapper -> repeatable evaluation.

Current gate: research until dataset, training protocol and deterministic
fallback are defined.

Forbidden claims: training accuracy cannot be used as flight control evidence.
