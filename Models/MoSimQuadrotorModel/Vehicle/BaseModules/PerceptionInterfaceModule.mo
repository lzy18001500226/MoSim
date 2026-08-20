within MoSimQuadrotorModel.Vehicle.BaseModules;
block PerceptionInterfaceModule
  "Top-level perception interface: GPS/GNSS and Mid360 local-map data"
  parameter Real gps_dropout_start_s = 1e9;
  parameter Real gps_dropout_end_s = 1e9;
  parameter Real mid360_dropout_start_s = 1e9;
  parameter Real mid360_dropout_end_s = 1e9;
  parameter Real nominal_obstacle_margin_m = 5.0;
  Modelica.Blocks.Interfaces.RealInput position_raw[3] 
    annotation (Placement(transformation(origin = {-110, 0}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput gps_position[3] 
    annotation (Placement(transformation(origin = {110, 60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput local_position[3] 
    annotation (Placement(transformation(origin = {110, 20}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput obstacle_margin 
    annotation (Placement(transformation(origin = {110, -20}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput health 
    annotation (Placement(transformation(origin = {110, -55}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput gps_valid 
    annotation (Placement(transformation(origin = {110, -75}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput mid360_valid 
    annotation (Placement(transformation(origin = {110, -95}, extent = {{-8, -8}, {8, 8}})));
equation
  gps_position = position_raw;
  local_position = position_raw;
  gps_valid = if time >= gps_dropout_start_s and time <= gps_dropout_end_s then 0 else 1;
  mid360_valid = if time >= mid360_dropout_start_s and time <= mid360_dropout_end_s then 0 else 1;
  obstacle_margin = if mid360_valid > 0.5 then nominal_obstacle_margin_m else 0.2;
  health = 0.5 * gps_valid + 0.5 * mid360_valid;
  annotation (
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 100, 150}, fillColor = {242, 252, 255}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {-58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/GPS.png"),
      Bitmap(origin = {58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/MId360.png"),
      Text(origin = {0, -78}, extent = {{-100, 14}, {100, -14}}, textString = "GPS + Mid360", textColor = {0, 100, 150})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end PerceptionInterfaceModule;