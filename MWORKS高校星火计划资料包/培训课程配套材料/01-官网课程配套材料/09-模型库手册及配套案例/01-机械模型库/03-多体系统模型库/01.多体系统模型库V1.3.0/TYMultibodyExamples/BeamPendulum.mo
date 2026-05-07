model BeamPendulum "柔性梁的单摆对比"
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
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={-12,1}, 
points={{-98,49},{-98,-47},{98,-49},{98,47},{-98,49}}, 
color={255,255,255})}), 
    Documentation(link = "modelica://TYMultibody/Resources/html/BeamPendulum.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-8e-05, 8e-05)), 
Plot(y=["solidCylinderBeam.qe[1]", "solidCylinderBeam.qe[2]", "solidCylinderBeam.qe[3]"], colors=["4278190335", "4294901760", "4278222848"])})
}),ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.006,ContinueTimeVector)),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.001,StartTime=0,StopTime=3,Tolerance=1e-05));
  inner TYMultibody.World world 
    annotation (Placement(transformation(origin = {-76.0, -6.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute 
    annotation (Placement(transformation(origin = {-23.999999999999996, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation(
                                           r = {0, 0, 0.5}


                                                          ) 
    annotation (Placement(transformation(origin = {-22.0, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute1 
    annotation (Placement(transformation(origin = {8.0, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.FlexibleBeam.SolidCylinderBeam solidCylinderBeam(
                                                   beta = 0.01,ShapeColor={0,170,0}


                                                                                   ) 
    annotation (Placement(transformation(origin = {10.0, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyCylinder bodyCylinder 
    annotation (Placement(transformation(origin = {46.0, -30.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.RelativePosition relativePosition(
                                            resolveInFrame = TYMultibody.Types.ResolveInFrameAB.frame_b


                                                                                           ) 
    annotation (Placement(transformation(origin = {48.0, 18.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(rigidTranslation.frame_a, revolute.frame_a) 
    annotation (Line(origin = {-42.0, 38.0}, 
      points = {{10.0, -68.0}, {-6.0, -68.0}, {-6.0, -20.0}, {8.0, -20.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation.frame_b, revolute1.frame_a) 
    annotation (Line(origin = {-7.0, -30.0}, 
      points = {{-5.0, 0.0}, {5.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute.frame_b, solidCylinderBeam.frame_a) 
    annotation (Line(origin = {-7.0, 18.0}, 
      points = {{-7.0, 0.0}, {7.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute1.frame_b, bodyCylinder.frame_a) 
    annotation (Line(origin = {29.0, -30.0}, 
      points = {{-11.0, 0.0}, {7.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(solidCylinderBeam.frame_b, relativePosition.frame_a) 
    annotation (Line(origin = {29.0, 18.0}, 
      points = {{-9.0, 0.0}, {9.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(relativePosition.frame_b, bodyCylinder.frame_b) 
    annotation (Line(origin = {59.0, -6.0}, 
      points = {{-1.0, 24.0}, {10.0, 24.0}, {10.0, -24.0}, {-3.0, -24.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(world.frame_b, revolute.frame_a) 
    annotation (Line(origin = {-50.0, 6.0}, 
      points = {{-16.0, -12.0}, {2.0, -12.0}, {2.0, 12.0}, {16.0, 12.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
end BeamPendulum;