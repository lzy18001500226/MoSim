within MoSimQuadrotorModel.Guidance.Trajectories;
model Figure8 "Figure-eight Lissajous trajectory at fixed altitude"
  extends PartialTrajectory;

  parameter Real altitude_m(unit = "m") = 2.0
    "Flight altitude";
  parameter Real takeoff_duration_s(unit = "s") = 5.0
    "Duration of takeoff ramp from 0 to altitude_m";
  parameter Real x_amplitude_m(unit = "m") = 2.0
    "X-axis sinusoidal amplitude";
  parameter Real y_amplitude_m(unit = "m") = 1.0
    "Y-axis half-amplitude (y = y_amplitude_m * sin(2*omega*tau))";
  parameter Real angular_rate_rad_s(unit = "rad/s") = 0.35
    "Base angular rate omega";

protected
  Real tau "Elapsed time since takeoff phase ended";

equation
  tau = max(0.0, time - takeoff_duration_s);

  position_command[1] = if time < takeoff_duration_s then 0 else 
      x_amplitude_m * sin(angular_rate_rad_s * tau);
  position_command[2] = if time < takeoff_duration_s then 0 else 
      y_amplitude_m * sin(2 * angular_rate_rad_s * tau);
  position_command[3] = if time < takeoff_duration_s then 
      (altitude_m / takeoff_duration_s) * time 
    else 
      altitude_m;

  velocity_command[1] = if time < takeoff_duration_s then 0 else 
      x_amplitude_m * angular_rate_rad_s * cos(angular_rate_rad_s * tau);
  velocity_command[2] = if time < takeoff_duration_s then 0 else 
      2 * y_amplitude_m * angular_rate_rad_s * cos(2 * angular_rate_rad_s * tau);
  velocity_command[3] = if time < takeoff_duration_s then 
      altitude_m / takeoff_duration_s 
    else 0;

  acceleration_command[1] = if time < takeoff_duration_s then 0 else 
      -(x_amplitude_m * angular_rate_rad_s ^ 2) * sin(angular_rate_rad_s * tau);
  acceleration_command[2] = if time < takeoff_duration_s then 0 else 
      -(4 * y_amplitude_m * angular_rate_rad_s ^ 2) * sin(2 * angular_rate_rad_s * tau);
  acceleration_command[3] = 0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end Figure8;