within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineAttitudeRateAllocator
  "MWORKS offline attitude/rate inner loop plus allocator; not PX4 evidence"

  parameter Real hover_speed = 53.562090367172424;
  parameter Real k_attitude = 4;
  Modelica.Blocks.Interfaces.RealInput attitude_ref[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealInput collective_thrust_delta;
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
protected
  Real roll_term;
  Real pitch_term;
  Real yaw_term;
equation
  roll_term = k_attitude * (attitude_ref[1] - attitude_mea[1]);
  pitch_term = k_attitude * (attitude_ref[2] - attitude_mea[2]);
  yaw_term = k_attitude * (attitude_ref[3] - attitude_mea[3]);
  rotor_command[1] = hover_speed + collective_thrust_delta - roll_term + pitch_term + yaw_term;
  rotor_command[2] = -hover_speed - collective_thrust_delta - roll_term - pitch_term + yaw_term;
  rotor_command[3] = hover_speed + collective_thrust_delta + roll_term - pitch_term + yaw_term;
  rotor_command[4] = -hover_speed - collective_thrust_delta + roll_term + pitch_term + yaw_term;
end OfflineAttitudeRateAllocator;
