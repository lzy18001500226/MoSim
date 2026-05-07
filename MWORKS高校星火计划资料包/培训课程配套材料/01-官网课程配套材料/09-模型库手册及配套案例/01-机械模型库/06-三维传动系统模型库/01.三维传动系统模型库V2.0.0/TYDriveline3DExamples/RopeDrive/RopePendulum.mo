model RopePendulum "绳摆系统"
  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-65.51834651493952, 2.183453095810128}, 
    extent = {{-10, -10}, {10, 10}})));

  TYDriveline3D.RopeDrive3D.RopesSMS ropesSMS(noM = 3) 
    annotation(Placement(transformation(origin = {13.536723163841813, 12.971751412429384}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.CableMSM cableMSM(noM = 3) 
    annotation(Placement(transformation(origin = {12.371368494550474, -16.256594556074553}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.CableSpring cableSpring(UnloadedL0 = 1) 
    annotation(Placement(transformation(origin = {12.97175128248588, 44.61016937288135}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.RopeDrive3D.RopeSpring ropeSpring 
    annotation(Placement(transformation(origin = {14.304299248572526, -44.293331384276094}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Bodies.PointMass pointMass(r_0(start = {1, 0, 0}, fixed = true), m = 10) 
    annotation(Placement(transformation(origin = {59.70854438983051, 44.93379841242938}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Bodies.PointMass pointMass1(r_0(start = {1, 0, 0}, fixed = true), m = 10) 
    annotation(Placement(transformation(origin = {59.476935593220304, 12.740142372881365}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Bodies.PointMass pointMass2(r_0(start = {1, 0, 0}, fixed = true), m = 10) 
    annotation(Placement(transformation(origin = {59.24532685875708, -16.210987887005654}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Bodies.PointMass pointMass3(r_0(start = {1, 0, 0}, fixed = true), m = 10) 
    annotation(Placement(transformation(origin = {60.17176259887006, -44.93050818079095}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(cableMSM.frame_a, world.frame_b) 
    annotation(Line(origin = {-8.463276836158187, -2.0282485875706158}, 
    points = {{10.83464533070866, -14.228345968503938}, {-36.622981787935416, -14.228345968503938}, {-36.622981787935416, 4.211701683380744}, {-47.05506967878134, 4.211701683380744}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropeSpring.frame_a, world.frame_b) 
    annotation(Line(origin = {-7.463276836158187, -16.028248587570616}, 
    points = {{11.767576084730713, -28.265082796705478}, {-37.57627118644068, -28.265082796705478}, {-37.57627118644068, 18.211701683380745}, {-48.05506967878134, 18.211701683380745}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cableSpring.frame_a, world.frame_b) 
    annotation(Line(origin = {-25.463276836158187, 19.971751412429384}, 
    points = {{28.435028118644066, 24.638417960451967}, {-19.762355430171283, 24.638417960451967}, {-19.762355430171283, -17.788298316619255}, {-30.055069678781337, -17.788298316619255}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropesSMS.frame_a, world.frame_b) 
    annotation(Line(origin = {-26.463276836158187, 10.971751412429384}, 
    points = {{30, 2}, {-18.707460717177895, 2}, {-18.707460717177895, -8.788298316619256}, {-29.055069678781337, -8.788298316619256}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cableSpring.frame_b, pointMass.frame_a) 
    annotation(Line(origin = {36.53672316384181, 44.971751412429384}, 
    points = {{-13.564971881355934, -0.3615820395480327}, {13.171821225988694, -0.3615820395480327}, {13.171821225988694, -0.03795300000000168}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(ropesSMS.frame_b, pointMass1.frame_a) 
    annotation(Line(origin = {36.53672316384181, 13.971751412429384}, 
    points = {{-13, -1}, {12.94021242937849, -1}, {12.94021242937849, -1.2316090395480188}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(cableMSM.frame_b, pointMass2.frame_a) 
    annotation(Line(origin = {35.53672316384181, -16.028248587570616}, 
    points = {{-13.16535466929134, -0.2283459685039375}, {13.708603694915269, -0.2283459685039375}, {13.708603694915269, -0.1827392994350383}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(pointMass3.frame_a, ropeSpring.frame_b) 
    annotation(Line(origin = {37.53672316384181, -43.028248587570616}, 
    points = {{12.635039435028247, -1.9022595932203359}, {-13.232423915269287, -1.9022595932203359}, {-13.232423915269287, -1.265082796705478}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));

  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
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
    Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, grid = {2, 2})), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/RopePendulum.html"), 
    experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 0.0001),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-1.5, 1.5)), 
Plot(y=["pointMass.r_0[1]", "pointMass1.r_0[1]", "pointMass2.r_0[1]", "pointMass3.r_0[1]"], colors=["4278190335", "4294901760", "4278222848", "4294902015"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-1.2, 0.2)), 
Plot(y=["pointMass.r_0[2]", "pointMass1.r_0[2]", "pointMass2.r_0[2]", "pointMass3.r_0[2]"], colors=["4278190335", "4294901760", "4278222848", "4294902015"])})
})));

end RopePendulum;