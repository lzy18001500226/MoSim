within MoSimQuadrotorModel.Vehicle;
package Blocks "控制系统"
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



  package ControlMethod "控制算法"
    extends Modelica.Icons.Package;
    model PID "连续PID控制器"

      parameter Real KP = 1;
      parameter Real KI = 1;
      parameter Real KD = 1;
      Modelica.Blocks.Math.Gain gain(k = KP) 
        annotation (Placement(transformation(origin = {-30.0, 60.0},
          extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Math.Add3 add3_1 
        annotation (Placement(transformation(origin = {38.0, 0.0},
          extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Continuous.Integrator integrator 
        annotation (Placement(transformation(origin = {-50.0, 0.0},
          extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Continuous.Derivative der1 annotation (Placement(transformation(origin = {-50.0, -60.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      Modelica.Blocks.Math.Gain gain1(k = KI) 
        annotation (Placement(transformation(origin = {-10.0, 0.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain2(k = KD) 
        annotation (Placement(transformation(origin = {-10.0, -60.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
        grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.9443507588532611, -1.0556492411467104},
        lineColor = {200, 200, 200},
        fillColor = {248, 248, 248},
        fillPattern = FillPattern.HorizontalCylinder,
        extent = {{-100.0, -100.0}, {100.0, 100.0}},
        radius = 25.0), Text(origin = {-0.24957841483981724, 0.527824620573357},
        lineColor = {120, 120, 120},
        extent = {{-92.0, 73.0}, {92.0, -73.0}},
        textString = "PID",
        fontName = "Times New Roman",
        textStyle = {TextStyle.None},
        textColor = {120, 120, 120})}));
      extends Modelica.Blocks.Interfaces.SISO;
      Modelica.Blocks.Math.Gain gain3 
        annotation (Placement(transformation(origin = {73.99999999999999, 0.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    equation
      connect(u, integrator.u) 
        annotation (Line(origin = {-91.0, 0.0},
          points = {{-29.0, 0.0}, {29.0, 0.0}},
          color = {0, 0, 127}));
      connect(u, gain.u) 
        annotation (Line(origin = {-81.0, 30.0},
          points = {{-39.0, -30.0}, {1.0, -30.0}, {1.0, 30.0}, {39.0, 30.0}},
          color = {0, 0, 127}));
      connect(u, der1.u) 
        annotation (Line(origin = {-91.0, -30.0},
          points = {{-29.0, 30.0}, {11.0, 30.0}, {11.0, -30.0}, {29.0, -30.0}},
          color = {0, 0, 127}));
      connect(integrator.y, gain1.u) 
        annotation (Line(origin = {-30.0, 0.0},
          points = {{-9.0, 0.0}, {8.0, 0.0}},
          color = {0, 0, 127}));
      connect(der1.y, gain2.u) 
        annotation (Line(origin = {-30.0, -60.0},
          points = {{-9.0, 0.0}, {8.0, 0.0}},
          color = {0, 0, 127}));
      connect(gain.y, add3_1.u1) 
        annotation (Line(origin = {20.0, 34.0},
          points = {{-39.0, 26.0}, {-6.0, 26.0}, {-6.0, -26.0}, {6.0, -26.0}},
          color = {0, 0, 127}));
      connect(gain1.y, add3_1.u2) 
        annotation (Line(origin = {30.0, 0.0},
          points = {{-29.0, 0.0}, {-4.0, 0.0}},
          color = {0, 0, 127}));
      connect(gain2.y, add3_1.u3) 
        annotation (Line(origin = {30.0, -34.0},
          points = {{-29.0, -26.0}, {-16.0, -26.0}, {-16.0, 26.0}, {-4.0, 26.0}},
          color = {0, 0, 127}));
      connect(add3_1.y, gain3.u) 
        annotation (Line(origin = {55.0, 0.0},
          points = {{-6.0, 0.0}, {6.999999999999986, 0.0}},
          color = {0, 0, 127}));
      connect(gain3.y, y) 
        annotation (Line(origin = {98.0, 0.0},
          points = {{-13.000000000000014, 0.0}, {12.0, 0.0}},
          color = {0, 0, 127}));
    end PID;
  end ControlMethod;

  package Controller "控制器"
    extends Modelica.Icons.Package;
    model Controller "6Dof控制器-"
      Modelica.Blocks.Math.Gain gain2(k = 1) 
        annotation (Placement(transformation(origin = {-212.69990699270426, -179.0123120728828},
          extent = {{9.663753636058601, -9.663753636058573}, {-9.663753636058544, 9.663753636058573}},
          rotation = -180.0)));
      Modelica.Blocks.Math.Add add 
        annotation (Placement(transformation(origin = {195.38603678043503, 136.2455786404107},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add add1 
        annotation (Placement(transformation(origin = {194.07688458582734, 43.30416328490037},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add add2 
        annotation (Placement(transformation(origin = {194.07688458582734, -49.63725207061002},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add add3 
        annotation (Placement(transformation(origin = {193.41777678011923, -143.77619343602075},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add3 add3_1(k3 = +1, k2 = -1,
        k1 = -1) 
        annotation (Placement(transformation(origin = {132.88406102774712, 142.6102498040092},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add3 add3_2(k3 = -1, k2 = -1,
        k1 = +1) 
        annotation (Placement(transformation(origin = {132.88406102774712, 49.929746327695895},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add3 add3_3(k3 = -1, k2 = +1,
        k1 = -1) 
        annotation (Placement(transformation(origin = {132.88406102774712, -34.903964680479746},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Add3 add3_4(k3 = +1, k2 = +1,
        k1 = +1) 
        annotation (Placement(transformation(origin = {132.88406102774712, -120.6610719227242},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain(k = 0.707) 
        annotation (Placement(transformation(origin = {50.0, 51.929746327695895},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain1(k = 0.707) 
        annotation (Placement(transformation(origin = {50.31127897946099, -41.478087343389646},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Feedback feedback 
        annotation (Placement(transformation(origin = {-40.0, 136.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      ControlMethod.PID PID1(KP = 5, KI = 0, KD = 0) annotation (Placement(transformation(origin = {-10.000000000000004, 136.24557864041074},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      Modelica.Blocks.Math.Feedback feedback1 
        annotation (Placement(transformation(origin = {-40.0, 51.9297463276959},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      ControlMethod.PID PID5(KP = 14.142, KI = 0, KD = 1.414) annotation (Placement(transformation(origin = {-9.999999999999998, 51.929746327695895},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      Modelica.Blocks.Math.Feedback feedback2 
        annotation (Placement(transformation(origin = {-39.99999999999999, -41.737719741257976},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      ControlMethod.PID PID6(KP = 14.142, KI = 0, KD = 1.414) annotation (Placement(transformation(origin = {-10.0, -41.737719741257976},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      Modelica.Blocks.Math.Feedback feedback3 
        annotation (Placement(transformation(origin = {-177.0338684599124, -144.95408039247764},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      ControlMethod.PID PID7(KP = 8, KI = 6, KD = 4) annotation (Placement(transformation(origin = {-147.6231252910071, -145.3480005256226},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      Modelica.Blocks.Math.Gain gain3(k = 1) 
        annotation (Placement(transformation(origin = {-112.51509596744064, -144.65059206492597},
          extent = {{7.892020399656985, -7.892020399656985}, {-7.892020399656985, 7.892020399656985}},
          rotation = -180.0)));
      ControlMethod.PID PID3(KP = 1.5, KI = 0, KD = 1) annotation (Placement(transformation(origin = {-147.89106799143525, 54.13037202945324},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      ControlMethod.PID PID4(KP = 1.5, KI = 0, KD = 1) annotation (Placement(transformation(origin = {-147.6231252910071, -42.78744987823214},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

      Modelica.Blocks.Math.Feedback feedback4 
        annotation (Placement(transformation(origin = {-174.06836126495082, 55.01839156918994},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Feedback feedback5 
        annotation (Placement(transformation(origin = {-175.50457262869273, -43.28839032256941},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain4(k = 1) 
        annotation (Placement(transformation(origin = {-212.36366062876286, -74.70691878418587},
          extent = {{10.0, -10.0}, {-10.0, 10.0}},
          rotation = -180.0)));
      Modelica.Blocks.Nonlinear.Limiter limiter1(uMax = 15 / 57.3) 
        annotation (Placement(transformation(origin = {-70.0, 52.63497015576597},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Nonlinear.Limiter limiter2(uMax = 15 / 57.3) 
        annotation (Placement(transformation(origin = {-68.9630855717734, -42.78744987823214},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain5(k = 0.1) 
        annotation (Placement(transformation(origin = {-110.40711636709761, -44.40672684784512},
          extent = {{10.0, -10.0}, {-10.0, 10.0}},
          rotation = -180.0)));
      Modelica.Blocks.Math.Gain gain6(k = 0.1) 
        annotation (Placement(transformation(origin = {-110.40711636709761, 53.95747780349969},
          extent = {{10.0, -10.0}, {-10.0, 10.0}},
          rotation = -180.0)));
      annotation (Diagram(coordinateSystem(extent = {{-270.0, -200.0}, {270.0, 200.0}},
        grid = {2.0, 2.0}), graphics = {Rectangle(origin = {161.99999999999994, 6.039613253960852e-14},
        fillColor = {250, 250, 187},
        pattern = LinePattern.Dash,
        fillPattern = FillPattern.Solid,
        extent = {{-87.99999999999994, 199.99999999999994}, {88.00000000000006, -200.00000000000006}}), Rectangle(origin = {-8.999999999999993, -5.684341886080802e-14},
        fillColor = {170, 255, 127},
        pattern = LinePattern.Dash,
        fillPattern = FillPattern.Solid,
        extent = {{-75.00000000000001, 200.00000000000006}, {74.99999999999997, -199.99999999999994}}), Rectangle(origin = {-178.0, -2.1316282072803006e-14},
        fillColor = {170, 255, 255},
        pattern = LinePattern.Dash,
        fillPattern = FillPattern.Solid,
        extent = {{-84.0, 200.00000000000003}, {84.0, -199.99999999999997}}), Text(origin = {-172.0, 187.0},
        extent = {{-40.0, 15.0}, {40.0, -15.0}},
        textString = "位置控制",
        fontName = "等线",
        textStyle = {TextStyle.None}), Text(origin = {-5.0, 188.0},
        extent = {{-39.0, 20.0}, {39.0, -20.0}},
        textString = "姿态控制",
        fontName = "等线",
        textStyle = {TextStyle.None}), Text(origin = {151.0, 188.0},
        extent = {{-39.0, 12.0}, {39.0, -12.0}},
        textString = "控制分配",
        fontName = "等线",
        textStyle = {TextStyle.None})}),
        Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
          grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.22951688694824135, 0.45903377389647915},
          lineColor = {200, 200, 200},
          fillColor = {248, 248, 248},
          fillPattern = FillPattern.HorizontalCylinder,
          extent = {{-100.0, -100.0}, {100.0, 100.0}},
          radius = 25.0), Text(origin = {2.0, 3.0},
          lineColor = {136, 136, 136},
          extent = {{-78.0, 81.0}, {78.0, -81.0}},
          textString = "PIDController",
          fontName = "Times New Roman",
          textStyle = {TextStyle.None},
          textColor = {136, 136, 136})}));
      Modelica.Blocks.Math.Gain gain7(k = 1) 
        annotation (Placement(transformation(origin = {-212.36366062876286, 22.765560154234876},
          extent = {{10.0, -10.0}, {-10.0, 10.0}},
          rotation = -180.0)));
      Modelica.Blocks.Math.Gain gain8(k = 1) 
        annotation (Placement(transformation(origin = {230.0, 136.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain9(k = -1) 
        annotation (Placement(transformation(origin = {230.0, 44.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain10(k = 1) 
        annotation (Placement(transformation(origin = {230.0, -50.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain11(k = -1) 
        annotation (Placement(transformation(origin = {230.0, -144.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain12(k = 0.707) 
        annotation (Placement(transformation(origin = {50.0, 136.2455786404107},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Math.Gain gain13(k = -1) 
        annotation (Placement(transformation(origin = {-112.51509596744066, -95.58264925655706},
          extent = {{10.0, -10.0}, {-10.0, 10.0}},
          rotation = -180.0)));
      Modelica.Blocks.Nonlinear.Limiter limiter3(uMax = 7) 
        annotation (Placement(transformation(origin = {20.0, 51.929746327695895},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Nonlinear.Limiter limiter4(uMax = 7) 
        annotation (Placement(transformation(origin = {20.155639489730493, -41.47808734338966},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Nonlinear.Limiter limiter5(uMax = 7) 
        annotation (Placement(transformation(origin = {19.999999999999996, 136.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Interfaces.RealInput position_command[3] "指令信号 --- x，y，z" annotation (Placement(transformation(origin = {-286.0, 94.0},
        extent = {{-20.0, -20.0}, {20.0, 20.0}}),
        iconTransformation(origin = {-110.0, 60.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Interfaces.RealInput position[3] "位置信息---x,y,z" annotation (Placement(transformation(origin = {-290.0, -8.0},
        extent = {{-20.0, -20.0}, {20.0, 20.0}}),
        iconTransformation(origin = {-110.0, 2.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Interfaces.RealInput angle[3] "姿态信息--roll,pitch,yaw" annotation (Placement(transformation(origin = {-290.0, -118.0},
        extent = {{-20.0, -20.0}, {20.0, 20.0}}),
        iconTransformation(origin = {-110.0, -62.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
      Modelica.Blocks.Interfaces.RealOutput y
        "一号电机转速控制信号" annotation (Placement(transformation(origin = {280.0, 136.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}}),
          iconTransformation(origin = {110.0, 59.999999999999986},
            extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Interfaces.RealOutput y1
        "二号电机转速控制信号" annotation (Placement(transformation(origin = {280.0, 44.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}}),
          iconTransformation(origin = {110.0, 20.666666666666657},
            extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Interfaces.RealOutput y2
        "三号电机转速控制信号" annotation (Placement(transformation(origin = {280.0, -50.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}}),
          iconTransformation(origin = {110.0, -18.66666666666667},
            extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Interfaces.RealOutput y3
        "四号电机转速控制信号" annotation (Placement(transformation(origin = {280.0, -144.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}}),
          iconTransformation(origin = {110.0, -58.0},
            extent = {{-6.0, -6.0}, {6.0, 6.0}})));
      Modelica.Blocks.Sources.Constant const(k = 0) 
        annotation (Placement(transformation(origin = {-68.96308557177342, 136.0},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    equation
      connect(gain2.y, feedback3.u2) 
        annotation (Line(origin = {53.610508919861104, -149.8919319107595},
          points = {{-256.0, -29.0}, {-231.0, -29.0}, {-231.0, -3.0}},
          color = {0, 0, 127}));
      connect(add3_1.y, add.u1) 
        annotation (Line(origin = {146.95118178983827, 32.2855521816803},
          points = {{-3.0, 110.0}, {36.0, 110.0}},
          color = {0, 0, 127}));
      connect(add3_2.y, add1.u1) 
        annotation (Line(origin = {146.95118178983827, -5.714447818319712},
          points = {{-3.0, 56.0}, {35.0, 56.0}, {35.0, 55.0}},
          color = {0, 0, 127}));
      connect(add3_3.y, add2.u1) 
        annotation (Line(origin = {146.95118178983827, -42.71444781831971},
          points = {{-3.0, 8.0}, {12.0, 8.0}, {12.0, -1.0}, {35.0, -1.0}},
          color = {0, 0, 127}));
      connect(add3_4.y, add3.u1) 
        annotation (Line(origin = {146.95118178983827, -81.71444781831971},
          points = {{-3.0, -39.0}, {12.0, -39.0}, {12.0, -56.0}, {34.0, -56.0}},
          color = {0, 0, 127}));
      connect(feedback.y, PID1.u) 
        annotation (Line(origin = {-9.047589837435265, 139.7139393638377},
          points = {{-22.0, -4.0}, {-13.0, -4.0}, {-13.0, -3.0}},
          color = {0, 0, 127}));
      connect(feedback1.y, PID5.u) 
        annotation (Line(origin = {-1.8744491963850756, 53.89544133659771},
          points = {{-29.0, -2.0}, {-20.0, -2.0}},
          color = {0, 0, 127}));
      connect(feedback2.y, PID6.u) 
        annotation (Line(origin = {5.864782786952201, -42.06148659675134},
          points = {{-37.0, 0.0}, {-28.0, 0.0}},
          color = {0, 0, 127}));


      connect(feedback3.y, PID7.u) 
        annotation (Line(origin = {-161.74937830820016, -145.67176738111604},
          points = {{-6.0, 1.0}, {2.0, 1.0}, {2.0, 0.0}},
          color = {0, 0, 127}));
      connect(PID7.y, gain3.u) 
        annotation (Line(origin = {-135.56294479613206, -145.14130128012883},
          points = {{-1.0, 0.0}, {14.0, 0.0}},
          color = {0, 0, 127}));
      connect(gain3.y, add3.u2) 
        annotation (Line(origin = {57.977999938512994, -148.58583127373336},
          points = {{-162.0, 4.0}, {101.0, 4.0}, {101.0, -1.0}, {123.0, -1.0}},
          color = {0, 0, 127}));
      connect(gain3.y, add2.u2) 
        annotation (Line(origin = {204.07901205363325, -160.393356432471},
          points = {{-308.0, 16.0}, {-45.0, 16.0}, {-45.0, 105.0}, {-22.0, 105.0}},
          color = {0, 0, 127}));
      connect(gain3.y, add1.u2) 
        annotation (Line(origin = {204.07901205363325, -146.393356432471},
          points = {{-308.0, 2.0}, {-45.0, 2.0}, {-45.0, 184.0}, {-22.0, 184.0}},
          color = {0, 0, 127}));
      connect(gain3.y, add.u2) 
        annotation (Line(origin = {204.07901205363325, -131.393356432471},
          points = {{-308.0, -13.0}, {-45.0, -13.0}, {-45.0, 262.0}, {-21.0, 262.0}},
          color = {0, 0, 127}));
      connect(feedback5.y, PID4.u) 
        annotation (Line(origin = {-135.32525239618457, -30.028667121554385},
          points = {{-31.0, -13.0}, {-24.0, -13.0}},
          color = {0, 0, 127}));
      connect(feedback4.y, PID3.u) 
        annotation (Line(origin = {-151.46206049556133, 51.98219706603876},
          points = {{-14.0, 3.0}, {-8.0, 3.0}, {-8.0, 2.0}},
          color = {0, 0, 127}));
      connect(gain4.y, feedback5.u2) 
        annotation (Line(origin = {-175.42140257154261, -75.53967302362271},
          points = {{-26.0, 1.0}, {0.0, 1.0}, {0.0, 24.0}},
          color = {0, 0, 127}));
      connect(PID4.y, gain5.u) 
        annotation (Line(origin = {-135.73433357702584, -44.19664220500482},
          points = {{-1.0, 1.0}, {13.0, 1.0}, {13.0, 0.0}},
          color = {0, 0, 127}));
      connect(gain5.y, limiter2.u) 
        annotation (Line(origin = {-110.02331656999085, -44.19664220500482},
          points = {{11.0, 0.0}, {29.0, 0.0}, {29.0, 1.0}},
          color = {0, 0, 127}));
      connect(limiter2.y, feedback2.u1) 
        annotation (Line(origin = {41.53983579048576, -78.62459613738737},
          points = {{-100.0, 36.0}, {-90.0, 36.0}, {-90.0, 37.0}},
          color = {0, 0, 127}));
      connect(limiter1.y, feedback1.u1) 
        annotation (Line(origin = {11.888478860152016, 25.15658168995462},
          points = {{-71.0, 27.0}, {-60.0, 27.0}},
          color = {0, 0, 127}));
      connect(PID3.y, gain6.u) 
        annotation (Line(origin = {-169.1959584533509, 51.52860783033083},
          points = {{32.0, 3.0}, {47.0, 3.0}, {47.0, 2.0}},
          color = {0, 0, 127}));
      connect(gain6.y, limiter1.u) 
        annotation (Line(origin = {-125.48494144631586, 51.52860783033083},
          points = {{26.0, 2.0}, {43.0, 2.0}, {43.0, 1.0}},
          color = {0, 0, 127}));
      connect(gain7.y, feedback4.u2) 
        annotation (Line(origin = {-179.56687759540455, 32.5558016868566},
          points = {{-22.0, -10.0}, {5.0, -10.0}, {5.0, 14.0}},
          color = {0, 0, 127}));
      connect(gain12.y, add3_1.u1) 
        annotation (Line(origin = {95.08607863974495, 145.47608926673752},
          points = {{-34.0, -9.0}, {-16.0, -9.0}, {-16.0, 5.0}, {26.0, 5.0}},
          color = {0, 0, 127}));
      connect(add3_3.u1, gain12.y) 
        annotation (Line(origin = {95.08607863974495, 56.47608926673752},
          points = {{26.0, -83.0}, {-16.0, -83.0}, {-16.0, 80.0}, {-34.0, 80.0}},
          color = {0, 0, 127}));
      connect(add3_4.u1, gain12.y) 
        annotation (Line(origin = {95.08607863974495, 13.476089266737517},
          points = {{26.0, -126.0}, {-16.0, -126.0}, {-16.0, 123.0}, {-34.0, 123.0}},
          color = {0, 0, 127}));
      connect(gain.y, add3_1.u2) 
        annotation (Line(origin = {71.0, 98.0},
          points = {{-10.0, -46.0}, {8.0, -46.0}, {8.0, 45.0}, {50.0, 45.0}},
          color = {0, 0, 127}));
      connect(add3_2.u2, gain.y) 
        annotation (Line(origin = {71.0, 52.0},
          points = {{50.0, -2.0}, {-10.0, -2.0}, {-10.0, 0.0}},
          color = {0, 0, 127}));
      connect(add3_3.u2, gain.y) 
        annotation (Line(origin = {71.0, 9.0},
          points = {{50.0, -44.0}, {8.0, -44.0}, {8.0, 43.0}, {-10.0, 43.0}},
          color = {0, 0, 127}));
      connect(add3_4.u2, gain.y) 
        annotation (Line(origin = {71.0, -34.0},
          points = {{50.0, -87.0}, {8.0, -87.0}, {8.0, 86.0}, {-10.0, 86.0}},
          color = {0, 0, 127}));
      connect(gain1.y, add3_1.u3) 
        annotation (Line(origin = {71.0, 47.0},
          points = {{-10.0, -88.0}, {8.0, -88.0}, {8.0, 88.0}, {50.0, 88.0}},
          color = {0, 0, 127}));
      connect(add3_2.u3, gain1.y) 
        annotation (Line(origin = {71.0, 0.0},
          points = {{50.0, 42.0}, {50.0, 41.0}, {8.0, 41.0}, {8.0, -41.0}, {-10.0, -41.0}},
          color = {0, 0, 127}));
      connect(add3_3.u3, gain1.y) 
        annotation (Line(origin = {70.0, -42.0},
          points = {{51.0, -1.0}, {9.0, -1.0}, {9.0, 1.0}, {-9.0, 1.0}},
          color = {0, 0, 127}));
      connect(add3_4.u3, gain1.y) 
        annotation (Line(origin = {71.0, -87.0},
          points = {{50.0, -42.0}, {8.0, -42.0}, {8.0, 46.0}, {-10.0, 46.0}},
          color = {0, 0, 127}));
      connect(add3_2.u1, gain12.y) 
        annotation (Line(origin = {95.08607863974495, 99.47608926673752},
          points = {{26.0, -42.0}, {-16.0, -42.0}, {-16.0, 37.0}, {-34.0, 37.0}},
          color = {0, 0, 127}));
      connect(gain7.u, position[1]) 
        annotation (Line(origin = {-247.0, -29.0},
          points = {{23.0, 52.0}, {7.0, 52.0}, {7.0, 21.0}, {-43.0, 21.0}},
          color = {0, 0, 127}));
      connect(gain4.u, position[2]) 
        annotation (Line(origin = {-247.0, -78.0},
          points = {{23.0, 3.0}, {7.0, 3.0}, {7.0, 70.0}, {-43.0, 70.0}},
          color = {0, 0, 127}));
      connect(gain2.u, position[3]) 
        annotation (Line(origin = {-247.0, -130.0},
          points = {{23.0, -49.0}, {7.0, -49.0}, {7.0, 122.0}, {-43.0, 122.0}},
          color = {0, 0, 127}));
      connect(feedback.u2, angle[3]) 
        annotation (Line(origin = {-145.0, 25.0},
          points = {{105.0, 103.0}, {105.0, 85.0}, {-95.0, 85.0}, {-95.0, -143.0}, {-145.0, -143.0}},
          color = {0, 0, 127}));
      connect(feedback1.u2, angle[2]) 
        annotation (Line(origin = {-149.0, -18.0},
          points = {{109.0, 62.0}, {110.0, 62.0}, {110.0, 12.0}, {-91.0, 12.0}, {-91.0, -100.0}, {-141.0, -100.0}},
          color = {0, 0, 127}));
      connect(gain13.u, angle[1]) 
        annotation (Line(origin = {-149.0, -73.0},
          points = {{24.0, -23.0}, {-91.0, -23.0}, {-91.0, -45.0}, {-141.0, -45.0}},
          color = {0, 0, 127}));
      connect(add3.y, gain11.u) 
        annotation (Line(origin = {211.0, -144.0},
          points = {{-7.0, 0.0}, {7.0, 0.0}},
          color = {0, 0, 127}));
      connect(add2.y, gain10.u) 
        annotation (Line(origin = {212.0, -50.0},
          points = {{-7.0, 0.0}, {6.0, 0.0}},
          color = {0, 0, 127}));
      connect(add1.y, gain9.u) 
        annotation (Line(origin = {214.0, 43.0},
          points = {{-9.0, 0.0}, {-8.0, 0.0}, {-8.0, 1.0}, {4.0, 1.0}},
          color = {0, 0, 127}));
      connect(add.y, gain8.u) 
        annotation (Line(origin = {213.0, 136.0},
          points = {{-7.0, 0.0}, {5.0, 0.0}},
          color = {0, 0, 127}));
      connect(gain8.y, y) 
        annotation (Line(origin = {256.0, 67.0},
          points = {{-15.0, 69.0}, {24.0, 69.0}},
          color = {0, 0, 127}));
      connect(gain9.y, y1) 
        annotation (Line(origin = {256.0, 21.0},
          points = {{-15.0, 23.0}, {24.0, 23.0}},
          color = {0, 0, 127}));
      connect(gain10.y, y2) 
        annotation (Line(origin = {256.0, -26.0},
          points = {{-15.0, -24.0}, {24.0, -24.0}},
          color = {0, 0, 127}));
      connect(gain11.y, y3) 
        annotation (Line(origin = {256.0, -73.0},
          points = {{-15.0, -71.0}, {24.0, -71.0}},
          color = {0, 0, 127}));

      connect(gain13.y, feedback2.u2) 
        annotation (Line(origin = {-63.0, -73.0},
          points = {{-39.0, -23.0}, {23.0, -23.0}, {23.0, 23.0}},
          color = {0, 0, 127}));
      connect(PID5.y, limiter3.u) 
        annotation (Line(origin = {3.0, 50.0},
          points = {{-2.0, 2.0}, {5.0, 2.0}},
          color = {0, 0, 127}));
      connect(limiter3.y, gain.u) 
        annotation (Line(origin = {29.0, 50.0},
          points = {{2.0, 2.0}, {9.0, 2.0}},
          color = {0, 0, 127}));
      connect(PID6.y, limiter4.u) 
        annotation (Line(origin = {5.0, -42.0},
          points = {{-4.0, 0.0}, {3.0, 0.0}, {3.0, 1.0}},
          color = {0, 0, 127}));
      connect(limiter4.y, gain1.u) 
        annotation (Line(origin = {35.0, -42.0},
          points = {{-4.0, 1.0}, {-4.0, 0.0}, {3.0, 0.0}, {3.0, 1.0}},
          color = {0, 0, 127}));
      connect(PID1.y, limiter5.u) 
        annotation (Line(origin = {4.0, 136.0},
          points = {{-3.0, 0.0}, {4.0, 0.0}},
          color = {0, 0, 127}));
      connect(limiter5.y, gain12.u) 
        annotation (Line(origin = {35.0, 136.0},
          points = {{-4.0, 0.0}, {3.0, 0.0}},
          color = {0, 0, 127}));
      connect(feedback.u1, const.y) 
        annotation (Line(origin = {-53.0, 136.0},
          points = {{5.0, 0.0}, {-4.963085571773419, 0.0}},
          color = {0, 0, 127}));
      connect(position_command[1], feedback4.u1) 
        annotation (Line(origin = {-234.0, 75.0},
          points = {{-52.0, 19.0}, {-6.0, 19.0}, {-6.0, -20.0}, {52.0, -20.0}},
          color = {0, 0, 127}));
      connect(position_command[2], feedback5.u1) 
        annotation (Line(origin = {-235.0, 26.0},
          points = {{-51.0, 68.0}, {-5.0, 68.0}, {-5.0, -69.0}, {51.0, -69.0}},
          color = {0, 0, 127}));
      connect(position_command[3], feedback3.u1) 
        annotation (Line(origin = {-235.0, -27.0},
          points = {{-51.0, 121.0}, {-5.0, 121.0}, {-5.0, -118.0}, {50.0, -118.0}},
          color = {0, 0, 127}));
    end Controller;
  end Controller;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Blocks;