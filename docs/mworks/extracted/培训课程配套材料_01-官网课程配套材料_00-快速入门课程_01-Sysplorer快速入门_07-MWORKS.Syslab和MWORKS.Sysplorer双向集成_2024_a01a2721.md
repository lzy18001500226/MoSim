# InvertedPendlum.mo

- Source: `培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/07-MWORKS.Syslab和MWORKS.Sysplorer双向集成(2024a)/一维倒立摆/InvertedPendlum.mo`
- Category: `sysplorer_modeling`
- Score: `120`
- Size: `0.05 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿within ;
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
```
