within MoSimQuadrotorModel.Vehicle.Dynamics;
model RotorActuatorCore
  "Experimental Sunray150 rotor dynamics core: command lag, thrust, yaw reaction torque, and rotor-center moment"
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile
    "Source-labeled virtual plant profile; not identified real-aircraft truth";
  parameter Real mass_kg = profile.takeoff_mass_kg;
  parameter Real gravity_mps2 = profile.gravity_mps2;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real moment_constant = profile.moment_constant_ratio_m;
  parameter Real time_constant_up = profile.motor_time_constant_up_s;
  parameter Real time_constant_down = profile.motor_time_constant_down_s;
  parameter Real hover_motor_speed_cmd = sqrt(mass_kg * gravity_mps2 / (4 * lift_coefficient));
  parameter Real initial_rotor_speed[4] = {
    hover_motor_speed_cmd,
    -hover_motor_speed_cmd,
    hover_motor_speed_cmd,
    -hover_motor_speed_cmd};
  parameter Real rotor_center[4, 3] = profile.mworks_rotor_center_m;
  parameter Real spin_command_sign[4] = profile.mworks_spin_command_sign;
  parameter Real yaw_direction[4] = profile.mworks_yaw_direction;
  parameter Real thrust_effectiveness[4] = {1, 1, 1, 1}
    "Per-rotor thrust effectiveness for degradation/fault studies; default preserves nominal dynamics";
  parameter Real reaction_moment_effectiveness[4] = {1, 1, 1, 1}
    "Per-rotor yaw reaction moment effectiveness; default preserves nominal dynamics";
  parameter Real fault_start_s(unit = "s") = 1e9
    "Fault start time; the default is outside formal experiment horizons";
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1
    "One-based rotor index affected by the scheduled fault";
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1
    "Additional scheduled rotor multiplier after fault_start_s";
  Real motor_command[4](each unit = "rad/s")
    "Signed visual rotor speed command";
  Real omega[4](start = initial_rotor_speed, each unit = "rad/s")
    "Lagged signed visual rotor speed";
  Real motor_tau[4](each unit = "s");
  Real thrust[4](each unit = "N")
    "Per-rotor thrust Ct * omega^2";
  Real yaw_reaction_moment[4](each unit = "N.m")
    "Per-rotor reaction yaw moment Cm * thrust";
  Real nominal_thrust[4](each unit = "N")
    "Unscaled Ct * omega^2 thrust before static effectiveness and scheduled fault";
  Real fault_effectiveness[4]
    "Time-varying multiplier; only the selected rotor changes after fault_start_s";
  Real rotor_arm_moment[4, 3](each unit = "N.m")
    "Per-rotor moment from r_cross_F plus yaw reaction moment";
  Real total_thrust(unit = "N");
  Real total_moment_body[3](each unit = "N.m");
  Real hover_thrust_error(unit = "N");
  Real thrust_effectiveness_loss[4]
    "Per-rotor thrust loss ratio from nominal effectiveness";
  Real reaction_moment_effectiveness_loss[4]
    "Per-rotor yaw reaction moment loss ratio from nominal effectiveness";
  Real minimum_thrust_effectiveness
    "Minimum thrust effectiveness across rotors";
  Real minimum_reaction_moment_effectiveness
    "Minimum reaction moment effectiveness across rotors";
equation
  for i in 1:4 loop
    motor_tau[i] = if abs(motor_command[i]) > abs(omega[i]) then time_constant_up else time_constant_down;
    der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i];
    nominal_thrust[i] = lift_coefficient * omega[i] * omega[i];
    fault_effectiveness[i] = if i == fault_rotor_index and time >= fault_start_s then
      fault_rotor_effectiveness else 1;
    thrust[i] = fault_effectiveness[i] * thrust_effectiveness[i] * nominal_thrust[i];
    // Static effectiveness retains its historical meaning. The scheduled fault
    // multiplies the rotor's thrust and reaction torque once, rather than twice.
    yaw_reaction_moment[i] = fault_effectiveness[i] * yaw_direction[i]
      * reaction_moment_effectiveness[i] * moment_constant
      * thrust_effectiveness[i] * nominal_thrust[i];
    rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i];
    rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i];
    rotor_arm_moment[i, 3] = yaw_reaction_moment[i];
    thrust_effectiveness_loss[i] = 1 - fault_effectiveness[i] * thrust_effectiveness[i];
    reaction_moment_effectiveness_loss[i] = 1 - fault_effectiveness[i]
      * reaction_moment_effectiveness[i];
  end for;
  total_thrust = sum(thrust);
  total_moment_body[1] = sum({rotor_arm_moment[i, 1] for i in 1:4});
  total_moment_body[2] = sum({rotor_arm_moment[i, 2] for i in 1:4});
  total_moment_body[3] = sum({rotor_arm_moment[i, 3] for i in 1:4});
  hover_thrust_error = total_thrust - mass_kg * gravity_mps2;
  minimum_thrust_effectiveness = min({fault_effectiveness[i] * thrust_effectiveness[i] for i in 1:4});
  minimum_reaction_moment_effectiveness = min({fault_effectiveness[i]
    * reaction_moment_effectiveness[i] for i in 1:4});
  annotation(__MWORKS(hide=true,version="26.3.0"));
end RotorActuatorCore;
