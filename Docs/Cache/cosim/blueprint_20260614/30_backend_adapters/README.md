# Backend Adapters

Status: discussion draft, 2026-06-14.

Backend adapters connect CoSim vehicle-family needs to specific simulators,
flight controllers, middleware, renderers, and controller-generation tools.

Read first:

```text
Docs/Cache/cosim/blueprint_20260614/research/07_Backend_Decision_Matrix.md
```

## Adapter Categories

| Category | Candidates | Main role |
|---|---|---|
| Plant/world | MWORKS, Gazebo, JSBSim, MuJoCo, Isaac, Genesis, Bullet, Flightmare | Vehicle/world state integration. |
| Flight control | PX4, ArduPilot/ArduPlane, Simulink generated code, MWORKS controller, RL policy | Converts goals/state into actuator authority. |
| Algorithm bus | ROS2, direct API, training loop, MAVLink/MAVSDK | Connects autonomy modules and logs. |
| Rendering/review | UE, RViz, Gazebo GUI, Isaac renderer, backend-native viewer | Human-facing visualization and replay. |
| Sensor source | Gazebo sensors, UE sensors, backend-native sensors, replay/real logs | Produces labelled observations. |

## Adapter Contract

Each backend adapter must declare:

```yaml
adapter_id:
vehicle_families:
authority_surfaces:
supported_modes:
clock_policy:
input_contracts:
output_contracts:
evidence_outputs:
known_limits:
stop_conditions:
```

## One-Truth Rule

For one entity in one run:

```text
exactly one plant-truth backend
zero or one active flight-control authority
zero or one primary algorithm bus
zero or more render/review surfaces
zero or more labelled sensor sources
```

Multiple renderers and sensors are allowed. Multiple plant truth integrators for
the same entity are not allowed unless a future coupled-simulation contract
explicitly defines master/slave authority and synchronization.

## Current Adapter Decisions

| Adapter | Decision |
|---|---|
| `mworks_competition` | Current A8 model/control evidence route. |
| `gazebo_px4_ros2_multirotor` | Default post-competition multirotor engineering route. |
| `jsbsim_ardupilot_fixed_wing` | Default fixed-wing route. |
| `simulink_codegen_controller` | Future controller design and generated-code route. |
| `ue_frontend` | Default high-quality render/review/console surface. |
| `mujoco_rl` | Optional RL/control research route. |
| `isaac_rl_sensor` | Optional GPU/RL/synthetic-sensor route. |
| `airsim_reference` | Architecture and UE vehicle/sensor API reference, not default plant. |
