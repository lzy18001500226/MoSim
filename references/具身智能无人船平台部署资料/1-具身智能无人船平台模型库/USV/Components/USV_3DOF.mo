model USV_3DOF "无人船三自由度动力学模型"
  extends USV.Utilities.Icons.Model;
  parameter Real mass = 50;
  parameter Real LCG = 0.45;
  parameter Real rho = 1000;
  parameter Real L = 1.3;
  parameter Real Cd = 0.5;
  parameter Real T = 0.12;
  parameter Real Bhull = 0.21;
  parameter Real Xulinear = 75.55;
  parameter Real Xupoly = -25;
  parameter Real Xuulinear = -70.92;
  parameter Real Xuupoly = 0;
  // parameter Real disturbX = 0;
  // parameter Real disturbY = 0;
  Modelica.Blocks.Interfaces.RealInput surge 
    "推杆" annotation(Placement(transformation(origin={-110.849,57.5598}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
  Modelica.Blocks.Interfaces.RealInput yaw 
    "偏航" annotation(Placement(transformation(origin={-110.849,-52.1963}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
  Modelica.Blocks.Interfaces.RealOutput n_global[3] 
    annotation(Placement(transformation(origin={110,50}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
  Modelica.Blocks.Interfaces.RealOutput V_local[3] 
    annotation(Placement(transformation(origin={110,-50}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
  Control.Control_Allocation control_Allocation 
    annotation (Placement(transformation(origin={-42,55}, 
extent={{-10,-10},{10,10}})));
  Hydrodynamics.Hydrodynamic_Coefficients hydrodynamic_Coefficients 
    annotation (Placement(transformation(origin={40,-53.2}, 
extent={{-32,-33},{32,33}})));
  Dynamic_Equations.Dynamic_Model_Equations dynamic_Model_Equations 
    annotation (Placement(transformation(origin={18,24}, 
extent={{-10,-10},{10,10}})));
  Caculate.caculate caculate1 
    annotation (Placement(transformation(origin={76,16.05163}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y=mass) 
    annotation (Placement(transformation(origin={-78,26.5}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y=LCG) 
    annotation (Placement(transformation(origin={-78,12.85}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression2(y=rho) 
    annotation (Placement(transformation(origin={-78,-0.8}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y=L) 
    annotation (Placement(transformation(origin={-78,-14.45}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression4(y=Cd) 
    annotation (Placement(transformation(origin={-78,-28.1}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression5(y=T) 
    annotation (Placement(transformation(origin={-78,-41.75}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression6(y=Bhull) 
    annotation (Placement(transformation(origin={-78,-55.4}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression7(y=Xulinear) 
    annotation (Placement(transformation(origin={-78,-69.05}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression8(y=Xupoly) 
    annotation (Placement(transformation(origin={-78,-82.7}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression9(y=Xuulinear) 
    annotation (Placement(transformation(origin={-78,-96.35}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression realExpression10(y=Xuupoly) 
    annotation (Placement(transformation(origin={-78,-110}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Logical.Switch switch1 
    annotation (Placement(transformation(origin={-22,-69.7}, 
extent={{-4,-4},{4,4}})));
  Modelica.Blocks.Logical.GreaterThreshold greaterThreshold(threshold=1.2) 
    annotation (Placement(transformation(origin={-44,-69.7}, 
extent={{-4,-4},{4,4}})));
  Modelica.Blocks.Logical.Switch switch2 
    annotation (Placement(transformation(origin={-22,-88.7}, 
extent={{-4,-4},{4,4}})));
  Modelica.Blocks.Logical.GreaterThreshold greaterThreshold1(threshold=1.2) 
    annotation (Placement(transformation(origin={-44,-88.7}, 
extent={{-4,-4},{4,4}})));
  Modelica.Blocks.Interfaces.RealInput disturbY "Y方向扰动" 
    annotation (Placement(transformation(origin={-110.849,-11.7984}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-110.849,-15.6109}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput disturbX "X方向扰动" 
    annotation (Placement(transformation(origin={-110.849,22.9278}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-110.849,20.9744}, 
extent={{-10,-10},{10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={1.84993,-147.991}, 
lineColor={0,0,0}, 
extent={{-60,45},{60,-45}}, 
textString="USV130
3DOF_Dynamic_Model", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Polygon(origin={1.59087,-10.60015}, 
fillColor={255,255,255}, 
lineThickness=1, 
points={{-21,37},{-11,31},{5,21},{21,9},{41,-5},{49,-13},{53,-17},{47,-31},{41,-39},{33,-43},{29,-43},{13,-33},{-5,-21},{-17,-11},{-27,-3},{-47,17},{-51,25},{-53,29},{-53,33},{-51,37},{-47,41},{-41,43},{-37,43},{-27,39}}, 
smooth=Smooth.Bezier), Line(origin={3.59087,1.39985}, 
points={{-11,-3},{-9,-1},{-7,1},{-3,3},{-1,3},{1,3},{3,3},{5,3},{7,3},{11,1}}, 
color={0,128,0}, 
thickness=1, 
arrow={Arrow.None,Arrow.Filled}, 
smooth=Smooth.Bezier), Line(origin={18.5909,27.39985}, 
points={{-12,5},{-8,5},{-6,5},{-2,3},{0,3},{4,1},{6,-1},{8,-1},{10,-3},{12,-5}}, 
color={0,128,0}, 
thickness=1, 
arrow={Arrow.None,Arrow.Filled}, 
smooth=Smooth.Bezier), Line(origin={-8.40913,16.39985}, 
points={{-15,-6},{-13,-4},{-9,0},{-5,2},{-1,4},{3,6},{7,6},{11,6},{13,6},{15,6}}, 
color={0,128,0}, 
thickness=1, 
arrow={Arrow.Filled,Arrow.None}), Rectangle(origin={-5.50084,-4.21115}, 
rotation=-36, 
fillColor={255,255,255}, 
lineThickness=1, 
extent={{-26.7662,9.46363},{26.7662,-9.46363}}, 
radius=5), Rectangle(origin={30.4992,-31.2112}, 
rotation=-36, 
fillColor={255,255,255}, 
lineThickness=1, 
extent={{-11.3254,12.0295},{11.3254,-12.0295}}, 
radius=5), Line(origin={6.59087,32.39985}, 
points={{0,44},{0,-44}}, 
color={0,85,255}, 
thickness=1, 
arrow={Arrow.Filled,Arrow.None}, 
__MWorks_Manhattanize=true), Line(origin={-26.3788,11.39985}, 
points={{-35.0303,25},{32.9697,-23}}, 
color={0,85,255}, 
thickness=1, 
arrow={Arrow.Filled,Arrow.None}), Line(origin={22.5909,8.39985}, 
points={{16,20},{-16,-20}}, 
color={255,0,0}, 
thickness=1, 
arrow={Arrow.Filled,Arrow.None}, 
arrowSize=6), Text(origin={20.5909,34.3998}, 
rotation=-30, 
lineColor={255,0,0}, 
extent={{-12,6},{12,-6}}, 
textString="α0", 
fontSize=9, 
textStyle={TextStyle.None}, 
textColor={255,0,0}), Text(origin={61.5909,42.39985}, 
extent={{-41,6},{41,-6}}, 
textString="Wind or wave direction", 
fontSize=9, 
textStyle={TextStyle.None}), Text(origin={-54.4091,50.39985}, 
extent={{-43,6},{43,-6}}, 
textString="Ship advance direction", 
fontSize=9, 
textStyle={TextStyle.None}), Text(origin={-13.4091,32.39985}, 
rotation=15, 
lineColor={255,0,0}, 
extent={{-12,6},{12,-6}}, 
textString="α01", 
fontSize=9, 
textStyle={TextStyle.None}, 
textColor={255,0,0}), Text(origin={-1.40913,10.39985}, 
rotation=15, 
lineColor={255,0,0}, 
extent={{-12,6},{12,-6}}, 
textString="α01", 
fontSize=9, 
textStyle={TextStyle.None}, 
textColor={255,0,0})}));
equation
  connect(caculate1.n_global, n_global) 
  annotation(Line(origin={96,22}, 
points={{-8.9662,-1.89377},{0,-1.89377},{0,28},{14,28}}, 
color={0,0,127}));
  connect(caculate1.V_local1, V_local) 
  annotation(Line(origin={96,-33}, 
points={{-8.9882,45.01063},{0,45.01063},{0,-17},{14,-17}}, 
color={0,0,127}));
  connect(dynamic_Model_Equations.V_local, caculate1.V_local) 
  annotation(Line(origin={44,7}, 
points={{-15,17},{2,17},{2,9.05425},{21.0353,9.05425}}, 
color={0,0,127}));
  connect(control_Allocation.right, dynamic_Model_Equations.Tstbd) 
  annotation(Line(origin={-12,46}, 
  points={{-19,14},{8,14},{8,-14.5},{18,-14.5}}, 
  color={0,0,127}));
  connect(hydrodynamic_Coefficients.Hydd_Coef, dynamic_Model_Equations.Hydd_Coef) 
  annotation(Line(origin={15,-22}, 
points={{60.2,-31.2},{65.4,-31.2},{65.4,3.8},{-13,3.8},{-13,38.5},{-9,38.5}}, 
color={0,0,127}));
  connect(control_Allocation.left, dynamic_Model_Equations.Tport) 
  annotation(Line(origin={-12,36}, 
  points={{-19,14},{-4,14},{-4,-14.5},{18,-14.5}}, 
  color={0,0,127}));
  connect(realExpression.y, dynamic_Model_Equations.Mass) 
  annotation(Line(origin={-11,28}, 
points={{-56,-1.5},{17,-1.5}}, 
color={0,0,127}));
  connect(surge, control_Allocation.surge) 
  annotation(Line(origin={-87,55}, 
points={{-23.849,2.5598},{33,2.5598},{33,5}}, 
color={0,0,127}));
  connect(yaw, control_Allocation.yaw) 
  annotation(Line(origin={-87,0}, 
points={{-23.849,-52.1963},{-7,-52.1963},{-7,50},{33,50}}, 
color={0,0,127}));
  connect(realExpression.y, hydrodynamic_Coefficients.m) 
  annotation(Line(origin={-53,-2}, 
points={{-14,28.5},{31,28.5},{31,-21.5},{57.8,-21.5}}, 
color={0,0,127}));
  connect(realExpression1.y, hydrodynamic_Coefficients.LCG) 
  annotation(Line(origin={-31,-9}, 
  points={{-36,21},{7,21},{7,-21.1},{35.8,-21.1}}, 
  color={0,0,127}));
  connect(realExpression2.y, hydrodynamic_Coefficients.rho) 
  annotation(Line(origin={-31,-19}, 
  points={{-36,18.2},{5,18.2},{5,-17.7},{35.8,-17.7}}, 
  color={0,0,127}));
  connect(realExpression3.y, hydrodynamic_Coefficients.L) 
  annotation(Line(origin={-31,-29}, 
  points={{-36,14.55},{3,14.55},{3,-14.3},{35.8,-14.3}}, 
  color={0,0,127}));
  connect(realExpression4.y, hydrodynamic_Coefficients.C_d) 
  annotation(Line(origin={-31,-39}, 
  points={{-36,10.9},{1,10.9},{1,-10.9},{35.8,-10.9}}, 
  color={0,0,127}));
  connect(realExpression5.y, hydrodynamic_Coefficients.T) 
  annotation(Line(origin={-31,-49}, 
  points={{-36,7.25},{-1,7.25},{-1,-7.5},{35.8,-7.5}}, 
  color={0,0,127}));
  connect(realExpression6.y, hydrodynamic_Coefficients.B_hull) 
  annotation(Line(origin={-31,-59}, 
  points={{-36,3.6},{-3,3.6},{-3,-4.1},{35.8,-4.1}}, 
  color={0,0,127}));
  connect(caculate1.V_local, hydrodynamic_Coefficients.V_local) 
  annotation(Line(origin={43,-39}, 
  points={{22.0353,55.0543},{3,55.0543},{3,35},{47,35},{47,-55},{-47,-55},{-47,-43.9},{-38.2,-43.9}}, 
  color={0,0,127}));
  connect(switch1.u2, greaterThreshold.y) 
  annotation(Line(origin={-57,-63.7}, 
points={{30.2,-6},{17.4,-6}}, 
color={255,0,255}));
  connect(switch2.u2, greaterThreshold1.y) 
  annotation(Line(origin={-57,-82.7}, 
points={{30.2,-6},{17.4,-6}}, 
color={255,0,255}));
  connect(switch1.y, hydrodynamic_Coefficients.Xu) 
  annotation(Line(origin={-6,-70}, 
  points={{-11.6,0.3},{10.8,0.3}}, 
  color={0,0,127}));
  connect(realExpression7.y, switch1.u1) 
  annotation(Line(origin={-47,-65}, 
  points={{-20,-4.05},{-9,-4.05},{-9,5},{11,5},{11,-1.5},{20.2,-1.5}}, 
  color={0,0,127}));
  connect(realExpression8.y, switch1.u3) 
  annotation(Line(origin={-47,-78}, 
  points={{-20,-4.7},{-9,-4.7},{-9,0},{11,0},{11,5.1},{20.2,5.1}}, 
  color={0,0,127}));
  connect(realExpression9.y, switch2.u1) 
  annotation(Line(origin={-47,-88}, 
  points={{-20,-8.35},{-11,-8.35},{-11,4},{-5,4},{-5,8},{17,8},{17,2.5},{20.2,2.5}}, 
  color={0,0,127}));
  connect(realExpression10.y, switch2.u3) 
  annotation(Line(origin={-47,-101}, 
  points={{-20,-9},{17,-9},{17,9.1},{20.2,9.1}}, 
  color={0,0,127}));
  connect(dynamic_Model_Equations.V_local[1], greaterThreshold.u) 
  annotation(Line(origin={18,-43}, 
  points={{11,67},{28,67},{28,39},{72,39},{72,-51},{-22,-51},{-22,-67},{-72,-67},{-72,-26.7},{-66.8,-26.7}}, 
  color={0,0,127}));
  connect(switch2.y, hydrodynamic_Coefficients.Xuu) 
  annotation(Line(origin={-6,-82}, 
  points={{-11.6,-6.7},{-6,-6.7},{-6,5.7},{10.8,5.7}}, 
  color={0,0,127}));
  connect(dynamic_Model_Equations.V_local[1], greaterThreshold1.u) 
  annotation(Line(origin={18,-43}, 
  points={{11,67},{28,67},{28,39},{72,39},{72,-51},{-22,-51},{-22,-67},{-72,-67},{-72,-45.7},{-66.8,-45.7}}, 
  color={0,0,127}));
  connect(disturbX, caculate1.disturbX) 
  annotation(Line(origin={-28,40}, 
points={{-82.849,-17.0722},{-66.0131,-17.0722},{-66.0131,31.2489},{74.0657,31.2489},{74.0657,-31.9235},{92.9204,-31.9235}}, 
color={0,0,127}));
  connect(disturbY, caculate1.disturbY) 
  annotation(Line(origin={-28,30}, 
points={{-82.849,-41.7984},{-66.069,-41.7984},{-66.069,41.156},{74.1892,41.156},{74.1892,-6},{92.8937,-6}}, 
color={0,0,127}));
  end USV_3DOF;