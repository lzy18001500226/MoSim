model BatteryCool "电池水冷"
  parameter Integer N = 5 "电池水冷板换热离散段数";
  parameter Modelica.Units.SI.MassFlowRate mflow_top = 0.5 "上冷板入口质量流量";
  parameter Modelica.Units.SI.MassFlowRate mflow_bottom = 0.5 "下冷板入口质量流量";
  parameter Modelica.Units.SI.Temperature T_int = 293.15 "水路初始温度";
  parameter Modelica.Units.SI.Temperature T_intBatt = 313.15 "电池初始温度";
  TYBase.Battery.Model.BatteryQIn batteryQIn(N_cells = N, chargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, dischargeResTable = {{10, 0.2}, {20, 0.2}, {30, 0.2}, {40, 0.2}, {50, 0.2}, {60, 0.2}, {70, 0.2}, {80, 0.2}, {90, 0.2}}, Ns = 96, Np = 2, QCellNominal = 33, C = 2000, T0 = T_intBatt) 
    annotation (Placement(transformation(origin = {-16.221496628870995, 28.000000000000004},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeDS coolingPipeDS(n = N, title = "水管道", Aheat = 0.1918, redeclare model Friction = TYBase.Thermal.FluidHeatFlow.PressureLoss.LiquidPressureDrop.SingularPressureDrop, redeclare Integer calType = 2, CF_HeatTransfer = 10, T0 = T_int) 
    annotation (Placement(transformation(origin = {-16.174548314435498, -44.010082025725545},
      extent = {{-10.0469483144355, -10.008632925201297}, {10.011048314435497, 10.010082025725545}})));



  TYBase.Battery.Component.Ground ground annotation (HideResult = true, Placement(transformation(origin = {15.778503371129027, -30.0},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));



  TAThermalSystem.Pipes.LiquidCoolingPipe.CoolingPipeDS coolingPipeDS1(n = N, title = "水管道",
    Aheat = 0.1918,
    redeclare Integer calType = 2,
    CF_HeatTransfer = 10,
    T0 = T_int) 
    annotation (Placement(transformation(origin = {-16.17454831443549, 71.98991797427445},
      extent = {{-10.0469483144355, -10.008632925201297}, {10.011048314435497, 10.010082025725545}})));
  Modelica.Electrical.Analog.Sources.ConstantCurrent constantCurrent(I = 66 * 2) 
    annotation (Placement(transformation(origin = {-16.1635, -15.98128504907315},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT2(title = "冷却液源", T = T_int) 
    annotation (Placement(transformation(origin = {45.61500337112899, 72.00000000000003},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT coolant_pT3(title = "冷却液源", T = T_int) 
    annotation (Placement(transformation(origin = {45.615003371129, -44.04785605607968},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT coolant_mT2(p0 = 1.5e5, mflow = mflow_top, T_source = T_int) 
    annotation (Placement(transformation(origin = {-77.99999999999997, 71.9521439439203},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_mT coolant_mT3(p0 = 1.5e5, mflow = mflow_bottom, T_source = T_int) 
    annotation (Placement(transformation(origin = {-77.99999999999999, -44.04785605607968},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/Batterycool.html",info="<html><p>
<br>
</p>
</html>"),
    Protection(access=Access.nonPackageDuplicate),experiment(Algorithm=Dassl,NumberOfIntervals=500,StartTime=0,StopTime=100,Tolerance=0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[degC]", fix_time_range_value=0, zoom_x=(0, 100), zoom_y_l=(20, 45)),
Plot(y=["batteryQIn.Batt_top[1].T", "batteryQIn.Batt_top[2].T", "batteryQIn.Batt_top[3].T", "batteryQIn.Batt_top[4].T", "batteryQIn.Batt_top[5].T"], colors=["4294901760", "4278222848", "4294902015", "4278190080", "4294951205"])})
})));
equation
  connect(batteryQIn.pin_p, constantCurrent.p) 
    annotation (Line(origin = {-27.0, 6.0},
      points = {{0.7785033711290055, 22.000000000000004}, {0.7785033711290055, 20.0}, {-10.0, 20.0}, {-10.0, -21.98128504907315}, {0.8365000000000009, -21.98128504907315}},
      color = {0, 0, 255}));
  connect(constantCurrent.n, batteryQIn.pin_n) 
    annotation (Line(origin = {-5.0, 6.0},
      points = {{-1.163499999999999, -21.98128504907315}, {14.0, -21.98128504907315}, {14.0, 22.000000000000004}, {-1.2214966288709945, 22.000000000000004}},
      color = {0, 0, 255}));
  connect(ground.p, batteryQIn.pin_n) 
    annotation (Line(origin = {5.0, 4.0},
      points = {{10.778503371129027, -24.0}, {10.778503371129027, -10.0}, {4.0, -10.0}, {4.0, 24.000000000000004}, {-11.221496628870995, 24.000000000000004}},
      color = {0, 0, 255}));
  connect(coolingPipeDS1.qa, batteryQIn.Batt_top) 
    annotation (Line(origin = {-10.0, 61.0},
      points = {{-6.174548314435491, 20.989917974274448}, {-4.0, 20.989917974274448}, {-4.0, 20.65269461077844}, {9.017964071856287, 20.65269461077844}, {9.017964071856287, -24.15}, {3.7785033711290055, -24.15}},
      color = {191, 0, 0},
      thickness = 1.0));
  connect(coolant_mT2.port_b, coolingPipeDS1.a) 
    annotation (Line(origin = {-47.0, 72.0},
      points = {{-20.99999999999997, -0.04785605607969501}, {20.81533364171965, -0.0478560560796808}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolant_mT3.port_b, coolingPipeDS.a) 
    annotation (Line(origin = {-47.0, -44.0},
      points = {{-20.999999999999986, -0.0478560560796808}, {20.815333641719644, -0.04785605607967369}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolingPipeDS1.b, coolant_pT2.port_a) 
    annotation (Line(origin = {15.0, 72.0},
      points = {{-21.051108179528235, -0.0478560560796808}, {20.615003371128992, 2.842170943040401e-14}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolingPipeDS.b, coolant_pT3.port_a) 
    annotation (Line(origin = {15.0, -44.0},
      points = {{-21.051108179528242, -0.04785605607967369}, {20.615003371129, -0.0478560560796808}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(coolingPipeDS.qa, batteryQIn.Batt_bot) 
    annotation (Line(origin = {-9.0, -2.0},
      points = {{-7.174548314435498, -32.010082025725545}, {-7.174548314435498, -30.526946107784433}, {7.658682634730539, -30.526946107784433}, {7.658682634730539, 32.95}, {2.7785033711290055, 32.95}},
      color = {191, 0, 0},
      thickness = 1.0));
end BatteryCool;