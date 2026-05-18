model caculate
  extends USV.Utilities.Icons.Model;
  Subsystem subsystem 
    annotation(Placement(transformation(origin = {39.5486, -40.5456}, 
    extent = {{-10, -10}, {10, 10}})));
  Subsystem5 subsystem5_1 
    annotation(Placement(transformation(origin = {-66.8009, 45.8635}, 
    extent = {{-10, -10}, {10, 10}})));
  USV.Utilities.Math.MatrixMultiply matrixMultiply 
    annotation(Placement(transformation(origin = {-12.0123, 40.9385}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput V_local[3] 
    "船速" annotation(Placement(transformation(origin = {-109.647, 0.0262381}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Continuous.Integrator integrator[3] 
    annotation(Placement(transformation(origin = {29.8934, 40.4853}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Discrete.UnitDelay unitDelay[3](samplePeriod = 0.001) 
    annotation(Placement(transformation(origin = {62.8657, 40.8022}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput n_global[3] 
    annotation(Placement(transformation(origin = {110.338, 40.546}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput V_local1[3] 
    annotation(Placement(transformation(origin = {110.118, -40.41}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput disturbX "X方向扰动" 
    annotation(Placement(transformation(origin = {-110.796, -79.7513}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput disturbY "Y方向扰动" 
    annotation(Placement(transformation(origin = {-111.063, 79.4837}, 
    extent = {{-10, -10}, {10, 10}})));
  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={1,0.0262381}, 
lineColor={0,0,0}, 
extent={{-53,38},{53,-38}}, 
textString="Calculate", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
equation
  connect(matrixMultiply.A, subsystem5_1.Jn) 
    annotation(Line(origin = {39.6231, 34.4688}, 
    points = {{-63.6354, 11.4697}, {-95.375, 11.4697}, {-95.375, 11.3247}}, 
    color = {0, 0, 127}));
  connect(matrixMultiply.B[:,1], V_local) 
    annotation(Line(origin = {-43, 17}, 
    points = {{18.9877, 18.9385}, {3.93914, 18.9385}, {3.93914, -16.9738}, {-66.647, -16.9738}}, 
    color = {0, 0, 127}));
  connect(subsystem.V_local, V_local) 
    annotation(Line(origin = {-57, -19}, 
    points = {{85.4841, -21.5456}, {17.9221, -21.5456}, {17.9221, 19.0262381}, {-52.647, 19.0262381}}, 
    color = {0, 0, 127}));
  connect(matrixMultiply.C[:,1], integrator.u) 
    annotation(Line(origin = {8.43286, 40.3955}, 
    points = {{-9.4452, 0.543}, {9.4605, 0.543}, {9.4605, 0.0898}}, 
    color = {0, 0, 127}));
  connect(unitDelay.u, integrator.y) 
    annotation(Line(origin = {45.8433, 40.3955}, 
    points = {{5.02237, 0.406721}, {-4.94994, 0.406721}, {-4.94994, 0.0898}}, 
    color = {0, 0, 127}));
  connect(unitDelay.y, subsystem5_1.psi) 
    annotation(Line(origin = {7, 56}, 
    points = {{66.8657, -15.1978}, {74, -15.1978}, {74, 13.8171}, {-96.4627, 13.8171}, {-96.4627, -10.1638}, {-84.8781, -10.1638}}, 
    color = {0, 0, 127}));
  connect(unitDelay.y, n_global) 
    annotation(Line(origin = {92, 19}, 
    points = {{-18.1343, 21.8022}, {18.3383, 21.8022}, {18.3383, 21.546}}, 
    color = {0, 0, 127}));
  connect(subsystem.V_local1, V_local1) 
    annotation(Line(origin = {81, -39}, 
    points = {{-30.4377, -1.54516}, {29.1176, -1.54516}, {29.1176, -1.41003}}, 
    color = {0, 0, 127}));
  connect(subsystem.disturbX, disturbX) 
    annotation(Line(origin = {-38, -46}, 
    points = {{66.5067, 14.43347}, {-1.07278, 14.43347}, {-1.07278, -33.7513}, {-72.7959, -33.7513}}, 
    color = {0, 0, 127}));
  connect(subsystem.disturbY, disturbY) 
    annotation(Line(origin = {-39, 15}, 
    points = {{67.5439, -64.47038}, {-0.08504, -64.47038}, {-0.08504, 64.4837}, {-72.0627, 64.4837}}, 
    color = {0, 0, 127}));

end caculate;