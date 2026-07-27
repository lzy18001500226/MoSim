within MoSimQuadrotorModel.Guidance.Trajectories;
model HoverHold
  "Take off to 2 m and hold the position for 30 s"

  parameter Real target_altitude_m(unit = "m") = 2;
  parameter Real takeoff_duration_s(unit = "s") = 5;
  parameter Real hold_duration_s(unit = "s") = 30;
  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position command [x, y, z] in m";
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference translational velocity [x, y, z] in m/s";
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference translational acceleration [x, y, z] in m/s2";

equation
  position_command[1] = 0;
  position_command[2] = 0;
  position_command[3] = if time < takeoff_duration_s then
    target_altitude_m * time / takeoff_duration_s else target_altitude_m;
  velocity_command = {0, 0, if time < takeoff_duration_s then
    target_altitude_m / takeoff_duration_s else 0};
  acceleration_command = {0, 0, 0};

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 35,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end HoverHold;
