model UseOfSensors "使用传感器"
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
    Protection(access = Access.nonPackageDuplicate),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={-8,4}, 
points={{-118,64},{-118,-64},{118,-64},{118,64},{-118,64}}, 
color={255,255,255})}), 
Documentation(link = "modelica://TYMultibody/Resources/html/UseOfSensors.html"),experiment(Algorithm=Dassl,Interval=0.001,StartTime=0,StopTime=3,Tolerance=1e-06),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.009,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title="[m]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-3, 3)), 
Plot(y=["absoluteSensor.r[1]", "absoluteSensor.r[2]", "absoluteSensor.r[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-4000, 10000)), 
Plot(y=["forceAndTorqueSensor.force[1]", "forceAndTorqueSensor.force[2]", "forceAndTorqueSensor.force[3]"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  inner TYMultibody.World world 
    annotation (Placement(transformation(origin = {-96.0, -1.3075104641920554}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyBox bodyBox(
                                     v_OA_0(start = {0, 0, 0}, fixed = false), angles_fixed = false, r_OA_0(fixed = false), angles_startDeg = {0, 0, 0}, om_0_fixed = false, om_0_start = {0, 0, 0}








                                                                                                                                                                                                   ) 
    annotation (Placement(transformation(origin = {61.15223878436588, -0.07998211987220016}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.AbsoluteSensor absoluteSensor(
                                                    resolveInFrame = TYMultibody.Types.ResolveInFrameA.world








                                                                                                            ) 
    annotation (Placement(transformation(origin = {86.27811761664155, 1.2594056773542204}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.DistanceSensor distanceSensor(
                                                    animation = true








                                                                    ) 
    annotation (Placement(transformation(origin = {-1.0185194796172148, -32.4503841068915}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute 
    annotation (Placement(transformation(origin = {-58.92131146366571, -1.3075104641920552}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.PowerSensor powerSensor 
    annotation (Placement(transformation(origin = {11.99201562651648, -0.5261526502059528}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.RelativeSensor relativeSensor(
                                                    get_r_rel = true, get_v_rel = true, get_a_rel = true, get_om_rel = true, get_alp_rel = true, get_phi_rel = true, 
    resolveInFrame = TYMultibody.Types.ResolveInFrameAB.frame_b








                                                               ) annotation (Placement(transformation(origin = {4.8522707497191, 33.43502287865148}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.RPYSensor rollPitchYawSensor 
    annotation (Placement(transformation(origin = {85.60321819261178, -29.097841952526714}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Sensors.ForceAndTorqueSensor forceAndTorqueSensor(
                                                                resolveInFrame = TYMultibody.Types.ResolveInFrameA.world








                                                                                                                        ) 
    annotation (Placement(transformation(origin = {37.13988017382595, -0.2264857679586083}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.BodyBox bodyBox1 
    annotation (Placement(transformation(origin = {-36.05999044191687, -1.3861563931812682}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Revolute revolute1 
    annotation (Placement(transformation(origin = {-12.850026649156339, -1.0947373188921734}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(world.frame_b, revolute.frame_a) 
    annotation (Line(origin = {-60.50316566387873, 1.4145125871100874}, 
      points = {{-25.0, -3.0}, {-8.0, -3.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(distanceSensor.frame_a, revolute.frame_a) 
    annotation (Line(origin = {-18.503165663878736, -7.585487412889913}, 
      points = {{7.0, -25.0}, {-51.0, -25.0}, {-51.0, 6.0}, {-50.0, 6.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(relativeSensor.frame_a, revolute.frame_a) 
    annotation (Line(origin = {-29.28353130374849, 23.735073568828092}, 
      points = {{24.0, 10.0}, {-40.0, 10.0}, {-40.0, -25.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(relativeSensor.frame_b, bodyBox.frame_b) 
    annotation (Line(origin = {61.71646869625151, 23.735073568828092}, 
      points = {{-47.0, 10.0}, {9.0, 10.0}, {9.0, -24.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rollPitchYawSensor.frame_a, bodyBox.frame_b) 
    annotation (Line(origin = {87.71646869625151, -26.264926431171908}, 
      points = {{-12.0, -3.0}, {-17.0, -3.0}, {-17.0, 26.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(forceAndTorqueSensor.frame_b, bodyBox.frame_a) 
    annotation (Line(origin = {62.05962630491621, -0.8628231705190377}, 
      points = {{-15.0, 1.0}, {-11.0, 1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(powerSensor.frame_b, forceAndTorqueSensor.frame_a) 
    annotation (Line(origin = {11.059626304916199, -0.8628231705190377}, 
      points = {{11.0, 0.0}, {16.0, 0.0}, {16.0, 1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(distanceSensor.frame_b, bodyBox.frame_b) 
    annotation (Line(origin = {30.91419074289098, -15.0}, 
      points = {{-22.0, -17.0}, {40.0, -17.0}, {40.0, 15.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(absoluteSensor.frame_a, bodyBox.frame_b) 
    annotation (Line(origin = {64.91419074289098, 1.0}, 
      points = {{11.0, 0.0}, {6.0, 0.0}, {6.0, -1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute.frame_b, bodyBox1.frame_a) 
    annotation (Line(origin = {-49.74265164844433, -0.5978967393471315}, 
      points = {{1.0, -1.0}, {4.0, -1.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(bodyBox1.frame_b, revolute1.frame_a) 
    annotation (Line(origin = {-24.74265164844433, -0.5978967393471315}, 
      points = {{-1.0, -1.0}, {-1.0, 0.0}, {2.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(revolute1.frame_b, powerSensor.frame_a) 
    annotation (Line(origin = {0.25734835155567026, -0.5978967393471315}, 
      points = {{-3.0, 0.0}, {2.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
end UseOfSensors;