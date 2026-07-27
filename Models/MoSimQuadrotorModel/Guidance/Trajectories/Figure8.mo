within MoSimQuadrotorModel.Guidance.Trajectories;
model Figure8
  "Horizontal figure-eight at a fixed altitude"

  parameter Real altitude_m(unit = "m") = 2;
  parameter Real takeoff_duration_s(unit = "s") = 5;
  parameter Real trajectory_start_s(unit = "s") = 5;
  parameter Real x_amplitude_m(unit = "m") = 2;
  parameter Real y_amplitude_m(unit = "m") = 1;
  parameter Real angular_rate_rad_s(unit = "rad/s") = 0.35;
  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position command [x, y, z] in m";
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference translational velocity [x, y, z] in m/s";
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference translational acceleration [x, y, z] in m/s2";

protected
  Real elapsed_s(unit = "s");

equation
  elapsed_s = max(0, time - trajectory_start_s);
  position_command[1] = x_amplitude_m * sin(angular_rate_rad_s * elapsed_s);
  position_command[2] = y_amplitude_m * sin(2 * angular_rate_rad_s * elapsed_s);
  position_command[3] = if time < takeoff_duration_s then
    altitude_m * time / takeoff_duration_s else altitude_m;
  velocity_command[1] = if time < trajectory_start_s then 0 else
    x_amplitude_m * angular_rate_rad_s * cos(angular_rate_rad_s * elapsed_s);
  velocity_command[2] = if time < trajectory_start_s then 0 else
    2 * y_amplitude_m * angular_rate_rad_s
      * cos(2 * angular_rate_rad_s * elapsed_s);
  velocity_command[3] = if time < takeoff_duration_s then
    altitude_m / takeoff_duration_s else 0;
  acceleration_command[1] = if time < trajectory_start_s then 0 else
    -x_amplitude_m * angular_rate_rad_s ^ 2
      * sin(angular_rate_rad_s * elapsed_s);
  acceleration_command[2] = if time < trajectory_start_s then 0 else
    -4 * y_amplitude_m * angular_rate_rad_s ^ 2
      * sin(2 * angular_rate_rad_s * elapsed_s);
  acceleration_command[3] = 0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end Figure8;
