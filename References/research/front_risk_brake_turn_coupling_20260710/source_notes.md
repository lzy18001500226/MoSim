# Front-Risk Brake-Turn Coupling Source Notes

## Why This Research Was Needed

v48 is the current best four-track candidate, but Track3 still has one early
obstacle contact and one road contact. v50 and v51 show that the next step
should not be another scalar-only speed tweak:

- v50 lowered the curvature speed threshold and did not change the first
  Track3 obstacle contact.
- v51 suppressed path speed too strongly in a narrow straight-brake condition
  and produced a non-comparable early stop.

## Relevant External Patterns

F1TENTH Follow-the-Gap and Disparity Extender are mapless local planners. Their
core idea is to avoid the closest obstacle using a safety bubble and steer into
the largest safe gap. This is not directly implementable here because the
controller sees only `front_dist`, `rear_dist`, `left_dist`, and `right_dist`,
not a LiDAR scan array.

Nav2 Regulated Pure Pursuit is also not directly portable, but its useful
pattern is velocity regulation by curvature and nearby collision risk. This is
already partially present in v45/v48 through the path-planner curvature speed
cap, but Track3's first obstacle event is near-straight, so a path-curvature
rule alone cannot affect it.

## Local Mapping

The practical v52 mechanism should be a bounded control-allocation rule, not a
new full planner:

```text
if obstacle avoidance is commanding reverse/brake
and path steering is nearly straight
and path steering opposes obstacle steering
then temporarily:
  reduce the path speed contribution moderately
  suppress or flip the path steering cancellation
else keep v48 behavior
```

This couples braking and turning only in the front-risk straight-on obstacle
window. It is more specific than v49 broad path-speed attenuation and less
aggressive than v51 straight-brake-only attenuation.

## Acceptance Filter

Accept the mechanism only if Track3 removes the early obstacle contact or
improves collision/score without a non-comparable early stop. If Track3 fails,
restore v48 and record the rejection before trying another route.
