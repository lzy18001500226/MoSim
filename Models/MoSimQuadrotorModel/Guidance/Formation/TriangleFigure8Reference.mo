within MoSimQuadrotorModel.Guidance.Formation;
model TriangleFigure8Reference
  "Virtual-structure triangle reference moving along a horizontal figure-eight"

  parameter Real altitude_m(unit = "m") = 2;
  parameter Real takeoff_duration_s(unit = "s") = 5;
  parameter Real trajectory_start_s(unit = "s") = 5;
  parameter Real x_amplitude_m(unit = "m") = 2;
  parameter Real y_amplitude_m(unit = "m") = 1;
  parameter Real angular_rate_rad_s(unit = "rad/s") = 0.35;
  parameter Real slot_offset_m[3, 3](each unit = "m") = {
    {0, 1.2, 0},
    {-1.0392304845, -0.6, 0},
    {1.0392304845, -0.6, 0}}
    "Three fixed virtual-structure slots in the world frame";

  Modelica.Blocks.Interfaces.RealOutput uav1_position_command[3]
    "UAV 1 reference position [m]";
  Modelica.Blocks.Interfaces.RealOutput uav1_velocity_command[3]
    "UAV 1 reference velocity [m/s]";
  Modelica.Blocks.Interfaces.RealOutput uav1_acceleration_command[3]
    "UAV 1 reference acceleration [m/s2]";
  Modelica.Blocks.Interfaces.RealOutput uav2_position_command[3]
    "UAV 2 reference position [m]";
  Modelica.Blocks.Interfaces.RealOutput uav2_velocity_command[3]
    "UAV 2 reference velocity [m/s]";
  Modelica.Blocks.Interfaces.RealOutput uav2_acceleration_command[3]
    "UAV 2 reference acceleration [m/s2]";
  Modelica.Blocks.Interfaces.RealOutput uav3_position_command[3]
    "UAV 3 reference position [m]";
  Modelica.Blocks.Interfaces.RealOutput uav3_velocity_command[3]
    "UAV 3 reference velocity [m/s]";
  Modelica.Blocks.Interfaces.RealOutput uav3_acceleration_command[3]
    "UAV 3 reference acceleration [m/s2]";

protected
  Real elapsed_s(unit = "s");
  Real center_position[3](each unit = "m");
  Real center_velocity[3](each unit = "m/s");
  Real center_acceleration[3](each unit = "m/s2");

equation
  elapsed_s = max(0, time - trajectory_start_s);
  center_position[1] = if time < trajectory_start_s then 0 else
    x_amplitude_m * sin(angular_rate_rad_s * elapsed_s);
  center_position[2] = if time < trajectory_start_s then 0 else
    y_amplitude_m * sin(2 * angular_rate_rad_s * elapsed_s);
  center_position[3] = if time < takeoff_duration_s then
    altitude_m * time / takeoff_duration_s else altitude_m;
  center_velocity[1] = if time < trajectory_start_s then 0 else
    x_amplitude_m * angular_rate_rad_s * cos(angular_rate_rad_s * elapsed_s);
  center_velocity[2] = if time < trajectory_start_s then 0 else
    2 * y_amplitude_m * angular_rate_rad_s
      * cos(2 * angular_rate_rad_s * elapsed_s);
  center_velocity[3] = if time < takeoff_duration_s then
    altitude_m / takeoff_duration_s else 0;
  center_acceleration[1] = if time < trajectory_start_s then 0 else
    -x_amplitude_m * angular_rate_rad_s ^ 2
      * sin(angular_rate_rad_s * elapsed_s);
  center_acceleration[2] = if time < trajectory_start_s then 0 else
    -4 * y_amplitude_m * angular_rate_rad_s ^ 2
      * sin(2 * angular_rate_rad_s * elapsed_s);
  center_acceleration[3] = 0;

  uav1_position_command = center_position + {
    slot_offset_m[1, 1], slot_offset_m[1, 2], slot_offset_m[1, 3]};
  uav2_position_command = center_position + {
    slot_offset_m[2, 1], slot_offset_m[2, 2], slot_offset_m[2, 3]};
  uav3_position_command = center_position + {
    slot_offset_m[3, 1], slot_offset_m[3, 2], slot_offset_m[3, 3]};
  uav1_velocity_command = center_velocity;
  uav2_velocity_command = center_velocity;
  uav3_velocity_command = center_velocity;
  uav1_acceleration_command = center_acceleration;
  uav2_acceleration_command = center_acceleration;
  uav3_acceleration_command = center_acceleration;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end TriangleFigure8Reference;
