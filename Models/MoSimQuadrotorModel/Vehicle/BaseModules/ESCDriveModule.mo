within MoSimQuadrotorModel.Vehicle.BaseModules;
block ESCDriveModule
  "Electronic speed controller abstraction between control allocation and motors"
  parameter Real nominal_voltage = 16.8;
  parameter Real motor_limit_abs = 80.0;
  Modelica.Blocks.Interfaces.RealInput motor_command_raw[4] 
    annotation (Placement(transformation(origin = {-110, 45}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput bus_voltage 
    annotation (Placement(transformation(origin = {-110, 0}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput power_ok 
    annotation (Placement(transformation(origin = {-110, -45}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput motor_command[4] 
    annotation (Placement(transformation(origin = {110, 35}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput esc_health[4] 
    annotation (Placement(transformation(origin = {110, -20}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput saturation_ratio_est 
    annotation (Placement(transformation(origin = {110, -65}, extent = {{-8, -8}, {8, 8}})));
  Real voltage_scale;
  Real saturated_count;
equation
  voltage_scale = max(0.0, min(1.0, bus_voltage / nominal_voltage));
  saturated_count =
    (if abs(motor_command_raw[1] * voltage_scale) >= motor_limit_abs then 1 else 0) +
    (if abs(motor_command_raw[2] * voltage_scale) >= motor_limit_abs then 1 else 0) +
    (if abs(motor_command_raw[3] * voltage_scale) >= motor_limit_abs then 1 else 0) +
    (if abs(motor_command_raw[4] * voltage_scale) >= motor_limit_abs then 1 else 0);
  for i in 1:4 loop
    motor_command[i] = if power_ok > 0.5 then max(-motor_limit_abs, min(motor_limit_abs, motor_command_raw[i] * voltage_scale)) else 0;
    esc_health[i] = power_ok * voltage_scale;
  end for;
  saturation_ratio_est = saturated_count / 4;
  annotation (
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {70, 70, 120}, fillColor = {246, 246, 255}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {0, 18}, extent = {{-80, -75.649}, {80, 75.649}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/ESC.png"),
      Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "ESC", textColor = {70, 70, 120})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end ESCDriveModule;