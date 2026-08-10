# Unified Obstacle Avoidance v45 Plan

created_at: 2026-07-10 00:34 CST

## Candidate

`v45_curvature_speed_regulation_scaled`

## Reason For v45

Candidate v44 used the right mechanism direction but the wrong target-speed
scale. Runtime evidence showed:

```text
pathPlanner.target_v min = 1.0
pathPlanner.target_v max = 1.0
ctrlAlloc.speed_pp min = 1.0
ctrlAlloc.speed_pp max = 1.0
```

Therefore `curve_slowdown_speed = 7.5` was above the active normalized path
speed and produced a no-op. v45 keeps the same track-agnostic mechanism but
sets the curve speed cap on the observed normalized scale.

## Mechanism

```text
if abs(steering_angle) > 0.35 and target_v > 0.75:
    target_v = 0.75
```

This remains a unified algorithm and does not branch on track, score, wrapper,
or scenario.

## First Gate

1. Run the same static deployability checker and record its boundary.
2. Run Track4 first because road collisions are the target symptom.
3. If Track4 improves, run four-track regression.
4. If Track4 regresses or stays unchanged, reject and restore v13/v13-path
   semantics before trying another mechanism.

## Non-Claims

This plan does not claim improvement until runtime metrics under `Results/`
show it.
