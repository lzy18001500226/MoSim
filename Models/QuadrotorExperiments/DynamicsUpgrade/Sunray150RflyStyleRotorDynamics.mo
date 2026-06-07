within QuadrotorExperiments.DynamicsUpgrade;
model Sunray150RflyStyleRotorDynamics
  "Experimental Sunray150 rotor dynamics core: command lag, thrust, yaw reaction torque, and rotor-center moment"
  parameter Real mass_kg = 1.0
    "source=SDF_migration; not a measured Sunray150 takeoff mass";
  parameter Real lift_coefficient = 0.000854858
    "source=SDF_migration; Sunray motorConstant scaled by rotorVelocitySlowdownSim^2 for MWORKS visual rotor speed";
  parameter Real moment_constant = 0.06
    "source=SDF_migration; Gazebo/Sunray yaw moment ratio seed, not ULog identified";
  parameter Real time_constant_up = 0.0125
    "source=SDF_migration; Sunray SDF motor plugin timeConstantUp";
  parameter Real time_constant_down = 0.025
    "source=SDF_migration; Sunray SDF motor plugin timeConstantDown";
  parameter Real hover_motor_speed_cmd = sqrt(mass_kg * 9.81 / (4 * lift_coefficient))
    "MWORKS visual rotor hover speed seed; physical Sunray rotor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real rotor_center[4, 3] = [
    0.053745, -0.053740, -0.014052;
    0.053746,  0.053759, -0.014052;
   -0.053761,  0.053760, -0.014052;
   -0.053761, -0.053739, -0.014052]
    "source=user-reviewed DAE screw-pair fit, mapped to MWORKS Dronefixed1..4 order";
  parameter Real spin_command_sign[4] = {1, -1, 1, -1}
    "Existing MWORKS actuator command sign convention; requires PX4 motor-order validation before allocation claims";
  parameter Real yaw_direction[4] = {1, -1, 1, -1}
    "source=Sunray SDF turningDirection mapped to MWORKS Dronefixed1..4 order; positive is an experimental convention";
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
equation
  for i in 1:4 loop
    motor_tau[i] = if abs(motor_command[i]) > abs(omega[i]) then time_constant_up else time_constant_down;
    der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i];
    thrust[i] = lift_coefficient * omega[i] * omega[i];
    yaw_reaction_moment[i] = yaw_direction[i] * moment_constant * thrust[i];
    rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i];
    rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i];
    rotor_arm_moment[i, 3] = yaw_reaction_moment[i];
  end for;
  total_thrust = sum(thrust);
  total_moment_body[1] = sum({rotor_arm_moment[i, 1] for i in 1:4});
  total_moment_body[2] = sum({rotor_arm_moment[i, 2] for i in 1:4});
  total_moment_body[3] = sum({rotor_arm_moment[i, 3] for i in 1:4});
  hover_thrust_error = total_thrust - mass_kg * 9.81;
  annotation(__MWORKS(hide=true));
end Sunray150RflyStyleRotorDynamics;
