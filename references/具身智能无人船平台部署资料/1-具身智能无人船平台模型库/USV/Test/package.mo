package Test "测试"
  model matricesDivision
    Utilities.Math.MatrixDivision matrixDivision 
      annotation (Placement(transformation(origin={2,2}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant Thrust_configuration_matrix[2,2](k={{1,1},{0.395,-0.395}}) 
      annotation (Placement(transformation(origin={-48,-20}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const[2](k={2,2}) 
      annotation (Placement(transformation(origin={-48,18}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2})));
  equation
    connect(matrixDivision.B, Thrust_configuration_matrix.y) 
    annotation(Line(origin={-23,-3}, 
points={{13,0},{1,0},{1,-17},{-14,-17}}, 
color={0,0,127}));
    connect(const.y, matrixDivision.A[:,1]) 
    annotation(Line(origin={-23,13}, 
    points={{-14,5},{-7,5},{-7,-6},{13,-6}}, 
    color={0,0,127}));
    end matricesDivision;
  model matricesMultiply
    Utilities.Math.MatrixMultiply matrixMultiply 
      annotation (Placement(transformation(origin={2,2}, 
extent={{-34,-34},{34,34}})));
    Modelica.Blocks.Sources.Constant Thrust_configuration_matrix1[3,3](k={{1,2,3},{0,5,6},{0,0,9}}) 
      annotation (Placement(transformation(origin={-132,19}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Sources.Constant const[3](k={2,2,2}) 
      annotation (Placement(transformation(origin={-132,-52}, 
extent={{-20,-20},{20,20}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(Thrust_configuration_matrix1.y, matrixMultiply.A) 
    annotation(Line(origin={-74,19}, 
    points={{-36,0},{35.2,0}}, 
    color={0,0,127}));
    connect(const.y, matrixMultiply.B[:,1]) 
    annotation(Line(origin={-74,-33}, 
    points={{-36,-19},{4,-19},{4,18},{35.2,18}}, 
    color={0,0,127}));

  end matricesMultiply;
  model MatrixAdd
    Utilities.Math.MatrixAdd matrixAdd 
      annotation (Placement(transformation(origin={0,12}, 
extent={{-20,-20},{20,20}})));
    Modelica.Blocks.Sources.Constant const[3,3](k={{1,2,3},{4,5,6},{7,8,9}}) 
      annotation (Placement(transformation(origin={-72,36}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const1[3,3](k={{1,2,3},{4,5,6},{7,8,9}}) 
      annotation (Placement(transformation(origin={-72,-10}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2})));
  equation
    connect(const.y, matrixAdd.A) 
    annotation(Line(origin={-42,29}, 
    points={{-19,7},{2,7},{2,-7},{18,-7}}, 
    color={0,0,127}));
    connect(const1.y, matrixAdd.B) 
    annotation(Line(origin={-42,-4}, 
    points={{-19,-6},{2,-6},{2,6},{18,6}}, 
    color={0,0,127}));

  end MatrixAdd;
  model Control_Allocation
    Components.Control.Components.Control_Allocation control_Allocation 
      annotation (Placement(transformation(origin = {20, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant const[2](k={2,2}) 
      annotation (Placement(transformation(origin={-52,0}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2})));
  equation
    connect(control_Allocation.tau, const.y) 
    annotation(Line(origin={-16,0}, 
    points={{24,0},{-25,0}}, 
    color={0,0,127}));

  end Control_Allocation;
  model Signed_Square_Root
    Utilities.Math.Signed_Square_Root signed_Square_Root[2] 
      annotation (Placement(transformation(origin={14,5.5}, 
extent={{-36,-35.5},{36,35.5}})));
    Modelica.Blocks.Sources.Pulse pulse[2](offset=4,amplitude=-13) 
      annotation (Placement(transformation(origin={-100,5.5}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.01,StartTime=0,StopTime=100,Tolerance=0.0001));
  equation
    connect(pulse.y, signed_Square_Root.u) 
    annotation(Line(origin={-64,-18}, 
points={{-25,23.5},{34.8,23.5}}, 
color={0,0,127}));
    end Signed_Square_Root;
  model Control_Allocation2
    Components.Control.Control_Allocation control_Allocation 
      annotation (Placement(transformation(origin={-45,-5}, 
extent={{-15,-15},{15,15}})));
    Modelica.Blocks.Sources.Constant const(k=52.44690674053555) 
      annotation (Placement(transformation(origin={-138,34}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const1(k=33.12705285612364) 
      annotation (Placement(transformation(origin={-138,-42}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2})));
  equation
    connect(const1.y, control_Allocation.yaw) 
    annotation(Line(origin={-95,-27}, 
    points={{-32,-15},{-5,-15},{-5,14.5},{32,14.5}}, 
    color={0,0,127}));
    connect(const.y, control_Allocation.surge) 
    annotation(Line(origin={-95,18}, 
    points={{-32,16},{-5,16},{-5,-15.5},{32,-15.5}}, 
    color={0,0,127}));

  end Control_Allocation2;
  model power
    Utilities.Math.power power1(n=-2) 
      annotation (Placement(transformation(origin = {-10, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant const(k=-2) 
      annotation (Placement(transformation(origin={-102,0}, 
extent={{-10,-10},{10,10}})));
  equation
    connect(power1.u, const.y) 
    annotation(Line(origin={-56,0}, 
    points={{34,0},{-35,0}}, 
    color={0,0,127}));

  end power;
  model Hydrodynamic_Coefficient
    Components.Hydrodynamics.Hydrodynamic_Coefficients hydrodynamic_Coefficients 
      annotation (Placement(transformation(origin={-39,15}, 
extent={{-25,-25},{25,25}})));
    Modelica.Blocks.Sources.Constant const(k=1) 
      annotation (Placement(transformation(origin={-90,37.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const1(k=2) 
      annotation (Placement(transformation(origin={-90,32.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const2(k=3) 
      annotation (Placement(transformation(origin={-90,27.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const3(k=4) 
      annotation (Placement(transformation(origin={-90,22.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const4(k=5) 
      annotation (Placement(transformation(origin={-90,17.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const5(k=6) 
      annotation (Placement(transformation(origin={-90,12.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const6(k=7) 
      annotation (Placement(transformation(origin={-90,7.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const7(k=8) 
      annotation (Placement(transformation(origin={-90,2.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const8(k=9) 
      annotation (Placement(transformation(origin={-90,-2.5}, 
extent={{-2,-2},{2,2}})));
    Modelica.Blocks.Sources.Constant const9[3](k={1,2,3}) 
      annotation (Placement(transformation(origin={-90,-7.5}, 
extent={{-2,-2},{2,2}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(hydrodynamic_Coefficients.m, const.y) 
    annotation(Line(origin={-77,38}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.LCG, const1.y) 
    annotation(Line(origin={-77,33}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.rho, const2.y) 
    annotation(Line(origin={-77,28}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.L, const3.y) 
    annotation(Line(origin={-77,23}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.C_d, const4.y) 
    annotation(Line(origin={-77,18}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.T, const5.y) 
    annotation(Line(origin={-77,13}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.B_hull, const6.y) 
    annotation(Line(origin={-77,8}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.Xu, const7.y) 
    annotation(Line(origin={-77,3}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(hydrodynamic_Coefficients.Xuu, const8.y) 
    annotation(Line(origin={-77,-2}, 
    points={{10.5,-0.5},{-10.8,-0.5}}, 
    color={0,0,127}));
    connect(const9.y, hydrodynamic_Coefficients.V_local) 
    annotation(Line(origin={-77,-7}, 
    points={{-10.8,-0.5},{10.5,-0.5}}, 
    color={0,0,127}));

  end Hydrodynamic_Coefficient;
  model M
    Components.Dynamic_Equations.M m 
      annotation (Placement(transformation(origin={-12,14}, 
extent={{-30,-30},{30,30}})));
    Modelica.Blocks.Sources.Constant const(k=50) 
      annotation (Placement(transformation(origin = {-130, 50}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant const1(k=0) 
      annotation (Placement(transformation(origin={-130,14}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const2(k=0) 
      annotation (Placement(transformation(origin={-130,-22}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const3(k=3.1) 
      annotation (Placement(transformation(origin={-130,-58}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const4[19](k={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}) 
      annotation (Placement(transformation(origin={-130,-94}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(const.y, m.m) 
    annotation(Line(origin={-83,44}, 
    points={{-36,6},{13,6},{13,-6},{35,-6}}, 
    color={0,0,127}));
    connect(const1.y, m.X_G) 
    annotation(Line(origin={-83,20}, 
    points={{-36,-6},{-11,-6},{-11,6},{35,6}}, 
    color={0,0,127}));
    connect(const2.y, m.Y_G) 
    annotation(Line(origin={-83,-4}, 
    points={{-36,-18},{-3,-18},{-3,18},{35,18}}, 
    color={0,0,127}));
    connect(const3.y, m.I_z) 
    annotation(Line(origin={-83,-28}, 
    points={{-36,-30},{3,-30},{3,30},{35,30}}, 
    color={0,0,127}));
    connect(const4.y, m.Hydd_Coef) 
    annotation(Line(origin={-83,-52}, 
    points={{-36,-42},{11,-42},{11,42},{35,42}}, 
    color={0,0,127}));

  end M;
  model Tau
    Components.Dynamic_Equations.Components.Tau tau 
      annotation (Placement(transformation(origin={-18,20}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const(k=0.64) 
      annotation (Placement(transformation(origin={-92,50}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const1(k=1) 
      annotation (Placement(transformation(origin={-92,13.3333}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const2(k=1) 
      annotation (Placement(transformation(origin={-92,-23.3333}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(const.y, tau.B) 
    annotation(Line(origin={-55,38}, 
    points={{-26,12},{15,12},{15,-11.33333},{25,-11.33333}}, 
    color={0,0,127}));
    connect(const1.y, tau.Tstbd) 
    annotation(Line(origin={-55,17}, 
    points={{-26,-3.6667},{-5,-3.6667},{-5,3},{25,3}}, 
    color={0,0,127}));
    connect(const2.y, tau.Tport) 
    annotation(Line(origin={-55,-5}, 
    points={{-26,-18.3333},{5,-18.3333},{5,18.33333},{25,18.33333}}, 
    color={0,0,127}));

  end Tau;
  model C
    Components.Dynamic_Equations.Components.C c 
      annotation (Placement(transformation(origin={-38,10}, 
extent={{-32,-33},{32,33}})));
    Modelica.Blocks.Sources.Constant const(k=50) 
      annotation (Placement(transformation(origin={-144,62}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const1(k=0) 
      annotation (Placement(transformation(origin={-144,33}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const2(k=0) 
      annotation (Placement(transformation(origin={-144,4}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const4[19](k={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}) 
      annotation (Placement(transformation(origin={-144,-25}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const3[3](k={1,2,3}) 
      annotation (Placement(transformation(origin={-144,-68}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(const.y, c.m) 
    annotation(Line(origin={-104,49}, 
    points={{-29,13},{14,13},{14,-12.6},{29.4286,-12.6}}, 
    color={0,0,127}));
    connect(const1.y, c.X_G) 
    annotation(Line(origin={-104,28}, 
    points={{-29,5},{4,5},{4,-4.8},{29.4286,-4.8}}, 
    color={0,0,127}));
    connect(const2.y, c.Y_G) 
    annotation(Line(origin={-104,7}, 
    points={{-29,-3},{-6,-3},{-6,3},{29.4286,3}}, 
    color={0,0,127}));
    connect(const4.y, c.Hydd_Coef) 
    annotation(Line(origin={-104,-14}, 
    points={{-29,-11},{0,-11},{0,10.8},{29.4286,10.8}}, 
    color={0,0,127}));
    connect(const3.y, c.V_Local) 
    annotation(Line(origin={-104,-42}, 
    points={{-29,-26},{14,-26},{14,25.6},{29.4286,25.6}}, 
    color={0,0,127}));
    end C;
  model D
    Components.Dynamic_Equations.Components.D d 
      annotation (Placement(transformation(origin={-26,-6}, 
extent={{-40,-40},{40,40}})));
    Modelica.Blocks.Sources.Constant const4[19](k={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}) 
      annotation (Placement(transformation(origin={-160,14}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const3[3](k={1,2,3}) 
      annotation (Placement(transformation(origin={-160,-26}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
    grid={2,2})));
  equation
    connect(const4.y, d.Hydd_Coef) 
    annotation(Line(origin={-111,16}, 
points={{-38,-2},{37,-2},{37,-2}}, 
color={0,0,127}));
    connect(const3.y, d.V_local) 
    annotation(Line(origin={-111,-26}, 
    points={{-38,0},{37,0}}, 
    color={0,0,127}));

  end D;
  model TCD
    Components.Dynamic_Equations.T_C_D t_C_D 
      annotation (Placement(transformation(origin={-15,-15}, 
extent={{-45,-45},{45,45}})));
    Modelica.Blocks.Sources.Constant const(k=50) 
      annotation (Placement(transformation(origin={-172,74}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const1(k=0) 
      annotation (Placement(transformation(origin={-172,33.85713}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const2(k=0) 
      annotation (Placement(transformation(origin={-172,-2.14287}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const3[3](k={1,2,3}) 
      annotation (Placement(transformation(origin={-172,-38.1429}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const4(k=1) 
      annotation (Placement(transformation(origin={-172,-74.1429}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const5(k=1) 
      annotation (Placement(transformation(origin={-172,-110.143}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const6[19](k={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}) 
      annotation (Placement(transformation(origin={-172,-146.1431}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  equation
    connect(const.y, t_C_D.m) 
    annotation(Line(origin={-114,49}, 
    points={{-47,25},{-6,25},{-6,-25.428565},{47.5713,-25.428565}}, 
    color={0,0,127}));
    connect(const1.y, t_C_D.X_G) 
    annotation(Line(origin={-114,22}, 
    points={{-47,11.8571},{-16,11.8571},{-16,-11.285695},{47.5713,-11.285695}}, 
    color={0,0,127}));
    connect(const2.y, t_C_D.Y_G) 
    annotation(Line(origin={-114,-2}, 
    points={{-47,-0.14287},{47.5713,-0.14287},{47.5713,-0.14287}}, 
    color={0,0,127}));
    connect(const3.y, t_C_D.V_Local) 
    annotation(Line(origin={-114,-27}, 
    points={{-47,-11.1429},{-16,-11.1429},{-16,12},{47.5713,12}}, 
    color={0,0,127}));
    connect(const4.y, t_C_D.Tstbd) 
    annotation(Line(origin={-114,-51}, 
    points={{-47,-23.1429},{-6,-23.1429},{-6,23.1429},{47.5713,23.1429}}, 
    color={0,0,127}));
    connect(const5.y, t_C_D.Tport) 
    annotation(Line(origin={-114,-75}, 
    points={{-47,-35.1429},{4,-35.1429},{4,34.2857},{47.5713,34.2857}}, 
    color={0,0,127}));
    connect(const6.y, t_C_D.Hydd_Coef) 
    annotation(Line(origin={-114,-100}, 
    points={{-47,-46.1431},{24,-46.1431},{24,46.428565},{47.5713,46.428565}}, 
    color={0,0,127}));

  end TCD;
  model Dynamic_Model_Equation
    Components.Dynamic_Equations.Dynamic_Model_Equations dynamic_Model_Equations 
      annotation (Placement(transformation(origin={30,-1.77636e-15}, 
extent={{-30,-30},{30,30}})));
    Modelica.Blocks.Sources.Constant const4(k=1) 
      annotation (Placement(transformation(origin={-112,58.5001}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const5(k=1) 
      annotation (Placement(transformation(origin={-112,-7.5}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const(k=50) 
      annotation (Placement(transformation(origin={-112,25.50005}, 
extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Sources.Constant const6[19](k={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}) 
      annotation (Placement(transformation(origin={-112,-40.50005}, 
extent={{-10,-10},{10,10}})));
    annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Rkfix4,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=10,Tolerance=1e-06));
  equation
    connect(const4.y, dynamic_Model_Equations.Tstbd) 
    annotation(Line(origin={-53,41}, 
    points={{-48,17.5001},{23,17.5001},{23,-18.5},{47,-18.5}}, 
    color={0,0,127}));
    connect(dynamic_Model_Equations.Tport, const5.y) 
    annotation(Line(origin={-53,-8}, 
    points={{47,0.5},{-48,0.5}}, 
    color={0,0,127}));
    connect(const.y, dynamic_Model_Equations.Mass) 
    annotation(Line(origin={-53,17}, 
    points={{-48,8.50005},{3,8.50005},{3,-9.5},{47,-9.5}}, 
    color={0,0,127}));
    connect(const6.y, dynamic_Model_Equations.Hydd_Coef) 
    annotation(Line(origin={-53,-32}, 
    points={{-48,-8.50005},{3,-8.50005},{3,9.5},{47,9.5}}, 
    color={0,0,127}));
    end Dynamic_Model_Equation;
  model formatDegreeTest
    annotation(__MWORKS(version = "2025a"));
    Real a = 350;
    Real b = -350;
    Real c = 390;
    Real d = -390;
    Real ra;
    Real rb;
    Real rc;
    Real rd;
  equation
    ra = USV.Components.Navigation.Functions.formatDegree(a);
    rb = USV.Components.Navigation.Functions.formatDegree(b);
    rc = USV.Components.Navigation.Functions.formatDegree(c);
    rd = USV.Components.Navigation.Functions.formatDegree(d);
  end formatDegreeTest;
end Test;