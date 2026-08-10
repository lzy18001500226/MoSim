# Unified Obstacle Avoidance v44 Plan

created_at: 2026-07-10 00:28 CST

## Candidate

`v44_curvature_speed_regulation`

## Starting Point

Accepted baseline remains `v13_side_trigger045`:

```modelica
transition(cruise, avoid, df <= mindis or dl <= 0.45 or dr <= 0.45, reset = false)
transition(avoid, cruise, after(2,sec), reset = false)
avoid_lateral.ini_state steer := 0.6
```

## Problem Evidence

Recent candidates v42 and v43 show that open-side steering and side-only
decoupling can reduce road contacts but create obstacle contacts. Earlier v36
to v39 show that direct final-steering clipping or planner-steering suppression
can improve one track while regressing another.

Therefore the next candidate should not continue side-threshold, steering-gain,
release-dwell, braking, or final-steer limiter scans.

## Mechanism

Use a small Regulated Pure Pursuit style mechanism in the path planner:

```text
compute existing Pure Pursuit steering_angle
compute existing nominal target_v from path
if abs(steering_angle) > curve_slowdown_steer:
    target_v = curve_slowdown_speed
```

This keeps the same route and same obstacle controller, but reduces path speed
when the path itself asks for a large steering angle. It is track-agnostic and
does not inspect track id, wrapper id, score variables, or obstacle count.

## Edit Scope

Allowed edit:

```text
Models/UGV/Control/PathPlanning/PathPlanner.mo
```

No edits to:

```text
Models/UGV/Vehicle/
Models/UGV/Road/
Models/UGV/saidao/
Models/UGV/CountPoint/
Models/UGV/Example/
References/official_materials/
```

## First Gate

1. Static source gate: run `Scripts/quality/check_controller_deployability.py`
   and record that it checks the obstacle controller boundary only.
2. Target runtime: run Track4 first because v13 still has road contacts there
   and this mechanism targets path curvature / road-edge overshoot.
3. Continue to Track1/Track2/Track3 only if Track4 improves or reveals a
   comparable non-regression signal.

## Acceptance

Accept only if the same algorithm improves total four-track evidence against
v13 or produces a clear target-track improvement without unacceptable
regression.

Reject and restore v13 if Track4 or follow-up regression gets worse.

## Non-Claims

This plan does not claim score improvement, physical UGV readiness, or final
submission readiness. Runtime evidence under `Results/` is required.
