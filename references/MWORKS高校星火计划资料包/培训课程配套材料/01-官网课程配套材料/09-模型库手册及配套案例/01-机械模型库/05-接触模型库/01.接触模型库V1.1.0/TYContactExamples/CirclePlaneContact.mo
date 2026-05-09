model CirclePlaneContact "平面多物体碰撞"
  inner TYMultibody.World world(gravityType=TYMultibody.Types.GravityTypes.NoGravity) 
    annotation(Placement(transformation(origin={-68,-14}, 
extent={{-10,-10},{10,10}})));
  TYContact.PlaneContact.CircleCircle_Contact circleToCircle(k=1e6,p_max=1e-4) 
    annotation(Placement(transformation(origin={17.5501,34}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body circle1(v_OA_0(start = {0, 0.1, 0}, fixed = true), lengthDirection = {0, 0, 1},     length = 0.2, width = 0.1, r_shape = {0, 0, -0.1},ShapeColor={255,255,0}) 
    annotation(Placement(transformation(origin={-32,34}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body circle2(v_OA_0(start = {0, 0, 0}, fixed = true), lengthDirection = {0, 0, 1},     length = 0.2, width = 0.1, r_shape = {0, 0, -0.1},r_OA_0(start={0, 0.2, 0}),ShapeColor={255,170,0}) 
    annotation(Placement(transformation(origin={67.1002,34}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body circle3(v_OA_0( fixed = true,start={0.1, 0, 0}), lengthDirection = {0, 0, 1},     length = 0.2, width = 0.1, r_shape = {0, 0, -0.1},r_OA_0(start={-0.1, 0.1, 0})) 
    annotation(Placement(transformation(origin={67.1002,-14}, 
extent={{-10,-10},{10,10}})));
  TYContact.PlaneContact.CircleCircle_Contact circleToCircle1(k=1e6,p_max=1e-4) 
    annotation(Placement(transformation(origin={17.5501,-14}, 
extent={{-10,-10},{10,10}})));
  TYContact.PlaneContact.CircleCircle_Contact circleToCircle2(k=1e6,p_max=1e-4) 
    annotation(Placement(transformation(origin={116.65,34}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.RigidTransform rigidTransform(rotationType = TYMultibody.Types.RotationTypes.PlanarRotationSequence,r={0.1, 0.1, 0}  ) 
    annotation(Placement(transformation(origin={-32,-88}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body circle4(v_OA_0( fixed = true,start={0.1, 0, 0}), lengthDirection = {0, 0, 1},     length = 0.2, width = 0.1, r_shape = {0, 0, -0.1},r_OA_0(start={-0.1, 0.1, 0}),ShapeColor={203,203,203}) 
    annotation(Placement(transformation(origin={67.1002,-88}, 
extent={{-10,-10},{10,10}})));
  TYContact.PlaneContact.CircleCircle_Contact circleToCircle3(k=1e6,p_max=1e-4) 
    annotation(Placement(transformation(origin={17.5501,-46}, 
extent={{-10,-10},{10,10}})));
equation
  annotation(experiment(StartTime=0,StopTime=5,Algorithm=Dassl,IntegratorStep=0.0001,Tolerance=1e-06,Interval=0.001), Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=5,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-0.02, 0.12)), 
Plot(y=["circle2.frame_a.r_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-0.15, 0.1)), 
Plot(y=["circle3.frame_a.r_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 5), zoom_y_l=(-35, 5)), 
Plot(y=["circleToCircle3.F[1]", "circleToCircle3.F[2]"], colors=["4278190335", "4294901760"])})
})),Protection(access=Access.nonPackageDuplicate));
  annotation(Documentation(link = "modelica://TYContact/Resources/HTML/Examples/CirclePlaneContact.html"), 
  Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={0,31}, 
lineColor={96,96,96}, 
fillColor={96,96,96}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={0,-14}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5), Line(origin={0,-42}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5)}));
  connect(circleToCircle.frame_a, circle1.frame_b) 
  annotation(Line(origin={-12,34}, 
points={{19.5501,0},{-10,0}}, 
color={0,0,0}));
  connect(circleToCircle.frame_b, circle2.frame_a) 
  annotation(Line(origin={34,34}, 
points={{-6.4499,0},{23.1002,0}}, 
color={0,0,0}));
  connect(circle1.frame_b, circleToCircle1.frame_a) 
  annotation(Line(origin={-7,10}, 
points={{-15,24},{1,24},{1,-24},{14.5501,-24}}, 
color={95,95,95}, 
thickness=0.5));
  connect(circleToCircle1.frame_b, circle3.frame_a) 
  annotation(Line(origin={42,-14}, 
points={{-14.4499,0},{15.1002,0}}, 
color={0,0,0}));
  connect(circle2.frame_b, circleToCircle2.frame_a) 
  annotation(Line(origin={107,34}, 
points={{-29.8998,0},{-0.3497,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(circleToCircle2.frame_b, circle3.frame_b) 
  annotation(Line(origin={127,10}, 
points={{-0.3497,24},{17,24},{17,-24},{-49.8998,-24}}, 
color={0,0,0}));
  connect(world.frame_b, rigidTransform.frame_a) 
  annotation(Line(origin={-68,-40}, 
points={{10,26},{18,26},{18,-48},{26,-48}}, 
color={95,95,95}, 
thickness=0.5));
  connect(rigidTransform.frame_b, circle4.frame_a) 
  annotation(Line(origin={18,-88}, 
points={{-40,0},{39.1002,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(circle1.frame_b, circleToCircle3.frame_a) 
  annotation(Line(origin={-7,-6}, 
points={{-15,40},{1,40},{1,-40},{14.5501,-40}}, 
color={95,95,95}, 
thickness=0.5));
  connect(circleToCircle3.frame_b, circle4.frame_b) 
  annotation(Line(origin={69,-67}, 
points={{-41.4499,21},{41,21},{41,-21},{8.1002,-21}}, 
color={0,0,0}));
  end CirclePlaneContact;