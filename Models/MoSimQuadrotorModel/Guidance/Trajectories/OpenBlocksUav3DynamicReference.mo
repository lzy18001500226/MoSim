within MoSimQuadrotorModel.Guidance.Trajectories;
model OpenBlocksUav3DynamicReference
  "UAV3 dynamic reference that reads from MAT file at simulation time"

  parameter String matFilePath = "C:/Users/HP/Desktop/MoSim/Results/planning/three_uav_open_blocks_mworks_20260720/mat/uav3_reference.mat";
  parameter String tableName = "uav3_ref";

  Modelica.Blocks.Sources.CombiTimeTable referenceTable(
    tableOnFile = true,
    tableName = tableName,
    fileName = matFilePath,
    columns = {2, 3, 4, 5},
    smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments,
    extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint,
    verboseRead = false);

  Modelica.Blocks.Interfaces.RealOutput position_command[3]
    annotation(Placement(transformation(origin = {100, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput velocity_command[3]
    annotation(Placement(transformation(origin = {100, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput acceleration_command[3]
    annotation(Placement(transformation(origin = {100, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_command
    annotation(Placement(transformation(origin = {100, -60}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Continuous.Der velocityX;
  Modelica.Blocks.Continuous.Der velocityY;
  Modelica.Blocks.Continuous.Der velocityZ;
  Modelica.Blocks.Continuous.Der accelerationX;
  Modelica.Blocks.Continuous.Der accelerationY;
  Modelica.Blocks.Continuous.Der accelerationZ;

equation
  position_command[1] = referenceTable.y[1];
  position_command[2] = referenceTable.y[2];
  position_command[3] = referenceTable.y[3];
  yaw_command = referenceTable.y[4];

  connect(referenceTable.y[1], velocityX.u);
  connect(referenceTable.y[2], velocityY.u);
  connect(referenceTable.y[3], velocityZ.u);
  velocity_command[1] = velocityX.y;
  velocity_command[2] = velocityY.y;
  velocity_command[3] = velocityZ.y;

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
      Text(extent = {{-90, -50}, {90, -80}}, textString = "UAV3 Dynamic", textColor = {0, 127, 255})}));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end OpenBlocksUav3DynamicReference;
