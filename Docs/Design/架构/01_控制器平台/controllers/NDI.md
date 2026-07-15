# NDI

Status: BACKLOG.

Layer: nonlinear dynamic inversion candidate. NDI is model-based; INDI is kept
as a separate augmentation/module candidate under `../modules/INDI.md`.

Replaces: selected acceleration/attitude command generation after model and
actuator effectiveness are frozen.

Inputs: state estimate, trajectory derivatives, model parameters, actuator
effectiveness, saturation limits, dt, reset and enable.

Outputs: first candidate maps to `ATTITUDE_THRUST`; body-rate or actuator-level
outputs require a later interface release.

PX4 dependency: first version reuses PX4 attitude/rate loops.

MWORKS/codegen route: model inversion core -> saturation and singularity guards
-> generated C/C++ -> same offline and Gazebo gates.

Current gate: backlog. Compare with INDI only after baseline actuator and delay
profiles are measured.

Forbidden claims: do not conflate NDI and INDI; NDI requires stronger model
accuracy assumptions.
