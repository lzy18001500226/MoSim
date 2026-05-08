model InversePendulum "倒立摆"
  Modelica.Mechanics.Rotational.Sensors.AngleSensor angleSensor 
    annotation (Placement(transformation(origin = {39.99999999999999, -37.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Continuous.PID PID1(Ti = 1e9, k = -85 * 9.81 * 5, Td = 0.2) 
    annotation (Placement(transformation(origin = {39.99999999999999, 53.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 180.0)));
  Modelica.Mechanics.Translational.Sources.Force force 
    annotation (Placement(transformation(origin = {2.220446049250313e-16, 53.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = 180.0)));
  inner TYMultibody.World world 
    annotation (Placement(transformation(origin = {-72.0, 3.552713678800501e-15}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Prismatic prismatic(useAxisFlange = true, v_rel_0 = 0) 
    annotation (Placement(transformation(origin = {-34.0, 0.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYMultibody.Bodies.Body body(m = 75, r_AG_a = {0.5, 0, 0}, r_AB_a = {0.5, 0, 0}, shapeType = "box") 
    annotation (Placement(transformation(origin = {30.0, 3.552713678800501e-15}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.Body body2(m = 10, r_AG_a = {0, 2.5, 0}, r_AB_a = {0, 2.5, 0}) 
    annotation (Placement(transformation(origin = {2.220446049250313e-16, -68.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
      rotation = -90.0)));
  TYMultibody.Joints.Revolute revolute(useAxisFlange = true, phi_rel_0 = -0.349065850398866) 
    annotation (Placement(transformation(origin = {5.551115123125783e-16, -30.000000000000007}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = 90.0)));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0)}), 
    Protection(access = Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYMultibody/Resources/html/InversePendulum.html"), 
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={-6,-4}, 
points={{-92,80},{-92,-80},{92,-80},{92,80},{-92,80}}, 
color={255,255,255})}),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title="[m]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(0.5, 4)), 
Plot(y=["body2.r_OG_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(2.3, 2.55)), 
Plot(y=["body2.r_OG_0[2]"], colors=["4278190335"])})
})),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,NumberOfIntervals=500,StartTime=0,StopTime=10,Tolerance=0.0001));
equation
  connect(world.frame_b, prismatic.frame_a) 
    annotation (Line(origin = {-72.0, 0.0}, 
      points = {{10.0, 0.0}, {28.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(prismatic.frame_b, body.frame_a) 
    annotation (Line(origin = {-22.0, 0.0}, 
      points = {{-2.0, 0.0}, {42.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute.frame_a, prismatic.frame_b) 
    annotation (Line(origin = {-48.0, -30.0}, 
      points = {{48.0, 10.0}, {48.0, 30.0}, {24.0, 30.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute.axis, angleSensor.flange) 
    annotation (Line(origin = {24.0, -39.0}, 
      points = {{-14.0, 2.0}, {6.0, 2.0}}, 
      color = {0, 0, 0}));
  connect(PID1.y, force.f) 
    annotation (Line(origin = {23.0, 60.0}, 
      points = {{6.0, -6.0}, {-11.0, -6.0}}, 
      color = {0, 0, 127}));
  connect(angleSensor.phi, PID1.u) 
    annotation (Line(origin = {66.0, 12.0}, 
      points = {{-15.0, -49.0}, {4.0, -49.0}, {4.0, 42.0}, {-14.0, 42.0}}, 
      color = {0, 0, 127}));



  connect(revolute.frame_b, body2.frame_a) 
    annotation (Line(origin = {8.0, -75.0}, 
      points = {{-8.0, 35.0}, {-8.0, 17.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(prismatic.axis, force.flange) 
    annotation (Line(origin = {-38.0, 22.0}, 
      points = {{11.0, -12.0}, {11.0, 32.0}, {28.0, 32.0}}, 
      color = {96, 96, 96}));
end InversePendulum;