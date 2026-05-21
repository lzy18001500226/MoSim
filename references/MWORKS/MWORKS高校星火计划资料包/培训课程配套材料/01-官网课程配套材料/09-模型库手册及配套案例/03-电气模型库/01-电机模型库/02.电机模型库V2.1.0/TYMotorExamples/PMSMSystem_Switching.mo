model PMSMSystem_Switching "永磁同步电机示例，开关电路型"
  annotation(Documentation(link = "modelica://TYMotor/Resources/HTML/PMSMSystem_Switching.html"), Protection(access = Access.nonPackageDuplicate));
  extends TYMotor.Utilities.Icons.Common.Example;
  import Modelica.Constants.pi;
  TYMotor.Sensors.AngleSensor anglemeasure 
    annotation(Placement(transformation(origin = {38.0, -20.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
    rotation = -90.0)));
  TYMotor.Sensors.CurrentSensor currentmeasure 
    annotation(Placement(transformation(origin = {-2, -8}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = -90)));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {-75.91, 12}, 
    extent = {{-10, -10}, {10, 10.000000000000004}})));
  TYMotor.Machines.Synchronous.PMSM PMSM1(
    V0 = 112.3, 
    Rs = 1.25, Lssigma = 0.00047, Lmq = 0.00975, Lmd = 0.00975, J_Rotor = 0.05, p = 2, fsNominal = 50,terminalConnection="D") 
    annotation(Placement(transformation(origin = {-12.0, -46.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Ramp ramp(height = 20, duration = 2) 
    annotation(Placement(transformation(origin = {58.0, 23.299999999999986}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.TorqueStep torquestep(



    stepTorque = -0.1, 
    startTime = 0.5, offsetTorque = 0
    ) 
    annotation(Placement(transformation(origin = {68.0, -46.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Converters.IdealSwitching.DCAC.ThreePhase inverter 
    annotation(Placement(transformation(origin = {-28.0, 42.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMotor.Controllers.PMSM.PMSM_FOC1 controller(



    T_PWM = 0.000125, U_dc = 28.6, 
    phi_offset = 0, p = 2, N = 2, kp_i = 5, Ti_i = 0.0001, kp_w = 10, Ti_w = 0.0001, Ti_phi = 0.1, kp_phi = 5, uMax_phi = 1E7, uMin_phi = -1E7
    ) 
    annotation(Placement(transformation(origin = {14.0, 17.299999999999983}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage voltage(V = 48) 
    annotation(Placement(transformation(origin = {-75.91, 42}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
equation
  connect(PMSM1.flange_a, anglemeasure.flange_a) 
    annotation(Line(origin = {-3.0, -36.0}, 
    points = {{4.0, -10.0}, {41.0, -10.0}, {41.0, 6.0}}, 
    color = {0, 0, 0}));
  connect(torquestep.flange, PMSM1.flange_a) 
    annotation(Line(origin = {19.0, -45.0}, 
    points = {{39.0, -1.0}, {-18.0, -1.0}}, 
    color = {0, 0, 0}));
  connect(anglemeasure.phi, controller.phi) 
    annotation(Line(origin = {31.0, 3.0}, 
    points = {{7.0, -12.0}, {7.0, 14.0}, {-6.0, 14.0}}, 
    color = {0, 0, 127}));
  connect(controller.fire_p, inverter.fire_p) 
    annotation(Line(origin = {8.0, 23.0}, 
    points = {{-5.0, 0.0}, {-42.0, 0.0}, {-42.0, 7.0}}, 
    color = {255, 0, 255}));
  connect(controller.fire_n, inverter.fire_n) 
    annotation(Line(origin = {14.0, 25.0}, 
    points = {{-11.0, -14.0}, {-36.0, -14.0}, {-36.0, 5.0}}, 
    color = {255, 0, 255}));
  connect(controller.ref, ramp.y) 
    annotation(Line(origin = {54.0, 11.0}, 
    points = {{-29.0, 12.0}, {-7.0, 12.0}}, 
    color = {0, 0, 127}));
  connect(inverter.pload, currentmeasure.plug_p) 
    annotation(Line(origin = {-8, 16}, 
    points = {{-10, 26}, {-3.8610000000000007, 26}, {-3.8610000000000007, -20.009999999999998}}, 
    color = {0, 0, 255}));
  connect(voltage.n, inverter.nSupply) 
    annotation(Line(origin = {-38, 27.999999999999993}, 
    points = {{-37.91, 4.000000000000007}, {-37.91, 7.105427357601002e-15}, {0, 7.105427357601002e-15}, {0, 8.000000000000007}}, 
    color = {0, 0, 255}));
  annotation(Documentation(info = "<html><p>
该实例为永磁同步电机的一种应用案例，在特定输入电压下，通过PWM信号驱动的磁场定向控制器来控制逆变器的通断，使电机获得理想的电压输入，并模拟电机的工作特性。
</p>
</html>"), 
    Icon(graphics, 
    coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    Diagram(graphics, 
    coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    experiment(StartTime = 0, StopTime = 3, Interval = 1e-05, Algorithm = Dassl, Tolerance = 0.0001, DoublePrecision = true), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.06667, ContinueTimeVector), ResultViewerManager(resultViewers = {
    ResultViewer(name = "1", executeTrigger = executeTrigger.SimulationFinished, commands = {
    CreatePlot(id = 1, position = [0, 28, 739, 767], y = ["ramp.y", "PMSM1.w"], x_display_unit = "s", y_display_units = ["", "rad/s"], y_axis = [1, 1], legend_layout = 1, legend_frame = True, left_title_type = 2, left_title = "转速[rad/s]", bottom_title_type = 2, bottom_title = "时间/s", fix_time_range_value = 6.95255e-310)})
    })));
  connect(PMSM1.plugSupply, currentmeasure.plug_n) 
    annotation(Line(origin = {-12, -28}, 
    points = {{0, -5.200000000000003}, {0, 15.9}, {0.14999999999999858, 15.9}}, 
    color = {0, 0, 255}));
  connect(currentmeasure.y, controller.i_f) 
    annotation(Line(origin = {20, 2}, 
    points = {{-11.04, -10.0453}, {12, -10.0453}, {12, 9.299999999999983}, {5, 9.299999999999983}}, 
    color = {0, 0, 127}));
  connect(voltage.p, inverter.pSupply) 
    annotation(Line(origin = {-47, 43}, 
    points = {{-28.909999999999997, 9}, {-28.909999999999997, 13}, {9, 13}, {9, 5}}, 
    color = {0, 0, 255}));
  connect(ground.p, voltage.n) 
    annotation(Line(origin = {-66, 30}, 
    points = {{-9.909999999999997, -8}, {-9.909999999999997, 2}}, 
    color = {0, 0, 255}));
end PMSMSystem_Switching;