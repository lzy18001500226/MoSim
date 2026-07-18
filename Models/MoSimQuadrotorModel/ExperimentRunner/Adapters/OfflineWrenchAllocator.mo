within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineWrenchAllocator
  "MWORKS offline wrench-to-rotor allocator"

  parameter Real hover_speed = 53.562090367172424;
  Modelica.Blocks.Interfaces.RealInput body_force[3];
  Modelica.Blocks.Interfaces.RealInput body_torque[3];
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
equation
  rotor_command[1] = hover_speed + body_force[3] - body_torque[1] + body_torque[2] + body_torque[3];
  rotor_command[2] = -hover_speed - body_force[3] - body_torque[1] - body_torque[2] + body_torque[3];
  rotor_command[3] = hover_speed + body_force[3] + body_torque[1] - body_torque[2] + body_torque[3];
  rotor_command[4] = -hover_speed - body_force[3] + body_torque[1] + body_torque[2] + body_torque[3];
end OfflineWrenchAllocator;
