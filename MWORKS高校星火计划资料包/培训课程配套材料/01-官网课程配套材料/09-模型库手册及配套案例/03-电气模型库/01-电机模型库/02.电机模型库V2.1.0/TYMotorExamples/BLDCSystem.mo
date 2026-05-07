model BLDCSystem "无刷直流电机示例"
  annotation(Documentation(link = "modelica://TYMotor/Resources/HTML/BLDCSystem.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 739, 767], y=["bldc.w", "agVelocityCommand.y"], x_display_unit="s", y_display_units=["rad/s", ""], y_axis=[1, 1], legend_layout=1, legend_frame=True, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=6.95255e-310)})
})));
  extends TYMotor.Utilities.Icons.Common.Example;
  //------------------ 电源参数 ------------------//
  parameter Modelica.Units.SI.Voltage V = 28.6 "供电电压" 
    annotation(Dialog(tab = "电源参数"));
  //------------------ 电机参数 ------------------//
  parameter Modelica.Units.SI.Inertia J_Rotor = 0.0125 "转子转动惯量" 
    annotation(Dialog(tab = "电机参数"));
  parameter Integer p = 8 "极对数" 
    annotation(Dialog(tab = "电机参数"));
  parameter Integer m = 3 "相数" 
    annotation(Dialog(tab = "电机参数"));
  parameter Real k(unit = "V.s/rad") = 0.382 "反电势系数" 
    annotation(Dialog(tab = "电机参数"));
  parameter Modelica.Units.SI.Inductance L = 0.00095 "每相绕组自感" 
    annotation(Dialog(tab = "电机参数", group = "电阻及电感"));
  parameter Modelica.Units.SI.Inductance M = 6.7e-7 "相绕组之间互感" 
    annotation(Dialog(tab = "电机参数", group = "电阻及电感"));
  parameter Modelica.Units.SI.Resistance Rs = 2 "相电阻" 
    annotation(Dialog(tab = "电机参数", group = "电阻及电感"));
  //------------------ DCDC转换器 ------------------//
  parameter Modelica.Units.SI.Current IConverterMax = 100 "最大直流供电电流" 
    annotation(Dialog(tab = "DCDC转换器"));
  parameter Modelica.Units.SI.Resistance RonSwitch = 1e-5 "开关关断电阻" 
    annotation(Dialog(tab = "DCDC转换器", group = "理想电子开关"));
  parameter Modelica.Units.SI.Conductance GoffSwitch = 1e-5 "开关开通电导" 
    annotation(Dialog(tab = "DCDC转换器", group = "理想电子开关"));
  parameter Modelica.Units.SI.Resistance RonDiode = 1e-5 "二极管关断电阻" 
    annotation(Dialog(tab = "DCDC转换器", group = "理想二极管"));
  parameter Modelica.Units.SI.Conductance GoffDiode = 1e-5 "二极管开通电导" 
    annotation(Dialog(tab = "DCDC转换器", group = "理想二极管"));
  parameter Modelica.Units.SI.Voltage VkneeDiode = 0 "门限电压" 
    annotation(Dialog(tab = "DCDC转换器", group = "理想二极管"));
  //------------------ 控制器参数 ------------------//
  parameter Modelica.Units.SI.Frequency f = 10000 "PWM波的频率" 
    annotation(Dialog(tab = "控制器参数"));
  parameter Real kp_w = 10 "比例系数" 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  parameter Real ki_w = 30 "积分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "速度环参数"));
  parameter Real kp_i = 10 "比例系数" 
    annotation(Dialog(tab = "控制器参数", group = "电流环参数"));
  parameter Real ki_i = 100 "积分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "电流环参数"));
  parameter Real kd_i = 0 "微分时间常数" 
    annotation(Dialog(tab = "控制器参数", group = "电流环参数"));
  //------------------ 输出参数 ------------------//
  output Modelica.Units.SI.Voltage Uab = bldc.vs[1] - bldc.vs[2] "线电压Uab";
  output Modelica.Units.SI.Voltage Ua = bldc.vs[1] "相电压Ua";
  output Modelica.Units.SI.Current ia = bldc.is[1] "相电流ia";
  // output Modelica.SIunits.Torque Te = bldcm.rotor_bldc.tau_electrical "电磁转矩";
  // output Modelica.SIunits.Conversions.NonSIunits.AngularVelocity_rpm rpm_mechanical = bldcm.rotor_bldc.w * 30 / Modelica.Constants.pi "机械转速";
  TYMotor.Sensors.HallSensor hall(useSupport = false, 
    p = p, 
    shift = 0) 
    annotation(Placement(transformation(origin = {30.0, -40.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 90.0)));
  Modelica.Mechanics.Rotational.Sources.Torque torque 
    annotation(Placement(transformation(origin = {49.63, -60.02000000000001}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Controllers.BLDC.BLDCController BLDCController(f = 10000, 
    kp_i = kp_i, 
    dir(delta_w = 0), 
    kp_w = kp_w, 
    ki_i = ki_i, ki_w = ki_w, 
    uMax_i = 10, 
    limiter2(uMax 
    = 30, 
    uMin 
    = -30), 
    limiter(uMax 
    = 10, 
    uMin 
    = -10), 
    gain2(k = 1 / 10), 
    pulsewidth(f = 10000), 
    PI(k = 10, T = 15), PI2(k = 10, T = 6)) annotation(Placement(transformation(origin = {29.96, 10.997642456828599}, 
    extent = {{9.96, -10.05}, {-9.96, 10.05}})));
  TYMotor.Sensors.AngularVelecitySensor speedsensor 
    annotation(Placement(transformation(origin = {2, -28.000000000000004}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {-90.0, -4.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Step step(
    offset = 0, 
    startTime = 0.2, 
    height = -0.2) 
    annotation(Placement(transformation(origin = {80.0, -60.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 180.0)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentsensor1 
    annotation(Placement(transformation(origin = {-66.0, 39.999999999999986}, 
    extent = {{-9.999, -9.999}, {9.999, 9.999}}, 
    rotation = -180.0)));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantvoltage(V = 28.6) 
    annotation(Placement(transformation(extent = {{-10, -10}, {10, 10}}, rotation = 270, origin = {-90, 30})));
  TYMotor.Controllers.Basic.AgVelocityCommand agVelocityCommand(g = 3000, starttime = 2, offset2 = 1000, amplitude = 60, 
    offset1 = 500, 
    freqHz = 1, 
    N = 1, offset = 600) 
    annotation(Placement(transformation(origin = {68, 13.637644143171405}, 
    extent = {{10, -10}, {-10, 10}})));
  TYMotor.Machines.DCMachines.BLDC bldc(J_Rotor = J_Rotor, M = M, L = L, Rs = Rs, p = p, k = k) 
    annotation(Placement(transformation(origin = {-40.0, -60.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMotor.Converters.IdealSwitching.DCAC.ThreePhase inverter(RonTransistor = 1e-3, RonDiode = 1e-03) 
    annotation(Placement(transformation(origin = {-32.0, 34.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(hall.y[:], BLDCController.Hall[:]) 
    annotation(
    Line(origin = {30, -24}, 
    points = {{0, -6}, {0, 6}, {20, 6}, {20, 27.560642456828596}, {10.975760000000008, 27.560642456828596}}, 
    color = {255, 0, 255}));
  connect(speedsensor.w, BLDCController.w) 
    annotation(
    Line(origin = {20, -21.5}, 
    points = {{-17.9982, 4.495000000000001}, {-17.9982, 81.5}, {30, 81.5}, {30, 30.0962366}, {20.947872000000004, 30.0962366}}, 
    color = {0, 0, 127}));
  connect(ground.p, constantvoltage.n) 
    annotation(Line(origin = {-90.0, 10.0}, 
    points = {{0.0, -4.0}, {0.0, 10.0}}));
  connect(torque.tau, step.y) 
    annotation(Line(origin = {71.0, -60.0}, 
    points = {{-9.0, 0.0}, {-2.0, 0.0}}, 
    color = {0, 0, 127}));
  connect(BLDCController.w_ref, agVelocityCommand.y) 
    annotation(Line(origin = {51, 30}, 
    points = {{-10.054119999999998, -16.3413558568286}, {5.992000000000004, -16.3413558568286}, {5.992000000000004, -16.341355856828592}}, 
    color = {0, 0, 127}));
  connect(speedsensor.flange_a, torque.flange) 
    annotation(Line(origin = {20, -55}, 
    points = {{-18, 17}, {-18, -5.02000000000001}, {19.630000000000003, -5.02000000000001}}, 
    color = {0, 0, 0}));
  connect(hall.flange, torque.flange) 
    annotation(Line(origin = {35.0, -55.0}, 
    points = {{-5.0, 5.0}, {-5.0, -5.0}, {5.0, -5.0}}, 
    color = {0, 0, 0}));
  connect(bldc.flange_a, torque.flange) 
    annotation(Line(origin = {6.0, -63.0}, 
    points = {{-36.0, 3.0}, {34.0, 3.0}}, 
    color = {0, 0, 0}));
  annotation(experiment(StartTime = 0, StopTime = 5, Algorithm = Dassl, Tolerance = 0.0001, DoublePrecision = true, StoreEventValue = true, Interval = 1e-05, IntegratorStep = -1), 
    Protection(access = Access.nonPackageDuplicate), Documentation(info = "<html><p>
该实例为无刷直流电机的一种应用案例，利用控制器使得电机可以获得理想的，并与输出转矩对应的电压矢量，在此种模式下，模拟无刷直流电机工作时的输出特性。
</p>
</html>"));
  connect(constantvoltage.p, currentsensor1.n) 
    annotation(Line(origin = {-82.0, 45.0}, 
    points = {{-8.0, -5.0}, {6.0, -5.0}}, 
    color = {0, 0, 255}));
  connect(currentsensor1.i, BLDCController.i_bus) 
    annotation(Line(origin = {-21, 48}, 
    points = {{-45, 2.998899999999985}, {-45, 12}, {71, 12}, {71, -29.288998313657196}, {61.957831999999996, -29.288998313657196}}, 
    color = {0, 0, 127}));
  connect(BLDCController.fire_n, inverter.fire_n) 
    annotation(Line(origin = {-3, 20}, 
    points = {{22.004, -5.384357543171403}, {-23, -5.384357543171403}, {-23, 2}}, 
    color = {255, 0, 255}));
  connect(BLDCController.fire_p, inverter.fire_p) 
    annotation(Line(origin = {-9, 17}, 
    points = {{28.004, -10.344522239788878}, {-29, -10.344522239788878}, {-29, 5}}, 
    color = {255, 0, 255}));
  connect(currentsensor1.p, inverter.pSupply) 
    annotation(Line(origin = {-49, 40}, 
    points = {{-7.000999999999998, -1.4210854715202004e-14}, {7, -1.4210854715202004e-14}, {7, 0}}, 
    color = {0, 0, 255}));
  connect(constantvoltage.n, inverter.nSupply) 
    annotation(Line(origin = {-66, 23}, 
    points = {{-24, -3}, {-24, -5}, {24, -5}, {24, 5}}, 
    color = {0, 0, 255}));
  connect(inverter.pload, bldc.plugSupply) 
    annotation(Line(origin = {-24, -8}, 
    points = {{2, 42}, {16, 42}, {16, -6}, {-15.799999999999997, -6}, {-15.799999999999997, -42}}, 
    color = {0, 0, 255}));
end BLDCSystem;