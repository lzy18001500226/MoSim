within MoSimQuadrotorModel.Guidance.Trajectories;
model SimpleDiagonalReference
  "Simple diagonal trajectory with time-offset takeoff: linear ramp with smoothstep"

  parameter Real start_time(unit = "s") = 0 "Takeoff delay time";
  parameter Real duration(unit = "s") = 60 "Flight duration from start to end";
  parameter Real x_start(unit = "m") = 0;
  parameter Real y_start(unit = "m") = 0;
  parameter Real z_start(unit = "m") = 1;
  parameter Real x_end(unit = "m") = 10;
  parameter Real y_end(unit = "m") = 10;
  parameter Real z_end(unit = "m") = 5;

  Modelica.Blocks.Interfaces.RealOutput position_command[3](each unit = "m")
    "Reference position [x, y, z]"
    annotation(Placement(transformation(origin = {100, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3](each unit = "m/s")
    "Reference velocity [vx, vy, vz]"
    annotation(Placement(transformation(origin = {100, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_command(unit = "rad")
    "Reference yaw angle"
    annotation(Placement(transformation(origin = {100, -60}, extent = {{-10, -10}, {10, 10}})));

protected
  Real tau "Normalized time [0, 1]";
  Real s "Smoothstep interpolation factor [0, 1]";
  Real ds_dt "Derivative of smoothstep";

equation
  // Time-offset takeoff: hold at start position until start_time
  if time < start_time then
    tau = 0;
  elseif time < start_time + duration then
    tau = (time - start_time) / duration;
  else
    tau = 1;
  end if;

  // Smoothstep interpolation: s(tau) = 3*tau^2 - 2*tau^3
  s = 3 * tau^2 - 2 * tau^3;
  ds_dt = if time < start_time then
            0
          elseif time < start_time + duration then
            (6 * tau - 6 * tau^2) / duration
          else
            0;

  // Position: linear interpolation with smoothstep
  position_command[1] = x_start + (x_end - x_start) * s;
  position_command[2] = y_start + (y_end - y_start) * s;
  position_command[3] = z_start + (z_end - z_start) * s;

  // Velocity: derivative of position
  velocity_command[1] = (x_end - x_start) * ds_dt;
  velocity_command[2] = (y_end - y_start) * ds_dt;
  velocity_command[3] = (z_end - z_start) * ds_dt;

  // Yaw: constant zero
  yaw_command = 0;

  annotation(__MWORKS(hide=true, version="26.3.0"));
end SimpleDiagonalReference;
