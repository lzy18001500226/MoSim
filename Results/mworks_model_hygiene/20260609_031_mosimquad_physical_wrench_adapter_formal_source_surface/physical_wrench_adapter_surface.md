# PhysicalWrenchAdapter Formal Source Surface

Request: `PMO-MWORKS-R2-MOSIMQUAD-PHYSICAL-WRENCH-ADAPTER-FORMAL-SOURCE-SURFACE-20260609-031`

Status: `passed_static`

## Source Surface

- Formal target: `MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter`
- Formal source: `Models/MoSimQuadrotorModel/Dynamics/PhysicalWrenchAdapter.mo`
- Legacy alias preserved: `QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter`
- Legacy implementation preserved: `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchFrameAdapter.mo`

The formal source is intentionally an extends-only project-owned surface. It does not duplicate the MultiBody world/body/WorldForceAndTorque structure, force/torque equations, frame connection, wrapper outputs, or motor-order/yaw gate observations.

## Static Anchors

- MultiBody world/body/force adapter: `world`, `body`, and `WorldForceAndTorque` remain in the legacy implementation.
- Physical wrench application: `forceAndTorque.force = applied_force_body`, `forceAndTorque.torque = applied_torque_body`, and `connect(forceAndTorque.frame_b, body.frame_a)` remain intact.
- Wrapper bridge: `wrapper.total_thrust`, `wrapper.total_moment_body`, `motor_order_gate_error`, and `yaw_direction_gate_error` remain exposed.
- Legacy wrapper implementation remains a separate source anchor and was not edited by 031.

## Claim Boundary

- Static source/package surface only.
- No live MWORKS load, `check_model`, `SimulateModel`, result variable, package browser, or graphical acceptance is claimed.
- No physical wrench equation, numerical parameter, MultiBody world/body/force adapter, frame connection, wrapper force/torque mapping, motor order/yaw gate behavior, solver, controller, ROS2, UE, Sunray/PBR, Blender, References, official QuadrotorModel, or CoAgent runtime file was changed.
