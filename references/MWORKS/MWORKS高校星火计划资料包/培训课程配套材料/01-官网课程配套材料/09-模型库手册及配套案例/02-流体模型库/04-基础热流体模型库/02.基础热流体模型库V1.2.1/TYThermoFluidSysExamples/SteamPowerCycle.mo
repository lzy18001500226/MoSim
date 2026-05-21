model SteamPowerCycle "蒸汽动力循环系统"
  TYThermoFluidSys.HeatExchangers.Evaporator boiler(redeclare package Medium = Modelica.Media.Water.StandardWater, p_start(displayUnit = "bar") = 100000, m_D = 300e3, V_l_start = 67, energyDynamics = TYThermoFluidSys.Utilities.Types.Dynamics.FixedInitial, massDynamics = TYThermoFluidSys.Utilities.Types.Dynamics.FixedInitial, T(start = 500), T_D(start = 500), Tsat(start = 500), V_t = 100) 
    annotation(Placement(transformation(origin = {-118.0982, -9.0527}, 
    extent = {{14.6315, -15.9018}, {-14.6315, 15.9018}}, 
    rotation = -90)));
  TYThermoFluidSys.Boundaries.BoundaryHeatFlow boundaryHeatFlow(Q_flow(displayUnit = "MW") = 4e8, n = 1, use_Qflow_in = true) 
    annotation(Placement(transformation(origin = {-163.9096, -9.5938}, 
    extent = {{-14.0904, -14.0904}, {14.0904, 14.0904}})));
  Modelica.Blocks.Sources.TimeTable q_F_Tab(table = {{0, 0}, {1800, 400e5}, {7200, 400e5}}) 
    annotation(Placement(transformation(origin = {-203.819, -9.5938}, 
    extent = {{-10, -10}, {10, 10}})));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed(w(displayUnit = "rev/min") = 314.159265358979) 
    annotation(Placement(transformation(origin = {-35, 74}, 
    extent = {{-14.0904, -15.435}, {14.0904, 15.435}})));
  TYThermoFluidSys.Machines.SuterPump suterPump(redeclare package Medium = Modelica.Media.Water.StandardWater, qvr = 1, Hr = 90e3) 
    annotation(Placement(transformation(origin = {28.0982, -76.565}, 
    extent = {{15.9018, -15.435}, {-15.9018, 15.435}})));
  TYThermoFluidSys.Boundaries.BoundarySpeed boundarySpeed1(w(displayUnit = "rpm") = 314.159265358979, use_w_in = true) 
    annotation(Placement(transformation(origin = {-8.9645, -44.1177}, 
    extent = {{-14.0904, -15.435}, {14.0904, 15.435}})));
  TYThermoFluidSys.HeatExchangers.SimpleCondenser condenser(p_water_out0 = 100000, V = 100, A = 10, P0(displayUnit = "MPa") = 10000, redeclare package Medium_w = Modelica.Media.Water.StandardWater, redeclare package Medium = Modelica.Media.Water.StandardWater, mflow_start = 5) 
    annotation(Placement(transformation(origin = {57.6532, -16.82931}, 
    extent = {{-15.9095, -19.4703}, {15.9095, 19.4703}})));
  TYThermoFluidSys.Boundaries.BoundaryPressure boundaryPressure2(p = 100000, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {114.0905, 20}, 
    extent = {{15.9095, -15.435}, {-15.9095, 15.435}})));
  TYThermoFluidSys.Boundaries.BoundaryPressure boundaryPressure3(p = 9.999999999999999e5, T = 308.15, redeclare package Medium = Modelica.Media.Water.StandardWater) 
    annotation(Placement(transformation(origin = {114.09, -20.7234}, 
    extent = {{15.9095, -15.435}, {-15.9095, 15.435}})));
  TYThermoFluidSys.Machines.SteamTurbine steamTurbine(redeclare package Medium = Modelica.Media.Water.StandardWater, p_in_0(displayUnit="MPa")=9e7, p_out_0(displayUnit="MPa")=5e5, m_flow_0=180, h_in_0=3e6, redeclare model TurbineEta = TYThermoFluidSys.Machines.Basic.TurbineEffectiveness.ConstantEfficiency, p_out0=50000) annotation(Placement(transformation(origin = {-8.9645, 38.565}, 
    extent = {{-15.9095, -15.435}, {15.9095, 15.435}})));
  Modelica.Blocks.Continuous.PI controller(T=120, k=10, initType=Modelica.Blocks.Types.Init.InitialState) 
    annotation(Placement(transformation(origin = {-71.9451, -44.9212}, 
    extent = {{-7, -7}, {7, 7}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation(Placement(transformation(origin = {-59, -17.6842}, 
    extent = {{10, 10}, {-10, -10}})));
  Modelica.Blocks.Sources.Constant levelSetPoint(k=67) 
    annotation(Placement(transformation(origin = {-26.0905, -17.6842}, 
    extent = {{7, -7}, {-7, 7}})));
  Modelica.Blocks.Nonlinear.Limiter limiter(uMin=0, uMax=530) 
    annotation(Placement(transformation(origin = {-44, -44.9212}, 
    extent = {{7, 7}, {-7, -7}}, 
    rotation = -180)));
  TYThermoFluidSys.Sensors.SensorT TSensor 
    annotation(Placement(transformation(origin = {-48.8191, 22.4404}, 
    extent = {{-10, -10}, {10, 10}})));
  annotation(experiment(Algorithm=Dassl,StartTime=0,StopTime=7200,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false,Interval=0.5), Diagram(coordinateSystem(extent = {{-200, -140}, {240, 140}}, 
    grid = {2, 2})), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33}, 
    lineColor = {0, 94, 138}, 
    fillColor = {0, 94, 138}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -12}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {0, 94, 138}, 
    thickness = 5)}), 
    Documentation(link = "modelica://TYThermoFluidSys/Resources/HTML/SteamPowerCycle.html"), __MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=360,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="Result", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 7200), zoom_y_l=(0, 16)), 
