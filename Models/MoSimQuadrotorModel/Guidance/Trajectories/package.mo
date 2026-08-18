within MoSimQuadrotorModel.Guidance;
package Trajectories "Reference trajectories"
  extends Modelica.Icons.Package;
  model CirclePath "螺旋爬升模型"
    Modelica.Blocks.Sources.Ramp ramp(startTime = 0, duration = 150,
      height = 10) 
      annotation (Placement(transformation(origin = {-2.0, -50.209416252197016},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Interfaces.RealOutput position_command[3] "指令信号--x,y,z" annotation (Placement(transformation(origin = {111.0, 0.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {110.0, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain gain(k = 1) 
      annotation (Placement(transformation(origin = {55.94162521970009, -50.121461426274266},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain gain1(k = 1) 
      annotation (Placement(transformation(origin = {55.94162521970009, 41.790583747803},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Sources.Sine sine(f=0.03, amplitude=3, startTime=10) 
      annotation (Placement(transformation(origin = {-2.0, -0.209416252197002},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Sources.Cosine cosine(f=0.03, amplitude=3, startTime=10) 
      annotation (Placement(transformation(origin = {-2.0, 41.790583747803},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));



    Modelica.Blocks.Math.Gain gain2(k = 1) 
      annotation (Placement(transformation(origin = {56.779290228488094, 0.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {-0.2695547533092224, 0.5391095066185301},
      lineColor = {200, 200, 200},
      fillColor = {248, 248, 248},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-100.0, -100.0}, {100.0, 100.0}},
      radius = 25.0), Ellipse(origin = {2.0, 1.0},
      lineColor = {118, 118, 118},
      fillColor = {255, 255, 255},
      lineThickness = 0.5,
      extent = {{60.0, 39.0}, {-60.0, -39.0}}), Line(origin = {2.0, 31.0},
      points = {{0.0, -33.0}, {0.0, 33.0}},
      color = {132, 132, 132},
      pattern = LinePattern.Dash,
      arrow = {Arrow.None, Arrow.Filled},
      arrowSize = 4.0,
      __MWorks_Manhattanize = true)}));
  equation
    connect(gain1.y, position_command[1]) 
      annotation (Line(origin = {89.0, 21.0},
        points = {{-22.0, 21.0}, {-9.0, 21.0}, {-9.0, -21.0}, {22.0, -21.0}},
        color = {0, 0, 127}));
    connect(gain2.y, position_command[2]) 
      annotation (Line(origin = {90.0, 0.0},
        points = {{-22.0, 0.0}, {21.0, 0.0}},
        color = {0, 0, 127}));
    connect(gain.y, position_command[3]) 
      annotation (Line(origin = {90.0, -25.0},
        points = {{-23.0, -25.0}, {-10.0, -25.0}, {-10.0, 25.0}, {21.0, 25.0}},
        color = {0, 0, 127}));
    connect(cosine.y, gain1.u) 
      annotation (Line(origin = {7.0, 42.0},
        points = {{2.0, 0.0}, {37.0, 0.0}},
        color = {0, 0, 127}));
    connect(sine.y, gain2.u) 
      annotation (Line(origin = {7.0, 0.0},
        points = {{2.0, 0.0}, {38.0, 0.0}},
        color = {0, 0, 127}));
    connect(ramp.y, gain.u) 
      annotation (Line(origin = {7.0, -50.0},
        points = {{2.0, 0.0}, {37.0, 0.0}},
        color = {0, 0, 127}));
  end CirclePath;


  model EightPath "横8字型模型"
    Modelica.Blocks.Sources.RealExpression realExpression(y = x) 
      annotation (Placement(transformation(origin = {1.1591052234775123, 47.17773039939571},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Sources.RealExpression realExpression1(y = y) 
      annotation (Placement(transformation(origin = {-0.1359852938817938, -0.17597254192228462},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Sources.Ramp ramp(duration = 10, height = 10) 
      annotation (Placement(transformation(origin = {-0.9087221095334688, -41.28301853656825},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Interfaces.RealOutput position_command[3] "指令信号--x,y,z" annotation (Placement(transformation(origin = {110.30852974245975, 0.03180971102869656},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    import pi = Modelica.Constants.pi;
    Real x "x方向输出";
    Real y "y方向输出";
    parameter Real XAMP = 10 "x方向输出幅值";
    parameter Real XOmega = 0.02 "X方向频率";
    parameter Real YAMP = 10 "Y方向输出幅值";
    parameter Real YOmega = 0.04 "Y方向频率";
    Modelica.Blocks.Nonlinear.FixedDelay fixedDelay(delayTime=10) 
      annotation (Placement(transformation(origin={52,47.1777},
  extent={{-10,-10},{10,10}})));
    Modelica.Blocks.Nonlinear.FixedDelay fixedDelay1(delayTime=10) 
      annotation (Placement(transformation(origin={52,-0.175973},
  extent={{-10,-10},{10,10}})));
    annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {5.684341886080802e-14, -0.6522262334536704},
      lineColor = {200, 200, 200},
      fillColor = {248, 248, 248},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-100.0, -100.0}, {100.0, 100.0}},
      radius = 25.0), Ellipse(origin = {-40.0, -1.0},
      lineColor = {135, 135, 135},
      fillColor = {255, 255, 255},
      extent = {{40.0, 23.0}, {-40.0, -23.0}}), Ellipse(origin = {39.0, -2.0},
      lineColor = {135, 135, 135},
      fillColor = {255, 255, 255},
      extent = {{39.0, 24.0}, {-39.0, -24.0}}), Line(origin = {-76.0, -1.0},
      points = {{10.0, 23.0}, {2.7886769820447683, 18.49292311377798}, {-6.0, 13.0}, {-10.0, 1.0}, {-6.0, -15.0}, {8.0, -23.0}},
      color = {135, 135, 135},
      pattern = LinePattern.Dash,
      arrow = {Arrow.None, Arrow.Filled},
      smooth = Smooth.Bezier)}),Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
  grid={2,2})));
    equation
    if time<=0 then
    x=0;
    y=0;
    else
    x = XAMP * sin((XOmega * time + 1 / 360) * pi);
    y = YAMP * sin(YOmega * time * pi);
    end if;
    connect(ramp.y, position_command[3]) 
      annotation (Line(origin = {60.0, -11.0},
        points = {{-50.0, -30.0}, {20.0, -30.0}, {20.0, 11.0}, {50.0, 11.0}},
        color = {0, 0, 127}));
    connect(realExpression.y, fixedDelay.u) 
    annotation(Line(origin={61,24},
  points={{-48.8409,23.1777},{-21,23.1777}},
  color={0,0,127}));
    connect(realExpression1.y, fixedDelay1.u) 
    annotation(Line(origin={61,0},
  points={{-50.136,-0.175973},{-21,-0.175973}},
  color={0,0,127}));
    connect(fixedDelay.y, position_command[1]) 
    annotation(Line(origin={87,24},
  points={{-24,23.1777},{-7,23.1777},{-7,-23.9682},{23.3085,-23.9682}},
  color={0,0,127}));
    connect(fixedDelay1.y, position_command[2]) 
    annotation(Line(origin={122,20},
  points={{-59,-20.176},{-11.6915,-20.176},{-11.6915,-19.9682}},
  color={0,0,127}));
  end EightPath;


  annotation (Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0})),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      preserveAspectRatio = false,
      grid = {2.0, 2.0}), graphics = {Line(origin = {4.0, 16.25},
      points = {{-70.0, -34.25}, {-30.0, 34.25}, {37.0, 34.25}, {70.0, -34.25}},
      color = {158, 158, 158},
      thickness = 0.5), Line(origin = {-66.0, -6.0},
      points = {{0.0, 80.0}, {0.0, -80.0}},
      color = {153, 153, 153},
      arrow = {Arrow.Filled, Arrow.None},
      arrowSize = 5.0), Line(origin = {10.0, -18.0},
      points = {{-76.0, 0.0}, {76.0, 0.0}},
      color = {158, 158, 158},
      arrow = {Arrow.None, Arrow.Filled},
      arrowSize = 5.0), Text(origin = {8.0, 28.0},
      lineColor = {192, 192, 192},
      extent = {{-35.5, 21.5}, {35.5, -21.5}},
      textString = "w",
      textColor = {192, 192, 192}), Polygon(origin = {-66.0, 72.0},
      lineColor = {192, 192, 192},
      fillColor = {192, 192, 192},
      fillPattern = FillPattern.Solid,
      points = {{0.0, 11.0}, {-8.0, -11.0}, {8.0, -11.0}, {0.0, 11.0}}), Polygon(origin = {88.0, -18.0},
      rotation = -90.0,
      lineColor = {192, 192, 192},
      fillColor = {192, 192, 192},
      fillPattern = FillPattern.Solid,
      points = {{0.0, 11.0}, {8.0, -11.0}, {-8.0, -11.0}, {0.0, 11.0}})}));
end Trajectories;
