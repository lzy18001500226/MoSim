# H-Infinity

Status: OFFLINE CANDIDATE / frozen-hover WRENCH core implemented.

Layer: robust linear control candidate for uncertainty and disturbance
attenuation around a frozen operating region.

Replaces: selected linearized outer-loop or attitude-loop design only after
the plant uncertainty model is frozen.

Inputs: state estimate, reference state, linearized plant, weighting functions,
disturbance model, dt, reset and enable.

Outputs: the licensed upstream formulation produces total thrust and three-axis
moment, so the faithful first candidate is `WRENCH`. It remains
`selectable=false` until a matching safety filter, allocator and backend adapter
exist. It must not be relabeled as `ATTITUDE_THRUST`.

PX4 dependency: first version reuses PX4 attitude/rate loops.

MWORKS/codegen route: plant linearization -> weighting design -> controller
synthesis -> reduced/implementable core -> offline consistency -> Gazebo A/B.

Current gate: the upstream MIT implementation at commit
`fd51f68701ec1bd549b9796d8277db2c8fb89240` is reproduced at the zero-Euler
hover operating point. `Config/control_platform/hinf_hover_frozen_gain.json`
records the weights-derived gain, gamma, Riccati residual and closed-loop pole
bound. `Scripts/control_platform/wave_b_hinf_core.c` is a fixed-size C step
core; `Results/control_platform/g5_wave_b_hinf_20260716/G5_WAVE_B_HINF_GATE.json`
is its independent offline oracle gate.

The current result proves only licensed synthesis reproduction and C arithmetic
equivalence at one frozen operating point. Nonlinear gain scheduling, MWORKS
MIL, generated-C, WRENCH safety/allocation, Factory disturbance A/B and Gazebo
runtime remain pending.

Forbidden claims: cannot claim robust superiority from nominal tracking only.
