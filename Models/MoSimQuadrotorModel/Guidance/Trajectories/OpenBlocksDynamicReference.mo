within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksDynamicReference
  "Dynamic OpenBlocks reference that reads from MAT file at simulation time"

  parameter String csvFilePath = "C:/Users/HP/Desktop/MoSim/Results/planning/three_uav_open_blocks_mworks_20260720/sysplorer/uav1_reference.csv"
    "Absolute path to CSV file containing planning results";

  Modelica.Blocks.Sources.CombiTimeTable referenceTable(
    tableOnFile = true,
    tableName = "tab1",
    fileName = csvFilePath,
    columns = {2, 3, 4, 14},
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint,
    verboseRead = true)
    "Read [time, x_ref, y_ref, z_ref, yaw_ref] from CSV file (columns 2-4, 14)";

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    "Reference position [x, y, z] in meters" 
    annotation(Placement(transformation(origin = {100, 60}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    "Reference velocity [vx, vy, vz] in m/s (zero, controller computes from position error)" 
    annotation(Placement(transformation(origin = {100, 20}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    "Reference acceleration [ax, ay, az] in m/s^2 (zero, no feedforward)" 
    annotation(Placement(transformation(origin = {100, -20}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Interfaces.RealOutput yaw_command
    "Reference yaw angle in radians" 
    annotation(Placement(transformation(origin = {100, -60}, extent = {{-10, -10}, {10, 10}})));

equation
  // Position output directly from table
  position_command[1] = referenceTable.y[1];
  position_command[2] = referenceTable.y[2];
  position_command[3] = referenceTable.y[3];
  yaw_command = referenceTable.y[4];

  // Velocity and acceleration set to zero (controller uses position feedback only)
  // Avoids Sysplorer symbolic differentiation limitation with CombiTimeTable
  velocity_command = {0, 0, 0};
  acceleration_command = {0, 0, 0};

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