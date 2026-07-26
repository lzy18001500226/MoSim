within MoSimQuadrotorModel.Common.Models;
model EchoMcpStateSmoke
  "Minimal MWORKS_MCP echo state smoke; exposes command-echo status variables only"
  Real controller_select_status;
  Real wind_profile_status;
  Real motor_fault_status;
  Real scenario_reset_status;
  Real recording_status;
  Real forbidden_pose_status;
  Real no_pose_overwrite_status;
  Real accepted_mworks_owned_count;
  Real rejected_non_mworks_count;
  Real not_live_ue_runtime_ack;
  Real not_closed_loop;
  Real echo_state_keepalive;
equation
  controller_select_status = 1;
  wind_profile_status = if time >= 0.2 then 1 else 0;
  motor_fault_status = 1;
  scenario_reset_status = if time >= 0.4 then 1 else 0;
  recording_status = if time >= 0.6 then 1 else 0;
  forbidden_pose_status = -1;
  no_pose_overwrite_status = 1;
  accepted_mworks_owned_count = controller_select_status + wind_profile_status + motor_fault_status + scenario_reset_status + recording_status;
  rejected_non_mworks_count = 2;
  not_live_ue_runtime_ack = 1;
  not_closed_loop = 1;
  echo_state_keepalive = 0.001 * (accepted_mworks_owned_count + no_pose_overwrite_status - forbidden_pose_status);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end EchoMcpStateSmoke;