within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfficialPIDRotorAdapter
  "Official PID adapted explicitly to the offline ROTOR_COMMAND boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialRotorCommandController;
  parameter Real legacy_hover_speed = 13.985413115099604;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / legacy_hover_speed;
  MoSimQuadrotorModel.Plant.Blocks.Controller.Controller core;
  annotation(__MWORKS(version="26.3.0"));
equation
  connect(position_ref, core.position_command);
  connect(position_mea, core.position);
  connect(attitude_mea, core.angle);
  rotor_command[1] = hover_speed + command_scale * core.y;
  rotor_command[2] = -hover_speed + command_scale * core.y1;
  rotor_command[3] = hover_speed + command_scale * core.y2;
  rotor_command[4] = -hover_speed + command_scale * core.y3;
end OfficialPIDRotorAdapter;
