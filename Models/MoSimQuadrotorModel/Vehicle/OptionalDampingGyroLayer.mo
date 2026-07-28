within MoSimQuadrotorModel.Vehicle;
model OptionalDampingGyroLayer
  "Optional source-labeled rotor gyro, body drag, and angular damping layer"
  parameter Boolean enable_rotor_gyro = false
    "Default disabled; rotor gyro moment is not identified Sunray150 truth";
  parameter Boolean enable_body_drag = false
    "Default disabled; translational body drag coefficients are not identified";
  parameter Boolean enable_angular_damping = false
    "Default disabled; angular damping coefficients are not identified";
  parameter Real rotor_polar_inertia[4](each unit = "kg.m2") = {0, 0, 0, 0}
    "source=zero_seed; optional rotor inertia placeholder, not ULog/bench identified";
  parameter Real gyro_axis_sign[4] = {1, -1, 1, -1}
    "source=sign_convention_seed; follows current MWORKS visual spin convention until motor-order validation";
  parameter Real gyro_convention_sign = -1
    "source=interface_seed; sign for body-rate cross rotor-angular-momentum convention";
  parameter Real body_drag_coefficient[3](each unit = "N.s/m") = {0, 0, 0}
    "source=zero_seed; body-frame linear drag coefficients, not identified";
  parameter Real angular_damping_coefficient[3](each unit = "N.m.s/rad") = {0, 0, 0}
    "source=zero_seed; body angular-rate damping coefficients, not identified";
  ActuatorMappedWrapperSurface mapped_wrapper;
  input Real normalized_actuator_command[4]
    "External normalized actuator/throttle command input surface";
  input Real body_velocity_body[3](each unit = "m/s")
    "Body-frame translational velocity input for optional drag only";
  input Real body_angular_velocity_body[3](each unit = "rad/s")
    "Body-frame angular-rate input for optional gyro and damping only";
  Real saturated_normalized_command[4]
    "Mapper bounded normalized command";
  Real actuator_saturation_error[4]
    "Mapper saturation residual";
  Real signed_visual_rotor_speed_command[4](each unit = "rad/s")
    "Mapper output feeding the unchanged rotor dynamics chain";
  Real base_force_body[3](each unit = "N")
    "Unchanged mapped-wrapper force boundary before optional drag";
  Real base_moment_body[3](each unit = "N.m")
    "Unchanged mapped-wrapper moment before optional gyro/damping";
  Real rotor_angular_momentum_body_z[4](each unit = "kg.m2/s")
    "Optional rotor angular momentum around body z";
  Real rotor_gyro_moment_body[4, 3](each unit = "N.m")
    "Optional per-rotor gyroscopic moment contribution";
  Real rotor_gyro_total_moment_body[3](each unit = "N.m")
    "Optional total rotor gyroscopic moment";
  Real body_drag_force_body[3](each unit = "N")
    "Optional body-frame translational drag force";
  Real angular_damping_moment_body[3](each unit = "N.m")
    "Optional body-frame angular damping moment";
  Real optional_force_body[3](each unit = "N")
    "Optional force contribution; zero by default";
  Real optional_moment_body[3](each unit = "N.m")
    "Optional moment contribution; zero by default";
  Real total_force_body[3](each unit = "N")
    "Base wrapper force plus optional drag force";
  Real total_moment_body[3](each unit = "N.m")
    "Base wrapper moment plus optional gyro and damping moments";
  Real base_total_thrust(unit = "N")
    "Lagged total thrust from the unchanged mapped-wrapper/core chain";
  Real commanded_total_thrust(unit = "N")
    "Command-side total thrust after mapper and before motor lag";
  Real commanded_total_moment_body[3](each unit = "N.m")
    "Command-side body moment after mapper and before motor lag";
  Real hover_thrust_error(unit = "N");
  Real commanded_hover_thrust_error(unit = "N");
  Real yaw_moment_gate(unit = "N.m");
  Real commanded_yaw_moment_gate(unit = "N.m");
  Real optional_force_norm(unit = "N")
    "Magnitude proxy for optional force terms";
  Real optional_moment_norm(unit = "N.m")
    "Magnitude proxy for optional moment terms";
  Real default_disabled_force_delta(unit = "N")
    "Zero when optional force terms preserve the base force";
  Real default_disabled_moment_delta(unit = "N.m")
    "Zero when optional moment terms preserve the base moment";
  Real motor_order_gate_error;
  Real yaw_direction_gate_error;
