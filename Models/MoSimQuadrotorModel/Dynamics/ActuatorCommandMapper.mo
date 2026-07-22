within MoSimQuadrotorModel.Dynamics;
model ActuatorCommandMapper
  "Map normalized actuator command to signed MWORKS visual rotor speed"
  parameter Real mass_kg = 1.0
    "source=SDF_migration seed used only to derive hover visual speed; not identified truth";
  parameter Real lift_coefficient = 0.000854858
    "source=SDF_migration visual-speed thrust coefficient seed; not ULog identified";
  parameter Real normalized_command_min = 0.0
    "source=interface_seed; lower bound for normalized actuator/throttle command";
  parameter Real normalized_command_max = 1.0
    "source=interface_seed; upper bound for normalized actuator/throttle command";
  parameter Real hover_normalized_command = 0.5
    "source=interface_seed; placeholder until real actuator command/RPM evidence exists";
  parameter Real min_visual_rotor_speed = 0.0
    "source=interface_seed; zero normalized command maps to stopped visual rotor";
  parameter Real hover_visual_rotor_speed = sqrt(mass_kg * 9.81 / (4 * lift_coefficient))
    "Derived MWORKS visual rotor hover-speed seed, not physical RPM truth";
  parameter Real max_visual_rotor_speed = hover_visual_rotor_speed / hover_normalized_command
    "source=interface_seed derived from hover_normalized_command; not identified max speed";
  parameter Real spin_command_sign[4] = {1, -1, 1, -1}
    "Existing MWORKS signed visual speed convention; not PX4 allocation proof";
  input Real normalized_command[4]
    "Normalized actuator/throttle command surface, expected in [0, 1]";
  Real saturated_normalized_command[4]
    "Bounded normalized actuator command";
  Real actuator_saturation_error[4]
    "normalized_command minus saturated_normalized_command";
  Real visual_rotor_speed_unsigned[4](each unit = "rad/s")
    "Unsigned MWORKS visual rotor speed target";
  Real signed_visual_rotor_speed_command[4](each unit = "rad/s")
    "Signed visual rotor speed command for RotorActuatorCore.motor_command";
  Real hover_command_error[4]
    "saturated command minus hover_normalized_command";
equation
  for i in 1:4 loop
    saturated_normalized_command[i] =
      if normalized_command[i] < normalized_command_min then normalized_command_min
      else if normalized_command[i] > normalized_command_max then normalized_command_max
      else normalized_command[i];
    actuator_saturation_error[i] = normalized_command[i] - saturated_normalized_command[i];
    visual_rotor_speed_unsigned[i] =
      min_visual_rotor_speed
      + (saturated_normalized_command[i] - normalized_command_min)
        * (max_visual_rotor_speed - min_visual_rotor_speed)
        / (normalized_command_max - normalized_command_min);
    signed_visual_rotor_speed_command[i] =
      spin_command_sign[i] * visual_rotor_speed_unsigned[i];
    hover_command_error[i] =
      saturated_normalized_command[i] - hover_normalized_command;
  end for;
  annotation(__MWORKS(hide=true));
end ActuatorCommandMapper;