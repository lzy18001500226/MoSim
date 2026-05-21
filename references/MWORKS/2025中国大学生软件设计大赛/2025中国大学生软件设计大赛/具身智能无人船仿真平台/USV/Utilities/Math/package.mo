package Math "数学运算"
  model MatrixDivision "矩阵除法A/B"
    extends USV.Utilities.Icons.Model;

    parameter Integer A1 = 2 "矩阵A的第一维数";
    parameter Integer A2 = 1 "矩阵A的第二维数";
    parameter Integer B1 = 2 "矩阵B的第一维数";
    parameter Integer B2 = 2 "矩阵B的第二维数";
    // 输入矩阵 A 和 B
    Modelica.Blocks.Interfaces.RealInput A[A1,A2] "Matrix A" 
      annotation(Placement(transformation(origin = {-120, 50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput B[B1,B2] "Matrix B" 
      annotation(Placement(transformation(origin = {-120, -50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    // 输出矩阵 C
    Modelica.Blocks.Interfaces.RealOutput C[size(B, 1),size(A, 2)] "Result of A / B" 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    MatrixInverse matrixInverse 
      annotation (Placement(transformation(origin={-60,-50}, 
  extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2}),graphics = {Text(origin={0,5}, 
  lineColor={0,0,0}, 
  extent={{-50,35},{50,-35}}, 
  textString="A/B", 
  textStyle={TextStyle.None}, 
  textColor={0,0,0}, 
  horizontalAlignment=LinePattern.None)}));
    initial equation
    // 检查矩阵 B 是否可逆
    assert(size(A, 1) == size(B, 1), "Matrix A and B must have the same number of rows.");
    assert(size(B, 1) == size(B, 2), "Matrix B must be square.");
  equation
    // 执行矩阵除法 A / B 通过乘以 B 的逆
    C = matrixInverse.Inv * A;
    connect(B, matrixInverse.Mat) 
    annotation(Line(origin={-96,-50}, 
    points={{-24,0},{24.2,0}}, 
    color={0,0,127}));

  end MatrixDivision;
  model MatrixMultiply "矩阵乘法A*B"
    extends USV.Utilities.Icons.Model;

    parameter Integer A1 = 3 "矩阵A的第一维数";
    parameter Integer A2 = 3 "矩阵A的第二维数";
    parameter Integer B1 = 3 "矩阵B的第一维数";
    parameter Integer B2 = 1 "矩阵B的第二维数";
    // 输入矩阵 A 和 B
    Modelica.Blocks.Interfaces.RealInput A[A1,A2] "Matrix A" 
      annotation(Placement(transformation(origin = {-120, 50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput B[B1,B2] "Matrix B" 
      annotation(Placement(transformation(origin = {-120, -50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    // 输出矩阵 C
    Modelica.Blocks.Interfaces.RealOutput C[size(A, 1),size(B, 2)] "Result of A * B" 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2}),graphics = {Text(origin={5,0}, 
    lineColor={0,0,0}, 
    extent={{-55,40},{55,-40}}, 
    textString="A*B", 
    textStyle={TextStyle.None}, 
    textColor={0,0,0}, 
    horizontalAlignment=LinePattern.None)}));

  equation
    C = A * B;
  end MatrixMultiply;
  model MatrixAdd "矩阵加法A+B"
    extends USV.Utilities.Icons.Model;
    parameter Integer A1 = 3 "矩阵的第一维数";
    parameter Integer A2 = 3 "矩阵的第二维数";
    // 输入矩阵 A 和 B
    Modelica.Blocks.Interfaces.RealInput A[A1,A2] "Matrix A" 
      annotation(Placement(transformation(origin = {-120, 50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput B[A1,A2] "Matrix B" 
      annotation(Placement(transformation(origin = {-120, -50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    // 输出矩阵 C
    Modelica.Blocks.Interfaces.RealOutput C[A1,A2] "Result of A + B" 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2}),graphics = {Text(origin={5,2}, 
    lineColor={0,0,0}, 
    extent={{-55,42},{55,-42}}, 
    textString="A+B", 
    textStyle={TextStyle.None}, 
    textColor={0,0,0}, 
    horizontalAlignment=LinePattern.None)}));
  equation
    C = A + B;
  end MatrixAdd;
  model Signed_Square_Root "带符号的平方根"
  extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput u 
      annotation (Placement(transformation(origin={-120,0}, 
  extent={{-20,-20},{20,20}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput y 
      annotation (Placement(transformation(origin={110,0}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={0,0})));
    annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2}),graphics = {Text(origin={0,5}, 
  lineColor={0,0,0}, 
  extent={{-40,45},{40,-45}}, 
  textString="±sqrt", 
  textStyle={TextStyle.None}, 
  textColor={0,0,0}, 
  horizontalAlignment=LinePattern.None)}));
  equation
    y = noEvent(if u >= 0 then sqrt(u) else -sqrt(abs(u)));
  end Signed_Square_Root;
  model power "指数幂"
  extends USV.Utilities.Icons.Model;
    parameter Real n = 2 "幂指数";
    Modelica.Blocks.Interfaces.RealInput u 
      annotation (Placement(transformation(origin={-120,0}, 
  extent={{-20,-20},{20,20}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput y 
      annotation (Placement(transformation(origin={110,0}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={0,0})));
    annotation(Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2}),graphics = {Text(origin={5,-5}, 
    lineColor={0,0,0}, 
    extent={{-55,35},{55,-35}}, 
    textString="u^n", 
    textStyle={TextStyle.None}, 
    textColor={0,0,0}, 
    horizontalAlignment=LinePattern.None)}));
  equation
    y = u ^ n;
  end power;
end Math;