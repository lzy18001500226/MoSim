within MoSimQuadrotorModel.Control.PID;
model OfficialPidContinuousMapper
  "Stateless current-sample rotor mapper for the Official PID Sysblock core"

  parameter Real hover_command = 64.7923778389665;
  parameter Real command_scale = 4.632854053414571;
  parameter Real yaw_authority_scale = 0.26666666666666666;

  Modelica.Blocks.Interfaces.RealInput amplitude_1;
  Modelica.Blocks.Interfaces.RealInput amplitude_2;
  Modelica.Blocks.Interfaces.RealInput amplitude_3;
  Modelica.Blocks.Interfaces.RealInput amplitude_4;
  Modelica.Blocks.Interfaces.RealOutput rotor_command_1;
  Modelica.Blocks.Interfaces.RealOutput rotor_command_2;
  Modelica.Blocks.Interfaces.RealOutput rotor_command_3;
  Modelica.Blocks.Interfaces.RealOutput rotor_command_4;

protected
  Real yaw_amplitude;
  Real non_yaw_amplitude[4];
  Real mapped_amplitude[4];

equation
  yaw_amplitude = (-amplitude_1 + amplitude_2 - amplitude_3 + amplitude_4) / 4;
  non_yaw_amplitude[1] = amplitude_1 + yaw_amplitude;
  non_yaw_amplitude[2] = amplitude_2 - yaw_amplitude;
  non_yaw_amplitude[3] = amplitude_3 + yaw_amplitude;
  non_yaw_amplitude[4] = amplitude_4 - yaw_amplitude;
  mapped_amplitude[1] = non_yaw_amplitude[1] - yaw_authority_scale * yaw_amplitude;
  mapped_amplitude[2] = non_yaw_amplitude[2] + yaw_authority_scale * yaw_amplitude;
  mapped_amplitude[3] = non_yaw_amplitude[3] - yaw_authority_scale * yaw_amplitude;
  mapped_amplitude[4] = non_yaw_amplitude[4] + yaw_authority_scale * yaw_amplitude;
  rotor_command_1 = hover_command + command_scale * mapped_amplitude[1];
  rotor_command_2 = -(hover_command + command_scale * mapped_amplitude[2]);
  rotor_command_3 = hover_command + command_scale * mapped_amplitude[3];
  rotor_command_4 = -(hover_command + command_scale * mapped_amplitude[4]);

  annotation(__MWORKS(version = "26.3.0"));
end OfficialPidContinuousMapper;