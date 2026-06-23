# Vehicle Families

Status: discussion draft, 2026-06-14.

CoSim is organized by vehicle family first. Simulator backends are selected
under each family, not used as the top-level product structure.

| Family | Entry | Default route |
|---|---|---|
| Multirotor | `multirotor/README.md` | MWORKS now; Gazebo + ROS2 exported-controller validation next; PX4 when deployment semantics are claimed; UE render/review. |
| Fixed-wing | `fixed_wing/README.md` | JSBSim + ArduPlane + UE, ROS2 optional. |
| VTOL | `vtol/README.md` | PX4 VTOL/Gazebo first, JSBSim candidate for aero studies. |
| Ducted model-aircraft | `ducted_model_aircraft/README.md` | Benign model-aircraft route with JSBSim/custom six-DOF candidate. |

## Shared Rule

Each family must define:

- user-facing goals;
- default plant truth backend;
- default flight-control backend;
- controller design/codegen route;
- ROS2 and autonomy needs;
- UE/review needs;
- evidence levels and blockers;
- future expansion path.
