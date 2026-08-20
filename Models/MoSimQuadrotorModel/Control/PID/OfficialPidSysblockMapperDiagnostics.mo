within MoSimQuadrotorModel.Control.PID;
model OfficialPidSysblockMapperDiagnostics
  "Telemetry sidecar for the native Official PID Sysblock rotor mapper"

  Modelica.Blocks.Interfaces.RealInput amplitude_1 
    annotation(Placement(
      transformation(origin = {-130, 75}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput amplitude_2 
    annotation(Placement(
      transformation(origin = {-130, 25}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 20}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput amplitude_3 
    annotation(Placement(
      transformation(origin = {-130, -25}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, -20}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput amplitude_4 
    annotation(Placement(
      transformation(origin = {-130, -75}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, -60}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput direct_control_bus[10]
    "[yaw, non-yaw(2:5), mapped(6:9), collective error(10)]" 
    annotation(Placement(
      transformation(origin = {130, 0}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 0}, extent = {{-8, -8}, {8, 8}})));

  Real yaw_amplitude;
  Real non_yaw_amplitude[4];
  Real mapped_amplitude[4];
  Real mapped_collective_amplitude_error;

equation
  yaw_amplitude = (-amplitude_1 + amplitude_2 - amplitude_3 + amplitude_4) / 4;
  non_yaw_amplitude[1] = amplitude_1 + yaw_amplitude;
  non_yaw_amplitude[2] = amplitude_2 - yaw_amplitude;
  non_yaw_amplitude[3] = amplitude_3 + yaw_amplitude;
  non_yaw_amplitude[4] = amplitude_4 - yaw_amplitude;
  mapped_amplitude[1] = non_yaw_amplitude[1] - 0.26666666666666666 * yaw_amplitude;
  mapped_amplitude[2] = non_yaw_amplitude[2] + 0.26666666666666666 * yaw_amplitude;
  mapped_amplitude[3] = non_yaw_amplitude[3] - 0.26666666666666666 * yaw_amplitude;
  mapped_amplitude[4] = non_yaw_amplitude[4] + 0.26666666666666666 * yaw_amplitude;
  mapped_collective_amplitude_error = sum(mapped_amplitude)
    - (amplitude_1 + amplitude_2 + amplitude_3 + amplitude_4);
  direct_control_bus[1] = yaw_amplitude;
  direct_control_bus[2:5] = non_yaw_amplitude;
  direct_control_bus[6:9] = mapped_amplitude;
  direct_control_bus[10] = mapped_collective_amplitude_error;

  annotation(
    Diagram(coordinateSystem(extent = {{-150, -110}, {150, 110}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, 100}, {100, -100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {70, 100, 80},
        fillColor = {245, 250, 245}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 22}, extent = {{-88, 18}, {88, -18}},
        textString = "MAPPER", textColor = {70, 100, 80}),
      Text(origin = {0, -22}, extent = {{-88, 18}, {88, -18}},
        textString = "TELEMETRY", textColor = {70, 100, 80})}),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockMapperDiagnostics;