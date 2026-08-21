within MoSimQuadrotorModel.Guidance.Trajectories;
model HoverHold "Takeoff ramp then hold at target altitude"
  extends PartialTrajectory;

  parameter Real target_altitude_m(unit = "m") = 2.0
    "Target hold altitude";
  parameter Real takeoff_duration_s(unit = "s") = 5.0
    "Duration of takeoff ramp from 0 to target_altitude_m";
  parameter Real hold_duration_s(unit = "s") = 30.0
    "Duration of altitude hold after takeoff";

equation
  position_command[1] = 0;
  position_command[2] = 0;
  position_command[3] = if time < takeoff_duration_s then 
      (target_altitude_m / takeoff_duration_s) * time 
    else 
      target_altitude_m;

  velocity_command[1] = 0;
  velocity_command[2] = 0;
  velocity_command[3] = if time < takeoff_duration_s then 
      target_altitude_m / takeoff_duration_s 
    else 0;

  acceleration_command[1] = 0;
  acceleration_command[2] = 0;
  acceleration_command[3] = 0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 35,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end HoverHold;