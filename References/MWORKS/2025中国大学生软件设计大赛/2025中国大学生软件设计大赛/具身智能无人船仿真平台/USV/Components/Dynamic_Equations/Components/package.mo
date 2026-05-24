package Components "组件"
  model Tau
    extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput B 
      annotation (Placement(transformation(origin={-120,66.6667}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Tstbd 
      annotation (Placement(transformation(origin={-120,0}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Tport 
      annotation (Placement(transformation(origin={-120,-66.6667}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput T[3] 
      annotation (Placement(transformation(origin={110,0}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Math.Gain gain(k=1) 
      annotation (Placement(transformation(origin={-70,-66.6667}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add(k1=-1) 
      annotation (Placement(transformation(origin={-10,-6}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add1 
      annotation (Placement(transformation(origin={-10,-60.6667}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain1(k=1.78) 
      annotation (Placement(transformation(origin={-70,0}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Product product1 
      annotation (Placement(transformation(origin={-20,60.6667}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain2(k=1/2) 
      annotation (Placement(transformation(origin={30,60.6667}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const(k=0) 
      annotation (Placement(transformation(origin = {30, 0}, extent = {{-10, -10}, {10, 10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-1,-1}, 
lineColor={0,0,0}, 
extent={{-45,39},{45,-39}}, 
textString="Tau", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
  equation
    connect(Tport, gain.u) 
    annotation(Line(origin={-101,-67}, 
    points={{-19,0.3333},{19,0.3333}}, 
    color={0,0,127}));
    connect(gain.y, add1.u2) 
    annotation(Line(origin={-40,-67}, 
    points={{-19,0.3333},{18,0.3333}}, 
    color={0,0,127}));
    connect(Tstbd, gain1.u) 
    annotation(Line(origin={-101,0}, 
    points={{-19,0},{19,0}}, 
    color={0,0,127}));
    connect(gain1.y, add1.u1) 
    annotation(Line(origin={-40,-27}, 
    points={{-19,27},{-14,27},{-14,-27.6667},{18,-27.6667}}, 
    color={0,0,127}));
    connect(gain1.y, add.u1) 
    annotation(Line(origin={-40,0}, 
    points={{-19,0},{18,0}}, 
    color={0,0,127}));
    connect(gain.y, add.u2) 
    annotation(Line(origin={-40,-39}, 
    points={{-19,-27.6667},{-6,-27.6667},{-6,27},{18,27}}, 
    color={0,0,127}));
    connect(B, product1.u1) 
    annotation(Line(origin={-76,67}, 
    points={{-44,-0.3333},{44,-0.3333}}, 
    color={0,0,127}));
    connect(add.y, product1.u2) 
    annotation(Line(origin={-23,24}, 
    points={{24,-30},{33,-30},{33,12},{-33,12},{-33,30.6667},{-9,30.6667}}, 
    color={0,0,127}));
    connect(product1.y, gain2.u) 
    annotation(Line(origin={5,61}, 
    points={{-14,-0.3333},{13,-0.3333}}, 
    color={0,0,127}));
    connect(add1.y, T[1]) 
    annotation(Line(origin={56,-30}, 
    points={{-55,-30.6667},{24,-30.6667},{24,30},{54,30}}, 
    color={0,0,127}));
    connect(const.y, T[2]) 
    annotation(Line(origin={76,0}, 
    points={{-35,0},{34,0}}, 
    color={0,0,127}));
    connect(gain2.y, T[3]) 
    annotation(Line(origin={76,30}, 
    points={{-35,30.6667},{4,30.6667},{4,-30},{34,-30}}, 
    color={0,0,127}));
    end Tau;
  model C
    extends USV.Utilities.Icons.Model;
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2}),graphics = {Text(origin={0,0}, 
  lineColor={0,0,0}, 
  extent={{-30,30},{30,-30}}, 
  textString="C", 
  textStyle={TextStyle.None}, 
  textColor={0,0,0}, 
  horizontalAlignment=LinePattern.None)}));
    Modelica.Blocks.Interfaces.RealInput m 
      annotation (Placement(transformation(origin={-114.2857,80}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={-114.2857,80}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Modelica.Blocks.Interfaces.RealInput X_G 
      annotation (Placement(transformation(origin={-114.2857,40}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={-114.2857,40}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Modelica.Blocks.Interfaces.RealInput Y_G 
      annotation (Placement(transformation(origin={-114.2857,0}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={-114.2857,0}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Modelica.Blocks.Interfaces.RealInput V_Local[3] 
      annotation (Placement(transformation(origin={-114.2857,-80}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={-114.2857,-80}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Modelica.Blocks.Interfaces.RealInput Hydd_Coef[19] 
      annotation (Placement(transformation(origin={-114.2857,-40}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={-114.2857,-40}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Modelica.Blocks.Interfaces.RealOutput Cv[3,3] 
      annotation (Placement(transformation(origin={116,-4.1429}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={110,0}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Product product1 
      annotation (Placement(transformation(origin={-19,77.5714}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Add add 
      annotation (Placement(transformation(origin={-47,66}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Product product2 
      annotation (Placement(transformation(origin={-71,54}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Interfaces.RealOutput CRB[3,3] 
      annotation (Placement(transformation(origin={52,9}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={46,44.2857}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain(k=-1) 
      annotation (Placement(transformation(origin={24,77.5714}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Sources.Constant const(k=0) 
      annotation (Placement(transformation(origin={-6,9}, 
extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Gain gain1(k=-1) 
      annotation (Placement(transformation(origin={24,54}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Product product3 
      annotation (Placement(transformation(origin={-19,54}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Add add1(k2=-1) 
      annotation (Placement(transformation(origin={-47,36.0714}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Product product4 
      annotation (Placement(transformation(origin={-71,41.0714}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Interfaces.RealOutput CA[3,3] 
      annotation (Placement(transformation(origin={52,-27.2858}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={46,-44.2857}, 
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain2(k=2) 
      annotation (Placement(transformation(origin={-9,-9.1429}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Add add2 
      annotation (Placement(transformation(origin={-33,-9.1429}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Product product5 
      annotation (Placement(transformation(origin={-47,9}, 
extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Gain gain3(k=0.5) 
      annotation (Placement(transformation(origin={-64,12}, 
extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Add add3 
      annotation (Placement(transformation(origin={-81,12}, 
extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Product product6 
      annotation (Placement(transformation(origin={-59,-12.1429}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Gain gain4(k=-1) 
      annotation (Placement(transformation(origin={-9,-27.2858}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Product product7 
      annotation (Placement(transformation(origin={-33,-27.2858}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Gain gain5(k=2) 
      annotation (Placement(transformation(origin={-9,-62.2143}, 
  extent={{-5,-5},{5,5}})));
    Modelica.Blocks.Math.Add add4(k1=-1,k2=-1) 
      annotation (Placement(transformation(origin={-33,-62.2143}, 
  extent={{-5,-5},{5,5}})));
    Utilities.Math.MatrixAdd matrixAdd 
      annotation (Placement(transformation(origin={84,-4.1429}, 
  extent={{-10,-10},{10,10}})));
  equation
    connect(m, product1.u1) 
    annotation(Line(origin={-92,81}, 
  points={{-66,-0.4286},{67,-0.4286}}, 
  color={0,0,127}));
    connect(add.y, product1.u2) 
    annotation(Line(origin={-35,63}, 
  points={{-6.5,3},{7,3},{7,11.5714},{10,11.5714}}, 
  color={0,0,127}));
    connect(V_Local[2], add.u1) 
    annotation(Line(origin={-113,-17}, 
points={{-1.2857,-63},{23,-63},{23,86},{60,86}}, 
color={0,0,127}));
    connect(product2.y, add.u2) 
    annotation(Line(origin={-59,54}, 
  points={{-6.5,0},{-1,0},{-1,9},{6,9}}, 
  color={0,0,127}));
    connect(X_G, product2.u1) 
    annotation(Line(origin={-117,42}, 
points={{2.7143,-2},{27,-2},{27,15},{40,15}}, 
color={0,0,127}));
    connect(V_Local[3], product2.u2) 
    annotation(Line(origin={-117,-23}, 
points={{2.7143,-57},{27,-57},{27,74},{40,74}}, 
color={0,0,127}));
    connect(gain.u, product1.y) 
    annotation(Line(origin={-9,78}, 
  points={{27,-0.4286},{-4.5,-0.4286}}, 
  color={0,0,127}));
    connect(gain.y, CRB[1,3]) 
    annotation(Line(origin={31,57}, 
  points={{-1.5,20.5714},{1,20.5714},{1,-48},{21,-48}}, 
  color={0,0,127}));
    connect(product1.y, CRB[3,1]) 
    annotation(Line(origin={20,57}, 
points={{-33.5,20.5714},{-14,20.5714},{-14,-48},{32,-48}}, 
color={0,0,127}));
    connect(const.y, CRB[1,1]) 
    annotation(Line(origin={20,23}, 
points={{-20.5,-14},{32,-14}}, 
color={0,0,127}));
    connect(const.y, CRB[1,2]) 
    annotation(Line(origin={20,23}, 
points={{-20.5,-14},{32,-14}}, 
color={0,0,127}));
    connect(const.y, CRB[2,1]) 
    annotation(Line(origin={20,23}, 
points={{-20.5,-14},{32,-14}}, 
color={0,0,127}));
    connect(const.y, CRB[2,2]) 
    annotation(Line(origin={20,23}, 
points={{-20.5,-14},{32,-14}}, 
color={0,0,127}));
    connect(const.y, CRB[3,3]) 
    annotation(Line(origin={20,23}, 
points={{-20.5,-14},{32,-14}}, 
color={0,0,127}));
    connect(gain1.y, CRB[2,3]) 
    annotation(Line(origin={42,45}, 
  points={{-12.5,9},{-10,9},{-10,-36},{10,-36}}, 
  color={0,0,127}));
    connect(m, product3.u1) 
    annotation(Line(origin={-91,69}, 
    points={{-67,11.5714},{57,11.5714},{57,-12},{66,-12}}, 
    color={0,0,127}));
    connect(add1.y, product3.u2) 
    annotation(Line(origin={-33,46}, 
  points={{-8.5,-9.9286},{-1,-9.9286},{-1,5},{8,5}}, 
  color={0,0,127}));
    connect(product4.y, add1.u1) 
    annotation(Line(origin={-59,41}, 
  points={{-6.5,0.0714},{3,0.0714},{3,-1.9286},{6,-1.9286}}, 
  color={0,0,127}));
    connect(Y_G, product4.u1) 
    annotation(Line(origin={-117,18}, 
points={{2.7143,-18},{27,-18},{27,22},{40,22},{40,26.0714}}, 
color={0,0,127}));
    connect(V_Local[3], product4.u2) 
    annotation(Line(origin={-117,-30}, 
points={{2.7143,-50},{27,-50},{27,68.0714},{40,68.0714}}, 
color={0,0,127}));
    connect(V_Local[1], add1.u2) 
    annotation(Line(origin={-105,-31}, 
points={{-9.2857,-49},{15,-49},{15,64.0714},{52,64.0714}}, 
color={0,0,127}));
    connect(product3.y, gain1.u) 
    annotation(Line(origin={2,54}, 
    points={{-15.5,0},{16,0}}, 
    color={0,0,127}));
    connect(product3.y, CRB[3,2]) 
    annotation(Line(origin={20,45}, 
points={{-33.5,9},{-8,9},{-8,-36},{32,-36}}, 
color={0,0,127}));
    connect(const.y, CA[1,1]) 
    annotation(Line(origin={20,-20}, 
points={{-20.5,29},{16,29},{16,-7.2858},{32,-7.2858}}, 
color={0,0,127}));
    connect(const.y, CA[1,2]) 
    annotation(Line(origin={20,-20}, 
points={{-20.5,29},{12,29},{12,-7.2858},{32,-7.2858}}, 
color={0,0,127}));
    connect(const.y, CA[2,1]) 
    annotation(Line(origin={20,-20}, 
points={{-20.5,29},{8,29},{8,-7.2858},{32,-7.2858}}, 
color={0,0,127}));
    connect(const.y, CA[2,2]) 
    annotation(Line(origin={20,-20}, 
points={{-20.5,29},{4,29},{4,-7.2858},{32,-7.2858}}, 
color={0,0,127}));
    connect(const.y, CA[3,3]) 
    annotation(Line(origin={20,-20}, 
points={{-20.5,29},{0,29},{0,-7.2858},{32,-7.2858}}, 
color={0,0,127}));
    connect(gain2.y, CA[1,3]) 
    annotation(Line(origin={25,-29}, 
  points={{-28.5,19.8571},{-17,19.8571},{-17,1.7142},{27,1.7142}}, 
  color={0,0,127}));
    connect(gain2.u, add2.y) 
    annotation(Line(origin={-21,-9}, 
    points={{6,-0.1429},{-6.5,-0.1429}}, 
    color={0,0,127}));
    connect(product5.y, add2.u1) 
    annotation(Line(origin={-46,1}, 
points={{4.5,8},{7,8},{7,1},{4,1},{4,-7.1429},{7,-7.1429}}, 
color={0,0,127}));
    connect(product5.u1, gain3.y) 
    annotation(Line(origin={-58,12}, 
points={{5,0},{-0.5,0}}, 
color={0,0,127}));
    connect(gain3.u, add3.y) 
    annotation(Line(origin={-92,12}, 
points={{22,0},{16.5,0}}, 
color={0,0,127}));
    connect(Hydd_Coef[3], add3.u1) 
    annotation(Line(origin={-133,-19}, 
points={{18.7143,-21},{43,-21},{43,34},{46,34}}, 
color={0,0,127}));
    connect(Hydd_Coef[4], add3.u2) 
    annotation(Line(origin={-133,-22}, 
points={{18.7143,-18},{43,-18},{43,31},{46,31}}, 
color={0,0,127}));
    connect(product5.u2, V_Local[3]) 
    annotation(Line(origin={-111,-46}, 
points={{58,52},{21,52},{21,-34},{-3.2857,-34}}, 
color={0,0,127}));
    connect(add2.u2, product6.y) 
    annotation(Line(origin={-46,-12}, 
    points={{7,-0.1429},{-7.5,-0.1429}}, 
    color={0,0,127}));
    connect(Hydd_Coef[2], product6.u1) 
    annotation(Line(origin={-111,-31}, 
points={{-3.2857,-9},{21,-9},{21,21.8571},{46,21.8571}}, 
color={0,0,127}));
    connect(V_Local[2], product6.u2) 
    annotation(Line(origin={-111,-56}, 
points={{-3.2857,-24},{21,-24},{21,40.8571},{46,40.8571}}, 
color={0,0,127}));
    connect(gain4.y, CA[2,3]) 
    annotation(Line(origin={25,-38}, 
  points={{-28.5,10.7142},{27,10.7142},{27,10.7142}}, 
  color={0,0,127}));
    connect(gain4.u, product7.y) 
    annotation(Line(origin={-21,-27}, 
    points={{6,-0.2858},{-6.5,-0.2858}}, 
    color={0,0,127}));
    connect(product7.u1, Hydd_Coef[1]) 
    annotation(Line(origin={-98,-39}, 
points={{59,14.7142},{8,14.7142},{8,-1},{-16.2857,-1}}, 
color={0,0,127}));
    connect(product7.u2, V_Local[1]) 
    annotation(Line(origin={-98,-64}, 
points={{59,33.7142},{8,33.7142},{8,-16},{-16.2857,-16}}, 
color={0,0,127}));
    connect(product7.y, CA[3,2]) 
    annotation(Line(origin={13,-38}, 
  points={{-40.5,10.7142},{-31,10.7142},{-31,0},{3,0},{3,10.7142},{39,10.7142}}, 
  color={0,0,127}));
    connect(gain5.y, CA[3,1]) 
    annotation(Line(origin={25,-55}, 
  points={{-28.5,-7.2143},{-17,-7.2143},{-17,27.7142},{27,27.7142}}, 
  color={0,0,127}));
    connect(add4.y, gain5.u) 
    annotation(Line(origin={-21,-62}, 
    points={{-6.5,-0.2143},{6,-0.2143}}, 
    color={0,0,127}));
    connect(product6.y, add4.u1) 
    annotation(Line(origin={-46,-36}, 
    points={{-7.5,23.8571},{-2,23.8571},{-2,-23.2143},{7,-23.2143}}, 
    color={0,0,127}));
    connect(product5.y, add4.u2) 
    annotation(Line(origin={-46,-28}, 
points={{4.5,37},{7,37},{7,30},{4,30},{4,-37.2143},{7,-37.2143}}, 
color={0,0,127}));
    connect(matrixAdd.C, Cv) 
    annotation(Line(origin={106,-4}, 
  points={{-11,-0.1429},{10,-0.1429},{10,-0.1429}}, 
  color={0,0,127}));
    connect(CRB, matrixAdd.A) 
    annotation(Line(origin={63,18}, 
  points={{-11,-9},{3,-9},{3,-17.1429},{9,-17.1429}}, 
  color={0,0,127}));
    connect(CA, matrixAdd.B) 
    annotation(Line(origin={63,-29}, 
  points={{-11,1.7142},{5,1.7142},{5,19.8571},{9,19.8571}}, 
  color={0,0,127}));
    end C;
  model D
    extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput Hydd_Coef[19] 
      annotation(Placement(transformation(origin = {-120, 50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealInput V_local[3] 
      annotation(Placement(transformation(origin = {-120, -50}, 
      extent = {{-20, -20}, {20, 20}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput Dv[3,3] 
      annotation(Placement(transformation(origin = {110, 0}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Interfaces.RealOutput Dl[3,3] 
      annotation(Placement(transformation(origin = {42, 40}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput Dn[3,3] 
      annotation(Placement(transformation(origin = {42, -40}, 
      extent = {{-10, -10}, {10, 10}}), 
      iconTransformation(origin = {0, 0})));
    Modelica.Blocks.Sources.Constant const(k = 0) 
      annotation(Placement(transformation(origin = {-78, 72}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Product product1 
      annotation(Placement(transformation(origin = {-12, 22}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Abs abs1 
      annotation(Placement(transformation(origin = {-50, 16}, 
      extent = {{-10, -10}, {10, 10}})));
    SubSystem1 subSystem1 annotation(Placement(transformation(origin = {-12, -6}, 
      extent = {{-10, -10}, {10, 10}})));
    SubSystem2 subSystem2 annotation(Placement(transformation(origin = {-12, -34}, 
      extent = {{-10, -10}, {10, 10}})));
    SubSystem3 subSystem3 annotation(Placement(transformation(origin = {-12, -62}, 
      extent = {{-10, -10}, {10, 10}})));
    SubSystem4 subSystem4 annotation(Placement(transformation(origin = {-12, -90}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Abs abs2 
      annotation(Placement(transformation(origin = {-50, -26.5}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Abs abs3 
      annotation(Placement(transformation(origin = {-50, -69}, 
      extent = {{-10, -10}, {10, 10}})));
    Utilities.Math.MatrixAdd matrixAdd 
      annotation(Placement(transformation(origin = {82, 0}, 
      extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Gain gain[3,3](k = -1) 
      annotation(Placement(transformation(origin = {52, 40}, 
      extent = {{-4, -4}, {4, 4}})));
    Modelica.Blocks.Math.Gain gain1[3,3](k = -1) 
      annotation(Placement(transformation(origin = {52, -40}, 
      extent = {{-4, -4}, {4, 4}})));
    annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
      grid = {2, 2}), graphics = {Text(origin = {-2, 5}, 
      lineColor = {0, 0, 0}, 
      extent = {{-50, 55}, {50, -55}}, 
      textString = "D", 
      textStyle = {TextStyle.None}, 
      textColor = {0, 0, 0}, 
      horizontalAlignment = LinePattern.None)}));
    block SubSystem1
      annotation(__MWorks(PortArrangement(Left(u1, u2, u3, u4), Right(y1), Top()), independentInstance = true));
      Modelica.Blocks.Math.Product product2 
        annotation(Placement(transformation(origin = {-226, 16}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Product product3 
        annotation(Placement(transformation(origin = {-226, -24}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Add add 
        annotation(Placement(transformation(origin = {-188, 0}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
        annotation(Placement(transformation(extent = {{-252, 18}, {-244, 26}})));
      Modelica.Blocks.Interfaces.RealInput u2 
        annotation(Placement(transformation(extent = {{-252, 6}, {-244, 14}})));
      Modelica.Blocks.Interfaces.RealInput u3 
        annotation(Placement(transformation(extent = {{-252, -22}, {-244, -14}})));
      Modelica.Blocks.Interfaces.RealInput u4 
        annotation(Placement(transformation(extent = {{-252, -34}, {-244, -26}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
        annotation(Placement(transformation(extent = {{-169, -2}, {-165, 2}})));
    equation
      connect(product2.y, add.u1) 
        annotation(Line(origin = {-207, 11}, 
        points = {{-8, 5}, {3, 5}, {3, -5}, {7, -5}}, 
        color = {0, 0, 127}));
      connect(product3.y, add.u2) 
        annotation(Line(origin = {-207, -15}, 
        points = {{-8, -9}, {3, -9}, {3, 9}, {7, 9}}, 
        color = {0, 0, 127}));
      connect(u1, product2.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u2, product2.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u3, product3.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u4, product3.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(y1, add.y) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
    end SubSystem1;
    block SubSystem2
      annotation(__MWorks(PortArrangement(Left(u1, u2, u3, u4), Right(y1), Top()), independentInstance = true));
      Modelica.Blocks.Math.Product product2 
        annotation(Placement(transformation(origin = {-226, 16}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Product product3 
        annotation(Placement(transformation(origin = {-226, -24}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Add add 
        annotation(Placement(transformation(origin = {-188, 0}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
        annotation(Placement(transformation(extent = {{-252, 18}, {-244, 26}})));
      Modelica.Blocks.Interfaces.RealInput u2 
        annotation(Placement(transformation(extent = {{-252, 6}, {-244, 14}})));
      Modelica.Blocks.Interfaces.RealInput u3 
        annotation(Placement(transformation(extent = {{-252, -22}, {-244, -14}})));
      Modelica.Blocks.Interfaces.RealInput u4 
        annotation(Placement(transformation(extent = {{-252, -34}, {-244, -26}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
        annotation(Placement(transformation(extent = {{-169, -2}, {-165, 2}})));
    equation
      connect(product2.y, add.u1) 
        annotation(Line(origin = {-207, 11}, 
        points = {{-8, 5}, {3, 5}, {3, -5}, {7, -5}}, 
        color = {0, 0, 127}));
      connect(product3.y, add.u2) 
        annotation(Line(origin = {-207, -15}, 
        points = {{-8, -9}, {3, -9}, {3, 9}, {7, 9}}, 
        color = {0, 0, 127}));
      connect(u1, product2.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u2, product2.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u3, product3.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u4, product3.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(y1, add.y) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
    end SubSystem2;
    block SubSystem3
      annotation(__MWorks(PortArrangement(Left(u1, u2, u3, u4), Right(y1), Top()), independentInstance = true));
      Modelica.Blocks.Math.Product product2 
        annotation(Placement(transformation(origin = {-226, 16}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Product product3 
        annotation(Placement(transformation(origin = {-226, -24}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Add add 
        annotation(Placement(transformation(origin = {-188, 0}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
        annotation(Placement(transformation(extent = {{-252, 18}, {-244, 26}})));
      Modelica.Blocks.Interfaces.RealInput u2 
        annotation(Placement(transformation(extent = {{-252, 6}, {-244, 14}})));
      Modelica.Blocks.Interfaces.RealInput u3 
        annotation(Placement(transformation(extent = {{-252, -22}, {-244, -14}})));
      Modelica.Blocks.Interfaces.RealInput u4 
        annotation(Placement(transformation(extent = {{-252, -34}, {-244, -26}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
        annotation(Placement(transformation(extent = {{-169, -2}, {-165, 2}})));
    equation
      connect(product2.y, add.u1) 
        annotation(Line(origin = {-207, 11}, 
        points = {{-8, 5}, {3, 5}, {3, -5}, {7, -5}}, 
        color = {0, 0, 127}));
      connect(product3.y, add.u2) 
        annotation(Line(origin = {-207, -15}, 
        points = {{-8, -9}, {3, -9}, {3, 9}, {7, 9}}, 
        color = {0, 0, 127}));
      connect(u1, product2.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u2, product2.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u3, product3.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u4, product3.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(y1, add.y) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
    end SubSystem3;
    block SubSystem4
      annotation(__MWorks(PortArrangement(Left(u1, u2, u3, u4), Right(y1), Top()), independentInstance = true));
      Modelica.Blocks.Math.Product product2 
        annotation(Placement(transformation(origin = {-226, 16}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Product product3 
        annotation(Placement(transformation(origin = {-226, -24}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Add add 
        annotation(Placement(transformation(origin = {-188, 0}, 
        extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
        annotation(Placement(transformation(extent = {{-252, 18}, {-244, 26}})));
      Modelica.Blocks.Interfaces.RealInput u2 
        annotation(Placement(transformation(extent = {{-252, 6}, {-244, 14}})));
      Modelica.Blocks.Interfaces.RealInput u3 
        annotation(Placement(transformation(extent = {{-252, -22}, {-244, -14}})));
      Modelica.Blocks.Interfaces.RealInput u4 
        annotation(Placement(transformation(extent = {{-252, -34}, {-244, -26}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
        annotation(Placement(transformation(extent = {{-169, -2}, {-165, 2}})));
    equation
      connect(product2.y, add.u1) 
        annotation(Line(origin = {-207, 11}, 
        points = {{-8, 5}, {3, 5}, {3, -5}, {7, -5}}, 
        color = {0, 0, 127}));
      connect(product3.y, add.u2) 
        annotation(Line(origin = {-207, -15}, 
        points = {{-8, -9}, {3, -9}, {3, 9}, {7, 9}}, 
        color = {0, 0, 127}));
      connect(u1, product2.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u2, product2.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u3, product3.u1) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(u4, product3.u2) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
      connect(y1, add.y) 
        annotation(Line(origin = {0, 0}, 
        points = {{0, 0}, {0, 0}}, 
        color = {0, 0, 0}));
    end SubSystem4;
  equation
    connect(Hydd_Coef[6], Dl[1,1]) 
      annotation(Line(origin = {-39, 64}, 
      points = {{-81, -14}, {-55, -14}, {-55, 24}, {65, 24}, {65, -24}, {81, -24}}, 
      color = {0, 0, 127}));
    connect(const.y, Dl[1,2]) 
      annotation(Line(origin = {-12, 56}, 
      points = {{-55, 16}, {36, 16}, {36, -16}, {54, -16}}, 
      color = {0, 0, 127}));
    connect(const.y, Dl[1,3]) 
      annotation(Line(origin = {-12, 56}, 
      points = {{-55, 16}, {34, 16}, {34, -16}, {54, -16}}, 
      color = {0, 0, 127}));
    connect(const.y, Dl[2,1]) 
      annotation(Line(origin = {-12, 56}, 
      points = {{-55, 16}, {32, 16}, {32, -16}, {54, -16}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[10], Dl[2,2]) 
      annotation(Line(origin = {-39, 45}, 
      points = {{-81, 5}, {57, 5}, {57, -5}, {81, -5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[13], Dl[2,3]) 
      annotation(Line(origin = {-39, 45}, 
      points = {{-81, 5}, {55, 5}, {55, -5}, {81, -5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[15], Dl[3,2]) 
      annotation(Line(origin = {-39, 45}, 
      points = {{-81, 5}, {53, 5}, {53, -5}, {81, -5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[18], Dl[3,3]) 
      annotation(Line(origin = {-39, 45}, 
      points = {{-81, 5}, {51, 5}, {51, -5}, {81, -5}}, 
      color = {0, 0, 127}));
    connect(product1.y, Dn[1,1]) 
      annotation(Line(origin = {21, -9}, 
      points = {{-22, 31}, {7, 31}, {7, -31}, {21, -31}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[7], product1.u1) 
      annotation(Line(origin = {-72, 39}, 
      points = {{-48, 11}, {40, 11}, {40, -11}, {48, -11}}, 
      color = {0, 0, 127}));
    connect(abs1.y, product1.u2) 
      annotation(Line(origin = {-31, 16}, 
      points = {{-8, 0}, {7, 0}}, 
      color = {0, 0, 127}));
    connect(V_local[1], abs1.u) 
      annotation(Line(origin = {-91, -17}, 
      points = {{-29, -33}, {-3, -33}, {-3, 33}, {29, 33}}, 
      color = {0, 0, 127}));
    connect(const.y, Dn[1,2]) 
      annotation(Line(origin = {-12, 16}, 
      points = {{-55, 56}, {36, 56}, {36, -56}, {54, -56}}, 
      color = {0, 0, 127}));
    connect(const.y, Dn[1,3]) 
      annotation(Line(origin = {-12, 16}, 
      points = {{-55, 56}, {34, 56}, {34, -56}, {54, -56}}, 
      color = {0, 0, 127}));
    connect(const.y, Dn[2,1]) 
      annotation(Line(origin = {-12, 16}, 
      points = {{-55, 56}, {32, 56}, {32, -56}, {54, -56}}, 
      color = {0, 0, 127}));
    connect(const.y, Dn[3,1]) 
      annotation(Line(origin = {-12, 16}, 
      points = {{-55, 56}, {30, 56}, {30, -56}, {54, -56}}, 
      color = {0, 0, 127}));
    connect(subSystem1.y1, Dn[2,2]) 
      annotation(Line(origin = {21, -23}, 
      points = {{-21.2, 17}, {-5, 17}, {-5, -17}, {21, -17}}, 
      color = {0, 0, 127}));
    connect(subSystem2.y1, Dn[2,3]) 
      annotation(Line(origin = {21, -37}, 
      points = {{-21.2, 3}, {-7, 3}, {-7, -3}, {21, -3}}, 
      color = {0, 0, 127}));
    connect(subSystem3.y1, Dn[3,2]) 
      annotation(Line(origin = {21, -51}, 
      points = {{-21.2, -11}, {-9, -11}, {-9, 11}, {21, 11}}, 
      color = {0, 0, 127}));
    connect(subSystem4.y1, Dn[3,3]) 
      annotation(Line(origin = {21, -65}, 
      points = {{-21.2, -25}, {-11, -25}, {-11, 25}, {21, 25}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[8], subSystem1.u1) 
      annotation(Line(origin = {-72, 26}, 
      points = {{-48, 24}, {4, 24}, {4, -24.5}, {48.2, -24.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[9], subSystem1.u4) 
      annotation(Line(origin = {-72, 23}, 
      points = {{-48, 27}, {0, 27}, {0, -33}, {38, -33}, {38, -36.5}, {48.2, -36.5}}, 
      color = {0, 0, 127}));
    connect(abs2.y, subSystem1.u3) 
      annotation(Line(origin = {-31, -17}, 
      points = {{-8, -9.5}, {1, -9.5}, {1, 8.5}, {7.2, 8.5}}, 
      color = {0, 0, 127}));
    connect(V_local[3], abs2.u) 
      annotation(Line(origin = {-91, -38}, 
      points = {{-29, -12}, {21, -12}, {21, 11.5}, {29, 11.5}}, 
      color = {0, 0, 127}));
    connect(abs3.u, V_local[2]) 
      annotation(Line(origin = {-91, -59}, 
      points = {{29, -10}, {21, -10}, {21, 9}, {-29, 9}}, 
      color = {0, 0, 127}));
    connect(abs3.y, subSystem1.u2) 
      annotation(Line(origin = {-31, -36}, 
      points = {{-8, -33}, {-1, -33}, {-1, 32.5}, {7.2, 32.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[11], subSystem2.u1) 
      annotation(Line(origin = {-72, 12}, 
      points = {{-48, 38}, {44.4, 38}, {44.4, -38.5}, {48.2, -38.5}}, 
      color = {0, 0, 127}));
    connect(abs3.y, subSystem2.u2) 
      annotation(Line(origin = {-31, -50}, 
      points = {{-8, -19}, {-1, -19}, {-1, 18.5}, {7.2, 18.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[12], subSystem2.u3) 
      annotation(Line(origin = {-72, 7}, 
      points = {{-48, 43}, {44.4, 43}, {44.4, -43.5}, {48.2, -43.5}}, 
      color = {0, 0, 127}));
    connect(abs2.y, subSystem2.u4) 
      annotation(Line(origin = {-31, -34}, 
      points = {{-8, 7.5}, {3.4, 7.5}, {3.4, -7.5}, {7.2, -7.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[16], subSystem3.u1) 
      annotation(Line(origin = {-72, -2}, 
      points = {{-48, 52}, {44.4, 52}, {44.4, -52.5}, {48.2, -52.5}}, 
      color = {0, 0, 127}));
    connect(abs2.y, subSystem3.u2) 
      annotation(Line(origin = {-31, -43}, 
      points = {{-8, 16.5}, {3.4, 16.5}, {3.4, -16.5}, {7.2, -16.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[14], subSystem3.u3) 
      annotation(Line(origin = {-72, -7}, 
      points = {{-48, 57}, {44.4, 57}, {44.4, -57.5}, {48.2, -57.5}}, 
      color = {0, 0, 127}));
    connect(abs3.y, subSystem3.u4) 
      annotation(Line(origin = {-31, -69}, 
      points = {{-8, 0}, {7.2, 0}, {7.2, -0.5}}, 
      color = {0, 0, 127}));
    connect(abs2.y, subSystem4.u1) 
      annotation(Line(origin = {-31, -54}, 
      points = {{-8, 27.5}, {3.4, 27.5}, {3.4, -28.5}, {7.2, -28.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[19], subSystem4.u2) 
      annotation(Line(origin = {-72, -19}, 
      points = {{-48, 69}, {44.4, 69}, {44.4, -68.5}, {48.2, -68.5}}, 
      color = {0, 0, 127}));
    connect(Hydd_Coef[17], subSystem4.u3) 
      annotation(Line(origin = {-72, -21}, 
      points = {{-48, 71}, {44.4, 71}, {44.4, -71.5}, {48.2, -71.5}}, 
      color = {0, 0, 127}));
    connect(abs3.y, subSystem4.u4) 
      annotation(Line(origin = {-31, -83}, 
      points = {{-8, 14}, {3.4, 14}, {3.4, -14.5}, {7.2, -14.5}}, 
      color = {0, 0, 127}));
    connect(gain.y, matrixAdd.A) 
      annotation(Line(origin = {63, 23}, 
      points = {{-6.6, 17}, {3, 17}, {3, -18}, {7, -18}}, 
      color = {0, 0, 127}));
    connect(gain1.y, matrixAdd.B) 
      annotation(Line(origin = {63, -22}, 
      points = {{-6.6, -18}, {3, -18}, {3, 17}, {7, 17}}, 
      color = {0, 0, 127}));
    connect(Dv, matrixAdd.C) 
      annotation(Line(origin = {102, 0}, 
      points = {{8, 0}, {-9, 0}}, 
      color = {0, 0, 127}));
    connect(Dl, gain.u) 
      annotation(Line(origin = {45, 40}, 
      points = {{-3, 0}, {2.2, 0}}, 
      color = {0, 0, 127}));
    connect(Dn, gain1.u) 
      annotation(Line(origin = {45, -40}, 
      points = {{-3, 0}, {2.2, 0}}, 
      color = {0, 0, 127}));
    connect(const.y, Dl[3,1]) 
      annotation(Line(origin = {-12, 56}, 
      points = {{-55, 16}, {28, 16}, {28, -16}, {54, -16}}, 
      color = {0, 0, 127}));
  end D;

end Components;