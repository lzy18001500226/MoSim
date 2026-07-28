within MoSimQuadrotorModel.Vehicle;
package Mechanics "机械多体库"
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0},
    lineColor = {200, 200, 200},
    fillColor = {248, 248, 248},
    fillPattern = FillPattern.HorizontalCylinder,
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    radius = 25.0), Rectangle(origin = {0.0, 0.0},
    lineColor = {128, 128, 128},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    radius = 25.0), Rectangle(origin = {8.6, 63.3333},
    lineColor = {64, 64, 64},
    fillColor = {192, 192, 192},
    fillPattern = FillPattern.HorizontalCylinder,
    extent = {{-4.6, -93.3333}, {41.4, -53.3333}}), Ellipse(origin = {9.0, 46.0},
    extent = {{-90.0, -60.0}, {-80.0, -50.0}}), Line(origin = {9.0, 46.0},
    points = {{-85.0, -55.0}, {-60.0, -21.0}},
    thickness = 0.5), Ellipse(origin = {9.0, 46.0},
    extent = {{-65.0, -26.0}, {-55.0, -16.0}}), Line(origin = {9.0, 46.0},
    points = {{-60.0, -21.0}, {9.0, -55.0}},
    thickness = 0.5), Ellipse(origin = {9.0, 46.0},
    fillPattern = FillPattern.Solid,
    extent = {{4.0, -60.0}, {14.0, -50.0}}), Line(origin = {9.0, 46.0},
    points = {{-10.0, -26.0}, {72.0, -26.0}, {72.0, -86.0}, {-10.0, -86.0}})}));
  model QuadrotorBody "四旋翼机身"
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a
      annotation (Placement(transformation(origin = {-100.0, 0.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b
      annotation (Placement(transformation(origin = {100.0, 0.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Parts.BodyShape body(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      r_CM = {0, 0, 0},
      m = 1.0,
      I_11 = 0.0085,
      I_22 = 0.0085,
      I_33 = 0.012,
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_body.stl",
      r_shape = {0, 0, 0.0525},
      lengthDirection = {0, -1, 0},
      widthDirection = {1, 0, 0},
      length = 0.03,
      width = 0.03,
      height = 0.03,
      extra = 1,
      color = {255, 255, 255},
      specularCoefficient = 1,
      r_0(fixed = false),
      enforceStates = true) annotation (Placement(transformation(extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  equation
    connect(frame_a, body.frame_b)
      annotation (Line(origin = {-55.0, 0.0},
        points = {{-45.0, 0.0}, {45.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(body.frame_a, frame_b)
      annotation (Line(origin = {55.0, 0.0},
        points = {{-45.0, 0.0}, {45.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
  end QuadrotorBody;
  model Rotor "旋翼模型"
    Modelica.Mechanics.MultiBody.Parts.BodyShape propellers1(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      m = 0.005,
      I_11 = 9.75e-7,
      I_22 = 0.000173104,
      I_33 = 0.000174004,
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_propeller.stl",
      r_shape = {0, 0, 0},
      lengthDirection = {1, 0, 0},
      widthDirection = {0, 1, 0},
      length = 0.03,
      width = 0.03,
      height = 0.03,
      extra = 1,
      color = {255, 255, 255},
      specularCoefficient = 1,
      r_0(fixed = false))
      annotation (Placement(transformation(origin = {-25.00000000000003, -0.5000000000000284},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute1(
      animation = false,
      n = {0, 0, 1},
      useAxisFlange = true)
      annotation (Placement(transformation(origin = {16.99999999999997, -0.5000000000000284},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange_a annotation (Placement(transformation(origin = {-100.0, 18.000000000000014},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {-100.40059043098442, 1.7339167500375368},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b
      annotation (Placement(transformation(origin = {101.0, 0.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
  equation
    connect(propellers1.frame_a, revolute1.frame_b)
      annotation (Line(origin = {-4.0, -0.5},
        points = {{-11.0, 0.0}, {11.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));



    connect(revolute1.axis, flange_a)
      annotation (Line(origin = {19.0, 14.5},
        points = {{-2.0, -5.0}, {-2.0, 4.0}, {-118.0, 4.0}},
        color = {0, 0, 0}));
    connect(revolute1.frame_a, frame_b)
      annotation (Line(origin = {64.0, 1.0},
        points = {{-37.0, -2.0}, {37.0, -2.0}, {37.0, -1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
  end Rotor;
  model Arm "机臂"
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed1(
      animation = false,
      r = {0.053745, -0.05374, -0.014052})
      annotation (Placement(transformation(origin = {2.4999999999999716, 75.50000000000004},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed2(
      animation = false,
      r = {0.053746, 0.053759, -0.014052})
      annotation (Placement(transformation(origin = {4.499999999999972, 24.83333333333337},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed3(
      animation = false,
      r = {-0.053761, 0.05376, -0.014052})
      annotation (Placement(transformation(origin = {2.4999999999999716, -25.8333333333333},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed4(
      animation = false,
      r = {-0.053761, -0.053739, -0.014052})
      annotation (Placement(transformation(origin = {2.4999999999999716, -76.49999999999997},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b
      annotation (Placement(transformation(origin = {101.0, 76.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b1
      annotation (Placement(transformation(origin = {101.0, 26.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b2
      annotation (Placement(transformation(origin = {101.0, -24.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_b frame_b3
      annotation (Placement(transformation(origin = {101.0, -76.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a
      annotation (Placement(transformation(origin = {-100.0, 76.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a1
      annotation (Placement(transformation(origin = {-100.0, 24.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a2
      annotation (Placement(transformation(origin = {-100.0, -26.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a3
      annotation (Placement(transformation(origin = {-100.0, -76.0},
        extent = {{-16.0, -16.0}, {16.0, 16.0}})));
  equation
    connect(Dronefixed1.frame_a, frame_b)
      annotation (Line(origin = {64.0, 77.0},
        points = {{-52.0, -1.0}, {37.0, -1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed2.frame_a, frame_b1)
      annotation (Line(origin = {58.0, 25.0},
        points = {{-44.0, 0.0}, {-44.0, 1.0}, {43.0, 1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed3.frame_a, frame_b2)
      annotation (Line(origin = {57.0, -25.0},
        points = {{-45.0, -1.0}, {44.0, -1.0}, {44.0, 1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed4.frame_a, frame_b3)
      annotation (Line(origin = {58.0, -74.0},
        points = {{-46.0, -2.0}, {43.0, -2.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed1.frame_b, frame_a)
      annotation (Line(origin = {-54.0, 76.0},
        points = {{46.0, 0.0}, {-46.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed2.frame_b, frame_a1)
      annotation (Line(origin = {-53.0, 25.0},
        points = {{47.0, 0.0}, {45.0, 0.0}, {45.0, -1.0}, {-47.0, -1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(frame_a3, Dronefixed4.frame_b)
      annotation (Line(origin = {-54.0, -76.0},
        points = {{-46.0, 0.0}, {46.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(frame_a2, Dronefixed3.frame_b)
      annotation (Line(origin = {-54.0, -25.0},
        points = {{-46.0, -1.0}, {46.0, -1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
  end Arm;
  model QuadChassis "四旋翼本体+地面"
    annotation (Icon(coordinateSystem(extent = {{-200.0, -200.0}, {200.0, 200.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0},
      lineColor = {200, 200, 200},
      fillColor = {248, 248, 248},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-200.0, -200.0}, {200.0, 200.0}},
      radius = 25.0), Bitmap(origin = {-5.999999999999947, 7.628925581943946},
      extent = {{-137.50000000000006, -135.62892558194395}, {137.49999999999994, 135.62892558194395}},
      fileName = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Images/Sunray150.png"), Line(origin = {0.0, 35.0},
      rotation = 270.0,
      points = {{31.0, 0.0}, {-31.0, 0.0}},
      color = {255, 0, 0},
      thickness = 1.0,
      arrow = {Arrow.None, Arrow.Filled},
      arrowSize = 5.0), Line(origin = {35.99999999999998, 1.9999999999999982},
      rotation = 270.0,
      points = {{1.7763568394002505e-15, -35.99999999999999}, {-1.7763568394002505e-15, 36.00000000000002}},
      color = {0, 128, 0},
      thickness = 1.0,
      arrow = {Arrow.None, Arrow.Filled},
      arrowSize = 5.0), Text(origin = {-122.0, 141.0},
      lineColor = {0, 0, 0},
      extent = {{-4.0, 5.0}, {4.0, -5.0}},
      textString = "1",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {120.0, 141.0},
      lineColor = {0, 0, 0},
      extent = {{-6.0, 5.0}, {6.0, -5.0}},
      textString = "2",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {121.0, -119.0},
      lineColor = {0, 0, 0},
      extent = {{-5.0, 5.0}, {5.0, -5.0}},
      textString = "3",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {-117.0, -119.0},
      lineColor = {0, 0, 0},
      extent = {{-7.0, 5.0}, {7.0, -5.0}},
      textString = "4",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {-177.0, 116.0},
      lineColor = {0, 0, 0},
      extent = {{-3.0, 4.0}, {3.0, -4.0}},
      textString = "1",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {-176.0, 40.0},
      lineColor = {0, 0, 0},
      extent = {{-4.0, 4.0}, {4.0, -4.0}},
      textString = "2",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {-175.0, -42.0},
      lineColor = {0, 0, 0},
      extent = {{-5.0, 4.0}, {5.0, -4.0}},
      textString = "3",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {-175.0, -124.0},
      lineColor = {0, 0, 0},
      extent = {{-5.0, 4.0}, {5.0, -4.0}},
      textString = "4",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {10.0, 60.0},
      lineColor = {0, 0, 0},
      extent = {{-4.0, 4.0}, {4.0, -4.0}},
      textString = "X",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {68.0, 18.0},
      lineColor = {0, 0, 0},
      extent = {{-4.0, 16.0}, {4.0, -16.0}},
      textString = "Y",
      textStyle = {TextStyle.None},
      textColor = {0, 0, 0},
      horizontalAlignment = LinePattern.None), Text(origin = {0.0, 169.0},
      lineColor = {136, 136, 136},
      extent = {{-102.0, 97.0}, {102.0, -97.0}},
      textString = "QuadrotorBody",
      textStyle = {TextStyle.Bold},
      textColor = {136, 136, 136})}),
      Diagram(coordinateSystem(extent = {{-200.0, -200.0}, {200.0, 200.0}},
        grid = {2.0, 2.0})),
      experiment(Algorithm = Dassl, Interval = 0.001, StartTime = 0, StopTime = 30, Tolerance = 1e-10));
    parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile
      "Source-labeled virtual plant profile; not identified real-aircraft truth";
    inner Modelica.Mechanics.MultiBody.World world(
      animateWorld = false,
      animateGravity = false,
      n = {0, 0, -1},
      gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity,
      g = profile.gravity_mps2)

      annotation (Placement(transformation(origin = {124.60787940430421, 90.30849111731482},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    parameter Real lift_cofficient = profile.mworks_visual_thrust_coefficient
      "PX4 Gazebo Classic physical Ct scaled by rotorVelocitySlowdownSim squared for MWORKS visual speed";
    Modelica.Mechanics.MultiBody.Parts.BodyShape body(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      r_CM = {0, 0, 0},
      m = profile.mworks_quad_chassis_body_mass_kg,
      I_11 = profile.body_inertia_diagonal_kg_m2[1],
      I_22 = profile.body_inertia_diagonal_kg_m2[2],
      I_33 = profile.body_inertia_diagonal_kg_m2[3],
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_body.stl",
      r_shape = {0, 0, 0.0525},
      lengthDirection = {0, -1, 0},
      widthDirection = {1, 0, 0},
      length = 0.03,
      width = 0.03,
      height = 0.03,
      extra = 1,
      color = {255, 141, 11},
      specularCoefficient = 1,
      r_0(fixed = false),
      enforceStates = true) annotation (Placement(transformation(origin = {145.7168984524965, -2.964434436258074},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.BodyShape propellers1(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      m = profile.rotor_mass_kg,
      I_11 = profile.rotor_inertia_diagonal_kg_m2[1],
      I_22 = profile.rotor_inertia_diagonal_kg_m2[2],
      I_33 = profile.rotor_inertia_diagonal_kg_m2[3],
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_propeller.stl",
      r_shape = {0, 0, 0},
      lengthDirection = {1, 0, 0},
      widthDirection = {0, 1, 0},
      length = 0.00125,
      width = 0.00125,
      height = 0.00125,
      extra = 1,
      color = {192, 192, 192},
      r_0(fixed = false),
      specularCoefficient = 1) annotation (Placement(transformation(origin = {-8.223051505802104, 99.50262144364181},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute1(
      animation = false,
      n = {0, 0, 1},
      useAxisFlange = true)
      annotation (Placement(transformation(origin = {33.77694849419791, 99.50262144364181},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed1(
      animation = false,
      r = {profile.mworks_rotor_center_m[1, 1], profile.mworks_rotor_center_m[1, 2], profile.mworks_rotor_center_m[1, 3]})
      annotation (Placement(transformation(origin = {73.77694849419791, 99.5026214436419},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute2(
      animation = false,
      n = {0, 0, 1},
      useAxisFlange = true)
      annotation (Placement(transformation(origin = {33.77694849419791, 37.50262144364184},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed2(
      animation = false,
      r = {profile.mworks_rotor_center_m[2, 1], profile.mworks_rotor_center_m[2, 2], profile.mworks_rotor_center_m[2, 3]})
      annotation (Placement(transformation(origin = {73.77694849419791, 39.502621443641885},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute3(
      animation = false,
      n = {0, 0, 1},
      useAxisFlange = true)
      annotation (Placement(transformation(origin = {33.77694849419791, -40.49737855635814},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed3(
      animation = false,
      r = {profile.mworks_rotor_center_m[3, 1], profile.mworks_rotor_center_m[3, 2], profile.mworks_rotor_center_m[3, 3]})
      annotation (Placement(transformation(origin = {73.77694849419791, -40.497378556358086},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Joints.Revolute revolute4(
      animation = false,
      n = {0, 0, 1},
      useAxisFlange = true)
      annotation (Placement(transformation(origin = {33.77694849419791, -100.49737855635817},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedTranslation Dronefixed4(
      animation = false,
      r = {profile.mworks_rotor_center_m[4, 1], profile.mworks_rotor_center_m[4, 2], profile.mworks_rotor_center_m[4, 3]})
      annotation (Placement(transformation(origin = {73.7769484941979, -100.49737855635811},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Forces.WorldForce force1(resolveInFrame=Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b, animation=false) annotation (Placement(transformation(origin = {-43.68550815051444, 80.71820959281155},
        extent = {{10.0, -10.0}, {-10.0, 10.0}},
        rotation = -180.0)));
    Modelica.Mechanics.MultiBody.Forces.WorldForce force2(resolveInFrame=Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b, animation=false) annotation (Placement(transformation(origin = {-43.68550815051444, 20.437682636071557},
        extent = {{10.0, -10.0}, {-10.0, 10.0}},
        rotation = -180.0)));
    Modelica.Mechanics.MultiBody.Forces.WorldForce force3(resolveInFrame=Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b, animation=false) annotation (Placement(transformation(origin = {-43.68550815051444, -61.29549361916214},
        extent = {{10.0, -10.0}, {-10.0, 10.0}},
        rotation = -180.0)));
    Modelica.Mechanics.MultiBody.Forces.WorldForce force4(resolveInFrame=Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b, animation=false) annotation (Placement(transformation(origin = {-43.68550815051444, -121.52273778588403},
        extent = {{10.0, -10.0}, {-10.0, 10.0}},
        rotation = -180.0)));
    Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a
      annotation (Placement(transformation(origin = {198.73389546164995, -2.6981293698647804},
        extent = {{-16.0, -16.0}, {16.0, 16.0}}),
        iconTransformation(origin = {201.16363719723324, -0.25785116388788687},
          extent = {{-16.0, -16.0}, {16.0, 16.0}})));
    Modelica.Mechanics.MultiBody.Parts.FixedRotation fixedRotation(r = {0, 0, -0.05},
      animation = false) annotation (Placement(transformation(origin = {158.25275041021322, 90.48433844745136},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Visualizers.FixedShape2 fixedShape2_1(shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/Jichang1.stl",
      extra = 1, length = 4, width = 4, height = 4, color = {155, 155, 155}, animation = false) annotation (Placement(transformation(origin = {191.55742017263336, 92.28481521933296},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor annotation (
      Placement(transformation(origin = {-167.0062898849564, 81.17560498021649},
        extent = {{10.0, 10.0}, {-10.0, -10.0}},
        rotation = 180.0)));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange_a annotation (Placement(transformation(origin = {-202.121, 118.705},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {-200.40059043098444, 117.73391675003751},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    Modelica.Blocks.Math.Gain gain2(k = lift_cofficient)
      annotation (Placement(transformation(origin = {-86.81308142887323, 80.23120583227565},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Product PF3
      annotation (Placement(transformation(origin = {-118.58572547423151, 80.06209401758375},
        extent = {{-11.0, -11.0}, {11.0, 11.0}})));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor1 annotation (
      Placement(transformation(origin = {-164.99920358087837, 21.03024798179142},
        extent = {{10.0, 10.0}, {-10.0, -10.0}},
        rotation = 180.0)));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange_a1 annotation (Placement(transformation(origin = {-203.656, 58.8397},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {-200.40059043098444, 38.95688026849126},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    Modelica.Blocks.Math.Gain gain3(k = lift_cofficient)
      annotation (Placement(transformation(origin = {-84.80599512479517, 20.085848833850648},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Product PF4
      annotation (Placement(transformation(origin = {-116.57863917015342, 19.91673701915868},
        extent = {{-11.0, -11.0}, {11.0, 11.0}})));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor2 annotation (
      Placement(transformation(origin = {-161.75066788483727, -60.34082342126454},
        extent = {{10.0, 10.0}, {-10.0, -10.0}},
        rotation = 180.0)));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange_a2 annotation (Placement(transformation(origin = {-202.548, -22.2587},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {-200.40059043098444, -39.820156213054986},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    Modelica.Blocks.Math.Gain gain4(k = lift_cofficient)
      annotation (Placement(transformation(origin = {-81.55745942875407, -61.28522256920533},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Product PF5
      annotation (Placement(transformation(origin = {-113.33010347411226, -61.45433438389731},
        extent = {{-11.0, -11.0}, {11.0, 11.0}})));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor3 annotation (
      Placement(transformation(origin = {-161.3686131501953, -120.82889806644587},
        extent = {{10.0, 10.0}, {-10.0, -10.0}},
        rotation = 180.0)));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange_a3 annotation (Placement(transformation(origin = {-203.305, -81.059},
      extent = {{-10.0, -10.0}, {10.0, 10.0}}),
      iconTransformation(origin = {-200.40059043098444, -118.59719269460122},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));

    Modelica.Blocks.Math.Gain gain5(k = lift_cofficient)
      annotation (Placement(transformation(origin = {-81.17540469411205, -121.77329721438676},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Product PF6
      annotation (Placement(transformation(origin = {-112.9480487394703, -121.9424090290787},
        extent = {{-11.0, -11.0}, {11.0, 11.0}})));
    GroundModel.TouchModel touchModel(V_s = 0, Cst = 0, Vtr = 0, Cdy = 0,
      Fs(animation
         = false))
      annotation (Placement(transformation(origin = {144.0, 48.0},
        extent = {{-10.0, 10.0}, {10.0, -10.0}},
        rotation = -90.0)));
    Modelica.Mechanics.MultiBody.Parts.BodyShape propellers2(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      m = profile.rotor_mass_kg,
      I_11 = profile.rotor_inertia_diagonal_kg_m2[1],
      I_22 = profile.rotor_inertia_diagonal_kg_m2[2],
      I_33 = profile.rotor_inertia_diagonal_kg_m2[3],
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_propeller.stl",
      r_shape = {0, 0, 0},
      lengthDirection = {1, 0, 0},
      widthDirection = {0, 1, 0},
      length = 0.00125,
      width = 0.00125,
      height = 0.00125,
      extra = 1,
      color = {192, 192, 192},
      specularCoefficient = 1,
      r_0(fixed = false))
      annotation (Placement(transformation(origin = {-8.223051505802104, 37.50262144364186},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.BodyShape propellers3(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      m = profile.rotor_mass_kg,
      I_11 = profile.rotor_inertia_diagonal_kg_m2[1],
      I_22 = profile.rotor_inertia_diagonal_kg_m2[2],
      I_33 = profile.rotor_inertia_diagonal_kg_m2[3],
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_propeller.stl",
      r_shape = {0, 0, 0},
      lengthDirection = {1, 0, 0},
      widthDirection = {0, 1, 0},
      length = 0.00125,
      width = 0.00125,
      height = 0.00125,
      extra = 1,
      color = {192, 192, 192},
      specularCoefficient = 1,
      r_0(fixed = false))
      annotation (Placement(transformation(origin = {-8.223051505802102, -40.49737855635814},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
    Modelica.Mechanics.MultiBody.Parts.BodyShape propellers4(
      animation = true,
      animateSphere = false,
      r = {0, 0, 0},
      m = profile.rotor_mass_kg,
      I_11 = profile.rotor_inertia_diagonal_kg_m2[1],
      I_22 = profile.rotor_inertia_diagonal_kg_m2[2],
      I_33 = profile.rotor_inertia_diagonal_kg_m2[3],
      I_21 = 0,
      I_31 = 0,
      I_32 = 0,
      shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_mid360_propeller.stl",
      r_shape = {0, 0, 0},
      lengthDirection = {1, 0, 0},
      widthDirection = {0, 1, 0},
      length = 0.00125,
      width = 0.00125,
      height = 0.00125,
      extra = 1,
      color = {192, 192, 192},
      specularCoefficient = 1,
      r_0(fixed = false))
      annotation (Placement(transformation(origin = {-8.223051505802102, -100.4973785563582},
        extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  equation
    force1.force[1] = 0;
    force1.force[2] = 0;
    force2.force[1] = 0;
    force2.force[2] = 0;
    force3.force[1] = 0;
    force3.force[2] = 0;
    force4.force[1] = 0;
    force4.force[2] = 0;
    connect(propellers1.frame_a, revolute1.frame_b)
      annotation (Line(origin = {12.776948494197939, 99.50262144364183},
        points = {{-11.0, 0.0}, {11.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute1.frame_a, Dronefixed1.frame_b)
      annotation (Line(origin = {53.77694849419794, 99.50262144364183},
        points = {{-10.0, 0.0}, {10.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed1.frame_a, body.frame_b)
      annotation (Line(origin = {104.77694849419794, 49.50262144364184},
        points = {{-21.0, 50.0}, {-1.0, 50.0}, {-1.0, -52.0}, {31.0, -52.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute2.frame_a, Dronefixed2.frame_b)
      annotation (Line(origin = {53.77694849419794, 39.50262144364184},
        points = {{-10.0, -2.0}, {12.0, -2.0}, {12.0, 0.0}, {10.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute3.frame_a, Dronefixed3.frame_b)
      annotation (Line(origin = {53.77694849419794, -40.49737855635815},
        points = {{-10.0, 0.0}, {10.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute4.frame_a, Dronefixed4.frame_b)
      annotation (Line(origin = {53.77694849419794, -100.49737855635817},
        points = {{-10.0, 0.0}, {10.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed2.frame_a, body.frame_b)
      annotation (Line(origin = {104.77694849419794, 19.502621443641846},
        points = {{-21.0, 20.0}, {-1.0, 20.0}, {-1.0, -22.0}, {31.0, -22.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed3.frame_a, body.frame_b)
      annotation (Line(origin = {104.77694849419794, -20.497378556358157},
        points = {{-21.0, -20.0}, {-1.0, -20.0}, {-1.0, 18.0}, {31.0, 18.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(Dronefixed4.frame_a, body.frame_b)
      annotation (Line(origin = {104.77694849419794, -50.49737855635815},
        points = {{-21.0, -50.0}, {-1.0, -50.0}, {-1.0, 48.0}, {31.0, 48.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(force1.frame_b, Dronefixed1.frame_b)
      annotation (Line(origin = {-27.22305150580206, 99.50262144364183},
        points = {{-6.0, -19.0}, {90.0, -19.0}, {90.0, 0.0}, {91.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(force2.frame_b, Dronefixed2.frame_b)
      annotation (Line(origin = {-27.22305150580206, 39.50262144364184},
        points = {{-6.0, -19.0}, {90.0, -19.0}, {90.0, 0.0}, {91.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(force3.frame_b, Dronefixed3.frame_b)
      annotation (Line(origin = {-27.22305150580206, -40.49737855635815},
        points = {{-6.0, -21.0}, {90.0, -21.0}, {90.0, 0.0}, {91.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(force4.frame_b, Dronefixed4.frame_b)
      annotation (Line(origin = {-27.22305150580206, -100.49737855635817},
        points = {{-6.0, -21.0}, {96.0, -21.0}, {96.0, 0.0}, {91.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(world.frame_b, fixedRotation.frame_a)
      annotation (Line(origin = {141.19763229997702, 89.57095262067975},
        points = {{-7.0, 1.0}, {7.0, 1.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(fixedRotation.frame_b, fixedShape2_1.frame_a)
      annotation (Line(origin = {176.88393527497624, 90.4095726524103},
        points = {{-9.0, 0.0}, {5.0, 0.0}, {5.0, 2.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(flange_a, speedSensor.flange)
      annotation (Line(origin = {-152.40323470449508, 109.45508643941054},
        points = {{-50.0, 9.0}, {-31.0, 9.0}, {-31.0, -28.0}, {-25.0, -28.0}},
        color = {0, 0, 0}));
    connect(PF3.y, gain2.u)
      annotation (Line(origin = {-116.0632797293461, 80.06209401758369},
        points = {{10.0, 0.0}, {17.0, 0.0}},
        color = {0, 0, 127}));
    connect(speedSensor.w, PF3.u1)
      annotation (Line(origin = {-143.70360332410846, 83.94180069248642},
        points = {{-12.0, -3.0}, {-4.0, -3.0}, {-4.0, 3.0}, {12.0, 3.0}},
        color = {0, 0, 127}));
    connect(PF3.u2, speedSensor.w)
      annotation (Line(origin = {-143.70360332410846, 77.94180069248642},
        points = {{12.0, -4.0}, {-4.0, -4.0}, {-4.0, 3.0}, {-12.0, 3.0}},
        color = {0, 0, 127}));
    connect(gain2.y, force1.force[3])
      annotation (Line(origin = {-68.5072156121318, 80.71820959281146},
        points = {{-7.0, 0.0}, {13.0, 0.0}},
        color = {0, 0, 127}));
    connect(revolute1.axis, flange_a)
      annotation (Line(origin = {-84.22305150580206, 114.50262144364183},
        points = {{118.0, -5.0}, {118.0, 4.0}, {-118.0, 4.0}},
        color = {0, 0, 0}));
    connect(flange_a1, speedSensor1.flange)
      annotation (Line(origin = {-154.68031250674682, 30.52531759015514},
        points = {{-49.0, 28.0}, {-29.0, 28.0}, {-29.0, -9.0}, {-20.0, -9.0}},
        color = {0, 0, 0}));
    connect(PF4.y, gain3.u)
      annotation (Line(origin = {-114.05619342526796, 19.916737019158653},
        points = {{10.0, 0.0}, {17.0, 0.0}},
        color = {0, 0, 127}));
    connect(speedSensor1.w, PF4.u1)
      annotation (Line(origin = {-141.69651702003043, 23.796443694061388},
        points = {{-12.0, -3.0}, {-13.0, -3.0}, {-13.0, 3.0}, {12.0, 3.0}},
        color = {0, 0, 127}));
    connect(PF4.u2, speedSensor1.w)
      annotation (Line(origin = {-141.69651702003043, 17.796443694061374},
        points = {{12.0, -4.0}, {-13.0, -4.0}, {-13.0, 3.0}, {-12.0, 3.0}},
        color = {0, 0, 127}));
    connect(revolute2.axis, flange_a1)
      annotation (Line(origin = {-84.22305150580206, 54.50262144364184},
        points = {{118.0, -7.0}, {118.0, 4.0}, {-119.0, 4.0}},
        color = {0, 0, 0}));
    connect(gain3.y, force2.force[3])
      annotation (Line(origin = {-65.96584132947362, 20.437682636071507},
        points = {{-8.0, 0.0}, {10.0, 0.0}},
        color = {0, 0, 127}));
    connect(flange_a2, speedSensor2.flange)
      annotation (Line(origin = {-153.16495306593922, -30.04763875009685},
        points = {{-49.0, 8.0}, {-29.0, 8.0}, {-29.0, -30.0}, {-19.0, -30.0}},
        color = {0, 0, 0}));
    connect(PF5.y, gain4.u)
      annotation (Line(origin = {-110.80765772922683, -61.45433438389731},
        points = {{10.0, 0.0}, {17.0, 0.0}},
        color = {0, 0, 127}));
    connect(speedSensor2.w, PF5.u1)
      annotation (Line(origin = {-138.44798132398932, -57.574627708994576},
        points = {{-12.0, -3.0}, {-12.0, 3.0}, {12.0, 3.0}},
        color = {0, 0, 127}));
    connect(PF5.u2, speedSensor2.w)
      annotation (Line(origin = {-138.44798132398932, -63.574627708994605},
        points = {{12.0, -4.0}, {-12.0, -4.0}, {-12.0, 3.0}},
        color = {0, 0, 127}));
    connect(gain4.y, force3.force[3])
      annotation (Line(origin = {-63.48987525056839, -60.29549361916214},
        points = {{-7.0, -1.0}, {8.0, -1.0}},
        color = {0, 0, 127}));
    connect(revolute3.axis, flange_a2)
      annotation (Line(origin = {-84.22305150580206, -25.497378556358157},
        points = {{118.0, -5.0}, {118.0, 3.0}, {-118.0, 3.0}},
        color = {0, 0, 0}));
    connect(flange_a3, speedSensor3.flange)
      annotation (Line(origin = {-151.0497220760636, -111.33382845808222},
        points = {{-52.0, 30.0}, {-29.0, 30.0}, {-29.0, -9.0}, {-20.0, -9.0}},
        color = {0, 0, 0}));
    connect(PF6.y, gain5.u)
      annotation (Line(origin = {-110.42560299458489, -121.9424090290787},
        points = {{10.0, 0.0}, {17.0, 0.0}},
        color = {0, 0, 127}));
    connect(speedSensor3.w, PF6.u1)
      annotation (Line(origin = {-138.06592658934738, -118.06270235417597},
        points = {{-12.0, -3.0}, {-12.0, 3.0}, {12.0, 3.0}},
        color = {0, 0, 127}));
    connect(PF6.u2, speedSensor3.w)
      annotation (Line(origin = {-138.06592658934738, -124.062702354176},
        points = {{12.0, -4.0}, {-12.0, -4.0}, {-12.0, 3.0}},
        color = {0, 0, 127}));
    connect(revolute4.axis, flange_a3)
      annotation (Line(origin = {-84.22305150580206, -85.49737855635817},
        points = {{118.0, -5.0}, {118.0, 4.0}, {-119.0, 4.0}},
        color = {0, 0, 0}));
    connect(gain5.y, force4.force[3])
      annotation (Line(origin = {-62.685508150514465, -121.52273778588409},
        points = {{-7.0, 0.0}, {7.0, 0.0}},
        color = {0, 0, 127}));
    connect(touchModel.frame_a, world.frame_b)
      annotation (Line(origin = {143.0, 75.0},
        points = {{1.0, -17.0}, {1.0, 15.0}, {-8.0, 15.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(touchModel.frame_b, body.frame_a)
      annotation (Line(origin = {150.0, 18.0},
        points = {{-6.0, 20.0}, {-6.0, -6.0}, {6.0, -6.0}, {6.0, -21.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(body.frame_b, frame_a)
      annotation (Line(origin = {167.0, -7.0},
        points = {{-31.0, 4.0}, {-33.0, 4.0}, {-33.0, -9.0}, {8.0, -9.0}, {8.0, 4.0}, {32.0, 4.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute2.frame_b, propellers2.frame_a)
      annotation (Line(origin = {13.0, 38.0},
        points = {{10.77694849419791, -0.4973785563581572}, {-11.223051505802104, -0.497378556358143}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute3.frame_b, propellers3.frame_a)
      annotation (Line(origin = {13.0, -40.0},
        points = {{11.0, 0.0}, {-11.0, 0.0}},
        color = {95, 95, 95},
        thickness = 0.5));
    connect(revolute4.frame_b, propellers4.frame_a)
      annotation (Line(origin = {13.0, -100.0},
        points = {{10.77694849419791, -0.4973785563581714}, {-11.223051505802102, -0.49737855635819983}},
        color = {95, 95, 95},
        thickness = 0.5));
  end QuadChassis;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Mechanics;
