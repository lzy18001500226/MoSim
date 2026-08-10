within MoSimQuadrotorModel.Control.Adapters;
model OfficialPidSysblockRotorAdapter
  "Modelica-only PlantBridge for the native Official PID Sysblock runner"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;

  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidSysblockRunner 
    controller 
    annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-80, -120}, {80, 120}})),
      __MWORKS(SECInstance = true));

equation
  connect(position_ref[1], controller.x_ref) 
    annotation(Line(points = {{-100, 90}, {-80, 90}}, color = {0, 0, 127}));
  connect(position_ref[2], controller.y_ref) 
    annotation(Line(points = {{-100, 67.5}, {-80, 67.5}}, color = {0, 0, 127}));
  connect(position_ref[3], controller.z_ref) 
    annotation(Line(points = {{-100, 45}, {-80, 45}}, color = {0, 0, 127}));
  connect(position_mea[1], controller.x_mea) 
    annotation(Line(points = {{-100, 22.5}, {-80, 22.5}}, color = {0, 100, 150}));
  connect(position_mea[2], controller.y_mea) 
    annotation(Line(points = {{-100, 0}, {-80, 0}}, color = {0, 100, 150}));
  connect(position_mea[3], controller.z_mea) 
    annotation(Line(points = {{-100, -22.5}, {-80, -22.5}}, color = {0, 100, 150}));
  connect(attitude_mea[1], controller.roll_mea) 
    annotation(Line(points = {{-100, -45}, {-80, -45}}, color = {0, 100, 150}));
  connect(attitude_mea[2], controller.pitch_mea) 
    annotation(Line(points = {{-100, -67.5}, {-80, -67.5}}, color = {0, 100, 150}));
  connect(attitude_mea[3], controller.yaw_mea) 
    annotation(Line(points = {{-100, -90}, {-80, -90}}, color = {0, 100, 150}));
  connect(controller.rotor_command_1, rotor_command[1]) 
    annotation(Line(points = {{80, 75}, {100, 75}}, color = {0, 0, 127}));
  connect(controller.rotor_command_2, rotor_command[2]) 
    annotation(Line(points = {{80, 25}, {100, 25}}, color = {0, 0, 127}));
  connect(controller.rotor_command_3, rotor_command[3]) 
    annotation(Line(points = {{80, -25}, {100, -25}}, color = {0, 0, 127}));
  connect(controller.rotor_command_4, rotor_command[4]) 
    annotation(Line(points = {{80, -75}, {100, -75}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-140, -160}, {140, 160}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 130, 0},
        fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
      Rectangle(extent = {{-82, 58}, {82, -58}}, lineColor = {0, 100, 150},
        fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 28}, extent = {{-88, 18}, {88, -18}},
        textString = "Official PID", textColor = {0, 130, 0}),
      Text(origin = {0, -26}, extent = {{-88, 16}, {88, -16}},
        textString = "SYSBLOCK", textColor = {0, 100, 150})}),
    __MWORKS(version = "26.3.0"));
end OfficialPidSysblockRotorAdapter;