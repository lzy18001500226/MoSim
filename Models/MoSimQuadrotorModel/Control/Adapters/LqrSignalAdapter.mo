within MoSimQuadrotorModel.Control.Adapters;
model LqrSignalAdapter
  "Signal adapter for LQR-family controllers: passes plant/reference signals to Sysblock core"

  // Input ports (from plant and trajectory)
  Modelica.Blocks.Interfaces.RealInput position_x(unit = "m")
    annotation(Placement(transformation(origin = {-110, 90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput position_y(unit = "m")
    annotation(Placement(transformation(origin = {-110, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput position_z(unit = "m")
    annotation(Placement(transformation(origin = {-110, 50}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealInput velocity_x(unit = "m/s")
    annotation(Placement(transformation(origin = {-110, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput velocity_y(unit = "m/s")
    annotation(Placement(transformation(origin = {-110, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput velocity_z(unit = "m/s")
    annotation(Placement(transformation(origin = {-110, -10}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealInput reference_position_x(unit = "m")
    annotation(Placement(transformation(origin = {-110, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput reference_position_y(unit = "m")
    annotation(Placement(transformation(origin = {-110, -50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput reference_position_z(unit = "m")
    annotation(Placement(transformation(origin = {-110, -70}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealInput reference_velocity_x(unit = "m/s")
    annotation(Placement(transformation(origin = {-110, -90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput reference_velocity_y(unit = "m/s")
    annotation(Placement(transformation(origin = {-110, -110}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput reference_velocity_z(unit = "m/s")
    annotation(Placement(transformation(origin = {-110, -130}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealInput reference_acceleration_x(unit = "m/s2")
    annotation(Placement(transformation(origin = {-110, -150}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput reference_acceleration_y(unit = "m/s2")
    annotation(Placement(transformation(origin = {-110, -170}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput reference_acceleration_z(unit = "m/s2")
    annotation(Placement(transformation(origin = {-110, -190}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealInput dt(unit = "s")
    annotation(Placement(transformation(origin = {-110, -210}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput enable
    annotation(Placement(transformation(origin = {-110, -230}, extent = {{-10, -10}, {10, 10}})));

  // Output ports (to Sysblock core)
  Modelica.Blocks.Interfaces.RealOutput position_x_out(unit = "m")
    annotation(Placement(transformation(origin = {110, 90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput position_y_out(unit = "m")
    annotation(Placement(transformation(origin = {110, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput position_z_out(unit = "m")
    annotation(Placement(transformation(origin = {110, 50}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput velocity_x_out(unit = "m/s")
    annotation(Placement(transformation(origin = {110, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput velocity_y_out(unit = "m/s")
    annotation(Placement(transformation(origin = {110, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput velocity_z_out(unit = "m/s")
    annotation(Placement(transformation(origin = {110, -10}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput reference_position_x_out(unit = "m")
    annotation(Placement(transformation(origin = {110, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput reference_position_y_out(unit = "m")
    annotation(Placement(transformation(origin = {110, -50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput reference_position_z_out(unit = "m")
    annotation(Placement(transformation(origin = {110, -70}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput reference_velocity_x_out(unit = "m/s")
    annotation(Placement(transformation(origin = {110, -90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput reference_velocity_y_out(unit = "m/s")
    annotation(Placement(transformation(origin = {110, -110}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput reference_velocity_z_out(unit = "m/s")
    annotation(Placement(transformation(origin = {110, -130}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput reference_acceleration_x_out(unit = "m/s2")
    annotation(Placement(transformation(origin = {110, -150}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput reference_acceleration_y_out(unit = "m/s2")
    annotation(Placement(transformation(origin = {110, -170}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput reference_acceleration_z_out(unit = "m/s2")
    annotation(Placement(transformation(origin = {110, -190}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput dt_out(unit = "s")
    annotation(Placement(transformation(origin = {110, -210}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput enable_out
    annotation(Placement(transformation(origin = {110, -230}, extent = {{-10, -10}, {10, 10}})));

equation
  // Direct passthrough
  position_x_out = position_x;
  position_y_out = position_y;
  position_z_out = position_z;
  velocity_x_out = velocity_x;
  velocity_y_out = velocity_y;
  velocity_z_out = velocity_z;
  reference_position_x_out = reference_position_x;
  reference_position_y_out = reference_position_y;
  reference_position_z_out = reference_position_z;
  reference_velocity_x_out = reference_velocity_x;
  reference_velocity_y_out = reference_velocity_y;
  reference_velocity_z_out = reference_velocity_z;
  reference_acceleration_x_out = reference_acceleration_x;
  reference_acceleration_y_out = reference_acceleration_y;
  reference_acceleration_z_out = reference_acceleration_z;
  dt_out = dt;
  enable_out = enable;

  annotation(
    Icon(coordinateSystem(preserveAspectRatio = false, extent = {{-100, -240}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -240}}, lineColor = {0, 100, 150}, fillColor = {255, 255, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 20}, extent = {{-80, 20}, {80, -20}}, textString = "LQR Signal", textColor = {0, 100, 150}),
      Text(origin = {0, -20}, extent = {{-80, 20}, {80, -20}}, textString = "Adapter", textColor = {0, 100, 150}),
      Line(points = {{-60, 0}, {60, 0}}, color = {0, 100, 150})}),
    Diagram(coordinateSystem(preserveAspectRatio = false, extent = {{-100, -240}, {100, 100}})));
end LqrSignalAdapter;
