model AdiabaticChamber "绝热腔室"
  annotation (Documentation(link = "modelica://TYPneumaticComponents/Resources/HTML/AdiabaticChamber.html"), Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Polygon(origin={-7.105427357601002e-15,33}, 
lineColor={0,98,98}, 
fillColor={0,98,98}, 
fillPattern=FillPattern.Solid, 
points={{-64,1},{0,37},{64,1},{0,-37}}), Line(origin={0,-12}, 
points={{-62,18},{0,-18},{62,18}}, 
color={0,98,98}, 
thickness=5), Line(origin={7.105427357601002e-15,-39.99999999999999}, 
points={{-62,18},{0,-18},{62,18}}, 
color={0,98,98}, 
thickness=5)}), 
    experiment(Algorithm = Dassl, Interval = 0.01, StartTime = 0, StopTime = 1, Tolerance = 1e-05), 
    Diagram(coordinateSystem(extent={{-180,-100},{180,100}}, 
grid={2,2}),graphics = {Text(origin={17.99999999999997,50.999999999999986}, 
lineColor={0,0,0}, 
extent={{-18,7},{18,-7}}, 
textString="闭腔", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={17.99999999999997,-44.000000000000014}, 
lineColor={0,0,0}, 
extent={{-18,7},{18,-7}}, 
textString="开腔", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-127.16923845193506,56.999999999999986}, 
lineColor={0,0,0}, 
extent={{-18,7},{18,-7}}, 
textString="闭腔", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-127.16923845193506,-38}, 
lineColor={0,0,0}, 
extent={{-18,7},{18,-7}}, 
textString="开腔", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-87.99999999999999,83}, 
lineColor={0,0,0}, 
extent={{-36,7},{36,-7}}, 
textString="多变模式", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={73.99999999999994,78.99999999999997}, 
lineColor={0,0,0}, 
extent={{-36,7},{36,-7}}, 
textString="热交换模式", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s ", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(-0.02, 0.1)), 
Plot(y=["gasVolumeV.p", "gasVolumeV1.p"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 1), zoom_y_l=(0, 300)), 
Plot(y=["gasVolume.T_A", "gasVolume1.T_A"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="温度/degC", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 1), zoom_y_l=(18, 28)), 
Plot(y=["gasVolumeV.T", "gasVolumeV1.T"], colors=["4278190335", "4294901760"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="压力/Bar", bottom_title_type=2, bottom_title="时间/s
", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 1), zoom_y_l=(-2, 12)), 
Plot(y=["gasVolume.pA", "gasVolume1.pA"], colors=["4278190335", "4294901760"])})
})));
  Modelica.Mechanics.Translational.Sources.Position position1(
                                                              f_crit = 10000
                                                                            ) 
    annotation (Placement(transformation(origin={73.99999999999994,19.999999999999993}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV1(
                                                           V0(displayUnit = "l") = 0.001, 
    T(start = 293), Text = 293.15
                                 ) 
    annotation (Placement(transformation(origin={115.16923845193506,-3.9999999999999964}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Sources.ZeroFlowSource zeroFlowSource1 
    annotation (Placement(transformation(origin={115.16923845193506,-28.000000000000007}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp ramp1(
                                     duration = 1
                                                 ) 
    annotation (Placement(transformation(origin={37.99999999999997,20.000000000000007}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Sources.MHFlowSource mHFlowSource1(
                                                           constantMassflow = 0.005, constantTemperature = 293
                                                                                                              ) 
    annotation (Placement(transformation(origin={45.41538077403243,-71.07845303867404}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Auxiliaries.GasVolume gasVolume1(
                                                         Tin(start = 293), Text = 293.15,Model="Thermal Exchange Model"
                                                                                                                       ) 
    annotation (Placement(transformation(origin={83.99999999999994,-71}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYPneumaticComponents.Sources.ZeroFlowSource zeroFlowSource3 
    annotation (Placement(transformation(origin={122.58461922596749,-71.07845303867404}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston1(
                                                                 reverse = true
                                                                               ) 
    annotation (Placement(transformation(origin={110,19.999999999999993}, 
extent={{10,-10},{-10,10}})));
  Modelica.Mechanics.Translational.Sources.Position position(f_crit=10000) 
    annotation (Placement(transformation(origin={-71.16923845193513,25.999999999999993}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Auxiliaries.GasVolumeV gasVolumeV(
                                     V0(displayUnit = "l") = 0.001, 
    T(start = 293), Text = 293.15,Model="Polytropic Model", kpoly = 1.4
                                                                       ) 
    annotation (Placement(transformation(origin={-30,2.0000000000000018}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Sources.ZeroFlowSource zeroFlowSource 
    annotation (Placement(transformation(origin={-30,-22.000000000000014}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp ramp(
                                     duration = 1
                                                ) 
    annotation (Placement(transformation(origin={-107.16923845193506,26.000000000000007}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Sources.MHFlowSource mHFlowSource(
                                     constantMassflow = 0.005, constantTemperature = 293
                                                                                       ) 
    annotation (Placement(transformation(origin={-99.75385767790263,-65.07845303867403}, 
extent={{-10,-10},{10,10}})));
  TYPneumaticComponents.Auxiliaries.GasVolume gasVolume(
                                   Tin(start = 293), Text = 293.15,Model="Polytropic Model", kpoly = 1.4
                                                                                                       ) 
    annotation (Placement(transformation(origin={-61.16923845193513,-64.99999999999999}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYPneumaticComponents.Sources.ZeroFlowSource zeroFlowSource2 
    annotation (Placement(transformation(origin={-22.58461922596757,-65.07845303867403}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  TYPneumaticComponents.Pistons.FixedBodyPiston fixedBodyPiston(
                                           reverse = true,InterfaceSwitch=false
                                                                              ) 
    annotation (Placement(transformation(origin={-35.16923845193506,25.999999999999993}, 
extent={{10,-10},{-10,10}})));
equation
  connect(zeroFlowSource1.port_B, gasVolumeV1.port_A) 
    annotation (Line(origin={114.99999999999997,-16.00000000000001}, 
points={{0.24769149060911388,-3.9999999999999964},{0.24769149060911388,4.9776779026217355},{0.19720349563046113,4.9776779026217355}}, 
color={90,229,225}));
  connect(ramp1.y, position1.s_ref) 
    annotation (Line(origin={55.99999999999997,19.999999999999993}, 
points={{-7,1.4210854715202004e-14},{5.999999999999972,1.4210854715202004e-14},{5.999999999999972,0}}, 
color={0,0,127}));
  connect(gasVolume1.port_A, zeroFlowSource3.port_B) 
    annotation (Line(origin={101.41538077403243,-71.07845303867403}, 
points={{-10.393058676654206,0.0784530386740272},{13.169238451935058,0.0784530386740272},{13.169238451935058,0.07845303867401299}}, 
color={90,229,225}));
  connect(mHFlowSource1.port_B, gasVolume1.port_B) 
    annotation (Line(origin={65.4153807740324,-71.07845303867403}, 
points={{-11.96541935483868,0.030709677419338277},{11.553907615480654,0.030709677419338277},{11.553907615480654,0.0812495430435689}}, 
color={90,229,225}));
  connect(position1.flange, fixedBodyPiston1.flange_b) 
    annotation (Line(origin={91.99999999999997,19.999999999999993}, 
points={{-8.000000000000028,0},{7.7829565217391234,0}}, 
color={0,127,0}));
  connect(fixedBodyPiston1.portV_A, gasVolumeV1.portV_B[1]) 
    annotation (Line(origin={114.99999999999997,5.999999999999989}, 
points={{0.20000000000003126,4.0000000000000036},{0.20000000000003126,-3.053183520599232},{0.20000000000000284,-3.053183520599232}}, 
color={90,229,225}));
  connect(zeroFlowSource.port_B, gasVolumeV.port_A) 
  annotation(Line(origin={-30.169238451935087,-10.000000000000012}, 
points={{0.247691490609121,-4},{0.247691490609121,4.977677902621736},{0.19720349563046824,4.977677902621736}}, 
color={90,229,225}));
  connect(ramp.y, position.s_ref) 
  annotation(Line(origin={-89.16923845193507,25.999999999999993}, 
points={{-6.999999999999986,1.4210854715202004e-14},{5.999999999999943,1.4210854715202004e-14},{5.999999999999943,0}}, 
color={0,0,127}));
  connect(gasVolume.port_A, zeroFlowSource2.port_B) 
  annotation(Line(origin={-43.75385767790263,-65.07845303867403}, 
points={{-10.39305867665422,0.07845303867404141},{13.169238451935058,0.07845303867404141},{13.169238451935058,0.0784530386740272}}, 
color={90,229,225}));
  connect(mHFlowSource.port_B, gasVolume.port_B) 
  annotation(Line(origin={-79.75385767790264,-65.07845303867403}, 
points={{-11.965419354838701,0.030709677419352488},{11.553907615480625,0.030709677419352488},{11.553907615480625,0.08124954304358312}}, 
color={90,229,225}));
  connect(position.flange, fixedBodyPiston.flange_b) 
  annotation(Line(origin={-53.16923845193507,25.999999999999993}, 
points={{-8.000000000000057,0},{7.782956521739109,0}}, 
color={0,127,0}));
  connect(fixedBodyPiston.portV_A, gasVolumeV.portV_B[1]) 
  annotation(Line(origin={-30.169238451935087,11.999999999999988}, 
points={{0.20000000000003126,4.0000000000000036},{0.20000000000003126,-3.053183520599232},{0.20000000000000284,-3.053183520599232}}, 
color={90,229,225}));
end AdiabaticChamber;