within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model Px4CtrlFormalRunnerTransitionHarness
  "Full pre/post comparison: graphical formal base versus the preserved EquationBridge baseline"

  // MWORKS compiler 3823 rejects an extends-only alias as a nested component.
  // Px4CtrlFormalRunner is statically verified as a no-modifier extends alias
  // of this exact class and is simulated separately by the evidence runner.
  MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlGraphicalRealStateFormalRunner graphical_formal 
    annotation(Placement(transformation(origin = {155, 75}, extent = {{-55, -55}, {55, 55}})));
  MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlEquationBridgeFormalRunner equation_formal 
    annotation(Placement(transformation(origin = {155, -145}, extent = {{-55, -55}, {55, 55}})));

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
  Real graphical_quat_xyzw[4];
  Real graphical_quat_wxyz[4];
  Real equation_quat_xyzw[4];
  Real equation_quat_wxyz[4];
  Real graphical_desired_acc[3];
  Real equation_desired_acc[3];
  Real graphical_attitude_command[3];
  Real equation_attitude_command[3];
  Real graphical_collective_thrust_delta;
  Real equation_collective_thrust_delta;
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
  Real delta_collective_thrust_delta;
  Real delta_rotor_command[4];
  Real quat_to_euler_error[3];
  Real graphical_quaternion_norm_error;

equation
  graphical_reference_position = graphical_formal.position_ref;
  graphical_reference_velocity = graphical_formal.velocity_ref;
  graphical_reference_acceleration = graphical_formal.acceleration_ref;
  equation_reference_position = equation_formal.position_ref;
  equation_reference_velocity = equation_formal.reference.velocity_command;
  equation_reference_acceleration = equation_formal.reference.acceleration_command;

  graphical_position = graphical_formal.position;
  equation_position = equation_formal.position;
  graphical_velocity_mea = graphical_formal.velocity_mea;
  equation_velocity_mea = equation_formal.plant.VelMea;
  for i in 1:3 loop
    equation_velocity_estimate[i] = equation_formal.velocity_estimator[i].y;
  end for;
  graphical_attitude = graphical_formal.attitude;
  equation_attitude = equation_formal.attitude;
  graphical_body_rate_mea = graphical_formal.body_rate_mea;
  equation_body_rate_mea = equation_formal.plant.BodyRateMea;
  graphical_quat_xyzw = graphical_formal.quat_xyzw;
  graphical_quat_wxyz = graphical_formal.quat_wxyz;
  equation_quat_xyzw = equation_formal.plant.QuatMea;
  equation_quat_wxyz = {equation_quat_xyzw[4], equation_quat_xyzw[1],
    equation_quat_xyzw[2], equation_quat_xyzw[3]};
  graphical_desired_acc = graphical_formal.desired_acc;
  equation_desired_acc = {equation_formal.controller.core.desired_acc_x,
    equation_formal.controller.core.desired_acc_y, equation_formal.controller.core.desired_acc_z};
  graphical_attitude_command = graphical_formal.attitude_ref;
  equation_attitude_command = equation_formal.controller.attitude_ref;
  graphical_collective_thrust_delta = graphical_formal.collective_thrust_delta;
  equation_collective_thrust_delta = equation_formal.controller.collective_thrust_delta;
  graphical_rotor_command = graphical_formal.rotor_command;
  equation_rotor_command = equation_formal.rotor_command;
  quat_to_euler_error = graphical_formal.quat_to_euler_error;
  graphical_quaternion_norm_error = graphical_formal.quaternion_norm_error;

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

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-250, -230}, {240, 150}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlFormalRunnerTransitionHarness;