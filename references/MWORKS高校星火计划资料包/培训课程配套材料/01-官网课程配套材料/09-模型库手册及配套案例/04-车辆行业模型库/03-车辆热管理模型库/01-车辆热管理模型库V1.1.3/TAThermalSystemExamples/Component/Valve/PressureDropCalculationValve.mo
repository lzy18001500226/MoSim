model PressureDropCalculationValve "压降计算阀门"
  parameter Modelica.Units.SI.Pressure p = 5e5 "入口压力";
  annotation(Documentation(link = "modelica://TAThermalSystem/Resource/Doc/PressureDropValve.html"), Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(0.4019, 0.40198)),
Plot(y=["coolingvalve.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
  TAThermalSystem.Valves.HydraulicValve.FixedValve coolingvalve annotation(Placement(transformation(origin = {2.0, -1.9999999999999998},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(p = 100000) 
    annotation(Placement(transformation(origin = {54.550215646511106, -2.1842887473460726},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = p) 
    annotation(Placement(transformation(origin = {-42.90046133608076, -2.293895452697459},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(coolingvalve.b, Coolant_pT.port_a) 
    annotation(Line(origin = {28.9502156465111, -2.384288747346071},
    points = {{-17.0, 0.0}, {16.0, 0.0}},
    color = {0, 0, 128},
    thickness = 1.0));
  connect(Coolant_pT1.port_a, coolingvalve.a) 
    annotation(Line(origin = {-18.049784353488903, -2.384288747346071},
    points = {{-15.0, 0.0}, {10.0, 0.0}},
    color = {0, 0, 128},
    thickness = 1.0));
end PressureDropCalculationValve;