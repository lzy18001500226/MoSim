model PlanarFourQuadrilateralLinkage "四连杆机构"


  TYDriveline3D.Mechanisms.QuadrilateralLinkage quadrilateralLinkage(rotationType = .TYDriveline3D.Utilities.Type.RotationTypes.XYplane, om1 = 2) 
    annotation(Placement(transformation(origin = {16, 6}, 
    extent = {{-12, -10}, {12, 10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyCylinder crank(w_0_fixed = false, angles_fixed = false, r = {0, 0, -0.03}, lengthDirection = {0, 0, -1}, length(displayUnit = "mm") = 0.03, diameter = 0.6, innerDiameter(displayUnit = "mm") = 0.1, density(displayUnit = "kg/m3") = 7850) 
    annotation(Placement(transformation(origin = {-74, -0.2}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.FixedTranslation rod3(r = {0, 0, 0.015}) 
    annotation(Placement(transformation(origin = {-30, -0.2}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyBox link(r = quadrilateralLinkage.jointRRR1.rRod1_ia, width(displayUnit = "mm") = 0.1, height(displayUnit = "mm") = 0.03, density(displayUnit = "kg/m3") = 7850) 
    annotation(Placement(transformation(origin = {38, 44}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Parts.BodyBox rocker(r = quadrilateralLinkage.jointRRR1.rRod2_ib, width(displayUnit = "mm") = 0.1, height(displayUnit = "mm") = 0.03, density(displayUnit = "kg/m3") = 7850) 
    annotation(Placement(transformation(origin = {62, -0.3}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Sensors.AbsoluteAngularVelocity absoluteAngularVelocity(resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world) 
    annotation(Placement(transformation(origin = {-30, -34}, 
    extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-74, 60}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.MultiBody.Sensors.AbsoluteAngularVelocity absoluteAngularVelocity1(resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameA.world) 
    annotation(Placement(transformation(origin = {62, -34}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(rod3.frame_b, crank.frame_a) 
    annotation(Line(origin = {-44, 4}, 
    points = {{4, -4.2}, {-20, -4.2}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rod3.frame_a, quadrilateralLinkage.frame_a) 
    annotation(Line(origin = {-13, -12}, 
    points = {{-7, 11.8}, {17, 11.8}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(link.frame_a, quadrilateralLinkage.frame_b) 
    annotation(Line(origin = {38, 20}, 
    points = {{-10, 24}, {-34, 24}, {-34, -12.8}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rocker.frame_a, quadrilateralLinkage.frame_c) 
    annotation(Line(origin = {42, -3}, 
    points = {{10, 2.7}, {-14, 2.7}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(absoluteAngularVelocity.frame_a, rod3.frame_b) 
    annotation(Line(origin = {-39, -32}, 
    points = {{-1, -2}, {-1, 31.8}, {-1, 31.8}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(absoluteAngularVelocity1.frame_a, rocker.frame_a) 
    annotation(Line(origin = {52, -17}, 
    points = {{0, -17}, {-10, -17}, {-10, 16.7}, {0, 16.7}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {0, 27}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {0, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {0, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}), 
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2})), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/Mechanism/PlanarFourQuadrilateralLinkage.html"), 

    experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 5, Tolerance = 1e-06),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(1, 9)), 
Plot(y=["absoluteAngularVelocity.w[3]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-3, 2)), 
Plot(y=["absoluteAngularVelocity1.w[3]"], colors=["4278190335"])})
})));


end PlanarFourQuadrilateralLinkage;