equation
  mapped_wrapper.normalized_actuator_command = normalized_actuator_command;

  saturated_normalized_command = mapped_wrapper.saturated_normalized_command;
  actuator_saturation_error = mapped_wrapper.actuator_saturation_error;
  signed_visual_rotor_speed_command = mapped_wrapper.signed_visual_rotor_speed_command;

  base_force_body = {0, 0, mapped_wrapper.total_thrust};
  base_moment_body = mapped_wrapper.total_moment_body;

  for i in 1:4 loop
    rotor_angular_momentum_body_z[i] =
      if enable_rotor_gyro then
        rotor_polar_inertia[i] * gyro_axis_sign[i] * mapped_wrapper.wrapper.dynamics.omega[i]
      else 0;
    rotor_gyro_moment_body[i, 1] =
      if enable_rotor_gyro then
        gyro_convention_sign * body_angular_velocity_body[2] * rotor_angular_momentum_body_z[i]
      else 0;
    rotor_gyro_moment_body[i, 2] =
      if enable_rotor_gyro then
        -gyro_convention_sign * body_angular_velocity_body[1] * rotor_angular_momentum_body_z[i]
      else 0;
    rotor_gyro_moment_body[i, 3] = 0;
  end for;

  for j in 1:3 loop
    rotor_gyro_total_moment_body[j] = sum({rotor_gyro_moment_body[i, j] for i in 1:4});
    body_drag_force_body[j] =
      if enable_body_drag then
        -body_drag_coefficient[j] * body_velocity_body[j]
      else 0;
    angular_damping_moment_body[j] =
      if enable_angular_damping then
        -angular_damping_coefficient[j] * body_angular_velocity_body[j]
      else 0;
    optional_force_body[j] = body_drag_force_body[j];
    optional_moment_body[j] = rotor_gyro_total_moment_body[j] + angular_damping_moment_body[j];
    total_force_body[j] = base_force_body[j] + optional_force_body[j];
    total_moment_body[j] = base_moment_body[j] + optional_moment_body[j];
  end for;

  base_total_thrust = mapped_wrapper.total_thrust;
  commanded_total_thrust = mapped_wrapper.commanded_total_thrust;
  commanded_total_moment_body = mapped_wrapper.commanded_total_moment_body;
  hover_thrust_error = mapped_wrapper.hover_thrust_error;
  commanded_hover_thrust_error = mapped_wrapper.commanded_hover_thrust_error;
  yaw_moment_gate = mapped_wrapper.yaw_moment_gate;
  commanded_yaw_moment_gate = mapped_wrapper.commanded_yaw_moment_gate;
  optional_force_norm = abs(optional_force_body[1]) + abs(optional_force_body[2]) + abs(optional_force_body[3]);
  optional_moment_norm = abs(optional_moment_body[1]) + abs(optional_moment_body[2]) + abs(optional_moment_body[3]);
  default_disabled_force_delta =
    abs(total_force_body[1] - base_force_body[1])
    + abs(total_force_body[2] - base_force_body[2])
    + abs(total_force_body[3] - base_force_body[3]);
  default_disabled_moment_delta =
    abs(total_moment_body[1] - base_moment_body[1])
    + abs(total_moment_body[2] - base_moment_body[2])
    + abs(total_moment_body[3] - base_moment_body[3]);
  motor_order_gate_error = mapped_wrapper.motor_order_gate_error;
  yaw_direction_gate_error = mapped_wrapper.yaw_direction_gate_error;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end OptionalDampingGyroLayer;
