within MoSimQuadrotorModel.Control.Adapters;
model OfficialPIDYawCorrectedRotorAdapter
  "Diagnostic translation of the embedded Official PID at the signed ROTOR_COMMAND boundary"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  parameter Real legacy_hover_speed = 13.985413115099604;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / legacy_hover_speed;
  parameter Real embedded_yaw_authority_reference_ratio = 0.016
    "Adapter-only reference for the embedded mixer; the physical plant remains at profile.moment_constant_ratio_m";
  parameter Real yaw_authority_scale =
    embedded_yaw_authority_reference_ratio / profile.moment_constant_ratio_m;
  parameter Real yaw_pattern[4] = {
    -profile.mworks_yaw_direction[1],
    -profile.mworks_yaw_direction[2],
    -profile.mworks_yaw_direction[3],
    -profile.mworks_yaw_direction[4]}
    "Matches Sunray150Assembly aerodynamic yaw-reaction direction";
  parameter Real maximum_rotor_speed = profile.mworks_max_visual_rotor_speed_rad_s;
  MoSimQuadrotorModel.Vehicle.Blocks.Controller.Controller core;
  Real amplitude_command[4]
    "Core outputs mapped to unsigned rotor amplitudes before yaw translation";
  Real yaw_amplitude
    "Embedded Official PID yaw projection onto the physical yaw-reaction pattern";
  Real non_yaw_amplitude[4]
    "Collective, roll, and pitch contribution preserved from the embedded mixer";
  Real unclamped_rotor_command[4]
    "Signed command before the physical visual-speed limit";
  Real command_limit_residual[4]
    "Amount removed by the signed visual-speed limit";
  annotation(__MWORKS(version="26.3.0"));
equation
  connect(position_ref, core.position_command);
  connect(position_mea, core.position);
  connect(attitude_mea, core.angle);

  amplitude_command[1] = core.y;
  amplitude_command[2] = -core.y1;
  amplitude_command[3] = core.y2;
  amplitude_command[4] = -core.y3;
  yaw_amplitude = sum({yaw_pattern[i] * amplitude_command[i] for i in 1:4}) / 4;

  for i in 1:4 loop
    non_yaw_amplitude[i] = amplitude_command[i] - yaw_pattern[i] * yaw_amplitude;
    unclamped_rotor_command[i] = profile.mworks_spin_command_sign[i]
      * (hover_speed + command_scale * (non_yaw_amplitude[i]
        + yaw_pattern[i] * yaw_authority_scale * yaw_amplitude));
    rotor_command[i] = min(max(unclamped_rotor_command[i], -maximum_rotor_speed), maximum_rotor_speed);
    command_limit_residual[i] = unclamped_rotor_command[i] - rotor_command[i];
  end for;
end OfficialPIDYawCorrectedRotorAdapter;