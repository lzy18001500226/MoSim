model DoublePendulum "双摆"
  TYMultibody.Joints.Revolute revolute(useAxisFlange = false, 
    animation = true) annotation (Placement(transformation(origin = {-36.193109527419594, 4.10757946210269}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute1(
    phi_rel_fixed = true, om_rel_fixed = false, 
    useAxisFlange = true) 

    annotation (Placement(transformation(origin = {40.06365869577208, 4.381418092909536}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
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
    Protection(access = Access.nonPackageDuplicate),experiment(Algorithm=Dassl,Interval=0.001,StartTime=0,StopTime=3,Tolerance=1e-06),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={0,0}, 
points={{-100,60},{-100,-60},{100,-60},{100,60},{-100,60}}, 
color={255,255,255})}), 
Documentation(link = "modelica://TYMultibody/Resources/html/DoublePendulum.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="111", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, position=[0, 28, 2077, 1102], y=["bodyBox1.frame_a.r_0[1]", "bodyBox1.frame_a.r_0[2]", "bodyBox1.frame_a.r_0[3]"], x_display_unit="s", y_display_units=["m", "m", "m"], y_axis=[1, 1, 1], legend_layout=7, legend_frame=True, left_title="[m]", fix_time_range_value=6.95309e-310)})
})));
  inner TYMultibody.World world(enableAnimation = true) 
    annotation (Placement(transformation(origin = {-80.0, 4.10757946210269}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyBox bodyBox(r_OA_0(fixed = false), v_OA_0(fixed = false), angles_fixed = false) 
    annotation (Placement(transformation(origin = {1.9352745841762413, 4.381418092909538}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyBox bodyBox1(r_OA_0(fixed = false), v_OA_0(fixed = false), angles_fixed = false) 
    annotation (Placement(transformation(origin = {78.19204280736791, 4.381418092909536}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Rotational.Components.SpringDamper Rot_Stiff(c = 1000, d = 1) 
    annotation (Placement(transformation(origin = {40.0, -32.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(revolute.frame_a, world.frame_b) 
    annotation (Line(origin = {-52.0, 4.0}, 
      points = {{6.0, 0.0}, {-18.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute.frame_b, bodyBox.frame_a) 
    annotation (Line(origin = {-17.0, 4.0}, 
      points = {{-9.0, 0.0}, {9.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(bodyBox.frame_b, revolute1.frame_a) 
    annotation (Line(origin = {21.0, 4.0}, 
      points = {{-9.0, 0.0}, {9.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute1.frame_b, bodyBox1.frame_a) 
    annotation (Line(origin = {59.0, 4.0}, 
      points = {{-9.0, 0.0}, {9.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(Rot_Stiff.flange_b, revolute1.axis) 
    annotation (Line(origin = {49.0, -23.0}, 
      points = {{1.0, -9.0}, {10.0, -9.0}, {10.0, 17.0}, {-2.0, 17.0}}, 
      color = {0, 0, 0}));
  connect(Rot_Stiff.flange_a, revolute1.support) 
    annotation (Line(origin = {32.0, -23.0}, 
      points = {{-2.0, -9.0}, {-14.0, -9.0}, {-14.0, 17.0}, {1.0, 17.0}}, 
      color = {0, 0, 0}));
end DoublePendulum;