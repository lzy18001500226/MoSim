within MoSimQuadrotorModel.Vehicle.BaseModules;
block V6XFlightControllerModule
  "Top-level V6X flight-controller interface"
  parameter Real estimator_position_T = 0.08;
  parameter Real estimator_attitude_T = 0.03;
  parameter Real estimator_motor_T = 0.05;
  Modelica.Blocks.Interfaces.RealInput gps_position[3] 
    annotation (Placement(transformation(origin = {110, 65}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealInput attitude_raw[3] 
    annotation (Placement(transformation(origin = {110, 25}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealInput motor_speed_raw[4] 
    annotation (Placement(transformation(origin = {110, -25}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealInput gps_valid 
    annotation (Placement(transformation(origin = {110, -75}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput position_est[3] 
    annotation (Placement(transformation(origin = {-110, 65}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput attitude_est[3] 
    annotation (Placement(transformation(origin = {-110, 30}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput motor_speed_est[4] 
    annotation (Placement(transformation(origin = {-110, -5}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput health 
    annotation (Placement(transformation(origin = {-110, -35}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput estimator_quality 
    annotation (Placement(transformation(origin = {-110, -65}, extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Interfaces.RealOutput estimator_mode 
    annotation (Placement(transformation(origin = {-110, -90}, extent = {{-7, -7}, {7, 7}})));
equation
  position_est = gps_position;
  attitude_est = attitude_raw;
  motor_speed_est = motor_speed_raw;
  estimator_quality = if gps_valid > 0.5 then 1 else 0.45;
  estimator_mode = if gps_valid > 0.5 then 1 else 2;
  health = estimator_quality;
  annotation (
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {100, 70, 20}, fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {0, 14}, extent = {{-96, -54.154}, {96, 54.154}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/V6X.png"),
      Text(origin = {0, -78}, extent = {{-95, 14}, {95, -14}}, textString = "V6X", textColor = {100, 70, 20})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end V6XFlightControllerModule;