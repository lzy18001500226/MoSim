# RL And High-Speed Physics Backends

Status: reviewed research decision draft, 2026-06-14.

Source raw notes:

- `research/raw/MuJoCo.md`
- `research/raw/MuJoCo生态`
- `research/raw/Isaac.md`
- `research/raw/Genesis.md`
- `research/raw/Bullet.md`
- `research/raw/Flightmare.md`

External sources:

- MuJoCo overview: https://mujoco.readthedocs.io/en/stable/overview.html
- MuJoCo computation docs: https://mujoco.readthedocs.io/en/stable/computation/
- Isaac Sim documentation: https://docs.isaacsim.omniverse.nvidia.com/
- Isaac Lab documentation: https://isaac-sim.github.io/IsaacLab/

## 1. Position

MuJoCo, Isaac, Genesis, Bullet/PyBullet, and Flightmare are optional CoSim
research backends for high-throughput control, reinforcement learning,
contact-rich simulation, high-speed tasks, and photorealistic or GPU-accelerated
experiments. They are not a single replacement for Gazebo/PX4 or JSBSim/ArduPilot.

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |
|---|---|---|
| Multirotor | strong research fit | Fast batch hover/tracking/disturbance/RL and high-speed gate experiments. |
| Fixed-wing | optional | Useful for simplified control/RL, but JSBSim is stronger for aero truth. |
| VTOL | optional | Useful for transition policy exploration; engineering validation still needs PX4/ArduPilot/Gazebo/JSBSim gates. |
| Ducted model-aircraft | candidate | Useful for direct actuator and short high-speed research if aero model is defined. |
| Ground/legged future | strong fit | Isaac/MuJoCo/Bullet are natural for robotics contact and manipulation. |

## 3. Authority Classification

| Authority surface | Classification |
|---|---|
| Plant truth | May own plant truth for RL/research runs if declared. |
| Flight-control authority | Often direct actuator or policy control; not equivalent to PX4/ArduPilot authority. |
| ROS2 / algorithm bus | Optional bridge; many training loops bypass ROS2 for speed. |
| UE / rendering frontend | Usually separate; Isaac has its own renderer, Flightmare has decoupled rendering. |
| Sensor generation | Varies by backend; Isaac strongest for synthetic sensors, MuJoCo strong for state/sensor primitives. |
| RL / batch training | Primary use case. |
| SIL / HIL / deployment | Indirect: policies/controllers must be exported and revalidated in engineering stack. |

## 4. Integration Pattern

Training/research route:

```text
VehicleFamilyEnv
  -> backend-specific plant step
  -> observation vector / image / point cloud
  -> policy or controller
  -> direct actuator command
  -> reward / metrics / replay
  -> selected controller exported to CoSim Controller ABI
  -> validated in Gazebo/PX4 or JSBSim/ArduPilot route
```

Do not treat direct-motor policy success as PX4/ArduPilot deployment success.

## 5. Strengths

- Faster iteration than full autopilot-in-loop for many research tasks.
- Good for parameter sweeps, domain randomization, RL, and high-speed tasks.
- MuJoCo has clean model/data separation and actuator/control APIs.
- Isaac/Isaac Lab is strong for GPU simulation, synthetic sensors, and large
  robotics workflows.
- Flightmare demonstrates a useful separation of fast dynamics and rendering.

## 6. Gaps And Risks

- Direct actuator control removes the autopilot API layer, which the user
  correctly identified as a major abstraction gap.
- Policies trained without PX4/ArduPilot modes/failsafes may not transfer.
- Sensor realism and timing must be revalidated in ROS2/Gazebo/UE routes.
- Backend-specific model formats can fragment the vehicle model registry.

## 7. CoSim Adoption Decision

Decision: optional high-throughput research backends.

Recommended roles:

| Backend | CoSim role |
|---|---|
| MuJoCo / MJX | fast control/RL, model/data separation reference, direct actuator backend. |
| Isaac Sim / Isaac Lab | GPU/sensor/RL route and synthetic perception reference. |
| Genesis | future GPU/multi-physics research candidate. |
| Bullet / PyBullet | lightweight reference and education/prototyping backend. |
| Flightmare | multirotor fast dynamics/rendering split reference. |

## 8. Required Next Evidence

- Unified `VehicleFamilyEnv` interface: reset, step, observe, reward, done,
  event, and export.
- Controller/policy export path into `ControllerInput` / `ControllerOutput`.
- Domain-randomization manifest and seed discipline.
- Revalidation gate in Gazebo/PX4 or JSBSim/ArduPilot before engineering
  claims.

