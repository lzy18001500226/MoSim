within MoSimQuadrotorModel.Control.Adapters;
model PidAwffLinearEsoRotorAdapter
  "AWFF PID with bounded linear ESO at the ROTOR_COMMAND boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  parameter Real eso_bandwidth_xy = 3.0;
  parameter Real eso_bandwidth_z = 2.0;
  parameter Real eso_b0_xy = 1.0;
  parameter Real eso_b0_z = 1.0;
  parameter Real eso_comp_limit_xy = 0.06;
  parameter Real eso_comp_limit_z = 1.0;
  parameter Real eso_enable = 1.0;

  MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_PidLinearEsoControllerEquation_Sysblock core(
    eso_bandwidth_xy = eso_bandwidth_xy,
    eso_bandwidth_z = eso_bandwidth_z,
    eso_b0_xy = eso_b0_xy,
    eso_b0_z = eso_b0_z,
    eso_comp_limit_xy = eso_comp_limit_xy,
    eso_comp_limit_z = eso_comp_limit_z,
    eso_enable = eso_enable);

  annotation(__MWORKS(version="26.3.0"));

equation
  core.x_error = position_ref[1] - position_mea[1];
  core.y_error = position_ref[2] - position_mea[2];
  core.z_error = position_ref[3] - position_mea[3];
  core.z_ref_rate = velocity_ref[3];
  core.roll_mea = attitude_mea[1];
  core.pitch_mea = attitude_mea[2];
  core.yaw_mea = attitude_mea[3];
  core.yaw_ref = 0;
  rotor_command = {hover_speed + command_scale * core.y,
    -hover_speed + command_scale * core.y1,
    hover_speed + command_scale * core.y2,
    -hover_speed + command_scale * core.y3};
end PidAwffLinearEsoRotorAdapter;