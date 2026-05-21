model BeamWithMass "悬挂质量的悬臂梁"
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
    Documentation(link = "modelica://TYMultibody/Resources/html/BeamWithMass.html"), 
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={-5,9}, 
points={{-89,47},{-89,-47},{89,-47},{89,47},{-89,47}}, 
color={255,255,255})}),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="555", executeTrigger=executeTrigger.SimulationStarted, commands={
CreatePlot(id=1, position=[0, 28, 1036, 619], y=["solidRectangleBeam.qe[2]"], x_display_unit="s", y_axis=[1], legend_layout=7, legend_frame=True, fix_time_range_value=6.95309e-310)})
}),ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.006,ContinueTimeVector)),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.001,StartTime=0,StopTime=3,Tolerance=1e-05));
  inner TYMultibody.World world 
    annotation (Placement(transformation(origin={-43.99999999999999,0}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.FlexibleBeam.SolidRectangleBeam solidRectangleBeam 
    annotation (Placement(transformation(origin={-2,0}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.PointMass pointMass(
                             m = 100








                                    ) 
    annotation (Placement(transformation(origin={38,0}, 
extent={{-10,-10},{10,10}})));
equation
  connect(world.frame_b, solidRectangleBeam.frame_a) 
    annotation (Line(origin={-27,0}, 
points={{-6.999999999999993,0},{15,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(solidRectangleBeam.frame_b, pointMass.frame_a) 
    annotation (Line(origin={18,0}, 
points={{-10,0},{10,0}}, 
color={95,95,95}, 
thickness=0.5));
end BeamWithMass;