within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksUav3DynamicReference
  "UAV3 dynamic reference that reads from MAT file at simulation time"

  parameter String csvFilePath = "C:/Users/HP/Desktop/MoSim/Results/planning/three_uav_open_blocks_mworks_20260720/raw/uav3_reference.csv";

  Modelica.Blocks.Sources.CombiTimeTable referenceTable(
    tableOnFile = true,
    tableName = "NoName",
    fileName = csvFilePath,
    columns = {2, 3, 4, 14},
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint,
    verboseRead = true);

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    annotation(Placement(transformation(origin = {100, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    annotation(Placement(transformation(origin = {100, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    annotation(Placement(transformation(origin = {100, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_command
    annotation(Placement(transformation(origin = {100, -60}, extent = {{-10, -10}, {10, 10}})));

equation
  position_command[1] = referenceTable.y[1];
  position_command[2] = referenceTable.y[2];
  position_command[3] = referenceTable.y[3];
  yaw_command = referenceTable.y[4];

  // Velocity and acceleration set to zero (controller uses position feedback only)
  velocity_command = {0, 0, 0};
  acceleration_command = {0, 0, 0};

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 127, 255}, fillColor = {230, 245, 255}, fillPattern = FillPattern.Solid),
      Line(points = {{-80, -20}, {-40, 40}, {0, 10}, {40, 60}, {80, 30}}, color = {0, 127, 255}, thickness = 1.5, smooth = Smooth.Bezier),
      Text(extent = {{-90, -50}, {90, -80}}, textString = "UAV3 Dynamic", textColor = {0, 127, 255})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end OpenBlocksUav3DynamicReference;
