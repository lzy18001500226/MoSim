# Learning MPC

Status: RESEARCH.

Layer: learning-assisted MPC candidate. Learning may tune model residuals,
cost weights, terminal terms or warm starts.

Replaces: no first-stage flight loop. It may augment LMPC/NMPC after the base
MPC pipeline has deterministic behavior and fallback.

Inputs: base MPC inputs, learned model or parameter artifact, confidence/status,
dataset/version hash, safety limits, dt and reset.

Outputs: adjusted model, weights, warm start or bounded residual; final control
must pass through the base MPC and SafetySupervisor.

PX4 dependency: first route reuses PX4 attitude/rate loops through the base
`ATTITUDE_THRUST` adapter.

MWORKS/codegen route: offline learning -> fixed artifact -> deterministic
inference wrapper -> ablation against base MPC.

Current gate: research only.

Forbidden claims: learned improvement must be separated from base MPC
performance and cannot be reported without ablation.
