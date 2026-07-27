within MoSimQuadrotorModel.Guidance.Trajectories;
model StepResponse
  "Hover at 2 m, then apply an XY position step"

  parameter Real hover_altitude_m(unit = "m") = 2;
  parameter Real takeoff_duration_s(unit = "s") = 5;
  parameter Real step_time_s(unit = "s") = 15;
  parameter Real x_step_m(unit = "m") = 1;
  parameter Real y_step_m(unit = "m") = -1;
  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position command [x, y, z] in m";
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference translational velocity [x, y, z] in m/s";
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference translational acceleration [x, y, z] in m/s2";

equation
  position_command[1] = if time < step_time_s then 0 else x_step_m;
  position_command[2] = if time < step_time_s then 0 else y_step_m;
  position_command[3] = if time < takeoff_duration_s then
    hover_altitude_m * time / takeoff_duration_s else hover_altitude_m;
  velocity_command = {0, 0, if time < takeoff_duration_s then
    hover_altitude_m / takeoff_duration_s else 0};
  acceleration_command = {0, 0, 0};

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 45,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end StepResponse;
