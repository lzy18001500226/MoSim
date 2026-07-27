within MoSimQuadrotorModel.Guidance.Trajectories;
model SpiralAscent
  "Horizontal circular motion with a continuous altitude climb"

  parameter Real radius_m(unit = "m") = 1.5;
  parameter Real angular_rate_rad_s(unit = "rad/s") = 0.30;
  parameter Real climb_rate_m_s(unit = "m/s") = 0.15;
  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position command [x, y, z] in m";
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference translational velocity [x, y, z] in m/s";
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference translational acceleration [x, y, z] in m/s2";

equation
  position_command[1] = radius_m * (cos(angular_rate_rad_s * time) - 1);
  position_command[2] = radius_m * sin(angular_rate_rad_s * time);
  position_command[3] = climb_rate_m_s * time;
  velocity_command[1] = -radius_m * angular_rate_rad_s
    * sin(angular_rate_rad_s * time);
  velocity_command[2] = radius_m * angular_rate_rad_s
    * cos(angular_rate_rad_s * time);
  velocity_command[3] = climb_rate_m_s;
  acceleration_command[1] = -radius_m * angular_rate_rad_s ^ 2
    * cos(angular_rate_rad_s * time);
  acceleration_command[2] = -radius_m * angular_rate_rad_s ^ 2
    * sin(angular_rate_rad_s * time);
  acceleration_command[3] = 0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end SpiralAscent;
