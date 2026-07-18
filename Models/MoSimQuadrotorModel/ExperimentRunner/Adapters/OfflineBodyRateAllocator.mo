within MoSimQuadrotorModel.ExperimentRunner.Adapters;
model OfflineBodyRateAllocator
  "MWORKS offline body-rate inner loop plus allocator; not PX4 evidence"

  parameter Real hover_speed = 53.562090367172424;
  Modelica.Blocks.Interfaces.RealInput body_rate_ref[3];
  Modelica.Blocks.Interfaces.RealInput collective_thrust_delta;
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
equation
  rotor_command[1] = hover_speed + collective_thrust_delta - body_rate_ref[1] + body_rate_ref[2] + body_rate_ref[3];
  rotor_command[2] = -hover_speed - collective_thrust_delta - body_rate_ref[1] - body_rate_ref[2] + body_rate_ref[3];
  rotor_command[3] = hover_speed + collective_thrust_delta + body_rate_ref[1] - body_rate_ref[2] + body_rate_ref[3];
  rotor_command[4] = -hover_speed - collective_thrust_delta + body_rate_ref[1] + body_rate_ref[2] + body_rate_ref[3];
end OfflineBodyRateAllocator;
