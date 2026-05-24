model MatrixInverse "矩阵求逆"
  extends USV.Utilities.Icons.Model;
  parameter Integer M1 = 2 "Mat矩阵的第一维数";
  parameter Integer M2 = 2 "Mat矩阵的第二维数";
  parameter Integer I1 = 2 "Inv矩阵的第一维数";
  parameter Integer I2 = 2 "Inv矩阵的第二维数";
  Modelica.Blocks.Interfaces.RealInput Mat[M1,M2] 
    annotation (Placement(transformation(origin = {-110.0, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Interfaces.RealOutput Inv[I1,I2] 
    annotation (Placement(transformation(origin = {110.0, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  Inv = Modelica.Math.Matrices.inv(Mat);
  annotation (
    Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      preserveAspectRatio = false, 
      grid = {2.0, 2.0}), graphics = {graphics()}), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
      lineColor = {128, 128, 128}, 
      extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      radius = 25.0), Text(origin = {-20.0, -10.0}, 
      lineColor = {102, 102, 102}, 
      extent = {{-50.0, 60.0}, {50.0, -60.0}}, 
      textString = "M", 
      textStyle = {TextStyle.None}, 
      textColor = {102, 102, 102}), Text(origin = {48.0, 42.0}, 
      lineColor = {102, 102, 102}, 
      extent = {{-40.0, 40.0}, {40.0, -40.0}}, 
      textString = "-1", 
      textStyle = {TextStyle.None}, 
      textColor = {102, 102, 102})}), 
    __MWorks(PortArrangement(Left(Mat), Right(Inv))));
end MatrixInverse;