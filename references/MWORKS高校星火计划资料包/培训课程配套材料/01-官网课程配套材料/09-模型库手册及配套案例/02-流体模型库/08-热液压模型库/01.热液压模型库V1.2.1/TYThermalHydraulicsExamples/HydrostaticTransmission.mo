model HydrostaticTransmission "静压传动系统"
import Modelica.Constants.pi;
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    Diagram(coordinateSystem(extent = {{-110.0, -100.0}, {110.0, 100.0}}, 
      grid = {2.0, 2.0})), 
    Documentation(link = "modelica://TYThermalHydraulics/Resources/HTML/HydrostaticTransmission.html"), 
    experiment(Algorithm=Dassl,Interval=0.01,StartTime=0,StopTime=10,Tolerance=1e-05,InlineIntegrator=false,InlineStepSize=false),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=2,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="[rev/min]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-500, 2000)), 
Plot(y=["constantPump.constantPump.w", "constantMotor1.constantMotor.w"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar
", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-50, 250)), 
Plot(y=["constantPump.port_B.p"], colors=["4278190335"])})
})),Protection(access=Access.nonPackageDuplicate));
  TYThermalHydraulics.Pumps.ConstantPumps.ConstantPump constantPump(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {2.000000000000001, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Valves.PressureValves.ReliefValve reliefValve1(pcrack = 1.8e7, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {34.50000000000001, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Actuators.Motors.ConstantMotor constantMotor1(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {67.00000000000003, 0.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYThermalHydraulics.Sources.Tank tank3(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {1.9964584516129067, -21.999999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Pipes.Pipe_C pipe_C(length = 4, 
    redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) annotation (Placement(transformation(origin = {53.50000000000001, 22.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Sources.Speed speed1 
    annotation (Placement(transformation(origin = {-30.50000000000001, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const1(k = 1500) 
    annotation (Placement(transformation(origin = {-95.50000000000006, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Math.Gain gain1(k = 2 * pi / 60) 
    annotation (Placement(transformation(origin = {-63.00000000000003, 0.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Components.Inertia inertia1(w(fixed = true, start = 0)) 
    annotation (Placement(transformation(origin = {93.50000000000001, -1.4210854715202004e-14}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Sources.Tank tank4(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {34.49645845161291, -22.000000000000025}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYThermalHydraulics.Sources.Tank tank5(redeclare model Medium = TYOilMedia.ThermalHydraulicOil.Types._5W30) 
    annotation (Placement(transformation(origin = {66.99645845161294, -22.000000000000025}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Components.Damper damper(d=0.2) 
    annotation (Placement(transformation(origin={132,-1.40998e-14}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.Rotational.Components.Fixed fixed 
    annotation (Placement(transformation(origin={158,-22}, 
extent={{-10,-10},{10,10}})));
equation
  connect(speed1.w_ref, gain1.y) 
    annotation (Line(origin = {-62.50000000000003, 9.999999999999986}, 
      points = {{20.0, -10.0}, {11.0, -10.0}}, 
      color = {0, 0, 127}));
  connect(gain1.u, const1.y) 
    annotation (Line(origin = {-94.50000000000003, 9.999999999999986}, 
      points = {{20.0, -10.0}, {10.0, -10.0}}, 
      color = {0, 0, 127}));
  connect(speed1.flange, constantPump.flange_a) 
    annotation (Line(origin = {-12.499999999999993, -1.4210854715202004e-14}, 
      points = {{-8.0, 0.0}, {4.0, 0.0}}, 
      color = {0, 0, 0}));
  connect(tank3.port_A, constantPump.port_A) 
    annotation (Line(origin = {1.500000000000007, -21.000000000000014}, 
      points = {{0.0, -1.0}, {0.0, 11.0}}, 
      color = {255, 170, 0}));
  connect(constantMotor1.flange_b, inertia1.flange_a) 
    annotation (Line(origin = {80.5, -1.4210854715202004e-14}, 
      points = {{-3.0, 0.0}, {3.0, 0.0}}, 
      color = {0, 0, 0}));
  connect(tank4.port_A, reliefValve1.port_B) 
    annotation (Line(origin = {34.5, -16.000000000000014}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(tank5.port_A, constantMotor1.port_B) 
    annotation (Line(origin = {67.5, -16.000000000000014}, 
      points = {{0.0, -6.0}, {0.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(constantPump.port_B, pipe_C.port_A) 
    annotation (Line(origin = {22.500000000000007, 16.999999999999986}, 
      points = {{-21.0, -7.0}, {-21.0, 6.0}, {21.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(reliefValve1.port_A, pipe_C.port_A) 
    annotation (Line(origin = {39.5, 16.999999999999986}, 
      points = {{-5.0, -7.0}, {-5.0, 6.0}, {4.0, 6.0}}, 
      color = {255, 170, 0}));
  connect(pipe_C.port_B, constantMotor1.port_A) 
    annotation (Line(origin = {65.5, 16.999999999999986}, 
      points = {{-2.0, 6.0}, {2.0, 6.0}, {2.0, -7.0}}, 
      color = {255, 170, 0}));
  connect(inertia1.flange_b, damper.flange_a) 
  annotation(Line(origin={117,0}, 
points={{-13.5,-1.42109e-14},{5,-1.42109e-14},{5,-1.40998e-14}}, 
color={0,0,0}));
  connect(damper.flange_b, fixed.flange) 
  annotation(Line(origin={156,-11}, 
points={{-14,11},{2,11},{2,-11}}, 
color={0,0,0}));
end HydrostaticTransmission;