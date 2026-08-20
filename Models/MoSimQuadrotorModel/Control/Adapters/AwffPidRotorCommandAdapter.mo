within MoSimQuadrotorModel.Control.Adapters;
model AwffPidRotorCommandAdapter
  "AWFF PID adapter at the ROTOR_COMMAND boundary for fixed_awff_pid integration"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialRotorCommandController;
  extends ModelWorkspace;
  import BaseWorkspace.*;
  parameter Real legacy_hover_speed = 13.985413115099604;
  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real command_scale = hover_speed / legacy_hover_speed;

  MoSimQuadrotorModel.Control.Implementations.Graphical.AWFF.AwffFullControllerCoreSysblock core 
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-52, -58}, {52, 58}})));
  Modelica.Blocks.Math.Feedback x_error_feedback 
    annotation(Placement(transformation(origin = {-120, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Feedback y_error_feedback 
    annotation(Placement(transformation(origin = {-120, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Feedback z_error_feedback 
    annotation(Placement(transformation(origin = {-120, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant z_ref_rate_source(k = 0) 
    annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.Constant yaw_ref_source(k = 0) 
    annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Math.Gain motor_1_scale(k = command_scale) 
    annotation(Placement(transformation(origin = {90, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor_2_scale(k = command_scale) 
    annotation(Placement(transformation(origin = {90, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor_3_scale(k = command_scale) 
    annotation(Placement(transformation(origin = {90, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor_4_scale(k = command_scale) 
    annotation(Placement(transformation(origin = {90, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor_1_hover(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {120, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor_2_hover(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {120, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor_3_hover(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {120, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor_4_hover(k1 = 1, k2 = 1) 
    annotation(Placement(transformation(origin = {120, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant hover_source(k = hover_speed) 
    annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(position_ref[1], x_error_feedback.u1) 
    annotation(Line(points = {{-160, 50}, {-128, 50}}, color = {0, 0, 127}));
  connect(position_mea[1], x_error_feedback.u2) 
    annotation(Line(points = {{-160, 50}, {-120, 42}}, color = {0, 0, 127}));
  connect(x_error_feedback.y, core.x_error) 
    annotation(Line(points = {{-111, 50}, {-52, 50}}, color = {0, 0, 127}));

  connect(position_ref[2], y_error_feedback.u1) 
    annotation(Line(points = {{-160, 30}, {-128, 30}}, color = {0, 0, 127}));
  connect(position_mea[2], y_error_feedback.u2) 
    annotation(Line(points = {{-160, 30}, {-120, 22}}, color = {0, 0, 127}));
  connect(y_error_feedback.y, core.y_error) 
    annotation(Line(points = {{-111, 30}, {-52, 30}}, color = {0, 0, 127}));

  connect(position_ref[3], z_error_feedback.u1) 
    annotation(Line(points = {{-160, 10}, {-128, 10}}, color = {0, 0, 127}));
  connect(position_mea[3], z_error_feedback.u2) 
    annotation(Line(points = {{-160, 10}, {-120, 2}}, color = {0, 0, 127}));
  connect(z_error_feedback.y, core.z_error) 
    annotation(Line(points = {{-111, 10}, {-52, 10}}, color = {0, 0, 127}));

  connect(z_ref_rate_source.y, core.z_ref_rate) 
    annotation(Line(points = {{0, -10}, {-52, -10}}, color = {0, 0, 127}));
  connect(attitude_mea[1], core.roll_mea) 
    annotation(Line(points = {{-160, -15}, {-52, -15}}, color = {0, 0, 127}));
  connect(attitude_mea[2], core.pitch_mea) 
    annotation(Line(points = {{-160, -20}, {-52, -20}}, color = {0, 0, 127}));
  connect(attitude_mea[3], core.yaw_mea) 
    annotation(Line(points = {{-160, -25}, {-52, -25}}, color = {0, 0, 127}));
  connect(yaw_ref_source.y, core.yaw_ref) 
    annotation(Line(points = {{0, -30}, {-52, -30}}, color = {0, 0, 127}));

  connect(core.y, motor_1_scale.u) 
    annotation(Line(points = {{52, 40}, {78, 40}}, color = {0, 0, 127}));
  connect(motor_1_scale.y, motor_1_hover.u1) 
    annotation(Line(points = {{101, 40}, {108, 46}}, color = {0, 0, 127}));
  connect(hover_source.y, motor_1_hover.u2) 
    annotation(Line(points = {{0, -50}, {105, -50}, {105, 34}, {108, 34}}, color = {0, 0, 127}));
  connect(motor_1_hover.y, rotor_command[1]) 
    annotation(Line(points = {{131, 40}, {180, 40}}, color = {0, 0, 127}));

  connect(core.y1, motor_2_scale.u) 
    annotation(Line(points = {{52, 20}, {78, 20}}, color = {0, 0, 127}));
  connect(motor_2_scale.y, motor_2_hover.u1) 
    annotation(Line(points = {{101, 20}, {108, 26}}, color = {0, 0, 127}));
  connect(hover_source.y, motor_2_hover.u2) 
    annotation(Line(points = {{0, -50}, {105, -50}, {105, 14}, {108, 14}}, color = {0, 0, 127}));
  connect(motor_2_hover.y, rotor_command[2]) 
    annotation(Line(points = {{131, 20}, {180, 20}}, color = {0, 0, 127}));

  connect(core.y2, motor_3_scale.u) 
    annotation(Line(points = {{52, 0}, {78, 0}}, color = {0, 0, 127}));
  connect(motor_3_scale.y, motor_3_hover.u1) 
    annotation(Line(points = {{101, 0}, {108, 6}}, color = {0, 0, 127}));
  connect(hover_source.y, motor_3_hover.u2) 
    annotation(Line(points = {{0, -50}, {105, -50}, {105, -6}, {108, -6}}, color = {0, 0, 127}));
  connect(motor_3_hover.y, rotor_command[3]) 
    annotation(Line(points = {{131, 0}, {180, 0}}, color = {0, 0, 127}));

  connect(core.y3, motor_4_scale.u) 
    annotation(Line(points = {{52, -20}, {78, -20}}, color = {0, 0, 127}));
  connect(motor_4_scale.y, motor_4_hover.u1) 
    annotation(Line(points = {{101, -20}, {108, -14}}, color = {0, 0, 127}));
  connect(hover_source.y, motor_4_hover.u2) 
    annotation(Line(points = {{0, -50}, {105, -50}, {105, -26}, {108, -26}}, color = {0, 0, 127}));
  connect(motor_4_hover.y, rotor_command[4]) 
    annotation(Line(points = {{131, -20}, {180, -20}}, color = {0, 0, 127}));

  annotation(
    Diagram(coordinateSystem(extent = {{-180, -135}, {180, 135}}, grid = {2, 2})),
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 130, 0},
        fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 25}, extent = {{-90, 20}, {90, -20}},
        textString = "AWFF PID", textColor = {0, 130, 0}),
      Text(origin = {0, -25}, extent = {{-90, 15}, {90, -15}},
        textString = "ROTOR CMD", textColor = {0, 130, 0})}),
    __MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"));
end AwffPidRotorCommandAdapter;
