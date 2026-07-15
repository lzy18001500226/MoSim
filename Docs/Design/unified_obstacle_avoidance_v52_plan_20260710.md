# Unified Obstacle Avoidance v52 Plan

Status: planned_for_target_track_validation, 2026-07-10 CST

## Goal

Continue from v48, the current review-ready best candidate, with one unified
front-risk brake-turn coupling mechanism. This is not a per-track rule and does
not branch on wrapper name, score variable, collision counter, or scenario id.

## Evidence Basis

Current accepted cursor:

```text
v48 total wrapper score: 37.2
Track3: T=112.45, cR=1, cO=1, P=9.2, simulate_failed with result variables
```

Fresh diagnostic evidence:

```text
Results/metrics/signal_window_summary_v48_v50_v51_track3_for_v52_20260710.md
References/research/front_risk_brake_turn_coupling_20260710/MANIFEST.md
References/research/front_risk_brake_turn_coupling_20260710/source_notes.md
```

At the first v48 Track3 obstacle event:

```text
time = 1.05 s
df = 0.8306
dl = 0.5677
dr = 0.5673
flag = 1
speed_pp = 1
speed_oa = -1
final_speed = 0.7196
steer_pp = -0.0386
steer_oa = 0.6
final_steer = 0.1623
```

v50 did not affect this event. v51 suppressed path speed too strongly and
ended at `T=2.25`, so v52 must couple moderate speed reduction with obstacle
steering priority instead of repeating either isolated route.

## Candidate Mechanism

Allowed edit:

```text
Models/UGV/Control/ControlAllocate/package.mo
```

In the narrow straight-front risk window:

```modelica
frontRiskStraight = speed_oa < 0
  and abs(unitDelay1.y) < 0.10
  and steer_oa * unitDelay1.y < 0;
```

Apply:

```modelica
gain2.u = if frontRiskStraight then 0.75 * unitDelay3.y else unitDelay3.y;
gain3.u = if frontRiskStraight then -0.5 * unitDelay1.y
  else if speed_oa < 0 and steer_oa * unitDelay1.y < 0 then 0.5 * unitDelay1.y
  else unitDelay1.y;
```

Rationale:

- `0.75` path-speed contribution matches the already accepted curvature-speed
  scale and is less aggressive than v51's rejected `0.4`.
- Flipping half of the small opposing path-steer contribution turns path
  cancellation into weak obstacle-steer support only when path steering is
  nearly straight.
- The broader v48 opposing-steer guard remains unchanged outside the narrow
  front-risk window.

## Validation Gate

1. Run the source/static deployability checker.
2. Run Track3 first.
3. Accept continuation only if Track3 removes the early obstacle contact,
   improves score/collision counts, or at least keeps a comparable runtime
   while improving one collision metric.
4. If Track3 regresses or early-stops, restore v48 semantics, write rejection
   evidence, send the sparse Chinese terminal notice, and continue with a
   different evidence-backed route.
5. If Track3 improves, run all four tracks before accepting v52.

## Non-Claims

- This plan does not claim final competition score.
- This plan does not claim physical UGV success.
- This plan does not authorize final submission packaging or sending.
