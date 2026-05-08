package RefrigerantAir "制冷剂空气换热器"
  annotation(__MWORKS(version="2025a"));
  model HXEvaporatorDemo "蒸发器案例"
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    parameter Modelica.SIunits.Temperature TAirIn = 300.15;
    parameter Real CF_refDp = 1;
    parameter Real CF_AirDp = 1;
    parameter Real CF_refHeat = 1;
    parameter Real CF_AirHeat = 1;
    TAThermalSystem.Sources.Air.AirSource_mT airSource(m = 0.124, phi_source = 0.5, T = 308.15) 
      annotation (Placement(transformation(origin = {45.999999999999986, 8.0},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TAThermalSystem.Sources.Air.AirSink_pT airSink 
      annotation (Placement(transformation(origin = {-46.000000000000014, 8.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    annotation (Documentation(link="modelica://TAThermalSystem/Resource/Doc/HXEvaporatorDemo.html"
  ), Protection(access=Access.nonPackageDuplicate), experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(0, 2.5)),
Plot(y=["evaporatorR134a.hXSummary.dp_ref"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(0, 60000)),
Plot(y=["evaporatorR134a.hXSummary.Qdot_refTotal"], thicknesses=[2], colors=["4278190335"])})
})));
    TAThermalSystem.HeatExchangers.Evaporator evaporatorR134a(CF_RefrigerantSidePressureLoss = CF_refDp, CF_AirSidePressureLoss = CF_AirDp, CF_RefrigerantSideHeatTransfer = CF_refHeat, CF_AirSideHeatTransfer = CF_AirHeat) 
      annotation (Placement(transformation(origin = {-7.105427357601002e-15, 2.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Sink_ph flowSink_ph(p0 = 3.04e5) 
      annotation (Placement(transformation(origin = {50.00000000000001, -26.000000000000014},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource_mT(h_source = 277.75e3) annotation (Placement(transformation(origin = {-46.000000000000014, -26.000000000000014},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  equation
    connect(airSource.port_b, evaporatorR134a.air_in) 
      annotation (Line(origin = {22.999999999999986, 8.0},
        points = {{13.0, 0.0}, {-13.0, 0.0}},
        color = {0, 232, 232},
        thickness = 1.0));
    connect(airSink.port_a, evaporatorR134a.air_out) 
      annotation (Line(origin = {-23.000000000000014, 8.0},
        points = {{-13.0, 0.0}, {13.0, 0.0}},
        color = {0, 232, 232},
        thickness = 1.0));
    connect(r134aSource_mT.port_b, evaporatorR134a.a1) 
      annotation (Line(origin = {-23.000000000000014, -15.000000000000014},
        points = {{-13.0, -11.0}, {10.0, -11.0}, {10.0, 11.0}, {13.0, 11.0}},
        color = {0, 128, 0},
        thickness = 1.0));
    connect(flowSink_ph.a, evaporatorR134a.b1) 
      annotation (Line(origin = {24.999999999999986, -15.000000000000014},
        points = {{15.0, -11.0}, {-11.0, -11.0}, {-11.0, 11.0}, {-15.0, 11.0}},
        color = {0, 128, 0},
        thickness = 1.0));
  end HXEvaporatorDemo;
  model MultiHXDemo "多换热器连接"
    extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;
    annotation (Documentation(link="modelica://TAThermalSystem/Resource/Doc/MultiHXDemo.html"
  ),
      Protection(access=Access.nonPackageDuplicate),
      experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 120, Tolerance = 0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2})),__MWORKS(ResultViewerManager(resultViewers={
  ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
  CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 120), zoom_y_l=(-6, 2)),
  Plot(y=["condenser.hXSummary.dp_ref"], colors=["4278190335"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 120), zoom_y_l=(-6, 2)),
  Plot(y=["condenser1.hXSummary.dp_ref"], colors=["4278190335"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 120), zoom_y_l=(-40000, 100000)),
  Plot(y=["condenser1.hXSummary.Qdot_refTotal"], colors=["4278190335"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 120), zoom_y_l=(-40000, 100000)),
  Plot(y=["condenser.hXSummary.Qdot_refTotal"], colors=["4278190335"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(3, 2), zoom_x=(0, 120), zoom_y_l=(-40000, 100000)),
  Plot(y=["condenser2.hXSummary.Qdot_refTotal"], colors=["4278190335"]),
  CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 120), zoom_y_l=(-6, 2)),
  Plot(y=["condenser2.hXSummary.dp_ref"], colors=["4278190335"])})
  })));
    TAThermalSystem.HeatExchangers.Condenser condenser 
      annotation (Placement(transformation(origin = {-58.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.HeatExchangers.Condenser condenser1 
      annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.HeatExchangers.Condenser condenser2 
      annotation (Placement(transformation(origin = {60.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource 
      annotation (Placement(transformation(origin = {-86.0, -38.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Sink_ph r134aSink 
      annotation (Placement(transformation(origin={-43.5774,-64.6388},
  extent={{-10,10},{10,-10}},
  rotation=-90)));
    TAThermalSystem.Sources.Air.AirSource_mT airSource(T = 298.15) 
      annotation (Placement(transformation(origin = {90.0, 6.0},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    TAThermalSystem.Sources.Air.AirSink_pT airSink 
      annotation (Placement(transformation(origin = {-90.0, 6.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource1 
      annotation (Placement(transformation(origin={-28.0491,-34.545},
  extent={{-10,-10},{10,10}})));
    TAThermalSystem.Sources.Refrigerant.Sink_ph r134aSink1 
      annotation (Placement(transformation(origin={14.3735,-61.1838},
  extent={{-10,10},{10,-10}},
  rotation=-90)));
    TAThermalSystem.Sources.Refrigerant.Source_mh r134aSource2 
      annotation (Placement(transformation(origin={36.3399,-26.8525},
  extent={{-10,-10},{10,10}})));
    TAThermalSystem.Sources.Refrigerant.Sink_ph r134aSink2 
      annotation (Placement(transformation(origin={78.7625,-58.5507},
  extent={{-10,10},{10,-10}},
  rotation=-90)));
    equation
    connect(airSource.port_b, condenser2.air_in) 
      annotation (Line(origin = {75.0, 6.0},
        points = {{5.0, 0.0}, {-5.0, 0.0}},
        color = {0, 232, 232},
        thickness = 1.0));
    connect(condenser.air_out, airSink.port_a) 
      annotation (Line(origin = {-74.0, 6.0},
        points = {{6.0, 0.0}, {-6.0, 0.0}},
        color = {0, 232, 232},
        thickness = 1.0));
    connect(r134aSource.port_b, condenser.a1) 
    annotation(Line(origin={-72,-22},
  points={{-4,-16},{4,-16},{4,16}},
  color={0,128,0},
  thickness=1));
    connect(condenser2.air_out, condenser1.air_in) 
    annotation(Line(origin={30,6},
    points={{20,0},{-20,0}},
    color={0,232,232},
    thickness=1));
    connect(condenser1.air_out, condenser.air_in) 
    annotation(Line(origin={-29,6},
    points={{19,0},{-19,0}},
    color={0,232,232},
    thickness=1));
    connect(condenser.b1, r134aSink.a) 
    annotation(Line(origin={-48,-32},
  points={{0,26},{4.42262,26},{4.42262,-22.6388}},
  color={0,128,0},
  thickness=1));
    connect(r134aSource1.port_b, condenser1.a1) 
    annotation(Line(origin={-14,-20},
    points={{-4.04908,-14.545},{4,-14.545},{4,14}},
    color={0,128,0},
    thickness=1));
    connect(condenser1.b1, r134aSink1.a) 
    annotation(Line(origin={12,-29},
    points={{-2,23},{2.37352,23},{2.37352,-22.1838}},
    color={0,128,0},
    thickness=1));
    connect(r134aSource2.port_b, condenser2.a1) 
    annotation(Line(origin={48,-16},
    points={{-1.66011,-10.8525},{2,-10.8525},{2,10}},
    color={0,128,0},
    thickness=1));
    connect(condenser2.b1, r134aSink2.a) 
    annotation(Line(origin={74,-25},
  points={{-4,19},{4.76249,19},{4.76249,-23.5507}},
  color={0,128,0},
  thickness=1));
    end MultiHXDemo;
  end RefrigerantAir;