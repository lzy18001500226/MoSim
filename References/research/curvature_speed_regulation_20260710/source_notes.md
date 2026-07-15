# Source Notes

## What Transfers

Regulated Pure Pursuit introduces the practical idea that path tracking should
not always use a constant linear velocity. In constrained or high-curvature
motion, reducing speed can improve safety and tracking stability.

For this UGV model, that idea maps to `PathPlanner.target_v`: after the existing
Pure Pursuit steering command is computed, reduce the target speed only when
`abs(steering_angle)` exceeds a bounded threshold.

## What Does Not Transfer

Full Follow-the-Gap, DWA, TEB, costmap-based planning, and learned local
planning are not directly portable to the current official interface because
the controller sees only front/rear/left/right distance signals and the path
planner has no obstacle cloud or occupancy grid.

## Candidate Rule

Use one track-agnostic rule:

```text
if abs(steering_angle) > threshold:
    target_v = slow_speed
else:
    target_v = nominal path speed
```

The first candidate uses a conservative threshold so it targets sharp turns
rather than every ordinary path correction.

## Risk

The rule can improve road-edge or overshoot failures but may reduce score if it
slows useful straight-line motion or changes obstacle timing. It must be tested
on a weak target track first and then regressed across all four tracks only if
the first gate improves.
