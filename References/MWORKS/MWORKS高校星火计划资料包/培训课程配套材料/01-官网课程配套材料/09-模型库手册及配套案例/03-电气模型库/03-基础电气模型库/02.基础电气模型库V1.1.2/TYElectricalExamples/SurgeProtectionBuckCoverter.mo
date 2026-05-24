model SurgeProtectionBuckCoverter "浪涌保护降压变换电路"
  parameter Real D = 0.5 "占空比";
  parameter Modelica.Units.SI.Frequency fsw = 5000 "频率";
  parameter Modelica.Units.SI.Time simTime = 0.05 "时间";
  parameter Modelica.Units.SI.Voltage Vdc = 169.7056 "直流电压";

  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-3.55271e-15, 27}, 
    lineColor = {85, 0, 255}, 
    fillColor = {85, 0, 255}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {3.55271e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {85, 0, 255}, 
    thickness = 5), Line(origin = {1.06581e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {85, 0, 255}, 
    thickness = 5)}), 
    Diagram(coordinateSystem(extent = {{-204.0, -100.0}, {246.0, 122.0}}, 
    grid = {2.0, 2.0})), 
    experiment(Algorithm = Dassl, Interval = 1e-06, StartTime = 0, StopTime = 0.05, Tolerance = 0.0001), 
    Documentation(link = "modelica://TYElectrical/Resources/Example/SurgeProtectionBuckCoverter.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 886], y=["Source1.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310), 
