model FourCylinderEngineLubricationCircuit "四缸发动机润滑系统"
import Modelica.Constants.pi;
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {167, 98, 0}, 
    fillColor = {167, 98, 0}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {167, 98, 0}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {167, 98, 0}, 
    thickness = 5.0)}), 
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 10, Tolerance = 0.0001), 
    Diagram(coordinateSystem(extent = {{-340.0, -220.0}, {340.0, 220.0}}, 
    grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/FourCylinderEngineLubricationCircuit.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.5, 2)), 
Plot(y=["hydraulicBearing_bearingfeeding2.port_A.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量/(kg/s)", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(-0.01, 0.07)), 
Plot(y=["symThrottleValve2.port_A.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(-0.05, 0.3)), 
Plot(y=["symThrottleValve2.port_A.p"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量/(kg/s)", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-5e-05, 0.00025)), 
Plot(y=["hydraulicBearing_bearingfeeding2.port_A.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量/(kg/s)", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 3), zoom_x=(0, 10), zoom_y_l=(0.00078, 0.00094)), 
Plot(y=["hydraulicBearing_bearingfeeding9.port_A.m_flow"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 3), zoom_x=(0, 10), zoom_y_l=(-0.2, 1.4)), 
Plot(y=["hydraulicBearing_bearingfeeding9.port_A.p"], colors=["4278190335"])})
})));
  TYThermalHydraulics.Pumps.SpecialPumps.VolumetricPump volumetric_Pump(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-79.99645845161285, -183.63336472912619}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Sources.Tank tank(T_load = 313.15, 
    p_load = 0, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-79.99645845161285, -201.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed(phi(fixed = true), exact = false) 
    annotation(Placement(transformation(origin = {-105.99645845161305, -183.63336472912619}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C(d = mainDatas.Dmain, length = 0.2, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-79.99645845161294, -155.63336472912613}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.GeneralBend generalBend(D = mainDatas.Dmain, delta_degree = 1.39626340159546, rc = 0.015, Re_crit = 200, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-77.13147770894128, -127.63336472912619}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C1(d = mainDatas.Dmain, length = 0.77, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-51.99645845161308, -124.54445490970869}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.GeneralBend generalBend1(D = mainDatas.Dmain, rc = 0.015, Re_crit = 200, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-26.861439194284742, -127.40943565238032}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C2(d = mainDatas.Dmain, length = 0.031, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-23.772529374867275, -155.63336472912613}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Auxiliaries.Resistive.Filter filter(qchar = 0.000666666666666667, Method = "Q/dp", 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-23.772529374867275, -183.85729380587208}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C3(d = mainDatas.Dmain, length = 0.031, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-5.996458451613044, -201.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.GeneralBend generalBend2(D = mainDatas.Dmain, delta_degree = 0.523598775598299, rc = 0.015, Re_crit = 200, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {19.77961247164123, -198.54445490970875}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C4(d = mainDatas.Dmain, length = 0.1, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {22.868522291058717, -169.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AbruptPipe abruptPipe(ds = mainDatas.Dmainbra, dl = mainDatas.Dmain, Recrit = 100, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {22.868522291058717, -140.72227454854374}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C5(d = mainDatas.Dmainbra, length = 0.026, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {22.868522291058717, -111.81118436796108}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg(T_init = 313.15, dm = mainDatas.Dmainbra, ds = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {22.868522291058753, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C6(d = mainDatas.Dmainbra, length = 0.021, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-5.996458451613037, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg1(dm = mainDatas.Dmainbra, ds = mainDatas.Dmainbear, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-34.86143919428487, -82.90009418737858}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C7(d = mainDatas.Dmainbear, length = 0.033, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-34.86143919428483, -55.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AbruptPipe abruptPipe1(dl = mainDatas.Dmainbear, ds = mainDatas.Dmainbear1, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-34.861439194284856, -28.36663527087378}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C8(d = mainDatas.Dmainbear1, length = 0.03, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-34.861439194284856, 1.8166823645631034}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C9(d = 0.01, length = 0.021, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-63.72641993695663, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg2(ds = mainDatas.Dpiston, ks = 1.4, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-92.5914006796284, -82.90009418737858}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C10(d = mainDatas.Dpiston, length = 0.01, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-92.5914006796284, -55.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-92.5914006796284, -28.36663527087378}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C11(d = mainDatas.Dmainbra, length = 0.022, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-121.45638142230007, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg3(ds = mainDatas.Dmainbear, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-150.32136216497196, -82.90009418737858}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C12(d = mainDatas.Dmainbear, length = 0.033, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-150.32136216497187, -55.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AbruptPipe abruptPipe2(dl = mainDatas.Dmainbear, ds = mainDatas.Dmainbear1, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-150.32136216497187, -28.366635270873786}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C13(d = mainDatas.Dmainbra, length = 0.044, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-175.1314777089413, -82.90009418737866}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg4(ds = mainDatas.Dpiston, ks = 1.4, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-203.99645845161302, -82.90009418737858}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C14(d = mainDatas.Dpiston, length = 0.01, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-203.99645845161305, -55.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-203.99645845161305, -28.366635270873786}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C15(d = mainDatas.Dmainbra, length = 0.022, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-236.99645845161302, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.AxesIntersectingHoles intersectingHoleswith2ports90degAxesIntersecting(d = mainDatas.Dmainbra, kAB = 13, kBA = 13, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-269.9964584516131, -82.91711076196422}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C16(d = mainDatas.Dmainbear, length = 0.033, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-269.9964584516131, -55.63336472912613}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AbruptPipe abruptPipe3(dl = mainDatas.Dmainbear, ds = mainDatas.Dmainbear1, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) annotation(Placement(transformation(origin = {-269.9964584516131, -28.36663527087378}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding(coordination = "polar", 
    filmAssumption = "2piFilm", with = false, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-130.00000000000009, 39.99999999999999}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.CentrifugalPipes_CRC centrifugalPipes_CRC(d = mainDatas.Dconrod, rposi = 0, rposo = 0.025, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-296.0, 9.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding1(coordination = "polar", 
    filmAssumption = "2piFilm", with = false, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-255.99999999999994, 39.99999999999999}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_journalfeeding hydraulicBearing_journalfeeding(coordination = "polar", 
    db = 0.045, lb = 0.012, dh = mainDatas.Dconrod, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-296.0, 40.00000000000003}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_journalfeeding hydraulicBearing_journalfeeding1(coordination = "polar", 
    db = 0.045, lb = 0.012, dh = mainDatas.Dconrod, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-164.00000000000006, 39.99999999999995}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.CentrifugalPipes_CRC centrifugalPipes_CRC1(d = mainDatas.Dconrod, rposi = 0, rposo = 0.025, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-164.00000000000006, 9.633364729126185}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding2(coordination = "polar", 
    filmAssumption = "2piFilm", with = false, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-34.86498074267186, 39.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank1(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-276.00000000000006, 65.63336472912621}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Sources.Tank tank2(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-146.00000000000003, 65.63336472912621}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Sources.Tank tank3(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-34.864980742671946, 70.36663527087381}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Sources.Tank tank4(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-204.00000000000014, -13.633364729126193}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Sources.Tank tank5(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-92.5914006796284, -13.633364729126193}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C17(d = mainDatas.Dmainbra, length = 0.05, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {51.73350303373059, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg5(ds = mainDatas.Dpiston, ks = 1.4, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {80.00354154838706, -82.90009418737858}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C19(d = mainDatas.Dpiston, length = 0.01, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {80.00354154838709, -55.63336472912613}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve2(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {80.00354154838709, -28.366635270873786}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank6(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {80.00354154838706, -13.633364729126193}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg6(ds = mainDatas.Dmainbear, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {135.67863783502827, -82.90009418737856}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C20(d = mainDatas.Dmainbear, length = 0.033, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {135.67863783502824, -55.63336472912613}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AbruptPipe abruptPipe4(dl = mainDatas.Dmainbear, ds = mainDatas.Dmainbear1, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {135.67863783502824, -28.366635270873786}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C21(d = mainDatas.Dmainbra, length = 0.044, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {106.86852229105868, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding3(coordination = "polar", 
    filmAssumption = "2piFilm", with = false, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {156.0, 52.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_journalfeeding hydraulicBearing_journalfeeding2(coordination = "polar", 
    db = 0.045, lb = 0.012, dh = mainDatas.Dconrod, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {122.0, 51.99999999999998}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.CentrifugalPipes_CRC centrifugalPipes_CRC2(d = mainDatas.Dconrod, rposi = 0, rposo = 0.025, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {122.0, 19.633364729126193}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank7(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {139.6750962866412, 75.09990581262136}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg7(ks = 1.4, ds = mainDatas.Dpiston, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {194.00354154838706, -82.90009418737856}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C22(d = mainDatas.Dpiston, length = 0.01, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {194.00354154838712, -55.63336472912607}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve3(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {194.00354154838712, -28.36663527087378}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank8(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {194.00354154838706, -13.633364729126193}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C23(d = mainDatas.Dmainbra, length = 0.022, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {162.0, -82.90009418737856}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg8(ds = mainDatas.Dmainbear, T_init = 313.15, dm = mainDatas.Dmainbra, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {251.67863783502807, -82.90009418737858}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C18(d = mainDatas.Dmainbear, length = 0.033, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {251.67863783502807, -55.633364729126214}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AbruptPipe abruptPipe5(dl = mainDatas.Dmainbear, ds = mainDatas.Dmainbear1, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {251.67863783502807, -28.36663527087383}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C24(d = mainDatas.Dmainbra, length = 0.044, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {222.00354154838706, -82.90009418737858}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding4(coordination = "polar", 
    filmAssumption = "2piFilm", with = false, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {272.0, 52.00000000000001}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_journalfeeding hydraulicBearing_journalfeeding3(coordination = "polar", 
    db = 0.045, lb = 0.012, dh = mainDatas.Dconrod, rc = 8e-5, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {237.99999999999997, 52.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.CentrifugalPipes_CRC centrifugalPipes_CRC3(d = mainDatas.Dconrod, rposi = 0, rposo = 0.025, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {237.99999999999997, 19.633364729126214}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank9(T_load = 283.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {253.67863783502813, 75.09990581262136}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C25(d = mainDatas.Dmainbra, length = 0.022, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {287.84108969170757, -82.90009418737856}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.AxesIntersectingHoles intersectingHoleswith2ports90degAxesIntersecting1(d = mainDatas.Dmainbra, kAB = 13, kBA = 13, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {332.00354154838715, -82.90009418737856}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C26(length = 0.021, d = mainDatas.Dmainbra, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {332.00354154838703, -41.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.HolesandPipes.AnnularPipe annularPipe(dinn = 0.015, dout = 0.02, length = 0.4, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {332.0, 27.633364729126207}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C27(length = 0.015, d = mainDatas.Dcam, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {332.0, 83.09990581262136}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.AxesIntersectingHoles intersectingHoleswith2ports90degAxesIntersecting2(d = mainDatas.Dcam, kAB = 13, kBA = 13, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {332.003541548387, 107.61634815454056}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg9(dm = mainDatas.Dcam, ds = mainDatas.Dcambear, ks = 0.6, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {145.7299614853434, 107.6333647291262}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C28(d = mainDatas.Dcambear, length = 0.025, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {145.7299614853434, 134.90009418737856}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C29(d = mainDatas.Dcam, length = 0.0925, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {116.86498074267163, 107.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg10(dm = mainDatas.Dcam, ds = mainDatas.Dcambear, ks = 0.6, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {87.99999999999983, 107.6333647291262}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C30(d = mainDatas.Dcambear, length = 0.025, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {87.99999999999983, 134.90009418737856}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C31(d = mainDatas.Dcam, length = 0.0925, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {59.13501925732812, 107.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg11(ds = mainDatas.Dcambear, dm = mainDatas.Dcam, ks = 0.6, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {30.270038514656335, 107.6333647291262}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C32(length = 0.025, d = mainDatas.Dcambear, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {30.27003851465639, 134.90009418737856}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C33(length = 0.089, d = mainDatas.Dcam, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {5.459922970686932, 107.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.Tjunction90deg tjunction90deg12(dm = mainDatas.Dcam, ds = mainDatas.Dcambear, ks = 0.6, T_init = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-23.4050577719848, 107.6333647291262}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C34(d = mainDatas.Dcambear, length = 0.025, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-23.405057771984744, 134.90009418737856}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C35(d = mainDatas.Dcam, length = 0.0925, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-56.40505777198476, 107.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Resistances.Junctions.AxesIntersectingHoles intersectingHoleswith2ports90degAxesIntersecting3(d = mainDatas.Dcam, kAB = 1, kBA = 1, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-89.40505777198476, 107.61634815454056}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = -90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C36(d = mainDatas.Dcambear, length = 0.025, Type = "刚性管路", Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-89.40505777198476, 134.90009418737867}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding5(coordination = "polar", 
    db = 0.025, lb = 0.01, dh = mainDatas.Dcambear, thetah = 3.14159265358979, rc = 8e-5, 
    filmAssumption = "2piFilm", 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-89.40505777198476, 175.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank10(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-89.40505777198493, 195.63336472912613}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding6(coordination = "polar", 
    db = 0.025, lb = 0.01, dh = mainDatas.Dcambear, thetah = 3.14159265358979, rc = 8e-5, 
    filmAssumption = "2piFilm", 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-23.40505777198483, 175.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank11(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {-23.405057771984914, 195.63336472912613}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding7(coordination = "polar", 
    db = 0.025, lb = 0.01, dh = mainDatas.Dcambear, thetah = 3.14159265358979, rc = 8e-5, 
    filmAssumption = "2piFilm", 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {30.27003851465642, 175.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank12(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {30.27003851465632, 195.63336472912613}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding8(coordination = "polar", 
    db = 0.025, lb = 0.01, dh = mainDatas.Dcambear, thetah = 3.14159265358979, rc = 8e-5, 
    filmAssumption = "2piFilm", 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {87.99999999999983, 175.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank13(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {87.99999999999977, 195.63336472912613}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Resistances.PlainJournalBearings.HydraulicBearing_bearingfeeding hydraulicBearing_bearingfeeding9(coordination = "polar", 
    db = 0.025, lb = 0.01, dh = mainDatas.Dcambear, thetah = 3.14159265358979, rc = 8e-5, 
    filmAssumption = "2piFilm", 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {145.7299614853434, 175.63336472912616}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  TYThermalHydraulics.Sources.Tank tank14(T_load = 313.15, 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {145.7299614853434, 195.63336472912613}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C37(d = mainDatas.Dcam, length = 0.085, 
    Type = "刚性管路", 
    Tin(start = 313.15), 
  redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._15W40) 
    annotation(Placement(transformation(origin = {175.99999999999997, 107.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  FourCylinderEngineLubricationCircuit.MainDatas mainDatas 
    annotation(Placement(transformation(origin = {-256.0000000000001, 124.90009418737868}, 
    extent = {{-20.0, -20.0}, {20.0, 20.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression(y = 0.5 * mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {-175.13501925732845, 156.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {-175.13501925732845, 191.63336472912613}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression2(y = mainDatas.w) 
    annotation(Placement(transformation(origin = {-141.99645845161294, -183.63336472912619}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression3(y = mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {-326.00000000000006, 25.633364729126214}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression4(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {-326.00000000000006, 51.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression5(y = mainDatas.wb) 
    annotation(Placement(transformation(origin = {-277.99645845161297, 9.6333647291262}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression6(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {-216.0, 63.12485644183337}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression7(y = mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {-216.0, 17.633364729126203}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression8(y = mainDatas.wb) 
    annotation(Placement(transformation(origin = {-148.00000000000003, 17.633364729126207}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression9(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {-84.64272432994349, 63.12485644183337}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression10(y = mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {-84.64272432994349, 17.633364729126217}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression11(y = mainDatas.wb) 
    annotation(Placement(transformation(origin = {-8.000000000000043, 33.99999999999999}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 180.0)));
  Modelica.Blocks.Sources.RealExpression realExpression12(y = mainDatas.wb) 
    annotation(Placement(transformation(origin = {139.67863783502833, 19.633364729126207}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression13(y = mainDatas.wb) 
    annotation(Placement(transformation(origin = {253.68217938341516, 19.633364729126207}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression14(y = mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {80.00354154838705, 26.733270541747594}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression15(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {80.00354154838706, 70.36663527087381}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression16(y = mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {194.0, 26.73327054174758}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression17(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {194.0, 75.09990581262136}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  Modelica.Blocks.Sources.RealExpression realExpression18(y = mainDatas.load_intensity) 
    annotation(Placement(transformation(origin = {306.0, 33.99999999999999}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression19(y = mainDatas.load_angle) 
    annotation(Placement(transformation(origin = {306.0, 65.63336472912621}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression20(y = 0.5 * mainDatas.wb) 
    annotation(Placement(transformation(origin = {194.0, 169.6333647291262}, 
    extent = {{-12.0, -10.0}, {11.999999999999972, 10.0}}, 
    rotation = 180.0)));

  record MainDatas "主要参数"
    extends Modelica.Icons.Record;
    import SI = Modelica.SIunits;
    import Modelica.Constants.pi;
    parameter SI.Force load_intensity = 5000 "负载力" 
      annotation(Dialog(group = "负载参数"));
    parameter Real load_angle = 0 "负载角度" 
      annotation(Dialog(group = "负载参数"));
    parameter SI.AngularVelocity w(displayUnit = "rev/min") = 209.43951023932 "电机转速" 
      annotation(Dialog(group = "负载参数"));
    parameter Real wb = w * 30 / pi "轴承转速" 
      annotation(Dialog(group = "负载参数"));
    parameter SI.Diameter Dmain(displayUnit = "mm") = 0.015 "主管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dmainbra(displayUnit = "mm") = 0.01 "主分支管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dpiston(displayUnit = "mm") = 0.003 "活塞分支管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dcam(displayUnit = "mm") = 0.00525 "凸轮轴分支管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dcambear(displayUnit = "mm") = 0.004 "凸轮轴轴承分支管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dmainbear(displayUnit = "mm") = 0.006 "轴承主分支管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dmainbear1(displayUnit = "mm") = 0.005 "轴承主分支管道直径" 
      annotation(Dialog(group = "管路参数"));
    parameter SI.Diameter Dconrod(displayUnit = "mm") = 0.004 "离心管道直径" 
      annotation(Dialog(group = "管路参数"));
    annotation(Protection(access=Access.nonPackageDuplicate));
  end MainDatas;
equation
  connect(pipe_C.port_B, generalBend.port_A) 
    annotation(Line(origin = {-79.996458451613, -141.63336472912616}, 
    points = {{5.684341886080802e-14, -3.9999999999999716}, {5.684341886080802e-14, 4.200422362379896}}, 
    color = {255, 170, 0}));
  connect(speed.flange, volumetric_Pump.flange_a) 
    annotation(Line(origin = {-92.99645845161302, -183.63336472912616}, 
    points = {{-3.0000000000000284, -2.842170943040401e-14}, {3.0000000000001705, -2.842170943040401e-14}}, 
    color = {0, 0, 0}));
  connect(generalBend.port_B, pipe_C1.port_A) 
    annotation(Line(origin = {-61.996458451612995, -124.63336472912616}, 
    points = {{-5.209847498914911, 0.08890981941745224}, {-8.526512829121202e-14, 0.08890981941746645}}, 
    color = {255, 170, 0}));
  connect(pipe_C1.port_B, generalBend1.port_A) 
    annotation(Line(origin = {-32.996458451612995, -124.63336472912616}, 
    points = {{-9.000000000000085, 0.08890981941746645}, {-3.6645583802918082, 0.08890981941749487}}, 
    color = {255, 170, 0}));
  connect(pipe_C2.port_A, generalBend1.port_B) 
    annotation(Line(origin = {-15.996458451612995, -141.63336472912616}, 
    points = {{-7.776070923254281, -3.9999999999999716}, {-7.776070923254274, 4.298757318332463}}, 
    color = {255, 170, 0}));
  connect(pipe_C2.port_B, filter.port_A) 
    annotation(Line(origin = {-23.996458451612995, -169.63336472912616}, 
    points = {{0.22392907674571916, 4.000000000000028}, {0.22392907674571916, -4.223929076745918}}, 
    color = {255, 170, 0}));
  connect(filter.port_B, pipe_C3.port_A) 
    annotation(Line(origin = {-15.996458451612995, -197.63336472912616}, 
    points = {{-7.776070923254281, 3.776070923254082}, {-7.776070923254281, -4.0}, {-4.973799150320701e-14, -4.0}}, 
    color = {255, 170, 0}));
  connect(pipe_C3.port_B, generalBend2.port_A) 
    annotation(Line(origin = {12.003541548387012, -201.63336472912619}, 
    points = {{-8.000000000000057, 2.842170943040401e-14}, {-2.023506714365844, 2.842170943040401e-14}, {-2.023506714365844, 0.223929076745776}}, 
    color = {255, 170, 0}));
  connect(generalBend2.port_B, pipe_C4.port_A) 
    annotation(Line(origin = {23.003541548387012, -183.63336472912616}, 
    points = {{-0.13501925732830955, -4.98591842216922}, {-0.13501925732829534, 4.0}}, 
    color = {255, 170, 0}));
  connect(pipe_C4.port_B, abruptPipe.port_B) 
    annotation(Line(origin = {23.003541548387012, -154.63336472912616}, 
    points = {{-0.13501925732829534, -5.0}, {-0.13501925732829534, 3.91109018058242}}, 
    color = {255, 170, 0}));
  connect(abruptPipe.port_A, pipe_C5.port_A) 
    annotation(Line(origin = {23.003541548387012, -126.63336472912616}, 
    points = {{-0.13501925732829534, -4.08890981941758}, {-0.13501925732829534, 4.822180361165081}}, 
    color = {255, 170, 0}));
  connect(pipe_C5.port_B, tjunction90deg.port_C) 
    annotation(Line(origin = {23.003541548387012, -97.63336472912616}, 
    points = {{-0.13501925732829534, -4.177819638834919}, {-0.1350192573282598, 4.733270541747572}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg.port_A, pipe_C6.port_B) 
    annotation(Line(origin = {8.003541548387012, -82.63336472912619}, 
    points = {{4.86498074267174, -0.26672945825239935}, {-4.00000000000005, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg1.port_B, pipe_C6.port_A) 
    annotation(Line(origin = {-19.996458451612995, -82.63336472912619}, 
    points = {{-4.864980742671875, -0.26672945825239935}, {3.9999999999999574, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg1.port_C, pipe_C7.port_A) 
    annotation(Line(origin = {-34.996458451612995, -69.63336472912619}, 
    points = {{0.1350192573281248, -3.2667294582523994}, {0.13501925732816744, 4.000000000000028}}, 
    color = {255, 170, 0}));
  connect(pipe_C7.port_B, abruptPipe1.port_B) 
    annotation(Line(origin = {-34.996458451612995, -41.633364729126185}, 
    points = {{0.13501925732816744, -3.9999999999999716}, {0.13501925732813902, 3.2667294582524065}}, 
    color = {255, 170, 0}));
  connect(abruptPipe1.port_A, pipe_C8.port_A) 
    annotation(Line(origin = {-34.996458451612995, -14.633364729126185}, 
    points = {{0.13501925732813902, -3.7332705417475935}, {0.13501925732813902, 6.450047093689289}}, 
    color = {255, 170, 0}));
  connect(pipe_C9.port_B, tjunction90deg1.port_A) 
    annotation(Line(origin = {-48.996458451612995, -82.63336472912619}, 
    points = {{-4.729961485343637, -0.26672945825239935}, {4.135019257328125, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(pipe_C9.port_A, tjunction90deg2.port_B) 
    annotation(Line(origin = {-77.996458451613, -82.63336472912619}, 
    points = {{4.270038514656363, -0.26672945825239935}, {-4.594942228015412, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg2.port_C, pipe_C10.port_A) 
    annotation(Line(origin = {-92.99645845161302, -69.63336472912619}, 
    points = {{0.405057771984616, -3.2667294582523994}, {0.405057771984616, 4.000000000000028}}, 
    color = {255, 170, 0}));
  connect(pipe_C10.port_B, symThrottleValve.port_A) 
    annotation(Line(origin = {-92.99645845161302, -41.633364729126185}, 
    points = {{0.405057771984616, -3.9999999999999716}, {0.405057771984616, 3.2667294582524065}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg3.port_B, pipe_C11.port_A) 
    annotation(Line(origin = {-135.4563814223001, -82.63336472912619}, 
    points = {{-4.864980742671861, -0.26672945825239935}, {4.000000000000028, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg3.port_C, pipe_C12.port_A) 
    annotation(Line(origin = {-150.4563814223001, -69.63336472912619}, 
    points = {{0.13501925732813902, -3.2667294582523994}, {0.13501925732822428, 4.000000000000028}}, 
    color = {255, 170, 0}));
  connect(pipe_C12.port_B, abruptPipe2.port_B) 
    annotation(Line(origin = {-150.4563814223001, -41.633364729126185}, 
    points = {{0.13501925732822428, -3.9999999999999716}, {0.13501925732822428, 3.2667294582523994}}, 
    color = {255, 170, 0}));
  connect(pipe_C11.port_B, tjunction90deg2.port_A) 
    annotation(Line(origin = {-106.99645845161294, -82.63336472912619}, 
    points = {{-4.459922970687131, -0.26672945825239935}, {4.405057771984531, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(pipe_C13.port_A, tjunction90deg4.port_B) 
    annotation(Line(origin = {-189.4015162235977, -82.63336472912619}, 
    points = {{4.270038514656392, -0.2667294582524704}, {-4.594942228015327, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg4.port_C, pipe_C14.port_A) 
    annotation(Line(origin = {-204.40151622359764, -69.63336472912619}, 
    points = {{0.405057771984616, -3.2667294582523994}, {0.4050577719845876, 4.000000000000028}}, 
    color = {255, 170, 0}));
  connect(pipe_C14.port_B, symThrottleValve1.port_A) 
    annotation(Line(origin = {-204.40151622359764, -41.633364729126185}, 
    points = {{0.4050577719845876, -3.9999999999999716}, {0.4050577719845876, 3.2667294582523994}}, 
    color = {255, 170, 0}));
  connect(pipe_C13.port_B, tjunction90deg3.port_A) 
    annotation(Line(origin = {-161.99645845161294, -82.63336472912619}, 
    points = {{-3.1350192573283664, -0.2667294582524704}, {1.6750962866409793, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(pipe_C15.port_B, tjunction90deg4.port_A) 
    annotation(Line(origin = {-222.99645845161302, -82.63336472912619}, 
    points = {{-4.0, -0.26672945825239935}, {9.0, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(pipe_C16.port_B, abruptPipe3.port_B) 
    annotation(Line(origin = {-270.1314777089412, -41.633364729126185}, 
    points = {{0.1350192573281106, -3.999999999999943}, {0.1350192573281106, 3.2667294582524065}}, 
    color = {255, 170, 0}));
  connect(intersectingHoleswith2ports90degAxesIntersecting.port_B, pipe_C15.port_A) 
    annotation(Line(origin = {-255.99645845161302, -82.63336472912619}, 
    points = {{-4.000000000000057, -0.26672945825239935}, {9.0, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(intersectingHoleswith2ports90degAxesIntersecting.port_A, pipe_C16.port_A) 
    annotation(Line(origin = {-269.996458451613, -68.63336472912619}, 
    points = {{-5.684341886080802e-14, -4.283746032838039}, {-5.684341886080802e-14, 3.000000000000057}}, 
    color = {255, 170, 0}));
  connect(abruptPipe3.port_A, centrifugalPipes_CRC.port_A) 
    annotation(Line(origin = {-269.9964584516129, -14.633364729126185}, 
    points = {{-1.7053025658242404e-13, -3.7332705417475935}, {-1.7053025658242404e-13, 2.0}, {-26.00354154838709, 2.0}, {-26.00354154838709, 14.266729458252385}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding1.port_A, abruptPipe3.port_A) 
    annotation(Line(origin = {-262.9964584516129, -3.6333647291261855}, 
    points = {{6.996458451612966, 33.63336472912618}, {6.996458451612966, -10.0}, {-7.0000000000001705, -10.0}, {-7.0000000000001705, -14.733270541747594}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC.port_B, hydraulicBearing_journalfeeding.port_A) 
    annotation(Line(origin = {-296.0, -13.366635270873786}, 
    points = {{0.0, 32.999999999999986}, {0.0, 43.366635270873815}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC1.port_B, hydraulicBearing_journalfeeding1.port_A) 
    annotation(Line(origin = {-164.0, -13.366635270873786}, 
    points = {{-5.684341886080802e-14, 32.99999999999997}, {-5.684341886080802e-14, 43.366635270873736}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC1.port_A, abruptPipe2.port_A) 
    annotation(Line(origin = {-156.9964584516129, -10.633364729126185}, 
    points = {{-7.0035415483871475, 10.266729458252371}, {-7.0035415483871475, 0.0}, {6.675096286641036, 0.0}, {6.675096286641036, -7.733270541747601}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding.port_A, abruptPipe2.port_A) 
    annotation(Line(origin = {-139.9964584516129, -3.6333647291261855}, 
    points = {{9.996458451612824, 33.63336472912618}, {9.996458451612824, -8.0}, {-10.324903713358964, -8.0}, {-10.324903713358964, -14.7332705417476}}, 
    color = {255, 170, 0}));
  connect(pipe_C8.port_B, hydraulicBearing_bearingfeeding2.port_A) 
    annotation(Line(origin = {-35.0, -17.366635270873786}, 
    points = {{0.1385608057151444, 29.18331763543689}, {0.13501925732813902, 47.36663527087378}}, 
    color = {255, 170, 0}));
  connect(symThrottleValve1.port_B, tank4.port_A) 
    annotation(Line(origin = {-203.9964584516129, -9.633364729126185}, 
    points = {{-1.4210854715202004e-13, -8.7332705417476}, {-1.4210854715202004e-13, -4.089766752688179}}, 
    color = {255, 170, 0}));
  connect(symThrottleValve.port_B, tank5.port_A) 
    annotation(Line(origin = {-92.99645845161291, -9.633364729126185}, 
    points = {{0.4050577719845023, -8.733270541747594}, {0.40859932037159297, -4.089766752688179}}, 
    color = {255, 170, 0}));
  connect(tank1.port_A, hydraulicBearing_journalfeeding.port_B) 
    annotation(Line(origin = {-283.0, 60.633364729126214}, 
    points = {{7.003541548387034, 4.910233247311822}, {-13.0, 4.910233247311822}, {-13.0, -10.633364729126185}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding1.port_B, tank1.port_A) 
    annotation(Line(origin = {-263.0, 60.633364729126214}, 
    points = {{7.000000000000057, -10.633364729126221}, {7.000000000000057, 4.910233247311822}, {-12.996458451612966, 4.910233247311822}}, 
    color = {255, 170, 0}));
  connect(tank2.port_A, hydraulicBearing_journalfeeding1.port_B) 
    annotation(Line(origin = {-157.0, 60.633364729126214}, 
    points = {{11.003541548387062, 4.910233247311822}, {-7.000000000000057, 4.910233247311822}, {-7.000000000000057, -10.633364729126264}}, 
    color = {255, 170, 0}));
  connect(tank2.port_A, hydraulicBearing_bearingfeeding.port_B) 
    annotation(Line(origin = {-140.0, 60.633364729126214}, 
    points = {{-5.996458451612938, 4.910233247311822}, {9.999999999999915, 4.910233247311822}, {9.999999999999915, -10.633364729126221}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding2.port_B, tank3.port_A) 
    annotation(Line(origin = {-35.0, 60.633364729126214}, 
    points = {{0.13501925732813902, -10.633364729126221}, {0.1385608057151515, 9.643503789059423}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg5.port_C, pipe_C19.port_A) 
    annotation(Line(origin = {79.59848377640242, -69.63336472912619}, 
    points = {{0.40505777198464443, -3.2667294582523994}, {0.40505777198467285, 4.000000000000057}}, 
    color = {255, 170, 0}));
  connect(pipe_C19.port_B, symThrottleValve2.port_A) 
    annotation(Line(origin = {79.59848377640242, -41.633364729126185}, 
    points = {{0.40505777198467285, -3.999999999999943}, {0.40505777198467285, 3.2667294582523994}}, 
    color = {255, 170, 0}));
  connect(symThrottleValve2.port_B, tank6.port_A) 
    annotation(Line(origin = {79.5984837764025, -9.633364729126185}, 
    points = {{0.4050577719845876, -8.7332705417476}, {0.4085993203716498, -4.089766752688179}}, 
    color = {255, 170, 0}));
  connect(pipe_C17.port_B, tjunction90deg5.port_A) 
    annotation(Line(origin = {70.00354154838709, -82.63336472912619}, 
    points = {{-8.270038514656498, -0.26672945825239935}, {-2.842170943040401e-14, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg6.port_C, pipe_C20.port_A) 
    annotation(Line(origin = {135.54361857769996, -69.63336472912613}, 
    points = {{0.13501925732830955, -3.2667294582524278}, {0.13501925732828113, 4.0}}, 
    color = {255, 170, 0}));
  connect(pipe_C20.port_B, abruptPipe4.port_B) 
    annotation(Line(origin = {135.54361857769996, -41.63336472912613}, 
    points = {{0.13501925732828113, -4.0}, {0.13501925732828113, 3.2667294582523425}}, 
    color = {255, 170, 0}));
  connect(pipe_C21.port_B, tjunction90deg6.port_A) 
    annotation(Line(origin = {124.003541548387, -82.63336472912613}, 
    points = {{-7.135019257328324, -0.2667294582524562}, {1.6750962866412635, -0.2667294582524278}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC2.port_B, hydraulicBearing_journalfeeding2.port_A) 
    annotation(Line(origin = {122.0, -13.366635270873743}, 
    points = {{0.0, 42.999999999999936}, {0.0, 55.36663527087372}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC2.port_A, abruptPipe4.port_A) 
    annotation(Line(origin = {129.0035415483871, -18.63336472912613}, 
    points = {{-7.003541548387091, 28.26672945825232}, {-7.003541548387091, 10.0}, {6.67509628664115, 10.0}, {6.67509628664115, 0.2667294582523425}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding3.port_A, abruptPipe4.port_A) 
    annotation(Line(origin = {146.0035415483871, -3.6333647291261286}, 
    points = {{9.99645845161291, 45.63336472912613}, {9.99645845161291, -5.0}, {-10.32490371335885, -5.0}, {-10.32490371335885, -14.733270541747657}}, 
    color = {255, 170, 0}));
  connect(tank7.port_A, hydraulicBearing_journalfeeding2.port_B) 
    annotation(Line(origin = {129.0, 60.63336472912624}, 
    points = {{10.678637835028297, 14.376774330806938}, {-7.0, 14.376774330806938}, {-7.0, 1.3666352708737364}}, 
    color = {255, 170, 0}));
  connect(tank7.port_A, hydraulicBearing_bearingfeeding3.port_B) 
    annotation(Line(origin = {146.0, 60.63336472912624}, 
    points = {{-6.321362164971703, 14.376774330806938}, {10.0, 14.376774330806938}, {10.0, 1.3666352708737577}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg5.port_B, pipe_C21.port_A) 
    annotation(Line(origin = {107.00354154838709, -82.63336472912619}, 
    points = {{-17.00000000000003, -0.26672945825239935}, {-10.135019257328409, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg7.port_C, pipe_C22.port_A) 
    annotation(Line(origin = {193.59848377640242, -69.63336472912616}, 
    points = {{0.40505777198464443, -3.2667294582523994}, {0.4050577719847013, 4.000000000000085}}, 
    color = {255, 170, 0}));
  connect(pipe_C22.port_B, symThrottleValve3.port_A) 
    annotation(Line(origin = {193.59848377640242, -41.63336472912616}, 
    points = {{0.4050577719847013, -3.9999999999999147}, {0.4050577719847013, 3.266729458252378}}, 
    color = {255, 170, 0}));
  connect(symThrottleValve3.port_B, tank8.port_A) 
    annotation(Line(origin = {193.59848377640245, -9.633364729126157}, 
    points = {{0.40505777198467285, -8.733270541747622}, {0.40859932037170665, -4.089766752688208}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg.port_B, pipe_C17.port_A) 
    annotation(Line(origin = {38.0035415483871, -82.63336472912619}, 
    points = {{-5.135019257328345, -0.26672945825239935}, {3.7299614853434946, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg6.port_B, pipe_C23.port_A) 
    annotation(Line(origin = {155.0035415483871, -82.63336472912619}, 
    points = {{-9.324903713358822, -0.26672945825237093}, {-3.0035415483870906, -0.26672945825237093}}, 
    color = {255, 170, 0}));
  connect(pipe_C23.port_B, tjunction90deg7.port_A) 
    annotation(Line(origin = {190.0035415483871, -82.63336472912619}, 
    points = {{-18.00354154838709, -0.26672945825237093}, {-6.000000000000028, -0.26672945825237093}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg8.port_C, pipe_C18.port_A) 
    annotation(Line(origin = {251.54361857769987, -69.63336472912619}, 
    points = {{0.13501925732819586, -3.2667294582523994}, {0.13501925732819586, 3.9999999999999716}}, 
    color = {255, 170, 0}));
  connect(pipe_C18.port_B, abruptPipe5.port_B) 
    annotation(Line(origin = {251.54361857769987, -41.633364729126185}, 
    points = {{0.13501925732819586, -4.000000000000028}, {0.13501925732819586, 3.2667294582523567}}, 
    color = {255, 170, 0}));
  connect(pipe_C24.port_B, tjunction90deg8.port_A) 
    annotation(Line(origin = {240.00354154838686, -82.63336472912619}, 
    points = {{-7.999999999999801, -0.26672945825239935}, {1.6750962866412067, -0.26672945825239935}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC3.port_B, hydraulicBearing_journalfeeding3.port_A) 
    annotation(Line(origin = {237.9999999999999, -13.3666352708738}, 
    points = {{8.526512829121202e-14, 43.000000000000014}, {8.526512829121202e-14, 55.3666352708738}}, 
    color = {255, 170, 0}));
  connect(centrifugalPipes_CRC3.port_A, abruptPipe5.port_A) 
    annotation(Line(origin = {245.00354154838698, -18.633364729126185}, 
    points = {{-7.003541548387005, 28.2667294582524}, {-7.003541548387005, 11.0}, {6.675096286641093, 11.0}, {6.675096286641093, 0.2667294582523567}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding4.port_A, abruptPipe5.port_A) 
    annotation(Line(origin = {262.003541548387, -3.6333647291261855}, 
    points = {{9.996458451613023, 45.63336472912619}, {9.996458451613023, -4.0}, {-10.324903713358907, -4.0}, {-10.324903713358907, -14.733270541747643}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_journalfeeding3.port_B, tank9.port_A) 
    annotation(Line(origin = {244.9999999999999, 102.63336472912623}, 
    points = {{-6.999999999999915, -40.63336472912623}, {-6.999999999999915, -27.623225669193047}, {8.682179383415331, -27.623225669193047}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding4.port_B, tank9.port_A) 
    annotation(Line(origin = {254.9999999999999, 85.63336472912623}, 
    points = {{17.000000000000114, -23.63336472912622}, {17.000000000000114, -10.623225669193047}, {-1.3178206165846689, -10.623225669193047}}, 
    color = {255, 170, 0}));
  connect(pipe_C24.port_A, tjunction90deg7.port_B) 
    annotation(Line(origin = {216.0035415483871, -82.63336472912619}, 
    points = {{-4.000000000000028, -0.26672945825239935}, {-12.000000000000028, -0.26672945825237093}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg8.port_B, pipe_C25.port_A) 
    annotation(Line(origin = {274.0035415483871, -82.63336472912619}, 
    points = {{-12.324903713358992, -0.26672945825239935}, {3.8375481433204754, -0.26672945825237093}}, 
    color = {255, 170, 0}));
  connect(pipe_C25.port_B, intersectingHoleswith2ports90degAxesIntersecting1.port_A) 
    annotation(Line(origin = {313.003541548387, -82.63336472912619}, 
    points = {{-15.16245185667941, -0.26672945825237093}, {9.00000000000017, -0.26672945825237093}}, 
    color = {255, 170, 0}));
  connect(pipe_C26.port_A, intersectingHoleswith2ports90degAxesIntersecting1.port_B) 
    annotation(Line(origin = {332.003541548387, -61.633364729126185}, 
    points = {{5.684341886080802e-14, 9.999999999999986}, {-0.01701657458545469, -11.266729458252371}}, 
    color = {255, 170, 0}));
  connect(pipe_C26.port_B, annularPipe.port_A) 
    annotation(Line(origin = {332.003541548387, -20.633364729126185}, 
    points = {{5.684341886080802e-14, -11.000000000000014}, {-0.003541548386976956, 38.26672945825239}}, 
    color = {255, 170, 0}));
  connect(annularPipe.port_B, pipe_C27.port_A) 
    annotation(Line(origin = {331.99999999999994, 57.633364729126214}, 
    points = {{5.684341886080802e-14, -20.000000000000007}, {5.684341886080802e-14, 15.466541083495144}}, 
    color = {255, 170, 0}));
  connect(pipe_C27.port_B, intersectingHoleswith2ports90degAxesIntersecting2.port_A) 
    annotation(Line(origin = {349.99999999999994, 106.31663071667651}, 
    points = {{-17.999999999999943, -13.216724904055155}, {-17.996458451612966, -8.700282562135953}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg9.port_C, pipe_C28.port_A) 
    annotation(Line(origin = {145.5949422280152, 120.90009418737861}, 
    points = {{0.13501925732819586, -3.2667294582524136}, {0.13501925732819586, 3.999999999999943}}, 
    color = {255, 170, 0}));
  connect(pipe_C29.port_B, tjunction90deg9.port_A) 
    annotation(Line(origin = {131.5949422280152, 107.90009418737861}, 
    points = {{-4.72996148534358, -0.26672945825241356}, {4.135019257328196, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(pipe_C29.port_A, tjunction90deg10.port_B) 
    annotation(Line(origin = {102.59494222801519, 107.90009418737861}, 
    points = {{4.270038514656449, -0.26672945825241356}, {-4.594942228015356, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg10.port_C, pipe_C30.port_A) 
    annotation(Line(origin = {87.59494222801521, 120.90009418737861}, 
    points = {{0.405057771984616, -3.2667294582524136}, {0.405057771984616, 3.999999999999943}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg11.port_B, pipe_C31.port_A) 
    annotation(Line(origin = {45.135019257328146, 107.90009418737861}, 
    points = {{-4.864980742671811, -0.26672945825241356}, {3.9999999999999716, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg11.port_C, pipe_C32.port_A) 
    annotation(Line(origin = {30.135019257328146, 120.90009418737861}, 
    points = {{0.13501925732818876, -3.2667294582524136}, {0.1350192573282456, 3.999999999999943}}, 
    color = {255, 170, 0}));
  connect(pipe_C31.port_B, tjunction90deg10.port_A) 
    annotation(Line(origin = {73.59494222801521, 107.90009418737861}, 
    points = {{-4.459922970687103, -0.26672945825241356}, {4.405057771984616, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(pipe_C33.port_A, tjunction90deg12.port_B) 
    annotation(Line(origin = {-8.810115543969488, 107.90009418737861}, 
    points = {{4.27003851465642, -0.26672945825241356}, {-4.594942228015313, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(tjunction90deg12.port_C, pipe_C34.port_A) 
    annotation(Line(origin = {-23.81011554396946, 120.90009418737861}, 
    points = {{0.40505777198465864, -3.2667294582524136}, {0.4050577719847155, 3.999999999999943}}, 
    color = {255, 170, 0}));
  connect(pipe_C33.port_B, tjunction90deg11.port_A) 
    annotation(Line(origin = {18.594942228015192, 107.90009418737861}, 
    points = {{-3.13501925732826, -0.26672945825241356}, {1.6750962866411427, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(pipe_C35.port_B, tjunction90deg12.port_A) 
    annotation(Line(origin = {-42.40505777198484, 107.90009418737861}, 
    points = {{-3.9999999999999147, -0.26672945825241356}, {9.000000000000043, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(intersectingHoleswith2ports90degAxesIntersecting3.port_B, pipe_C35.port_A) 
    annotation(Line(origin = {-75.40505777198484, 107.90009418737861}, 
    points = {{-3.9999999999999147, -0.26672945825241356}, {9.000000000000085, -0.26672945825241356}}, 
    color = {255, 170, 0}));
  connect(intersectingHoleswith2ports90degAxesIntersecting3.port_A, pipe_C36.port_A) 
    annotation(Line(origin = {-89.40505777198484, 121.90009418737861}, 
    points = {{8.526512829121202e-14, -4.283746032838053}, {8.526512829121202e-14, 3.000000000000057}}, 
    color = {255, 170, 0}));
  connect(tank10.port_A, hydraulicBearing_bearingfeeding5.port_B) 
    annotation(Line(origin = {-88.99999999999994, 182.21682819982823}, 
    points = {{-0.40151622359789485, 13.326769776609723}, {-0.40505777198481496, 3.416536529297929}}, 
    color = {255, 170, 0}));
  connect(pipe_C36.port_B, hydraulicBearing_bearingfeeding5.port_A) 
    annotation(Line(origin = {-89.0, 156.63336472912624}, 
    points = {{-0.4050577719847581, -11.733270541747572}, {-0.4050577719847581, 8.999999999999915}}, 
    color = {255, 170, 0}));
  connect(tank11.port_A, hydraulicBearing_bearingfeeding6.port_B) 
    annotation(Line(origin = {-22.99999999999997, 182.21682819982823}, 
    points = {{-0.4015162235978451, 13.326769776609723}, {-0.4050577719848576, 3.416536529297929}}, 
    color = {255, 170, 0}));
  connect(tank12.port_A, hydraulicBearing_bearingfeeding7.port_B) 
    annotation(Line(origin = {30.675096286641285, 182.21682819982823}, 
    points = {{-0.40151622359786643, 13.326769776609723}, {-0.4050577719848647, 3.416536529297929}}, 
    color = {255, 170, 0}));
  connect(tank13.port_A, hydraulicBearing_bearingfeeding8.port_B) 
    annotation(Line(origin = {88.40505777198473, 182.21682819982823}, 
    points = {{-0.40151622359786643, 13.326769776609723}, {-0.40505777198490023, 3.416536529297929}}, 
    color = {255, 170, 0}));
  connect(tank14.port_A, hydraulicBearing_bearingfeeding9.port_B) 
    annotation(Line(origin = {146.13501925732828, 182.21682819982823}, 
    points = {{-0.40151622359778116, 13.326769776609723}, {-0.4050577719848718, 3.416536529297929}}, 
    color = {255, 170, 0}));
  connect(pipe_C34.port_B, hydraulicBearing_bearingfeeding6.port_A) 
    annotation(Line(origin = {-23.0, 156.63336472912624}, 
    points = {{-0.4050577719847439, -11.733270541747686}, {-0.4050577719848292, 8.999999999999915}}, 
    color = {255, 170, 0}));
  connect(pipe_C32.port_B, hydraulicBearing_bearingfeeding7.port_A) 
    annotation(Line(origin = {30.000000000000007, 156.63336472912624}, 
    points = {{0.2700385146563846, -11.733270541747686}, {0.27003851465641304, 8.999999999999915}}, 
    color = {255, 170, 0}));
  connect(pipe_C30.port_B, hydraulicBearing_bearingfeeding8.port_A) 
    annotation(Line(origin = {88.0, 156.63336472912624}, 
    points = {{-1.7053025658242404e-13, -11.733270541747686}, {-1.7053025658242404e-13, 8.999999999999915}}, 
    color = {255, 170, 0}));
  connect(pipe_C28.port_B, hydraulicBearing_bearingfeeding9.port_A) 
    annotation(Line(origin = {146.0, 156.63336472912624}, 
    points = {{-0.2700385146565907, -11.733270541747686}, {-0.2700385146565907, 8.999999999999915}}, 
    color = {255, 170, 0}));
  connect(hydraulicBearing_bearingfeeding6.load_p, hydraulicBearing_bearingfeeding5.load_p) 
    annotation(Line(origin = {-81.0, 160.63336472912624}, 
    points = {{48.59494222801517, 8.999999999999915}, {45.0, 8.999999999999915}, {45.0, -5.0}, {-49.0, -5.0}, {-49.0, 8.999999999999915}, {-17.405057771984758, 8.999999999999915}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding7.load_p, hydraulicBearing_bearingfeeding5.load_p) 
    annotation(Line(origin = {-55.0, 158.63336472912624}, 
    points = {{76.27003851465642, 10.999999999999915}, {69.0, 10.999999999999915}, {69.0, -3.0}, {-75.0, -3.0}, {-75.0, 10.999999999999915}, {-43.40505777198476, 10.999999999999915}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding8.load_p, hydraulicBearing_bearingfeeding5.load_p) 
    annotation(Line(origin = {-26.0, 154.63336472912624}, 
    points = {{104.99999999999983, 14.999999999999915}, {100.0, 14.999999999999915}, {100.0, 1.0}, {-104.0, 1.0}, {-104.0, 14.999999999999915}, {-72.40505777198476, 14.999999999999915}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding9.load_p, hydraulicBearing_bearingfeeding5.load_p) 
    annotation(Line(origin = {3.000000000000007, 154.63336472912624}, 
    points = {{133.7299614853434, 14.999999999999915}, {133.7299614853434, 1.0}, {-133.0, 1.0}, {-133.0, 14.999999999999915}, {-101.40505777198476, 14.999999999999915}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding6.angle_p, hydraulicBearing_bearingfeeding5.angle_p) 
    annotation(Line(origin = {-83.0, 188.63336472912627}, 
    points = {{50.59494222801517, -7.000000000000114}, {-15.405057771984758, -7.000000000000114}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding7.angle_p, hydraulicBearing_bearingfeeding5.angle_p) 
    annotation(Line(origin = {-56.0, 188.63336472912627}, 
    points = {{77.27003851465642, -7.000000000000114}, {68.0, -7.000000000000114}, {68.0, 2.0}, {-70.0, 2.0}, {-70.0, -7.000000000000114}, {-42.40505777198476, -7.000000000000114}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding8.angle_p, hydraulicBearing_bearingfeeding5.angle_p) 
    annotation(Line(origin = {-27.0, 188.63336472912627}, 
    points = {{105.99999999999983, -7.000000000000114}, {93.0, -7.000000000000114}, {93.0, 2.0}, {-99.0, 2.0}, {-99.0, -7.000000000000114}, {-71.40505777198476, -7.000000000000114}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding9.angle_p, hydraulicBearing_bearingfeeding5.angle_p) 
    annotation(Line(origin = {2.000000000000007, 188.63336472912627}, 
    points = {{134.7299614853434, -7.000000000000114}, {134.7299614853434, 2.0}, {-128.0, 2.0}, {-128.0, -7.000000000000114}, {-100.40505777198476, -7.000000000000114}}, 
    color = {0, 0, 127}));
  connect(tjunction90deg9.port_B, pipe_C37.port_A) 
    annotation(Line(origin = {161.0, 107.63336472912624}, 
    points = {{-5.270038514656591, -4.263256414560601e-14}, {4.999999999999972, -4.263256414560601e-14}}, 
    color = {255, 170, 0}));
  connect(pipe_C37.port_B, intersectingHoleswith2ports90degAxesIntersecting2.port_B) 
    annotation(Line(origin = {239.99999999999994, 107.63336472912624}, 
    points = {{-53.99999999999997, -4.263256414560601e-14}, {82.00354154838703, -0.0340331491713215}}, 
    color = {255, 170, 0}));
  connect(tank.port_A, volumetric_Pump.port_A) 
    annotation(Line(origin = {-79.99645845161291, -197.63336472912616}, 
    points = {{0.003541548387147486, -3.9102332473118224}, {5.684341886080802e-14, 4.19999999999996}}, 
    color = {255, 170, 0}));
  connect(volumetric_Pump.port_B, pipe_C.port_A) 
    annotation(Line(origin = {-79.99645845161291, -169.63336472912616}, 
    points = {{5.684341886080802e-14, -4.000000000000028}, {-2.842170943040401e-14, 4.000000000000028}}, 
    color = {255, 170, 0}));
  connect(realExpression.y, hydraulicBearing_bearingfeeding5.load_p) 
    annotation(Line(origin = {-131.0, 145.63336472912624}, 
    points = {{-33.13501925732845, 10.366635270873758}, {1.0, 10.366635270873758}, {1.0, 23.999999999999915}, {32.59494222801524, 23.999999999999915}}, 
    color = {0, 0, 127}));
  connect(realExpression1.y, hydraulicBearing_bearingfeeding5.angle_p) 
    annotation(Line(origin = {-131.0, 190.63336472912627}, 
    points = {{-33.13501925732845, 0.9999999999998579}, {5.0, 0.9999999999998579}, {5.0, -9.000000000000114}, {32.59494222801524, -9.000000000000114}}, 
    color = {0, 0, 127}));
  connect(realExpression2.y, speed.w_ref) 
    annotation(Line(origin = {-123.99645845161291, -183.63336472912616}, 
    points = {{-7.000000000000028, -2.842170943040401e-14}, {5.999999999999858, -2.842170943040401e-14}}, 
    color = {0, 0, 127}));
  connect(realExpression4.y, hydraulicBearing_journalfeeding.angle_p) 
    annotation(Line(origin = {-315.0, 49.633364729126214}, 
    points = {{-5.684341886080802e-14, 2.366635270873772}, {2.0, 2.366635270873772}, {2.0, -3.6333647291261855}, {10.0, -3.6333647291261855}}, 
    color = {0, 0, 127}));
  connect(realExpression3.y, hydraulicBearing_journalfeeding.load_p) 
    annotation(Line(origin = {-315.0, 24.633364729126214}, 
    points = {{-5.684341886080802e-14, 1.0}, {1.0, 1.0}, {1.0, 9.366635270873815}, {10.0, 9.366635270873815}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_journalfeeding.RPMS, realExpression5.y) 
    annotation(Line(origin = {-282.0, 27.633364729126214}, 
    points = {{-5.0, 6.3666352708738145}, {4.003541548387034, 6.3666352708738145}, {4.003541548387034, -7.000000000000014}}, 
    color = {0, 0, 127}));
  connect(realExpression5.y, hydraulicBearing_bearingfeeding1.RPMS) 
    annotation(Line(origin = {-271.0, 29.633364729126214}, 
    points = {{-6.996458451612966, -9.000000000000014}, {-6.996458451612966, 4.366635270873779}, {6.000000000000057, 4.366635270873779}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding1.angle_p, realExpression6.y) 
    annotation(Line(origin = {-231.0, 49.633364729126214}, 
    points = {{-15.999999999999943, -3.633364729126221}, {15.0, -3.633364729126221}, {15.0, 2.491491712707159}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_journalfeeding1.angle_p, realExpression6.y) 
    annotation(Line(origin = {-194.0, 49.633364729126214}, 
    points = {{20.999999999999943, -3.6333647291262636}, {-22.0, -3.6333647291262636}, {-22.0, 2.491491712707159}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding1.load_p, realExpression7.y) 
    annotation(Line(origin = {-231.0, 27.633364729126214}, 
    points = {{-15.999999999999943, 6.366635270873779}, {15.0, 6.366635270873779}, {15.0, 0.9999999999999893}}, 
    color = {0, 0, 127}));
  connect(realExpression7.y, hydraulicBearing_journalfeeding1.load_p) 
    annotation(Line(origin = {-194.0, 27.633364729126214}, 
    points = {{-22.0, 0.9999999999999893}, {-22.0, 6.366635270873736}, {20.999999999999943, 6.366635270873736}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_journalfeeding1.RPMS, realExpression8.y) 
    annotation(Line(origin = {-152.0, 27.633364729126214}, 
    points = {{-3.000000000000057, 6.366635270873736}, {3.9999999999999716, 6.366635270873736}, {3.9999999999999716, 0.9999999999999929}}, 
    color = {0, 0, 127}));
  connect(realExpression8.y, hydraulicBearing_bearingfeeding.RPMS) 
    annotation(Line(origin = {-144.0, 27.633364729126214}, 
    points = {{-4.000000000000028, 0.9999999999999929}, {-4.000000000000028, 6.366635270873779}, {4.999999999999915, 6.366635270873779}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding.angle_p, realExpression9.y) 
    annotation(Line(origin = {-107.0, 45.633364729126214}, 
    points = {{-14.000000000000085, 0.366635270873779}, {22.0, 0.366635270873779}, {22.0, 6.491491712707159}, {22.35727567005651, 6.491491712707159}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding.load_p, realExpression10.y) 
    annotation(Line(origin = {-107.0, 33.633364729126214}, 
    points = {{-14.000000000000085, 0.366635270873779}, {22.0, 0.366635270873779}, {22.0, -4.9999999999999964}, {22.35727567005651, -4.9999999999999964}}, 
    color = {0, 0, 127}));
  connect(realExpression9.y, hydraulicBearing_bearingfeeding2.angle_p) 
    annotation(Line(origin = {-68.0, 45.633364729126214}, 
    points = {{-16.64272432994349, 6.491491712707159}, {-16.64272432994349, 0.0}, {24.13501925732814, 0.0}, {24.13501925732814, 0.366635270873779}}, 
    color = {0, 0, 127}));
  connect(realExpression10.y, hydraulicBearing_bearingfeeding2.load_p) 
    annotation(Line(origin = {-68.0, 31.633364729126214}, 
    points = {{-16.64272432994349, -2.9999999999999964}, {-16.64272432994349, 2.0}, {24.13501925732814, 2.0}, {24.13501925732814, 2.366635270873779}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding2.RPMS, realExpression11.y) 
    annotation(Line(origin = {-22.0, 33.633364729126214}, 
    points = {{-3.864980742671861, 0.366635270873779}, {2.9999999999999574, 0.366635270873779}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_journalfeeding2.RPMS, realExpression12.y) 
    annotation(Line(origin = {136.0, 38.633364729126214}, 
    points = {{-5.0, 7.366635270873765}, {4.0, 7.366635270873765}, {4.0, -8.000000000000007}, {3.6786378350283258, -8.000000000000007}}, 
    color = {0, 0, 127}));
  connect(realExpression12.y, hydraulicBearing_bearingfeeding3.RPMS) 
    annotation(Line(origin = {144.0, 38.633364729126214}, 
    points = {{-4.321362164971674, -8.000000000000007}, {-4.321362164971674, 7.0}, {3.0, 7.0}, {3.0, 7.366635270873786}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_journalfeeding3.RPMS, realExpression13.y) 
    annotation(Line(origin = {251.0, 38.633364729126214}, 
    points = {{-4.000000000000028, 7.366635270873786}, {3.0, 7.366635270873786}, {3.0, -8.000000000000007}, {2.6821793834151606, -8.000000000000007}}, 
    color = {0, 0, 127}));
  connect(realExpression13.y, hydraulicBearing_bearingfeeding4.RPMS) 
    annotation(Line(origin = {259.0, 38.633364729126214}, 
    points = {{-5.317820616584839, -8.000000000000007}, {-5.317820616584839, 7.0}, {4.0, 7.0}, {4.0, 7.366635270873793}}, 
    color = {0, 0, 127}));
  connect(realExpression15.y, hydraulicBearing_journalfeeding2.angle_p) 
    annotation(Line(origin = {124.0, 62.633364729126214}, 
    points = {{-32.99645845161294, 7.733270541747601}, {-20.0, 7.733270541747601}, {-20.0, -4.633364729126235}, {-11.0, -4.633364729126235}}, 
    color = {0, 0, 127}));
  connect(realExpression14.y, hydraulicBearing_journalfeeding2.load_p) 
    annotation(Line(origin = {124.0, 36.633364729126214}, 
    points = {{-32.99645845161295, -9.90009418737862}, {-20.0, -9.90009418737862}, {-20.0, 9.366635270873765}, {-11.0, 9.366635270873765}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding3.angle_p, realExpression17.y) 
    annotation(Line(origin = {174.0, 60.633364729126214}, 
    points = {{-9.0, -2.633364729126214}, {20.0, -2.633364729126214}, {20.0, 3.4665410834951444}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_journalfeeding3.angle_p, realExpression17.y) 
    annotation(Line(origin = {205.0, 60.633364729126214}, 
    points = {{23.99999999999997, -2.633364729126214}, {-11.0, -2.633364729126214}, {-11.0, 3.4665410834951444}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding3.load_p, realExpression16.y) 
    annotation(Line(origin = {174.0, 38.633364729126214}, 
    points = {{-9.0, 7.366635270873786}, {20.0, 7.366635270873786}, {20.0, -0.9000941873786346}}, 
    color = {0, 0, 127}));
  connect(realExpression16.y, hydraulicBearing_journalfeeding3.load_p) 
    annotation(Line(origin = {206.0, 38.633364729126214}, 
    points = {{-12.0, -0.9000941873786346}, {-12.0, 7.366635270873786}, {22.99999999999997, 7.366635270873786}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding4.angle_p, realExpression19.y) 
    annotation(Line(origin = {288.0, 61.633364729126214}, 
    points = {{-7.0, -3.633364729126207}, {-2.0, -3.633364729126207}, {-2.0, 4.0}, {7.0, 4.0}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding4.load_p, realExpression18.y) 
    annotation(Line(origin = {288.0, 38.633364729126214}, 
    points = {{-7.0, 7.366635270873793}, {-2.0, 7.366635270873793}, {-2.0, -4.633364729126221}, {7.0, -4.633364729126221}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding9.RPMS, realExpression20.y) 
    annotation(Line(origin = {168.0, 169.6333647291262}, 
    points = {{-13.27003851465659, -5.684341886080802e-14}, {12.800000000000011, 0.0}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding5.RPMS, realExpression20.y) 
    annotation(Line(origin = {51.00000000000001, 161.63336472912624}, 
    points = {{-131.40505777198476, 7.999999999999915}, {-119.0, 7.999999999999915}, {-119.0, -6.0}, {117.0, -6.0}, {117.0, 7.999999999999972}, {129.8, 7.999999999999972}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding6.RPMS, realExpression20.y) 
    annotation(Line(origin = {84.0, 162.63336472912624}, 
    points = {{-98.40505777198483, 6.999999999999915}, {-86.0, 6.999999999999915}, {-86.0, -7.0}, {84.0, -7.0}, {84.0, 6.999999999999972}, {96.80000000000001, 6.999999999999972}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding7.RPMS, realExpression20.y) 
    annotation(Line(origin = {110.0, 162.63336472912624}, 
    points = {{-70.72996148534358, 6.999999999999915}, {70.80000000000001, 6.999999999999972}}, 
    color = {0, 0, 127}));
  connect(hydraulicBearing_bearingfeeding8.RPMS, realExpression20.y) 
    annotation(Line(origin = {139.0, 162.63336472912624}, 
    points = {{-42.00000000000017, 6.999999999999915}, {41.80000000000001, 6.999999999999972}}, 
    color = {0, 0, 127}));
end FourCylinderEngineLubricationCircuit;