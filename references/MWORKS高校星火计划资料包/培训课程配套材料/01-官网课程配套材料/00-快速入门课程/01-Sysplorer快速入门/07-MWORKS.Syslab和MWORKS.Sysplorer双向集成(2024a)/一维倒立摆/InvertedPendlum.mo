within ;
package InvertedPendlum "一阶倒立摆"
  extends Modelica.Icons.ExamplesPackage;
  package Systems "系统模型"
    model InvertedPendlumWithControl_System "倒立摆闭环控制系统"
      inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity, animateWorld = false, animateGravity = false)
        annotation (Placement(transformation(origin = {-2.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic
        annotation (Placement(transformation(origin = {36.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, 
        phi(start
           = 0.349065850398866, fixed
           = true))
        annotation (Placement(transformation(origin = {102.0, 46.0}, 
          extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
          rotation = 360.0)));
      Modelica.Mechanics.MultiBody.Forces.WorldForce force
        annotation (Placement(transformation(origin = {0.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Blocks.Sources.Constant const1(k = 0)
        annotation (Placement(transformation(origin = {-56.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Blocks.Sources.Constant const2(k = 0)
        annotation (Placement(transformation(origin = {-56.0, 46.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Mechanics.MultiBody.Sensors.AbsolutePosition absolutePosition
        annotation (Placement(transformation(origin = {156.0, 76.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.Rotational.Sensors.AngleSensor angleSensor
        annotation (Placement(transformation(origin = {120.0, 0.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.BodyShape M(m = 2, 
        shapeType = "box", length = 0.25, width = 0.125, 
        animateSphere = false, 
        r_shape = {-0.125, 0, 0})
        annotation (Placement(transformation(origin = {36.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.Body m(sphereColor = {255, 255, 0}, sphereDiameter = 0.1, m = 0.1, 
        r_CM = {0, 0.5, 0})
        annotation (Placement(transformation(origin = {166.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor
        annotation (Placement(transformation(origin = {146.0, 18.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Sensors.AbsoluteVelocity absoluteVelocity
        annotation (Placement(transformation(origin = {176.0, 100.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain K3(k = -494.898)
        annotation (Placement(transformation(origin = {78.0, -88.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
          rotation = 180.0)));
      Modelica.Blocks.Math.Gain K2(k = -255.995)
        annotation (Placement(transformation(origin = {100.0, -68.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
          rotation = 180.0)));
      Modelica.Blocks.Math.Gain K1(k = -982.029)
        annotation (Placement(transformation(origin = {122.0, -48.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
          rotation = 180.0)));
      Modelica.Blocks.Math.Feedback feedback
        annotation (Placement(transformation(origin = {-96.0, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain K4(k = -419.19)
        annotation (Placement(transformation(origin = {56.0, -110.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
          rotation = 180.0)));
      Modelica.Blocks.Continuous.Integrator x5
        annotation (Placement(transformation(origin = {-169.5, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain Kl(k = -306.12)
        annotation (Placement(transformation(origin = {-129.5, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
          rotation = 360.0)));
      Modelica.Blocks.Math.Feedback feedback2
        annotation (Placement(transformation(origin = {-209.5, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Sum sum1(nin = 4)
        annotation (Placement(transformation(origin = {-10.0, -68.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {1, 1}, {8, 1}, {8, -1}, {16, -1}, {16, 0}, {17, 0}})
        annotation (Placement(transformation(origin = {-242.0, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      annotation (Diagram(coordinateSystem(extent = {{-300.0, -200.0}, {300.0, 200.0}}, 
        grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.0, -61.0}, 
        fillColor = {255, 242, 219}, 
        fillPattern = FillPattern.Solid, 
        points = {{-217.0, 101.0}, {-73.0, 101.0}, {-73.0, 31.0}, {219.0, 31.0}, {219.0, -101.0}, {-219.0, -101.0}}), Text(origin = {-166.74999999999997, -149.4705882352941}, 
        extent = {{-52.75000000000003, 14.529411764705912}, {52.74999999999997, -14.529411764705912}}, 
        textString = "Controller", 
        fontSize = 16, 
        fontName = "Consolas", 
        textStyle = {TextStyle.Bold}), Rectangle(origin = {71.0, 52.372727272727275}, 
        lineColor = {156, 156, 156}, 
        fillColor = {230, 230, 230}, 
        pattern = LinePattern.Dash, 
        fillPattern = FillPattern.Solid, 
        lineThickness = 1.0, 
        extent = {{-141.0, 75.62727272727273}, {141.0, -75.62727272727273}}, 
        radius = 5.0), Text(origin = {-31.75, 118.24999999999997}, 
        lineColor = {0, 0, 0}, 
        extent = {{-25.75, 5.750000000000028}, {25.75, -5.750000000000028}}, 
        textString = "Plant", 
        fontSize = 16, 
        fontName = "Consolas", 
        textStyle = {TextStyle.None, TextStyle.Bold}, 
        textColor = {0, 0, 0}, 
        horizontalAlignment = LinePattern.None)}), 
        Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
          lineColor = {200, 200, 200}, 
          fillColor = {248, 248, 248}, 
          fillPattern = FillPattern.HorizontalCylinder, 
          extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          radius = 25.0), Rectangle(origin = {0.0, 0.0}, 
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
          points = {{-10.0, 0.0}, {5.0, 5.0}, {5.0, -5.0}})}), 
        __MWorks(ResultViewerManager(resultViewers = {
          ResultViewer(name = "默认", executeTrigger = executeTrigger.SimulationFinished, commands = {
          CreatePlot(id = 1, position = [0, 0, 600, 400], y = ["timeTable.y", "absolutePosition.r[1]"], x_display_unit = "s", y_display_units = ["", "m"], y_axis = [1, 1], legend_layout = 7, legend_frame = True, curve_vernier = True, fix_time_range_value = 6.95325e-310), 
          CreatePlot(id = 2, position = [0, 400, 600, 400], y = ["angleSensor.flange.phi"], x_display_unit = "s", y_display_units = ["deg"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg]", curve_vernier = True, fix_time_range_value = 6.95325e-310), 
          CreatePlot(id = 3, position = [600, 0, 600, 400], y = ["speedSensor.w"], x_display_unit = "s", y_display_units = ["deg/s"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg/s]", curve_vernier = True, fix_time_range_value = 6.95325e-310)})})), 
        experiment(StopTime = 50, NumberOfIntervals = 5000));
    equation 
      connect(world.frame_b, prismatic.frame_a)
        annotation (Line(origin = {-6.0, 46.0}, 
          points = {{14.0, 0.0}, {32.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(revolute.axis, angleSensor.flange)
        annotation (Line(origin = {128.0, 41.0}, 
          points = {{-26.0, -5.0}, {-26.0, -41.0}, {-18.0, -41.0}}, 
          color = {0, 0, 0}, 
          thickness = 1.0));
      connect(force.frame_b, M.frame_b)
        annotation (Line(origin = {85.0, 0.0}, 
          points = {{-75.0, 76.0}, {-59.0, 76.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(M.frame_a, prismatic.frame_b)
        annotation (Line(origin = {53.0, 33.0}, 
          points = {{-7.0, 43.0}, {3.0, 43.0}, {3.0, 13.0}, {-7.0, 13.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(absolutePosition.frame_a, M.frame_a)
        annotation (Line(origin = {51.0, -20.0}, 
          points = {{95.0, 96.0}, {-5.0, 96.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(speedSensor.flange, revolute.axis)
        annotation (Line(origin = {127.0, 78.0}, 
          points = {{9.0, -60.0}, {-25.0, -60.0}, {-25.0, -42.0}}, 
          color = {0, 0, 0}, 
          thickness = 1.0));
      connect(absoluteVelocity.frame_a, M.frame_a)
        annotation (Line(origin = {60.0, -45.0}, 
          points = {{106.0, 145.0}, {-4.0, 145.0}, {-4.0, 121.0}, {-14.0, 121.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(angleSensor.phi, K1.u)
        annotation (Line(origin = {175.0, -66.0}, 
          points = {{-44.0, 66.0}, {-23.0, 66.0}, {-23.0, 18.0}, {-41.0, 18.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(speedSensor.w, K2.u)
        annotation (Line(origin = {181.0, -59.0}, 
          points = {{-24.0, 77.0}, {-13.0, 77.0}, {-13.0, -9.0}, {-69.0, -9.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absolutePosition.r[1], K3.u)
        annotation (Line(origin = {56.0, -141.0}, 
          points = {{111.0, 217.0}, {134.0, 217.0}, {134.0, 53.0}, {34.0, 53.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absoluteVelocity.v[1], K4.u)
        annotation (Line(origin = {39.0, -167.0}, 
          points = {{148.0, 267.0}, {161.0, 267.0}, {161.0, 57.0}, {29.0, 57.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback.y, force.force[1])
        annotation (Line(origin = {53.0, 9.0}, 
          points = {{-140.0, 11.0}, {-81.0, 11.0}, {-81.0, 67.0}, {-65.0, 67.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(x5.y, Kl.u)
        annotation (Line(origin = {-167.5, 4.0}, 
          points = {{9.0, 16.0}, {26.0, 16.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback2.y, x5.u)
        annotation (Line(origin = {-208.5, 4.0}, 
          points = {{8.0, 16.0}, {27.0, 16.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback2.u2, absolutePosition.r[1])
        annotation (Line(origin = {-82.0, -136.0}, 
          points = {{-128.0, 148.0}, {-128.0, 4.0}, {272.0, 4.0}, {272.0, 212.0}, {249.0, 212.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(const1.y, force.force[2])
        annotation (Line(origin = {-25.0, -10.0}, 
          points = {{-20.0, 86.0}, {13.0, 86.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(const2.y, force.force[3])
        annotation (Line(origin = {-25.0, -25.0}, 
          points = {{-20.0, 71.0}, {-3.0, 71.0}, {-3.0, 101.0}, {13.0, 101.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(Kl.y, feedback.u1)
        annotation (Line(origin = {-118.0, 2.0}, 
          points = {{-1.0, 18.0}, {14.0, 18.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K1.y, sum1.u[1])
        annotation (Line(origin = {44.0, -60.0}, 
          points = {{67.0, 12.0}, {-28.0, 12.0}, {-28.0, -8.0}, {-42.0, -8.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K2.y, sum1.u[2])
        annotation (Line(origin = {39.0, -69.0}, 
          points = {{50.0, 1.0}, {-37.0, 1.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K3.y, sum1.u[3])
        annotation (Line(origin = {34.0, -78.0}, 
          points = {{33.0, -10.0}, {-18.0, -10.0}, {-18.0, 10.0}, {-32.0, 10.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K4.y, sum1.u[4])
        annotation (Line(origin = {24.0, -88.0}, 
          points = {{21.0, -22.0}, {-8.0, -22.0}, {-8.0, 20.0}, {-22.0, 20.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(sum1.y, feedback.u2)
        annotation (Line(origin = {-85.0, -37.0}, 
          points = {{64.0, -31.0}, {-11.0, -31.0}, {-11.0, 49.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(timeTable.y, feedback2.u1)
        annotation (Line(origin = {-184.0, 20.0}, 
          points = {{-47.0, 0.0}, {-34.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(prismatic.frame_b, revolute.frame_b)
        annotation (Line(origin = {69.0, 46.0}, 
          points = {{-23.0, 0.0}, {23.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(revolute.frame_a, m.frame_a)
        annotation (Line(origin = {134.0, 46.0}, 
          points = {{-22.0, 0.0}, {22.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
    end InvertedPendlumWithControl_System;
    model InvertedPendlumWithControl_CPS "倒立摆系统-信息物理深度融合"
      inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity, animateWorld = false, animateGravity = false)
        annotation (Placement(transformation(origin = {-2.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic
        annotation (Placement(transformation(origin = {36.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, 
        phi(start
           = 0.349065850398866, fixed
           = true))
        annotation (Placement(transformation(origin = {102.0, 46.0}, 
          extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
          rotation = 360.0)));
      Modelica.Mechanics.MultiBody.Forces.WorldForce force
        annotation (Placement(transformation(origin = {0.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Blocks.Sources.Constant const1(k = 0)
        annotation (Placement(transformation(origin = {-56.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Blocks.Sources.Constant const2(k = 0)
        annotation (Placement(transformation(origin = {-56.0, 46.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Mechanics.MultiBody.Sensors.AbsolutePosition absolutePosition
        annotation (Placement(transformation(origin = {156.0, 76.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.Rotational.Sensors.AngleSensor angleSensor
        annotation (Placement(transformation(origin = {120.0, 0.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.BodyShape bodyShape1(m = 2, 
        shapeType = "box", length = 0.25, width = 0.125, 
        animateSphere = false, 
        r_shape = {-0.125, 0, 0})
        annotation (Placement(transformation(origin = {36.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.Body body(sphereColor = {255, 255, 0}, sphereDiameter = 0.1, m = 0.1, 
        r_CM = {0, 0.5, 0})
        annotation (Placement(transformation(origin = {166.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor
        annotation (Placement(transformation(origin = {146.0, 18.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Sensors.AbsoluteVelocity absoluteVelocity
        annotation (Placement(transformation(origin = {176.0, 100.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      BasicModels.Gain K3 annotation (Placement(transformation(origin = {78.0, -88.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      BasicModels.Gain K2 annotation (Placement(transformation(origin = {100.0, -68.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      BasicModels.Gain K1 annotation (Placement(transformation(origin = {122.0, -48.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      Modelica.Blocks.Math.Feedback feedback
        annotation (Placement(transformation(origin = {-96.0, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      BasicModels.Gain K4 annotation (Placement(transformation(origin = {56.0, -110.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      Modelica.Blocks.Continuous.Integrator x5
        annotation (Placement(transformation(origin = {-169.5, 14.999999999999998}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      BasicModels.Gain Kl annotation (Placement(transformation(origin = {-129.5, 20.0}, 
        extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
        rotation = -360.0)));
      Modelica.Blocks.Math.Feedback feedback2
        annotation (Placement(transformation(origin = {-209.5, 14.999999999999998}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Sum sum1(nin = 4)
        annotation (Placement(transformation(origin = {-10.0, -68.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {1, 1}, {8, 1}, {8, -1}, {16, -1}, {16, 0}, {17, 0}})
        annotation (Placement(transformation(origin = {-249.5, 14.999999999999998}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.FromWorkspace.FromWorkspace_Vector fromWorkspace_Vector(varName = "K", row_dims = 4)
        annotation (Placement(transformation(origin = {256.99999999999994, -63.00000000000001}, 
          extent = {{17.000000000000057, -16.0}, {-17.0, 16.000000000000007}})));
      SyslabWorkspace.FromWorkspace.FromWorkspace_Scale fromWorkspace_Scale(varName = "k1")
        annotation (Placement(transformation(origin = {-169.5, 60.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale(varName = "v")
        annotation (Placement(transformation(origin = {250.0, 100.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale1(varName = "x")
        annotation (Placement(transformation(origin = {250.0, 76.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale2(varName = "w")
        annotation (Placement(transformation(origin = {250.0, 18.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale3(varName = "phi")
        annotation (Placement(transformation(origin = {250.0, 2.220446049250313e-16}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      annotation (Diagram(coordinateSystem(extent = {{-300.0, -200.0}, {300.0, 200.0}}, 
        grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.0, -61.0}, 
        fillColor = {255, 242, 219}, 
        fillPattern = FillPattern.Solid, 
        points = {{-217.0, 101.0}, {-73.0, 101.0}, {-73.0, 31.0}, {219.0, 31.0}, {219.0, -101.0}, {-219.0, -101.0}}), Text(origin = {-166.74999999999997, -149.4705882352941}, 
        extent = {{-52.75000000000003, 14.529411764705912}, {52.74999999999997, -14.529411764705912}}, 
        textString = "Controller", 
        fontSize = 16, 
        fontName = "Consolas", 
        textStyle = {TextStyle.Bold}), Rectangle(origin = {71.0, 52.372727272727275}, 
        lineColor = {156, 156, 156}, 
        fillColor = {230, 230, 230}, 
        pattern = LinePattern.Dash, 
        fillPattern = FillPattern.Solid, 
        lineThickness = 1.0, 
        extent = {{-141.0, 75.62727272727273}, {141.0, -75.62727272727273}}, 
        radius = 5.0), Text(origin = {-31.75, 118.24999999999997}, 
        lineColor = {0, 0, 0}, 
        extent = {{-25.75, 5.750000000000028}, {25.75, -5.750000000000028}}, 
        textString = "Plant", 
        fontSize = 16, 
        fontName = "Consolas", 
        textStyle = {TextStyle.None, TextStyle.Bold}, 
        textColor = {0, 0, 0}, 
        horizontalAlignment = LinePattern.None)}), 
        Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
          lineColor = {200, 200, 200}, 
          fillColor = {248, 248, 248}, 
          fillPattern = FillPattern.HorizontalCylinder, 
          extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          radius = 25.0), Rectangle(origin = {0.0, 0.0}, 
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
          points = {{-10.0, 0.0}, {5.0, 5.0}, {5.0, -5.0}})}), 
        __MWorks(ResultViewerManager(resultViewers = {
          ResultViewer(name = "默认", executeTrigger = executeTrigger.SimulationFinished, commands = {
          CreatePlot(id = 1, position = [0, 0, 600, 400], y = ["timeTable.y", "absolutePosition.r[1]"], x_display_unit = "s", y_display_units = ["", "m"], y_axis = [1, 1], legend_layout = 7, legend_frame = True, curve_vernier = True, fix_time_range_value = 6.95325e-310), 
          CreatePlot(id = 2, position = [0, 400, 600, 400], y = ["angleSensor.flange.phi"], x_display_unit = "s", y_display_units = ["deg"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg]", curve_vernier = True, fix_time_range_value = 6.95325e-310), 
          CreatePlot(id = 3, position = [600, 0, 600, 400], y = ["speedSensor.w"], x_display_unit = "s", y_display_units = ["deg/s"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg/s]", curve_vernier = True, fix_time_range_value = 6.95325e-310)})})), 
        experiment(StopTime = 50, NumberOfIntervals = 5000));
    equation 
      connect(world.frame_b, prismatic.frame_a)
        annotation (Line(origin = {-6.0, 46.0}, 
          points = {{14.0, 0.0}, {32.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(revolute.axis, angleSensor.flange)
        annotation (Line(origin = {128.0, 41.0}, 
          points = {{-26.0, -5.0}, {-26.0, -41.0}, {-18.0, -41.0}}, 
          color = {0, 0, 0}, 
          thickness = 1.0));
      connect(force.frame_b, bodyShape1.frame_b)
        annotation (Line(origin = {85.0, 0.0}, 
          points = {{-75.0, 76.0}, {-59.0, 76.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(bodyShape1.frame_a, prismatic.frame_b)
        annotation (Line(origin = {53.0, 33.0}, 
          points = {{-7.0, 43.0}, {3.0, 43.0}, {3.0, 13.0}, {-7.0, 13.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(absolutePosition.frame_a, bodyShape1.frame_a)
        annotation (Line(origin = {51.0, -20.0}, 
          points = {{95.0, 96.0}, {-5.0, 96.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(speedSensor.flange, revolute.axis)
        annotation (Line(origin = {127.0, 78.0}, 
          points = {{9.0, -60.0}, {-25.0, -60.0}, {-25.0, -42.0}}, 
          color = {0, 0, 0}, 
          thickness = 1.0));
      connect(absoluteVelocity.frame_a, bodyShape1.frame_a)
        annotation (Line(origin = {60.0, -45.0}, 
          points = {{106.0, 145.0}, {-4.0, 145.0}, {-4.0, 121.0}, {-14.0, 121.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(angleSensor.phi, K1.u)
        annotation (Line(origin = {175.0, -66.0}, 
          points = {{-44.0, 66.0}, {-23.0, 66.0}, {-23.0, 13.0}, {-41.0, 13.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(speedSensor.w, K2.u)
        annotation (Line(origin = {181.0, -59.0}, 
          points = {{-24.0, 77.0}, {-13.0, 77.0}, {-13.0, -14.0}, {-69.0, -14.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absolutePosition.r[1], K3.u)
        annotation (Line(origin = {56.0, -141.0}, 
          points = {{111.0, 217.0}, {134.0, 217.0}, {134.0, 48.0}, {34.0, 48.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absoluteVelocity.v[1], K4.u)
        annotation (Line(origin = {39.0, -167.0}, 
          points = {{148.0, 267.0}, {161.0, 267.0}, {161.0, 52.0}, {29.0, 52.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback.y, force.force[1])
        annotation (Line(origin = {53.0, 9.0}, 
          points = {{-140.0, 11.0}, {-81.0, 11.0}, {-81.0, 67.0}, {-65.0, 67.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(x5.y, Kl.u)
        annotation (Line(origin = {-167.5, 4.0}, 
          points = {{9.0, 11.0}, {26.0, 11.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback2.y, x5.u)
        annotation (Line(origin = {-208.5, 4.0}, 
          points = {{8.0, 11.0}, {27.0, 11.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback2.u2, absolutePosition.r[1])
        annotation (Line(origin = {-82.0, -136.0}, 
          points = {{-128.0, 143.0}, {-128.0, 4.0}, {272.0, 4.0}, {272.0, 212.0}, {249.0, 212.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(const1.y, force.force[2])
        annotation (Line(origin = {-25.0, -10.0}, 
          points = {{-20.0, 86.0}, {13.0, 86.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(const2.y, force.force[3])
        annotation (Line(origin = {-25.0, -25.0}, 
          points = {{-20.0, 71.0}, {-3.0, 71.0}, {-3.0, 101.0}, {13.0, 101.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(Kl.y, feedback.u1)
        annotation (Line(origin = {-118.0, 2.0}, 
          points = {{-1.0, 18.0}, {14.0, 18.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K1.y, sum1.u[1])
        annotation (Line(origin = {44.0, -60.0}, 
          points = {{67.0, 12.0}, {-28.0, 12.0}, {-28.0, -8.0}, {-42.0, -8.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K2.y, sum1.u[2])
        annotation (Line(origin = {39.0, -69.0}, 
          points = {{50.0, 1.0}, {-37.0, 1.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K3.y, sum1.u[3])
        annotation (Line(origin = {34.0, -78.0}, 
          points = {{33.0, -10.0}, {-18.0, -10.0}, {-18.0, 10.0}, {-32.0, 10.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K4.y, sum1.u[4])
        annotation (Line(origin = {24.0, -88.0}, 
          points = {{21.0, -22.0}, {-8.0, -22.0}, {-8.0, 20.0}, {-22.0, 20.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(sum1.y, feedback.u2)
        annotation (Line(origin = {-85.0, -37.0}, 
          points = {{64.0, -31.0}, {-11.0, -31.0}, {-11.0, 49.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(timeTable.y, feedback2.u1)
        annotation (Line(origin = {-184.0, 20.0}, 
          points = {{-55.0, -5.0}, {-34.0, -5.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(fromWorkspace_Vector.outputs[1], K1.k)
        annotation (Line(origin = {180.0, -54.0}, 
          points = {{58.0, -9.0}, {28.0, -9.0}, {28.0, 11.0}, {-46.0, 11.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(fromWorkspace_Vector.outputs[2], K2.k)
        annotation (Line(origin = {169.0, -64.0}, 
          points = {{69.0, 1.0}, {-57.0, 1.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(fromWorkspace_Vector.outputs[3], K3.k)
        annotation (Line(origin = {158.0, -73.0}, 
          points = {{80.0, 10.0}, {50.0, 10.0}, {50.0, -10.0}, {-68.0, -10.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(fromWorkspace_Vector.outputs[4], K4.k)
        annotation (Line(origin = {147.0, -84.0}, 
          points = {{91.0, 21.0}, {61.0, 21.0}, {61.0, -21.0}, {-79.0, -21.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(fromWorkspace_Scale.outputs, Kl.k)
        annotation (Line(origin = {-150.0, 43.0}, 
          points = {{-9.0, 17.0}, {2.0, 17.0}, {2.0, -18.0}, {9.0, -18.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(angleSensor.phi, toWorkspace_Scale3.dataInput)
        annotation (Line(origin = {185.0, 0.0}, 
          points = {{-54.0, 0.0}, {54.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(speedSensor.w, toWorkspace_Scale2.dataInput)
        annotation (Line(origin = {198.0, 18.0}, 
          points = {{-41.0, 0.0}, {41.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absolutePosition.r[1], toWorkspace_Scale1.dataInput)
        annotation (Line(origin = {203.0, 76.0}, 
          points = {{-36.0, 0.0}, {36.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(toWorkspace_Scale.dataInput, K4.u)
        annotation (Line(origin = {154.0, -7.0}, 
          points = {{85.0, 107.0}, {46.0, 107.0}, {46.0, -108.0}, {-86.0, -108.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(prismatic.frame_b, revolute.frame_b)
        annotation (Line(origin = {69.0, 46.0}, 
          points = {{-23.0, 0.0}, {23.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(revolute.frame_a, body.frame_a)
        annotation (Line(origin = {134.0, 46.0}, 
          points = {{-22.0, 0.0}, {22.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
    end InvertedPendlumWithControl_CPS;

    model InvertedPendlumWithControl_CPS2 "倒立摆系统-信息物理深度融合"
      parameter Real k1 = SyslabWorkspace.FromWorkspace.Functions.FwReal("k1");
      parameter Real K[4] = SyslabWorkspace.FromWorkspace.Functions.FwRealVector("K", 4);
      inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity, animateWorld = false, animateGravity = false)
        annotation (Placement(transformation(origin = {-2.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic
        annotation (Placement(transformation(origin = {36.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, 
        phi(start
           = 0.349065850398866, fixed
           = true))
        annotation (Placement(transformation(origin = {102.0, 46.0}, 
          extent = {{10.0, 10.0}, {-10.0, -10.0}}, 
          rotation = 360.0)));
      Modelica.Mechanics.MultiBody.Forces.WorldForce force
        annotation (Placement(transformation(origin = {0.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Blocks.Sources.Constant const1(k = 0)
        annotation (Placement(transformation(origin = {-56.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Blocks.Sources.Constant const2(k = 0)
        annotation (Placement(transformation(origin = {-56.0, 46.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
      Modelica.Mechanics.MultiBody.Sensors.AbsolutePosition absolutePosition
        annotation (Placement(transformation(origin = {156.0, 76.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.Rotational.Sensors.AngleSensor angleSensor
        annotation (Placement(transformation(origin = {120.0, 0.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.BodyShape bodyShape1(m = 2, 
        shapeType = "box", length = 0.25, width = 0.125, 
        animateSphere = false, 
        r_shape = {-0.125, 0, 0})
        annotation (Placement(transformation(origin = {36.0, 76.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.Body body(sphereColor = {255, 255, 0}, sphereDiameter = 0.1, m = 0.1, 
        r_CM = {0, 0.5, 0})
        annotation (Placement(transformation(origin = {166.0, 46.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor
        annotation (Placement(transformation(origin = {146.0, 18.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Sensors.AbsoluteVelocity absoluteVelocity
        annotation (Placement(transformation(origin = {176.0, 100.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain K3(k = K[3]) annotation (Placement(transformation(origin = {78.0, -88.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      Modelica.Blocks.Math.Gain K2(k = K[2]) annotation (Placement(transformation(origin = {100.0, -68.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      Modelica.Blocks.Math.Gain K1(k = K[1]) annotation (Placement(transformation(origin = {122.0, -48.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      Modelica.Blocks.Math.Feedback feedback
        annotation (Placement(transformation(origin = {-96.0, 20.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain K4(k = K[4]) annotation (Placement(transformation(origin = {56.0, -110.0}, 
        extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
        rotation = 180.0)));
      Modelica.Blocks.Continuous.Integrator x5
        annotation (Placement(transformation(origin = {-169.5, 19.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain Kl(k = k1) annotation (Placement(transformation(origin = {-129.5, 20.0}, 
        extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
        rotation = -360.0)));
      Modelica.Blocks.Math.Feedback feedback2
        annotation (Placement(transformation(origin = {-209.5, 19.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Sum sum1(nin = 4)
        annotation (Placement(transformation(origin = {-10.0, -68.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Blocks.Sources.TimeTable timeTable(table = {{0, 1}, {1, 1}, {8, 1}, {8, -1}, {16, -1}, {16, 0}, {17, 0}})
        annotation (Placement(transformation(origin = {-249.5, 19.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale(varName = "v")
        annotation (Placement(transformation(origin = {250.0, 100.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale1(varName = "x")
        annotation (Placement(transformation(origin = {250.0, 76.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale2(varName = "w")
        annotation (Placement(transformation(origin = {250.0, 18.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      SyslabWorkspace.ToWorkspace.ToWorkspace_Scale toWorkspace_Scale3(varName = "phi")
        annotation (Placement(transformation(origin = {250.0, 2.220446049250313e-16}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      annotation (Diagram(coordinateSystem(extent = {{-300.0, -200.0}, {300.0, 200.0}}, 
        grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.0, -61.0}, 
        fillColor = {255, 242, 219}, 
        fillPattern = FillPattern.Solid, 
        points = {{-217.0, 101.0}, {-73.0, 101.0}, {-73.0, 31.0}, {219.0, 31.0}, {219.0, -101.0}, {-219.0, -101.0}}), Text(origin = {-166.74999999999997, -149.4705882352941}, 
        extent = {{-52.75000000000003, 14.529411764705912}, {52.74999999999997, -14.529411764705912}}, 
        textString = "Controller", 
        fontSize = 16, 
        fontName = "Consolas", 
        textStyle = {TextStyle.Bold}), Rectangle(origin = {71.0, 52.372727272727275}, 
        lineColor = {156, 156, 156}, 
        fillColor = {230, 230, 230}, 
        pattern = LinePattern.Dash, 
        fillPattern = FillPattern.Solid, 
        lineThickness = 1.0, 
        extent = {{-141.0, 75.62727272727273}, {141.0, -75.62727272727273}}, 
        radius = 5.0), Text(origin = {-31.75, 118.24999999999997}, 
        lineColor = {0, 0, 0}, 
        extent = {{-25.75, 5.750000000000028}, {25.75, -5.750000000000028}}, 
        textString = "Plant", 
        fontSize = 16, 
        fontName = "Consolas", 
        textStyle = {TextStyle.None, TextStyle.Bold}, 
        textColor = {0, 0, 0}, 
        horizontalAlignment = LinePattern.None)}), 
        Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
          lineColor = {200, 200, 200}, 
          fillColor = {248, 248, 248}, 
          fillPattern = FillPattern.HorizontalCylinder, 
          extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          radius = 25.0), Rectangle(origin = {0.0, 0.0}, 
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
          points = {{-10.0, 0.0}, {5.0, 5.0}, {5.0, -5.0}})}), 
        __MWorks(ResultViewerManager(resultViewers = {
          ResultViewer(name = "默认", executeTrigger = executeTrigger.SimulationFinished, commands = {
          CreatePlot(id = 1, position = [0, 0, 600, 400], y = ["timeTable.y", "absolutePosition.r[1]"], x_display_unit = "s", y_display_units = ["", "m"], y_axis = [1, 1], legend_layout = 7, legend_frame = True, curve_vernier = True, fix_time_range_value = 6.95325e-310), 
          CreatePlot(id = 2, position = [0, 400, 600, 400], y = ["angleSensor.flange.phi"], x_display_unit = "s", y_display_units = ["deg"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg]", curve_vernier = True, fix_time_range_value = 6.95325e-310), 
          CreatePlot(id = 3, position = [600, 0, 600, 400], y = ["speedSensor.w"], x_display_unit = "s", y_display_units = ["deg/s"], y_axis = [1], legend_layout = 7, legend_frame = True, left_title = "[deg/s]", curve_vernier = True, fix_time_range_value = 6.95325e-310)})})), 
        experiment(StopTime = 50, NumberOfIntervals = 5000));
    equation 
      connect(world.frame_b, prismatic.frame_a)
        annotation (Line(origin = {-6.0, 46.0}, 
          points = {{14.0, 0.0}, {32.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(revolute.axis, angleSensor.flange)
        annotation (Line(origin = {128.0, 41.0}, 
          points = {{-26.0, -5.0}, {-26.0, -41.0}, {-18.0, -41.0}}, 
          color = {0, 0, 0}, 
          thickness = 1.0));
      connect(force.frame_b, bodyShape1.frame_b)
        annotation (Line(origin = {85.0, 0.0}, 
          points = {{-75.0, 76.0}, {-59.0, 76.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(bodyShape1.frame_a, prismatic.frame_b)
        annotation (Line(origin = {53.0, 33.0}, 
          points = {{-7.0, 43.0}, {3.0, 43.0}, {3.0, 13.0}, {-7.0, 13.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(absolutePosition.frame_a, bodyShape1.frame_a)
        annotation (Line(origin = {51.0, -20.0}, 
          points = {{95.0, 96.0}, {-5.0, 96.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(speedSensor.flange, revolute.axis)
        annotation (Line(origin = {127.0, 78.0}, 
          points = {{9.0, -60.0}, {-25.0, -60.0}, {-25.0, -42.0}}, 
          color = {0, 0, 0}, 
          thickness = 1.0));
      connect(absoluteVelocity.frame_a, bodyShape1.frame_a)
        annotation (Line(origin = {60.0, -45.0}, 
          points = {{106.0, 145.0}, {-4.0, 145.0}, {-4.0, 121.0}, {-14.0, 121.0}}, 
          color = {95, 95, 95}, 
          thickness = 1.0));
      connect(angleSensor.phi, K1.u)
        annotation (Line(origin = {175.0, -66.0}, 
          points = {{-44.0, 66.0}, {-23.0, 66.0}, {-23.0, 13.0}, {-41.0, 13.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(speedSensor.w, K2.u)
        annotation (Line(origin = {181.0, -59.0}, 
          points = {{-24.0, 77.0}, {-13.0, 77.0}, {-13.0, -14.0}, {-69.0, -14.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absolutePosition.r[1], K3.u)
        annotation (Line(origin = {56.0, -141.0}, 
          points = {{111.0, 217.0}, {134.0, 217.0}, {134.0, 48.0}, {34.0, 48.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absoluteVelocity.v[1], K4.u)
        annotation (Line(origin = {39.0, -167.0}, 
          points = {{148.0, 267.0}, {161.0, 267.0}, {161.0, 52.0}, {29.0, 52.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback.y, force.force[1])
        annotation (Line(origin = {53.0, 9.0}, 
          points = {{-140.0, 11.0}, {-81.0, 11.0}, {-81.0, 67.0}, {-65.0, 67.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(x5.y, Kl.u)
        annotation (Line(origin = {-167.5, 4.0}, 
          points = {{9.0, 15.0}, {26.0, 15.0}, {26.0, 16.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback2.y, x5.u)
        annotation (Line(origin = {-208.5, 4.0}, 
          points = {{8.0, 15.0}, {27.0, 15.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(feedback2.u2, absolutePosition.r[1])
        annotation (Line(origin = {-82.0, -136.0}, 
          points = {{-128.0, 147.0}, {-128.0, 4.0}, {272.0, 4.0}, {272.0, 212.0}, {249.0, 212.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(const1.y, force.force[2])
        annotation (Line(origin = {-25.0, -10.0}, 
          points = {{-20.0, 86.0}, {13.0, 86.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(const2.y, force.force[3])
        annotation (Line(origin = {-25.0, -25.0}, 
          points = {{-20.0, 71.0}, {-3.0, 71.0}, {-3.0, 101.0}, {13.0, 101.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(Kl.y, feedback.u1)
        annotation (Line(origin = {-118.0, 2.0}, 
          points = {{-1.0, 18.0}, {14.0, 18.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K1.y, sum1.u[1])
        annotation (Line(origin = {44.0, -60.0}, 
          points = {{67.0, 12.0}, {-28.0, 12.0}, {-28.0, -8.0}, {-42.0, -8.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K2.y, sum1.u[2])
        annotation (Line(origin = {39.0, -69.0}, 
          points = {{50.0, 1.0}, {-37.0, 1.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K3.y, sum1.u[3])
        annotation (Line(origin = {34.0, -78.0}, 
          points = {{33.0, -10.0}, {-18.0, -10.0}, {-18.0, 10.0}, {-32.0, 10.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(K4.y, sum1.u[4])
        annotation (Line(origin = {24.0, -88.0}, 
          points = {{21.0, -22.0}, {-8.0, -22.0}, {-8.0, 20.0}, {-22.0, 20.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(sum1.y, feedback.u2)
        annotation (Line(origin = {-85.0, -37.0}, 
          points = {{64.0, -31.0}, {-11.0, -31.0}, {-11.0, 49.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(timeTable.y, feedback2.u1)
        annotation (Line(origin = {-184.0, 20.0}, 
          points = {{-55.0, -1.0}, {-34.0, -1.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(angleSensor.phi, toWorkspace_Scale3.dataInput)
        annotation (Line(origin = {185.0, 0.0}, 
          points = {{-54.0, 0.0}, {54.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(speedSensor.w, toWorkspace_Scale2.dataInput)
        annotation (Line(origin = {198.0, 18.0}, 
          points = {{-41.0, 0.0}, {41.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(absolutePosition.r[1], toWorkspace_Scale1.dataInput)
        annotation (Line(origin = {203.0, 76.0}, 
          points = {{-36.0, 0.0}, {36.0, 0.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(toWorkspace_Scale.dataInput, K4.u)
        annotation (Line(origin = {154.0, -7.0}, 
          points = {{85.0, 107.0}, {46.0, 107.0}, {46.0, -108.0}, {-86.0, -108.0}}, 
          color = {0, 0, 127}, 
          thickness = 1.0));
      connect(prismatic.frame_b, revolute.frame_b)
        annotation (Line(origin = {69.0, 46.0}, 
          points = {{-23.0, 0.0}, {23.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(revolute.frame_a, body.frame_a)
        annotation (Line(origin = {134.0, 46.0}, 
          points = {{-22.0, 0.0}, {22.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
    end InvertedPendlumWithControl_CPS2;
  end Systems;
  package Plant "被控对象"
    model InvertedPendlum "倒立摆物理模型"
      annotation (Diagram(coordinateSystem(extent = {{-200.0, -100.0}, {200.0, 100.0}}, 
        grid = {2.0, 2.0}), graphics = {Rectangle(origin = {-12.0, -25.0}, 
        lineColor = {156, 156, 156}, 
        fillColor = {230, 230, 230}, 
        pattern = LinePattern.Dash, 
        fillPattern = FillPattern.Solid, 
        lineThickness = 1.0, 
        extent = {{-110.0, 59.0}, {110.0, -59.0}}, 
        radius = 5.0), Text(origin = {-94.0, 24.5}, 
        lineColor = {0, 0, 0}, 
        extent = {{-15.5, 5.5}, {15.5, -5.5}}, 
        textString = "Plant-", 
        fontName = "Consolas", 
        textStyle = {TextStyle.None, TextStyle.Bold}, 
        textColor = {0, 0, 0}, 
        horizontalAlignment = LinePattern.None), Text(origin = {-46.0, 24.5}, 
        lineColor = {0, 0, 0}, 
        extent = {{-32.0, 5.5}, {32.0, -5.5000000000000036}}, 
        textString = "Inverted Pendulum", 
        fontName = "Consolas", 
        textStyle = {TextStyle.None, TextStyle.Italic}, 
        textColor = {0, 0, 0}, 
        horizontalAlignment = LinePattern.None)}), 
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
      inner Modelica.Mechanics.MultiBody.World world(gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity, animateGravity = false, animateWorld = false)
        annotation (Placement(transformation(origin = {-40.0, -30.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Prismatic prismatic
        annotation (Placement(transformation(origin = {-2.0, -30.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Joints.Revolute revolute(useAxisFlange = true, 
        phi(start
           = 0.261799387799149, fixed
           = true))
        annotation (Placement(transformation(origin = {36.0, -30.000000000000007}, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}, 
          rotation = -360.0)));
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
      Modelica.Mechanics.MultiBody.Parts.BodyShape M(m = 2, 
        shapeType = "box", length = 0.25, width = 0.125, 
        r_shape = {-0.125, 0, 0}, 
        animateSphere = false)
        annotation (Placement(transformation(origin = {-2.0, 0.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}})));
      Modelica.Mechanics.MultiBody.Parts.Body m(sphereColor = {255, 255, 0}, sphereDiameter = 0.1, m = 0.1, r_CM = {0, 0.5, 0})
        annotation (Placement(transformation(origin = {74.0, -30.00000000000001}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Sources.Constant const3(k = 0)
        annotation (Placement(transformation(origin = {-94.0, -60.0}, 
          extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
          rotation = -180.0)));
    equation 
      connect(world.frame_b, prismatic.frame_a)
        annotation (Line(origin = {-44.0, -30.0}, 
          points = {{14.0, 0.0}, {32.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(force.frame_b, M.frame_b)
        annotation (Line(origin = {47.0, -76.0}, 
          points = {{-75.0, 76.0}, {-59.0, 76.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(M.frame_a, prismatic.frame_b)
        annotation (Line(origin = {15.0, -43.0}, 
          points = {{-7.0, 43.0}, {3.0, 43.0}, {3.0, 13.0}, {-7.0, 13.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(prismatic.frame_b, revolute.frame_a)
        annotation (Line(origin = {32.0, -30.0}, 
          points = {{-24.0, 0.0}, {-6.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(m.frame_a, revolute.frame_b)
        annotation (Line(origin = {97.0, -30.0}, 
          points = {{-33.0, 0.0}, {-51.0, 0.0}}, 
          color = {95, 95, 95}, 
          thickness = 0.5));
      connect(const3.y, force.force[1])
        annotation (Line(origin = {-66.0, 16.0}, 
          points = {{-17.0, -76.0}, {2.0, -76.0}, {2.0, -16.0}, {16.0, -16.0}}, 
          color = {0, 0, 127}));
      connect(const1.y, force.force[2])
        annotation (Line(origin = {-66.0, 0.0}, 
          points = {{-17.0, 0.0}, {16.0, 0.0}}, 
          color = {0, 0, 127}));
      connect(const2.y, force.force[3])
        annotation (Line(origin = {-66.0, -15.0}, 
          points = {{-17.0, -15.0}, {2.0, -15.0}, {2.0, 15.0}, {16.0, 15.0}}, 
          color = {0, 0, 127}));
    end InvertedPendlum;
  end Plant;
  package BasicModels "基础模型"
    model Gain "增益"
      Modelica.Blocks.Interfaces.RealInput u
        annotation (Placement(transformation(origin = {-120.0, 50.00000000000001}, 
          extent = {{-20.0, -20.0}, {20.0, 20.0}})));
      Modelica.Blocks.Interfaces.RealInput k
        annotation (Placement(transformation(origin = {-119.99999999999999, -50.0}, 
          extent = {{-20.0, -20.0}, {20.0, 20.0}})));
      Modelica.Blocks.Interfaces.RealOutput y
        annotation (Placement(transformation(origin = {110.0, 0.0}, 
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
        grid = {2.0, 2.0}), graphics = {Polygon(origin = {7.105427357601002e-15, 0.0}, 
        lineColor = {0, 0, 127}, 
        fillColor = {255, 255, 255}, 
        fillPattern = FillPattern.Solid, 
        points = {{-100.0, -100.0}, {-100.0, 100.0}, {100.0, 0.0}, {-100.0, -100.0}}), Text(origin = {0.0, 120.0}, 
        lineColor = {0, 0, 255}, 
        extent = {{-150.0, 20.0}, {150.0, -20.0}}, 
        textString = "%name", 
        textColor = {0, 0, 255})}));
    equation 
      y = k * u;
    end Gain;
  end BasicModels;
end InvertedPendlum;