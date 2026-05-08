model HVACCircuitApplication "闭环空调回路应用,应用在系统模型集成中,不能单独运行"
  annotation(Diagram(coordinateSystem(extent={{-140,-120},{140,120}}, 
grid={2,2})), 
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/HVACCircuitApplication.html"
), 
    Protection(access=Access.nonPackageDuplicate), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Text(origin = {177.0, 76.0}, 
    extent = {{-71.0, 22.0}, {71.0, -22.0}}, 
    textString = "压缩机转速rpm", 
    fontName = "微软雅黑", 
    textStyle = {TextStyle.None}), Text(origin = {0.0, 69.0}, 
    extent = {{-80.0, 15.0}, {80.0, -15.0}}, 
    textString = "HVAC冷凝器空气流通", 
    fontName = "微软雅黑", 
    textStyle = {TextStyle.None}), Text(origin = {0.0, -71.0}, 
    extent = {{-80.0, 15.0}, {80.0, -15.0}}, 
    textString = "HVAC蒸发器空气流通", 
    fontName = "微软雅黑", 
    textStyle = {TextStyle.None})}));
  extends TAThermalSystem.Utilities.Icons.SpecialIcons.HVACCircuit;
  Real[4] xin = {compressorR134a.hout, condenser1.refrigerant.h_out, evaporatorR134a.refrigerant.h_in, compressorR134a.hin} "横坐标比焓变量,单位kJ/kg" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));
  Real[4] yin = {compressorR134a.pout, condenser1.refrigerant.b.p, evaporatorR134a.refrigerant.a.p, compressorR134a.pin} "纵坐标对应压力变量,单位Pa" annotation(Dialog(group = "可视化变量序列,用于ph相图动态显示"));

  parameter Modelica.Units.SI.Temperature T_Amb = 308.15 "环境温度";
  parameter Real phi_Amb = 0.4 "环境湿度";
  parameter Modelica.Units.SI.Pressure P0_high = 12e5 "高压侧初始压力";
  parameter Modelica.Units.SI.Pressure P0_low = 3e5 "低压侧初始压力";
  parameter Modelica.Units.SI.SpecificEnthalpy h0_high = 400e3 "压缩机排气初始比焓";
  parameter Modelica.Units.SI.SpecificEnthalpy h0_low = 250e3 "蒸发器前初始比焓";
  parameter Integer n_segAirCond = 1 
    "空气流道的离散段数,每层中的空气段数" annotation(Dialog(tab = "冷凝器", group = "离散"));
  parameter Modelica.SIunits.MassFlowRate mdotAir_cond = 1 "前端模块空气流量" annotation(Dialog(tab = "冷凝器"));
  parameter Integer n_segRefCond = 2 
    "每个冷媒管道的离散段数" annotation(Dialog(tab = "冷凝器", group = "离散"));
  parameter Integer n_segMtlCond = 1 "所有管道金属壁面的离散段数" annotation(Dialog(tab = "冷凝器", group = "离散"));
  replaceable record GeometryCondensor = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal 
    constrainedby TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal "几何数据" 
    annotation(Dialog(tab = "冷凝器", group = "几何"), choicesAllMatching = true, 
    Protection(access=Access.nonPackageDuplicate));
  replaceable record HEXmaterial_Cond = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium 
    constrainedby TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterial 
    "热构件材料" annotation(Dialog(tab = "冷凝器", group = "材料"), Protection(access=Access.nonPackageDuplicate));
  replaceable record HX_InitCondensor = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HEXInit(T0 = T_Amb, T_air0 = T_Amb) 
    "组件初始化" annotation(Dialog(tab = "冷凝器", group = "初始化"), 
    Protection(access=Access.nonPackageDuplicate)) 
    constrainedby TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HEXInit;
  parameter Integer n_segAirEvap = 1 
    "空气流道的离散段数,每层中的空气段数" annotation(Dialog(tab = "蒸发器", group = "离散"));
  parameter Integer n_segRefEvap = 2 
    "每个冷媒管道的离散段数" annotation(Dialog(tab = "蒸发器", group = "离散"));
  parameter Integer n_segMtlEvap = 1 "所有管道金属壁面的离散段数" annotation(Dialog(tab = "蒸发器", group = "离散"));
  replaceable record GeometryEvaporator = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoVertical 
    constrainedby TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoVertical "几何数据" annotation(Dialog(tab = "蒸发器", group = "几何"), choicesAllMatching = true, 
    Protection(access=Access.nonPackageDuplicate));
  replaceable record HEXmaterial_Evap = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterialType.WallMaterialAluminium 
    constrainedby TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.PropertiesRecords.WallMaterial 
    "热构件材料" annotation(Dialog(tab = "蒸发器", group = "材料"), Protection(access=Access.nonPackageDuplicate));
  replaceable record HX_InitEvaporator = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HEXInit(T0 = T_Amb, T_air0 = T_Amb) 
    "组件初始化" annotation(Dialog(tab = "蒸发器", group = "初始化"), 
    Protection(access=Access.nonPackageDuplicate)) 
    constrainedby TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HEXInit;
  parameter Real k = 0.02 "热膨胀阀比例系数k" 
    annotation(Dialog(tab = "控制阀", group = "控制特性"));
  parameter Real yMax = 0.3 "最大开度的值" 
    annotation(Dialog(tab = "控制阀", group = "流动特性"));
  parameter Real yMin = 0.001 
    "最小开度的值" 
    annotation(Dialog(tab = "控制阀", group = "流动特性"));
  parameter Modelica.Units.SI.MassFlowRate mdot0 = 0.05 "初始化质量流量" 
    annotation(Dialog(tab = "控制阀", group = "初始化"));
  parameter Modelica.Units.SI.TemperatureDifference SuperHeatSetPoint = 5 
    "蒸发器过热度设置值" 
    annotation(Dialog(tab = "控制阀", group = "控制特性"));
  parameter Modelica.Units.SI.Time Ti = 10 "液态膨胀时间常数" 
    annotation(Dialog(tab = "控制阀", group = "控制特性"));
  parameter Boolean steadySuperheat = true 
    "是否设置过热稳态初始值" 
    annotation(Dialog(tab = "控制阀", group = "控制特性"));
  parameter Modelica.Units.SI.Length D(displayUnit = "mm") = 0.005 "喉部直径" 
    annotation(Dialog(tab = "控制阀", group = "几何"));
  TAThermalSystem.Sensors.Refrigerant.SuperHeatingSensor superHeatingSensor(redeclare package Medium = TYMedia.Helmholtz.R134a) annotation(Placement(transformation(origin = {-64.0, 12.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));

  TAThermalSystem.HeatExchangers.Evaporator evaporatorR134a(

    n_segAir = n_segAirEvap, n_segRef = n_segRefEvap, n_segMtl = n_segMtlEvap, 
  redeclare record HXGeo = GeometryEvaporator, HX_Init(T0 = T_Amb, T_air0 = T_Amb, h_in = h0_low, h_out = h0_high),CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a) 

    annotation(Placement(transformation(origin = {-70.0, -30.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));


  TAThermalSystem.HeatExchangers.Condenser condenser(

    n_segAir = n_segAirCond, n_segRef = n_segRefCond, n_segMtl = n_segMtlCond, 
  redeclare record HXGeo = GeometryCondensor,   HX_Init(T0 = T_Amb, T_air0 = T_Amb, p_in = P0_high, p_out = P0_high, h_in = h0_high, h_out = h0_low),CF_AirSideHeatTransfer=10,CF_RefrigerantSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a) 


    annotation(Placement(transformation(origin = {99.11428571428577, -66}, 
    extent = {{11, 11}, {-11, -11}})));

  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation(Placement(transformation(origin = {28.0, 56.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Compressor.Compressor compressorR134a(
    p0_in = P0_low, p0_out = P0_high, 
    MaximumDisplacement(displayUnit = "ml") = 3.5e-5,h0_out=h0_high,h0_in=h0_low,redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation(Placement(transformation(origin = {48.0, 80.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Utilities.summary.summaryHVAC summaryHVAC 
    annotation(Placement(transformation(origin = {-90.0, 88.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Interfaces.RealInput speed_in_rpm "Reference angular velocity of flange with respect to support as input signal" 
    annotation(Placement(transformation(origin = {60.0, 34.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}), 
    iconTransformation(origin = {100.0, 40.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_evapout(temperature = summaryHVAC.temp_evap_out, pressure = summaryHVAC.press_evap_out, specificEnthalpy = summaryHVAC.h_evap_out, massflowRate = summaryHVAC.mdot_evap_out, blockname = "蒸发器出口") 
    annotation(Placement(transformation(origin = {-116.0, 8.0}, 
    extent = {{-10.0, -4.0}, {34.0, 10.0}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_evapin(temperature = summaryHVAC.temp_evap_in, pressure = summaryHVAC.press_evap_in, specificEnthalpy = summaryHVAC.h_evap_in, massflowRate = summaryHVAC.mdot_evap_in, blockname = "蒸发器进口") 
    annotation(Placement(transformation(origin = {-116.0, -62.0}, 
    extent = {{-10.0, -4.0}, {34.0, 10.0}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_condout(temperature = summaryHVAC.temp_cond_out, pressure = summaryHVAC.press_cond_out, specificEnthalpy = summaryHVAC.h_cond_out, massflowRate = summaryHVAC.mdot_cond_out, blockname = "冷凝器出口") 
    annotation(Placement(transformation(origin = {46.0, -26.0}, 
    extent = {{-10.0, -4.0}, {34.0, 10.0}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display hX_Display_condin(temperature = summaryHVAC.temp_cond_in, pressure = summaryHVAC.press_cond_in, specificEnthalpy = summaryHVAC.h_cond_in, massflowRate = summaryHVAC.mdot_cond_in, blockname = "冷凝器进口") 
    annotation(Placement(transformation(origin = {104.0, -26.0}, 
    extent = {{-10.0, -4.0}, {34.0, 10.0}})));
  TAThermalSystem.Utilities.DynamicDisplay.Single_Display single_Display(variable = superHeatingSensor.outPort, blockname = "过热度/°C") 
    annotation(Placement(transformation(origin = {-45.0, 21.0}, 
    extent = {{-15.0, 3.0}, {21.0, 15.0}})));
  TAThermalSystem.Reservoirs.Reservoir_fillinglevel reservoir(zeta = 30,H_Out=0.02,FillingLevel0=0.1,redeclare package Medium = TYMedia.Helmholtz.R134a) 

    annotation(Placement(transformation(origin={46,-59.3}, 
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Interfaces.FluidInterfaces.AirPortIn air_in1 
    annotation(Placement(transformation(origin = {-90.0, -10.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}), 
    iconTransformation(origin = {-60.0, -100.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Interfaces.FluidInterfaces.AirPortOut air_out1 
    annotation(Placement(transformation(origin = {-76.0, -74.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}), 
    iconTransformation(origin = {60.0, -100.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Utilities.DynamicDisplay.HX_Display_legend hX_Display_legend annotation(Placement(transformation(origin = {-126.81818181818181, 60.81818181818181}, 
    extent = {{-13.181818181818173, -5.272727272727273}, {44.81818181818183, 13.18181818181818}})));

  Modelica.Blocks.Math.Gain gain1(k = Modelica.Constants.pi / 30) 
    annotation(Placement(transformation(origin = {19.999999999999996, 34.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sensors.Refrigerant.PTSensor pTSensor(
    SelectMode = TAThermalSystem.Sensors.Refrigerant.Mode.h, print_var = false,outPortP(start=5e5),redeclare package Medium = TYMedia.Helmholtz.R134a) 

    annotation(Placement(transformation(origin = {78, 80}, 
    extent = {{-10, -10}, {10, 10}})));









  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe lumpedPipeR134a(
  redeclare package Medium = TYMedia.Helmholtz.R134a, 
    init(h_in = h0_high, h_out = h0_high, T0 = T_Amb, T_air0 = T_Amb),RefrigerantMassDistribution=2) 

    annotation(Placement(transformation(origin = {116, 34}, 
    extent = {{10, 10}, {-10, -10}}, 
    rotation = -270)));
  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe lumpedPipeR134a1(
  redeclare package Medium = TYMedia.Helmholtz.R134a, 
    init(h_in 
= h0_low, h_out 
= h0_low, T0 = T_Amb, T_air0 = T_Amb),RefrigerantMassDistribution=2) 

    annotation(Placement(transformation(origin={-18,-59.3}, 
extent={{10,10},{-10,-10}}, 
rotation=-360)));
  TAThermalSystem.Sources.Air.AirSink_pT airSink2(T_sink = 303.15) 
    annotation(Placement(transformation(origin={128.77,-88.809}, 
extent={{10,-10},{-10,10}})));
  Modelica.Blocks.Sources.Constant const(k = T_Amb) 
    annotation(Placement(transformation(origin={-102.43,-144.889}, 
extent={{-7,-7},{7,7}})));
  Modelica.Blocks.Sources.Constant const1(k = phi_Amb) 
    annotation(Placement(transformation(origin={-102.43,-120.846}, 
extent={{-7,-7},{7,7}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource3(m = 0.11, T = 303.15, 
    phi_source = 40, use_mT_input = true) 

    annotation(Placement(transformation(origin={76.1286,-89.0797}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const2(k = mdotAir_cond) 
    annotation(Placement(transformation(origin={-102.43,-96.8031}, 
extent={{-7,-7},{7,7}})));
  TAThermalSystem.Utilities.DynamicDisplay.ph_R134a ph_R134a1(
    x = xin, y = yin
    ) 
    annotation(Placement(transformation(origin = {165, -101}, 
    extent = {{-1.4210854715202004e-14, 0}, {199, 199}})));
  TAThermalSystem.Pipes.TwoPhasePipe.SimplePipe lumpedPipeR134a2(
  redeclare package Medium = TYMedia.Helmholtz.R134a, 
    init(h_in = 200e3, h_out = 200e3, T0 = T_Amb, T_air0 = T_Amb),RefrigerantMassDistribution=2) 

    annotation(Placement(transformation(origin={-21,80}, 
extent={{10,10},{-10,-10}}, 
rotation=-180)));
  TAThermalSystem.Valves.RefrigerantValve.SimpleEXV simpleTXV(k=k,SuperHeatSetPoint=SuperHeatSetPoint,Ti=Ti,yMax=yMax,yMin=yMin,D=D,redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation (Placement(transformation(origin={-40,-60}, 
extent={{10,10},{-10,-10}})));
  TAThermalSystem.HeatExchangers.Condenser condenser1(redeclare record HXGeo = TYBase.Thermal.FluidHeatFlow.Components.BasicComponents.Records.HXRecords.HXGeoHorizontal(flattubes = {20}, flowScheme = {{1}}),CF_RefrigerantSideHeatTransfer=10,CF_AirSideHeatTransfer=10,redeclare package Medium = TYMedia.Helmholtz.R134a) 
    annotation (Placement(transformation(origin={14,-65.3}, 
extent={{10,10},{-10,-10}})));
  TAThermalSystem.Sources.Air.AirSink_pT airSink1(T_sink = 303.15) 
    annotation(Placement(transformation(origin={44.8232,-86.1697}, 
extent={{10,-10},{-10,10}})));
  TAThermalSystem.Sources.Air.AirSource_mT airSource1(m = 0.11, T = 303.15, 
    phi_source = 40, use_mT_input = true) 

    annotation(Placement(transformation(origin={-30.6525,-87.117}, 
extent={{-10,-10},{10,10}})));
  TYBase.Blocks.Gain gain(k=0.75) 
    annotation (Placement(transformation(origin={57.8111,-96.258}, 
extent={{-7,-7},{7,7}})));
  TYBase.Blocks.Gain gain2(k=0.25) 
    annotation (Placement(transformation(origin={-60.4507,-97.5087}, 
extent={{-7,-7},{7,7}})));
  equation
  summaryHVAC.temp_cond_in = condenser.refrigerant.T_in;
  summaryHVAC.press_cond_in = condenser.refrigerant.p[1];
  summaryHVAC.h_cond_in = condenser.refrigerant.h[1];
  summaryHVAC.mdot_cond_in = 

















    condenser.refrigerant.mdot[1];

  summaryHVAC.temp_cond_out = condenser.refrigerant.T_out;
  summaryHVAC.press_cond_out = condenser.refrigerant.p[2];
  summaryHVAC.h_cond_out = condenser.refrigerant.h[2];
  summaryHVAC.mdot_cond_out = condenser.refrigerant.mdot[2];

  summaryHVAC.temp_evap_in = evaporatorR134a.refrigerant.T_in;
  summaryHVAC.press_evap_in = evaporatorR134a.refrigerant.p[1];
  summaryHVAC.h_evap_in 









    = evaporatorR134a.refrigerant.h[1];
  summaryHVAC.mdot_evap_in = evaporatorR134a.refrigerant.mdot[1];

  summaryHVAC.temp_evap_out = evaporatorR134a.refrigerant.T_out;
  summaryHVAC.press_evap_out = evaporatorR134a.refrigerant.p[2];
  summaryHVAC.h_evap_out = evaporatorR134a.refrigerant.h[2];
  summaryHVAC.mdot_evap_out = evaporatorR134a.refrigerant.mdot[3];

  connect(speed.flange, compressorR134a.flange) 
    annotation(Line(origin = {39.0, 67.0}, 
    points = {{-1.0, -11.0}, {9.0, -11.0}, {9.0, 3.0}}, 
    color = {0, 0, 0}));
  connect(superHeatingSensor.a, evaporatorR134a.b1) 
    annotation(Line(origin = {-64.0, -9.0}, 
    points = {{0.0, 11.0}, {0.0, -11.0}}, 
    color = {0, 128, 0}, 
    thickness = 1.0));
  connect(evaporatorR134a.air_in, air_in1) 
    annotation(Line(origin = {-83.0, -15.0}, 
    points = {{7.0, -5.0}, {7.0, 5.0}, {-7.0, 5.0}}, 
    color = {0, 232, 232}, 
    thickness = 1.0));
  connect(evaporatorR134a.air_out, air_out1) 
    annotation(Line(origin = {-76.0, -57.0}, 
    points = {{0.0, 17.0}, {0.0, -17.0}}, 
    color = {0, 232, 232}, 
    thickness = 1.0));
  connect(speed.w_ref, gain1.y) 
    annotation(Line(origin = {6.0, 45.0}, 
    points = {{10.0, 11.0}, {-10.0, 11.0}, {-10.0, -11.0}, {3.0, -11.0}}, 
    color = {0, 0, 127}));


  connect(gain1.u, speed_in_rpm) 
    annotation(Line(origin = {46.0, 34.0}, 
    points = {{-14.0, 0.0}, {14.0, 0.0}}, 
    color = {0, 0, 127}));
  connect(compressorR134a.b, pTSensor.a) 
    annotation(Line(origin = {69, 80}, 
    points = {{-11, 0}, {-1, 0}}, 
    color = {0, 128, 0}, 
    thickness = 1));
  connect(pTSensor.b, lumpedPipeR134a.a) 
    annotation(Line(origin = {102, 62}, 
    points = {{-14, 18}, {14, 18}, {14, -18}}, 
    color = {0, 128, 0}, 
    thickness = 1));
  connect(lumpedPipeR134a.b, condenser.a1) 
    annotation(Line(origin = {92, -18}, 
    points = {{24, 42}, {24, -41.4}, {18.11428571428577, -41.4}}, 
    color = {0, 128, 0}, 
    thickness = 1));
  connect(const.y, airSource3.T_input_K) 
    annotation(Line(origin={34.2784,-130.734}, 
points={{-129.0084,-14.155},{41.8502,-14.155},{41.8502,51.6543}}, 
color={0,0,127}));
  connect(const1.y, airSource3.phi_input) 
    annotation(Line(origin={48.2784,-130.734}, 
points={{-143.0084,9.888},{33.8502,9.888},{33.8502,51.6543}}, 
color={0,0,127}));
  connect(condenser.air_in, airSource3.port_b) 
    annotation(Line(origin={85,-85}, 
points={{3.11429,12.4},{1.12857,12.4},{1.12857,-4.07972}}, 
color={0,232,232}, 
thickness=1));
  connect(condenser.air_out, airSink2.port_a) 
    annotation(Line(origin={111,-85}, 
points={{-0.885714,12.4},{2.21429,12.4},{2.21429,-3.80899},{7.76962,-3.80899}}, 
color={0,232,232}, 
thickness=1));
  connect(airSource3.m_input, gain.y) 
    annotation(Line(origin={-3.55271e-15,-125.118}, 
points={{70.1286,46.0381},{70.1286,28.8599},{65.5111,28.8599}}, 
color={0,0,127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(reservoir.port_a, condenser.b1) 
    annotation(Line(origin={47,-59}, 
points={{9,-0.3999999999999986},{41.11428571428577,-0.3999999999999986}}, 
color={0,128,0}, 
thickness=1));
  connect(lumpedPipeR134a2.b, compressorR134a.a) 
  annotation(Line(origin={14,80}, 
  points={{-25,0},{24,0}}, 
  color={0,128,0}, 
  thickness=1));
  connect(lumpedPipeR134a2.a, superHeatingSensor.b) 
  annotation(Line(origin={-47,51}, 
  points={{16,29},{-17,29},{-17,-29}}, 
  color={0,128,0}, 
  thickness=1));
  connect(simpleTXV.a, lumpedPipeR134a1.b) 
  annotation(Line(origin={-22,-60}, 
points={{-8,0},{-6,0},{-6,0.7000000000000028}}, 
color={0,128,0}, 
thickness=1));
  connect(simpleTXV.b, evaporatorR134a.a1) 
  annotation(Line(origin={-57,-50}, 
points={{7,-10},{-7,-10},{-7,10}}, 
color={0,128,0}, 
thickness=1));
  connect(superHeatingSensor.outPort, simpleTXV.DeltaT_SH) 
  annotation(Line(origin={-46,-19}, 
  points={{-6.600000000000001,31},{6,31},{6,-31}}, 
  color={0,0,127}));
  connect(condenser1.a1, reservoir.b) 
  annotation(Line(origin={30,-59}, 
  points={{-6,-0.29999999999999716},{6,-0.29999999999999716},{6,-0.3999999999999986}}, 
  color={0,128,0}, 
  thickness=1));
  connect(condenser1.b1, lumpedPipeR134a1.a) 
  annotation(Line(origin={-2,-59}, 
  points={{6,-0.29999999999999716},{-6,-0.29999999999999716}}, 
  color={0,128,0}, 
  thickness=1));
  connect(airSource1.port_b, condenser1.air_in) 
  annotation(Line(origin={-19,-86}, 
points={{-1.65252,-1.11705},{1,-1.11705},{1,14.7},{23,14.7}}, 
color={0,232,232}, 
thickness=1));
  connect(airSink1.port_a, condenser1.air_out) 
  annotation(Line(origin={8,-84}, 
points={{26.8232,-2.16971},{26.8232,12.7},{16,12.7}}, 
color={0,232,232}, 
thickness=1));
  connect(gain.u, const2.y) 
  annotation(Line(origin={31,-97}, 
points={{18.4111,0.741993},{-125.73,0.741993},{-125.73,0.1969}}, 
color={0,0,127}));
  connect(gain2.y, airSource1.m_input) 
  annotation(Line(origin={-59,-106}, 
points={{6.24929,8.49129},{22.3475,8.49129},{22.3475,28.883}}, 
color={0,0,127}));
  connect(airSource1.T_input_K, const.y) 
  annotation(Line(origin={-5,-134}, 
points={{-25.6525,56.883},{-25.6525,-10.889},{-89.73,-10.889}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(const1.y, airSource1.phi_input) 
  annotation(Line(origin={-2,-116}, 
points={{-92.73,-4.846},{-22.6525,-4.846},{-22.6525,38.883}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
  connect(const2.y, gain2.u) 
  annotation(Line(origin={1,-103}, 
points={{-95.73,6.1969},{-69.8507,6.1969},{-69.8507,5.49129}}, 
color={0,0,127}),__MWORKS(BlockSystem(NamedSignal)));
end HVACCircuitApplication;