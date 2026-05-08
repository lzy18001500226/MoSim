model SynchronousBuck "同步降压电路"
  parameter Modelica.SIunits.Frequency f = 50e3 "MOSFET信号频率";
  parameter Real D = 0.5 "占空比";
  parameter Modelica.SIunits.Voltage Vth = 2 "阈值电压";
  parameter Modelica.SIunits.Resistance R1 = 5 "MOSFET1输入电阻";
  parameter Modelica.SIunits.Resistance R2 = 20 "MOSFET2输入电阻";
  parameter Modelica.SIunits.Capacitance Cgd = 80e-12 "MOSFET的gd间电容";
  parameter Modelica.SIunits.Capacitance Cgs = 270e-12 "MOSFET的gs间电容";
  TYElectrical.BasicComponents.IdealElectricSource.DCVoltageSource dCVoltageSource(v0 = 30) 
    annotation (Placement(transformation(origin = {-202.99999999999997, 33.0}, 
      extent = {{17.0, -17.0}, {-17.0, 17.0}}, 
      rotation = -270.0)));
  TYElectrical.Semiconductors.NchannelMOSFET MOSFET1(ParamMode = 1, Rd = 0.01, Rs = 0.01, 
    Coss = 100e-12, C_param = 2, Cds = 1e-12, 
    Rds_on = 0.1, Vgs_on = 15, vth = Vth) 
    annotation (Placement(transformation(origin = {-128.0474576271185, 101.99999999999993}, 
      extent = {{-18.000000000000057, -18.0}, {17.999999999999943, 18.0}}, 
      rotation = 90.0)));
  TYElectrical.Semiconductors.HalfBridgeDriver halfBridgeDriver(ModelingOption = "电接口输入", Mode = "给定输出电阻", Ron = 100, Roff = 10) 
    annotation (Placement(transformation(origin = {-111.04745762711855, -18.00000000000012}, 
      extent = {{-18.0, -18.0}, {18.0, 18.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference gound 
    annotation (Placement(transformation(origin = {-203.0806779661017, -141.00000000000009}, 
      extent = {{-12.999999999999943, -12.999999999999993}, {13.0, 13.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference GND1 
    annotation (Placement(transformation(origin = {-177.99999999999983, -80.00000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (Diagram(coordinateSystem(extent = {{-310.0, -200.0}, {290.0, 200.0}}, 
    grid = {2.0, 2.0})), 
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={-3.55271e-15,37}, 
lineColor={85,0,255}, 
fillColor={85,0,255}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={3.55271e-15,-8}, 
points={{-62,18},{0,-18},{62,18}}, 
color={85,0,255}, 
thickness=5), Line(origin={1.06581e-14,-36}, 
points={{-62,18},{0,-18},{62,18}}, 
color={85,0,255}, 
thickness=5)}), 
    experiment(Algorithm=Dassl,Interval=1e-06,StartTime=0,StopTime=0.006,Tolerance=1e-05), 
    Documentation(link="modelica://TYElectrical/Resources/Example/SynchronousBuck.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.006,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["dCVoltageSource.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310), 
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["R4.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310, sub_plot=[2, 1])})
})));
  TYElectrical.Semiconductors.Diode diode(Model = 1, I_curve = {0.25, 5}, V_curve = {0.7, 0.8}, Cj = 100e-12) 
    annotation (Placement(transformation(origin = {-127.0474576271184, 148.9999999999999}, 
      extent = {{16.999999999999943, -16.999999999999957}, {-17.0, 16.999999999999915}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor r1(R = R1) 
    annotation (Placement(transformation(origin = {-72.54745762711863, 31.499999999999943}, 
      extent = {{-15.499999999999943, -15.499999999999773}, {15.499999999999943, 15.500000000000114}}, 
      rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor r2(R = R2) 
    annotation (Placement(transformation(origin = {-52.047457627118575, -46.320000000000064}, 
      extent = {{-15.0, -15.0}, {15.0, 15.0}}, 
      rotation = 360.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C1(C = Cgs * 2) 
    annotation (Placement(transformation(origin = {-16.047457627118604, -71.00000000000013}, 
      extent = {{-15.0, -15.0}, {15.0, 15.0}}, 
      rotation = 270.0)));
  TYElectrical.Semiconductors.Diode diode1(Model = 1, I_curve = {0.25, 5}, V_curve = {0.7, 0.8}, Cj = 100e-12) 
    annotation (Placement(transformation(origin = {73.9525423728816, -47.248813559322215}, 
      extent = {{16.999999999999943, -16.999999999999957}, {-17.0, 16.999999999999915}}, 
      rotation = 270.0)));
  TYElectrical.Semiconductors.NchannelMOSFET MOSFET2(ParamMode = 1, Rd = 0.01, Rs = 0.01, 
    Coss = 100e-12, C_param = 2, Cds = 1e-12, 
    Rds_on = 0.1, Vgs_on = 15, vth = Vth, 
    Cgs = Cgs, Cgd = Cgd) 
    annotation (Placement(transformation(origin = {22.952542372881368, -46.24881355932218}, 
      extent = {{-18.000000000000057, -18.0}, {17.999999999999943, 18.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor L(L = 1e-3) 
    annotation (Placement(transformation(origin = {102.95254237288145, 119.99999999999987}, 
      extent = {{15.0, -14.999999999999986}, {-15.000000000000014, 15.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R3(R = 10e3) 
    annotation (Placement(transformation(origin = {102.95254237288137, 81.9999999999999}, 
      extent = {{15.0, -15.0}, {-15.0, 15.0}}, 
      rotation = -360.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C2(C(displayUnit = "uF") = 2.2e-5) 
    annotation (Placement(transformation(origin = {151.95254237288145, 7.999999999999897}, 
      extent = {{-15.0, -15.0}, {15.0, 15.0}}, 
      rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R4(R = 3.75) 
    annotation (Placement(transformation(origin = {196.95254237288145, 7.999999999999897}, 
      extent = {{-15.0, -15.0}, {15.0, 15.0}}, 
      rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference GND2 
    annotation (Placement(transformation(origin = {-92.04745762711843, -80.00000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.Sources.VoltageSources.PulseVoltageGenerator pulseVoltageGenerator(v_2 = 5, TR = 0, TF = 0, PER = 1 / f, PW = D * 100) 
    annotation (Placement(transformation(origin = {-178.04745762711846, -18.00000000000012}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 270.0)));
equation
  connect(gound.p, dCVoltageSource.n) 
    annotation (Line(origin = {-199.04745762711855, -17.000000000000107}, 
      points = {{-4.0, -111.0}, {-4.0, 33.0}}, 
      color = {0, 0, 255}));
  connect(r2.p, halfBridgeDriver.LO) 
    annotation (Line(origin = {-82.04745762711855, -46.000000000000114}, 
      points = {{15.0, 0.0}, {15.0, 24.0}, {-11.0, 24.0}}, 
      color = {0, 0, 255}));
  connect(r1.p, MOSFET1.G) 
    annotation (Line(origin = {-129.04745762711855, 64.99999999999989}, 
      points = {{56.0, -18.0}, {56.0, 19.0}, {1.0, 19.0}}, 
      color = {0, 0, 255}));
  connect(r1.n, halfBridgeDriver.HO) 
    annotation (Line(origin = {-85.04745762711855, -5.000000000000107}, 
      points = {{13.0, 21.0}, {13.0, 2.0}, {-8.0, 2.0}}, 
      color = {0, 0, 255}));
  connect(diode1.A, dCVoltageSource.n) 
    annotation (Line(origin = {-64.04745762711855, -46.000000000000114}, 
      points = {{138.0, -18.0}, {138.0, -64.0}, {-139.0, -64.0}, {-139.0, 62.0}}, 
      color = {0, 0, 255}));
  connect(MOSFET2.S, dCVoltageSource.n) 
    annotation (Line(origin = {-64.04745762711855, -46.000000000000114}, 
      points = {{105.0, -11.0}, {105.0, -39.0}, {138.0, -39.0}, {138.0, -64.0}, {-139.0, -64.0}, {-139.0, 62.0}}, 
      color = {0, 0, 255}));
  connect(C2.n, dCVoltageSource.n) 
    annotation (Line(origin = {-25.047457627118547, -46.000000000000114}, 
      points = {{177.0, 39.0}, {177.0, -64.0}, {-178.0, -64.0}, {-178.0, 62.0}}, 
      color = {0, 0, 255}));
  connect(C1.n, dCVoltageSource.n) 
    annotation (Line(origin = {-109.04745762711855, -47.000000000000114}, 
      points = {{93.0, -39.0}, {93.0, -63.0}, {-94.0, -63.0}, {-94.0, 63.0}}, 
      color = {0, 0, 255}));
  connect(R4.n, dCVoltageSource.n) 
    annotation (Line(origin = {-3.047457627118547, -47.000000000000114}, 
      points = {{200.0, 40.0}, {200.0, -63.0}, {-200.0, -63.0}, {-200.0, 63.0}}, 
      color = {0, 0, 255}));
  connect(GND2.p, halfBridgeDriver.LS) 
    annotation (Line(origin = {-93.04745762711855, -54.000000000000114}, 
      points = {{1.0, -16.0}, {1.0, 21.0}, {0.0, 21.0}}, 
      color = {0, 0, 255}));
  connect(pulseVoltageGenerator.p, halfBridgeDriver.PWM) 
    annotation (Line(origin = {-144.04745762711855, -5.000000000000107}, 
      points = {{-34.0, -3.0}, {15.0, -3.0}, {15.0, -2.0}}, 
      color = {0, 0, 255}));
  connect(pulseVoltageGenerator.n, halfBridgeDriver.REF) 
    annotation (Line(origin = {-145.04745762711855, -32.00000000000012}, 
      points = {{-33.0, 4.0}, {16.0, 4.0}, {16.0, 3.0}}, 
      color = {0, 0, 255}));
  connect(GND1.p, pulseVoltageGenerator.n) 
    annotation (Line(origin = {-153.04745762711843, -52.000000000000114}, 
      points = {{-25.0, -18.0}, {-25.0, 24.0}}, 
      color = {0, 0, 255}));
  connect(R4.p, L.p) 
    annotation (Line(origin = {157.95254237288157, 71.99999999999989}, 
      points = {{39.0, -49.0}, {39.0, 48.0}, {-40.0, 48.0}}, 
      color = {0, 0, 255}));
  connect(C2.p, L.p) 
    annotation (Line(origin = {134.95254237288157, 71.99999999999989}, 
      points = {{17.0, -49.0}, {17.0, 48.0}, {-17.0, 48.0}}, 
      color = {0, 0, 255}));
  connect(R3.n, L.n) 
    annotation (Line(origin = {87.95254237288157, 100.99999999999989}, 
      points = {{0.0, -19.0}, {0.0, 19.0}}, 
      color = {0, 0, 255}));
  connect(R3.p, L.p) 
    annotation (Line(origin = {117.95254237288157, 100.99999999999989}, 
      points = {{0.0, -19.0}, {0.0, 19.0}}, 
      color = {0, 0, 255}));
  connect(diode.K, MOSFET1.D) 
    annotation (Line(origin = {-149.0, 135.0}, 
      points = {{5.0, 14.0}, {-11.0, 14.0}, {-11.0, -15.0}, {10.0, -15.0}}, 
      color = {0, 0, 255}));
  connect(dCVoltageSource.p, MOSFET1.D) 
    annotation (Line(origin = {-171.0, 85.0}, 
      points = {{-32.0, -35.0}, {-32.0, 35.0}, {32.0, 35.0}}, 
      color = {0, 0, 255}));
  connect(diode.A, MOSFET1.S) 
    annotation (Line(origin = {-106.0, 135.0}, 
      points = {{-4.0, 14.0}, {10.0, 14.0}, {10.0, -15.0}, {-11.0, -15.0}}, 
      color = {0, 0, 255}));
  connect(r2.n, MOSFET2.G) 
    annotation (Line(origin = {-16.0, -46.0}, 
      points = {{-21.0, 0.0}, {21.0, 0.0}}, 
      color = {0, 0, 255}));
  connect(C1.p, MOSFET2.G) 
    annotation (Line(origin = {-5.0, -51.0}, 
      points = {{-11.0, -5.0}, {-11.0, 5.0}, {10.0, 5.0}}, 
      color = {0, 0, 255}));
  connect(MOSFET2.D, halfBridgeDriver.HS) 
    annotation (Line(origin = {-26.0, -24.0}, 
      points = {{67.0, -12.0}, {67.0, 11.0}, {-67.0, 11.0}}, 
      color = {0, 0, 255}));
  connect(diode1.K, MOSFET2.D) 
    annotation (Line(origin = {58.0, -32.0}, 
      points = {{16.0, 2.0}, {16.0, 60.0}, {-17.0, 60.0}, {-17.0, -4.0}}, 
      color = {0, 0, 255}));
  connect(L.n, MOSFET1.S) 
    annotation (Line(origin = {-14.0, 120.0}, 
      points = {{102.0, 0.0}, {-103.0, 0.0}}, 
      color = {0, 0, 255}));
  connect(MOSFET2.D, MOSFET1.S) 
    annotation (Line(origin = {-38.0, 42.0}, 
      points = {{79.0, -78.0}, {79.0, 78.0}, {-79.0, 78.0}}, 
      color = {0, 0, 255}));
end SynchronousBuck;