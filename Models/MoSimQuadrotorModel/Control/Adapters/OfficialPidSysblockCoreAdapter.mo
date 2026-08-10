within MoSimQuadrotorModel.Control.Adapters;
model OfficialPidSysblockCoreAdapter
  "Array-port bridge for the native Official PID Sysblock core"

  Modelica.Blocks.Interfaces.RealInput position_command[3] 
    annotation(Placement(transformation(origin = {-130, 70}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput position[3] 
    annotation(Placement(transformation(origin = {-130, 0}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealInput angle[3] 
    annotation(Placement(transformation(origin = {-130, -70}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput y 
    annotation(Placement(transformation(origin = {130, 75}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput y1 
    annotation(Placement(transformation(origin = {130, 25}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput y2 
    annotation(Placement(transformation(origin = {130, -25}, extent = {{-8, -8}, {8, 8}})));
  Modelica.Blocks.Interfaces.RealOutput y3 
    annotation(Placement(transformation(origin = {130, -75}, extent = {{-8, -8}, {8, 8}})));

  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockCore 
    controller_core 
    annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-75, -100}, {75, 100}})),
      __MWORKS(SECInstance = true, PortLabels(labelType = "PortName")));

equation
  connect(position_command[1], controller_core.x_ref) 
    annotation(Line(points = {{-130, 70}, {-75, 70}}, color = {0, 0, 127}));
  connect(position_command[2], controller_core.y_ref) 
    annotation(Line(points = {{-130, 70}, {-95, 70}, {-95, 45}, {-75, 45}}, color = {0, 0, 127}));
  connect(position_command[3], controller_core.z_ref) 
    annotation(Line(points = {{-130, 70}, {-105, 70}, {-105, 20}, {-75, 20}}, color = {0, 0, 127}));
  connect(position[1], controller_core.x_mea) 
    annotation(Line(points = {{-130, 0}, {-110, 0}, {-110, -5}, {-75, -5}}, color = {0, 100, 150}));
  connect(position[2], controller_core.y_mea) 
    annotation(Line(points = {{-130, 0}, {-105, 0}, {-105, -30}, {-75, -30}}, color = {0, 100, 150}));
  connect(position[3], controller_core.z_mea) 
    annotation(Line(points = {{-130, 0}, {-95, 0}, {-95, -55}, {-75, -55}}, color = {0, 100, 150}));
  connect(angle[1], controller_core.roll_mea) 
    annotation(Line(points = {{-130, -70}, {-105, -70}, {-105, -80}, {-75, -80}}, color = {0, 100, 150}));
  connect(angle[2], controller_core.pitch_mea) 
    annotation(Line(points = {{-130, -70}, {-95, -70}, {-95, -100}, {-75, -100}}, color = {0, 100, 150}));
  connect(angle[3], controller_core.yaw_mea) 
    annotation(Line(points = {{-130, -70}, {-85, -70}, {-85, -120}, {-75, -120}}, color = {0, 100, 150}));
  connect(controller_core.y, y) 
    annotation(Line(points = {{75, 75}, {130, 75}}, color = {0, 0, 127}));
  connect(controller_core.y1, y1) 
    annotation(Line(points = {{75, 25}, {130, 25}}, color = {0, 0, 127}));
  connect(controller_core.y2, y2) 
    annotation(Line(points = {{75, -25}, {130, -25}}, color = {0, 0, 127}));
  connect(controller_core.y3, y3) 
    annotation(Line(points = {{75, -75}, {130, -75}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-150, -150}, {150, 150}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 130, 0},
        fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 0}, extent = {{-88, 20}, {88, -20}},
        textString = "Official PID Sysblock", textColor = {0, 100, 150})}),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockCoreAdapter;