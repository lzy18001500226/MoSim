model StrainGauge "应变片测量电路"
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
    thickness = 5)}), Diagram(coordinateSystem(extent = {{-184, -100}, {170, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 0.0001), 
    __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 10, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, position=[0, 28, 2029, 790], y=["gain.y", "pulse.y"], x_display_unit="s", y_display_units=["", "1"], y_axis=[1, 1], legend_layout=7, legend_frame=True, fix_time_range_value=6.95225e-310)})
})), 
    Documentation(link = "modelica://TYElectrical/Resources/Example/StrainGauge.html"));
  TYElectrical.Sources.VoltageSources.PositiveSupplyRail positiveSupplyRail(v_constant = 10) 
    annotation(Placement(transformation(origin = {-116, 74}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.Sensors.StrainGauge strainGauge 
    annotation(Placement(transformation(origin = {-132, 37.9186}, 
    extent = {{-10, 10}, {10, -10}}, 
    rotation = -90)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor(R = 100) 
    annotation(Placement(transformation(origin = {-132, -18.0814}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference 
    annotation(Placement(transformation(origin = {-116, -44.0814}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor1(R = 100) 
    annotation(Placement(transformation(origin = {-98.0136, -18.0814}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor2(R = 100) 
    annotation(Placement(transformation(origin = {-98, 37.9186}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor3(R = 10e3) 
    annotation(Placement(transformation(origin = {-70, 19.9322}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor4(R = 10e3) 
    annotation(Placement(transformation(origin = {-32, 20}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYElectrical.DigitalComponents.GeneralCircuits.BandLimitOpAmp bandLimitOpAmp 
    annotation(Placement(transformation(origin = {-32, -0.149176}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference1 
    annotation(Placement(transformation(origin = {-4, 20.0136}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor5(R = 10e3) 
    annotation(Placement(transformation(origin = {-70, -18.0814}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor6(R = 10e3) 
    annotation(Placement(transformation(origin = {-32, -30.1492}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor8(R = 1000) 
    annotation(Placement(transformation(origin = {12, -0.0949691}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYElectrical.DigitalComponents.GeneralCircuits.BandLimitOpAmp bandLimitOpAmp1 
    annotation(Placement(transformation(origin = {60, 3.36283}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference2 
    annotation(Placement(transformation(origin = {23, 20.0136}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Sources.Pulse pulse(amplitude = 0.01, period = 0.5) 
    annotation(Placement(transformation(origin = {-166, 37.9186}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealSensors.VoltageSensor voltageSensor 
    annotation(Placement(transformation(origin = {102, -25.9864}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.ElectricalReference electricalReference3 
    annotation(Placement(transformation(origin = {132, -25.9864}, 
    extent = {{10, -10}, {-10, 10}}, 
    rotation = 90)));
  Modelica.Blocks.Math.Gain gain(k = -1 / 447) 
    annotation(Placement(transformation(origin = {122, -50}, 
    extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Resistor resistor7(R = 100000) 
    annotation(Placement(transformation(origin = {60, -30}, extent = {{-10, -10}, {10, 10}})));
  TYElectrical.BasicComponents.IdealBasicComponents.Capacitor capacitor(R = 1e-6) 
    annotation(Placement(transformation(origin = {60, -50}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(strainGauge.p, positiveSupplyRail.pin_p) 
    annotation(Line(origin = {-115, 53.9186}, 
    points = {{-16.9458, -5.89764}, {-16.9458, 11.8814}, {-1, 11.8814}}, 
    color = {0, 0, 255}));
  connect(resistor.p, strainGauge.n) 
    annotation(Line(origin = {-132, 18.9186}, 
    points = {{-0.0542065, -26.8976}, {-0.0542065, 8.8712}, {-0.0135696, 8.8712}}, 
    color = {0, 0, 255}));
  connect(resistor.n, electricalReference.p) 
    annotation(Line(origin = {-132, -19.0814}, 
    points = {{0.0135696, -9.1288}, {0.0135696, -15}, {16, -15}}, 
    color = {0, 0, 255}));
  connect(resistor2.p, positiveSupplyRail.pin_p) 
    annotation(Line(origin = {-83, 53.9186}, 
    points = {{-15.0542, -5.89764}, {-15.0542, 11.8814}, {-33, 11.8814}}, 
    color = {0, 0, 255}));
  connect(resistor2.n, resistor1.p) 
    annotation(Line(origin = {-68, 18.9186}, 
    points = {{-29.9864, 8.8712}, {-29.9864, -26.8976}, {-30.0678, -26.8976}}, 
    color = {0, 0, 255}));
  connect(resistor1.n, electricalReference.p) 
    annotation(Line(origin = {-85, -21.0814}, 
    points = {{-13, -7.1288}, {-13, -13}, {-31, -13}}, 
    color = {0, 0, 255}));
  connect(resistor3.p, resistor2.n) 
    annotation(Line(origin = {-55, 23.9186}, 
    points = {{-25.1024, -4.04061}, {-42.9864, -4.04061}, {-42.9864, 3.8712}}, 
    color = {0, 0, 255}));
  connect(bandLimitOpAmp.p, resistor3.n) 
    annotation(Line(origin = {-46, 11.8508}, 
    points = {{3.96485, -8.40423}, {-13.8712, -8.40423}, {-13.8712, 8.09497}}, 
    color = {0, 0, 255}));
  connect(resistor4.p, resistor3.n) 
    annotation(Line(origin = {-36, 19.8508}, 
    points = {{-6.10236, 0.0949935}, {-23.8712, 0.0949935}, {-23.8712, 0.0949696}}, 
    color = {0, 0, 255}));
  connect(resistor4.n, electricalReference1.p) 
    annotation(Line(origin = {35, 19.9186}, 
    points = {{-56.8712, 0.0949696}, {-49, 0.0949696}}, 
    color = {0, 0, 255}));
  connect(resistor5.p, resistor.p) 
    annotation(Line(origin = {-89, 4.91862}, 
    points = {{8.89764, -23.0542}, {5, -23.0542}, {5, 3}, {-43.0542, 3}, {-43.0542, -12.8977}}, 
    color = {0, 0, 255}));
  connect(bandLimitOpAmp.n, resistor5.n) 
    annotation(Line(origin = {-48, -11.1492}, 
    points = {{5.96485, 7.55579}, {-11.8712, 7.55579}, {-11.8712, -6.91863}}, 
    color = {0, 0, 255}));
  connect(resistor6.p, resistor5.n) 
    annotation(Line(origin = {-48, -24.1492}, 
    points = {{5.89764, -6.05421}, {-11.8712, -6.05421}, {-11.8712, 6.08137}}, 
    color = {0, 0, 255}));
  connect(bandLimitOpAmp.out, resistor8.p) 
    annotation(Line(origin = {11, -0.0813761}, 
    points = {{-33, -0.0677999}, {-9.10236, -0.0677999}, {-9.10236, -0.0677995}}, 
    color = {0, 0, 255}));
  connect(bandLimitOpAmp1.p, electricalReference2.p) 
    annotation(Line(origin = {77, 23.9186}, 
    points = {{-27.0352, -16.96}, {-44, -16.96}, {-44, -3.90503}}, 
    color = {0, 0, 255}));
  connect(resistor6.n, bandLimitOpAmp.out) 
    annotation(Line(origin = {-20, -15.0678}, 
    points = {{-1.8712, -15.0678}, {2, -15.0678}, {2, 14.9186239}, {-2, 14.9186239}}, 
    color = {0, 0, 255}));
  connect(resistor8.n, bandLimitOpAmp1.n) 
    annotation(Line(origin = {35, 0}, 
    points = {{-12.8712, -0.0813995}, {14.9648, -0.0813995}, {14.9648, -0.0813995}}, 
    color = {0, 0, 255}));
  connect(pulse.y, strainGauge.E) 
    annotation(Line(origin = {-153, 38}, 
    points = {{-2, -0.0814}, {9.5485, -0.0814}, {9.5485, -0.0725748}}, 
    color = {0, 0, 127}));
  connect(voltageSensor.n, electricalReference3.p) 
    annotation(Line(origin = {116, -20}, 
    points = {{-4, -5.98643}, {6, -5.98643}}, 
    color = {0, 0, 255}));
  connect(gain.u, voltageSensor.v) 
    annotation(Line(origin = {97, -38}, 
    points = {{13, -12}, {5, -12}, {5, 1.0136}}, 
    color = {0, 0, 127}));
  connect(resistor7.p, resistor8.n) 
    annotation(Line(origin = {40, -15}, 
    points = {{9.89764, -15.0542}, {-10, -15.0542}, {-10, 14.9186}, {-17.8712, 14.9186}}, 
    color = {0, 0, 255}));
  connect(bandLimitOpAmp1.out, resistor7.n) 
    annotation(Line(origin = {76, -13}, 
    points = {{-6, 16.36283}, {6, 16.36283}, {6, -16.9864}, {-5.8712, -16.9864}}, 
    color = {0, 0, 255}));
  connect(capacitor.n, bandLimitOpAmp1.out) 
    annotation(Line(origin = {75, -23}, 
    points = {{-4.8712, -26.9864}, {7, -26.9864}, {7, 26.36283}, {-5, 26.36283}}, 
    color = {0, 0, 255}));
  connect(capacitor.p, resistor8.n) 
    annotation(Line(origin = {40, -25}, 
    points = {{9.89764, -25.0542}, {-10, -25.0542}, {-10, 24.9186}, {-17.8712, 24.9186}}, 
    color = {0, 0, 255}));
  connect(voltageSensor.p, resistor7.n) 
    annotation(Line(origin = {81, -28}, 
    points = {{11, 2.0136}, {1, 2.0136}, {1, -1.98643}, {-10.8712, -1.98643}}, 
    color = {0, 0, 255}));
end StrainGauge;