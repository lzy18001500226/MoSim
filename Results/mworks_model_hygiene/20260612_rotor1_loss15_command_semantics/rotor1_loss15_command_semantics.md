# Rotor1 Loss15 Command Semantics Profile

Status: `diagnostic_profile_ready`
Direct/delta mismatch count: `0`
Hover-mapped count: `7`

Read-only diagnostic profile. It does not run MWORKS.

## Scenario Profiles

| Controller | Topology | Inferred Semantics | Abs Cmd Max | Final Z Error | Quality | Action |
|---|---|---|---:|---:|---|---|
| awff_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 20.000 | -14.999 | needs_iteration | retain_current_topology_for_controller_tuning |
| l1_residual_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 20.000 | -0.000 | needs_iteration | retain_current_topology_for_controller_tuning |
| l1_fault_allocation_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 20.000 | -14.999 | needs_iteration | retain_current_topology_for_controller_tuning |
| l1_online_fault_allocation_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 20.000 | -14.999 | needs_iteration | retain_current_topology_for_controller_tuning |
| l1_multi_fault_isolation_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 20.000 | -15.001 | needs_iteration | retain_current_topology_for_controller_tuning |
| linear_mpc_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 20.000 | -0.000 | needs_iteration | retain_current_topology_for_controller_tuning |
| linear_mpc_online_fault_allocation_sysblock | delta_to_hover_command_mapper | controller_outputs_delta_commands_mapped_to_hover_actuator_domain | 8.138 | 0.000 | pass | retain_current_topology_for_controller_tuning |

## Recommended Next Steps

- Treat Sysblock y/y1/y2/y3 outputs with output_limit around +/-20 as delta-like motor commands unless a controller proves otherwise.
- For direct-controller-to-actuator rotor-loss P1-B models with delta-like command traces, restore or standardize a hover command mapper before retuning gains.
- After each topology change, run a short smoke simulation first, then the 50 s scenario, then refresh candidate matrix and closeout gate.
- Do not enter UE replay/rendering until a current accepted rotor1_loss15 candidate exists.

## Claim Boundary

- This profile reads source and existing raw/metrics only.
- It does not prove a new live MWORKS run.
- It is diagnostic evidence for choosing the next single-UAV iteration, not controller acceptance.
