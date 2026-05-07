model PMSMSystem_DTC "永磁同步电机示例，直接转矩控制"
  annotation(Documentation(link = "modelica://TYMotor/Resources/HTML/PMSMSystem_DTC.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 739, 767], y=["sine.y", "angularVelecitySensor.w"], x_display_unit="s", y_display_units=["", "rad/s"], y_axis=[1, 1], legend_layout=1, legend_frame=True, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=6.95255e-310)})
})));
  import Modelica.Constants.pi;
  extends TYMotor.Utilities.Icons.Common.Example;
  //******************** 电源电压 ********************//
  parameter Modelica.Units.SI.Voltage V = 60 
    annotation(Dialog(tab = "电源参数"));
  //******************** 电机 ********************//
  parameter Modelica.Units.SI.Inductance Lrsigmad = 0.05 / (2 * pi * fsNominal) "转换到定子的d轴相电感" 
    annotation(Dialog(tab = "电机参数"));
  parameter Boolean useSupport = false 
    "使用支撑还是固定定子" 
    annotation(Dialog(tab = "电机参数"), Evaluate = true);
  parameter Modelica.Units.SI.Inertia J_Rotor = 0.0008 
    "转子转动惯量" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.RotationalDampingConstant d(final min = 0, start = 0) = 0 
    "阻尼系数" 
    annotation(Dialog(tab = "电机参数"));
  parameter Integer p = 4 
    "电机极对数" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Frequency fsNominal = 50 
    "额定频率" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Resistance Rs = 3 
    "定子绕组相电阻" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Inductance Lssigma = 0.0028 
    "定子相绕组的漏电感" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Voltage V0 = 26 
    "额定条件下每相空载有效电压" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Inductance Lmd = 0.0085 
    "d轴电感" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Inductance Lmq = 0.0085 
    "q轴电感" 
    annotation(Dialog(tab = "电机参数"));
  //******************** 逆变器参数 ********************//
  parameter Modelica.Units.SI.Current IConverterMax = 100 
    "最大直流供电电流" 
    annotation(Dialog(tab = "逆变器参数"));
  parameter Modelica.Units.SI.Resistance RonTransistor = 1e-5 
    "晶体管关断电阻" 
    annotation(Dialog(tab = "逆变器参数", group = "理想晶体管参数"));
  parameter Modelica.Units.SI.Conductance GoffTransistor = 1e-5 
    "晶体管开通电导" 
    annotation(Dialog(tab = "逆变器参数", group = "理想晶体管参数"));
  parameter Modelica.Units.SI.Voltage VkneeTransistor = 0 
    "晶体管阈值电压" 
    annotation(Dialog(tab = "逆变器参数", group = "理想晶体管参数"));
  parameter Modelica.Units.SI.Resistance RonDiode = 1e-5 
    "二极管关断电阻" 
    annotation(Dialog(tab = "逆变器参数", group = "理想二极管参数"));
  parameter Modelica.Units.SI.Conductance GoffDiode = 1e-5 
    "二极管开通电导" 
    annotation(Dialog(tab = "逆变器参数", group = "理想二极管参数"));
  parameter Modelica.Units.SI.Voltage VkneeDiode = 0 
    "门限电压" 
    annotation(Dialog(tab = "逆变器参数", group = "理想二极管参数"));
  TYMotor.Sensors.AngleSensor anglemeasure 
    annotation(Placement(transformation(origin = {18.001799999999996, -28.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));
  Modelica.Electrical.MultiPhase.Sensors.CurrentSensor currentmeasure 
    annotation(Placement(transformation(origin = {-30.0, 0.0}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = -90.0)));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantvoltage(V = V) 
    annotation(Placement(transformation(origin = {-68, 56.00000000000001}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {-68, 22}, 
    extent = {{-10, -10}, {10, 10.000000000000004}})));
  TYMotor.Sensors.AngularVelecitySensor angularVelecitySensor 
    annotation(Placement(transformation(origin = {0.0, -28.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torquestep(stepTorque = 0) 
    annotation(Placement(transformation(origin = {50.0, -52.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Converters.IdealSwitching.DCAC.ThreePhase inverter(RonTransistor = RonTransistor, GoffTransistor = GoffTransistor, VkneeTransistor = VkneeTransistor, RonDiode = RonDiode, GoffDiode = GoffDiode, VkneeDiode = VkneeDiode) 
    annotation(Placement(transformation(origin = {-30.000000000000004, 56.00000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMotor.Controllers.PMSM.PMSM_DTC PMSM_DTC(flux_Stator = 0.17, uLowTe = -0.2, uHighTe = 0.2, uLowFlux = -0.01, uHighighFlux = 0.01) annotation(Placement(transformation(origin = {24.0, 30.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Machines.Synchronous.PMSM PMSM1(
    J_Rotor = J_Rotor, p = p, fsNominal = fsNominal, V0 = V0, Lssigma = Lssigma, Rs = Rs, Lmd = Lmd, Lmq = Lmq, d = d) 
    annotation(Placement(transformation(origin = {-30.0, -52.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Sine sine(amplitude = 10, offset = 100) 
    annotation(Placement(transformation(origin = {56.0, 30.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(PMSM_DTC.fire_p, inverter.fire_p) 
    annotation(Line(origin = {-11.000000000000004, 17.999999999999993}, 
    points = {{24.0, 6.0}, {-25.0, 6.0}, {-25.0, 26.0}}, 
    color = {255, 0, 255}));
  connect(PMSM_DTC.fire_n, inverter.fire_n) 
    annotation(Line(origin = {-5.0000000000000036, 14.999999999999993}, 
    points = {{18.0, 21.0}, {-19.0, 21.0}, {-19.0, 29.0}}, 
    color = {255, 0, 255}));
  connect(currentmeasure.i, PMSM_DTC.i_abc) 
    annotation(Line(origin = {18, 15}, 
    points = {{-37, -15}, {22, -15}, {22, 9}, {17, 9}}, 
    color = {0, 0, 127}));
  connect(PMSM1.flange_a, angularVelecitySensor.flange_a) 
    annotation(Line(origin = {0.0, -34.0}, 
    points = {{-20.0, -18.0}, {0.0, -18.0}, {0.0, -4.0}}, 
    color = {0, 0, 0}));
  connect(PMSM1.flange_a, anglemeasure.flange_a) 
    annotation(Line(origin = {12.0, -34.0}, 
    points = {{-32.0, -18.0}, {6.0, -18.0}, {6.0, -4.0}}, 
    color = {0, 0, 0}));
  connect(PMSM1.flange_a, torquestep.flange) 
    annotation(Line(origin = {16.0, -42.0}, 
    points = {{-36.0, -10.0}, {24.0, -10.0}}, 
    color = {0, 0, 0}));
  annotation(Documentation(info = "<html><p>
该实例为永磁同步电机的一种应用案例，根据PWM信号驱动原理，通过直接转矩控制器来控制逆变器的通断，使电机获得理想的电压输入，并模拟电机的工作特性。
</p>
</html>"), 
    Icon(coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    Diagram(coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    experiment(StartTime = 0, StopTime = 5, Interval = 0.01, Algorithm = Dassl, Tolerance = 0.0001, DoublePrecision = true), 
    Protection(access = Access.nonPackageDuplicate));
  connect(constantvoltage.p, inverter.pSupply) 
    annotation(Line(origin = {-52, 60.99999999999999}, 
    points = {{-16, 5.000000000000007}, {12, 5.000000000000007}, {12, 1.0000000000000142}}, 
    color = {0, 0, 255}));
  connect(inverter.pload, currentmeasure.plug_p) 
    annotation(Line(origin = {-25.000000000000004, 13.999999999999993}, 
    points = {{5.0, 42.0}, {5.0, -4.0}, {-5.0, -4.0}}, 
    color = {0, 0, 255}));
  connect(sine.y, PMSM_DTC.ref) 
    annotation(Line(origin = {50, 30}, 
    points = {{-5, 0}, {-10, 0}, {-10, 6}, {-15, 6}}, 
    color = {0, 0, 127}));
  connect(anglemeasure.phi, PMSM_DTC.theta) 
    annotation(Line(origin = {18, 12}, 
    points = {{-3.552713678800501e-15, -29.0075}, {22, -29.0075}, {22, 18}, {17, 18}}, 
    color = {0, 0, 127}));
  connect(currentmeasure.plug_n, PMSM1.plugSupply) 
    annotation(Line(origin = {-30, -25}, 
    points = {{0, 15}, {0, -14.600000000000001}}, 
    color = {0, 0, 255}));
  connect(constantvoltage.n, inverter.nSupply) 
    annotation(Line(origin = {-52, 50}, 
    points = {{-16, -3.999999999999993}, {-16, -6}, {12, -6}, {12, 7.105427357601002e-15}}, 
    color = {0, 0, 255}));
  connect(ground.p, constantvoltage.n) 
    annotation(Line(origin = {-74, 41}, 
    points = {{6, -9}, {6, 5.000000000000007}}, 
    color = {0, 0, 255}));
end PMSMSystem_DTC;