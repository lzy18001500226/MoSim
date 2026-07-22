within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model LinearMPCRotorAdapter
  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialRotorCommandController;
  parameter Real hover_speed = 53.562090367172424;
  parameter Real command_scale = hover_speed / 13.985413115099604;
  MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock core;
equation
  core.x_error = position_ref[1] - position_mea[1];
  core.y_error = position_ref[2] - position_mea[2];
  core.z_error = position_ref[3] - position_mea[3];
  core.z_ref_rate = 0;
  core.roll_mea = attitude_mea[1];
  core.pitch_mea = attitude_mea[2];
  core.yaw_mea = attitude_mea[3];
  core.yaw_ref = 0;
  rotor_command = {hover_speed + command_scale * core.y,
    -hover_speed + command_scale * core.y1,
    hover_speed + command_scale * core.y2,
    -hover_speed + command_scale * core.y3};
end LinearMPCRotorAdapter;
