within MoSimQuadrotorModel.Vehicle.Dynamics;
model PhysicalWrenchAdapter
  "Apply the project-owned Sunray150 wrapper force and torque to a MultiBody frame"
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real initial_rotor_speed[4] = {
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s,
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s};
  parameter Real lift_coefficient(unit = "N.s2/rad2") =
    profile.mworks_visual_thrust_coefficient;
  parameter Real reaction_moment_ratio = profile.moment_constant_ratio_m;
  parameter Real yaw_reaction_direction[4] = profile.mworks_yaw_direction;
  parameter Real thrust_effectiveness[4] = {1, 1, 1, 1};
  parameter Real reaction_moment_effectiveness[4] = {1, 1, 1, 1};
  parameter Real mass_scale(min = 0.01) = 1
    "Physical-body mass multiplier; controller profiles remain nominal";
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1}
    "Physical-body principal-inertia multipliers; controller profiles remain nominal";
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  inner Modelica.Mechanics.MultiBody.World world(
    final enableAnimation = false,
    final animateWorld = false,
    final animateGravity = false,
    final animateGround = false,
    final axisShowLabels = false,
    n = {0, 0, -1},
    gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity,
    g = profile.gravity_mps2);
  WrapperSurface wrapper(
    profile = profile,
    expected_yaw_direction = yaw_reaction_direction,
    dynamics(
      initial_rotor_speed = initial_rotor_speed,
      lift_coefficient = lift_coefficient,
      moment_constant = reaction_moment_ratio,
      yaw_direction = yaw_reaction_direction,
      thrust_effectiveness = thrust_effectiveness,
      reaction_moment_effectiveness = reaction_moment_effectiveness,
      mass_kg = profile.takeoff_mass_kg * mass_scale,
      fault_start_s = fault_start_s,
      fault_rotor_index = fault_rotor_index,
      fault_rotor_effectiveness = fault_rotor_effectiveness));
  Modelica.Mechanics.MultiBody.Parts.Body body(
    animation = false,
    r_CM = {0, 0, 0},
    m = wrapper.dynamics.mass_kg,
    I_11 = profile.body_inertia_diagonal_kg_m2[1] * inertia_scale[1],
    I_22 = profile.body_inertia_diagonal_kg_m2[2] * inertia_scale[2],
    I_33 = profile.body_inertia_diagonal_kg_m2[3] * inertia_scale[3],
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
  annotation(__MWORKS(hide=true,version="26.3.0"));
end PhysicalWrenchAdapter;
