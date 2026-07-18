within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfficialPIDRotorAdapter
  "Official PID adapted explicitly to the offline ROTOR_COMMAND boundary"

  extends MoSimQuadrotorModel.ExperimentRunner.Interfaces.PartialRotorCommandController;
  parameter Real legacy_hover_speed = 13.985413115099604;
  parameter Real hover_speed = 53.562090367172424;
  parameter Real command_scale = hover_speed / legacy_hover_speed;
  QuadrotorModel.Blocks.Controller.Controller core;
equation
  connect(position_ref, core.position_command);
  connect(position_mea, core.position);
  connect(attitude_mea, core.angle);
  rotor_command[1] = hover_speed + command_scale * core.y;
  rotor_command[2] = -hover_speed + command_scale * core.y1;
  rotor_command[3] = hover_speed + command_scale * core.y2;
  rotor_command[4] = -hover_speed + command_scale * core.y3;
end OfficialPIDRotorAdapter;
