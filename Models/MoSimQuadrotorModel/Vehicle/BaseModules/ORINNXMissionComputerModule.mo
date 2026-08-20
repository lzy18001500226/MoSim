within MoSimQuadrotorModel.Vehicle.BaseModules;
block ORINNXMissionComputerModule
  "Top-level ORIN NX mission computer with internal trajectory source"
  parameter Real takeoff_time_s = 3.0;
  parameter Real return_altitude_m = 1.0;
  parameter Real landing_altitude_m = 0.15;
  parameter Real obstacle_warning_margin_m = 0.6;
  parameter Real estimator_degraded_threshold = 0.6;
  parameter Real degraded_nav_start_s = 1e9;
  parameter Real degraded_nav_end_s = 1e9;
  Modelica.Blocks.Interfaces.RealInput aircraft_position[3] 
    annotation (Placement(transformation(origin = {-110, 50}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealInput local_position[3] 
    annotation (Placement(transformation(origin = {-110, 15}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealInput obstacle_margin 
    annotation (Placement(transformation(origin = {-110, -20}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealInput estimator_quality 
    annotation (Placement(transformation(origin = {-110, -55}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput reference_position[3] 
    annotation (Placement(transformation(origin = {110, 65}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput reference_velocity[3] 
    annotation (Placement(transformation(origin = {110, 42}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput reference_acceleration[3] 
    annotation (Placement(transformation(origin = {110, 20}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_reference 
    annotation (Placement(transformation(origin = {110, -2}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput z_reference_rate 
    annotation (Placement(transformation(origin = {110, -22}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput health 
    annotation (Placement(transformation(origin = {110, -10}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput flight_mode 
    annotation (Placement(transformation(origin = {110, -30}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput active_setpoint_source 
    annotation (Placement(transformation(origin = {110, -50}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput safety_status 
    annotation (Placement(transformation(origin = {110, -70}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput event_code 
    annotation (Placement(transformation(origin = {110, -90}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Interfaces.RealOutput obstacle_avoid_active 
    annotation (Placement(transformation(origin = {110, -112}, extent = {{-5, -5}, {5, 5}})));
  MoSimQuadrotorModel.Guidance.Trajectories.ClimbTrajectory trajectory(gain(k = 1));
  Real degraded_nav_active;
equation
  degraded_nav_active = if estimator_quality < estimator_degraded_threshold then 1 else if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 1 else 0;
  obstacle_avoid_active = if obstacle_margin < obstacle_warning_margin_m then 1 else 0;
  flight_mode = if degraded_nav_active > 0.5 then 6 else if obstacle_avoid_active > 0.5 then 4 else if time < takeoff_time_s then 3 else 5;
  active_setpoint_source = if degraded_nav_active > 0.5 then 90 else if obstacle_avoid_active > 0.5 then 60 else if time < takeoff_time_s then 30 else 40;
  safety_status = if degraded_nav_active > 0.5 then 3 else if obstacle_avoid_active > 0.5 then 2 else 0;
  event_code = if degraded_nav_active > 0.5 then 60 else if obstacle_avoid_active > 0.5 then 40 else if time < takeoff_time_s then 30 else 50;
  reference_position[1] = if flight_mode >= 6 then 0 else trajectory.position_command[1];
  reference_position[2] = if flight_mode >= 6 then 0 else trajectory.position_command[2];
  reference_position[3] = if flight_mode >= 6 then return_altitude_m else if flight_mode >= 3 then trajectory.position_command[3] else landing_altitude_m;
  for i in 1:3 loop
    reference_velocity[i] = if flight_mode >= 6 then 0 else trajectory.velocity_command[i];
    reference_acceleration[i] = if flight_mode >= 6 then 0 else trajectory.acceleration_command[i];
  end for;
  yaw_reference = 0;
  z_reference_rate = 0;
  health = min(estimator_quality, if obstacle_margin >= obstacle_warning_margin_m then 1 else 0.6);
  annotation (
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {248, 248, 248}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {0, 14}, extent = {{-96, -72}, {96, 72}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/ORIN_NX.png"),
      Text(origin = {0, -82}, extent = {{-95, 14}, {95, -14}}, textString = "ORIN NX", textColor = {80, 80, 80})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end ORINNXMissionComputerModule;