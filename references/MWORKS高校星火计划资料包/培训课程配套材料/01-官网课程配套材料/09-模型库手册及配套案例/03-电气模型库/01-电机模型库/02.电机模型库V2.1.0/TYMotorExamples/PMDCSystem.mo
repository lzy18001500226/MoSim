model PMDCSystem "永磁直流电机示例"
  annotation(Documentation(link = "modelica://TYMotor/Resources/HTML/PMDCSystem.html"), Protection(access = Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 739, 767], y=["ramp.y", "PMDC1.w"], x_display_unit="s", y_display_units=["", "rad/s"], y_axis=[1, 1], legend_layout=1, legend_frame=True, left_title_type=2, left_title="转速[rad/s]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=6.95255e-310)})
})));
  extends TYMotor.Utilities.Icons.Common.Example;
  Modelica.Mechanics.Rotational.Sources.TorqueStep torquestep(stepTorque = -10, 
    startTime = 1.5) 
    annotation(Placement(transformation(origin = {64.0, -36.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation(Placement(transformation(origin = {-52.0, 7.996999999999998}, 
    extent = {{-10.0, -9.997}, {10.000000000000007, 9.997}})));
  TYMotor.Sensors.CurrentSensor1ph currentsensor 
    annotation(Placement(transformation(origin = {-8, 1}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = -270)));
  TYMotor.Machines.DCMachines.PMDC PMDC1 
    annotation(Placement(transformation(origin = {-14.0, -36.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMotor.Converters.PowerBalance.DCDC.Ideal dcdc(
    VDC = 200, INominal = 10) 
    annotation(Placement(transformation(origin = {-14.0, 38.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V = 48) 
    annotation(Placement(transformation(origin = {-52.0, 38.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = -90.0)));
  TYMotor.Sensors.AngleSensor angleSensor 
    annotation(Placement(transformation(origin = {46.0, 4.0}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
    rotation = -270.0)));
  Modelica.Blocks.Sources.Ramp ramp(height = 70, duration = 5) 
    annotation(Placement(transformation(origin = {64.00000000000001, 44.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMotor.Controllers.PMDC.PMDC_Controller controller(
    N = 2, kp_phi = 10, Ti_phi = 0.1, Td_phi = 0.1, kp_w = 30, Ti_w = 0.1, Td_w = 0.1, Ti_i = 0.1, Td_i = 0.1, kp_i = 30) 
    annotation(Placement(transformation(origin = {18.0, 38.0}, 
    extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Electrical.Analog.Basic.Ground ground1 
    annotation(Placement(transformation(origin = {-51.99999999999999, -36.003}, 
    extent = {{-10.0, -9.997}, {10.000000000000007, 9.997}})));
equation
  connect(PMDC1.pin_ap, currentsensor.n) 
    annotation(Line(origin = {4, 61}, 
    points = {{-14, -85}, {-12, -85}, {-12, -70}}, 
    color = {0, 0, 255}));
  connect(dcdc.pLoad, currentsensor.p) 
    annotation(Line(origin = {-7, 56}, 
    points = {{-1, -28}, {-1, -45}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.n, dcdc.nSupply) 
    annotation(Line(origin = {-44.0, 74.0}, 
    points = {{-8.0, -46.0}, {-8.0, -48.0}, {20.0, -48.0}, {20.0, -42.0}}, 
    color = {0, 0, 255}));
  connect(constantVoltage.p, dcdc.pSupply) 
    annotation(Line(origin = {-51.0, 33.0}, 
    points = {{-1.0, 15.0}, {27.0, 15.0}, {27.0, 11.0}}, 
    color = {0, 0, 255}));
  connect(angleSensor.flange_a, PMDC1.flange_a) 
    annotation(Line(origin = {-2.0, 8.0}, 
    points = {{48.0, -14.0}, {48.0, -44.0}, {1.0, -44.0}}, 
    color = {0, 0, 0}));
  connect(PMDC1.flange_a, torquestep.flange) 
    annotation(Line(origin = {35.0, 19.0}, 
    points = {{-36.0, -55.0}, {19.0, -55.0}}, 
    color = {0, 0, 0}));
  connect(constantVoltage.n, ground.p) 
    annotation(Line(origin = {-43.0, 35.0}, 
    points = {{-9.0, -7.0}, {-9.0, -17.0}}, 
    color = {0, 0, 255}));
  connect(angleSensor.phi, controller.phi) 
    annotation(Line(origin = {29.0, -2.0}, 
    points = {{17.0, 17.0}, {17.0, 40.0}, {0.0, 40.0}}, 
    color = {0, 0, 127}));
  connect(currentsensor.i, controller.i) 
    annotation(Line(origin = {25, 7}, 
    points = {{-22, -6}, {10, -6}, {10, 25}, {4, 25}}, 
    color = {0, 0, 127}));
  connect(controller.ref, ramp.y) 
    annotation(Line(origin = {47.0, 36.0}, 
    points = {{-18.0, 8.0}, {6.0, 8.0}}, 
    color = {0, 0, 127}));
  connect(controller.y, dcdc.vRef) 
    annotation(Line(origin = {11.0, 36.0}, 
    points = {{-4.0, 2.0}, {-15.0, 2.0}}, 
    color = {0, 0, 127}));
  connect(dcdc.nLoad, PMDC1.pin_an) 
    annotation(Line(origin = {-20.0, 1.0}, 
    points = {{0.0, 27.0}, {0.0, -25.0}, {2.0, -25.0}}, 
    color = {0, 0, 255}));
  connect(ground1.p, PMDC1.pin_an) 
    annotation(Line(origin = {-31, -23.000000000000007}, 
    points = {{-20.999999999999986, -3.005999999999993}, {-20.999999999999986, -0.9999999999999929}, {13, -0.9999999999999929}}, 
    color = {0, 0, 255}));
  annotation(Icon(graphics, 
    coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    Diagram(graphics, 
    coordinateSystem(preserveAspectRatio = true, 
    extent = {{-100, -100}, {100, 100}})), 
    Documentation(info = "<html><p>
该案例可以模拟永磁直流电机在特性工况下的工作特性，控制器默认为转速控制模式，通过左侧恒定电压源提供输入电压，右侧ramp组件设置控制器转速控制基准。
</p>
</html>"), 
    experiment(StartTime = 0, StopTime = 10, Interval = 0.01, Algorithm = Dassl, Tolerance = 0.0001, DoublePrecision = true, StoreEventValue = true, IntegratorStep = -1));
end PMDCSystem;