within MoSimQuadrotorModel.Guidance.Trajectories;
model SpiralAscent "Spiraling ascent with constant radius and climb rate"
  extends PartialTrajectory;

  parameter Real radius_m(unit = "m") = 1.5
    "Horizontal spiral radius";
  parameter Real angular_rate_rad_s(unit = "rad/s") = 0.3
    "Spiral angular rate";
  parameter Real climb_rate_m_s(unit = "m/s") = 0.15
    "Constant vertical climb rate";

protected
  Real theta "Spiral phase angle (rad)";

equation
  theta = angular_rate_rad_s * time;

  // Start at origin (0,0,0): x=r*sin(theta), y=r*(cos(theta)-1) = 0 at t=0
  position_command[1] = radius_m * sin(theta);
  position_command[2] = radius_m * (cos(theta) - 1);
  position_command[3] = climb_rate_m_s * time;

  velocity_command[1] = radius_m * angular_rate_rad_s * cos(theta);
  velocity_command[2] = -(radius_m * angular_rate_rad_s) * sin(theta);
  velocity_command[3] = climb_rate_m_s;

  acceleration_command[1] = -(radius_m * angular_rate_rad_s ^ 2) * sin(theta);
  acceleration_command[2] = -(radius_m * angular_rate_rad_s ^ 2) * cos(theta);
  acceleration_command[3] = 0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end SpiralAscent;