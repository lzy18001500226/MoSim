model Demo_System "系统示例"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,StartTime=0,StopTime=2,Tolerance=0.0001,Interval=0.001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=2,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="T1", executeTrigger=executeTrigger.None, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 2), zoom_y_l=(-2, 8)),
Plot(y=["combiTable1Ds.y[1]", "const.y"], line_styles=[1, 3], thicknesses=[4, 2], colors=["4278190335", "4294901760"])})
})));
  Controller.PID_Controller pI_Controller(gain(k=60),integrator(k=2),derivative(k=0.1)) 
    annotation (Placement(transformation(origin = {-110, 30}, extent = {{-10, -10}, {10, 10}})));
  Valve.Electrical electrical(resistor(R=50),inductor(L=1.2e-4)) 
    annotation (Placement(transformation(origin={-64,16},
extent={{-10,-10},{10,10}})));
  Valve.ValveBody1 valveBody(emf(k=10),endStop(g_F=6.28318530717959)) 
    annotation (Placement(transformation(origin={-64,-8},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=5) 
    annotation (Placement(transformation(origin={-186,36},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add add(k2=-1) 
    annotation (Placement(transformation(origin={-144,30},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds(table={{0, 0}, {2*3.14, 50}}) 
    annotation (Placement(transformation(origin={-32,-14},
extent={{-10,-10},{10,10}})));
  equation
  connect(const.y, add.u1) 
  annotation(Line(origin={-165,36},
points={{-10,0},{9,0}},
color={0,0,127}));
  connect(pI_Controller.u, add.y) 
  annotation(Line(origin={-127,30},
  points={{6,0},{-6,0}},
  color={0,0,127}));
  connect(pI_Controller.y, electrical.v) 
  annotation(Line(origin={-90,30},
points={{-9,0},{26,0},{26,-3}},
color={0,0,127}));
  connect(electrical.n, valveBody.p) 
  annotation(Line(origin={-40,36},
points={{-16,-30},{-16,-34}},
color={0,0,255}));
  connect(valveBody.n, electrical.p) 
  annotation(Line(origin={-40,24},
points={{-32,-22},{-32,-18}},
color={0,0,255}));
  connect(valveBody.phi, combiTable1Ds.u) 
  annotation(Line(origin={9,30},
points={{-62,-44},{-53,-44}},
color={0,0,127}));
  connect(combiTable1Ds.y[1], add.u2) 
  annotation(Line(origin={-62,10},
points={{41,-24},{52,-24},{52,-52},{-108,-52},{-108,14},{-94,14}},
color={0,0,127}));
  end Demo_System;