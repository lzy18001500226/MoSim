package Components "组件"
  model Control_Allocation
    extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput tau[2] 
      annotation (Placement(transformation(origin={-120,0}, 
  extent={{-20,-20},{20,20}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput n_abs_n[2] 
      annotation (Placement(transformation(origin={110,0}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Sources.Constant Thrust_configuration_matrix[2,2](k={{1,1},{0.395,-0.395}}) 
      annotation (Placement(transformation(origin={-78,40}, 
  extent={{-10,-10},{10,10}})));
    Utilities.Math.MatrixDivision matrixDivision 
      annotation (Placement(transformation(origin={-38,5}, 
  extent={{-10,10},{10,-10}})));
    Modelica.Blocks.Math.Gain gain[2](k=1/0.011) 
      annotation (Placement(transformation(origin={10,5}, 
  extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-3,-1}, 
lineColor={0,0,0}, 
extent={{-43,39},{43,-39}}, 
textString="C_A", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
  equation
    connect(tau, matrixDivision.A[:,1]) 
    annotation(Line(origin={-66,0}, 
  points={{-54,0},{16,0}}, 
  color={0,0,127}));
    connect(Thrust_configuration_matrix.y, matrixDivision.B) 
    annotation(Line(origin={-68,-34}, 
  points={{1,74},{8,74},{8,44},{18,44}}, 
  color={0,0,127}));
    connect(matrixDivision.C[:,1], gain.u) 
    annotation(Line(origin={-14,5}, 
    points={{-13,0},{12,0}}, 
    color={0,0,127}));
    connect(gain.y, n_abs_n) 
    annotation(Line(origin={66,3}, 
    points={{-45,2},{-22,2},{-22,-3},{44,-3}}, 
    color={0,0,127}));
    end Control_Allocation;
  model Thrust
  extends USV.Utilities.Icons.Model;
    parameter Real g = 9.8;
    parameter Real k_pos = 0.02216/2;
    parameter Real k_neg = 0.02216/2;
    Modelica.Blocks.Interfaces.RealInput L 
      annotation (Placement(transformation(origin={-260,80}, 
  extent={{-20,-20},{20,20}}), 
  iconTransformation(origin={-120,50}, 
  extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealOutput Thrust 
      annotation (Placement(transformation(origin={230,80}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={110,50}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Interfaces.RealInput R 
      annotation (Placement(transformation(origin={-260,-80}, 
  extent={{-20,-20},{20,20}}), 
  iconTransformation(origin={-120,-50}, 
  extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealOutput Thrust1 
      annotation (Placement(transformation(origin={230,-80}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={110,-50}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Continuous.TransferFunction transferFunction(a={1, 1}) 
      annotation (Placement(transformation(origin={-76,27.6666}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Continuous.TransferFunction transferFunction1(a={1, 1}) 
      annotation (Placement(transformation(origin={-76,-28}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const(k=0.5*24.4) 
      annotation (Placement(transformation(origin={-196,123.8888}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.RealExpression realExpression(y=g) 
      annotation (Placement(transformation(origin={-196,96}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.RealExpression realExpression1(y=k_pos) 
      annotation (Placement(transformation(origin={-196,68.111}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Sqrt n_max 
      annotation (Placement(transformation(origin={-126,96}, 
  extent={{-10,-10},{10,10}})));
    SubSystem1 subSystem1 annotation(Placement(transformation(origin={-161,96}, 
  extent={{-5,-41.3332},{5,41.3332}})));
    Modelica.Blocks.Sources.Constant const1(k=0.5*24.4) 
      annotation (Placement(transformation(origin={-196,-62.1112}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.RealExpression realExpression2(y=g) 
      annotation (Placement(transformation(origin={-196,-90}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.RealExpression realExpression3(y=k_neg) 
      annotation (Placement(transformation(origin={-196,-117.889}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Sqrt n_max1 
      annotation (Placement(transformation(origin={-126,-90}, 
  extent={{-10,-10},{10,10}})));
    SubSystem2 subSystem2 annotation(Placement(transformation(origin={-161,-90}, 
  extent={{-5,-41.3332},{5,41.3332}})));
    Modelica.Blocks.Math.Gain n_min(k=-2) 
      annotation (Placement(transformation(origin={-86,-90}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Nonlinear.VariableLimiter variableLimiter[2] 
      annotation (Placement(transformation(origin={4,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Routing.Multiplex2 multiplex2_1 
      annotation (Placement(transformation(origin={-86,90}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Routing.Multiplex2 multiplex2_2 
      annotation (Placement(transformation(origin={-46,-84}, 
  extent={{-10,-10},{10,10}})));
    SubSystem3 subSystem3[2](realExpression4(y=0)) annotation(Placement(transformation(origin={84,-2.22045e-16}, 
  extent={{-10,-25},{10,25}})));
    Modelica.Blocks.Sources.RealExpression realExpression4[2](y=k_pos) 
      annotation (Placement(transformation(origin={46,0}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.RealExpression realExpression5[2](y=k_neg) 
      annotation (Placement(transformation(origin={46,-16.6667}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Abs abs1[2] 
      annotation (Placement(transformation(origin={84,-46}, 
  extent={{-10,-10},{10,10}})));
    SubSystem4 subSystem4[2] annotation(Placement(transformation(origin={138,-46}, 
  extent={{-10,-25},{10,25}})));
    annotation(Diagram(coordinateSystem(extent={{-240,-160},{220,160}}, 
  grid={2,2})));
    block SubSystem1
                annotation(__MWorks(PortArrangement(Left(u1,u2,u3), Right(y1),Top()),independentInstance = true));
      Modelica.Blocks.Math.Product product1 
        annotation (Placement(transformation(origin={-24,34}, 
  extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Math.Division division 
        annotation (Placement(transformation(origin={24,-18}, 
  extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
          annotation (Placement(transformation(origin={-46,40}, 
  extent={{-4,-4},{4,4}}), 
  iconTransformation(origin={-101.8,66.6667}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealInput u2 
          annotation (Placement(transformation(origin={-46,28}, 
  extent={{-4,-4},{4,4}}), 
  iconTransformation(origin={-101.8,0}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealInput u3 
          annotation (Placement(transformation(origin={2,-24}, 
  extent={{-4,-4},{4,4}}), 
  iconTransformation(origin={-101.8,-66.6667}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
          annotation (Placement(transformation(origin={45,-18}, 
  extent={{-2,-2},{2,2}}), 
  iconTransformation(origin={101.8,0}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
    equation
      connect(product1.y, division.u1) 
      annotation(Line(origin={16,11}, 
  points={{-29,23},{-16,23},{-16,-23},{-4,-23}}, 
  color={0,0,127}));
      connect(u1, product1.u1) 
        annotation (Line(origin={10,-124}, 
  points={{-56,164},{-46,164}}, 
  color={0,0,0}));
      connect(u2, product1.u2) 
        annotation (Line(origin={10,-124}, 
  points={{-56,152},{-46,152}}, 
  color={0,0,0}));
      connect(u3, division.u2) 
        annotation (Line(origin={10,-124}, 
  points={{-8,100},{2,100}}, 
  color={0,0,0}));
      connect(y1, division.y) 
        annotation (Line(origin={10,-124}, 
  points={{35,106},{25,106}}, 
  color={0,0,0}));
                end SubSystem1;
    block SubSystem2
                annotation(__MWorks(PortArrangement(Left(u1,u2,u3), Right(y1),Top()),independentInstance = true));
      Modelica.Blocks.Math.Product product1 
        annotation (Placement(transformation(origin={-24,20}, 
  extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Math.Division division 
        annotation (Placement(transformation(origin={24,-32}, 
  extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
          annotation (Placement(transformation(origin={-46,26}, 
  extent={{-4,-4},{4,4}}), 
  iconTransformation(origin={-101.8,66.6667}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealInput u2 
          annotation (Placement(transformation(origin={-46,14}, 
  extent={{-4,-4},{4,4}}), 
  iconTransformation(origin={-101.8,0}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealInput u3 
          annotation (Placement(transformation(origin={2,-38}, 
  extent={{-4,-4},{4,4}}), 
  iconTransformation(origin={-101.8,-66.6667}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
          annotation (Placement(transformation(origin={45,-32}, 
  extent={{-2,-2},{2,2}}), 
  iconTransformation(origin={101.8,0}, 
  extent={{-1.8,-1.8},{1.8,1.8}})));
    equation
      connect(product1.y, division.u1) 
      annotation(Line(origin={16,-3}, 
  points={{-29,23},{-16,23},{-16,-23},{-4,-23}}, 
  color={0,0,127}));
      connect(u1, product1.u1) 
        annotation (Line(origin={10,-138}, 
  points={{-56,164},{-46,164}}, 
  color={0,0,0}));
      connect(u2, product1.u2) 
        annotation (Line(origin={10,-138}, 
  points={{-56,152},{-46,152}}, 
  color={0,0,0}));
      connect(u3, division.u2) 
        annotation (Line(origin={10,-138}, 
  points={{-8,100},{2,100}}, 
  color={0,0,0}));
      connect(y1, division.y) 
        annotation (Line(origin={10,-138}, 
  points={{35,106},{25,106}}, 
  color={0,0,0}));
                end SubSystem2;
    block SubSystem3
      annotation(__MWorks(PortArrangement(Left(u1, u2, u3), Right(y1), Top()), independentInstance = true));
      Modelica.Blocks.Sources.RealExpression realExpression4 
        annotation(Placement(transformation(origin={-54,-10}, 
    extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Logical.Greater greater 
        annotation(Placement(transformation(origin={-18,18}, 
    extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Logical.Switch switch1 
        annotation(Placement(transformation(origin={16,18}, 
    extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
        annotation(Placement(transformation(origin={-40,18}, 
    extent={{-4,-4},{4,4}}), 
    iconTransformation(origin={-101.8,66.6667}, 
    extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealInput u2 
        annotation(Placement(transformation(origin={-6,26}, 
    extent={{-4,-4},{4,4}}), 
    iconTransformation(origin={-101.8,0}, 
    extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealInput u3 
        annotation(Placement(transformation(origin={-6,10}, 
    extent={{-4,-4},{4,4}}), 
    iconTransformation(origin={-101.8,-66.6667}, 
    extent={{-1.8,-1.8},{1.8,1.8}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
        annotation(Placement(transformation(origin={37,18}, 
    extent={{-2,-2},{2,2}}), 
    iconTransformation(origin={101.8,0}, 
    extent={{-1.8,-1.8},{1.8,1.8}})));
    equation
      connect(greater.u2, realExpression4.y) 
        annotation(Line(origin={-53,10.3332}, 
    points={{23,-0.3332},{15,-0.3332},{15,-20.3332},{10,-20.3332}}, 
    color={0,0,127}));
      connect(greater.y, switch1.u2) 
        annotation(Line(origin={-9,18.3332}, 
    points={{2,-0.3332},{13,-0.3332}}, 
    color={255,0,255}));
      connect(u1, greater.u1) 
        annotation(Line(origin={-112,18}, 
    points={{72,0},{82,0}}, 
    color={0,0,0}));
      connect(u2, switch1.u1) 
        annotation(Line(origin={-112,18}, 
    points={{106,8},{116,8}}, 
    color={0,0,0}));
      connect(u3, switch1.u3) 
        annotation(Line(origin={-112,18}, 
    points={{106,-8},{116,-8}}, 
    color={0,0,0}));
      connect(y1, switch1.y) 
        annotation(Line(origin={-112,18}, 
    points={{149,0},{139,0}}, 
    color={0,0,0}));
    end SubSystem3;
    block SubSystem4
                annotation(__MWorks(PortArrangement(Left(u1,u2,u3), Right(y1),Top()),independentInstance = true));
      Modelica.Blocks.Math.Product product1 
        annotation (Placement(transformation(origin={138,-28}, 
      extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Math.Product product2 
        annotation (Placement(transformation(origin={174,-52}, 
      extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
          annotation (Placement(transformation(extent = { {112, -26}, {120, -18}})));
      Modelica.Blocks.Interfaces.RealInput u2 
          annotation (Placement(transformation(extent = { {112, -38}, {120, -30}})));
      Modelica.Blocks.Interfaces.RealInput u3 
          annotation (Placement(transformation(extent = { {148, -62}, {156, -54}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
          annotation (Placement(transformation(extent = { {193, -54}, {197, -50}})));
    equation
      connect(product1.y, product2.u1) 
      annotation(Line(origin={152,-44}, 
      points={{-3,16},{6,16},{6,-2},{10,-2}}, 
      color={0,0,127}));
      connect(u1, product1.u1) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
      connect(u2, product1.u2) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
      connect(u3, product2.u2) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
      connect(y1, product2.y) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
                end SubSystem4;
  equation
    connect(L, transferFunction.u) 
    annotation(Line(origin={-94,50}, 
  points={{-166,30},{-126,30},{-126,-22.3334},{6,-22.3334}}, 
  color={0,0,127}));
    connect(R, transferFunction1.u) 
    annotation(Line(origin={-94,-50}, 
  points={{-166,-30},{-126,-30},{-126,22},{6,22}}, 
  color={0,0,127}));
    connect(transferFunction.y, variableLimiter[1].u) 
    annotation(Line(origin={-55,25}, 
  points={{-10,2.6666},{1,2.6666},{1,-25},{47,-25}}, 
  color={0,0,127}));
    connect(transferFunction1.y, variableLimiter[2].u) 
    annotation(Line(origin={-55,-25}, 
  points={{-10,-3},{1,-3},{1,25},{47,25}}, 
  color={0,0,127}));
    connect(const.y, subSystem1.u1) 
    annotation(Line(origin={-165,121.333}, 
  points={{-20,2.5558},{-2.8,2.5558},{-2.8,2.22247}}, 
  color={0,0,127}));
    connect(realExpression.y, subSystem1.u2) 
    annotation(Line(origin={-165,99.333}, 
  points={{-20,-3.333},{-2.8,-3.333}}, 
  color={0,0,127}));
    connect(subSystem1.u3, realExpression1.y) 
    annotation(Line(origin={-145,57.333}, 
  points={{-22.8,11.1115},{-40,11.1115},{-40,10.778}}, 
  color={0,0,127}));
    connect(subSystem1.y1, n_max.u) 
    annotation(Line(origin={-102,63.333}, 
  points={{-52.2,32.667},{-36,32.667}}, 
  color={0,0,127}));
    connect(const1.y, subSystem2.u1) 
    annotation(Line(origin={-165,-64.667}, 
  points={{-20,2.5558},{-2.8,2.5558},{-2.8,2.22247}}, 
  color={0,0,127}));
    connect(realExpression2.y, subSystem2.u2) 
    annotation(Line(origin={-165,-86.667}, 
  points={{-20,-3.333},{-2.8,-3.333}}, 
  color={0,0,127}));
    connect(subSystem2.u3, realExpression3.y) 
    annotation(Line(origin={-145,-128.667}, 
  points={{-22.8,11.1115},{-40,11.1115},{-40,10.778}}, 
  color={0,0,127}));
    connect(subSystem2.y1, n_max1.u) 
    annotation(Line(origin={-102,-122.667}, 
  points={{-52.2,32.667},{-36,32.667}}, 
  color={0,0,127}));
    connect(n_max1.y, n_min.u) 
    annotation(Line(origin={-106,-90.1112}, 
  points={{-9,0.1112},{8,0.1112}}, 
  color={0,0,127}));
    connect(n_max.y, multiplex2_1.u1[1]) 
    annotation(Line(origin={-106,95.6668}, 
  points={{-9,0.3332},{8,0.3332}}, 
  color={0,0,127}));
    connect(multiplex2_1.y, variableLimiter.limit1) 
    annotation(Line(origin={-40,57}, 
  points={{-35,33},{10,33},{10,-49},{32,-49}}, 
  color={0,0,127}));
    connect(n_min.y, multiplex2_2.u1[1]) 
    annotation(Line(origin={-66,-84.1112}, 
  points={{-9,-5.8888},{-4,-5.8888},{-4,6.1112},{8,6.1112}}, 
  color={0,0,127}));
    connect(multiplex2_2.y, variableLimiter.limit2) 
    annotation(Line(origin={-17,-55}, 
  points={{-18,-29},{-13,-29},{-13,47},{9,47}}, 
  color={0,0,127}));
    connect(variableLimiter.y, subSystem3.u1) 
    annotation(Line(origin={42,0}, 
points={{-27,0},{-18,0},{-18,16.6667},{30.2,16.6667}}, 
color={0,0,127}));
    connect(subSystem3.u3, realExpression5.y) 
    annotation(Line(origin={64,-7}, 
  points={{8.2,-9.66667},{-7,-9.66667}}, 
  color={0,0,127}));
    connect(abs1.y, subSystem4.u2) 
    annotation(Line(origin={113,-46}, 
  points={{-18,0},{13.2,0}}, 
  color={0,0,127}));
    connect(abs1.u, variableLimiter.y) 
    annotation(Line(origin={52,-23.6667}, 
  points={{20,-22.3333},{-28,-22.3333},{-28,23.6667},{-37,23.6667}}, 
  color={0,0,127}));
    connect(subSystem3.y1, subSystem4.u1) 
    annotation(Line(origin={111,-15}, 
    points={{-15.2,15},{-1,15},{-1,-14.3333},{15.2,-14.3333}}, 
    color={0,0,127}));
    connect(subSystem4.u3, variableLimiter.y) 
    annotation(Line(origin={77,-31.6667}, 
  points={{49.2,-31},{-53,-31},{-53,31.6667},{-62,31.6667}}, 
  color={0,0,127}));
    connect(subSystem4[1].y1, Thrust) 
    annotation(Line(origin={190,17}, 
    points={{-40.2,-63},{-10,-63},{-10,63},{40,63}}, 
    color={0,0,127}));
    connect(subSystem4[2].y1, Thrust1) 
    annotation(Line(origin={190,-63}, 
    points={{-40.2,17},{-10,17},{-10,-17},{40,-17}}, 
    color={0,0,127}));
    connect(n_max.y, multiplex2_1.u2[1]) 
    annotation(Line(origin={-106,90}, 
    points={{-9,6},{0,6},{0,-6},{8,-6}}, 
    color={0,0,127}));
    connect(n_min.y, multiplex2_2.u2[1]) 
    annotation(Line(origin={-66,-90}, 
    points={{-9,0},{8,0}}, 
    color={0,0,127}));
    connect(subSystem3.u2, realExpression4.y) 
    annotation(Line(origin={65,0}, 
    points={{7.2,-3.95075e-22},{-8,0}}, 
    color={0,0,127}));
    end Thrust;

end Components;