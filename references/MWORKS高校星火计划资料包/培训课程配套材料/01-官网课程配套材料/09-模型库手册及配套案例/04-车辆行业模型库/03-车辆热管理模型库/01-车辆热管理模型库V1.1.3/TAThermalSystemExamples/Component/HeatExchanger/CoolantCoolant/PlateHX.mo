model PlateHX "板式换热器"
  extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
 TAThermalSystem.HeatExchangers.Plate.DiscreteChiller discreteChiller(volChannel_a=0.0001,volChannel_b=0.0001,diam_a=0.009,xArea_a=0.001,diam_b=0.009,xArea_b=0.001,nChannel_a=5,nChannel_b=4) 
    annotation (Placement(transformation(origin={-2.04837,4.20089},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(title = "水出口", mflow = 0.1, T_source = 273.15) 
    annotation (Placement(transformation(origin={-47.4818,-11.0386},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT(title = "水出口", p = 4.999999999999999e5,
    T_in(start
       = 293.15)) 
    annotation (Placement(transformation(origin={31.3225,-7.4877},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT1(title = "水出口", mflow = 0.1, T_source = 303.15) 
    annotation (Placement(transformation(origin={31.9922,19.5241},
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank Coolant_pT1(title = "水出口", p = 4.999999999999999e5,
    T_in(start
       = 293.15)) 
    annotation (Placement(transformation(origin={-47.1432,18.0102},
extent={{10,-10},{-10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})),experiment(Algorithm=Dassl,NumberOfIntervals=500,StartTime=0,StopTime=100,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",
NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=100,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(-1500, 1500)),
Plot(y=["discreteChiller.Chiller_a.pipeSummary.Qdot", "discreteChiller.Chiller_b.pipeSummary.Qdot"], thicknesses=[2, 2], colors=["4278190335", "4294901760"])})
})),Documentation(link="modelica://TAThermalSystem/Resource/Doc/PlateHX.html"),Protection(access=Access.nonPackageDuplicate));
equation
  connect(Coolant_mT.port_b, discreteChiller.c) 
  annotation(Line(origin={-23.4003,-3.89281},
points={{-14.0815,-7.14577},{-14.0815,2.20695},{11.4048,2.20695}},
color={0,170,255},
thickness=1));
  connect(discreteChiller.d, Coolant_pT.port_a) 
  annotation(Line(origin={18.5997,-3.89281},
points={{-10.8883,2.03285},{12.7228,2.03285},{12.7228,-3.59489}},
color={0,170,255},
thickness=1));
  connect(discreteChiller.b, Coolant_pT1.port_a) 
  annotation(Line(origin={-29.4003,14.1072},
points={{17.3461,-4.04644},{17.3461,7.25768},{-17.7429,7.25768},{-17.7429,3.903}},
color={0,170,255},
thickness=1));
  connect(Coolant_mT1.port_b, discreteChiller.a) 
  annotation(Line(origin={14.5997,15.1072},
points={{7.39243,4.4169},{-6.81784,4.4169},{-6.81784,-5.33679}},
color={0,170,255},
thickness=1));

end PlateHX;