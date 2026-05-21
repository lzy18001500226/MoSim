model HydraulicServoControlSystem "液压伺服控制系统"
import Modelica.Constants.pi;
  TYThermalHydraulics.Actuators.Cylinder.FixDActingAsysmCylinder fixDActingAsysmCylinder(s(start = 0.15), 
    m = 0) 
    annotation (Placement(transformation(origin = {-32.33, 100.80000000000001}, 
      extent = {{-10.200000000000001, -6.800000000000001}, {10.86, 8.0}})));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve 
    annotation (Placement(transformation(origin = {-53.999999999999986, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Valves.FlowValves.SymThrottleValve symThrottleValve1 
    annotation (Placement(transformation(origin = {-14.0, 78.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Valves.PressureValves.ReliefValve reliefValve(pcrack = 2.06e7) 
    annotation (Placement(transformation(origin = {-32.53, -72.0}, 
      extent = {{-10.530000000000003, -10.0}, {10.529999999999998, 9.999999999999986}})));
  TYThermalHydraulics.Valves.DirectionalValves.CheckValve checkValve 
    annotation (Placement(transformation(origin = {-67.0, -38.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.DirectionalValves.DirectionalValve34_O directionalValve34_O(qnom = 0.000666666666666667, 
    Userfp = "from oil") 
    annotation (Placement(transformation(origin = {-34.53, 14.850000000000033}, 
      extent = {{-21.0, -10.0}, {21.0, 10.0}})));
  TYThermalHydraulics.Pumps.ConstantPumps.ConstantPump constantPump 
    annotation (Placement(transformation(origin = {-66.99999999999999, -72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C 
    annotation (Placement(transformation(origin = {-53.999999999999986, 46.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C1 
    annotation (Placement(transformation(origin = {-14.0, 46.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C2 
    annotation (Placement(transformation(origin = {-66.99999999999999, -12.999999999999986}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 90.0)));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C3 
    annotation (Placement(transformation(origin = {-49.0, -54.00000000000003}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = -180.0)));
  Modelica.Mechanics.Rotational.Sources.Speed speed(f_crit = 0, exact = false) 
    annotation (Placement(transformation(origin = {-100.93999999999997, -72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const(k = 2000) 
    annotation (Placement(transformation(origin = {-166.94, -72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain(k = 2 *pi / 60) 
    annotation (Placement(transformation(origin = {-133.94, -72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Sensors.PositionSensor positionSensor 
    annotation (Placement(transformation(origin = {40.716886784682416, 100.80000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Sine sine(offset = 0.15, amplitude = 0.15, 
    f = 0.2) annotation (Placement(transformation(origin = {183.62500000000006, 12.800000000000026}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation (Placement(transformation(origin = {150.0, 12.800000000000026}, 
      extent = {{10.0, 10.0}, {-10.0, -10.0}})));
  Modelica.Blocks.Math.Gain gain1(k = 50) 
    annotation (Placement(transformation(origin = {97.37500000000003, 50.80000000000004}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Continuous.Integrator integrator(k = 1) 
    annotation (Placement(transformation(origin = {97.37500000000003, 12.800000000000026}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Continuous.Derivative derivative(k = 0, 
    T = 0.001) 
    annotation (Placement(transformation(origin = {97.37500000000003, -25.199999999999967}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Math.Add3 add3_1 
    annotation (Placement(transformation(origin = {55.75000000000003, 12.800000000000026}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain2(k = -1) 
    annotation (Placement(transformation(origin = {22.12500000000007, 12.800000000000033}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.Mass mass(m = 10, 
    s(start 
       = 0)) 
    annotation (Placement(transformation(origin = {6.0, 101.40000000000002}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 15, Tolerance = 0.0001), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
      lineColor = {167, 98, 0}, 
      fillColor = {167, 98, 0}, 
      fillPattern = FillPattern.Solid, 
      points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {167, 98, 0}, 
      thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {167, 98, 0}, 
      thickness = 5.0)}), 
    Diagram(coordinateSystem(extent = {{-200.0, -150.0}, {200.0, 150.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/HydraulicServoControlSystem.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="位移/m", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 15), zoom_y_l=(-0.05, 0.35)), 
Plot(y=["feedback.u1", "feedback.u2"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 15), zoom_y_l=(-50, 200)), 
Plot(y=["fixDActingAsysmCylinder.port_A.p", "fixDActingAsysmCylinder.port_B.p"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 15), zoom_y_l=(19, 26)), 
Plot(y=["fixDActingAsysmCylinder.port_A.T", "fixDActingAsysmCylinder.port_B.T"], colors=["4278190335", "4294901760"])})
})));
  TYThermalHydraulics.Sources.PressurizedTankwithHeatExchange pressurizedTankwithHeatExchange(Perimeter = 2, Area(displayUnit = "m2") = 0.25, h0(displayUnit = "m"), 
    useHeatPort = true, 
    Hcoeff = 1000) 
    annotation (Placement(transformation(origin = {-49.0, -108.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYThermalHydraulics.Sources.TemperatureSource temperatureSource(ConstantTemperature = 283.15) 
    annotation (Placement(transformation(origin = {-23.530000000000005, -122.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
equation
  connect(symThrottleValve.port_B, fixDActingAsysmCylinder.port_A) 
    annotation (Line(origin = {-42.0, 84.0}, 
      points = {{-11.999999999999986, 4.0}, {1.6700000000000017, 4.0}, {1.6700000000000017, 10.000000000000014}}, 
      color = {255, 170, 0}));
  connect(fixDActingAsysmCylinder.port_B, symThrottleValve1.port_B) 
    annotation (Line(origin = {-23.0, 102.0}, 
      points = {{-5.329999999999998, -7.999999999999986}, {-5.329999999999998, -14.0}, {9.0, -14.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C.port_B, symThrottleValve.port_A) 
    annotation (Line(origin = {-54.0, 62.0}, 
      points = {{1.4210854715202004e-14, -6.0}, {1.4210854715202004e-14, 6.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C1.port_B, symThrottleValve1.port_A) 
    annotation (Line(origin = {-14.0, 62.0}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C.port_A, directionalValve34_O.port_A) 
    annotation (Line(origin = {-46.0, 30.0}, 
      points = {{-7.999999999999986, 6.0}, {-7.999999999999986, 0.0}, {9.469999999999999, 0.0}, {9.469999999999999, -5.149999999999967}}, 
      color = {255, 170, 0}));
  connect(directionalValve34_O.port_B, pipe_C1.port_A) 
    annotation (Line(origin = {-23.0, 30.0}, 
      points = {{-9.530000000000001, -5.149999999999967}, {-9.530000000000001, 0.0}, {9.0, 0.0}, {9.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(checkValve.port_B, pipe_C2.port_A) 
    annotation (Line(origin = {-66.99999999999999, -25.0}, 
      points = {{-1.4210854715202004e-14, -3.0}, {0.0, 2.000000000000014}}, 
      color = {255, 170, 0}));
  connect(pipe_C2.port_B, directionalValve34_O.port_P) 
    annotation (Line(origin = {-66.99999999999999, 0.0}, 
      points = {{0.0, -2.999999999999986}, {0.0, 4.850000000000033}, {30.469999999999985, 4.850000000000033}}, 
      color = {255, 170, 0}));
  connect(constantPump.port_B, checkValve.port_A) 
    annotation (Line(origin = {-66.99999999999999, -55.0}, 
      points = {{0.0, -7.0}, {-1.4210854715202004e-14, 7.0}}, 
      color = {255, 170, 0}));
  connect(constantPump.port_B, pipe_C3.port_A) 
    annotation (Line(origin = {-61.0, -58.0}, 
      points = {{-5.999999999999986, -4.0}, {-5.999999999999986, 3.9999999999999716}, {2.0, 3.9999999999999716}}, 
      color = {255, 170, 0}));
  connect(pipe_C3.port_B, reliefValve.port_A) 
    annotation (Line(origin = {-34.0, -58.0}, 
      points = {{-5.0, 3.9999999999999716}, {1.4699999999999989, 3.9999999999999716}, {1.4699999999999989, -4.000000000000007}}, 
      color = {255, 170, 0}));
  connect(const.y, gain.u) 
    annotation (Line(origin = {-150.94, -72.0}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(gain.y, speed.w_ref) 
    annotation (Line(origin = {-117.94, -72.0}, 
      points = {{-5.0, 0.0}, {5.000000000000028, 0.0}}, 
      color = {0, 0, 127}));
  connect(speed.flange, constantPump.flange_a) 
    annotation (Line(origin = {-84.0, -72.0}, 
      points = {{-6.939999999999969, 0.0}, {7.000000000000014, 0.0}}, 
      color = {0, 0, 0}));
  connect(positionSensor.s, feedback.u2) 
    annotation (Line(origin = {135.92498678468232, 73.2}, 
      points = {{-84.2080999999999, 27.60000000000001}, {14.075013215317682, 27.60000000000001}, {14.075013215317682, -52.39999999999998}}, 
      color = {0, 0, 127}));
  connect(feedback.u1, sine.y) 
    annotation (Line(origin = {178.625, 32.800000000000026}, 
      points = {{-20.625, -20.0}, {-5.999999999999943, -20.0}}, 
      color = {0, 0, 127}));
  connect(gain1.u, feedback.y) 
    annotation (Line(origin = {124.00000000000003, 24.60000000000005}, 
      points = {{-14.625, 26.19999999999999}, {4.0, 26.19999999999999}, {4.0, -11.800000000000026}, {16.99999999999997, -11.800000000000026}}, 
      color = {0, 0, 127}));
  connect(integrator.u, feedback.y) 
    annotation (Line(origin = {124.00000000000003, 7.600000000000051}, 
      points = {{-14.625, 5.199999999999974}, {16.99999999999997, 5.199999999999974}}, 
      color = {0, 0, 127}));
  connect(derivative.u, feedback.y) 
    annotation (Line(origin = {124.00000000000003, -8.399999999999949}, 
      points = {{-14.625, -16.80000000000002}, {4.0, -16.80000000000002}, {4.0, 21.199999999999974}, {16.99999999999997, 21.199999999999974}}, 
      color = {0, 0, 127}));
  connect(add3_1.u1, gain1.y) 
    annotation (Line(origin = {80.00000000000004, 38.60000000000006}, 
      points = {{-12.250000000000014, -17.800000000000033}, {-3.0, -17.800000000000033}, {-3.0, 12.199999999999982}, {6.374999999999986, 12.199999999999982}}, 
      color = {0, 0, 127}));
  connect(add3_1.u3, derivative.y) 
    annotation (Line(origin = {80.37500000000004, -21.39999999999995}, 
      points = {{-12.625000000000014, 26.199999999999974}, {-4.0, 26.199999999999974}, {-4.0, -3.8000000000000185}, {5.999999999999986, -3.8000000000000185}}, 
      color = {0, 0, 127}));
  connect(add3_1.y, gain2.u) 
    annotation (Line(origin = {39.75000000000003, 12.600000000000051}, 
      points = {{5.0, 0.19999999999997442}, {-5.624999999999957, 0.19999999999998153}}, 
      color = {0, 0, 127}));
  connect(mass.flange_b, positionSensor.flange) 
    annotation (Line(origin = {23.716886784682423, 100.80000000000004}, 
      points = {{-7.716886784682423, 0.5999999999999801}, {6.999999999999993, 0.5999999999999801}, {6.999999999999993, -2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(integrator.y, add3_1.u2) 
    annotation (Line(origin = {77.0, 3.8000000000000256}, 
      points = {{9.375000000000028, 9.0}, {-9.249999999999972, 9.0}}, 
      color = {0, 0, 127}));
  connect(directionalValve34_O.realin, gain2.y) 
    annotation (Line(origin = {0.0, 13.0}, 
      points = {{-12.530000000000001, -0.19999999999996732}, {11.125000000000071, -0.19999999999996732}}, 
      color = {0, 0, 127}));
  connect(fixDActingAsysmCylinder.flange_b, mass.flange_a) 
    annotation (Line(origin = {-12.0, 100.0}, 
      points = {{-9.529999999999994, 0.8000000000000114}, {8.0, 0.8000000000000114}, {8.0, 1.40000000000002}}, 
      color = {0, 127, 0}));
  connect(pressurizedTankwithHeatExchange.port_B, constantPump.port_A) 
    annotation (Line(origin = {-59.0, -102.0}, 
      points = {{7.0, -12.0}, {7.0, -20.0}, {-7.999999999999986, -20.0}, {-7.999999999999986, 20.200000000000003}}, 
      color = {255, 170, 0}));
  connect(reliefValve.port_B, pressurizedTankwithHeatExchange.port_A) 
    annotation (Line(origin = {-39.0, -92.0}, 
      points = {{6.469999999999999, 10.0}, {6.469999999999999, -2.0}, {-5.0, -2.0}, {-5.0, -11.0}}, 
      color = {255, 170, 0}));
  connect(temperatureSource.heat_a, pressurizedTankwithHeatExchange.heat_a) 
    annotation (Line(origin = {-30.0, -116.0}, 
      points = {{-1.5464264331577198, -6.076712789877874}, {-16.146326158754363, -6.076712789877874}, {-16.146326158754363, 3.0117249174324883}}, 
      color = {191, 0, 0}));
  connect(directionalValve34_O.port_T, pressurizedTankwithHeatExchange.port_A) 
    annotation (Line(origin = {-38.0, -49.0}, 
      points = {{5.469999999999999, 53.85000000000004}, {36.0, 53.85000000000004}, {36.0, -45.0}, {-6.0, -45.0}, {-6.0, -54.0}}, 
      color = {255, 170, 0}));
end HydraulicServoControlSystem;