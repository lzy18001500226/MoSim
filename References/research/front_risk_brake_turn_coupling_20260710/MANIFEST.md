# Front-Risk Brake-Turn Coupling Research

Date: 2026-07-10 CST

Scope: targeted research for the next unified UGV obstacle-avoidance candidate
after v48/v50/v51 Track3 evidence.

## Sources

| Source | URL | Use |
|---|---|---|
| RoboRacer / F1TENTH Follow the Gap lab | https://f1tenth-coursekit.readthedocs.io/en/latest/assignments/labs/lab4.html | Confirms reactive obstacle avoidance can be compact and based on safety bubble / gap selection. |
| RoboRacer Follow the Gap lecture | https://f1tenth-coursekit.readthedocs.io/en/latest/lectures/ModuleB/lecture05.html | Lists Follow-the-Gap, Disparity Extender, Bug, and potential-field approaches as reactive methods. |
| Nav2 Regulated Pure Pursuit documentation | https://docs.nav2.org/configuration/packages/configuring-regulated-pp.html | Confirms curvature and collision-proximity velocity regulation as a deployable control pattern. |
| Nav2 controller selection notes | https://docs.nav2.org/setup_guides/algorithm/select_algorithm.html | Notes RPP is suitable for Ackermann platforms and uses collision / velocity constraints. |
| F1TENTH survey | https://arxiv.org/abs/2402.18558 | Confirms FTG / Disparity Extender are mapless local methods but normally require LiDAR scan arrays. |

## Local Evidence Inputs

```text
Results/metrics/four_track_candidate_review_v48_opposing_steer_guard_20260710.md
Results/metrics/track3_candidate_review_v50_moderate_curve_speed_20260710.md
Results/metrics/track3_candidate_review_v51_straight_brake_arbitration_20260710.md
Results/metrics/signal_window_summary_v48_v50_v51_track3_for_v52_20260710.md
```

## Reuse Boundary

Do not copy upstream code. The current contest controller has only four
distance inputs and speed/steer outputs, so complete FTG, DWA, TEB, MPPI, or
Nav2 controllers are out of scope. Reuse only the mechanism pattern:

```text
front risk + obstacle command active
  -> keep commands bounded
  -> slow enough for maneuvering
  -> let avoidance steering dominate briefly
  -> avoid per-track branches
```