CreatePlot(id=1, position=[0, 28, 2029, 886], y=["Source2.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310, sub_plot=[2, 1]), 
CreatePlot(id=1, position=[0, 28, 2029, 886], y=["buckConverter.vDC1"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310, sub_plot=[3, 1]), 
CreatePlot(id=1, position=[0, 28, 2029, 886], y=["R_load.v"], x_display_unit="s", y_display_units=["V"], y_axis=[1], legend_layout=7, legend_frame=True, left_title="[V]", fix_time_range_value=6.95225e-310, sub_plot=[4, 1])})
})));
  TYElectrical.PowerConverters.BuckConverter buckConverter(ModelingOption = 3, Switching_Device = "MOSFET", Vth = 1.7, Diode_Vf = 0.6, Lf = 1.5e-3, Rf = 1e-6, Cf = 1e-4) 
    annotation(Placement(transformation(origin = {153.00000000000003, -4.440892098500626e-15}, 
    extent = {{-23.0, -21.999999999999996}, {22.999999999999986, 21.999999999999996}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference GND 
    annotation(Placement(transformation(origin = {96.0474576271187, -64.0}, 
    extent = {{-12.999999999999943, -12.999999999999993}, {13.0, 13.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R_load(R = 15) 
    annotation(Placement(transformation(origin = {198.25000000000006, -10.500000000000002}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor L2(L = 1.5e-3, R = 0.1) 
    annotation(Placement(transformation(origin = {72.00000000000006, 13.136294168342427}, 
    extent = {{-13.0, -13.42372881355932}, {13.0, 13.42372881355932}})));
  TYElectrical.PowerConverters.TwoPulseGateMultiplexer twoPulseGateMultiplexer 
    annotation(Placement(transformation(origin = {138.134188034188, 86.80769230769236}, 
    extent = {{-15.834188034188049, -14.80769230769235}, {15.565811965811946, 15.992307692307648}})));
  Modelica.Blocks.Sources.Pulse pulse(amplitude = 15, 
    period = 1 / fsw, 
    width = D * 100) 
    annotation(Placement(transformation(origin = {96.00000000000003, 106.0}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Pulse pulse1(amplitude = 15, 
    period = 1 / fsw, 
    width = (1 - D) * 100, 
    offset = 0, 
    startTime = D / fsw) 
    annotation(Placement(transformation(origin = {96.00000000000003, 70.00000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.BasicComponents.IdealElectricSource.DCVoltageSource Source1(v0 = Vdc) 
    annotation(Placement(transformation(origin = {48.00000000000002, -15.000000000000007}, 
    extent = {{13.0, -13.0}, {-13.0, 13.0}}, 
    rotation = -270.0)));



  TYElectrical.BasicComponents.Passive.BasicPassive.Varistor varistor(VaristorType = "线性") 
    annotation(Placement(transformation(origin = {96.04745762711872, -18.00000000000001}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  Modelica.Blocks.Sources.Step step(startTime = 0.025) 
    annotation(Placement(transformation(origin = {-127.99999999999994, 82.95769230769235}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.BasicComponents.IdealElectricSource.DCVoltageSource Source2(v0 = 1082) 
    annotation(Placement(transformation(origin = {-148.99999999999991, 1.094915254237301}, 
    extent = {{13.0, -13.0}, {-13.0, 13.0}}, 
    rotation = -270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R1(R = 1000) 
    annotation(Placement(transformation(origin = {-127.99999999999994, 47.04745762711868}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 360.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Switch switch(R_closed = 1e-3, G_open = 1e-6) 
    annotation(Placement(transformation(origin = {-86, 47.1424}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R2(R = 25.1) 
    annotation(Placement(transformation(origin = {-61.99999999999994, 1.0949152542373013}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C1(C = 6.04e-6) 
    annotation(Placement(transformation(origin = {-109.99999999999994, 1.0949152542373046}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R3(R = 0.94) 
    annotation(Placement(transformation(origin = {-40.00000000000003, 47.094915254237314}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 360.0)));
  TYElectrical.BasicComponents.IdealBasicComponents.Inductor L1(L = 10.4e-6) 
    annotation(Placement(transformation(origin = {-7.999999999999986, 47.14237288135597}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor C2(C = 18e-6) 
    annotation(Placement(transformation(origin = {32.00000000000003, 47.14237288135597}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor R4(R = 19.8) 
    annotation(Placement(transformation(origin = {10.000000000000043, -1.905084745762699}, 
    extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
    rotation = 270.0)));
equation
  connect(L2.n, buckConverter.dc_p1) 
    annotation(Line(origin = {108.00000000000003, 13.000000000000007}, 
    points = {{-23.0, 0.0}, {22.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(twoPulseGateMultiplexer.G, buckConverter.G_PS1) 
    annotation(Line(origin = {154.00000000000003, 43.00000000000001}, 
    points = {{0.0, 44.0}, {0.0, -21.0}, {-1.0, -21.0}}, 
    color = {0, 0, 127}));
  connect(pulse.y, twoPulseGateMultiplexer.G1) 
    annotation(Line(origin = {115.00000000000003, 101.0}, 
    points = {{-8.0, 5.0}, {11.0, 5.0}, {11.0, -6.0}, {7.0, -6.0}}, 
    color = {0, 0, 127}));
  connect(pulse1.y, twoPulseGateMultiplexer.G2) 
    annotation(Line(origin = {115.00000000000003, 75.0}, 
    points = {{-8.0, -5.0}, {7.0, -5.0}, {7.0, 4.0}}, 
    color = {0, 0, 127}));
  connect(Source1.p, L2.p) 
    annotation(Line(origin = {18.000000000000036, 8.000000000000007}, 
    points = {{30.0, -10.0}, {30.0, 3.0}, {41.0, 3.0}, {41.0, 5.0}}, 
    color = {0, 0, 255}));
  connect(varistor.p, buckConverter.dc_p1) 
    annotation(Line(origin = {117.00000000000003, 4.000000000000006}, 
    points = {{-21.0, -12.0}, {-21.0, 9.0}, {13.0, 9.0}}, 
    color = {0, 0, 255}));
  connect(buckConverter.dc_n2, R_load.n) 
    annotation(Line(origin = {190.50000000000006, -19.499999999999993}, 
    points = {{-14.500000000000028, 6.299999999999983}, {-14.500000000000028, -8.906666666666663}, {7.797457627118632, -8.906666666666663}, {7.797457627118632, -1.0949152542372964}}, 
    color = {0, 0, 255}));
  connect(R1.n, switch.p) 
    annotation(Line(origin = {-107, 47}, 
    points = {{-10.8712, 0.0610272}, {10.8976, 0.0610272}, {10.8976, 0.0881664}}, 
    color = {0, 0, 255}));
  connect(R1.p, Source2.p) 
    annotation(Line(origin = {-142.99999999999994, 31.000000000000007}, 
    points = {{5.0, 16.0}, {-6.0, 16.0}, {-6.0, -17.0}}, 
    color = {0, 0, 255}));
  connect(C1.p, switch.p) 
    annotation(Line(origin = {-103, 29}, 
    points = {{-7.05421, -17.8027}, {-7.05421, 18.0882}, {6.89764, 18.0882}}, 
    color = {0, 0, 255}));
  connect(switch.n, R3.p) 
    annotation(Line(origin = {-63, 47}, 
    points = {{-12.8712, 0.155942}, {12.8976, 0.155942}, {12.8976, 0.0407087}}, 
    color = {0, 0, 255}));
  connect(R3.n, L1.p) 
    annotation(Line(origin = {-23.99999999999997, 47.00000000000001}, 
    points = {{-6.0, 0.0}, {6.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(L1.n, C2.p) 
    annotation(Line(origin = {12.000000000000028, 47.00000000000001}, 
    points = {{-10.0, 0.0}, {10.0, 0.0}}, 
    color = {0, 0, 255}));
  connect(C2.n, buckConverter.dc_p1) 
    annotation(Line(origin = {86.00000000000003, 30.000000000000007}, 
    points = {{-44.0, 17.0}, {44.0, 17.0}, {44.0, -17.0}}, 
    color = {0, 0, 255}));
  connect(step.y, switch.v_T) 
    annotation(Line(origin = {-106, 68}, 
    points = {{-11, 14.9577}, {15, 14.9577}, {15, -11.3542}, {20.0516, -11.3542}}, 
    color = {0, 0, 127}));
  connect(Source2.n, C1.n) 
    annotation(Line(origin = {-132.99999999999994, -21.999999999999993}, 
    points = {{-16.0, 10.0}, {-16.0, -14.0}, {23.0, -14.0}, {23.0, 13.0}}, 
    color = {0, 0, 255}));
  connect(R2.p, R3.p) 
    annotation(Line(origin = {-55.99999999999997, 29.000000000000007}, 
    points = {{-6.0, -18.0}, {-6.0, 16.0}, {6.0, 16.0}, {6.0, 18.0}}, 
    color = {0, 0, 255}));
  connect(R2.n, C1.n) 
    annotation(Line(origin = {-89.99999999999997, -21.999999999999993}, 
    points = {{28.0, 13.0}, {28.0, -14.0}, {-20.0, -14.0}, {-20.0, 13.0}}, 
    color = {0, 0, 255}));
  connect(R4.p, C2.p) 
    annotation(Line(origin = {14.000000000000028, 29.000000000000007}, 
    points = {{-4.0, -21.0}, {-4.0, 18.0}, {8.0, 18.0}}, 
    color = {0, 0, 255}));
  connect(R4.n, C1.n) 
    annotation(Line(origin = {-55.99999999999997, -21.999999999999993}, 
    points = {{66.0, 10.0}, {66.0, -14.0}, {-54.0, -14.0}, {-54.0, 13.0}}, 
    color = {0, 0, 255}));
  connect(Source1.n, varistor.n) 
    annotation(Line(origin = {72.00000000000003, -30.999999999999993}, 
    points = {{-24.0, 3.0}, {-24.0, -6.0}, {24.0, -6.0}, {24.0, 3.0}}, 
    color = {0, 0, 255}));
  connect(R4.n, varistor.n) 
    annotation(Line(origin = {51.00000000000003, -26.999999999999993}, 
    points = {{-41.0, 15.0}, {-41.0, -10.0}, {45.0, -10.0}, {45.0, -1.0}}, 
    color = {0, 0, 255}));
  connect(buckConverter.dc_n1, varistor.n) 
    annotation(Line(origin = {113.00000000000003, -28.999999999999993}, 
    points = {{17.0, 16.0}, {17.0, 1.0}, {-17.0, 1.0}}, 
    color = {0, 0, 255}));
  connect(GND.p, varistor.n) 
    annotation(Line(origin = {96.00000000000003, -45.99999999999998}, 
    points = {{0.0, -5.0}, {0.0, 18.0}}, 
    color = {0, 0, 255}));
  connect(R_load.p, buckConverter.dc_p2) 
    annotation(Line(origin = {187.00000000000003, 6.000000000000006}, 
    points = {{11.0, -7.0}, {11.0, 7.0}, {-11.0, 7.0}}, 
    color = {0, 0, 255}));
end SurgeProtectionBuckCoverter;