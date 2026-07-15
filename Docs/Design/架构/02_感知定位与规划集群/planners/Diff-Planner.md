# Diff-Planner

Status: CURRENT / Goal 3 primary planner.

Source: `References/Lab/planning_local/Diff-Planner`.

Inputs: map/perception input, state, goal and planner configuration.

Outputs: trajectory reference or candidate path to Planner Adapter.

State source: first reproduction must declare an explicit
`state_source_profile`. It may use PX4/MAVROS fused baseline odometry or a
FAST-LIO-derived profile, but the two result groups must not be mixed.

FAST-LIO dependency: not assumed by default. FAST-LIO is required only when the
selected reproduction profile declares it as map or state input.

Control boundary: no direct MAVROS control publication.

Current MoSim target: Diff-Planner is the primary engineering entry for the
known-goal minimum planning loop. It must cover single-UAV planning first and
then the frozen three-UAV swarm loop.

Three-UAV frozen profile:

```text
vehicle_id / namespace: uav1, uav2, uav3
mission input: preset goals or script-published goals
manual review input: RViz goal click only for audit/debug
mission flow: simultaneous takeoff -> three independent preset goals
              -> obstacle/agent avoidance -> hover -> land
localization: independent MID360 + FAST-LIO + state chain per UAV
control: independent px4ctrl + MAVROS + PX4 per UAV
```

Gazebo/RViz validation: single-UAV planning, three-UAV swarm planning,
trajectory handoff, tracking metrics, obstacle/agent clearance, RViz point
cloud/trajectory/axis/grid review and failure fallback.

Forbidden claims: Diff-Planner reproduction cannot be merged into EGO evidence;
it needs its own run profile and result bundle. Diff-Planner swarm success is
not autonomous exploration, not task allocation, not coverage exploration and
not MoSim self-developed formation control.
