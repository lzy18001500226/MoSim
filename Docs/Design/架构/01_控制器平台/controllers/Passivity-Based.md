# Passivity-Based Control

Status: RESEARCH.

Layer: nonlinear energy/passivity-based control candidate for stability and
robustness studies.

Replaces: no first-stage flight loop. It may become a candidate controller core
after its energy function, damping injection and output layer are specified.

Inputs: state estimate, reference, energy/storage function parameters, damping
parameters, model parameters, dt, reset and enable.

Outputs: not released for current implementation. Preferred first output, if
selected later, is `ATTITUDE_THRUST`.

PX4 dependency: first practical route should reuse PX4 attitude/rate loops.

MWORKS/codegen route: analytical design -> bounded core -> offline tests ->
Gazebo A/B after template controllers are accepted.

Current gate: research only.

Forbidden claims: stability proof under one model is not equivalent to robust
tracking evidence under Sunray/Gazebo profiles.
