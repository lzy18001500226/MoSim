# MPC Variants

Status: BACKLOG / taxonomy card.

Layer: umbrella card for MPC variants that are not yet released as standalone
implementation targets.

Covers:

```text
LTV-MPC
incremental MPC
gain-scheduled MPC
min-max MPC
stochastic MPC
output-feedback MPC
MPC-CBF composite profiles
```

Replaces: no current controller by default. A variant must be promoted into a
dedicated card or profile before implementation.

Inputs: selected base MPC inputs plus the variant-specific model schedule,
uncertainty set, probability model, output observer, CBF constraint or
incremental state.

Outputs: same output layer as the selected base MPC profile, normally
`ATTITUDE_THRUST` for the first practical route.

PX4 dependency: first practical variants reuse PX4 attitude/rate loops.

MWORKS/codegen route: base LMPC/NMPC template first -> variant-specific model
and constraint contract -> deadline/fallback check -> Gazebo A/B.

Current gate: taxonomy only. Do not implement before LMPC/NMPC baseline and
solver evidence exist.

Forbidden claims: a generic MPC result cannot be relabeled as LTV, stochastic,
min-max or MPC-CBF without the corresponding model and constraint evidence.
