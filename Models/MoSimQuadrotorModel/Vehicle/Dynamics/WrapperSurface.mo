within MoSimQuadrotorModel.Vehicle.Dynamics;
model WrapperSurface
  "Project-owned wrapper surface for the Sunray150 Rfly-style rotor dynamics core"
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real expected_yaw_direction[4] = profile.mworks_yaw_direction;
  parameter Real expected_rotor_center[4, 3] = profile.mworks_rotor_center_m;
  RotorActuatorCore dynamics(profile = profile);
  Real motor_command[4](each unit = "rad/s")
    "Signed MWORKS visual rotor speed command surface";
  Real commanded_thrust[4](each unit = "N")
    "Algebraic command-side Ct*omega_cmd^2 thrust for sign/order checks";
  Real commanded_yaw_reaction_moment[4](each unit = "N.m")
    "Command-side yaw reaction moment for sign/order checks";
  Real commanded_rotor_arm_moment[4, 3](each unit = "N.m")
    "Command-side rotor-center moment from r_cross_F plus yaw reaction moment";
  Real total_thrust(unit = "N")
    "Lagged dynamic wrapper total thrust";
  Real total_moment_body[3](each unit = "N.m")
    "Lagged dynamic wrapper body moment";
  Real commanded_total_thrust(unit = "N")
    "Command-side total thrust";
  Real commanded_total_moment_body[3](each unit = "N.m")
    "Command-side body moment";
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
  dynamics.motor_command = motor_command;

  for i in 1:4 loop
    commanded_thrust[i] = dynamics.thrust_effectiveness[i] * dynamics.lift_coefficient * motor_command[i] * motor_command[i];
    commanded_yaw_reaction_moment[i] = dynamics.yaw_direction[i] * dynamics.reaction_moment_effectiveness[i] * dynamics.moment_constant * commanded_thrust[i];
    commanded_rotor_arm_moment[i, 1] = dynamics.rotor_center[i, 2] * commanded_thrust[i];
    commanded_rotor_arm_moment[i, 2] = -dynamics.rotor_center[i, 1] * commanded_thrust[i];
    commanded_rotor_arm_moment[i, 3] = commanded_yaw_reaction_moment[i];
  end for;

  total_thrust = dynamics.total_thrust;
  total_moment_body = dynamics.total_moment_body;
  hover_thrust_error = dynamics.hover_thrust_error;
  commanded_total_thrust = sum(commanded_thrust);
  commanded_total_moment_body[1] = sum({commanded_rotor_arm_moment[i, 1] for i in 1:4});
  commanded_total_moment_body[2] = sum({commanded_rotor_arm_moment[i, 2] for i in 1:4});
  commanded_total_moment_body[3] = sum({commanded_rotor_arm_moment[i, 3] for i in 1:4});
  commanded_hover_thrust_error = commanded_total_thrust - dynamics.mass_kg * dynamics.gravity_mps2;
  yaw_moment_gate = total_moment_body[3];
  commanded_yaw_moment_gate = commanded_total_moment_body[3];
  minimum_thrust_effectiveness = dynamics.minimum_thrust_effectiveness;
  minimum_reaction_moment_effectiveness = dynamics.minimum_reaction_moment_effectiveness;
  motor_order_gate_error = sum({abs(dynamics.rotor_center[i, j] - expected_rotor_center[i, j]) for i in 1:4, j in 1:3});
  yaw_direction_gate_error = sum({abs(dynamics.yaw_direction[i] - expected_yaw_direction[i]) for i in 1:4});
  annotation(__MWORKS(hide=true,version="26.3.0"));
end WrapperSurface;
