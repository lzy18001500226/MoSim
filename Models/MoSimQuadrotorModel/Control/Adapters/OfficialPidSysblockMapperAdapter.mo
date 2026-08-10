within MoSimQuadrotorModel.Control.Adapters;
model OfficialPidSysblockMapperAdapter
  "Array-port bridge for the native Official PID Sysblock rotor mapper"

  Modelica.Blocks.Interfaces.RealInput amplitude_command[4] 
    annotation(Placement(
      transformation(origin = {-130, 0}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {-100, 0}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4] 
    annotation(Placement(
      transformation(origin = {130, 0}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, 43}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput direct_control_bus[10]
    "[yaw, non-yaw(2:5), mapped(6:9), collective error(10)]" 
    annotation(Placement(
      transformation(origin = {130, -80}, extent = {{-8, -8}, {8, 8}}),
      iconTransformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}})));

  Real yaw_amplitude;
  Real non_yaw_amplitude[4];
  Real mapped_amplitude[4];
  Real mapped_collective_amplitude_error;

  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockMapper 
    rotor_mapper 
    annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-75, -100}, {75, 100}})),
      __MWORKS(SECInstance = true, PortLabels(labelType = "PortName")));

equation
  connect(amplitude_command[1], rotor_mapper.amplitude_1) 
    annotation(Line(points = {{-130, 0}, {-75, 70}}, color = {0, 0, 127}));
  connect(amplitude_command[2], rotor_mapper.amplitude_2) 
    annotation(Line(points = {{-130, 0}, {-95, 0}, {-95, 25}, {-75, 25}}, color = {0, 0, 127}));
  connect(amplitude_command[3], rotor_mapper.amplitude_3) 
    annotation(Line(points = {{-130, 0}, {-95, 0}, {-95, -25}, {-75, -25}}, color = {0, 0, 127}));
  connect(amplitude_command[4], rotor_mapper.amplitude_4) 
    annotation(Line(points = {{-130, 0}, {-75, -70}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_1, rotor_command[1]) 
    annotation(Line(points = {{75, 70}, {130, 0}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_2, rotor_command[2]) 
    annotation(Line(points = {{75, 25}, {95, 25}, {95, 0}, {130, 0}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_3, rotor_command[3]) 
    annotation(Line(points = {{75, -25}, {95, -25}, {95, 0}, {130, 0}}, color = {0, 0, 127}));
  connect(rotor_mapper.rotor_command_4, rotor_command[4]) 
    annotation(Line(points = {{75, -70}, {130, 0}}, color = {0, 0, 127}));

  // The native mapper owns the command path. These equations retain the
  // legacy diagnostic bus using the same fixed native mapper constants.
  yaw_amplitude = (-amplitude_command[1] + amplitude_command[2]
    - amplitude_command[3] + amplitude_command[4]) / 4;
  non_yaw_amplitude[1] = amplitude_command[1] + yaw_amplitude;
  non_yaw_amplitude[2] = amplitude_command[2] - yaw_amplitude;
  non_yaw_amplitude[3] = amplitude_command[3] + yaw_amplitude;
  non_yaw_amplitude[4] = amplitude_command[4] - yaw_amplitude;
  mapped_amplitude[1] = non_yaw_amplitude[1] - 0.26666666666666666 * yaw_amplitude;
  mapped_amplitude[2] = non_yaw_amplitude[2] + 0.26666666666666666 * yaw_amplitude;
  mapped_amplitude[3] = non_yaw_amplitude[3] - 0.26666666666666666 * yaw_amplitude;
  mapped_amplitude[4] = non_yaw_amplitude[4] + 0.26666666666666666 * yaw_amplitude;
  mapped_collective_amplitude_error = sum(mapped_amplitude) - sum(amplitude_command);
  direct_control_bus[1] = yaw_amplitude;
  direct_control_bus[2:5] = non_yaw_amplitude;
  direct_control_bus[6:9] = mapped_amplitude;
  direct_control_bus[10] = mapped_collective_amplitude_error;

  annotation(
    Diagram(coordinateSystem(extent = {{-150, -150}, {150, 150}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 130, 0},
        fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 0}, extent = {{-88, 20}, {88, -20}},
        textString = "ROTOR MAP YAW", textColor = {0, 100, 150})}),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockMapperAdapter;