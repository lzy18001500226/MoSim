model RotationlWheel "车轮滚动"
  annotation(Documentation(link = "modelica://TYContact/Resources/HTML/Examples/RotationlWheel.html"), 

  Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,StartTime=0,StopTime=5,Tolerance=1e-06,Interval=0.001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=5,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[rad/s]", fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-12, -2)), 
Plot(y=["body1.om_a[3]", "body2.om_a[3]"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m/s]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-0.1, 0.6)), 
Plot(y=["body1.v_OA_0[1]", "body2.v_OA_0[1]"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, sub_plot=(3, 1), zoom_x=(0, 5), zoom_y_l=(-8, 2)), 
Plot(y=["sphereLine_Contact.Ff[1]", "sphereLine_Contact1.Ff[1]"], colors=["4278190335", "4294901760"])})
})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={0,21}, 
lineColor={96,96,96}, 
fillColor={96,96,96}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={0,-24}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5), Line(origin={0,-52}, 
points={{-62,18},{0,-18},{62,18}}, 
color={96,96,96}, 
thickness=5)}),Protection(access=Access.nonPackageDuplicate));
  Modelica.Mechanics.MultiBody.Parts.Fixed fixed(r={-2.5,0,0},animation=false) 
    annotation (Placement(transformation(origin={-74,-22}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body body(r_OA_0(fixed=true),shapeType="box", lengthDirection = {1, 0, 0}, length = 5, width = 1, height = 0.2, widthDirection = {0, 0, 1}, r_AB_a = {2.5, 0, 0}) 
    annotation (Placement(transformation(origin={-32,-22}, 
extent={{-10,-10},{10,10}})));
  inner TYMultibody.World world(gravityType=TYMultibody.Types.GravityTypes.UniformGravity) 
    annotation (Placement(transformation(origin={-74,38}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body body1(shapeType="cylinder", width = 0.3, height = 0.3, length = 0.1, lengthDirection = {0, 0, 1}, om_0_fixed = true,  r_OA_0(fixed = true, start = {-2, 0.25, 0}), m = 3.5342917353, Ixx = 2.2825634124E-02, Iyy = 2.2825634124E-02, Izz = 3.9760782022E-02,useQuaternions=true,enforceStates=false,sequence_angleStates={1, 2, 3},r_shape={0, 0, -0.05},om_0_start={0, 0, -10}) 
    annotation (Placement(transformation(origin={52,-22}, 
extent={{-10,-10},{10,10}})));
  TYContact.PointContact.SphereLine_Contact sphereLine_Contact(R1=0.15,R2=0.1,Points={{-2.5, 0, 0}, {2.5, 0, 0}},mue_k=0.1,mue_r=0,k=1e7,d=1e4,p_max=0.0001,v_e2=0.1,mue_s=0.2) 
    annotation (Placement(transformation(origin={6,-22}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.Body body2(shapeType="cylinder", width = 0.3, height = 0.3, length = 0.1, lengthDirection = {0, 0, 1}, om_0_fixed = true,  r_OA_0(fixed = true, start = {-1, 0.25, 0}), m = 3.5342917353, Ixx = 2.2825634124E-02, Iyy = 2.2825634124E-02, Izz = 3.9760782022E-02,useQuaternions=true,enforceStates=false,sequence_angleStates={1, 2, 3},r_shape={0, 0, -0.05},om_0_start={0, 0, -10}) 
    annotation (Placement(transformation(origin={52,-62}, 
extent={{-10,-10},{10,10}})));
  TYContact.PointContact.SphereLine_Contact sphereLine_Contact1(R1=0.15,R2=0.1,Points={{-2.5, 0, 0}, {2.5, 0, 0}},mue_k=0.1,mue_r=0,k=1e7,d=1e4,p_max=0.0001,v_e2=0.1,mue_s=0.2) 
    annotation (Placement(transformation(origin={6,-62}, 
extent={{-10,-10},{10,10}})));
  equation
  connect(fixed.frame_b, body.frame_a) 
  annotation(Line(origin={-53,-22}, 
points={{-11,0},{11,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(body.frame_b, sphereLine_Contact.frame_a) 
  annotation(Line(origin={-13,-22}, 
points={{-9,0},{9,0}}, 
color={95,95,95}, 
thickness=0.5));
  connect(sphereLine_Contact.frame_b, body1.frame_a) 
  annotation(Line(origin={29,-22}, 
points={{-13,0},{13,0}}, 
color={0,0,0}));
  connect(sphereLine_Contact1.frame_b, body2.frame_a) 
  annotation(Line(origin={29,-62}, 
points={{-13,0},{13,0}}, 
color={0,0,0}));
  connect(sphereLine_Contact1.frame_a, body.frame_b) 
  annotation(Line(origin={-13,-42}, 
  points={{9,-20},{-9,-20},{-9,20}}, 
  color={0,0,0}));
  end RotationlWheel;