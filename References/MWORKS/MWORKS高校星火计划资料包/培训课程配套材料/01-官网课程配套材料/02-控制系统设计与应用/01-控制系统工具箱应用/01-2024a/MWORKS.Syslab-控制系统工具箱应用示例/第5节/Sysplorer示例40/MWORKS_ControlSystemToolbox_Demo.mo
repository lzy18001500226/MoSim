within ;
package MWORKS_ControlSystemToolbox_Demo "MWORKS控制系统工具箱示例"
  extends Modelica.Icons.Package;
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    preserveAspectRatio = false, 
    grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
    lineColor = {128, 128, 128}, 
    extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    radius = 25.0), Rectangle(origin = {0.0, 35.1488}, 
    fillColor = {255, 255, 255}, 
    extent = {{-30.0, -20.1488}, {30.0, 20.1488}}), Rectangle(origin = {0.0, -34.8512}, 
    fillColor = {255, 255, 255}, 
    extent = {{-30.0, -20.1488}, {30.0, 20.1488}}), Line(origin = {-51.25, 0.0}, 
    points = {{21.25, -35.0}, {-13.75, -35.0}, {-13.75, 35.0}, {6.25, 35.0}}), Polygon(origin = {-40.0, 35.0}, 
    pattern = LinePattern.None, 
    fillPattern = FillPattern.Solid, 
    points = {{10.0, 0.0}, {-5.0, 5.0}, {-5.0, -5.0}}), Line(origin = {51.25, 0.0}, 
    points = {{-21.25, 35.0}, {13.75, 35.0}, {13.75, -35.0}, {-6.25, -35.0}}), Polygon(origin = {40.0, -35.0}, 
    pattern = LinePattern.None, 
    fillPattern = FillPattern.Solid, 
    points = {{-10.0, 0.0}, {5.0, 5.0}, {5.0, -5.0}})}));
  model Demo39_StateSpace_Plant "被控对象的状态空间模型"
    extends Modelica.Icons.Example;
    Modelica.Blocks.Continuous.Integrator x3 annotation (Placement(transformation(origin = {-30.0, 24.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Continuous.Integrator x2 annotation (Placement(transformation(origin = {30.0, 24.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Continuous.Integrator x1 annotation (Placement(transformation(origin = {90.0, 24.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain gain(k = -3)
      annotation (Placement(transformation(origin = {-30.0, -26.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain gain1(k = -2)
      annotation (Placement(transformation(origin = {32.0, -38.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Add add
      annotation (Placement(transformation(origin = {-72.0, -32.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Sources.Step U(startTime = 1)
      annotation (Placement(transformation(origin = {-148.0, 30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Add add1
      annotation (Placement(transformation(origin = {-86.0, 24.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain C(k = 1)
      annotation (Placement(transformation(origin = {140.0, 24.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation (Diagram(coordinateSystem(extent = {{-172.0, -100.0}, {166.0, 100.0}}, 
      grid = {2.0, 2.0})), 
      experiment(StopTime = 20, NumberOfIntervals = 5000), 
      __MWorks(ResultViewerManager(resultViewers = {
        ResultViewer(name = "后处理", executeTrigger = executeTrigger.SimulationFinished, commands = {
        CreatePlot(id = 1, position = [232, 131, 960, 640], y = ["U.y", "C.y"], x_display_unit = "s", y_axis = [1, 1], legend_layout = 7, legend_frame = True, fix_time_range_value = 6.95181e-310)})})));
  equation 
    connect(x3.y, x2.u)
      annotation (Line(origin = {3.552713678800501e-15, 24.0}, 
        points = {{-19.0, 0.0}, {18.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(x2.y, x1.u)
      annotation (Line(origin = {60.0, 24.0}, 
        points = {{-19.0, 0.0}, {18.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain.u, x3.y)
      annotation (Line(origin = {-9.0, -1.0}, 
        points = {{-9.0, -25.0}, {9.0, -25.0}, {9.0, 25.0}, {-10.0, 25.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain1.u, x2.y)
      annotation (Line(origin = {51.0, -16.0}, 
        points = {{-7.0, -22.0}, {9.0, -22.0}, {9.0, 40.0}, {-10.0, 40.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add.u2, gain.y)
      annotation (Line(origin = {-50.0, -27.0}, 
        points = {{-10.0, 1.0}, {9.0, 1.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain1.y, add.u1)
      annotation (Line(origin = {-20.0, -47.0}, 
        points = {{41.0, 9.0}, {-40.0, 9.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add.y, add1.u2)
      annotation (Line(origin = {-101.0, -6.9999999999999964}, 
        points = {{18.0, -25.0}, {-19.0, -25.0}, {-19.0, 25.0}, {3.0, 25.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(U.y, add1.u1)
      annotation (Line(origin = {-117.0, 30.0}, 
        points = {{-20.0, 0.0}, {19.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add1.y, x3.u)
      annotation (Line(origin = {-58.0, 24.0}, 
        points = {{-17.0, 0.0}, {16.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(x1.y, C.u)
      annotation (Line(origin = {115.0, 24.0}, 
        points = {{-14.0, 0.0}, {13.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
  end Demo39_StateSpace_Plant;
  model Demo39_States_Feedback_Control "状态反馈控制"
    extends Modelica.Icons.Example;
    Modelica.Blocks.Continuous.Integrator x3 annotation (Placement(transformation(origin = {10.0, 70.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Continuous.Integrator x2 annotation (Placement(transformation(origin = {70.0, 70.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Continuous.Integrator x1 annotation (Placement(transformation(origin = {130.0, 70.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Add add
      annotation (Placement(transformation(origin = {-50.0, 70.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Add add1
      annotation (Placement(transformation(origin = {-30.0, 24.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain gain(k = -2)
      annotation (Placement(transformation(origin = {70.0, 17.999999999999996}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain C(k = 1)
      annotation (Placement(transformation(origin = {190.0, 70.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain gain2(k = -3)
      annotation (Placement(transformation(origin = {10.0, 30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Sources.Step U(startTime = 1)
      annotation (Placement(transformation(origin = {-224.0, 76.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Add add2
      annotation (Placement(transformation(origin = {-50.0, -46.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain k2(k = 54)
      annotation (Placement(transformation(origin = {-10.0, -52.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain k3(k = 11)
      annotation (Placement(transformation(origin = {10.0, -32.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Feedback feedback
      annotation (Placement(transformation(origin = {-102.0, 76.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain k1(k = 160)
      annotation (Placement(transformation(origin = {-136.0, 76.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 360.0)));
    Modelica.Blocks.Math.Feedback feedback1
      annotation (Placement(transformation(origin = {-174.0, 76.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation (Diagram(coordinateSystem(extent = {{-244.0, -102.0}, {216.0, 100.0}}, 
      grid = {2.0, 2.0})), 
      experiment(StopTime = 8, NumberOfIntervals = 5000), 
      __MWorks(ResultViewerManager(resultViewers = {
        ResultViewer(name = "后处理", executeTrigger = executeTrigger.SimulationFinished, commands = {
        CreatePlot(id = 1, position = [221, 124, 960, 640], y = ["U.y", "C.y"], x_display_unit = "s", y_axis = [1, 1], legend_layout = 7, legend_frame = True, fix_time_range_value = 6.95181e-310)})})));
  equation 
    connect(x3.y, x2.u)
      annotation (Line(origin = {30.0, 70.0}, 
        points = {{-9.0, 0.0}, {28.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(x2.y, x1.u)
      annotation (Line(origin = {70.0, 70.0}, 
        points = {{11.0, 0.0}, {48.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(x1.y, C.u)
      annotation (Line(origin = {110.0, 70.0}, 
        points = {{31.0, 0.0}, {68.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain.u, x2.y)
      annotation (Line(origin = {66.0, 50.0}, 
        points = {{16.0, -32.0}, {34.0, -32.0}, {34.0, 20.0}, {15.0, 20.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain2.y, add1.u2)
      annotation (Line(origin = {-9.0, 30.0}, 
        points = {{8.0, 0.0}, {-9.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain.y, add1.u1)
      annotation (Line(origin = {1.0, 4.0}, 
        points = {{58.0, 14.0}, {-19.0, 14.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add.y, x3.u) "x3" 
      annotation (Line(origin = {-20.0, 70.0}, 
        points = {{-19.0, 0.0}, {18.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add1.y, add.u2)
      annotation (Line(origin = {-51.0, 44.0}, 
        points = {{10.0, -20.0}, {-19.0, -20.0}, {-19.0, 20.0}, {-11.0, 20.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(k2.u, x2.y)
      annotation (Line(origin = {38.0, 14.0}, 
        points = {{-36.0, -66.0}, {62.0, -66.0}, {62.0, 56.0}, {43.0, 56.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(k3.u, x3.y)
      annotation (Line(origin = {26.0, -1.0}, 
        points = {{-4.0, -31.0}, {14.0, -31.0}, {14.0, 71.0}, {-5.0, 71.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add2.u1, k2.y)
      annotation (Line(origin = {-29.0, -52.0}, 
        points = {{-9.0, 0.0}, {8.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add2.u2, k3.y)
      annotation (Line(origin = {-19.0, -36.0}, 
        points = {{-19.0, -4.0}, {-4.0, -4.0}, {-4.0, 4.0}, {18.0, 4.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(add2.y, feedback.u2)
      annotation (Line(origin = {-85.0, 8.0}, 
        points = {{24.0, -54.0}, {-17.0, -54.0}, {-17.0, 60.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(feedback.y, add.u1)
      annotation (Line(origin = {-81.0, 73.0}, 
        points = {{-12.0, 3.0}, {19.0, 3.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(k1.y, feedback.u1)
      annotation (Line(origin = {-117.0, 76.0}, 
        points = {{-8.0, 0.0}, {7.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(feedback1.y, k1.u)
      annotation (Line(origin = {-156.0, 76.0}, 
        points = {{-9.0, 0.0}, {8.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(U.y, feedback1.u1)
      annotation (Line(origin = {-197.0, 76.0}, 
        points = {{-16.0, 0.0}, {15.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(feedback1.u2, C.u)
      annotation (Line(origin = {-28.0, -5.0}, 
        points = {{-146.0, 73.0}, {-146.0, -75.0}, {182.0, -75.0}, {182.0, 75.0}, {206.0, 75.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(gain2.u, x3.y)
      annotation (Line(origin = {31.0, 50.0}, 
        points = {{-9.0, -20.0}, {9.0, -20.0}, {9.0, 20.0}, {-10.0, 20.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
  end Demo39_States_Feedback_Control;
  model Demo40_InvertedPendlum "倒立摆被控对象"
    inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity, animateWorld = false, animateGravity = false)
      annotation (Placement(transformation(origin = {-40.0, -30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic
      annotation (Placement(transformation(origin = {-2.0, -30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, 
      phi(start
         = 0.261799387799149, fixed
         = true))


      annotation (Placement(transformation(origin = {66.0, -30.0}, 
        extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
        rotation = 360.0)));
    Modelica.Mechanics.MultiBody.Forces.WorldForce force
      annotation (Placement(transformation(origin = {-38.0, 0.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    Modelica.Blocks.Sources.Constant const1(k = 0)
      annotation (Placement(transformation(origin = {-94.0, 0.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    Modelica.Blocks.Sources.Constant const2(k = 0)
      annotation (Placement(transformation(origin = {-94.0, -30.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    Modelica.Mechanics.MultiBody.Parts.FixedRotation fixedRotation(angle = 90, 
      n = {0, 0, 1}) annotation (Placement(transformation(origin = {36.0, -30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.BodyShape bodyShape1(m = 2, 
      shapeType = "box", length = 0.25, width = 0.125, 
      animateSphere = false, 
      r_shape = {-0.125, 0, 0})
      annotation (Placement(transformation(origin = {-2.0, 0.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation fixedTranslation(r = {0.5, 0, 0})
      annotation (Placement(transformation(origin = {98.0, -30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.Body body(sphereColor = {255, 255, 0}, sphereDiameter = 0.1, m = 0.1)
      annotation (Placement(transformation(origin = {128.0, -30.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Sources.Constant const3(k = 0)
      annotation (Placement(transformation(origin = {-94.0, 32.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    annotation (Diagram(coordinateSystem(extent = {{-116.0, -100.0}, {144.0, 98.0}}, 
      grid = {2.0, 2.0})), 
      Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
        grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
        lineColor = {200, 200, 200}, 
        fillColor = {248, 248, 248}, 
        fillPattern = FillPattern.HorizontalCylinder, 
        extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
        radius = 25.0), Rectangle(origin = {0.0, 0.0}, 
        lineColor = {128, 128, 128}, 
        extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
        radius = 25.0), Rectangle(origin = {12.7519, -0.6508000000000003}, 
        rotation = 75.0, 
        fillColor = {0, 0, 128}, 
        fillPattern = FillPattern.Solid, 
        extent = {{-59.184623844335945, 1.9981114376470046}, {59.184623844335945, -1.9981114376470082}}), Ellipse(origin = {29.0, 57.0}, 
        fillColor = {0, 0, 0}, 
        fillPattern = FillPattern.HorizontalCylinder, 
        extent = {{-9.0, 9.0}, {9.0, -9.0}}), Rectangle(origin = {0.0, -64.0}, 
        fillColor = {0, 128, 0}, 
        fillPattern = FillPattern.Solid, 
        extent = {{-50.0, -10.0}, {50.0, 10.0}})}));
  equation 
    connect(world.frame_b, prismatic.frame_a)
      annotation (Line(origin = {-44.0, -30.0}, 
        points = {{14.0, 0.0}, {32.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(fixedRotation.frame_a, prismatic.frame_b)
      annotation (Line(origin = {20.0, -30.0}, 
        points = {{6.0, 0.0}, {-12.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(fixedRotation.frame_b, revolute.frame_b)
      annotation (Line(origin = {50.0, -30.0}, 
        points = {{-4.0, 0.0}, {6.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(force.frame_b, bodyShape1.frame_b)
      annotation (Line(origin = {47.0, -76.0}, 
        points = {{-75.0, 76.0}, {-59.0, 76.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(bodyShape1.frame_a, prismatic.frame_b)
      annotation (Line(origin = {15.0, -43.0}, 
        points = {{-7.0, 43.0}, {3.0, 43.0}, {3.0, 13.0}, {-7.0, 13.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(revolute.frame_a, fixedTranslation.frame_a)
      annotation (Line(origin = {86.0, -30.0}, 
        points = {{-10.0, 0.0}, {2.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(fixedTranslation.frame_b, body.frame_a)
      annotation (Line(origin = {125.0, -30.0}, 
        points = {{-17.0, 0.0}, {-7.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 0.5));
    connect(const1.y, force.force[2])
      annotation (Line(origin = {-63.0, -86.0}, 
        points = {{-20.0, 86.0}, {13.0, 86.0}}, 
        color = {0, 0, 127}));
    connect(const2.y, force.force[3])
      annotation (Line(origin = {-63.0, -101.0}, 
        points = {{-20.0, 71.0}, {-3.0, 71.0}, {-3.0, 101.0}, {13.0, 101.0}}, 
        color = {0, 0, 127}));
    connect(const3.y, force.force[1])
      annotation (Line(origin = {-66.0, 16.0}, 
        points = {{-17.0, 16.0}, {0.0, 16.0}, {0.0, -16.0}, {16.0, -16.0}}, 
        color = {0, 0, 127}));
  end Demo40_InvertedPendlum;

  model Demo40_InvertedPendlumWithControl "倒立摆控制系统"
    extends Modelica.Icons.Example;
    annotation (Diagram(coordinateSystem(extent = {{-278.0, -160.0}, {240.0, 140.0}}, 
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {72.99999999999999, 54.0}, 
      lineColor = {255, 0, 0}, 
      fillColor = {182, 255, 103}, 
      pattern = LinePattern.Dot, 
      fillPattern = FillPattern.Solid, 
      extent = {{-141.0, 67.0}, {141.0, -67.0}}, 
      radius = 5.0), Polygon(origin = {-4.000000000000028, -48.0}, 
      fillColor = {255, 242, 219}, 
      fillPattern = FillPattern.Solid, 
      points = {{-218.0, 91.0}, {-74.0, 91.0}, {-74.0, 21.0}, {218.0, 21.0}, {218.0, -91.0}, {-218.0, -91.0}}), Text(origin = {-45.00000000000003, 111.0}, 
      extent = {{-17.0, 10.0}, {17.0, -10.0}}, 
      textString = "Plant", 
      fontName = "Consolas", 
      textStyle = {TextStyle.Bold}), Text(origin = {-160.0, -111.0}, 
      extent = {{-34.0, 16.0}, {34.0, -16.0}}, 
      textString = "Controller", 
      fontName = "Consolas", 
      textStyle = {TextStyle.Bold})}), 
      experiment(StopTime = 50, NumberOfIntervals = 5000), 
      __MWorks(ResultViewerManager(resultViewers = {
        ResultViewer(name = "后处理", executeTrigger = executeTrigger.SimulationFinished, commands = {
        CreatePlot(id = 1, position = [151, 167, 1126, 1245], y = ["timeTable.y", "absolutePosition.r[1]"], x_display_unit = "s", y_display_units = ["", "m"], y_axis = [1, 1], legend_layout = 7, legend_frame = True, fix_time_range_value = 6.95181e-310), 
        CreatePlot(id = 1, position = [151, 167, 1126, 1245], y = ["angleSensor.phi"], x_display_unit = "s", y_display_units = ["deg"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg]", fix_time_range_value = 6.95181e-310, sub_plot = [2, 1])})})));
    inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity, animateWorld = false, animateGravity = false)
      annotation (Placement(transformation(origin = {-2.7533531010703882e-14, 49.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic
      annotation (Placement(transformation(origin = {37.99999999999997, 49.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, 
      phi(start
         = 0.349065850398866, fixed
         = true))


      annotation (Placement(transformation(origin = {103.99999999999999, 49.0}, 
        extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
        rotation = 360.0)));
    Modelica.Mechanics.MultiBody.Forces.WorldForce force
      annotation (Placement(transformation(origin = {1.9999999999999725, 79.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    Modelica.Blocks.Sources.Constant const1(k = 0)
      annotation (Placement(transformation(origin = {-54.000000000000036, 79.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    Modelica.Blocks.Sources.Constant const2(k = 0)
      annotation (Placement(transformation(origin = {-54.000000000000036, 49.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
        rotation = -180.0)));
    Modelica.Mechanics.MultiBody.Parts.FixedRotation fixedRotation(angle = 90, 
      n = {0, 0, 1}) annotation (Placement(transformation(origin = {75.99999999999997, 49.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Sensors.AbsolutePosition absolutePosition
      annotation (Placement(transformation(origin = {157.99999999999994, 79.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Sensors.AngleSensor angleSensor
      annotation (Placement(transformation(origin = {121.99999999999999, 3.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.BodyShape bodyShape1(m = 2, 
      shapeType = "box", length = 0.25, width = 0.125, 
      animateSphere = false, 
      r_shape = {-0.125, 0, 0})
      annotation (Placement(transformation(origin = {37.99999999999997, 79.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation fixedTranslation(r = {0.5, 0, 0})
      annotation (Placement(transformation(origin = {138.0, 49.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.Body body(sphereColor = {255, 255, 0}, sphereDiameter = 0.1, m = 0.1)
      annotation (Placement(transformation(origin = {167.99999999999997, 49.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor
      annotation (Placement(transformation(origin = {147.99999999999994, 21.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Sensors.AbsoluteVelocity absoluteVelocity
      annotation (Placement(transformation(origin = {177.99999999999997, 103.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain K3(k = -494.898)
      annotation (Placement(transformation(origin = {79.99999999999997, -85.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain K2(k = -255.995)
      annotation (Placement(transformation(origin = {101.99999999999999, -65.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Gain K1(k = -982.029)
      annotation (Placement(transformation(origin = {123.99999999999999, -45.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Math.Feedback feedback
      annotation (Placement(transformation(origin = {-94.00000000000001, 23.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain K4(k = -419.19)
      annotation (Placement(transformation(origin = {57.999999999999964, -107.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
    Modelica.Blocks.Continuous.Integrator x5
      annotation (Placement(transformation(origin = {-167.50000000000003, 23.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain Kl(k = -306)
      annotation (Placement(transformation(origin = {-127.50000000000003, 23.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 360.0)));
    Modelica.Blocks.Math.Feedback feedback2
      annotation (Placement(transformation(origin = {-207.49999999999997, 23.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Sum sum1(nin = 4)
      annotation (Placement(transformation(origin = {-8.000000000000027, -65.0}, 
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {1, 1}, {8, 1}, {8, -1}, {16, -1}, {17, -1}, {17, 1}, {24, 1}, {24, -2}, {32, -2}, {32, 1}, {40, 1}, {46, 1}, {46, 0}, {50, 0}})
      annotation (Placement(transformation(origin = {-239.99999999999997, 23.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  equation 
    connect(world.frame_b, prismatic.frame_a)
      annotation (Line(origin = {-4.000000000000028, 49.0}, 
        points = {{14.0, 0.0}, {32.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(fixedRotation.frame_a, prismatic.frame_b)
      annotation (Line(origin = {59.99999999999997, 49.0}, 
        points = {{6.0, 0.0}, {-12.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(fixedRotation.frame_b, revolute.frame_b)
      annotation (Line(origin = {89.99999999999997, 49.0}, 
        points = {{-4.0, 0.0}, {4.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(revolute.axis, angleSensor.flange)
      annotation (Line(origin = {129.99999999999994, 44.0}, 
        points = {{-26.0, -5.0}, {-26.0, -39.0}, {-18.0, -39.0}, {-18.0, -41.0}}, 
        color = {0, 0, 0}, 
        thickness = 1.0));
    connect(force.frame_b, bodyShape1.frame_b)
      annotation (Line(origin = {86.99999999999997, 3.0}, 
        points = {{-75.0, 76.0}, {-59.0, 76.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(bodyShape1.frame_a, prismatic.frame_b)
      annotation (Line(origin = {54.99999999999997, 36.0}, 
        points = {{-7.0, 43.0}, {3.0, 43.0}, {3.0, 13.0}, {-7.0, 13.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(revolute.frame_a, fixedTranslation.frame_a)
      annotation (Line(origin = {125.99999999999997, 49.0}, 
        points = {{-12.0, 0.0}, {2.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(fixedTranslation.frame_b, body.frame_a)
      annotation (Line(origin = {165.0, 49.0}, 
        points = {{-17.0, 0.0}, {-7.0, 0.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(absolutePosition.frame_a, bodyShape1.frame_a)
      annotation (Line(origin = {52.99999999999997, -17.0}, 
        points = {{95.0, 96.0}, {-5.0, 96.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(speedSensor.flange, revolute.axis)
      annotation (Line(origin = {128.99999999999997, 81.0}, 
        points = {{9.0, -60.0}, {-25.0, -60.0}, {-25.0, -42.0}}, 
        color = {0, 0, 0}, 
        thickness = 1.0));
    connect(absoluteVelocity.frame_a, bodyShape1.frame_a)
      annotation (Line(origin = {61.99999999999997, -42.0}, 
        points = {{106.0, 145.0}, {-4.0, 145.0}, {-4.0, 121.0}, {-14.0, 121.0}}, 
        color = {95, 95, 95}, 
        thickness = 1.0));
    connect(angleSensor.phi, K1.u)
      annotation (Line(origin = {177.0, -63.0}, 
        points = {{-44.0, 66.0}, {-23.0, 66.0}, {-23.0, 18.0}, {-41.0, 18.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(speedSensor.w, K2.u)
      annotation (Line(origin = {183.0, -56.0}, 
        points = {{-24.0, 77.0}, {-13.0, 77.0}, {-13.0, -9.0}, {-69.0, -9.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(absolutePosition.r[1], K3.u)
      annotation (Line(origin = {57.99999999999997, -138.0}, 
        points = {{111.0, 217.0}, {134.0, 217.0}, {134.0, 53.0}, {34.0, 53.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(absoluteVelocity.v[1], K4.u)
      annotation (Line(origin = {40.99999999999997, -164.0}, 
        points = {{148.0, 267.0}, {161.0, 267.0}, {161.0, 57.0}, {29.0, 57.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(feedback.y, force.force[1])
      annotation (Line(origin = {54.99999999999997, 12.0}, 
        points = {{-140.0, 11.0}, {-81.0, 11.0}, {-81.0, 67.0}, {-65.0, 67.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(x5.y, Kl.u)
      annotation (Line(origin = {-165.5, 7.0}, 
        points = {{9.0, 16.0}, {26.0, 16.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(feedback2.y, x5.u)
      annotation (Line(origin = {-206.5, 7.0}, 
        points = {{8.0, 16.0}, {27.0, 16.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(feedback2.u2, absolutePosition.r[1])
      annotation (Line(origin = {-80.00000000000003, -133.0}, 
        points = {{-127.0, 148.0}, {-127.0, 4.0}, {272.0, 4.0}, {272.0, 212.0}, {249.0, 212.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(const1.y, force.force[2])
      annotation (Line(origin = {-23.000000000000025, -7.0}, 
        points = {{-20.0, 86.0}, {13.0, 86.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(const2.y, force.force[3])
      annotation (Line(origin = {-23.000000000000025, -22.0}, 
        points = {{-20.0, 71.0}, {-3.0, 71.0}, {-3.0, 101.0}, {13.0, 101.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(Kl.y, feedback.u1)
      annotation (Line(origin = {-116.00000000000003, 5.0}, 
        points = {{-1.0, 18.0}, {14.0, 18.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(K1.y, sum1.u[1])
      annotation (Line(origin = {45.99999999999997, -57.0}, 
        points = {{67.0, 12.0}, {-28.0, 12.0}, {-28.0, -8.0}, {-42.0, -8.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(K2.y, sum1.u[2])
      annotation (Line(origin = {40.99999999999997, -66.0}, 
        points = {{50.0, 1.0}, {-37.0, 1.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(K3.y, sum1.u[3])
      annotation (Line(origin = {35.99999999999997, -75.0}, 
        points = {{33.0, -10.0}, {-18.0, -10.0}, {-18.0, 10.0}, {-32.0, 10.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(K4.y, sum1.u[4])
      annotation (Line(origin = {25.999999999999975, -85.0}, 
        points = {{21.0, -22.0}, {-8.0, -22.0}, {-8.0, 20.0}, {-22.0, 20.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(sum1.y, feedback.u2)
      annotation (Line(origin = {-83.00000000000003, -34.0}, 
        points = {{64.0, -31.0}, {-11.0, -31.0}, {-11.0, 49.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
    connect(timeTable.y, feedback2.u1)
      annotation (Line(origin = {-182.0, 23.0}, 
        points = {{-47.0, 0.0}, {-33.0, 0.0}}, 
        color = {0, 0, 127}, 
        thickness = 1.0));
  end Demo40_InvertedPendlumWithControl;
  model Demo41_FrequencyEstimation "频率特性估算"
    extends Modelica.Icons.Example;
    Modelica.Mechanics.Translational.Components.Mass mass(m = 6000)
      annotation (Placement(transformation(origin = {-5.551115123125783e-16, 50.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 90.0)));
    Modelica.Mechanics.Translational.Components.Spring spring(c = 5000)
      annotation (Placement(transformation(origin = {-19.999999999999996, 10.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 90.0)));
    Modelica.Mechanics.Translational.Components.Damper damper(d = 1000)
      annotation (Placement(transformation(origin = {20.0, 10.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 90.0)));
    Modelica.Mechanics.Translational.Sensors.PositionSensor positionSensor
      annotation (Placement(transformation(origin = {40.0, 80.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Translational.Sources.Position position
      annotation (Placement(transformation(origin = {-42.0, -68.00000000000001}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Translational.Components.Mass mass1(m = 160)
      annotation (Placement(transformation(origin = {-3.552713678800501e-15, -30.000000000000014}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 90.0)));
    Modelica.Mechanics.Translational.Components.Spring spring1(c = 5000)
      annotation (Placement(transformation(origin = {-1.7763568394002505e-15, -58.000000000000014}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 90.0)));
  protected 
    Modelica.Blocks.Interfaces.RealInput s_ref "Reference position of flange as input signal" 
      annotation (Placement(transformation(origin = {-90.0, -68.0}, 
        extent = {{-20.0, -20.0}, {20.0, 20.0}}), 
        iconTransformation(origin = {-67.99999999999999, 0.0}, 
          extent = {{-20.0, -20.0}, {20.0, 20.0}})));
  public 
    Modelica.Blocks.Interfaces.RealOutput s "Absolute position of flange as output signal" 
      annotation (Placement(transformation(origin = {74.0, 80.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}), 
        iconTransformation(origin = {86.0, -6.661338147750939e-16}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  equation 
    connect(damper.flange_b, mass.flange_a)
      annotation (Line(origin = {8.0, 26.0}, 
        points = {{12.0, -6.0}, {12.0, 4.0}, {-8.0, 4.0}, {-8.0, 14.0}}, 
        color = {0, 127, 0}));
    connect(spring.flange_b, mass.flange_a)
      annotation (Line(origin = {-9.0, 26.0}, 
        points = {{-11.0, -6.0}, {-11.0, 4.0}, {9.0, 4.0}, {9.0, 14.0}}, 
        color = {0, 127, 0}));
    connect(spring.flange_a, mass1.flange_b)
      annotation (Line(origin = {-10.0, -10.0}, 
        points = {{-10.0, 10.0}, {-10.0, 0.0}, {10.0, 0.0}, {10.0, -10.0}}, 
        color = {0, 127, 0}));
    connect(damper.flange_a, mass1.flange_b)
      annotation (Line(origin = {10.0, -10.0}, 
        points = {{10.0, 10.0}, {10.0, 0.0}, {-10.0, 0.0}, {-10.0, -10.0}}, 
        color = {0, 127, 0}));
    connect(mass1.flange_a, spring1.flange_b)
      annotation (Line(origin = {0.0, -44.0}, 
        points = {{0.0, 4.0}, {0.0, -4.0}}, 
        color = {0, 127, 0}));
    connect(position.flange, spring1.flange_a)
      annotation (Line(origin = {-16.0, -68.0}, 
        points = {{-16.0, 0.0}, {16.0, 0.0}}, 
        color = {0, 127, 0}));
    connect(position.s_ref, s_ref)
      annotation (Line(origin = {-69.0, -68.0}, 
        points = {{15.0, 0.0}, {-21.0, 0.0}}, 
        color = {0, 0, 127}));
    connect(mass.flange_b, positionSensor.flange)
      annotation (Line(origin = {15.0, 70.0}, 
        points = {{-15.0, -10.0}, {-15.0, 10.0}, {15.0, 10.0}}, 
        color = {0, 127, 0}));
    connect(positionSensor.s, s)
      annotation (Line(origin = {58.0, 80.0}, 
        points = {{-7.0, 0.0}, {16.0, 0.0}}, 
        color = {0, 0, 127}));
  end Demo41_FrequencyEstimation;
end MWORKS_ControlSystemToolbox_Demo;