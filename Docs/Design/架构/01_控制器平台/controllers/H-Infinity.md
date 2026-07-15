# H-Infinity

Status: BACKLOG / research candidate.

Layer: robust linear control candidate for uncertainty and disturbance
attenuation around a frozen operating region.

Replaces: selected linearized outer-loop or attitude-loop design only after
the plant uncertainty model is frozen.

Inputs: state estimate, reference state, linearized plant, weighting functions,
disturbance model, dt, reset and enable.

Outputs: first candidate should be mapped to `ATTITUDE_THRUST` through the same
controller core contract; lower-level outputs require a separate interface
release.

PX4 dependency: first version reuses PX4 attitude/rate loops.

MWORKS/codegen route: plant linearization -> weighting design -> controller
synthesis -> reduced/implementable core -> offline consistency -> Gazebo A/B.

Current gate: no implementation until uncertainty weights and evaluation
disturbance profiles are explicit.

Forbidden claims: cannot claim robust superiority from nominal tracking only.
