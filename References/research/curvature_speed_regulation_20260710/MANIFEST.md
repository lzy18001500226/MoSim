# Curvature Speed Regulation Research Pack

created_at: 2026-07-10 00:28 CST

## Scope

This pack records the small research basis for UGV controller candidate
`v44_curvature_speed_regulation`. It is a reference note only; no external code
is copied into the official model.

## Sources

| Source | URL | Used For |
|---|---|---|
| Regulated Pure Pursuit for Robot Path Tracking | https://arxiv.org/abs/2305.20026 | Supports the idea that Pure Pursuit path tracking can regulate linear speed for safety in constrained spaces. |
| Nav2 / Navigation2 overview | https://docs.nav2.org/ | Confirms Nav2 is a production navigation framework and that RPP is an accepted controller-family pattern, but not directly reusable here. |
| F1TENTH Lab 4 Follow the Gap | https://f1tenth-coursekit.readthedocs.io/en/stable/assignments/labs/lab4.html | Confirms gap-following needs a scan array; current UGV has only four distance signals, so full FTG is not directly portable. |
| F1TENTH survey | https://arxiv.org/abs/2402.18558 | Confirms classical reactive/path-tracking methods are common in small Ackermann-like racing tasks. |

## Local Application

The current model has only four distance inputs and a Pure Pursuit path planner.
Therefore:

- Do not copy a full Follow-the-Gap planner.
- Do not add a costmap or optimizer.
- Do use a small, deployable speed regulation rule when path steering demand is
  high.

## Non-Claims

- This pack does not prove MWORKS score improvement.
- This pack does not prove real-vehicle readiness.
- Candidate acceptance still requires source gate and track runtime evidence.
