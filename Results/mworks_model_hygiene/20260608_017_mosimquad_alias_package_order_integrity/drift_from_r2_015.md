# Drift From R2 015

R2 015 is stale for current package/order counts and live-audit queue inputs.

| Surface | R2 015 | Current 017 static gate | Drift reason |
|---|---:|---:|---|
| MoSim formal top categories | 11 | 12 | R1 019 added `Parameters`. |
| MoSim ordered child entries | 64 | 68 | R1 017/018 added Dynamics entries; R1 019 added Parameters child. |
| Dynamics ordered entries | 9 | 12 | R1 017 added mapper/mapped wrapper; R1 018 added optional damping/gyro layer. |
| DynamicsUpgrade ordered entries | pre-017/018 | 12 | Compatibility aliases and concrete sources were added. |

015 remains useful as ownership taxonomy, but its counts, package surface map, and next live queue must not be used as current acceptance evidence.
