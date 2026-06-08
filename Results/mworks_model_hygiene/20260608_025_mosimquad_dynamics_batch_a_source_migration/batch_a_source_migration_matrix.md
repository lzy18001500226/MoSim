# Dynamics Batch A Source Migration

Request: `PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-BATCH-A-SOURCE-MIGRATION-20260608-025`

Status: `passed_static`

| Formal target | Formal source | Legacy alias | Legacy implementation | Migration state |
|---|---|---|---|---|
| `MoSimQuadrotorModel.Dynamics.RotorActuatorCore` | `Models/MoSimQuadrotorModel/Dynamics/RotorActuatorCore.mo` | `QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RflyStyleRotorDynamics.mo` | `formal_source_materialized_extends_only` |
| `MoSimQuadrotorModel.Dynamics.WrapperSurface` | `Models/MoSimQuadrotorModel/Dynamics/WrapperSurface.mo` | `QuadrotorExperiments.DynamicsUpgrade.WrapperSurface` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperSurface.mo` | `formal_source_materialized_extends_only` |

## Claim Boundary

- Batch A is static source migration only.
- Only `RotorActuatorCore` and `WrapperSurface` are in the Batch A source surface.
- Legacy `QuadrotorExperiments.DynamicsUpgrade` aliases and implementation files remain the behavior source.
- No live MWORKS load, `check_model`, `SimulateModel`, result variables, graphical/layout review, controller performance, planner readiness, runtime ack, mission success, or closed loop is claimed.
