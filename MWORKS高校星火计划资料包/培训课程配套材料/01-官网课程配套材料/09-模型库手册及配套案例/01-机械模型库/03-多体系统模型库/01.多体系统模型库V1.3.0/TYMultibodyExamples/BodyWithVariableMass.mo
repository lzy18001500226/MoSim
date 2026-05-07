model BodyWithVariableMass "变质量刚体"



  Modelica.Blocks.Sources.RealExpression dIxx(y = 0.001) 
    annotation (Placement(transformation(origin={-16.04302548663825,-25.833792837919717}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dIyy(y = 0.002) 
    annotation (Placement(transformation(origin={-15.999999999999998,-40}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dIzz(y = 0.003) 
    annotation (Placement(transformation(origin={-15.97830304242895,-54.11833911889339}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dIxy(y = 0) 
    annotation (Placement(transformation(origin={12.079741593302323,-25.7701913323112}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dyz(y = 0) 
    annotation (Placement(transformation(origin={12.076912385028116,-39.84607130195124}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dxz(y = 0) 
    annotation (Placement(transformation(origin={12.226908879179994,-54.12124741374325}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dvx(y = 0) 
    annotation (Placement(transformation(origin={44.49353838159908,50.41256393218667}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dvy(y = 0.3) 
    annotation (Placement(transformation(origin={44.40392754457805,36.15195843210073}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression dvz(y = 0) 
    annotation (Placement(transformation(origin={44.485819784664486,21.43947607870317}, 
extent={{-10,-10},{10,10}})));
  inner TYMultibody.World world(n = {0, 0, -1}) 
    annotation (Placement(transformation(origin={-66.30392888902139,-1.9125652139156628}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Joints.Cylindrical cylindrical(n = {0, 1, 0}, phi_rel_0 = 0, s_rel_0 = 0) 
    annotation (Placement(transformation(origin={-33.08664971429526,-0.9497455276918174}, 
extent={{-10,-10},{10,10}})));
  TYMultibody.Bodies.BodyVariable bodyVariable(r_AG_a = {0.5, 0, 0}, r_AB_a = {1, 0, 0}, m(start = 1), Ixx(start = 0.1), Iyy(start = 0.1), Izz(start = 0.1), Ixy(start = 0), Ixz(start = 0), Iyz(start = 0), r_OA_0(start = {0, 0, 0}, 
    fixed 
     = true), angles_fixed = false, angles_startDeg = {0, 0, 0}, v_OA_0(start = {0, 0, 0}, 
      fixed 
       = true), 
    ShowShape = true) annotation (Placement(transformation(origin={36.524740515666316,-0.801658784479006}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Sine sine(amplitude = 0.8, 
    phase = 0.523598775598299,f=1) annotation (Placement(transformation(origin={1.3644384764018511,20.73197417812897}, 
extent={{-10,-10},{10,10}})));
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
    Documentation(link = "modelica://TYMultibody/Resources/html/BodyWithVariableMass.html"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Dassl,Interval=0.001,StartTime=0,StopTime=3,Tolerance=1e-06),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.03,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-1, 1)), 
Plot(y=["bodyVariable.mdot_in"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[kg.m2]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(0.098, 0.112)), 
Plot(y=["bodyVariable.Ixx", "bodyVariable.Iyy", "bodyVariable.Izz"], colors=["4278190335", "4294901760", "4278222848"])})
})));
equation
  connect(world.frame_b, cylindrical.frame_a) 
    annotation (Line(origin={-49.46232132400961,-1.022171919267091}, 
points={{-6.841607565011785,-0.8903932946485718},{6.375671609714345,-0.8903932946485718},{6.375671609714345,0.07242639157527364}}, 
color={95,95,95}, 
thickness=0.5));

  connect(dvz.y, bodyVariable.v_g_in[3]) 
    annotation (Line(origin={53.23253046510685,13.1310222108301}, 
points={{2.253289319557638,8.30845386787307},{7,8.30845386787307},{7,-7.932680995309106},{-6.707789949440524,-7.932680995309106}}, 
color={0,0,127}));
  connect(dvy.y, bodyVariable.v_g_in[2]) 
    annotation (Line(origin={53.23253046510685,21.1310222108301}, 
points={{2.1713970794712054,15.020936221270627},{7,15.020936221270627},{7,-15.932680995309106},{-6.707789949440524,-15.932680995309106}}, 
color={0,0,127}));
  connect(dvx.y, bodyVariable.v_g_in[1]) 
    annotation (Line(origin={53.23253046510685,28.1310222108301}, 
points={{2.2610079164922325,22.28154172135657},{7,22.28154172135657},{7,-22.932680995309106},{-6.707789949440524,-22.932680995309106}}, 
color={0,0,127}));
  connect(dIxx.y, bodyVariable.Idot_in[1]) 
    annotation (Line(origin={11.232530465106848,-15.8689777891699}, 
points={{-16.275555951745098,-9.964815048749816},{-12,-9.964815048749816},{-12,9.067319004690894},{15.292210050559468,9.067319004690894}}, 
color={0,0,127}));
  connect(dIyy.y, bodyVariable.Idot_in[2]) 
    annotation (Line(origin={11.232530465106848,-22.8689777891699}, 
points={{-16.232530465106848,-17.1310222108301},{-12,-17.1310222108301},{-12,16.067319004690894},{15.292210050559468,16.067319004690894}}, 
color={0,0,127}));
  connect(dIzz.y, bodyVariable.Idot_in[3]) 
    annotation (Line(origin={10.232530465106848,-30.8689777891699}, 
points={{-15.210833507535797,-23.249361329723488},{-11,-23.249361329723488},{-11,24.067319004690894},{16.29221005055947,24.067319004690894}}, 
color={0,0,127}));
  connect(dIxy.y, bodyVariable.Idot_in[4]) 
    annotation (Line(origin={25.232530465106848,-16.8689777891699}, 
points={{-2.1527888718045247,-8.9012135431413},{0,-8.9012135431413},{0,10.067319004690894},{1.2922100505594685,10.067319004690894}}, 
color={0,0,127}));
  connect(dyz.y, bodyVariable.Idot_in[5]) 
    annotation (Line(origin={25.232530465106848,-23.8689777891699}, 
points={{-2.1556180800787317,-15.977093512781341},{0,-15.977093512781341},{0,17.067319004690894},{1.2922100505594685,17.067319004690894}}, 
color={0,0,127}));
  connect(dxz.y, bodyVariable.Idot_in[6]) 
    annotation (Line(origin={25.232530465106848,-29.8689777891699}, 
points={{-2.0056215859268534,-24.252269624573348},{0,-24.252269624573348},{0,23.067319004690894},{1.2922100505594685,23.067319004690894}}, 
color={0,0,127}));
  connect(cylindrical.frame_b, bodyVariable.frame_a) 
    annotation (Line(origin={1.2325304651068478,0.1310222108300998}, 
points={{-24.319180179402114,-1.0807677385219172},{25.29221005055947,-1.0807677385219172},{25.29221005055947,-0.9326809953091058}}, 
color={95,95,95}, 
thickness=0.5));
  connect(sine.y, bodyVariable.mdot_in) 
    annotation (Line(origin={19.232530465106848,13.1310222108301}, 
points={{-6.868091988704997,7.600951967298869},{7.2922100505594685,7.600951967298869},{7.2922100505594685,-7.932680995309106}}, 
color={0,0,127}));
end BodyWithVariableMass;