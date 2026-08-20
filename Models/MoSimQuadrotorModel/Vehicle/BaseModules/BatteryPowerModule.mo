within MoSimQuadrotorModel.Vehicle.BaseModules;
block BatteryPowerModule
  "Battery power source abstraction for system-level graphical review"
  parameter Real nominal_voltage = 16.8;
  parameter Real low_voltage = 14.0;
  parameter Real voltage_drop_per_second = 0.002;
  Modelica.Blocks.Interfaces.RealOutput bus_voltage 
    annotation (Placement(transformation(origin = {110, 40}, extent = {{-9, -9}, {9, 9}})));
  Modelica.Blocks.Interfaces.RealOutput power_ok 
    annotation (Placement(transformation(origin = {110, 0}, extent = {{-9, -9}, {9, 9}})));
  Modelica.Blocks.Interfaces.RealOutput voltage_margin 
    annotation (Placement(transformation(origin = {110, -40}, extent = {{-9, -9}, {9, 9}})));
equation
  bus_voltage = max(low_voltage, nominal_voltage - voltage_drop_per_second * time);
  voltage_margin = max(0, (bus_voltage - low_voltage) / (nominal_voltage - low_voltage));
  power_ok = if voltage_margin > 0.05 then 1 else 0;
  annotation (
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {250, 250, 250}, fillPattern = FillPattern.Solid),
      Bitmap(origin = {0, 20}, extent = {{-96, -76.304}, {96, 76.304}}, fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/Battery.png"),
      Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "Battery", textColor = {80, 80, 80})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end BatteryPowerModule;