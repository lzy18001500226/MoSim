# Fault Allocation

Status: BACKLOG / not first-stage ATTITUDE_THRUST.

Layer: allocation and actuator fault-tolerance.

Inputs: desired wrench or motor-level command, actuator health/effectiveness,
saturation limits, fault profile and allocation weights.

Outputs: motor thrust, rotor speed or allocation-adjusted wrench.

PX4 dependency: first-stage MoSim reuses PX4 control allocation; fault allocation
requires BODY_RATE/WRENCH/ROTOR-level release or a PX4 allocation integration.

MWORKS/codegen route: fault model -> allocator -> saturation/failure tests ->
PX4 or plant-level integration.

Gazebo/Sunray validation: motor thrust loss, single-motor failure and safe
landing/recovery metrics.

Forbidden claims: fault allocation cannot be accepted in the ATTITUDE_THRUST-only
stage unless the exact allocation interface is released.

Current reopen gate: do not claim motor-level fault allocation inside the
current ATTITUDE_THRUST-only path. The first allowed gate is a scoped fault
injection or actuator-effectiveness diagnostic that records the failure model,
observed degradation, safe fallback, and the exact interface that would be
needed for WRENCH/ROTOR or PX4 allocation integration. Passing this gate means
"fault-response evidence gathered"; it does not mean motor-level allocation or
fault-tolerant flight is accepted.
