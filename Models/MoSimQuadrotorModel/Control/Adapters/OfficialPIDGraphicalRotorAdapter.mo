within MoSimQuadrotorModel.Control.Adapters;
model OfficialPIDGraphicalRotorAdapter
  "Strict graphical Official PID boundary with explicit rotor signs"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  extends ModelWorkspace;
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

  MoSimQuadrotorModel.Control.Implementations.Graphical.PID.OfficialPidCoreSysblock core 
    annotation(Placement(transformation(origin = {-90, 0}, extent = {{-52, -58}, {52, 58}})));
  Modelica.Blocks.Math.Gain core_output_1_sign(k = 1) 
    annotation(Placement(transformation(origin = {0, 35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain core_output_2_sign(k = -1) 
    annotation(Placement(transformation(origin = {0, 10}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain core_output_3_sign(k = 1) 
    annotation(Placement(transformation(origin = {0, -15}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain core_output_4_sign(k = -1) 
    annotation(Placement(transformation(origin = {0, -40}, extent = {{-18, -12}, {18, 12}})));
  MoSimQuadrotorModel.Control.Allocation.OfficialPidRotorCommandMapper mapper(
    profile = profile,
    hover_speed = hover_speed,
    command_scale = command_scale,
    yaw_authority_scale = yaw_authority_scale,
    yaw_pattern = yaw_pattern) 
    annotation(Placement(transformation(origin = {105, 0}, extent = {{-42, -58}, {42, 58}})));

  Real amplitude_command[4]
    "Original embedded controller outputs after the original rotor signs";
  Real yaw_amplitude
    "Projection of the embedded mixer output onto the physical yaw-reaction pattern";
  Real non_yaw_amplitude[4]
    "Collective, roll, and pitch components retained from the embedded mixer";
  Real mapped_amplitude[4]
    "Embedded yaw component mapped to the shared physical yaw authority";
  Real mapped_collective_amplitude_error
    "Linear collective preservation check; zero means the map did not alter total amplitude";
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(position_ref, core.position_command) 
    annotation(Line(points = {{-160, 45}, {-142, 45}}, color = {0, 0, 127}));
  connect(position_mea, core.position) 
    annotation(Line(points = {{-160, 20}, {-142, 20}}, color = {0, 0, 127}));
  connect(attitude_mea, core.angle) 
    annotation(Line(points = {{-160, -15}, {-142, -15}}, color = {0, 0, 127}));

  connect(core.y, core_output_1_sign.u) 
    annotation(Line(points = {{-38, 30}, {-18, 30}, {-18, 35}}, color = {0, 0, 127}));
  connect(core_output_1_sign.y, mapper.amplitude_command[1]) 
    annotation(Line(points = {{18, 35}, {45, 35}, {45, 25}, {63, 25}}, color = {0, 0, 127}));
  connect(core.y1, core_output_2_sign.u) 
    annotation(Line(points = {{-38, 10}, {-18, 10}}, color = {0, 0, 127}));
  connect(core_output_2_sign.y, mapper.amplitude_command[2]) 
    annotation(Line(points = {{18, 10}, {50, 10}, {50, 15}, {63, 15}}, color = {0, 0, 127}));
  connect(core.y2, core_output_3_sign.u) 
    annotation(Line(points = {{-38, -10}, {-18, -10}, {-18, -15}}, color = {0, 0, 127}));
  connect(core_output_3_sign.y, mapper.amplitude_command[3]) 
    annotation(Line(points = {{18, -15}, {55, -15}, {55, 5}, {63, 5}}, color = {0, 0, 127}));
  connect(core.y3, core_output_4_sign.u) 
    annotation(Line(points = {{-38, -30}, {-18, -30}, {-18, -40}}, color = {0, 0, 127}));
  connect(core_output_4_sign.y, mapper.amplitude_command[4]) 
    annotation(Line(points = {{18, -40}, {60, -40}, {60, -5}, {63, -5}}, color = {0, 0, 127}));
  connect(mapper.rotor_command, rotor_command) 
    annotation(Line(points = {{147, 25}, {180, 25}}, color = {0, 0, 127}));

  amplitude_command[1] = core_output_1_sign.y;
  amplitude_command[2] = core_output_2_sign.y;
  amplitude_command[3] = core_output_3_sign.y;
  amplitude_command[4] = core_output_4_sign.y;
  yaw_amplitude = mapper.yaw_amplitude;
  non_yaw_amplitude = mapper.non_yaw_amplitude;
  mapped_amplitude = mapper.mapped_amplitude;
  mapped_collective_amplitude_error = mapper.mapped_collective_amplitude_error;

  annotation(
    Diagram(coordinateSystem(extent = {{-180, -135}, {180, 135}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 130, 0},
        fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 25}, extent = {{-90, 20}, {90, -20}},
        textString = "Official PID", textColor = {0, 130, 0}),
      Text(origin = {0, -25}, extent = {{-90, 15}, {90, -15}},
        textString = "GRAPHICAL", textColor = {0, 130, 0})}),
    __MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"));
end OfficialPIDGraphicalRotorAdapter;