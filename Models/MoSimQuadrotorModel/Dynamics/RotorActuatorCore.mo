within MoSimQuadrotorModel.Dynamics;
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
  parameter Real rotor_center[4, 3] = profile.mworks_rotor_center_m;
  parameter Real spin_command_sign[4] = profile.mworks_spin_command_sign;
  parameter Real yaw_direction[4] = profile.mworks_yaw_direction;
  parameter Real thrust_effectiveness[4] = {1, 1, 1, 1}
    "Per-rotor thrust effectiveness for degradation/fault studies; default preserves nominal dynamics";
  parameter Real reaction_moment_effectiveness[4] = {1, 1, 1, 1}
    "Per-rotor yaw reaction moment effectiveness; default preserves nominal dynamics";
  Real motor_command[4](each unit = "rad/s")
    "Signed visual rotor speed command";
  Real omega[4](start = {hover_motor_speed_cmd, -hover_motor_speed_cmd, hover_motor_speed_cmd, -hover_motor_speed_cmd}, each unit = "rad/s")
    "Lagged signed visual rotor speed";
  Real motor_tau[4](each unit = "s");
  Real thrust[4](each unit = "N")
    "Per-rotor thrust Ct * omega^2";
  Real yaw_reaction_moment[4](each unit = "N.m")
    "Per-rotor reaction yaw moment Cm * thrust";
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
    thrust[i] = thrust_effectiveness[i] * lift_coefficient * omega[i] * omega[i];
    yaw_reaction_moment[i] = yaw_direction[i] * reaction_moment_effectiveness[i] * moment_constant * thrust[i];
    rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i];
    rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i];
    rotor_arm_moment[i, 3] = yaw_reaction_moment[i];
    thrust_effectiveness_loss[i] = 1 - thrust_effectiveness[i];
    reaction_moment_effectiveness_loss[i] = 1 - reaction_moment_effectiveness[i];
  end for;
  total_thrust = sum(thrust);
  total_moment_body[1] = sum({rotor_arm_moment[i, 1] for i in 1:4});
  total_moment_body[2] = sum({rotor_arm_moment[i, 2] for i in 1:4});
  total_moment_body[3] = sum({rotor_arm_moment[i, 3] for i in 1:4});
  hover_thrust_error = total_thrust - mass_kg * gravity_mps2;
  minimum_thrust_effectiveness = min(thrust_effectiveness);
  minimum_reaction_moment_effectiveness = min(reaction_moment_effectiveness);
  annotation(__MWORKS(hide=true,version="26.3.0"));
end RotorActuatorCore;
