model CoolingSystem "电机冷却示例"
  annotation(Documentation(link = "modelica://TYMotor/Resources/HTML/CoolingSystem.html"), Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=4, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-10, 60)), 
Plot(y=["PMDC1.w", "ramp.y"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(13, 21)), 
Plot(y=["PMDC1.port_a.T"], colors=["4278190335"])})
})));
  extends TYMotor.Utilities.Icons.Common.Example;
  //******************** 电源电压 ********************//
  parameter Modelica.Units.SI.Voltage V = 48 
    annotation(Dialog(tab = "电源参数"));
  //******************** 电机参数 ********************//
  parameter Boolean useSupport = false 
    "=false，不使用支撑（定子固定）" 
    annotation(Dialog(tab = "电机参数"), Evaluate = true);
  parameter Boolean useHeatPort = true 
    "使用/不使用热接口" 
    annotation(Dialog(tab = "电机参数"), Evaluate = true);
  parameter Modelica.Units.SI.Inertia J_Rotor = 0.15 
    "转子转动惯量" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Inertia J_Stator = J_Rotor 
    "定子转动惯量" 
    annotation(Dialog(tab = "电机参数"), enable = useSupport);
  parameter Modelica.Units.SI.RotationalDampingConstant d(final min = 0, start = 0) = 0 
    "阻尼系数" 
    annotation(Dialog(tab = "电机参数"));
  // 额定参数
  parameter Modelica.Units.SI.Voltage VaNominal = 100 
    "额定电枢电压" 
    annotation(Dialog(tab = "电机参数", group = "额定参数"));
  parameter Modelica.Units.SI.Current IaNominal = 100 
    "额定电枢电流" 
    annotation(Dialog(tab = "电机参数", group = "额定参数"));
  parameter Modelica.SIunits.Conversions.NonSIunits.AngularVelocity_rpm rpmNominal = 1425 
    "额定转速" 
    annotation(Dialog(tab = "电机参数", group = "额定参数"));
  // 额定电阻与电感
  parameter Modelica.Units.SI.Resistance Ra = 0.05 
    "电枢电阻" 
    annotation(Dialog(tab = "电机参数", group = "额定电阻与电感"));
  parameter Modelica.Units.SI.Inductance La = 0.0015 
    "电枢电感" 
    annotation(Dialog(tab = "电机参数", group = "额定电阻与电感"));
  parameter Modelica.Units.SI.Inductance Le = 1 
    "励磁电感" 
    annotation(Dialog(tab = "电机参数", group = "励磁"));
  parameter Modelica.Units.SI.Current IeNominal = 1 
    "等效励磁电流" 
    annotation(Dialog(tab = "电机参数", group = "励磁"));
  //******************** 热计算 ********************//
  parameter Modelica.Units.SI.HeatCapacity C = 1000 "电机热容 (= cp*m)" 
    annotation(Dialog(tab = "电机参数", group = "热计算"));
  parameter Modelica.Units.SI.Temperature T_start = 293.15 "电机初始温度" 
    annotation(Dialog(tab = "电机参数", group = "热计算"));
  parameter Modelica.Units.SI.TemperatureSlope der_T_start = 0 "温度对时间导数的初值 (= der(T))" 
    annotation(Dialog(tab = "电机参数", group = "热计算"));
  //--------------- 控制器参数 ---------------//
  parameter Integer N = 2 
    "控制模式选择，1：位置控制，2：速度控制 " 
    annotation(Dialog(tab = "控制器参数", group = "电机控制模式"), 
    choices(
    choice = 1 "位置控制", 
    choice = 2 "速度控制"));
  //角度PID参数
  parameter Real kp_phi = 10 
    "比例系数 " 
    annotation(Dialog(tab = "控制器参数", group = "位置环参数"));
  parameter Real Ti_phi = 0.1 
    "积分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "位置环参数"));
  parameter Real Td_phi = 0.1 
    "微分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "位置环参数"));
  parameter Real uMax_phi = 1e7 
    "上限" 
    annotation(Dialog(tab = "控制器参数", group = "位置环参数"));
  parameter Real uMin_phi = -1e7 
    "下限" 
    annotation(Dialog(tab = "控制器参数", group = "位置环参数"));
  //角速度PID参数
  parameter Real kp_w = 30 
    "比例系数 " 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  parameter Real Ti_w = 0.1 
    "积分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  parameter Real Td_w = 0.1 
    "微分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  //限幅模块参数
  parameter Real uMax_w = 1e7 
    "上限" 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  parameter Real uMin_w = -1e7 
    "下限" 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  //电流环参数
  parameter Real kp_i = 30 
    "比例系数 " 
    annotation(Dialog(tab = "控制器参数", group = "电流环参数"));
  parameter Real Ti_i = 0.1 
    "积分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "电流环参数"));
  parameter Real Td_i = 0.1 
    "微分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "电流环参数"));
  //******************** DCDC变换器 ********************//
  parameter String ConverterType = "FullBridge" 
    "选择 DCDC 变换器类型" 
    annotation(choices(choice = "Buck/Chopper" "Buck/Chopper", 
    choice = "Boost" "Boost", 
    choice = "Buck-Boost" "Buck-Boost", 
    choice = "FullBridge" "FullBridge"), Dialog(tab = "DCDC变换器"));
  parameter Modelica.Units.SI.Voltage VDC = 200 
    "电源额定电压" 
    annotation(Dialog(tab = "DCDC变换器"));
  parameter Modelica.Units.SI.Current INominal = 10 
    "电源额定电流" 
    annotation(Dialog(tab = "DCDC变换器"));
  parameter Modelica.Units.SI.Time TiConverter = 1e-5 
    "特征时间常数" 
    annotation(Dialog(tab = "DCDC变换器"));
  parameter Modelica.Units.SI.Current IConverterMax = 100 
    "最大直流供电电流" 
    annotation(Dialog(tab = "DCDC变换器"));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torquestep(stepTorque = -1, 
    startTime = 1, offsetTorque = 0) 
    annotation(Placement(transformation(origin = {66, -12}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {-48.0, 25.997}, 
    extent = {{-10.0, -9.997}, {10.000000000000007, 9.997}})));
  TYMotor.Sensors.CurrentSensor1ph currentsensor 
    annotation(Placement(transformation(origin = {-6.0, 24.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -270.0)));
  TYMotor.Machines.DCMachines.PMDC PMDC1(
    J_Rotor = J_Rotor, VaNominal = VaNominal, IaNominal = IaNominal, rpmNominal = rpmNominal, Ra = Ra, La = La, 
    ra(alpha = 
    0), 
    d = d, 
    useHeatPort = useHeatPort, 
    C = C, 
    T_start = T_start, 
    der_T_start = der_T_start, 
    IeNominal = IeNominal) annotation(Placement(transformation(origin = {-11.999999999999998, -12.000000000000007}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMotor.Controllers.PMDC.PMDC_Controller controller(
    kp_phi = kp_phi, Ti_phi = Ti_phi, Td_phi = Td_phi, uMax_phi = uMax_phi, kp_w = kp_w, Ti_w = Ti_w, Td_w = Td_w, uMax_w = uMax_w, kp_i = kp_i, Ti_i = Ti_i, Td_i = Td_i, 
    uMin_w = uMin_w, uMin_phi = uMin_phi, 
    N = N) 
    annotation(Placement(transformation(origin = {18.0, 52.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Converters.PowerBalance.DCDC.Ideal dcdc(ConverterType = ConverterType, VDC = VDC, INominal = INominal, TiConverter = TiConverter, IConverterMax = IConverterMax) 
    annotation(Placement(transformation(origin = {-12.0, 52.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = V) 
    annotation(Placement(transformation(origin = {-48.0, 52.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYMotor.Sensors.AngleSensor angleSensor 
    annotation(Placement(transformation(origin = {46.0, 18.0}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = -270.0)));
  Modelica.Blocks.Sources.Ramp ramp(height = 50, duration = 5) 
    annotation(Placement(transformation(origin = {66.00000000000001, 58.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature fixedTemperature(T = 283.15) 
    annotation(Placement(transformation(origin = {-58.0, -37.994}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor thermalConductor(G = 100) 
    annotation(Placement(transformation(origin = {-32.0, -37.994}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation(Placement(transformation(origin = {-48.00000000000001, -11.997000000000007}, 
    extent = {{-10.0, -9.997}, {10.000000000000007, 9.997}})));
equation
  connect(PMDC1.pin_ap, currentsensor.n) 
    annotation(Line(origin = {-18, 81}, 
    points = {{10.000000000000002, -81}, {12, -81}, {12, -67}}, 
    color = {0, 0, 255}));
  connect(PMDC1.flange_a, torquestep.flange) 
    annotation(Line(origin = {0, 41}, 
    points = {{0.6, -53}, {56, -53}}, 
    color = {0, 0, 0}));
  connect(controller.i, currentsensor.i) 
    annotation(Line(origin = {47.0, 10.0}, 
    points = {{-18.0, 36.0}, {-12.0, 36.0}, {-12.0, 14.0}, {-42.0, 14.0}}, 
    color = {0, 0, 127}));
  connect(dcdc.pLoad, currentsensor.p) 
    annotation(Line(origin = {-29.0, 56.0}, 
    points = {{23.0, -14.0}, {23.0, -22.0}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.n, dcdc.nSupply) 
    annotation(Line(origin = {-74.0, 74.0}, 
    points = {{26.0, -32.0}, {52.0, -32.0}, {52.0, -28.0}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.p, dcdc.pSupply) 
    annotation(Line(origin = {-85.0, 73.0}, 
    points = {{37.0, -11.0}, {63.0, -11.0}, {63.0, -15.0}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.n, ground.p) 
    annotation(Line(origin = {-72.0, 46.0}, 
    points = {{24.0, -4.0}, {24.0, -10.0}}, 
    color = {0, 0, 255}));
  connect(angleSensor.flange_a, PMDC1.flange_a) 
    annotation(Line(origin = {2, 14}, 
    points = {{43.9, -6}, {43.9, -26.000000000000007}, {-1.3999999999999968, -26.000000000000007}}, 
    color = {0, 0, 0}));
  connect(angleSensor.phi, controller.phi) 
    annotation(Line(origin = {10.0, -47.0}, 
    points = {{36.0, 76.0}, {36.0, 99.0}, {19.0, 99.0}}, 
    color = {0, 0, 127}));
  connect(ramp.y, controller.ref) 
    annotation(Line(origin = {-4.0, -61.0}, 
    points = {{59.0, 119.0}, {33.0, 119.0}}, 
    color = {0, 0, 127}));
  connect(fixedTemperature.port, thermalConductor.port_a) 
    annotation(Line(origin = {-51.0, -37.994}, 
    points = {{3.0, 0.0}, {9.0, 0.0}}, 
    color = {191, 0, 0}));
  connect(thermalConductor.port_b, PMDC1.port_a) 
    annotation(Line(origin = {-25, 4}, 
    points = {{3, -41.994}, {13.000000000000002, -41.994}, {13.000000000000002, -26.000000000000007}}, 
    color = {191, 0, 0}));
  connect(controller.y, dcdc.vRef) 
    annotation(Line(origin = {14.0, 52.0}, 
    points = {{-7.0, 0.0}, {-16.0, 0.0}}, 
    color = {0, 0, 127}));
  connect(dcdc.nLoad, PMDC1.pin_an) 
    annotation(Line(origin = {-18, 33}, 
    points = {{0, 9}, {0, -33.00000000000001}, {2.0000000000000018, -33.00000000000001}}, 
    color = {0, 0, 255}));
  connect(ground1.p, PMDC1.pin_an) 
    annotation(Line(origin = {-33, 2}, 
    points = {{-15, -4.000000000000007}, {-15, -2.000000000000007}, {17, -2.000000000000007}}, 
    color = {0, 0, 255}));
  annotation(Icon(graphics, 
    coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    Diagram(graphics, 
    coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    Documentation(info = "<html><p>
该实例可以模拟永磁直流电机在外接冷却装置时的工作特性。实例中的冷却装置由固定温度，固定导热率的热板表示。
</p>
</html>"), 
    experiment(StartTime = 0, StopTime = 10, Interval = 0.01, Algorithm = Dassl, Tolerance = 0.0001, DoublePrecision = true, StoreEventValue = true, IntegratorStep = -1));
end CoolingSystem;