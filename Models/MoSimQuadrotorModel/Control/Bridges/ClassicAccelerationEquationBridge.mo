within MoSimQuadrotorModel.Control.Bridges;
model ClassicAccelerationEquationBridge
  "Shared CFunction bridge for the classic acceleration-command controller variants"

  parameter Integer controller_id = 5
    "1 pole placement, 2 MRAC, 3 NDI, 4 FOPID, 5 H2";
  parameter Real sample_time_s = 0.01;

  input Real position_x;
  input Real position_y;
  input Real position_z;
  input Real velocity_x;
  input Real velocity_y;
  input Real velocity_z;
  input Real reference_position_x;
  input Real reference_position_y;
  input Real reference_position_z;
  input Real reference_velocity_x;
  input Real reference_velocity_y;
  input Real reference_velocity_z;
  input Real reference_acceleration_x;
  input Real reference_acceleration_y;
  input Real reference_acceleration_z;
  input Real reference_yaw;
  input Real enable;
  input Real reset;

  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_attitude_w_out;
  output Real desired_attitude_x_out;
  output Real desired_attitude_y_out;
  output Real desired_attitude_z_out;
  output Real normalized_thrust_out;
  output Real collective_thrust_n_out;
  output Real saturated_out;
  output Real status_code_out;

protected
  MoSimQuadrotorModel.Control.Implementations.ClassicRobust.MoSim_Classic_CFunction_Sysblock core;

equation
  // The current Classic CFunction owns the exact stateful equations and uses
  // the frozen 1 kg Sunray150 parameter defaults shared by this formal line.
  core.controller_id_in = controller_id;
  core.dt_in = sample_time_s;
  core.position_x_in = position_x;
  core.position_y_in = position_y;
  core.position_z_in = position_z;
  core.velocity_x_in = velocity_x;
  core.velocity_y_in = velocity_y;
  core.velocity_z_in = velocity_z;
  core.reference_position_x_in = reference_position_x;
  core.reference_position_y_in = reference_position_y;
  core.reference_position_z_in = reference_position_z;
  core.reference_velocity_x_in = reference_velocity_x;
  core.reference_velocity_y_in = reference_velocity_y;
  core.reference_velocity_z_in = reference_velocity_z;
  core.reference_acceleration_x_in = reference_acceleration_x;
  core.reference_acceleration_y_in = reference_acceleration_y;
  core.reference_acceleration_z_in = reference_acceleration_z;
  core.reference_yaw_in = reference_yaw;
  core.enable_in = enable;
  core.reset_in = reset;

  desired_acceleration_x_out = core.desired_acceleration_x_out;
  desired_acceleration_y_out = core.desired_acceleration_y_out;
  desired_acceleration_z_out = core.desired_acceleration_z_out;
  desired_attitude_w_out = core.desired_attitude_w_out;
  desired_attitude_x_out = core.desired_attitude_x_out;
  desired_attitude_y_out = core.desired_attitude_y_out;
  desired_attitude_z_out = core.desired_attitude_z_out;
  normalized_thrust_out = core.normalized_thrust_out;
  collective_thrust_n_out = core.collective_thrust_n_out;
  saturated_out = core.saturated_out;
  status_code_out = core.status_code_out;

  annotation(__MWORKS(version = "26.3.0"));
end ClassicAccelerationEquationBridge;
