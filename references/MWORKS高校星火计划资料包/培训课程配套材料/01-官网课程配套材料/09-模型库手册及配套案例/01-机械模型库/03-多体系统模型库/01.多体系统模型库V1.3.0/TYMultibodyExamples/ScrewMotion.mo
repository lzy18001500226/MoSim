model ScrewMotion "螺母螺旋运动"

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
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 10, Tolerance = 1e-06), 
    Protection(access = Access.nonPackageDuplicate), 
    Documentation(link = "modelica://TYMultibody/Resources/html/ScrewMotion.html"), 
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={-3,24}, 
points={{-101,62},{-101,-62},{101,-60},{101,62},{-101,62}}, 
color={255,255,255})}),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title="[m]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.5, 2)), 
Plot(y=["nut.frame_a.r_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[deg]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(-500, 0)), 
Plot(y=["screw.revolute.phi_rel"], colors=["4278190335"])})
})));

  inner TYMultibody.World world 
    annotation (Placement(transformation(origin = {-68.00000000000001, -6.000000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Screw screw(
                                 S = 0.2, n = {1, 0, 0}


                                                       ) 
    annotation (Placement(transformation(origin = {12.999999999999993, -6.000000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyCylinder Bolt(
                                       length = 1.6


                                                   ) 
    annotation (Placement(transformation(origin = {-27.50000000000001, -6.000000000000002}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyCylinder nut(
                                      length = 0.1, diameter = 0.5, r_OA_0(fixed = true), innerDiameter = 0.1, v_OA_0(start = {0, 0, 0}, fixed = false)


                                                                                                                                                       ) 
    annotation (Placement(transformation(origin = {53.5, -6.000000000000002}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));

  TYMultibody.Forces.BodyTorque bodyTorque(
                               useVariableTorque = true, T = {100, 0, 0}


                                                                        ) 
    annotation (Placement(transformation(origin = {32.0, 36.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression 
    annotation (Placement(transformation(origin = {-27.500000000000004, 35.99999999999999}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression realExpression1 
    annotation (Placement(transformation(origin = {-27.50000000000001, 22.000000000000007}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Blocks.Sources.Pulse pulse(
                                      offset = -15, amplitude = 20, width = 50, period = 10


                                                                                           ) 
    annotation (Placement(transformation(origin={-29.39830508474577,64.73446327683615}, 
extent={{-10,-10},{10,10}})));
equation
  connect(world.frame_b, Bolt.frame_a) 
    annotation (Line(origin = {-48.0, -6.0}, 
      points = {{-10.0, 0.0}, {10.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(Bolt.frame_b, screw.frame_a) 
    annotation (Line(origin = {-7.0, -6.0}, 
      points = {{-11.0, 0.0}, {10.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(screw.frame_b, nut.frame_a) 
    annotation (Line(origin = {33.0, -6.0}, 
      points = {{-10.0, 0.0}, {11.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(bodyTorque.frame_b, nut.frame_b) 
    annotation (Line(origin = {56.0, 22.0}, 
      points = {{-14.0, 14.0}, {16.0, 14.0}, {16.0, -28.0}, {8.0, -28.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(realExpression.y, bodyTorque.Ty_in) 
    annotation (Line(origin = {3.0, 56.00000000000001}, 
      points = {{-20.0, -20.0}, {19.0, -20.0}}, 
      color = {0, 0, 127}));
  connect(realExpression1.y, bodyTorque.Tz_in) 
    annotation (Line(origin={3,27}, 
points={{-19.50000000000001,-4.999999999999993},{19,-4.999999999999993},{19,5}}, 
color={0,0,127}));
  connect(pulse.y, bodyTorque.Tx_in) 
    annotation (Line(origin={3,60}, 
points={{-21.39830508474577,4.734463276836152},{13.305084745762713,4.734463276836152},{13.305084745762713,-20},{19,-20}}, 
color={0,0,127}));
end ScrewMotion;