Plot(y=["steamTurbine.m_flow_in"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[kW]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 7200), zoom_y_l=(-2000, 12000)), 
Plot(y=["steamTurbine.P_t"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 7200), zoom_y_l=(66.8, 67.05)), 
Plot(y=["boiler.V", "levelSetPoint.y"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 7200), zoom_y_l=(0, 80)), 
Plot(y=["suterPump.port_a.p", "suterPump.port_b.p"], colors=["4278190335", "4294901760"])})
})), Protection(access = Access.nonPackageDuplicate));

equation
  connect(boundaryHeatFlow.port[1], boiler.heatPort) 
    annotation(Line(origin = {-166, -41}, 
    points = {{16.1808, 31.4062}, {32, 31.4062}, {32, 31.9473}}, 
    color = {191, 0, 0}));
  connect(boundarySpeed1.flange, suterPump.flange_a) 
    annotation(Line(origin = {-63.7081, -92.9679}, 
    points = {{68.834, 48.8502}, {92.124336, 48.8502}, {92.124336, 30.2944}}, 
    color = {0, 0, 0}));
  connect(suterPump.port_b, boiler.port_a) 
    annotation(Line(origin = {-72, -68}, 
    points = {{83.560328, -8.565}, {-46.0982, -8.565}, {-46.0982, 44.3158}}, 
    color = {0, 178, 226}));
  connect(condenser.Water_out, boundaryPressure2.fluidPort) 
    annotation(Line(origin = {151.761, -5.04308}, 
    points = {{-76.60735, -4.38752}, {-76.60735, 25.04308}, {-50.3981, 25.04308}}, 
    color = {0, 178, 226}, 
    thickness = 0.5));
  connect(condenser.Water_in, boundaryPressure3.fluidPort) 
    annotation(Line(origin = {149.761, -28.0431}, 
    points = {{-74.6073, 7.31973}, {-48.3981, 7.31973}}, 
    color = {0, 178, 226}, 
    thickness = 0.5));
  connect(suterPump.port_a, condenser.Liquid_out) 
    annotation(Line(origin = {18, -56}, 
    points = {{24.7279, -20.565}, {39.9714, -20.565}, {39.9714, 23.5944}}, 
    color = {0, 178, 226}));
  connect(boundarySpeed.flange, steamTurbine.flange_a) 
    annotation(Line(origin = {-43.8191, 67}, 
    points = {{22.9095, 7}, {36.44555, 7}, {36.44555, -16.3957}}, 
    color = {0, 0, 0}));
  connect(controller.u, feedback.y) 
    annotation(Line(origin = {-34.3002, -14.6842}, 
    points = {{-46.0449, -30.237}, {-51.6998, -30.237}, {-51.6998, -3}, {-33.6998, -3}}, 
    color = {0, 0, 127}));
  connect(controller.y, limiter.u) 
    annotation(Line(origin = {-56.65, -14.6842}, 
    points = {{-7.5951, -30.237}, {4.25, -30.237}}, 
    color = {0, 0, 127}));
  connect(levelSetPoint.y, feedback.u1) 
    annotation(Line(origin = {-121.809, -97.5}, 
    points = {{88.0185, 79.8158}, {70.809, 79.8158}}, 
    color = {0, 0, 127}));
  connect(boiler.V, feedback.u2) 
    annotation(Line(origin = {-117, -79}, 
    points = {{16.3938, 75.7999}, {58, 75.7999}, {58, 69.3158}}, 
    color = {0, 0, 127}));
  connect(limiter.y, boundarySpeed1.w_in) 
    annotation(Line(origin = {-137, -77}, 
    points = {{100.7, 32.0788}, {111.12702, 32.0788}, {111.12702, 32.8823}}, 
    color = {0, 0, 127}));
  connect(steamTurbine.port_out, condenser.Steam_in) 
    annotation(Line(origin = {-9, 24}, 
    points = {{16.2632, 15.7998}, {55.5165, 15.7998}, {55.5165, -27.2001}}, 
    color = {0, 178, 226}));
  connect(boundaryHeatFlow.Q_flow_in, q_F_Tab.y) 
    annotation(Line(origin = {-200.282, -8.6726}, 
    points = {{22.282, -0.9212}, {7.4628, -0.9212}}, 
    color = {0, 0, 127}));
  connect(TSensor.port_a, steamTurbine.port_in) 
    annotation(Line(origin = {-134.8191, 36}, 
    points = {{86, -23.5596}, {103, -23.5596}, {103, 3.7998}, {114.718, 3.7998}}, 
    color = {0, 178, 226}));
  connect(steamTurbine.port_in, boiler.port_b) 
    annotation(Line(origin = {-69, 43}, 
    points = {{48.8988, -3.2002}, {-49.0982, -3.2002}, {-49.0982, -37.1286}}, 
    color = {0, 178, 226}));
end SteamPowerCycle;