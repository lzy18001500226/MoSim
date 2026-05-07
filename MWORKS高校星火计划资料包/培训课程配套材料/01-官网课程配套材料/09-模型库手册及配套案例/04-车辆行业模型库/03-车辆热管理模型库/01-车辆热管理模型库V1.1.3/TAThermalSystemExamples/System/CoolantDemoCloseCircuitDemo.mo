model CoolantDemoCloseCircuitDemo "闭环空调回路"
  Real[4] xin = {compressorR134a.hout, condenser.refrigerant.h_out, evaporatorR134a.refrigerant.h_in, compressorR134a.hin} "横坐标比焓变量,单位kJ/kg" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  Real[4] yin = {compressorR134a.pout, condenser.refrigerant.b.p, evaporatorR134a.refrigerant.a.p, compressorR134a.pin} "纵坐标对应压力变量,单位Pa" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));

  parameter Modelica.SIunits.Temperature T_Amb = 303.15 "环境温度";
  parameter Modelica.SIunits.TemperatureDifference SuperHeatSetPoint = 5 "蒸发器过热度设置值";
  parameter Real[:,:] Rev_Compr = {{0, 500}, {10, 2000}, {200, 2000}, {201, 100}, {241, 100}, {242, 2000}, {5000, 2000}} "压缩机转速";
  parameter Real[:,:] mdotAir_cond = {{0.0, 500}, {10, 2000}, {600, 2000}} "前端模块空气流量";
  parameter Modelica.SIunits.MassFlowRate mdotAir_evap = 0.2 "空调箱空气流量";
  TAThermalSystem.Sensors.Refrigerant.SuperHeatingSensor superHeatingSensor(redeclare package Medium = TYMedia.Helmholtz.R134a,h0_in=2e5,h0_out=2e5) annotation(Placement(transformation(origin = {66.12633139265677, 57.82622086391848},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = -90.0)));
  TAThermalSystem.HeatExchangers.Evaporator evaporatorR134a(n_segAir = 1, n_segRef = 1, n_segMtl = 1, redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoVertical, redeclare package Medium = TYMedia.Helmholtz.R134a,redeclare TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium wallmaterial,RefrigerantTemperature=30,RefrigerantMass=0.0943607,CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10) 

    annotation(Placement(transformation(origin = {60.12633139265674, 15.826220863918486},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 90.0)));
  TAThermalSystem.HeatExchangers.Condenser condenser0(n_segAir = 1, n_segRef = 2, n_segMtl = 1,
  redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal,HX_Init(h_in = 400e3, h_out = 350e3),RefrigerantTemperature=30,RefrigerantMass=0.150977,CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {210.79411550679114, -19.577112309674767},
    extent = {{11.0, 11.0}, {-11.0, -11.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin={166.25266278531345,104.32622086391848},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe lumpedPipeR134a(
  redeclare package Medium = TYMedia.Helmholtz.R134a, init(h_in = 200e3, h_out = 200e3, initType = TYBase.Utilities.Types.Init.Initial_MT),RefrigerantTemperature=30,RefrigerantMass=0.109214,RefrigerantMassDistribution=2) 

    annotation(Placement(transformation(origin = {234.92826326963547, 57.82622086391847},
    extent = {{10.0, 10.0}, {-10.0, -10.0}},
    rotation = -270.0)));
  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe lumpedPipeR134a1(
  redeclare package Medium = TYMedia.Helmholtz.R134a,
    init(h_in
= 200e3, h_out
= 200e3, initType = TYBase.Utilities.Types.Init.Initial_MT),RefrigerantTemperature=30,RefrigerantMass=0.109214,RefrigerantMassDistribution=2) annotation(Placement(transformation(origin = {122.17077370723345, -13.577112309674767},
    extent = {{10.0, 10.0}, {-10.0, -10.0}},
    rotation = -360.0)));



  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir(H_Out = 0.02,  FillingLevel0 = 0.1, H = 0.5,zeta=20,RefrigerantTemperature=30,RefrigerantMass=0.0766954,RefrigerantMassDistribution=1,redeclare package Medium = TYMedia.Helmholtz.R134a) 


    annotation(Placement(transformation(origin = {181.67982979250536, -13.062826595388977},
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));


  TAThermalSystem.Valves.RefrigerantValve.SimpleEXV zetaFlow3(



  redeclare package Medium = TYMedia.Helmholtz.R134a, yMax = 0.8, yInit = 0.1, yMin = 0.01,
    SuperHeatSetPoint = SuperHeatSetPoint,Ti=10,init(initType = TYBase.Thermal.FluidHeatFlow.Components.Types.Init.Initial_MT)) annotation(Placement(transformation(origin = {95.12531595281612, -14.605566501597785},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 180.0)));
  annotation(Diagram(coordinateSystem(extent={{-100,-140},{540,200.979}},
grid={2,2})),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}), experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 500, Tolerance = 0.0001), Documentation(link="modelica://TAThermalSystem/Resource/Doc/CoolantDemoCloseCircuitDemo.html"), Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(0, 1)),
Plot(y=["evaporatorR134a.hXSummary.Qdot_refTotal"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1), zoom_y_l=(0, 1)),
Plot(y=["condenser.hXSummary.Qdot_refTotal"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[W]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 1), zoom_y_l=(0, 1)),
Plot(y=["compressorR134a.summary.p_refrigerant"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(0, 1)),
Plot(y=["compressorR134a.summary.mdot"], thicknesses=[2], colors=["4278190335"])})
})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(
    m = mdotAir_evap,
    T = T_Amb) 
    annotation(Placement(transformation(origin = {24.61650614266938, 36.092901264490706},
    extent = {{10.0, -10.0}, {-10.0, 10.0}},
    rotation = -180.0)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(T_sink = T_Amb) 
    annotation(Placement(transformation(origin = {24.61650614266938, -17.966681618687176},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));


  TAThermalSystem.Sensors.Refrigerant.PTSensor pTSensor(outPortP(start=10e5),redeclare package Medium = TYMedia.Helmholtz.R134a) 

    annotation(Placement(transformation(origin = {211.43959491197003, 125.82622086391848},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe lumpedPipeR134a2(

  redeclare package Medium = TYMedia.Helmholtz.R134a,
    init(h_in
= 200e3, h_out
= 200e3, initType = TYBase.Utilities.Types.Init.Initial_MT),RefrigerantTemperature=30,RefrigerantMass=0.109214,RefrigerantMassDistribution=2
    ) 

    annotation(Placement(transformation(origin={105.43451829135155,125.8262208639185},
extent={{-10,10},{10,-10}},
rotation=360)));
  TAThermalSystem.Utilities.summary.summaryHVAC summaryHVAC(

    temp_cond_in = condenser0.hXSummary.T_in,
    press_cond_in = condenser0.hXSummary.p_in,
    h_cond_in = condenser0.hXSummary.h_in,
    mdot_cond_in = condenser0.hXSummary.mdot_ref,
    temp_cond_out = condenser.refrigerant.T_out,
    press_cond_out = condenser.hXSummary.p_out,
    h_cond_out = condenser.hXSummary.h_out,
    mdot_cond_out = condenser.hXSummary.mdot_ref,
    temp_evap_in = evaporatorR134a.refrigerant.T_in,
    press_evap_in = evaporatorR134a.hXSummary.p_in,
    h_evap_in = evaporatorR134a.hXSummary.h_in,
    mdot_evap_in = evaporatorR134a.hXSummary.mdot_ref,
    temp_evap_out = evaporatorR134a.hXSummary.T_out,
    press_evap_out = evaporatorR134a.hXSummary.p_out,
    h_evap_out = evaporatorR134a.hXSummary.h_out,
    mdot_evap_out = evaporatorR134a.hXSummary.mdot_ref
    ) 
    annotation(Placement(transformation(origin = {32.742705190046394, 144}, extent = {{-10, -10}, {10, 10}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_evapout(
    temperature = summaryHVAC.temp_evap_out, pressure = summaryHVAC.press_evap_out, specificEnthalpy = summaryHVAC.h_evap_out, massflowRate = summaryHVAC.mdot_evap_out, blockname = "蒸发器出口"
    ) 
    annotation(Placement(transformation(origin = {0.6165061426693796, 51.82622086391848}, extent = {{-10, -4}, {34, 10}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display_legend hX_Display_legend 
    annotation(Placement(transformation(origin = {-10.201675675512433, 104.64440268210029}, extent = {{-13.181818181818173, -5.272727272727273}, {44.81818181818183, 13.18181818181818}})));
  TAThermalSystem.Utilities.DynamicDisplay.Single_Display single_Display(

    variable = superHeatingSensor.outPort, blockname = "过热度/°C"
    ) annotation(Placement(transformation(origin = {94.43451829135155, 66.82622086391848}, extent = {{-15, 3}, {21, 15}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_evapin(
    temperature = summaryHVAC.temp_evap_in, pressure = summaryHVAC.press_evap_in, specificEnthalpy = summaryHVAC.h_evap_in, massflowRate = summaryHVAC.mdot_evap_in, blockname = "蒸发器进口"
    ) 
    annotation(Placement(transformation(origin = {42.126331392656766, -51.75958410129284}, extent = {{-10, -4}, {34, 10}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_condout(
    temperature = summaryHVAC.temp_cond_out, pressure = summaryHVAC.press_cond_out, specificEnthalpy = summaryHVAC.h_cond_out, massflowRate = summaryHVAC.mdot_cond_out, blockname = "冷凝器出口"
    ) 
    annotation(Placement(transformation(origin = {138.12633139265674, 9.826220863918486}, extent = {{-10, -4}, {34, 10}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_condin(
    temperature = summaryHVAC.temp_cond_in, pressure = summaryHVAC.press_cond_in, specificEnthalpy = summaryHVAC.h_cond_in, massflowRate = summaryHVAC.mdot_cond_in, blockname = "冷凝器进口"
    ) 
    annotation(Placement(transformation(origin = {194.19525233013007, 9.826220863918486}, extent = {{-10, -4}, {34, 10}})));
  TAThermalSystem.Utilities.DynamicDisplay.ph_R134a ph_R134a1(
    x = xin, y = yin
    ) 
    annotation(Placement(transformation(origin = {283.667040871462, -41.67377913608152},
    extent = {{-1.4210854715202004e-14, 0.0}, {199.0, 199.0}})));
  TAThermalSystem.HeatExchangers.Condenser condenser(

    n_segAir = 1, n_segRef = 2, n_segMtl = 1,
  redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal(flattubes = {20}, flowScheme = {{1}}),RefrigerantTemperature=30,RefrigerantMass=0.0503257,CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a
    ) 



    annotation(Placement(transformation(origin = {152.87099186705697, -20.143730184605243},
    extent = {{11.0, 11.0}, {-11.0, -11.0}})));
  TAThermalSystem.Compressor.Compressor_EfficiencyDefinition compressorR134a(
    MaximumDisplacement = 3.3e-5, p0_out = 9.999999999999999e5, p0_in = 4.999999999999999e5,h0_out=400000,h0_in=420000,redeclare package Medium = TYMedia.Helmholtz.R134a
    ) annotation(Placement(transformation(origin = {178.1263313926567, 125.8262208639185},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1D1(
    table = Rev_Compr
    ) 
    annotation(Placement(transformation(origin={106.12633139265677,158},
extent={{-10,-10},{10,10}})));

  //TAThermalSystem.Utilities.PrintVar(getInstanceName() + " lumpedPipeR134a2.P = %f", lumpedPipeR134a2.p[1]);

  Modelica.Blocks.Sources.Clock clock1 
    annotation(Placement(transformation(origin={66.12633139265677,158},
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain1(
    k = Modelica.Constants.pi / 30
    ) 
    annotation(Placement(transformation(origin={138.12633139265674,104.32622086391848},
extent={{-10,-10},{10,10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink2(
    T_sink = 303.15
    ) 
    annotation(Placement(transformation(origin = {240.92826326963547, -51.75958410129284},
    extent = {{10, -10}, {-10, 10}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource2(
    m = 0.11, T = 303.15,
    phi_source = 40, use_mT_input = true
    ) 

    annotation(Placement(transformation(origin={122.479,-50.4107},
extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1D(
    table = mdotAir_cond
    ) 
    annotation(Placement(transformation(origin = {44.92826326963544, -75.75958410129283},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Clock clock 
    annotation(Placement(transformation(origin = {4.928263269635437, -75.75958410129283},
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain(
    k = 1 / 3600 * 0.25
    ) 
    annotation(Placement(transformation(origin = {88.18558449291662, -76.10269155309518},
    extent = {{-6.999999999999993, -7}, {7, 7}})));
  Modelica.Blocks.Sources.Constant const(
    k = T_Amb
    ) 
    annotation(Placement(transformation(origin = {107.80271377077838, -88.27215663514198},
    extent = {{-7, -7}, {6.9999999999999964, 6.999999999999986}})));
  Modelica.Blocks.Sources.Constant const1(
    k = 0.4
    ) 
    annotation(Placement(transformation(origin={107.502,-120.262},
extent={{-7,-7},{7,7}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource3(
    m = 0.11, T = 303.15,
    phi_source = 40, use_mT_input = true
    ) 

    annotation(Placement(transformation(origin={191.278,-52.1866},
extent={{-10,10},{10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink3(
    T_sink = 303.15
    ) 
    annotation(Placement(transformation(origin = {173.79772951641846, -51.261596793717324},
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Gain gain2(
    k = 1 / 3600 * 0.75
    ) 
    annotation(Placement(transformation(origin = {176.48082755203177, -75.43240275222072},
    extent = {{-6.999999999999993, -7}, {7, 7}})));
  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir1(H_Out = 0.4,  FillingLevel0 = 0.1, H = 0.5,zeta=20,RefrigerantTemperature=30,RefrigerantMass=0.0766954,RefrigerantMassDistribution=1,redeclare package Medium = TYMedia.Helmholtz.R134a) 


    annotation(Placement(transformation(origin={80.1942,125.838},
extent={{-10,-10},{10,10}})));
  initial equation
  lumpedPipeR134a2.p[1] = lumpedPipeR134a2.p0[1];
  evaporatorR134a.refrigerant.h[3] = evaporatorR134a.refrigerant.h0[3];
  condenser.refrigerant.h[2] = condenser.refrigerant.h0[2];
equation
  connect(lumpedPipeR134a.b, condenser0.a1) 
    annotation(Line(origin = {5.439594911970033, -33.907098735509294},
    points = {{229.48866835766543, 81.73331959942777}, {229.48866835766543, 20.929986425834528}, {216.3545205948211, 20.929986425834528}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(superHeatingSensor.a, evaporatorR134a.b1) 
    annotation(Line(origin = {-136.56040508802997, -12.907098735509294},
    points = {{202.68673648068673, 60.73331959942777}, {202.6867364806867, 38.73331959942778}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(condenser0.b1, reservoir.port_a) 
    annotation(Line(origin = {-6.8926209738956175, -62.31043190910255},
    points = {{206.68673648068676, 49.33331959942778}, {198.57245076640098, 49.33331959942778}, {198.57245076640098, 49.14760531371357}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(evaporatorR134a.a1, zetaFlow3.b) 
    annotation(Line(origin = {-126.56040508802997, -53.907098735509294},
    points = {{192.6867364806867, 59.73331959942778}, {192.6867364806867, 39.0}, {211.6857210408461, 39.0}, {211.6857210408461, 39.30153223391151}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(zetaFlow3.a, lumpedPipeR134a1.b) 
    annotation(Line(origin = {-65.89262097389562, -63.31043190910255},
    points = {{171.01793692671174, 48.70486540750476}, {178.06339468112907, 48.70486540750476}, {178.06339468112907, 49.73331959942778}},
    color = {0, 128, 0},
    thickness = 1.0));



  connect(airSink1.port_a, evaporatorR134a.air_out) 
    annotation(Line(origin = {44.43959491197003, -5.907098735509294},
    points = {{-9.823088769300654, -12.059582883177882}, {11.0, -12.059582883177882}, {11.0, 11.73331959942778}, {9.686736480686704, 11.73331959942778}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(airSource1.port_b, evaporatorR134a.air_in) 
    annotation(Line(origin = {27.439594911970033, 31.092901264490692},
    points = {{7.176911230699346, 5.000000000000014}, {26.686736480686704, 5.000000000000014}, {26.686736480686704, -5.266680400572206}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(pTSensor.b, lumpedPipeR134a.a) 
    annotation(Line(origin = {222.43959491197003, 96.09290126449069},
    points = {{-1.0, 29.733319599427787}, {12.0, 29.733319599427787}, {12.0, -28.266680400572213}, {12.488668357665432, -28.266680400572213}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(condenser.a1, reservoir.b) 
    annotation(Line(origin = {168.0, -13.0},
    points = {{-4.129008132943028, -0.5437301846052431}, {4.0, -0.5437301846052431}, {4.0, -0.16282659538897626}, {3.679829792505359, -0.16282659538897626}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(condenser.b1, lumpedPipeR134a1.a) 
    annotation(Line(origin = {137.0, -14.0},
    points = {{4.870991867056972, 0.45626981539475686}, {-4.829226292766549, 0.42288769032523277}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(pTSensor.a, compressorR134a.b) 
    annotation(Line(origin = {195.0, 126.0},
    points = {{6.439594911970033, -0.17377913608152085}, {-6.873668607343291, -0.17377913608150664}},
    color = {0, 128, 0},
    thickness = 1.0));
  connect(lumpedPipeR134a2.b, compressorR134a.a) 
    annotation(Line(origin={142,126},
points={{-26.56548170864845,-0.17377913608150664},{26.12633139265671,-0.17377913608150664}},
color={0,128,0},
thickness=1));
  connect(speed.flange, compressorR134a.flange) 
    annotation(Line(origin={173,109},
points={{3.252662785313447,-4.673779136081521},{5.126331392656709,-4.673779136081521},{5.126331392656709,6.826220863918493}},
color={0,0,0}));
  connect(clock1.y, combiTable1D1.u) 
    annotation(Line(origin={102.17077370723345,147.32622086391845},
points={{-25.044442314576685,10.67377913608155},{-8.044442314576685,10.67377913608155}},
color={0,0,127}));
  connect(gain1.y, speed.w_ref) 
    annotation(Line(origin={140,103},
points={{9.126331392656738,1.3262208639184792},{14.252662785313447,1.3262208639184792}},
color={0,0,127}));
  connect(combiTable1D1.y[1], gain1.u) 
    annotation(Line(origin={125,125},
points={{-7.873668607343234,33},{-2.8736686073432622,33},{-2.8736686073432622,-20.67377913608152},{1.1263313926567378,-20.67377913608152}},
color={0,0,127}));
  connect(clock.y, combiTable1D.u) 
    annotation(Line(origin = {24.928263269635437, -75.75958410129283},
    points = {{-9.0, 0.0}, {8.0, 0.0}},
    color = {0, 0, 127}));
  connect(combiTable1D.y[1], gain.u) 
    annotation(Line(origin = {64.92826326963544, -75.75958410129283},
    points = {{-9.0, 0.0}, {14.85732122328119, 0.0}, {14.85732122328119, -0.3431074518023536}},
    color = {0, 0, 127}));
  connect(gain.y, airSource2.m_input) 
    annotation(Line(origin={106.928,-58.7596},
points={{-11.0427,-17.3431},{9.55038,-17.3431},{9.55038,-1.65113}},
color={0,0,127}));
  connect(const1.y, airSource2.phi_input) 
    annotation(Line(origin={140.928,-68.7596},
points={{-25.726,-51.5024},{-12.4494,-51.5024},{-12.4494,8.34889}},
color={0,0,127}));
  connect(const.y, airSource2.T_input_K) 
    annotation(Line(origin={119.928,-68.7596},
points={{-4.42555,-19.5126},{2.55038,-19.5126},{2.55038,8.34887}},
color={0,0,127}));
  connect(combiTable1D.y[1], gain2.u) 
    annotation(Line(origin={115.928,-75.7596},
points={{-60,0},{-57,0},{-57,-26.421},{48.7526,-26.421},{48.7526,0.327181},{52.1526,0.327181}},
color={0,0,127}));
  connect(gain2.y, airSource3.m_input) 
    annotation(Line(origin={184.928,-58.7596},
points={{-0.747436,-16.6728},{-0.747436,-3.42706},{0.349481,-3.42706}},
color={0,0,127}));
  connect(const.y, airSource3.T_input_K) 
    annotation(Line(origin={153.928,-64.7596},
points={{-38.4253,-23.5126},{37.3497,-23.5126},{37.3497,2.57296}},
color={0,0,127}));
  connect(const1.y, airSource3.phi_input) 
    annotation(Line(origin={167.928,-64.7596},
points={{-52.726,-55.5024},{29.3497,-55.5024},{29.3497,2.57296}},
color={0,0,127}));
  connect(airSource2.port_b, condenser.air_in) 
    annotation(Line(origin={137,-39},
points={{-4.52136,-11.4107},{1.77099,-11.4107},{1.77099,12.2563},{4.87099,12.2563}},
color={0,232,232},
thickness=1));
  connect(condenser.air_out, airSink3.port_a) 
    annotation(Line(origin={164,-39},
points={{-0.129008,12.2563},{2.97099,12.2563},{2.97099,-12.2616},{-0.20227,-12.2616}},
color={0,232,232},
thickness=1));
  connect(airSource3.port_b, condenser0.air_in) 
    annotation(Line(origin={200,-39},
points={{1.27774,-13.1866},{-0.205884,-13.1866},{-0.205884,12.8229}},
color={0,232,232},
thickness=1));
  connect(airSink2.port_a, condenser0.air_out) 
    annotation(Line(origin = {226.0, -39.0},
    points = {{4.928263269635465, -12.759584101292837}, {-1.1058844932088618, -12.759584101292837}, {-1.1058844932088618, 12.822887690325231}, {-4.205884493208856, 12.822887690325231}},
    color = {0, 232, 232},
    thickness = 1.0));
  connect(superHeatingSensor.outPort, zetaFlow3.DeltaT_SH) 
  annotation(Line(origin={86,27},
points={{-8.473668607343228,30.82622086391848},{9.125315952816123,30.82622086391848},{9.125315952816123,-31.605566501597785}},
color={0,0,127}));
  connect(reservoir1.b, lumpedPipeR134a2.a) 
  annotation(Line(origin={93,126},
  points={{-2.80582,-0.262367},{2.43452,-0.262367},{2.43452,-0.173779}},
  color={0,128,0},
  thickness=1));
  connect(reservoir1.port_a, superHeatingSensor.b) 
  annotation(Line(origin={68,97},
  points={{2.19418,28.7376},{-1.87367,28.7376},{-1.87367,-29.1738}},
  color={0,128,0},
  thickness=1));
  end CoolantDemoCloseCircuitDemo;