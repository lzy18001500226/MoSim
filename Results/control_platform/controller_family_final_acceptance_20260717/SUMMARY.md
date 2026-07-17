# Controller Family Final Acceptance Summary

Overall status: `closed_with_blockers`.

| Cohort | Controller | Codegen | SIL | Gazebo acceptance | Selectable | XY RMSE m | Z RMSE m | Blocker |
|---|---|---|---|---|---|---:|---:|---|
| P1_PID | cascade_pid | passed | passed | `accepted` | true | 0.009204 | 0.017625 |  |
| P1_PID | anti_windup | passed | passed | `accepted` | true | 0.014941 | 0.012564 |  |
| P1_PID | feedforward_profile | passed | passed | `accepted` | true | 0.009214 | 0.014233 |  |
| P1_PID | gain_scheduled_pid | passed | passed | `accepted` | true | 0.007562 | 0.014174 |  |
| P1_PID | fuzzy_pid | passed | passed | `accepted` | true | 0.014190 | 0.016755 |  |
| P1_PID | neural_pid | passed | passed | `accepted` | true | 0.013620 | 0.016784 |  |
| P2_LINEAR_ROBUST | lqg | passed | passed | `executed_blocked` | false | 0.057520 | 0.056224 | hover_xy_rmse_above_max:0.05751968270141498;hover_xy_max_above_max:0.06594786493098181;hover_z_rmse_above_max:0.05622366268766644;hover_z_max_above_max:0.07285001216967557 |
| P2_LINEAR_ROBUST | feedback_linearization | passed | passed | `executed_blocked` | false | 0.040062 | 0.060494 | hover_xy_rmse_above_max:0.040061624031686026;hover_xy_max_above_max:0.0538885269235946;hover_z_rmse_above_max:0.06049444268045179;hover_z_max_above_max:0.08143961883526629 |
| P2_LINEAR_ROBUST | passivity_based_control | passed | passed | `executed_blocked` | false | 0.031252 | 0.056650 | hover_xy_rmse_above_max:0.03125234705705186;hover_z_rmse_above_max:0.05664976329424122;hover_z_max_above_max:0.07195761943142043 |
| P2_LINEAR_ROBUST | adaptive_backstepping | passed | passed | `executed_blocked` | false | 0.494129 | 0.408293 | hover_xy_rmse_above_max:0.4941291107500093;hover_xy_max_above_max:0.5377037841471708;hover_z_rmse_above_max:0.40829276904845296;hover_z_max_above_max:0.4526939850038475 |
| P3_SLIDING_MODE | integral_smc | passed | passed | `executed_blocked` | false | 0.056083 | 0.016372 | hover_xy_rmse_above_max:0.05608252569604952;hover_xy_max_above_max:0.10270480991554297 |
| P3_SLIDING_MODE | terminal_smc | passed | passed | `executed_blocked` | false | 0.076518 | 0.030917 | hover_xy_rmse_above_max:0.07651768848384811;hover_xy_max_above_max:0.1589163153328268;hover_z_rmse_above_max:0.03091747753707477 |
| P3_SLIDING_MODE | nonsingular_terminal_smc | passed | passed | `executed_blocked` | false | 0.111038 | 0.067996 | hover_xy_rmse_above_max:0.1110377801620468;hover_xy_max_above_max:0.18914370447420958;hover_z_rmse_above_max:0.06799564311561053;hover_z_max_above_max:0.09174977047410082 |
| P3_SLIDING_MODE | super_twisting_smc | passed | passed | `accepted` | true | 0.009259 | 0.012280 |  |
| P3_SLIDING_MODE | adaptive_smc | passed | passed | `executed_blocked` | false | 0.134973 | 0.136887 | hover_xy_rmse_above_max:0.13497322111509796;hover_xy_max_above_max:0.26267403824148605;hover_z_rmse_above_max:0.13688685527251165;hover_z_max_above_max:0.1879825407481872;truth_local_delta_error_bad_x:4.40276064023687;truth_local_delta_error_bad_y:0.28120569278570756;truth_local_delta_error_bad_z:7.976918852750077 |
| P3_SLIDING_MODE | fuzzy_smc | passed | passed | `executed_blocked` | false | 0.078415 | 0.091777 | hover_xy_rmse_above_max:0.0784145912375166;hover_xy_max_above_max:0.1495939748514583;hover_z_rmse_above_max:0.09177698862635217;hover_z_max_above_max:0.10988028892236801 |
| P4_MPC | linear_mpc | passed | passed | `accepted` | true | 0.018981 | 0.014502 |  |
| P4_MPC | robust_mpc | passed | passed | `accepted` | true | 0.013495 | 0.012113 |  |
| P4_MPC | adaptive_mpc | passed | passed | `accepted` | true | 0.013882 | 0.018888 |  |
| P4_MPC | tube_mpc | passed | passed | `executed_blocked` | false | 0.009374 | 0.021296 | hover_z_rmse_above_max:0.021296255261340543 |
| P4_MPC | explicit_gain_scheduled_mpc | passed | passed | `accepted` | true | 0.014436 | 0.016360 |  |
| P4_MPC | ilqr | passed | passed | `accepted` | true | 0.019562 | 0.013370 |  |
| P4_MPC | mppi | passed | passed | `accepted` | true | 0.015959 | 0.017084 |  |
| P5_ENHANCEMENT | l1_adaptive | passed | passed | `executed_blocked` | false | 0.082076 | 0.186452 | hover_xy_rmse_above_max:0.08207561898787691;hover_xy_max_above_max:0.12303823096290949;hover_z_rmse_above_max:0.1864518294546371;hover_z_max_above_max:0.20669818688037678 |
| P5_ENHANCEMENT | awff | passed | passed | `executed_blocked` | false | 0.086965 | 0.018681 | hover_xy_rmse_above_max:0.08696451638455865;hover_xy_max_above_max:0.1226416160055635 |
| P5_ENHANCEMENT | complete_adrc | passed | passed | `executed_blocked` | false | 0.112531 | 0.101222 | hover_xy_rmse_above_max:0.11253113303936185;hover_xy_max_above_max:0.37959415801647134;hover_z_rmse_above_max:0.10122230817759983;hover_z_max_above_max:0.16448450119727753 |
| P5_ENHANCEMENT | standardized_indi | passed | passed | `accepted` | true | 0.011952 | 0.017702 |  |
| P5_ENHANCEMENT | parameter_scheduling | passed | passed | `accepted` | true | 0.012125 | 0.018139 |  |
| P5_ENHANCEMENT | ilc | passed | passed | `accepted` | true | 0.009868 | 0.014096 |  |
| G9_CORE_COMPARISON | official_pid | passed | passed | `executed_blocked` | false | 0.023873 | 0.019332 | hover_xy_rmse_above_max:0.023873305858575323 |
| G9_CORE_COMPARISON | se3_basic | passed | passed | `not_run` | false |  |  | official_pid shared baseline blocked; controller gate not run |
| G9_CORE_COMPARISON | dfbc_basic | passed | passed | `not_run` | false |  |  | official_pid shared baseline blocked; controller gate not run |
| G9_CORE_COMPARISON | smc_boundary_layer | passed | passed | `not_run` | false |  |  | official_pid shared baseline blocked; controller gate not run |
| G9_CORE_COMPARISON | pid_indi | passed | passed | `not_run` | false |  |  | official_pid shared baseline blocked; controller gate not run |
| G9_CORE_COMPARISON | nmpc_outer | passed | passed | `not_run` | false |  |  | official_pid shared baseline blocked; controller gate not run |
| P6_SAFETY | safety_supervisor_family | passed | passed | `accepted` | true |  |  |  |
| P7_FTC | fdi_ftc_family | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | leader_follower | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | virtual_structure | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | consensus | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | containment | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | formation_tracking | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | formation_reconfiguration | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | fault_tolerant_formation | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | formation_cbf | passed | passed | `accepted` | true |  |  |  |
| P8_FORMATION | distributed_mpc_formation | passed | passed | `accepted` | true |  |  |  |
| P9_LEARNING | trained_neural_residual | passed | passed | `executed_blocked` | false |  |  | strict performance acceptance blocked |
| P9_LEARNING | rl_gain_scheduler | passed | passed | `executed_blocked` | false |  |  | strict performance acceptance blocked |

Counts: `accepted=27`, `executed_blocked=16`, `not_run=5`.
