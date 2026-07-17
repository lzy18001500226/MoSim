# Classic Controller Closeout Summary

Status: `closed_with_blockers`.

Rows: `67`. `accepted=27`, `executed_blocked=21`, `not_run=19`.

Complete row visibility is not acceptance. See each row's blocker and claim ceiling.

## Classic Additions

| Controller | Final status | Hover XY RMSE (m) | Hover Z RMSE (m) | Trajectory | First blocker |
|---|---|---:|---:|---|---|
| pole_placement_luenberger | executed_blocked | 0.016693 | 0.055173 | not_run | hover_z_rmse_above_max:0.05517251571082064;hover_z_max_above_max:0.06886479308336013 |
| mrac | executed_blocked | 0.014747 | 0.014800 | blocked | steady_hover_z_rmse_above_max:0.031083479536249837;trajectory_xyz_rmse_above_max:0.06349253762169102;trajectory_xyz_p95_above_max:0.08788831366383405 |
| ndi | executed_blocked | 0.010331 | 0.014736 | blocked | steady_hover_xy_rmse_above_max:0.023158034026257223;trajectory_xyz_rmse_above_max:0.05039725398991712 |
| fopid | executed_blocked | 0.010483 | 0.030180 | not_run | hover_z_rmse_above_max:0.030180420832681104;hover_z_max_above_max:0.05733039396824757 |
| h2_state_feedback | executed_blocked | 0.013688 | 0.022701 | not_run | hover_z_rmse_above_max:0.022701384839746073 |
