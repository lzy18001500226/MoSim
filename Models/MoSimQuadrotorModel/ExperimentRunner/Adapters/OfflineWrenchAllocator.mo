within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineWrenchAllocator
  "MWORKS offline wrench-to-rotor allocator"

  parameter Real hover_speed = 53.562090367172424;
  parameter Real torque_to_command = hover_speed / 13.985413115099604 * 0.707;
  Modelica.Blocks.Interfaces.RealInput body_force[3];
  Modelica.Blocks.Interfaces.RealInput body_torque[3];
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
protected
  Real roll_term;
  Real pitch_term;
  Real yaw_term;
equation
  roll_term = torque_to_command * body_torque[1];
  pitch_term = torque_to_command * body_torque[2];
  yaw_term = torque_to_command * body_torque[3];
  rotor_command[1] = hover_speed + body_force[3] - yaw_term - pitch_term + roll_term;
  rotor_command[2] = -hover_speed - body_force[3] - yaw_term + pitch_term + roll_term;
  rotor_command[3] = hover_speed + body_force[3] - yaw_term + pitch_term - roll_term;
  rotor_command[4] = -hover_speed - body_force[3] - yaw_term - pitch_term - roll_term;
end OfflineWrenchAllocator;
