within QuadrotorExperiments.DynamicsUpgrade;
model Sunray150PhysicalWrenchFrameAdapter
  "Apply the project-owned Sunray150 wrapper force and torque to a MultiBody frame"
  inner Modelica.Mechanics.MultiBody.World world(
    final enableAnimation = false,
    final animateWorld = false,
    final animateGravity = false,
    final animateGround = false,
    final axisShowLabels = false,
    n = {0, 0, -1},
    gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity,
    g = 9.81);
  Sunray150DynamicsWrapperSurface wrapper;
  Modelica.Mechanics.MultiBody.Parts.Body body(
    animation = false,
    r_CM = {0, 0, 0},
    m = wrapper.dynamics.mass_kg,
    I_11 = 0.0085,
    I_22 = 0.0085,
    I_33 = 0.012,
    I_21 = 0,
    I_31 = 0,
    I_32 = 0,
    r_0(start = {0, 0, 0}, fixed = {true, true, true}),
    v_0(start = {0, 0, 0}, fixed = {true, true, true}),
    angles_fixed = true,
    angles_start = {0, 0, 0},
    w_0_fixed = true,
    w_0_start = {0, 0, 0},
    enforceStates = true);
  Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque forceAndTorque(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b,
    animation = false);
  Real applied_force_body[3](each unit = "N");
  Real applied_torque_body[3](each unit = "N.m");
  Real applied_force_z_body(unit = "N");
  Real applied_yaw_torque_body(unit = "N.m");
  Real force_application_error(unit = "N");
  Real torque_application_error(unit = "N.m");
  Real hover_weight_balance_error(unit = "N");
  Real wrapper_total_thrust(unit = "N");
  Real wrapper_yaw_moment(unit = "N.m");
  Real motor_order_gate_error;
  Real yaw_direction_gate_error;
equation
  applied_force_body = {0, 0, wrapper.total_thrust};
  applied_torque_body = wrapper.total_moment_body;
  forceAndTorque.force = applied_force_body;
  forceAndTorque.torque = applied_torque_body;
  connect(forceAndTorque.frame_b, body.frame_a);

  applied_force_z_body = applied_force_body[3];
  applied_yaw_torque_body = applied_torque_body[3];
  wrapper_total_thrust = wrapper.total_thrust;
  wrapper_yaw_moment = wrapper.total_moment_body[3];
  force_application_error = abs(body.frame_a.f[3] - applied_force_z_body);
  torque_application_error = abs(body.frame_a.t[3] - applied_yaw_torque_body);
  hover_weight_balance_error = wrapper.total_thrust - wrapper.dynamics.mass_kg * world.g;
  motor_order_gate_error = wrapper.motor_order_gate_error;
  yaw_direction_gate_error = wrapper.yaw_direction_gate_error;
  annotation(__MWORKS(hide=true));
end Sunray150PhysicalWrenchFrameAdapter;
