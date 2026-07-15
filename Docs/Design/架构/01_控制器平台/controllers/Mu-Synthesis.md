# Mu-Synthesis

Status: RESEARCH.

Layer: structured robust control research candidate for parametric uncertainty.

Replaces: no current flight loop. It may become an analysis/design reference
after the linearized plant and uncertainty blocks are frozen.

Inputs: uncertain plant model, structured uncertainty description, weighting
functions and performance objectives.

Outputs: candidate controller model and robustness margins; flight output layer
is not released in the first stage.

PX4 dependency: not applicable until a reduced implementable controller is
selected.

MWORKS/codegen route: research only first. Any generated controller must be
order-reduced, bounded and passed through the same offline/Gazebo gates as other
cores.

Current gate: documentation and comparison candidate only.

Forbidden claims: mu-analysis margins do not equal Gazebo, PX4 or true-flight
success.
