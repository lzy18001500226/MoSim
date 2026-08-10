within MoSimQuadrotorModel.Control.Adapters;
model AWFFGraphicalRotorAdapter
  "Strict graphical AWFF boundary with explicit errors and rotor-command mapping"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / 13.985413115099604;

  MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned.AWFFCoreSysblock core 
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-68, -82}, {68, 82}})));
  Modelica.Blocks.Math.Add x_error(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-130, 125}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add y_error(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-130, 85}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add z_error(k1 = 1, k2 = -1) 
    annotation(Placement(transformation(origin = {-130, 45}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Sources.Constant yaw_ref(k = 0) 
    annotation(Placement(transformation(origin = {-130, -135}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain motor_1_delta(k = command_scale) 
    annotation(Placement(transformation(origin = {105, 95}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain motor_2_delta(k = command_scale) 
    annotation(Placement(transformation(origin = {105, 35}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain motor_3_delta(k = command_scale) 
    annotation(Placement(transformation(origin = {105, -25}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Gain motor_4_delta(k = command_scale) 
    annotation(Placement(transformation(origin = {105, -85}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Sources.Constant motor_1_hover(k = hover_speed) 
    annotation(Placement(transformation(origin = {105, 120}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Sources.Constant motor_2_hover(k = -hover_speed) 
    annotation(Placement(transformation(origin = {105, 60}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Sources.Constant motor_3_hover(k = hover_speed) 
    annotation(Placement(transformation(origin = {105, 0}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Sources.Constant motor_4_hover(k = -hover_speed) 
    annotation(Placement(transformation(origin = {105, -60}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_1_command(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {175, 105}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_2_command(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {175, 45}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_3_command(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {175, -15}, extent = {{-18, -12}, {18, 12}})));
  Modelica.Blocks.Math.Add motor_4_command(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {175, -75}, extent = {{-18, -12}, {18, 12}})));

equation
  connect(position_ref[1], x_error.u1);
  connect(position_mea[1], x_error.u2);
  connect(position_ref[2], y_error.u1);
  connect(position_mea[2], y_error.u2);
  connect(position_ref[3], z_error.u1);
  connect(position_mea[3], z_error.u2);
  connect(x_error.y, core.x_error);
  connect(y_error.y, core.y_error);
  connect(z_error.y, core.z_error);
  connect(velocity_ref[3], core.z_ref_rate);
  connect(attitude_mea[1], core.roll_mea);
  connect(attitude_mea[2], core.pitch_mea);
  connect(attitude_mea[3], core.yaw_mea);
  connect(yaw_ref.y, core.yaw_ref);

  connect(core.y, motor_1_delta.u);
  connect(core.y1, motor_2_delta.u);
  connect(core.y2, motor_3_delta.u);
  connect(core.y3, motor_4_delta.u);
  connect(motor_1_delta.y, motor_1_command.u1);
  connect(motor_2_delta.y, motor_2_command.u1);
  connect(motor_3_delta.y, motor_3_command.u1);
  connect(motor_4_delta.y, motor_4_command.u1);
  connect(motor_1_hover.y, motor_1_command.u2);
  connect(motor_2_hover.y, motor_2_command.u2);
  connect(motor_3_hover.y, motor_3_command.u2);
  connect(motor_4_hover.y, motor_4_command.u2);
  connect(motor_1_command.y, rotor_command[1]);
  connect(motor_2_command.y, rotor_command[2]);
  connect(motor_3_command.y, rotor_command[3]);
  connect(motor_4_command.y, rotor_command[4]);

  annotation(
    Diagram(coordinateSystem(extent = {{-200, -165}, {220, 165}}, grid = {2, 2})),
    __MWORKS(
      version="26.3.0",
      modelType=Control,
      BlockSystem(
        blockKind=BlockKind.userModel,
        SampleTime(auto=true),
        OutputInterval=0.01),
      SysblockVersion="1.0"));
end AWFFGraphicalRotorAdapter;