model matricesInverse
  Utilities.Math.MatrixInverse matrixInverse(M1=3,M2=3,I1=3,I2=3) 
    annotation (Placement(transformation(origin = {40, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant Thrust_configuration_matrix[2,2](k={{1,1},{0.395,-0.395}}) 
    annotation (Placement(transformation(origin={-42,58}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant Thrust_configuration_matrix1[3,3](k={{1,2,3},{0,5,6},{0,0,9}}) 
    annotation (Placement(transformation(origin={-42,10}, 
extent={{-10,-10},{10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
equation
  connect(matrixInverse.Mat, Thrust_configuration_matrix1.y) 
  annotation(Line(origin={-1,10}, 
  points={{29.2,0},{-30,0}}, 
  color={0,0,127}));
  end matricesInverse;