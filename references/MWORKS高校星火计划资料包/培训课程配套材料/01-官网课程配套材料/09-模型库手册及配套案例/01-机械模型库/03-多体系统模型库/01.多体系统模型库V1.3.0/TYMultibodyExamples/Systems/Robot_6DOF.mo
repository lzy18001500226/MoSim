model Robot_6DOF "6自由度机械臂作业系统"
  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {-15, -7.5}, 
    lineColor = {255, 255, 255}, 
    fillColor = {255, 255, 255}, 
    fillPattern = FillPattern.Solid, 
    extent = {{-281, 121.5}, {281, -121.5}})}), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-3.55271e-15, 27}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {3.55271e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {1.06581e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, NumberOfIntervals = 5000, StartTime = 0, StopTime = 5, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 1.667, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=3, x_display_unit="s", legend_layout=1, left_title="[m]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 5), zoom_y_l=(-1, 1.5)), 
Plot(y=["leftClaw1.body.r_OA_0[1]", "leftClaw1.body.r_OA_0[2]", "leftClaw1.body.r_OA_0[3]"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N.m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 5), zoom_y_l=(-600, 400)), 
Plot(y=["Revolute3.frame_b.t[1]", "Revolute3.frame_b.t[2]", "Revolute3.frame_b.t[3]"], colors=["4278190335", "4294901760", "4278222848"])})
})), Documentation(link = "modelica://TYMultibody/Resources/html/Examples/Robot_6DOF.html"));
  TYMultibody.Joints.Fixed Fixed1(r = {0.34723482703331, 0.09233346438177, 0.27493479996578}) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-281.044, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Joints.Revolute Revolute4(n = {0.40584417995742, 0.91394228570227, 0}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-18.1886, -53.8039}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMultibody.Joints.Revolute Revolute3(n = {0, 0, -1}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-86.0589, -53.8039}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMultibody.Joints.Revolute Revolute5(n = {0.4252156160569, -0.18882076658823, -0.8851770432893}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {49.4183, -53.8039}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMultibody.Joints.Revolute Revolute1(n = {0, 1, 0}, animation = false, om_rel_fixed = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-218.3759, -53.8039}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMultibody.Joints.Revolute Revolute6(n = {-0.73770210759203, 0.49432906900273, -0.45981993431469}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {121.4183, -53.8039}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMultibody.Joints.Revolute Revolute7(n = {-0.61361082296392, -0.7749788849214, 0.15129271584424}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {209.418, -24.99445}, 
    extent = {{-10, 10}, {10, -10}})));
  TYMultibody.Joints.Revolute Revolute8(n = {-0.61361082296392, -0.7749788849214, 0.15129271584424}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {209.418, -78}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Joints.Revolute Revolute2(n = {0, 0, -1}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-150.9629, -53.8039}, 
    extent = {{-10, 10}, {10, -10}})));
  inner TYMultibody.World world(n = {0, -1, 0} ) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-264, -16}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {-242.7862, 37.8261}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Math.Gain gain1(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {-176.3931, 37.8261}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Math.Gain gain2(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {-110, 37.8261}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Math.Gain gain3(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {-44, 37.8261}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Blocks.Sources.RealExpression realExpression(y = time) 
    annotation(Placement(transformation(origin = {-274, 98}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Position angle(useSupport = false) 
    annotation(Placement(transformation(origin = {-226.7089, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Position angle1(useSupport = false) 
    annotation(Placement(transformation(origin = {-159.0419, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Position angle2(useSupport = false) 
    annotation(Placement(transformation(origin = {-92, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Position angle3(useSupport = false) 
    annotation(Placement(transformation(origin = {-28.1886, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain6(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {22, 37.8261}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Mechanics.Rotational.Sources.Position angle6(useSupport = false) 
    annotation(Placement(transformation(origin = {42, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain7(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {98, 33.8261}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = -90)));
  Modelica.Mechanics.Rotational.Sources.Position angle7(useSupport = false) 
    annotation(Placement(transformation(origin = {116, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain5(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {160.365, -104}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.RealExpression realExpression1(y = time) 
    annotation(Placement(transformation(origin = {84.4728, -105.002}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Position angle5(useSupport = false) 
    annotation(Placement(transformation(origin = {196.746, -104.501}, 
    extent = {{-10, 10}, {10, -10}})));
  Modelica.Blocks.Math.Gain gain4(k = Modelica.Constants.D2R) 
    annotation(Placement(transformation(origin = {216.418, 56}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Mechanics.Rotational.Sources.Position angle4(useSupport = false) 
    annotation(Placement(transformation(origin = {216.418, 14}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds1(table = {{0.0, 0}, {1, 0}, {1.5, 0}, {2.5, 90}, {3.5, 90}, {4, 90}, {5, 0}}) 
    annotation(Placement(transformation(origin = {-242.7862, 72.0111}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds9(table = {{0.0, 90}, {0.6, 45}, {1, 45}, {1.5, 60}, {2.5, 60}, {3.5, 45}, {4, 45}, {5, 90}}) 
    annotation(Placement(transformation(origin = {-176.3931, 72.0111}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds2(table = {{0.0, -25}, {0.4, -30}, {1, -30}, {1.5, -10}, {2.5, -10}, {3.5, -30}, {5, -25}}) 
    annotation(Placement(transformation(origin = {-110, 72.0111}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds3(table = {{0.0, -152}, {1, -152}, {2, -152}, {3, -152}, {4, -152}, {5, -152}}) 
    annotation(Placement(transformation(origin = {-43.6069, 72.0111}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds4(table = {{0.0, -15}, {0.6, -60}, {1, -60}, {1.5, -25}, {2.5, -25}, {3.5, -60}, {5, -15}}) 
    annotation(Placement(transformation(origin = {22, 72.0111}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds7(table = {{0.0, -15}, {1, -15}, {1.2, -15}, {2, -15}, {3, -15}, {4, -15}, {5, -15}}) 
    annotation(Placement(transformation(origin = {98, 72.0111}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 270)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds5(table = {{0.0, -10}, {0.6, -45}, {1, -16}, {2.5, -16}, {3.5, -16}, {4, -45}, {5, -10}}) 
    annotation(Placement(transformation(origin = {168, 98}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds6(table = {{0.0, -10}, {0.6, 25}, {1, 0}, {2.5, 0}, {3.5, 0}, {4, 25}, {5, -10}}) 
    annotation(Placement(transformation(origin = {121.4183, -104.501}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 360)));
  TYMultibody.Examples.Systems.Utilities.Base base 
    annotation(Placement(transformation(origin = {-249.71, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.Arm1 arm1_1 
    annotation(Placement(transformation(origin = {-187.0419, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.Arm2 arm2_1 
    annotation(Placement(transformation(origin = {-118.511, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.Arm3 arm3_1 
    annotation(Placement(transformation(origin = {-53.6069, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.RotationArm1 rotationArm1_1 
    annotation(Placement(transformation(origin = {13.4183, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.RotationArm2 rotationArm2_1 
    annotation(Placement(transformation(origin = {85.4183, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.RotationArm3 rotationArm3_1 
    annotation(Placement(transformation(origin = {157.418, -53.8039}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.RightClaw rightClaw 
    annotation(Placement(transformation(origin = {241.418, -24.9944}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMultibody.Examples.Systems.Utilities.leftClaw leftClaw1 
    annotation(Placement(transformation(origin = {241.418, -78}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(gain.y, angle.phi_ref) 
    annotation(Line(origin = {-265.5969, 64.3321}, 
    points = {{22.8107, -37.506}, {22.8107, -66.3321}, {28.888, -66.3321}}, 
    color = {0, 0, 127}));
  connect(gain1.y, angle1.phi_ref) 
    annotation(Line(origin = {-188.7884, 32.8151}, 
    points = {{12.3953, -5.989}, {12.3953, -34.8151}, {19.7465, -34.8151}}, 
    color = {0, 0, 127}));
  connect(gain2.y, angle2.phi_ref) 
    annotation(Line(origin = {-161.6989, 65.6641}, 
    points = {{51.6989, -38.838}, {51.6989, -67.6641}, {59.6989, -67.6641}}, 
    color = {0, 0, 127}));
  connect(gain3.y, angle3.phi_ref) 
    annotation(Line(origin = {-56.2872, 69.6851}, 
    points = {{12.2872, -42.859}, {12.2872, -71.6851}, {18.0986, -71.6851}}, 
    color = {0, 0, 127}));
  connect(gain6.y, angle6.phi_ref) 
    annotation(Line(origin = {-3.5092, 70.4931}, 
    points = {{25.5092, -43.667}, {25.5092, -72.4931}, {35.5092, -72.4931}}, 
    color = {0, 0, 127}));
  connect(gain7.y, angle7.phi_ref) 
    annotation(Line(origin = {120.18, 71.8531}, 
    points = {{-22.1798, -49.027}, {-22.1798, -73.8531}, {-14.1798, -73.8531}}, 
    color = {0, 0, 127}));
  connect(angle2.flange, Revolute3.axis) 
    annotation(Line(origin = {-111.059, 1.1961}, 
    points = {{29.0594, -3.1961}, {32.0005, -3.1961}, {32.0005, -45}}, 
    color = {0, 0, 0}));
  connect(angle3.flange, Revolute4.axis) 
    annotation(Line(origin = {-15.6411, 3.1961}, 
    points = {{-2.5475, -5.1961}, {4.4525, -5.1961}, {4.4525, -47}}, 
    color = {0, 0, 0}));
  connect(angle6.flange, Revolute5.axis) 
    annotation(Line(origin = {67.9658, 4.1961}, 
    points = {{-15.9658, -6.1961}, {-11.5475, -6.1961}, {-11.5475, -48}}, 
    color = {0, 0, 0}));
  connect(angle7.flange, Revolute6.axis) 
    annotation(Line(origin = {174.966, 4.1961}, 
    points = {{-48.9658, -6.1961}, {-46.5475, -6.1961}, {-46.5475, -48}}, 
    color = {0, 0, 0}));
  connect(gain5.y, angle5.phi_ref) 
    annotation(Line(origin = {192.6023, -103.501}, 
    points = {{-21.237, -0.499}, {-5.856, -0.499}, {-5.856, -1}}, 
    color = {0, 0, 127}));
  connect(gain4.y, angle4.phi_ref) 
    annotation(Line(origin = {202.216, 54.7891}, 
    points = {{14.202, -9.7891}, {14.202, -30.7891}}, 
    color = {0, 0, 127}));
  connect(gain.u, combiTable1Ds1.y[1]) 
    annotation(Line(origin = {-243.0322, 55.0111}, 
    points = {{0.246, -5.185}, {0.246, 6}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds1.u, realExpression.y) 
    annotation(Line(origin = {-362.4944, 130.1961}, 
    points = {{119.708, -46.185}, {119.708, -32.1961}, {99.4944, -32.1961}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds9.y[1], gain1.u) 
    annotation(Line(origin = {-203.85, 55.0111}, 
    points = {{27.4565, 6}, {27.4565, -5.185}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds9.u, realExpression.y) 
    annotation(Line(origin = {-334.4944, 130.1961}, 
    points = {{158.101, -46.185}, {158.101, -32.1961}, {71.4944, -32.1961}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(gain2.u, combiTable1Ds2.y[1]) 
    annotation(Line(origin = {-109.929, 59.0111}, 
    points = {{-0.0708, -9.185}, {-0.0708, 2}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds2.u, realExpression.y) 
    annotation(Line(origin = {-305.0594, 130.1961}, 
    points = {{195.059, -46.185}, {195.059, -32.1961}, {42.0594, -32.1961}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(combiTable1Ds3.y[1], gain3.u) 
    annotation(Line(origin = {-44, 55.0111}, 
    points = {{0.3931, 6}, {0.3931, -5.185}, {0, -5.185}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds3.u, realExpression.y) 
    annotation(Line(origin = {-254.059, 130.1961}, 
    points = {{210.4525, -46.185}, {210.4525, -32.1961}, {-8.9406, -32.1961}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(combiTable1Ds4.y[1], gain6.u) 
    annotation(Line(origin = {22.142, 55.0111}, 
    points = {{-0.142, 6}, {-0.142, -5.185}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds4.u, realExpression.y) 
    annotation(Line(origin = {-220.4525, 130.1961}, 
    points = {{242.4525, -46.185}, {242.4525, -32.1961}, {-42.5475, -32.1961}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(combiTable1Ds7.y[1], gain7.u) 
    annotation(Line(origin = {98.1416, 53.0111}, 
    points = {{-0.1416, 8}, {-0.1416, -7.185}}, 
    color = {0, 0, 127}));
  connect(combiTable1Ds7.u, realExpression.y) 
    annotation(Line(origin = {-157.4525, 132.1961}, 
    points = {{255.4525, -48.185}, {255.4525, -34.1961}, {-105.548, -34.1961}}, 
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(gain4.u, combiTable1Ds5.y[1]) 
    annotation(Line(origin = {136.8933, 55.965}, 
    points = {{79.525, 12.035}, {79.525, 42.035}, {42.1067, 42.035}}, 
    color = {0, 0, 127}));
  connect(gain5.u, combiTable1Ds6.y[1]) 
    annotation(Line(origin = {161.037, -104.0738}, 
    points = {{-12.672, 0.0738}, {-28.619, 0.0738}, {-28.619, -0.4272}}, 
    color = {0, 0, 127}));
  connect(realExpression1.y, combiTable1Ds6.u) 
    annotation(Line(origin = {102.0373, -104.575}, 
    points = {{-6.5645, -0.4272}, {7.381, -0.4272}, {7.381, 0.0738}}, 
    color = {0, 0, 127}));
  connect(Fixed1.frame_b, base.Marker1) 
    annotation(Line(origin = {-274.9239, -54}, 
    points = {{3.88, 0.1961}, {15.214, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute3.frame_a, arm2_1.Marker4) 
    annotation(Line(origin = {-120.6069, -54}, 
    points = {{24.548, 0.1961}, {12.096, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute4.frame_b, rotationArm1_1.Marker5) 
    annotation(Line(origin = {29.4183, -54}, 
    points = {{-37.6069, 0.1961}, {-26, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute3.frame_b, arm3_1.Marker4) 
    annotation(Line(origin = {-55.6069, -54}, 
    points = {{-20.452, 0.1961}, {-8, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute4.frame_a, arm3_1.Marker5) 
    annotation(Line(origin = {4.3931, -54}, 
    points = {{-32.5817, 0.1961}, {-48, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(angle.flange, Revolute1.axis) 
    annotation(Line(origin = {-204.9239, -28}, 
    points = {{-11.785, 26}, {-6.452, 26}, {-6.452, -15.8039}}, 
    color = {0, 0, 0}));
  connect(Revolute1.frame_b, arm1_1.Marker2) 
    annotation(Line(origin = {-240.5109, -54}, 
    points = {{32.135, 0.1961}, {43.469, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute1.frame_a, base.Marker2) 
    annotation(Line(origin = {-236.9239, -54}, 
    points = {{8.548, 0.1961}, {-2.786, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(arm1_1.Marker3, Revolute2.frame_a) 
    annotation(Line(origin = {-176.5109, -54}, 
    points = {{-0.531, 0.1961}, {15.548, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute2.frame_b, arm2_1.Marker3) 
    annotation(Line(origin = {-180.6069, -54}, 
    points = {{39.644, 0.1961}, {52.096, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(angle1.flange, Revolute2.axis) 
    annotation(Line(origin = {-158.5109, 2}, 
    points = {{9.469, -4}, {14.548, -4}, {14.548, -45.8039}}, 
    color = {0, 0, 0}));
  connect(rotationArm1_1.Marker6, Revolute5.frame_a) 
    annotation(Line(origin = {41.4183, -54}, 
    points = {{-18, 0.1961}, {-2, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute5.frame_b, rotationArm2_1.Marker6) 
    annotation(Line(origin = {100.4183, -54}, 
    points = {{-41, 0.1961}, {-25, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(rotationArm2_1.Marker7, Revolute6.frame_a) 
    annotation(Line(origin = {128.418, -54}, 
    points = {{-33, 0.1961}, {-17, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute6.frame_b, rotationArm3_1.Marker7) 
    annotation(Line(origin = {200.418, -54}, 
    points = {{-69, 0.1961}, {-53, 0.1961}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute7.frame_a, rotationArm3_1.Marker8) 
    annotation(Line(origin = {190.418, -32}, 
    points = {{9, 7.00555}, {-9, 7.00555}, {-9, -15.8039}, {-23, -15.8039}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute7.frame_b, rightClaw.Marker8) 
    annotation(Line(origin = {231.418, -16}, 
    points = {{-12, -8.99445}, {0, -8.99445}, {0, -8.99445}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(angle4.flange, Revolute7.axis) 
    annotation(Line(origin = {233.418, 25}, 
    points = {{-17, -21}, {-17, -39.99445}}, 
    color = {0, 0, 0}));
  connect(combiTable1Ds5.u, realExpression.y) 
    annotation(Line(origin = {-133, 116}, 
    points = {{289, -18}, {-130, -18}}, 
    color = {0, 0, 127}));
  connect(rotationArm3_1.Marker9, Revolute8.frame_a) 
    annotation(Line(origin = {190.418, -69}, 
    points = {{-23, 9.1961}, {-9, 9.1961}, {-9, -9}, {9, -9}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(Revolute8.frame_b, leftClaw1.Marker9) 
    annotation(Line(origin = {231.418, -78}, 
    points = {{-12, 0}, {0, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(angle5.flange, Revolute8.axis) 
    annotation(Line(origin = {225.418, -114}, 
    points = {{-18.672, 9.499}, {-9, 9.499}, {-9, 26}}, 
    color = {0, 0, 0}));
end Robot_6DOF;