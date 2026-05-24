model GearUnit_main2
  annotation(cad_toolbox = true, cad_toolbox_model = false, cad_toolbox_icon = "GearUnit_main_20250427172057.png", Diagram(coordinateSystem(extent = {{-300, -300}, {300, 300}}, 
    grid = {2, 2})), Icon(coordinateSystem(extent = {{-300, -300}, {300, 300}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {0, 0}, 
    fillColor = {255, 255, 255}, 
    fillPattern = FillPattern.Solid, 
    lineThickness = 5, 
    borderPattern = BorderPattern.Engraved, 
    extent = {{-300, -300}, {300, 300}}), Bitmap(extent = {{-297, -297}, {297, 297}}, 
    fileName = "Visualizers/GearUnit_main_20250427172057.png"), Text(origin = {0, 220}, 
    extent = {{-150, 100}, {150, 140}}, 
    textString = "%name", textColor = {0, 0, 255}, 
    horizontalAlignment = LinePattern.None)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001));
  Default5.GearUnit.Worm1_2_5 Worm1_2_5_1_1 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-16, -94}, 
    extent = {{-30, -30}, {30, 30}})));

  Default5.GearUnit.BevelGear34X2 BevelGear34X2_1_1 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-16, 1.11022e-16}, 
    extent = {{-30, -30}, {30, 30}})));

  Default5.GearUnit.Fixed Fixed1_1 
    annotation(cad_toolbox = true, Placement(transformation(origin = {120, 0}, extent = {{-30, -30}, {30, 30}})));

  Default5.GearUnit.First First1 
    annotation(cad_toolbox = true, Placement(transformation(origin = {252, -8.88178e-16}, 
    extent = {{-30, -30}, {30, 30}})));

  Default5.GearUnit.Second Second1 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-16, 80}, 
    extent = {{-30, -30}, {30, 30}})));

  TYMultibody.Joints.Revolute Revolute6(n = {-0.68222558634882, 0.73114174366604, 0}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {60, -28}, 
    extent = {{-10, -10}, {10, 10}})));

  TYMultibody.Joints.Revolute Revolute4(n = {0, 0, -1}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {180, 30}, extent = {{-10, -10}, {10, 10}})));

  TYMultibody.Joints.Fixed Fixed1(r = {-0.03056920367697, -0.01867525317285, -0.06283598608669}) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {180, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 180)));

  TYMultibody.Joints.Revolute Revolute3(n = {0.85335544163685, 0.52132954091322, 0}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {60, 0}, extent = {{10, -10}, {-10, 10}})));

  TYMultibody.Joints.Revolute Revolute5(n = {0, 0, 1}, animation = false, useAxisFlange = true) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {60, 30}, 
    extent = {{-10, 10}, {10, -10}})));

  inner TYMultibody.World world(n = {0, -1, 0}, animateWorld = false, animateGravity = false) 
    annotation(cad_toolbox = true, Placement(transformation(origin = {-60, 210}, extent = {{-10, -10}, {10, 10}})));
  TYDriveline.Gears.StairGear.Bevelgear bevelgear(zA = 34, zB = 17) 
    annotation(Placement(transformation(origin = {128, -74}, 
    extent = {{-10, -10}, {10, 10}})));
  TYMechanics.Rotational.Sources.AngleVelocity angleVelocity 
    annotation(Placement(transformation(origin = {-50, -40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const 
    annotation(Placement(transformation(origin = {-88, -40}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline.Gears.CylindericalGear cylindericalGear(userWorkingPitch = false, z2 = 34) 
    annotation(Placement(transformation(origin = {154, 66}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline.Gears.WormGearAdv wormGearAdv(i = 28) 
    annotation(Placement(transformation(origin = {86, 100}, 
    extent = {{10, -10}, {-10, 10}})));
equation
  connect(Worm1_2_5_1_1.Marker5, Revolute6.frame_a) 
    annotation(Line(origin = {40, 0}, 
    points = {{-26, -94}, {-4, -94}, {-4, -28}, {10, -28}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(Fixed1_1.Marker5, Revolute6.frame_b) 
    annotation(Line(origin = {80, -7.5}, 
    points = {{10, -7.5}, {4, -7.5}, {4, -20.5}, {-10, -20.5}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(Fixed1_1.Marker3, Revolute4.frame_a) 
    annotation(Line(origin = {160, 20}, 
    points = {{-10, -10}, {6.4, -10}, {6.4, 10}, {10, 10}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(First1.Marker3, Revolute4.frame_b) 
    annotation(Line(origin = {200, 15}, 
    points = {{22, -15}, {-6.4, -15}, {-6.4, 15}, {-10, 15}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(Fixed1_1.Marker2, Revolute3.frame_a) 
    annotation(Line(origin = {80, 0}, 
    points = {{10, 0}, {-10, 0}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(BevelGear34X2_1_1.Marker2, Revolute3.frame_b) 
    annotation(Line(origin = {40, 45}, 
    points = {{-26, -45}, {10, -45}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(Fixed1_1.Marker4, Revolute5.frame_b) 
    annotation(Line(origin = {80, 22.5}, 
    points = {{10, -7.5}, {-6.4, -7.5}, {-6.4, 7.5}, {-10, 7.5}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(Second1.Marker4, Revolute5.frame_a) 
    annotation(Line(origin = {40, 105}, 
    points = {{-26, -25}, {-8, -25}, {-8, -75}, {10, -75}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(Fixed1_1.Marker1, Fixed1.frame_b) 
    annotation(Line(origin = {160, -20}, 
    points = {{-10, 10}, {6.4, 10}, {6.4, -10}, {10, -10}}, 
    color = {95, 95, 95}, 
    thickness = 0.5), cad_toolbox = true);
  connect(bevelgear.flange_a, Revolute3.axis) 
    annotation(Line(origin = {80, -42}, 
    points = {{38, -32}, {-38, -32}, {-38, 32}, {-27, 32}}, 
    color = {96, 96, 96}));
  connect(bevelgear.flange_b, Revolute4.axis) 
    annotation(Line(origin = {158, -40}, 
    points = {{-30, -44}, {-30, -60}, {29, -60}, {29, 60}}, 
    color = {0, 0, 0}));
  connect(angleVelocity.flange, Revolute3.axis) 
    annotation(Line(origin = {7, -25}, 
    points = {{-47, -15}, {13, -15}, {13, 15}, {46, 15}}, 
    color = {0, 0, 0}));
  connect(angleVelocity.om_ref, const.y) 
    annotation(Line(origin = {-68, -40}, 
    points = {{8, 0}, {-9, 0}}, 
    color = {0, 0, 127}));
  connect(cylindericalGear.flange_b, Revolute4.axis) 
    annotation(Line(origin = {199, 39}, 
    points = {{-35, 23}, {7, 23}, {7, -139}, {-12, -139}, {-12, -19}}, 
    color = {96, 96, 96}));
  connect(cylindericalGear.flange_a, Revolute5.axis) 
    annotation(Line(origin = {106, 45}, 
    points = {{38, 25}, {-39, 25}, {-39, -5}}, 
    color = {96, 96, 96}));
  connect(wormGearAdv.flange1, Revolute5.axis) 
    annotation(Line(origin = {79, 75}, 
    points = {{-3, 27.8}, {-12, 27.8}, {-12, -35}}, 
    color = {0, 0, 0}));
  connect(Revolute6.axis, wormGearAdv.flange2) 
    annotation(Line(origin = {92, 19}, 
    points = {{-25, -57}, {-25, -71}, {116, -71}, {116, 74.85}, {3.8, 74.85}}, 
    color = {96, 96, 96}));


end GearUnit_main2;