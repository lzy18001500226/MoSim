package Dynamic_Equations "运动学方程"
  model Dynamic_Model_Equations
    extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput Tstbd 
      annotation (Placement(transformation(origin={-120,75}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Mass 
      annotation (Placement(transformation(origin={-120,25}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Tport 
      annotation (Placement(transformation(origin={-120,-25}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Hydd_Coef[19] 
      annotation (Placement(transformation(origin={-120,-75}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput V_local[3] 
      annotation (Placement(transformation(origin={110,0}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={0,0})));
    M m 
      annotation (Placement(transformation(origin={-6,65}, 
extent={{-10,-10},{10,10}})));
    Utilities.Math.MatrixInverse matrixInverse(M1=3,M2=3,I1=3,I2=3) 
      annotation (Placement(transformation(origin={36,65}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const1(k=0) 
      annotation (Placement(transformation(origin={-60,64}, 
extent={{-4,-4},{4,4}})));
    Modelica.Blocks.Sources.Constant const2(k=0) 
      annotation (Placement(transformation(origin={-60,48}, 
extent={{-4,-4},{4,4}})));
    Modelica.Blocks.Sources.Constant const3(k=3.1) 
      annotation (Placement(transformation(origin={-60,31}, 
extent={{-4,-4},{4,4}})));
    Utilities.Math.MatrixMultiply matrixMultiply 
      annotation (Placement(transformation(origin = {50, -50}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Continuous.Integrator integrator[3] 
      annotation (Placement(transformation(origin={72,5.55112e-17}, 
extent={{-10,-10},{10,10}})));
    T_C_D t_C_D 
      annotation (Placement(transformation(origin={4,-55}, 
extent={{-20,-20},{20,20}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={5,2}, 
lineColor={0,0,0}, 
extent={{-75,38},{75,-38}}, 
textString="Dynamic_Model_Equations", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}));
  equation
    connect(m.M, matrixInverse.Mat) 
    annotation(Line(origin={15,65}, 
points={{-10,0},{9.2,0}}, 
color={0,0,127}));
    connect(Mass, m.m) 
    annotation(Line(origin={-69,49}, 
points={{-51,-24},{-15,-24},{-15,24},{51,24}}, 
color={0,0,127}));
    connect(const1.y, m.X_G) 
    annotation(Line(origin={-37,67}, 
    points={{-18.6,-3},{-5,-3},{-5,2},{19,2}}, 
    color={0,0,127}));
    connect(const2.y, m.Y_G) 
    annotation(Line(origin={-37,57}, 
    points={{-18.6,-9},{-1,-9},{-1,8},{19,8}}, 
    color={0,0,127}));
    connect(const3.y, m.I_z) 
    annotation(Line(origin={-37,46}, 
    points={{-18.6,-15},{3,-15},{3,15},{19,15}}, 
    color={0,0,127}));
    connect(Hydd_Coef, m.Hydd_Coef) 
    annotation(Line(origin={-69,-9}, 
    points={{-51,-66},{39,-66},{39,66},{51,66}}, 
    color={0,0,127}));
    connect(integrator.y, V_local) 
    annotation(Line(origin={97,0}, 
    points={{-14,5.55112e-17},{13,5.55112e-17},{13,0}}, 
    color={0,0,127}));
    connect(matrixMultiply.C[:,1], integrator.u) 
    annotation(Line(origin={63,-25}, 
    points={{-2,-25},{17,-25},{17,-1},{-17,-1},{-17,25},{-3,25}}, 
    color={0,0,127}));
    connect(matrixInverse.Inv, matrixMultiply.A) 
    annotation(Line(origin={47,10}, 
    points={{0.8,55},{17,55},{17,20},{-17,20},{-17,-55},{-9,-55}}, 
    color={0,0,127}));
    connect(t_C_D.y, matrixMultiply.B[:,1]) 
    annotation(Line(origin={32,-55}, 
    points={{-6,0},{6,0}}, 
    color={0,0,127}));
    connect(Mass, t_C_D.m) 
    annotation(Line(origin={-69,-6}, 
    points={{-51,31},{-15,31},{-15,-31.85714},{50.1428,-31.85714}}, 
    color={0,0,127}));
    connect(const1.y, t_C_D.X_G) 
    annotation(Line(origin={-37,10}, 
    points={{-18.6,54},{-5,54},{-5,-53.5714},{18.1428,-53.5714}}, 
    color={0,0,127}));
    connect(const2.y, t_C_D.Y_G) 
    annotation(Line(origin={-37,-1}, 
    points={{-18.6,49},{-1,49},{-1,-48.28572},{18.1428,-48.28572}}, 
    color={0,0,127}));
    connect(integrator.y, t_C_D.V_Local) 
    annotation(Line(origin={25,-40}, 
    points={{58,40},{67,40},{67,-40},{-67,-40},{-67,-15},{-43.8572,-15}}, 
    color={0,0,127}));
    connect(Tstbd, t_C_D.Tstbd) 
    annotation(Line(origin={-69,7}, 
points={{-51,68},{-17,68},{-17,-67.71428},{50.1428,-67.71428}}, 
color={0,0,127}));
    connect(Tport, t_C_D.Tport) 
    annotation(Line(origin={-69,-46}, 
points={{-51,21},{-19,21},{-19,-20.4286},{50.1428,-20.4286}}, 
color={0,0,127}));
    connect(Hydd_Coef, t_C_D.Hydd_Coef) 
    annotation(Line(origin={-69,-74}, 
    points={{-51,-1},{39,-1},{39,1.85714},{50.1428,1.85714}}, 
    color={0,0,127}));
  end Dynamic_Model_Equations;
  model M
    extends USV.Utilities.Icons.Model;
    Modelica.Blocks.Interfaces.RealInput m 
      annotation (Placement(transformation(origin={-220,70}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={-120,80}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealInput X_G 
      annotation (Placement(transformation(origin={-220,24}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={-120,40}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealInput Y_G 
      annotation (Placement(transformation(origin={-220,-22}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={-120,0}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealInput I_z 
      annotation (Placement(transformation(origin={-220,-68}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={-120,-40}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealInput Hydd_Coef[19] 
      annotation (Placement(transformation(origin={-220,-114}, 
extent={{-20,-20},{20,20}}), 
iconTransformation(origin={-120,-80}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Interfaces.RealOutput M[3,3] 
      annotation (Placement(transformation(origin={118,-12}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={110,0}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add(k2=-1) 
      annotation (Placement(transformation(origin = {10, 80}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant const(k=0) 
      annotation (Placement(transformation(origin={68,60}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Gain gain(k=-1) 
      annotation (Placement(transformation(origin={10,34}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Product product1 
      annotation (Placement(transformation(origin={-30,34}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add1(k2=-1) 
      annotation (Placement(transformation(origin={10,-12}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add2(k2=-1) 
      annotation (Placement(transformation(origin={-30,-42}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Product product2 
      annotation (Placement(transformation(origin={-88,-36}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add3(k2=-1) 
      annotation (Placement(transformation(origin={10,-62}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Math.Add add4(k2=-1) 
      annotation (Placement(transformation(origin={10,-104}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(m, add.u1) 
    annotation(Line(origin={-111,78}, 
points={{-109,-8},{-75,-8},{-75,8},{109,8}}, 
color={0,0,127}));
    connect(Hydd_Coef[1], add.u2) 
    annotation(Line(origin={-111,-20}, 
    points={{-109,-94},{-75,-94},{-75,94},{109,94}}, 
    color={0,0,127}));
    connect(add.y, M[1,1]) 
    annotation(Line(origin={70,34}, 
    points={{-49,46},{30,46},{30,-46},{48,-46}}, 
    color={0,0,127}));
    connect(const.y, M[1,2]) 
    annotation(Line(origin={99,24}, 
    points={{-20,36},{-3,36},{-3,-36},{19,-36}}, 
    color={0,0,127}));
    connect(const.y, M[2,1]) 
    annotation(Line(origin={99,24}, 
    points={{-20,36},{-7,36},{-7,-36},{19,-36}}, 
    color={0,0,127}));
    connect(gain.u, product1.y) 
    annotation(Line(origin={-10,34}, 
points={{8,0},{-9,0}}, 
color={0,0,127}));
    connect(m, product1.u1) 
    annotation(Line(origin={-131,32}, 
points={{-89,38},{77,38},{77,8},{89,8}}, 
color={0,0,127}));
    connect(Y_G, product1.u2) 
    annotation(Line(origin={-131,21}, 
points={{-89,-43},{-49,-43},{-49,43},{71,43},{71,7},{89,7}}, 
color={0,0,127}));
    connect(gain.y, M[1,3]) 
    annotation(Line(origin={70,-12}, 
points={{-49,46},{16,46},{16,0},{48,0}}, 
color={0,0,127}));
    connect(gain.y, M[3,1]) 
    annotation(Line(origin={70,-12}, 
points={{-49,46},{10,46},{10,0},{48,0}}, 
color={0,0,127}));
    connect(add1.y, M[2,2]) 
    annotation(Line(origin={70,-35}, 
points={{-49,23},{48,23}}, 
color={0,0,127}));
    connect(m, add1.u1) 
    annotation(Line(origin={-111,9}, 
points={{-109,61},{45,61},{45,-15},{109,-15}}, 
color={0,0,127}));
    connect(Hydd_Coef[2], add1.u2) 
    annotation(Line(origin={-111,-28}, 
points={{-109,-86},{-69,-86},{-69,4},{-63,4},{-63,86},{39,86},{39,10},{109,10}}, 
color={0,0,127}));
    connect(add2.y, M[2,3]) 
    annotation(Line(origin={50,-50}, 
points={{-69,8},{42,8},{42,38},{68,38}}, 
color={0,0,127}));
    connect(add2.u1, product2.y) 
    annotation(Line(origin={-59,-36}, 
points={{17,0},{-18,0}}, 
color={0,0,127}));
    connect(m, product2.u1) 
    annotation(Line(origin={-160,-3}, 
points={{-60,73},{50,73},{50,-27},{60,-27}}, 
color={0,0,127}));
    connect(product2.u2, X_G) 
    annotation(Line(origin={-160,-32}, 
points={{60,-10},{44,-10},{44,56},{-60,56}}, 
color={0,0,127}));
    connect(Hydd_Coef[3], add2.u2) 
    annotation(Line(origin={-131,-104}, 
points={{-89,-10},{-39,-10},{-39,56},{89,56}}, 
color={0,0,127}));
    connect(add3.y, M[3,2]) 
    annotation(Line(origin={70,-37}, 
    points={{-49,-25},{26,-25},{26,25},{48,25}}, 
    color={0,0,127}));
    connect(product2.y, add3.u1) 
    annotation(Line(origin={-39,-46}, 
    points={{-38,10},{-15,10},{-15,-10},{37,-10}}, 
    color={0,0,127}));
    connect(Hydd_Coef[4], add3.u2) 
    annotation(Line(origin={-111,-87}, 
    points={{-109,-27},{-53,-27},{-53,27},{105,27},{105,19},{109,19}}, 
    color={0,0,127}));
    connect(add4.y, M[3,3]) 
    annotation(Line(origin={70,-58}, 
    points={{-49,-46},{30,-46},{30,46},{48,46}}, 
    color={0,0,127}));
    connect(I_z, add4.u1) 
    annotation(Line(origin={-111,-83}, 
    points={{-109,15},{97,15},{97,-15},{109,-15}}, 
    color={0,0,127}));
    connect(Hydd_Coef[5], add4.u2) 
    annotation(Line(origin={-111,-112}, 
    points={{-109,-2},{97,-2},{97,2},{109,2}}, 
    color={0,0,127}));

  end M;
  model T_C_D
    extends USV.Utilities.Icons.Model;
    parameter Real B = 0.64;
    Modelica.Blocks.Interfaces.RealInput m 
      annotation (Placement(transformation(origin={-114.286,85.7143}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput X_G 
      annotation (Placement(transformation(origin={-114.286,57.1429}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Y_G 
      annotation (Placement(transformation(origin={-114.286,28.5714}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput V_Local[3] 
      annotation (Placement(transformation(origin={-114.286,-1.42109e-14}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Tstbd 
      annotation (Placement(transformation(origin={-114.286,-28.5714}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Tport 
      annotation (Placement(transformation(origin={-114.286,-57.1429}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealInput Hydd_Coef[19] 
      annotation (Placement(transformation(origin={-114.286,-85.7143}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}}), 
  iconTransformation(origin={0,0})));
    Modelica.Blocks.Interfaces.RealOutput y[3] 
      annotation (Placement(transformation(origin={110,0}, 
  extent={{-10,-10},{10,10}}), 
  iconTransformation(origin={0,0})));
    Components.Tau tau 
      annotation (Placement(transformation(origin={-7.7143,76.1905}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Modelica.Blocks.Sources.RealExpression realExpression(y=B) 
      annotation (Placement(transformation(origin={-61.0001,85.7143}, 
  extent={{-10,-10},{10,10}})));
    Components.C c 
      annotation (Placement(transformation(origin={-7.7143,11.4286}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Utilities.Math.MatrixMultiply matrixMultiply 
      annotation (Placement(transformation(origin={38,6.4286}, 
  extent={{-10,-10},{10,10}})));
    Components.D d 
      annotation (Placement(transformation(origin={-7.7143,-53.3333}, 
  extent={{-14.2857,-14.2857},{14.2857,14.2857}})));
    Utilities.Math.MatrixMultiply matrixMultiply1 
      annotation (Placement(transformation(origin={38,-58.3333}, 
  extent={{-10,-10},{10,10}})));
    SubSystem1 subSystem1[3](add(k2=-1)) annotation(Placement(transformation(origin={74,6.4286}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
    block SubSystem1
                annotation(__MWorks(PortArrangement(Left(u1,u2,u3), Right(y1),Top()),independentInstance = true));
      Modelica.Blocks.Math.Add add 
        annotation (Placement(transformation(origin = {70, 60}, extent = {{-10, -10}, {10, 10}})));
      Modelica.Blocks.Math.Add add1(k2=-1) 
        annotation (Placement(transformation(origin={94.5717,32.8571}, 
      extent={{-10,-10},{10,10}})));
      Modelica.Blocks.Interfaces.RealInput u1 
          annotation (Placement(transformation(extent = { {44, 62}, {52, 70}})));
      Modelica.Blocks.Interfaces.RealInput u2 
          annotation (Placement(transformation(extent = { {44, 50}, {52, 58}})));
      Modelica.Blocks.Interfaces.RealInput u3 
          annotation (Placement(transformation(extent = { {68.5717, 22.8571}, {76.5717, 30.8571}})));
      Modelica.Blocks.Interfaces.RealOutput y1 
          annotation (Placement(transformation(extent = { {113.572, 30.8571}, {117.572, 34.8571}})));
    equation
      connect(add.y, add1.u1) 
      annotation(Line(origin={81,49}, 
      points={{0,11},{3,11},{3,-1},{-2.4283,-1},{-2.4283,-10.1429},{1.5717,-10.1429}}, 
      color={0,0,127}));
      connect(u1, add.u1) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
      connect(u2, add.u2) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
      connect(u3, add1.u2) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
      connect(y1, add1.y) 
        annotation (Line(origin = {0, 0}, 
                  points = { {0, 0}, {0, 0} }, 
                  color = { 0, 0, 0 }));
                end SubSystem1;
  equation
    connect(tau.B, realExpression.y) 
    annotation(Line(origin={-37,86}, 
    points={{12.1429,-0.2857},{-13.0001,-0.2857}}, 
    color={0,0,127}));
    connect(Tstbd, tau.Tstbd) 
    annotation(Line(origin={-70,24}, 
    points={{-44.286,-52.5714},{0,-52.5714},{0,52.1905},{45.14286,52.1905}}, 
    color={0,0,127}));
    connect(Tport, tau.Tport) 
    annotation(Line(origin={-70,5}, 
    points={{-44.286,-62.1429},{10,-62.1429},{10,61.6667},{45.14286,61.6667}}, 
    color={0,0,127}));
    connect(m, c.m) 
    annotation(Line(origin={-69,49}, 
  points={{-45.286,36.7143},{-11,36.7143},{-11,-26.1429},{44.9592,-26.1429}}, 
  color={0,0,127}));
    connect(X_G, c.X_G) 
    annotation(Line(origin={-69,31}, 
  points={{-45.286,26.1429},{-17,26.1429},{-17,-13.8572},{44.9592,-13.8572}}, 
  color={0,0,127}));
    connect(Y_G, c.Y_G) 
    annotation(Line(origin={-69,14}, 
  points={{-45.286,14.5714},{-21,14.5714},{-21,-2.57144},{44.9592,-2.57144}}, 
  color={0,0,127}));
    connect(Hydd_Coef, c.Hydd_Coef) 
    annotation(Line(origin={-69,-46}, 
  points={{-45.286,-39.7143},{15,-39.7143},{15,51.7143},{44.9592,51.7143}}, 
  color={0,0,127}));
    connect(V_Local, c.V_Local) 
    annotation(Line(origin={-69,-6}, 
  points={{-45.286,6},{44.9592,6}}, 
  color={0,0,127}));
    connect(c.Cv, matrixMultiply.A) 
    annotation(Line(origin={17,11}, 
points={{-9.00003,0.4286},{9,0.4286},{9,0.4286}}, 
color={0,0,127}));
    connect(V_Local, matrixMultiply.B[:,1]) 
    annotation(Line(origin={-44,-4}, 
    points={{-70.286,4},{-34,4},{-34,-6},{64,-6},{64,5.4286},{70,5.4286}}, 
    color={0,0,127}));
    connect(Hydd_Coef, d.Hydd_Coef) 
    annotation(Line(origin={-70,-66}, 
    points={{-44.286,-19.7143},{16,-19.7143},{16,19.80955},{45.14286,19.80955}}, 
    color={0,0,127}));
    connect(V_Local, d.V_local) 
    annotation(Line(origin={-70,-30}, 
    points={{-44.286,30},{28,30},{28,-30.4762},{45.14286,-30.4762}}, 
    color={0,0,127}));
    connect(d.Dv, matrixMultiply1.A) 
    annotation(Line(origin={17,-53}, 
    points={{-9.00003,-0.3333},{9,-0.3333}}, 
    color={0,0,127}));
    connect(V_Local, matrixMultiply1.B[:,1]) 
    annotation(Line(origin={-44,-40}, 
    points={{-70.286,40},{-34,40},{-34,-40},{64,-40},{64,-23.3333},{70,-23.3333}}, 
    color={0,0,127}));
    connect(tau.T, subSystem1.u1) 
    annotation(Line(origin={34,65}, 
points={{-26,11.1905},{24.4,11.1905},{24.4,-51.9047},{28.2,-51.9047}}, 
color={0,0,127}));
    connect(matrixMultiply.C[:,1], subSystem1.u2) 
    annotation(Line(origin={55,26}, 
points={{-6,-19.5714},{7.2,-19.5714},{7.2,-19.5714}}, 
color={0,0,127}));
    connect(matrixMultiply1.C[:,1], subSystem1.u3) 
    annotation(Line(origin={55,-9}, 
points={{-6,-49.3333},{1.6858,-49.3333},{1.6858,8.76193},{7.2,8.76193}}, 
color={0,0,127}));
    connect(subSystem1.y1, y) 
    annotation(Line(origin={97,23}, 
points={{-11.2,-16.5714},{-7,-16.5714},{-7,-23},{13,-23}}, 
color={0,0,127}));
    end T_C_D;

end Dynamic_Equations;