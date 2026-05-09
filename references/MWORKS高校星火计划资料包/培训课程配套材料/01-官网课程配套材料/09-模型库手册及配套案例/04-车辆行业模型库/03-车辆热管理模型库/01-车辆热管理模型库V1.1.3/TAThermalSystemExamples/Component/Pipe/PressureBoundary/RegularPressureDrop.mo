model RegularPressureDrop "RegularPressureDrop压降方式"
  parameter Modelica.Units.SI.Temperature T_heatin(displayUnit = "degC") = 343.15 "壁面边界温度";
  parameter Modelica.Units.SI.Pressure p_in(displayUnit = "Pa") = 550076 "输入压力";
  TAThermalSystem.Sources.HeatTransfer.FixedTemperature fixedTemperature(T = T_heatin,
    n = 1) annotation (Placement(transformation(origin={-16.3831,39.5887},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(
    p = p_in, title = "水进口") annotation (Placement(transformation(origin = {-63.36515129559615, -3.3365388415381148},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipe coolingPipeBase2(
    useHeatTransfer = true, redeclare Integer calType = 2, h_conv_set = 75,
    CF_PressureLoss = 1,
    p0 = 100000,
    fromDp = true,
    redeclare model Friction =TAThermalSystem.Utilities.PressureDrop.RegularPressureDrop) annotation (Placement(transformation(origin={-3.63907,-3.44091},
extent={{-10.0178,-9.89563},{9.9822,10.1044}})));



  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = 100000, title = "水进口") 
    annotation (Placement(transformation(origin={56.0514,-3.33654},
extent={{-10,-10},{10,10}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/PressureBoundaryRegularPressureDrop.html"
),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(19.5591, 19.5594)),
Plot(y=["coolingPipeBase2.pipeSummary.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
equation
  connect(coolingPipeBase2.b, Coolant_pT1.port_a) 
    annotation (Line(origin={30,-2},
points={{-23.5977,-1.48328},{16.0514,-1.48328},{16.0514,-1.33654}},
color={0,0,128},
thickness=1));
  connect(Coolant_pT.port_a, coolingPipeBase2.a) 
    annotation (Line(origin={-30,-2},
points={{-23.3652,-1.33654},{16.432,-1.33654},{16.432,-1.48328}},
color={0,0,128},
thickness=1));
  connect(fixedTemperature.port[1], coolingPipeBase2.qa) 
    annotation (Line(origin={-11.3831,23.5887},
points={{5,16},{7.94242,16},{7.94242,-15.8123}},
color={191,0,0},
thickness=1));
end RegularPressureDrop;