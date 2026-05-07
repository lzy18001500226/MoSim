model LiftLoadsSystem "空中拉升重物系统"
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={5.694915254237293,23.83615819209039}, 
lineColor={96,96,96}, 
fillColor={96,96,96}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={5.6949152542373005,-21.16384180790961}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5), Line(origin={5.694915254237308,-49.163841807909606}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5)}),experiment(Algorithm=Dassl,StartTime=0,StopTime=5,Tolerance=1e-06,InlineIntegrator=false,InlineStepSize=false,Interval=0.001), 
Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/RopeDrive/LiftLoadsSystem.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.556,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-2.2, -0.8)), 
Plot(y=["Loads.frame_a.r_0[2]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[deg]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-20, 140)), 
Plot(y=["sheave.phi"], colors=["4278190335"])})
})));
  TYDriveline3D.RopeDrive3D.FixedPreset Anchor(r = {0.5 , -1, 1}, 
    animation = true,UncLpre=-0.2,UseRopePort=true) 
    annotation (Placement(transformation(origin={-64.93596326267337,4.817602139745361}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Joints.Fixed fixed(r = {1, -0.5, 1}) 
    annotation (Placement(transformation(origin={-34.23939334182894,-33.18239786025463}, 
extent={{-10,-10},{10,10}})));
  Modelica.Mechanics.MultiBody.Parts.Body Loads(r_0(fixed = true, start = {1.50, -2, 1.01}), 
    v_0(fixed 
       = true), 
    angles_fixed = true, 
    a_0(start = {0, 0.0, 0}), 
    m = 10, 
    w_0_fixed = true,r_CM={0,0,0}) 
    annotation (Placement(transformation(origin={69.04720092320639,5.994226777145329}, 
extent={{-10,-10},{10,10}})));
  TYDriveline3D.RopeDrive3D.Sheave_Ideal sheave(
    phi0_a = 3.14159265358979,showRope=true,showTension=true) annotation (Placement(transformation(origin={4.189178086742494,4.817602139745361}, 
extent={{-10,-10},{10,10}})));
  TYDriveline3D.RopeDrive3D.RopesSMS rope1(diameter = 0.01,EA=100000) annotation (Placement(transformation(origin={-30.373392587965427,4.817602139745361}, 
extent={{-10,-10},{10,10}})));
  TYDriveline3D.RopeDrive3D.RopesSMS rope2(  usePreload = true, diameter = 0.01, d=50, EA=100000) annotation(Placement(transformation(origin = {38.930505866171515, 4.931473527324982}, 
extent={{-10,-10},{10,10}})));
  inner Modelica.Mechanics.MultiBody.World world 
    annotation (Placement(transformation(origin = {-70.000000, 40.000000}, extent = {{-10.000000, -10.000000}, {10.000000, 10.000000}})));
equation
  connect(sheave.frame_housing, fixed.frame_b) 
  annotation(Line(origin={-12.525107627543228,-19.18239786025464}, 
points={{16.714285714285722,14.200000000000003},{16.714285714285722,-13.999999999999993},{-11.714285714285708,-13.999999999999993}}, 
color={95,95,95}, 
thickness=0.5));
  connect(Anchor.frame_b, rope1.frame_a) 
  annotation(Line(origin={-47.52510762754323,4.817602139745361}, 
points={{-7.410855635130133,0},{7.151715039577802,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(rope1.frame_b, sheave.frame_a) 
  annotation(Line(origin={-12.525107627543228,4.817602139745361}, 
points={{-7.848284960422198,0},{6.714285714285722,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(sheave.frame_b, rope2.frame_a) 
  annotation(Line(origin={21.47489237245677,4.817602139745361}, 
points={{-7.285714285714278,0},{7.455613493714743,0},{7.455613493714743,0.11387138757962134}}, 
color={95,95,95}, 
thickness=0.5));
  connect(rope2.frame_b, Loads.frame_a) 
  annotation(Line(origin={58.47489237245677,4.817602139745361}, 
points={{-9.544386506285257,0.11387138757962134},{0.5723085507496108,0.11387138757962134},{0.5723085507496108,1.1766246373999678}}, 
color={95,95,95}, 
thickness=0.5));
  connect(rope1.RopePort_b, sheave.RopePort_a) 
  annotation(Line(origin={-13.210761433808877,12.015342252739714}, 
points={{-7.16263115415655,-0.197740112994353},{7.399939520551371,-0.197740112994353}}, 
color={0,0,0}));
  connect(sheave.RopePort_b, rope2.RopePort_a) 
  annotation(Line(origin={21.789238566191123,12.015342252739714}, 
points={{-7.600060479448629,-0.197740112994353},{7.141267299980392,-0.197740112994353},{7.141267299980392,-0.08386872541473167}}, 
color={0,0,0}));
  connect(Anchor.RopePort_b, rope1.RopePort_a) 
  annotation(Line(origin={-47.21076143380888,12.015342252739714}, 
points={{-7.725201828864485,-0.197740112994353},{6.83736884584345,-0.197740112994353}}, 
color={0,0,0}));
  end LiftLoadsSystem;