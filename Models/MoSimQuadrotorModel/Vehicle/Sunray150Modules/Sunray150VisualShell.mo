within MoSimQuadrotorModel.Vehicle.Sunray150Modules;
model Sunray150VisualShell
  "Massless Sunray150 body and rotor visuals attached to the formal plant frame"

  parameter MoSimQuadrotorModel.Parameters.Sunray150Parameters profile;

  Modelica.Mechanics.MultiBody.Interfaces.Frame_a frame_a
    "Physical body frame; this shell applies neither force nor torque" 
    annotation(Placement(transformation(origin = {-140, 35}, extent = {{-14, -14}, {14, 14}})));
  Modelica.Blocks.Interfaces.RealInput rotor_speed[4](each unit = "rad/s")
    "Signed physical rotor speeds used only to animate the propellers" 
    annotation(Placement(transformation(origin = {-140, -70}, extent = {{-14, -14}, {14, 14}})));
  Real rotor_phase[4](each unit = "rad", each start = 0, each fixed = true)
    "Visual-only propeller phase; it does not feed the plant";

  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape body_visual(
    // This is the same propeller-free DAE body asset and the same +X 90 degree
    // visual rotation used by the accepted Gazebo SDF assembly.
    shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_dae_mid360_realistic_material_audit_gazebo_body_static.obj",
    R = Modelica.Mechanics.MultiBody.Frames.absoluteRotation(
      frame_a.R,
      Modelica.Mechanics.MultiBody.Frames.axisRotation(1, Modelica.Constants.pi / 2, 0)),
    r = frame_a.r_0,
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = 1,
    width = 1,
    height = 1,
    extra = 0,
    color = {255, 141, 11},
    specularCoefficient = 1) 
    annotation(Placement(transformation(origin = {0, 35}, extent = {{-42, -30}, {42, 30}})));
  // These files are the accepted Gazebo rotor-link-local meshes copied without
  // a coordinate conversion. They are deliberately four named Shape instances
  // rather than a Shape[4] array: Sysplorer 2026a evaluated the previous array
  // comprehension incorrectly for rotor 3 and overlapped it with rotor 2.
  // MWORKS order is {gazebo_0, gazebo_2, gazebo_1, gazebo_3}.
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape propeller_front_right_visual(
    shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_propeller_rotor_0_link_local.stl",
    R = Modelica.Mechanics.MultiBody.Frames.absoluteRotation(
      frame_a.R,
      Modelica.Mechanics.MultiBody.Frames.axisRotation(3, rotor_phase[1], rotor_speed[1])),
    r = frame_a.r_0 + Modelica.Mechanics.MultiBody.Frames.resolve1(
      frame_a.R, {profile.mworks_rotor_center_m[1, 1], profile.mworks_rotor_center_m[1, 2], profile.mworks_rotor_center_m[1, 3]}),
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = 1,
    width = 1,
    height = 1,
    extra = 0,
    color = {192, 192, 192},
    specularCoefficient = 1) 
    annotation(Placement(transformation(origin = {-70, -15}, extent = {{-25, -18}, {25, 18}})));
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape propeller_front_left_visual(
    shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_propeller_rotor_2_link_local.stl",
    R = Modelica.Mechanics.MultiBody.Frames.absoluteRotation(
      frame_a.R,
      Modelica.Mechanics.MultiBody.Frames.axisRotation(3, rotor_phase[2], rotor_speed[2])),
    r = frame_a.r_0 + Modelica.Mechanics.MultiBody.Frames.resolve1(
      frame_a.R, {profile.mworks_rotor_center_m[2, 1], profile.mworks_rotor_center_m[2, 2], profile.mworks_rotor_center_m[2, 3]}),
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = 1,
    width = 1,
    height = 1,
    extra = 0,
    color = {192, 192, 192},
    specularCoefficient = 1) 
    annotation(Placement(transformation(origin = {70, -15}, extent = {{-25, -18}, {25, 18}})));
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape propeller_back_left_visual(
    shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_propeller_rotor_1_link_local.stl",
    R = Modelica.Mechanics.MultiBody.Frames.absoluteRotation(
      frame_a.R,
      Modelica.Mechanics.MultiBody.Frames.axisRotation(3, rotor_phase[3], rotor_speed[3])),
    r = frame_a.r_0 + Modelica.Mechanics.MultiBody.Frames.resolve1(
      frame_a.R, {profile.mworks_rotor_center_m[3, 1], profile.mworks_rotor_center_m[3, 2], profile.mworks_rotor_center_m[3, 3]}),
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = 1,
    width = 1,
    height = 1,
    extra = 0,
    color = {192, 192, 192},
    specularCoefficient = 1) 
    annotation(Placement(transformation(origin = {-70, -65}, extent = {{-25, -18}, {25, 18}})));
  Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape propeller_back_right_visual(
    shapeType = "modelica://MoSimQuadrotorModel/Vehicle/Resources/Visualization/sunray150_propeller_rotor_3_link_local.stl",
    R = Modelica.Mechanics.MultiBody.Frames.absoluteRotation(
      frame_a.R,
      Modelica.Mechanics.MultiBody.Frames.axisRotation(3, rotor_phase[4], rotor_speed[4])),
    r = frame_a.r_0 + Modelica.Mechanics.MultiBody.Frames.resolve1(
      frame_a.R, {profile.mworks_rotor_center_m[4, 1], profile.mworks_rotor_center_m[4, 2], profile.mworks_rotor_center_m[4, 3]}),
    r_shape = {0, 0, 0},
    lengthDirection = {1, 0, 0},
    widthDirection = {0, 1, 0},
    length = 1,
    width = 1,
    height = 1,
    extra = 0,
    color = {192, 192, 192},
    specularCoefficient = 1) 
    annotation(Placement(transformation(origin = {70, -65}, extent = {{-25, -18}, {25, 18}})));

equation
  // The visual shell is a measurement-only MultiBody branch and cannot alter
  // the mass, inertia, wrench, or fault behavior owned by PhysicalWrenchAdapter.
  frame_a.f = zeros(3);
  frame_a.t = zeros(3);
  for i in 1:4 loop
    der(rotor_phase[i]) = rotor_speed[i];
  end for;

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {160, 80, 0},
        fillColor = {255, 250, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 18}, extent = {{-88, 32}, {88, -32}},
        textString = "Visual", textColor = {160, 80, 0},
        textStyle = {TextStyle.Bold}),
      Text(origin = {0, -22}, extent = {{-88, 28}, {88, -28}},
        textString = "Shell", textColor = {160, 80, 0},
        textStyle = {TextStyle.Bold}),
      Text(origin = {0, -74}, extent = {{-92, 16}, {92, -16}},
        textString = "3D Animation Only", textColor = {200, 140, 80})}),
    Diagram(coordinateSystem(extent = {{-165, -105}, {165, 105}}, grid = {2, 2})),
    __MWORKS(hide = false, version = "26.3.0"));
end Sunray150VisualShell;