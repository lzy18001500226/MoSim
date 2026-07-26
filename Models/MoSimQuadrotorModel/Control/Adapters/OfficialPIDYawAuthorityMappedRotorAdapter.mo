within MoSimQuadrotorModel.Control.Adapters;
model OfficialPIDYawAuthorityMappedRotorAdapter
  "Diagnostic Official PID adapter with calibrated yaw authority for the shared physical plant"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  parameter Real legacy_hover_speed = 13.985413115099604;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / legacy_hover_speed;
  parameter Real legacy_effective_yaw_reaction_ratio = 0.016
    "Diagnostic legacy yaw authority; the physical plant remains at profile.moment_constant_ratio_m";
  parameter Real yaw_authority_scale =
    legacy_effective_yaw_reaction_ratio / profile.moment_constant_ratio_m;
  parameter Real yaw_pattern[4] = {
    -profile.mworks_yaw_direction[1],
    -profile.mworks_yaw_direction[2],
    -profile.mworks_yaw_direction[3],
    -profile.mworks_yaw_direction[4]}
    "Matches Sunray150Assembly aerodynamic yaw-reaction direction";
  MoSimQuadrotorModel.Vehicle.Blocks.Controller.Controller core;
  Real amplitude_command[4]
    "Embedded controller outputs converted to unsigned rotor-speed amplitudes";
  Real yaw_amplitude
    "Projection of the embedded mixer output onto the physical yaw-reaction pattern";
  Real non_yaw_amplitude[4]
    "Collective, roll, and pitch components retained from the embedded mixer";
  Real mapped_amplitude[4]
    "Legacy yaw channel mapped to the shared physical yaw authority";
  Real mapped_collective_amplitude_error
    "Linear collective preservation check; zero means the map did not alter total amplitude";
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
    mapped_amplitude[i] = non_yaw_amplitude[i]
      + yaw_pattern[i] * yaw_authority_scale * yaw_amplitude;
    rotor_command[i] = profile.mworks_spin_command_sign[i]
      * (hover_speed + command_scale * mapped_amplitude[i]);
  end for;
  mapped_collective_amplitude_error = sum(mapped_amplitude) - sum(amplitude_command);
end OfficialPIDYawAuthorityMappedRotorAdapter;
