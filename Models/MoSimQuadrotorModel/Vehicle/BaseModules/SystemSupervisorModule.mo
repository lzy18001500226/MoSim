within MoSimQuadrotorModel.Vehicle.BaseModules;
block SystemSupervisorModule
  "System-level failsafe supervisor for exported mode/event evidence"
  parameter Real degraded_nav_start_s = 1e9;
  parameter Real degraded_nav_end_s = 1e9;
  parameter Real battery_low_start_s = 1e9;
  parameter Real battery_low_end_s = 1e9;
  parameter Real offboard_loss_start_s = 1e9;
  parameter Real offboard_loss_end_s = 1e9;
  parameter Real mission_failure_start_s = 1e9;
  parameter Real mission_failure_end_s = 1e9;
  parameter Real geofence_breach_start_s = 1e9;
  parameter Real geofence_breach_end_s = 1e9;
  parameter Real battery_low_threshold = 0.1;
  parameter Real takeoff_time_s = 3.0;
  Modelica.Blocks.Interfaces.RealInput voltage_margin 
    annotation (Placement(transformation(origin = {-110, 75}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput degraded_nav_active 
    annotation (Placement(transformation(origin = {110, 85}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput obstacle_avoid_active 
    annotation (Placement(transformation(origin = {110, 70}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput estimator_quality 
    annotation (Placement(transformation(origin = {110, 55}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput estimator_mode 
    annotation (Placement(transformation(origin = {110, 40}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput flight_mode 
    annotation (Placement(transformation(origin = {110, 25}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput active_setpoint_source 
    annotation (Placement(transformation(origin = {110, 10}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput safety_status 
    annotation (Placement(transformation(origin = {110, -5}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput event_code 
    annotation (Placement(transformation(origin = {110, -20}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput battery_low_active 
    annotation (Placement(transformation(origin = {110, -35}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput offboard_loss_active 
    annotation (Placement(transformation(origin = {110, -50}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput mission_failure_active 
    annotation (Placement(transformation(origin = {110, -65}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput geofence_breach_active 
    annotation (Placement(transformation(origin = {110, -80}, extent = {{-7, -7}, {7, 7}})));
equation
  degraded_nav_active = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 1 else 0;
  battery_low_active = if voltage_margin < battery_low_threshold then 1 else if time >= battery_low_start_s and time <= battery_low_end_s then 1 else 0;
  offboard_loss_active = if time >= offboard_loss_start_s and time <= offboard_loss_end_s then 1 else 0;
  mission_failure_active = if time >= mission_failure_start_s and time <= mission_failure_end_s then 1 else 0;
  geofence_breach_active = if time >= geofence_breach_start_s and time <= geofence_breach_end_s then 1 else 0;
  obstacle_avoid_active = 0;
  estimator_quality = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 0.45 else 1;
  estimator_mode = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 2 else 1;
  flight_mode = if geofence_breach_active > 0.5 then 6 else if mission_failure_active > 0.5 then 6 else if offboard_loss_active > 0.5 then 6 else if battery_low_active > 0.5 then 6 else if degraded_nav_active > 0.5 then 6 else if time < takeoff_time_s then 3 else 5;
  active_setpoint_source = if geofence_breach_active > 0.5 then 94 else if mission_failure_active > 0.5 then 93 else if offboard_loss_active > 0.5 then 92 else if battery_low_active > 0.5 then 91 else if degraded_nav_active > 0.5 then 90 else if time < takeoff_time_s then 30 else 40;
  safety_status = if geofence_breach_active > 0.5 then 7 else if mission_failure_active > 0.5 then 6 else if offboard_loss_active > 0.5 then 5 else if battery_low_active > 0.5 then 4 else if degraded_nav_active > 0.5 then 3 else 0;
  event_code = if geofence_breach_active > 0.5 then 64 else if mission_failure_active > 0.5 then 63 else if offboard_loss_active > 0.5 then 62 else if battery_low_active > 0.5 then 61 else if degraded_nav_active > 0.5 then 60 else if time < takeoff_time_s then 30 else 50;
  annotation (
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {120, 0, 0}, fillColor = {255, 245, 245}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 18}, extent = {{-95, 25}, {95, -25}}, textString = "System", textColor = {120, 0, 0}),
      Text(origin = {0, -38}, extent = {{-95, 25}, {95, -25}}, textString = "Supervisor", textColor = {120, 0, 0})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end SystemSupervisorModule;