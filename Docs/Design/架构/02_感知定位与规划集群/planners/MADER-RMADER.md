# MADER / RMADER

Status: REFERENCE / multi-UAV trajectory negotiation and communication-robust
deconfliction candidate.

Source:

```text
References/Lab/swarm_coordination/mader
References/Lab/swarm_coordination/rmader
```

Inputs: per-UAV state, planned trajectory, neighbor trajectory broadcasts,
obstacle map or local environment, timing and communication assumptions.

Outputs: collision-free trajectory candidates or trajectory revisions for the
Planner Adapter.

FAST-LIO dependency: not assumed by default. If a MoSim experiment uses FAST-LIO
as the state or map source, the run profile must declare it explicitly.

Control boundary: MADER/RMADER do not own MAVROS/PX4 control publication. They
can only feed trajectories into the Planner Adapter and Trajectory Server.

MoSim use: evaluate delayed or asynchronous multi-UAV trajectory coordination
after the current Diff-Planner three-UAV baseline is stable. The main questions
are communication delay, stale neighbor trajectories, replanning conflict,
minimum inter-UAV distance, and recovery after missing updates.

Gazebo/RViz validation if opened: start with two-UAV crossing paths, then three
UAVs with delayed trajectory broadcast, then obstacle-plus-neighbor avoidance.
Evidence must include per-UAV logs, namespace isolation, trajectory timestamps,
minimum inter-UAV distance, collision status, and RViz review.

Forbidden claims: MADER/RMADER source review is not autonomous exploration,
not MoSim self-developed formation control, and not proof that the generated
MWORKS controller works in multi-UAV runtime until codegen reinjection and
Gazebo/PX4 evidence are produced.
