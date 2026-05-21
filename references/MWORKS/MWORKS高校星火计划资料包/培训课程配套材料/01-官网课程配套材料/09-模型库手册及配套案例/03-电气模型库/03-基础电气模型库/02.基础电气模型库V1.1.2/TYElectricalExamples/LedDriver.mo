model LedDriver "led驱动电路"
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {85, 0, 255}, 
    fillColor = {85, 0, 255}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {85, 0, 255}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {85, 0, 255}, 
    thickness = 5.0)}), 
    Diagram(coordinateSystem(extent = {{-140.0, -124.0}, {140.0, 102.0}}, 
    grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYElectrical/Resources/Example/LedDriver.html"), Protection(access = Access.nonPackageDuplicate), experiment(Algorithm=Dassl,Interval=0.01,StartTime=0,StopTime=10,Tolerance=0.0001,InlineIntegrator=false,InlineStepSize=false), __MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=10,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[V]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-10, 50)), 
Plot(y=["piecewiseLinearVoltageSource.v"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[A]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-0.05, 0.25)), 
Plot(y=["currentSensor.i"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, bottom_title_type=2, right_title_type=2, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 10), zoom_y_l=(-0.05, 0.3)), 
Plot(y=["add3_1.y"], colors=["4278190335"])})
})));
  TYElectrical.Sources.VoltageSources.PiecewiseLinearVoltageSource piecewiseLinearVoltageSource(table = {{0, 0}, {10, 40}}, smoothness = Modelica.Blocks.Types.Smoothness.LinearSegments, extrapolation = Modelica.Blocks.Types.Extrapolation.LastTwoPoints) 
    annotation(Placement(transformation(origin = {-96.06169491525418, -10.999999999999998}, 
    extent = {{-13.000000000000004, -13.0}, {12.999999999999993, 13.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference gound1 
    annotation(Placement(transformation(origin = {-95.99999999999994, -105.00000000000004}, 
    extent = {{-12.999999999999943, -12.999999999999993}, {13.0, 13.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R1(R = 16000) 
    annotation(Placement(transformation(origin = {-69.95254237288134, -68.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R2(R = 1.7) 
    annotation(Placement(transformation(origin = {-39.99999999999999, 72.00000000000003}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 360.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R3(R = 1100) 
    annotation(Placement(transformation(origin = {-23.99999999999998, -30.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R4(R = 85) 
    annotation(Placement(transformation(origin = {-23.952542372881343, -70.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference gound2 
    annotation(Placement(transformation(origin = {-69.95254237288134, -105.00000000000004}, 
    extent = {{-12.999999999999943, -12.999999999999993}, {13.0, 13.0}})));
  TYElectrical.Semiconductors.Diode D1(Model = 1, 
    Main = 1, BV = 70) annotation(Placement(transformation(origin = {-69.99999999999999, 40.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.Semiconductors.Diode D2(Model = 1, 
    Main = 1) 
    annotation(Placement(transformation(origin = {-69.99999999999999, 13.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.Semiconductors.NPNBipolarTransistor nPNBipolarTransistor(Initial_eqution = 2) 
    annotation(Placement(transformation(origin = {10.000000000000014, -46.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.Semiconductors.PNPBipolarTransistor pNPBipolarTransistor(Initial_eqution = 2) 
    annotation(Placement(transformation(origin = {-39.99999999999999, -8.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.BasicComponents.IdealSensors.CurrentSensor currentSensor 
    annotation(Placement(transformation(origin = {18.000000000000014, 72.00000000000003}, 
    extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYElectrical.EncodersAndTransducers.LightEmittingDiode LED1(
    P_o = 0.4, 
    IS = 5e-7, 
    Diode_Type = 1) 
    annotation(Placement(transformation(origin = {50.000000000000036, 54.00000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.EncodersAndTransducers.LightEmittingDiode LED2(
    P_o = 0.4, 
    IS = 5e-7, 
    Diode_Type = 1) 
    annotation(Placement(transformation(origin = {50.000000000000036, 15.000000000000014}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.EncodersAndTransducers.LightEmittingDiode LED3(
    P_o = 0.4, 
    IS = 5e-7, 
    Diode_Type = 1) 
    annotation(Placement(transformation(origin = {50.000000000000036, -24.000000000000007}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  Modelica.Blocks.Math.Add3 add3_1 
    annotation(Placement(transformation(origin = {88.00000000000003, 25.999999999999986}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(piecewiseLinearVoltageSource.n, gound1.p) 
    annotation(Line(origin = {-95.99999999999999, -13.0}, 
    points = {{0.0, -11.0}, {0.0, -79.0}}, 
    color = {0, 0, 255}));
  connect(gound2.p, R1.n) 
    annotation(Line(origin = {-70.0, -39.00000000000001}, 
    points = {{0.0, -53.0}, {0.0, -39.0}}, 
    color = {0, 0, 255}));
  connect(piecewiseLinearVoltageSource.p, R2.p) 
    annotation(Line(origin = {-72.99999999999999, 45.0}, 
    points = {{-23.0, -43.0}, {-23.0, 27.0}, {23.0, 27.0}}, 
    color = {0, 0, 255}));
  connect(D1.A, R2.p) 
    annotation(Line(origin = {-59.999999999999986, 61.0}, 
    points = {{-10.0, -11.0}, {-10.0, 11.0}, {10.0, 11.0}}, 
    color = {0, 0, 255}));
  connect(D1.K, D2.A) 
    annotation(Line(origin = {-69.99999999999999, 27.0}, 
    points = {{0.0, 3.0}, {0.0, -4.0}}, 
    color = {0, 0, 255}));
  connect(D2.K, R1.p) 
    annotation(Line(origin = {-62.999999999999986, -4.0}, 
    points = {{-7.0, 7.0}, {-7.0, -54.0}}, 
    color = {0, 0, 255}));
  connect(R4.n, gound2.p) 
    annotation(Line(origin = {-46.999999999999986, -86.0}, 
    points = {{23.0, 6.0}, {23.0, -6.0}, {-23.0, -6.0}}, 
    color = {0, 0, 255}));
  connect(pNPBipolarTransistor.B, R1.p) 
    annotation(Line(origin = {-59.999999999999986, -33.0}, 
    points = {{10.0, 25.0}, {-10.0, 25.0}, {-10.0, -25.0}}, 
    color = {0, 0, 255}));
  connect(pNPBipolarTransistor.C, R3.p) 
    annotation(Line(origin = {-26.999999999999986, -17.0}, 
    points = {{-3.0, 3.0}, {3.0, 3.0}, {3.0, -3.0}}, 
    color = {0, 0, 255}));
  connect(pNPBipolarTransistor.E, R2.n) 
    annotation(Line(origin = {-18.999999999999986, 35.0}, 
    points = {{-11.0, -37.0}, {11.0, -37.0}, {11.0, 37.0}, {-11.0, 37.0}}, 
    color = {0, 0, 255}));
  connect(currentSensor.p, R2.n) 
    annotation(Line(origin = {-8.999999999999986, 72.0}, 
    points = {{17.0, 0.0}, {-21.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(currentSensor.n, LED1.p) 
    annotation(Line(origin = {37.000000000000014, 69.0}, 
    points = {{-9.0, 3.0}, {13.0, 3.0}, {13.0, -5.0}}, 
    color = {0, 0, 255}));
  connect(LED1.n, LED2.p) 
    annotation(Line(origin = {50.000000000000014, 35.00000000000001}, 
    points = {{0.0, 9.0}, {0.0, -10.0}}, 
    color = {0, 0, 255}));
  connect(LED2.n, LED3.p) 
    annotation(Line(origin = {50.000000000000014, -3.999999999999993}, 
    points = {{0.0, 9.0}, {0.0, -10.0}}, 
    color = {0, 0, 255}));
  connect(LED3.n, nPNBipolarTransistor.C) 
    annotation(Line(origin = {39.000000000000014, -38.0}, 
    points = {{11.0, 4.0}, {-19.0, 4.0}, {-19.0, -2.0}}, 
    color = {0, 0, 255}));
  connect(nPNBipolarTransistor.B, R4.p) 
    annotation(Line(origin = {-11.999999999999986, -53.0}, 
    points = {{12.0, 7.0}, {-12.0, 7.0}, {-12.0, -7.0}}, 
    color = {0, 0, 255}));
  connect(R3.n, R4.p) 
    annotation(Line(origin = {-23.999999999999986, -50.0}, 
    points = {{0.0, 10.0}, {0.0, -10.0}}, 
    color = {0, 0, 255}));
  connect(nPNBipolarTransistor.E, gound2.p) 
    annotation(Line(origin = {-24.999999999999986, -72.0}, 
    points = {{45.0, 20.0}, {45.0, -20.0}, {-45.0, -20.0}}, 
    color = {0, 0, 255}));
  connect(LED1.W, add3_1.u1) 
    annotation(Line(origin = {64.0, 69.0}, 
    points = {{-7.0, -4.0}, {-7.0, -35.0}, {12.0, -35.0}}, 
    color = {0, 0, 127}));
  connect(LED2.W, add3_1.u2) 
    annotation(Line(origin = {67.0, 26.0}, 
    points = {{-10.0, 0.0}, {9.0, 0.0}}, 
    color = {0, 0, 127}));
  connect(LED3.W, add3_1.u3) 
    annotation(Line(origin = {67.0, 3.0}, 
    points = {{-10.0, -16.0}, {-10.0, 15.0}, {9.0, 15.0}}, 
    color = {0, 0, 127}));
end LedDriver;