within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksDynamicReference
  "Dynamic OpenBlocks reference that reads from MAT file at simulation time"

  parameter String matFilePath = "C:/Users/HP/Desktop/MoSim/Results/planning/three_uav_open_blocks_mworks_20260720/mat/uav1_reference.mat"
    "Absolute path to MAT file containing planning results";
  parameter String tableName = "uav1_ref"
    "Table name in MAT file";

  Modelica.Blocks.Sources.CombiTimeTable referenceTable(
    tableOnFile = true,
    tableName = tableName,
    fileName = matFilePath,
    columns = {2, 3, 4, 5},
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint,
    verboseRead = false)
    "Read [time, x_ref, y_ref, z_ref, yaw_ref] from MAT file";

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position [x, y, z] in meters"
    annotation(Placement(transformation(origin = {100, 60}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference velocity [vx, vy, vz] in m/s (numerical derivative)"
    annotation(Placement(transformation(origin = {100, 20}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference acceleration [ax, ay, az] in m/s^2 (numerical derivative)"
    annotation(Placement(transformation(origin = {100, -20}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput yaw_command
    "Reference yaw angle in radians"
    annotation(Placement(transformation(origin = {100, -60}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Continuous.Der velocityX "Velocity = d(position)/dt";
  Modelica.Blocks.Continuous.Der velocityY;
  Modelica.Blocks.Continuous.Der velocityZ;
  Modelica.Blocks.Continuous.Der accelerationX "Acceleration = d(velocity)/dt";
  Modelica.Blocks.Continuous.Der accelerationY;
  Modelica.Blocks.Continuous.Der accelerationZ;

equation
  // Position output directly from table
  position_command[1] = referenceTable.y[1];
  position_command[2] = referenceTable.y[2];
  position_command[3] = referenceTable.y[3];
  yaw_command = referenceTable.y[4];

  // Velocity via numerical derivative
  connect(referenceTable.y[1], velocityX.u);
  connect(referenceTable.y[2], velocityY.u);
  connect(referenceTable.y[3], velocityZ.u);
  velocity_command[1] = velocityX.y;
  velocity_command[2] = velocityY.y;
  velocity_command[3] = velocityZ.y;

  // Acceleration via second derivative
  connect(velocityX.y, accelerationX.u);
  connect(velocityY.y, accelerationY.u);
  connect(velocityZ.y, accelerationZ.u);
  acceleration_command[1] = accelerationX.y;
  acceleration_command[2] = accelerationY.y;
  acceleration_command[3] = accelerationZ.y;

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 127, 255}, fillColor = {230, 245, 255}, fillPattern = FillPattern.Solid),
      Line(points = {{-80, -20}, {-40, 40}, {0, 10}, {40, 60}, {80, 30}}, color = {0, 127, 255}, thickness = 1.5, smooth = Smooth.Bezier),
      Polygon(points = {{80, 30}, {70, 35}, {70, 25}, {80, 30}}, lineColor = {0, 127, 255}, fillColor = {0, 127, 255}, fillPattern = FillPattern.Solid),
      Text(extent = {{-90, -50}, {90, -80}}, textString = "Dynamic MAT", textColor = {0, 127, 255}),
      Ellipse(extent = {{-8, 18}, {8, 2}}, lineColor = {255, 127, 0}, fillColor = {255, 127, 0}, fillPattern = FillPattern.Solid)}),
    Diagram(coordinateSystem(extent = {{-120, -100}, {120, 100}})));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end OpenBlocksDynamicReference;
