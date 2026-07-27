within MoSimQuadrotorModel.Control.Bridges;
model HinfHoverWrenchEquationBridge
  "H-infinity hover-wrench graphical law through its existing CFunction core"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real mass_kg = profile.takeoff_mass_kg;
  parameter Real gravity_mps2 = profile.gravity_mps2;
  parameter Real force_min_n = 0;
  parameter Real force_max_n = 25;
  parameter Real torque_limit_nm = 8;
  parameter Real roll_stiffness_nm_per_rad = 30;
  parameter Real pitch_stiffness_nm_per_rad = 30;
  parameter Real yaw_stiffness_nm_per_rad = 40;
  parameter Real tilt_limit_rad = 0.35;
  parameter Real yaw_correction_limit_rad = 0.2;
  parameter Real max_normalized_thrust = 0.62;

  input Real state_roll;
  input Real state_pitch;
  input Real state_yaw;
  input Real state_p;
  input Real state_q;
  input Real state_r;
  input Real state_u;
  input Real state_v;
  input Real state_w;
  input Real state_x;
  input Real state_y;
  input Real state_z;
  input Real reference_roll;
  input Real reference_pitch;
  input Real reference_yaw;
  input Real reference_p;
  input Real reference_q;
  input Real reference_r;
  input Real reference_u;
  input Real reference_v;
  input Real reference_w;
  input Real reference_x;
  input Real reference_y;
  input Real reference_z;
  input Real enable;
  input Real reset;

  output Real wrench_force_n_out;
  output Real wrench_tau_x_nm_out;
  output Real wrench_tau_y_nm_out;
  output Real wrench_tau_z_nm_out;
  output Real status_code_out;

protected
  MoSimQuadrotorModel.Control.Implementations.ClassicRobust.MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock core;

equation
  core.state_roll_in = state_roll;
  core.state_pitch_in = state_pitch;
  core.state_yaw_in = state_yaw;
  core.state_p_in = state_p;
  core.state_q_in = state_q;
  core.state_r_in = state_r;
  core.state_u_in = state_u;
  core.state_v_in = state_v;
  core.state_w_in = state_w;
  core.state_x_in = state_x;
  core.state_y_in = state_y;
  core.state_z_in = state_z;
  core.reference_roll_in = reference_roll;
  core.reference_pitch_in = reference_pitch;
  core.reference_yaw_in = reference_yaw;
  core.reference_p_in = reference_p;
  core.reference_q_in = reference_q;
  core.reference_r_in = reference_r;
  core.reference_u_in = reference_u;
  core.reference_v_in = reference_v;
  core.reference_w_in = reference_w;
  core.reference_x_in = reference_x;
  core.reference_y_in = reference_y;
  core.reference_z_in = reference_z;
  core.enable_in = enable;
  core.reset_in = reset;
  core.mass_in = mass_kg;
  core.gravity_in = gravity_mps2;
  core.force_min_n_in = force_min_n;
  core.force_max_n_in = force_max_n;
  core.torque_limit_nm_in = torque_limit_nm;
  core.roll_stiffness_nm_per_rad_in = roll_stiffness_nm_per_rad;
  core.pitch_stiffness_nm_per_rad_in = pitch_stiffness_nm_per_rad;
  core.yaw_stiffness_nm_per_rad_in = yaw_stiffness_nm_per_rad;
  core.hover_percentage_in = profile.mworks_controller_hover_percentage;
  core.tilt_limit_rad_in = tilt_limit_rad;
  core.yaw_correction_limit_rad_in = yaw_correction_limit_rad;
  core.min_normalized_thrust_in = 0;
  core.max_normalized_thrust_in = max_normalized_thrust;

  wrench_force_n_out = core.wrench_force_n_out;
  wrench_tau_x_nm_out = core.wrench_tau_x_nm_out;
  wrench_tau_y_nm_out = core.wrench_tau_y_nm_out;
  wrench_tau_z_nm_out = core.wrench_tau_z_nm_out;
  status_code_out = core.status_code_out;

  annotation(__MWORKS(version = "26.3.0"));
end HinfHoverWrenchEquationBridge;
