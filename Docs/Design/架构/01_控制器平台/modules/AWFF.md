# AWFF

Status: BACKLOG / semantics need audit.

Layer: augmentation or feedforward compensation.

Inputs: reference acceleration, disturbance estimate, wind/fault estimate or
host-controller diagnostics depending on the audited AWFF variant.

Outputs: feedforward or compensation term applied before SafetySupervisor.

PX4 dependency: depends on host controller and output layer.

MWORKS/codegen route: audit any existing AWFF Sysblock/Modelica entries before
claiming implementation -> split atomic AWFF from composite profiles ->
generated code validation.

Gazebo/Sunray validation: A/B against same host controller under trajectory and
disturbance profiles.

Forbidden claims: AWFF meaning must be frozen per implementation before using
its metrics in controller comparisons. Existing candidate code or notes do not
equal an accepted AWFF module without evidence paths and A/B validation.

Current reopen gate: first freeze the exact AWFF meaning for this turn
(aerodynamic drag feedforward, wind feedforward, or other compensation), then
run one host-controller A/B case in the current Sunray/Gazebo/PX4/MAVROS lane.
The evidence must include the no-AWFF baseline, AWFF profile snapshot,
disturbance/trajectory profile, compensation bounds, and unchanged controller
and planner parameters. Passing this gate means "candidate AWFF contribution
observed"; it does not authorize broad tuning, static-only completion, or
MWORKS/codegen promotion.
