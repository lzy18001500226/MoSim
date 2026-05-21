model BalanceBall "平衡球运动模型"
  inner Modelica.Mechanics.MultiBody.World world(axisColor_x = {0, 0, 255}, axisColor_y = {0, 255, 0}, axisColor_z = {255, 0, 0}) 

    annotation(Placement(transformation(origin = {-90, -1}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyShape surface(lengthDirection = {1, 0, 0}, length = 1, width = 1, height = 0.01, color = {255, 255, 0}, extra = 1, animateSphere = false, m = 78.01, I_33 = 6.5014834167, 
    I_11 = 13.0016666667, I_22 = 6.5014834167, 
    shapeType = "box", r_0(fixed = false), 
    widthDirection = {0, 0, 1}, r_shape = {-0.5, 0, 0}) 
    annotation(Placement(transformation(origin = {4, -24}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute1(useAxisFlange = true, 
    animation = false) annotation(Placement(transformation(origin = {-18.8, -1}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Mechanics.MultiBody.Joints.Revolute revolute2(useAxisFlange = false, 
    animation = false, 
    n = {1, 0, 0}) 
    annotation(Placement(transformation(origin = {-54.4, -1}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMechanics.Rotational.Sources.AngleVelocity angleVelocity 
    annotation(Placement(transformation(origin = {-54.4, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyShape sphere(lengthDirection = {1, 0, 0}, length = 0.04, width = 0.04, height = 0.04, color = {255, 0, 0}, animateSphere = false, m = 0.2614140191, I_33 = 4.1826243056E-05, 
    I_11 = 4.1826243056E-05, I_22 = 4.1826243056E-05, 
    shapeType = "sphere", r_0(fixed = true, start 
    = {0, 0.02, 0}), 
    r_shape = {-0.02, 0, 0}, 
    v_0(fixed = false
    )) 

    annotation(Placement(transformation(origin = {75.2, -1}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYContact.PointContact.SpherePolygon_Contact spherePolygon_Contact(Points = {{0.5, 0, 0.5}, {0.5, 0, -0.5}, {-0.5, 0, -0.5}, {-0.5, 0, 0.5}}, k = 1e7, d = 1e4, v_e1 = 0.01, v_e2 = 1, mue_s = 0.2, mue_k = 0.1, h = 0.005, n1 = 1.5, R1 = 0.02) 
    annotation(Placement(transformation(origin = {30, -1}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Sensors.AbsoluteSensor absoluteSensor(resolveInFrame = TYMultibody.Types.ResolveInFrameA.world) 
    annotation(Placement(transformation(origin = {84, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.CombiTimeTable combiTimeTable(table = {{0.0, 0.0}, {0.5, 0.02}, {1, 0.02}, {1.5, 0}, {2, -0.04}, {2.5, -0.02}, {3, 0}, {3.5, -0.02}, {4, -0.04}, {4.5, 0}, {5, 0.04}, {5.5, 0.02}, {6, 0}}, smoothness = Modelica.Blocks.Types.Smoothness.ContinuousDerivative) 
    annotation(Placement(transformation(origin = {-90, -40}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(world.frame_b, revolute2.frame_a) 
    annotation(Line(origin = {-92, -1}, 
    points = {{12, 0}, {27.6, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(revolute2.frame_b, revolute1.frame_a) 
    annotation(Line(origin = {-54, -1}, 
    points = {{9.6, 0}, {25.2, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(revolute1.frame_b, surface.frame_a) 
    annotation(Line(origin = {4, -1}, 
    points = {{-12.8, 0}, {0, 0}, {0, -13}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(angleVelocity.flange, revolute1.axis) 
    annotation(Line(origin = {-32, -31}, 
    points = {{-12.4, -9}, {13.2, -9}, {13.2, 20}}, 
    color = {0, 0, 0}));
  connect(spherePolygon_Contact.frame_b, sphere.frame_a) 
    annotation(Line(origin = {52.6, -1}, 
    points = {{-12.6, 0}, {12.6, 0}}, 
    color = {0, 0, 0}));
  connect(absoluteSensor.frame_a, sphere.frame_a) 
    annotation(Line(origin = {69.6, -21}, 
    points = {{4.4, -19}, {-4.4, -19}, {-4.4, 20}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(spherePolygon_Contact.frame_a, revolute1.frame_b) 
    annotation(Line(origin = {6, -1}, 
    points = {{14, 0}, {-14.8, 0}}, 
    color = {0, 0, 0}));
  connect(combiTimeTable.y[1], angleVelocity.om_ref) 
    annotation(Line(origin = {-72, -60}, 
    points = {{-7, 20}, {7.6, 20}}, 
    color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 6, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 6, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[deg]", fix_time_range_value=0, zoom_x=(0, 6), zoom_y_l=(-2.5, 1.5)), 
Plot(y=["angleVelocity.phi"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 6), zoom_y_l=(-1, 6)), 
Plot(y=["spherePolygon_Contact.Fp[2]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N.m]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 6), zoom_y_l=(-0.2, 1.4)), 
Plot(y=["spherePolygon_Contact.Tfp[3]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 6), zoom_y_l=(-0.5, 0.1)), 
Plot(y=["absoluteSensor.r[1]"], colors=["4278190335"])})
})), Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={-3.55271e-15,31}, 
lineColor={96,96,96}, 
fillColor={96,96,96}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={-3.55271e-15,-14}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5), Line(origin={-3.55271e-15,-42}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5)}), 
    Documentation(link = "modelica://TYContact/Resources/HTML/Examples/BalanceBall.html"),Protection(access=Access.nonPackageDuplicate));

end BalanceBall;