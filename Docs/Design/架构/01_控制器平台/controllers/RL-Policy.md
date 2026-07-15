# RL Policy

Status: RESEARCH.

Layer: candidate gain scheduler, residual controller or trajectory parameter
optimizer; not a first-stage flight controller.

Replaces: no safety-critical loop unless a separate architecture decision
releases it.

Inputs: task-specific observation vector, bounded action space, safety state and
fallback status.

Outputs: gain schedule, bounded residual, time allocation or high-level decision.

PX4 dependency: must run behind SafetySupervisor and deterministic fallback.

MWORKS/codegen route: first route is offline or co-simulation training, then a
fixed inference artifact wrapped as a bounded scheduler/residual module. Any
MWORKS use must freeze observation normalization, action limits, network
weights, fallback controller and reproducible evaluation data before codegen.

Gazebo/Sunray validation: only after base controllers and safety fallback are
accepted.

Current gate: research only.

Forbidden claims: end-to-end motor RL is not part of the current competition
mainline, and a trained policy cannot be claimed safe without SafetySupervisor
and deterministic fallback evidence.
