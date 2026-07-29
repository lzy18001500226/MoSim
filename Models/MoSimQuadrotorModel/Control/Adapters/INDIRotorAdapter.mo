within MoSimQuadrotorModel.Control.Adapters;
model INDIRotorAdapter
  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_INDIControllerEquation_Sysblock core;
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
    hover_speed - command_scale * core.y1,
    hover_speed + command_scale * core.y2,
    hover_speed - command_scale * core.y3};
end INDIRotorAdapter;
