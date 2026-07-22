within MoSimQuadrotorModel.Dynamics;
model ActuatorMappedWrapperSurface
  "Wrapper surface from normalized actuator command to existing rotor dynamics core"
  parameter Real mass_kg = 1.0
    "source=SDF_migration seed shared with mapper/core for static boundary consistency";
  parameter Real lift_coefficient = 0.000854858
    "source=SDF_migration visual-speed thrust coefficient seed; not ULog identified";
  parameter Real normalized_command_min = 0.0
    "source=interface_seed; lower normalized actuator command bound";
  parameter Real normalized_command_max = 1.0
    "source=interface_seed; upper normalized actuator command bound";
  parameter Real hover_normalized_command = 0.5
    "source=interface_seed; hover command placeholder, not measured PWM/throttle evidence";
  parameter Real min_visual_rotor_speed = 0.0
    "source=interface_seed; zero command visual rotor speed seed";
  parameter Real max_visual_rotor_speed = sqrt(mass_kg * 9.81 / (4 * lift_coefficient)) / hover_normalized_command
    "source=interface_seed derived from hover_normalized_command; not identified max speed";
  parameter Real spin_command_sign[4] = {1, -1, 1, -1}
    "Existing MWORKS signed visual speed convention; not PX4 allocation proof";
  ActuatorCommandMapper actuator_mapper(
    mass_kg = mass_kg,
    lift_coefficient = lift_coefficient,
    normalized_command_min = normalized_command_min,
    normalized_command_max = normalized_command_max,
    hover_normalized_command = hover_normalized_command,
    min_visual_rotor_speed = min_visual_rotor_speed,
    max_visual_rotor_speed = max_visual_rotor_speed,
    spin_command_sign = spin_command_sign);
  WrapperSurface wrapper(
    dynamics(
      mass_kg = mass_kg,
      lift_coefficient = lift_coefficient,
      spin_command_sign = spin_command_sign));
  input Real normalized_actuator_command[4]
    "External normalized actuator/throttle command input surface";
  Real saturated_normalized_command[4]
    "Mapper bounded normalized command";
  Real actuator_saturation_error[4]
    "Mapper saturation residual";
  Real signed_visual_rotor_speed_command[4](each unit = "rad/s")
    "Mapper output feeding wrapper.motor_command";
  Real total_thrust(unit = "N")
    "Lagged total thrust from unchanged rotor dynamics chain";
  Real total_moment_body[3](each unit = "N.m")
    "Lagged body moment from unchanged rotor dynamics chain";
  Real commanded_total_thrust(unit = "N")
    "Command-side total thrust after mapper and before motor lag";
  Real commanded_total_moment_body[3](each unit = "N.m")
    "Command-side body moment after mapper and before motor lag";
  Real hover_thrust_error(unit = "N");
  Real commanded_hover_thrust_error(unit = "N");
  Real yaw_moment_gate(unit = "N.m");
  Real commanded_yaw_moment_gate(unit = "N.m");
  Real minimum_thrust_effectiveness
    "Forwarded minimum per-rotor thrust effectiveness";
  Real minimum_reaction_moment_effectiveness
    "Forwarded minimum per-rotor yaw reaction moment effectiveness";
  Real motor_order_gate_error;
  Real yaw_direction_gate_error;
equation
  actuator_mapper.normalized_command = normalized_actuator_command;
  wrapper.motor_command = actuator_mapper.signed_visual_rotor_speed_command;

  saturated_normalized_command = actuator_mapper.saturated_normalized_command;
  actuator_saturation_error = actuator_mapper.actuator_saturation_error;
  signed_visual_rotor_speed_command = actuator_mapper.signed_visual_rotor_speed_command;

  total_thrust = wrapper.total_thrust;
  total_moment_body = wrapper.total_moment_body;
  commanded_total_thrust = wrapper.commanded_total_thrust;
  commanded_total_moment_body = wrapper.commanded_total_moment_body;
  hover_thrust_error = wrapper.hover_thrust_error;
  commanded_hover_thrust_error = wrapper.commanded_hover_thrust_error;
  yaw_moment_gate = wrapper.yaw_moment_gate;
  commanded_yaw_moment_gate = wrapper.commanded_yaw_moment_gate;
  minimum_thrust_effectiveness = wrapper.minimum_thrust_effectiveness;
  minimum_reaction_moment_effectiveness = wrapper.minimum_reaction_moment_effectiveness;
  motor_order_gate_error = wrapper.motor_order_gate_error;
  yaw_direction_gate_error = wrapper.yaw_direction_gate_error;
  annotation(__MWORKS(hide=true));
end ActuatorMappedWrapperSurface;