# Sunray150 DAE Assembly Parameters

Source: accepted DAE/Blender assembly audit. These values replace geometry only.
Motor/thrust, mass, inertia, controller, and timing parameters remain unchanged.

## Rotor Centers

| Rotor | New XYZ m | Previous SDF XYZ m | Delta m | Confidence |
|---|---:|---:|---:|---|
| `rotor_0_front_right` | `[0.053745, -0.05374, -0.014052]` | `[0.065, -0.065, -0.025]` | `[-0.011255, 0.01126, 0.010948]` | high |
| `rotor_1_back_left` | `[-0.053761, 0.05376, -0.014052]` | `[-0.065, 0.065, -0.025]` | `[0.011239, -0.01124, 0.010948]` | high |
| `rotor_2_front_left` | `[0.053746, 0.053759, -0.014052]` | `[0.065, 0.065, -0.025]` | `[-0.011254, -0.011241, 0.010948]` | high |
| `rotor_3_back_right` | `[-0.053761, -0.053739, -0.014052]` | `[-0.065, -0.065, -0.025]` | `[0.011239, 0.011261, 0.010948]` | high |

## MID360

- mechanical mount pose candidate xyz/rpy: `[-5e-06, 0.032295, 0.050167, 0.0, 0.0, 4.712389]`
- laser sensor origin candidate: `[-5e-06, 0.032295, 0.150167]`
- mount center: `[-5e-06, 0.032295, 0.050167]`
- visual bbox center: `[-5e-06, 0.028363, 0.080223]`
- visual bbox size: `[0.064889, 0.072754, 0.060111]`
- official point-cloud to IMU translation m: `[0.011, 0.02329, -0.04412]`
- FAST-LIO LiDAR pose in IMU body frame m: `[-0.011, -0.02329, 0.04412]`
- confidence: high for mount/yaw, medium for laser origin because the Sunray livox_mid360 model keeps its ray sensor at local z=0.1
- official reference: Livox Mid-360 User Manual: point-cloud coordinate origin O-XYZ and built-in IMU position (11.0, 23.29, -44.12) mm in point-cloud coordinates.
- replacement status: hold_for_review - Livox official documents define a point-cloud coordinate origin O-XYZ and a built-in IMU, while FAST-LIO expects LiDAR pose in IMU body frame. The local Gazebo model also places its ray sensor at base_link local z=0.1. These are not the same as the mechanical mount center.

## Cameras

- front: pose xyz/rpy `[0.0, 0.1032, 0.0185, 0.0, 0.0, 0.0]`, confidence medium
- down: pose xyz/rpy `[0.0, 0.0145, -0.0263, 0.0, 1.5707963, 3.14]`, confidence medium

## Collision Envelope

- base_link box pose xyz/rpy: `[0.0, 0.001574, 0.044965, 0.0, 0.0, 0.0]`
- base_link box size xyz: `[0.211502, 0.214651, 0.16193]`
- source: conservative AABB of accepted full DAE assembly bounds, including propellers and top MID360
