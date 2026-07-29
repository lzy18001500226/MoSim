# Non-Frontend Report Source Tables

更新时间：2026-07-18。本文是报告数据源，不是最终报告，也不是最终验收。

## Controller Family Summary

- accepted: `27`
- executed_blocked: `33`
- not_run: `7`

| Cohort | Accepted | Executed blocked | Not run |
|---|---:|---:|---:|
| G9_CORE_COMPARISON | 0 | 1 | 5 |
| P10_CLASSIC_RECONCILIATION | 0 | 12 | 2 |
| P11_CLASSIC_ADDITIONS | 0 | 5 | 0 |
| P1_PID | 6 | 0 | 0 |
| P2_LINEAR_ROBUST | 0 | 4 | 0 |
| P3_SLIDING_MODE | 1 | 5 | 0 |
| P4_MPC | 6 | 1 | 0 |
| P5_ENHANCEMENT | 3 | 3 | 0 |
| P6_SAFETY | 1 | 0 | 0 |
| P7_FTC | 1 | 0 | 0 |
| P8_FORMATION | 9 | 0 | 0 |
| P9_LEARNING | 0 | 2 | 0 |

## Official PID vs Gain-Scheduled PID

| Profile | Scenario | Status | Primary RMSE (m) | Wind/Fault injection | Landing/disarm | Reason |
|---|---|---|---:|---|---|---|
| official_pid | hover | executed_blocked | 0.031203254464950998 | not_applicable | True | hover_xy_rmse_above_max:0.029876911296298433 |
| official_pid | step | accepted | 0.06333609238399877 | not_applicable | True |  |
| official_pid | figure8 | executed_blocked | 0.05573648730301019 | not_applicable | True | trajectory_xyz_rmse_above_max:0.05573648730301019 |
| official_pid | spiral | executed_blocked | 0.05088783673802406 | not_applicable | True | steady_hover_xy_rmse_above_max:0.022686059229917108;steady_hover_z_rmse_above_max:0.029393586011077145;trajectory_xyz_rmse_above_max:0.05088783673802406 |
| official_pid | wind | executed_blocked | 0.10274094334956349 | passed | True | hover_xy_rmse_above_max:0.06191208313333685;hover_xy_max_above_max:0.12745810906338045 |
| official_pid | parameter_mismatch | executed_blocked | 0.03819686207486225 | not_applicable | True | hover_xy_rmse_above_max:0.03318827174950209;hover_xy_max_above_max:0.05023130264577199;hover_z_rmse_above_max:0.020060161206523583 |
| official_pid | motor_efficiency_fault | not_run | 0.02766978334535029 | blocked | True | hover_xy_rmse_above_max:0.028644744690470396 |
| gain_scheduled_pid | hover | executed_blocked | 0.03343078984895786 | not_applicable | True | hover_xy_rmse_above_max:0.0216863250978504;truth_local_delta_error_bad_z:0.40507688582847406 |
| gain_scheduled_pid | step | executed_blocked | 0.08024712740277866 | not_applicable | True | steady_hover_xy_rmse_above_max:0.02188283580985259;steady_hover_z_rmse_above_max:0.025111378210834055 |
| gain_scheduled_pid | figure8 | executed_blocked | 0.1577179555119819 | not_applicable | True | steady_hover_xy_rmse_above_max:0.03161627171035585;trajectory_xyz_rmse_above_max:0.1577179555119819;trajectory_xyz_p95_above_max:0.24127521754911463;trajectory_xyz_max_above_max:0.2698328185292799 |
| gain_scheduled_pid | spiral | executed_blocked | 0.16594111691348562 | not_applicable | True | steady_hover_xy_rmse_above_max:0.0381000202364988;steady_hover_xy_max_above_max:0.05239052053789186;trajectory_xyz_rmse_above_max:0.16594111691348562;trajectory_xyz_p95_above_max:0.2222126807333915;trajectory_xyz_max_above_max:0.23446400013501542 |
| gain_scheduled_pid | wind | executed_blocked | 0.23896818618862473 | passed | True | hover_xy_rmse_above_max:0.2222659780441552;hover_xy_max_above_max:0.2892686947242139;hover_z_rmse_above_max:0.02620173537652825 |
| gain_scheduled_pid | parameter_mismatch | executed_blocked | 0.0417040880513633 | not_applicable | True | hover_xy_rmse_above_max:0.029564099897827236;hover_xy_max_above_max:0.053351644149406185;hover_z_rmse_above_max:0.025022326198152065;hover_z_max_above_max:0.06616613471098054 |
| gain_scheduled_pid | motor_efficiency_fault | not_run | 0.03775122253227725 | blocked | True | hover_xy_rmse_above_max:0.029368238998306245 |

## Specialized Evidence

| Area | Authority status |
|---|---|
| Safety | `passed` |
| FTC | `passed` |
| Formation | `passed` |
| Learning | `closed_with_performance_blocker` |

## Writing Boundary

- Tables are generated from current authority JSON only.
- Rows retain accepted, executed_blocked and not_run status.
- A/B is an observed same-run comparison and does not establish general superiority.
- This source does not render figures, record video, or approve final submission wording.
