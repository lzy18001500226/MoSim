within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model Px4CtrlGraphicalRealStateClosedLoopEquivalenceHarness
  "Full physical comparison: graphical PX4CTRL with real sensors versus the formal EquationBridge runner"

  parameter Real controller_sample_period_s(unit = "s") = 0.01;
  parameter Real quaternion_domain_margin(min = 0, max = 0.01) = 1e-7;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_collective_thrust_n = 4
    * profile.mworks_visual_thrust_coefficient
    * profile.mworks_hover_visual_rotor_speed_rad_s ^ 2;

  MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock graphical_outer 
    annotation(
      Placement(transformation(origin = {-100, 75}, extent = {{-55, -55}, {55, 55}})),
      __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Control.Allocation.OfflineAttitudeRateAllocator graphical_inner_allocator(
    use_body_rate_mea = true) 
    annotation(Placement(transformation(origin = {55, 75}, extent = {{-45, -28}, {45, 28}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly graphical_plant 
    annotation(Placement(transformation(origin = {165, 5}, extent = {{-52, -75}, {52, 75}})));
  MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlEquationBridgeFormalRunner equation_formal 
    annotation(Placement(transformation(origin = {165, -175}, extent = {{-55, -55}, {55, 55}})));
  MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath graphical_reference 
    annotation(Placement(transformation(origin = {-205, 75}, extent = {{-20, -15}, {20, 15}})));

  Modelica.Blocks.Sources.Constant ref_yaw_zero(k = 0) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression yaw_mea_from_reordered_quat(
    y = graphical_attitude_mea_from_quat[3]) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Math.Gain graphical_output_capture[8](each k = 1);

  Real graphical_quat_xyzw[4]
    "Raw Modelica MultiBody sensor quaternion {x, y, z, w}";
  Real graphical_quat_wxyz[4]
    "Explicit PX4-style reordered quaternion {w, x, y, z}";
  Real graphical_quat_norm annotation(Placement(transformation(extent={{-15,-124},{15,-84}})));
  Real graphical_pitch_argument annotation(Placement(transformation(extent={{-15,-20},{15,20}})));
  Real graphical_pitch_argument_safe annotation(Placement(transformation(extent={{-15,-72},{15,-32}})));
  Real graphical_attitude_mea_from_quat[3]
    "Euler feedback reconstructed only from reordered QuatMea";
  Real graphical_attitude_ref[3]
    "Shared allocator convention: roll is opposite the graphical outer-loop roll output";
  Real graphical_collective_thrust_delta annotation(Placement(transformation(extent={{-15,32},{15,72}})));

  Real graphical_reference_position[3];
  Real graphical_reference_velocity[3];
  Real graphical_reference_acceleration[3];
  Real equation_reference_position[3];
  Real equation_reference_velocity[3];
  Real equation_reference_acceleration[3];
  Real graphical_position[3];
  Real equation_position[3];
  Real graphical_velocity_mea[3];
  Real equation_velocity_mea[3];
  Real equation_velocity_estimate[3];
  Real graphical_attitude[3];
  Real equation_attitude[3];
  Real graphical_body_rate_mea[3];
  Real equation_body_rate_mea[3];
  Real equation_quat_xyzw[4];
  Real equation_quat_wxyz[4];
  Real graphical_desired_acc[3];
  Real equation_desired_acc[3];
  Real graphical_attitude_command[3];
  Real equation_attitude_command[3];
  Real equation_collective_thrust_delta annotation(Placement(transformation(extent={{-15,84},{15,124}})));
  Real graphical_rotor_command[4];
  Real equation_rotor_command[4];

  Real delta_reference_position[3];
  Real delta_reference_velocity[3];
  Real delta_reference_acceleration[3];
  Real delta_position[3];
  Real delta_velocity_mea[3];
  Real delta_attitude[3];
  Real delta_body_rate_mea[3];
  Real delta_quat_wxyz[4];
  Real delta_desired_acc[3];
  Real delta_attitude_command[3];
  Real delta_collective_thrust_delta annotation(Placement(transformation(extent={{-15,136},{15,176}})));
  Real delta_rotor_command[4];
  Real quat_to_euler_error[3]
    "Separate quaternion-order check against the legacy AngleMea surface";
  Real graphical_quaternion_norm_error annotation(Placement(transformation(extent={{-15,-176},{15,-136}})));

equation
  connect(graphical_reference.position_command[1], graphical_outer.ref_px);
  connect(graphical_reference.position_command[2], graphical_outer.ref_py);
  connect(graphical_reference.position_command[3], graphical_outer.ref_pz);
  connect(graphical_reference.velocity_command[1], graphical_outer.ref_vx);
  connect(graphical_reference.velocity_command[2], graphical_outer.ref_vy);
  connect(graphical_reference.velocity_command[3], graphical_outer.ref_vz);
  connect(graphical_reference.acceleration_command[1], graphical_outer.ref_ax);
  connect(graphical_reference.acceleration_command[2], graphical_outer.ref_ay);
  connect(graphical_reference.acceleration_command[3], graphical_outer.ref_az);
  connect(ref_yaw_zero.y, graphical_outer.ref_yaw);

  connect(graphical_plant.position[1], graphical_outer.px);
  connect(graphical_plant.position[2], graphical_outer.py);
  connect(graphical_plant.position[3], graphical_outer.pz);
  connect(graphical_plant.VelMea[1], graphical_outer.vx);
  connect(graphical_plant.VelMea[2], graphical_outer.vy);
  connect(graphical_plant.VelMea[3], graphical_outer.vz);

  // Modelica to_Q exposes {x, y, z, w}; the graphical outer loop has only a
  // scalar yaw input, so this explicit reorder is its only quaternion boundary.
  graphical_quat_xyzw = graphical_plant.QuatMea;
  graphical_quat_wxyz = {graphical_quat_xyzw[4], graphical_quat_xyzw[1],
    graphical_quat_xyzw[2], graphical_quat_xyzw[3]};
  graphical_quat_norm = max(1e-12, sqrt(sum(graphical_quat_wxyz[i] ^ 2 for i in 1:4)));
  // The legacy AngleMea surface uses Modelica's {1,2,3} rotation sequence.
  // After the explicit order boundary above, use the matching XYZ extraction,
  // rather than the common ZYX roll-pitch-yaw convention.
  graphical_pitch_argument = 2 * (graphical_quat_wxyz[1] * graphical_quat_wxyz[3]
    + graphical_quat_wxyz[2] * graphical_quat_wxyz[4]) / graphical_quat_norm ^ 2;
  graphical_pitch_argument_safe = min(1 - quaternion_domain_margin,
    max(-1 + quaternion_domain_margin, graphical_pitch_argument));
  graphical_attitude_mea_from_quat[1] = atan2(2 * (graphical_quat_wxyz[1] * graphical_quat_wxyz[2]
    - graphical_quat_wxyz[3] * graphical_quat_wxyz[4]), graphical_quat_wxyz[1] ^ 2
    - graphical_quat_wxyz[2] ^ 2 - graphical_quat_wxyz[3] ^ 2 + graphical_quat_wxyz[4] ^ 2);
  graphical_attitude_mea_from_quat[2] = if graphical_pitch_argument >= 1 then Modelica.Constants.pi / 2 
    else if graphical_pitch_argument <= -1 then -Modelica.Constants.pi / 2 else asin(graphical_pitch_argument_safe);
  graphical_attitude_mea_from_quat[3] = atan2(2 * (graphical_quat_wxyz[1] * graphical_quat_wxyz[4]
    - graphical_quat_wxyz[2] * graphical_quat_wxyz[3]), graphical_quat_wxyz[1] ^ 2
    + graphical_quat_wxyz[2] ^ 2 - graphical_quat_wxyz[3] ^ 2 - graphical_quat_wxyz[4] ^ 2);
  graphical_quaternion_norm_error = graphical_quat_norm - 1;
  connect(yaw_mea_from_reordered_quat.y, graphical_outer.yaw_mea);

  connect(graphical_outer.desired_acc_x, graphical_output_capture[1].u);
  connect(graphical_outer.desired_acc_y, graphical_output_capture[2].u);
  connect(graphical_outer.desired_acc_z, graphical_output_capture[3].u);
  connect(graphical_outer.roll_cmd, graphical_output_capture[4].u);
  connect(graphical_outer.pitch_cmd, graphical_output_capture[5].u);
  connect(graphical_outer.yaw_cmd, graphical_output_capture[6].u);
  connect(graphical_outer.collective_thrust_n, graphical_output_capture[7].u);
  connect(graphical_outer.normalized_thrust, graphical_output_capture[8].u);
  graphical_attitude_ref = {-graphical_output_capture[4].y, graphical_output_capture[5].y,
    graphical_output_capture[6].y};
  graphical_collective_thrust_delta = graphical_output_capture[7].y - hover_collective_thrust_n;
  graphical_inner_allocator.attitude_ref = graphical_attitude_ref;
  graphical_inner_allocator.attitude_mea = graphical_attitude_mea_from_quat;
  connect(graphical_plant.BodyRateMea, graphical_inner_allocator.body_rate_mea);
  graphical_inner_allocator.collective_thrust_delta = graphical_collective_thrust_delta;
  connect(graphical_inner_allocator.rotor_command, graphical_plant.rotor_command);

  graphical_reference_position = graphical_reference.position_command;
  graphical_reference_velocity = graphical_reference.velocity_command;
  graphical_reference_acceleration = graphical_reference.acceleration_command;
  equation_reference_position = equation_formal.position_ref;
  equation_reference_velocity = equation_formal.reference.velocity_command;
  equation_reference_acceleration = equation_formal.reference.acceleration_command;
  graphical_position = graphical_plant.position;
  equation_position = equation_formal.position;
  graphical_velocity_mea = graphical_plant.VelMea;
  equation_velocity_mea = equation_formal.plant.VelMea;
  for i in 1:3 loop
    equation_velocity_estimate[i] = equation_formal.velocity_estimator[i].y;
  end for;
  graphical_attitude = graphical_attitude_mea_from_quat;
  equation_attitude = equation_formal.attitude;
  graphical_body_rate_mea = graphical_plant.BodyRateMea;
  equation_body_rate_mea = equation_formal.plant.BodyRateMea;
  equation_quat_xyzw = equation_formal.plant.QuatMea;
  equation_quat_wxyz = {equation_quat_xyzw[4], equation_quat_xyzw[1],
    equation_quat_xyzw[2], equation_quat_xyzw[3]};
  graphical_desired_acc = {graphical_output_capture[1].y, graphical_output_capture[2].y,
    graphical_output_capture[3].y};
  equation_desired_acc = {equation_formal.controller.core.desired_acc_x,
    equation_formal.controller.core.desired_acc_y, equation_formal.controller.core.desired_acc_z};
  graphical_attitude_command = graphical_attitude_ref;
  equation_attitude_command = equation_formal.controller.attitude_ref;
  equation_collective_thrust_delta = equation_formal.controller.collective_thrust_delta;
  graphical_rotor_command = graphical_plant.rotor_command;
  equation_rotor_command = equation_formal.rotor_command;

  delta_reference_position = graphical_reference_position - equation_reference_position;
  delta_reference_velocity = graphical_reference_velocity - equation_reference_velocity;
  delta_reference_acceleration = graphical_reference_acceleration - equation_reference_acceleration;
  delta_position = graphical_position - equation_position;
  delta_velocity_mea = graphical_velocity_mea - equation_velocity_mea;
  delta_attitude = graphical_attitude - equation_attitude;
  delta_body_rate_mea = graphical_body_rate_mea - equation_body_rate_mea;
  delta_quat_wxyz = graphical_quat_wxyz - equation_quat_wxyz;
  delta_desired_acc = graphical_desired_acc - equation_desired_acc;
  delta_attitude_command = graphical_attitude_command - equation_attitude_command;
  delta_collective_thrust_delta = graphical_collective_thrust_delta - equation_collective_thrust_delta;
  delta_rotor_command = graphical_rotor_command - equation_rotor_command;
  quat_to_euler_error = graphical_attitude_mea_from_quat - graphical_plant.attitude;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-250, -260}, {240, 150}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlGraphicalRealStateClosedLoopEquivalenceHarness;