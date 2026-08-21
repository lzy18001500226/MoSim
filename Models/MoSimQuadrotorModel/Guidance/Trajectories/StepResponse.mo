within MoSimQuadrotorModel.Guidance.Trajectories;
model StepResponse "Hover at fixed altitude then apply XY position step"
  extends PartialTrajectory;

  parameter Real hover_altitude_m(unit = "m") = 2.0
    "Hover altitude";
  parameter Real takeoff_duration_s(unit = "s") = 5.0
    "Duration of takeoff ramp from 0 to hover_altitude_m";
  parameter Real step_time_s(unit = "s") = 15.0
    "Time at which the XY position step is applied";
  parameter Real x_step_m(unit = "m") = 1.0
    "X position step magnitude";
  parameter Real y_step_m(unit = "m") = -1.0
    "Y position step magnitude";

equation
  position_command[1] = if time >= step_time_s then x_step_m else 0;
  position_command[2] = if time >= step_time_s then y_step_m else 0;
  position_command[3] = if time < takeoff_duration_s then 
      (hover_altitude_m / takeoff_duration_s) * time 
    else 
      hover_altitude_m;

  velocity_command[1] = 0;
  velocity_command[2] = 0;
  velocity_command[3] = if time < takeoff_duration_s then 
      hover_altitude_m / takeoff_duration_s 
    else 0;

  acceleration_command[1] = 0;
  acceleration_command[2] = 0;
  acceleration_command[3] = 0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 45,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end StepResponse;