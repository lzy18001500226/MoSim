within MoSimQuadrotorModel.Guidance.Planning;
model OpenBlocksLinearMPCVehicle
  "Reusable whole-aircraft Linear-MPC tracking vehicle for multi-UAV planning experiments"
  parameter Real initial_position[3] = {0, 0, 0.22};
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604;
  parameter Real hover_motor_speed_cmd = MoSimQuadrotorModel.Parameters.sunray150_virtual_px4_classic_hover_visual_rotor_speed_rad_s;
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd;

  Modelica.Blocks.Interfaces.RealInput position_reference[3] 
    annotation(Placement(transformation(origin = {-120, 60}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealInput z_reference_rate 
    annotation(Placement(transformation(origin = {-120, 10}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealInput yaw_reference 
    annotation(Placement(transformation(origin = {-120, -40}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealOutput position[3] 
    annotation(Placement(transformation(origin = {120, 60}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.RealOutput tracking_error_m 
    annotation(Placement(transformation(origin = {120, 10}, extent = {{-20, -20}, {20, 20}})));

  MoSimQuadrotorModel.Vehicle.Mechanics.QuadChassis chassis(
    body(r_0(start = initial_position, fixed = {true, true, true})));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
  MoSimQuadrotorModel.Vehicle.Sensors.Sensors sensors;

  Modelica.Blocks.Math.Feedback x_error;
  Modelica.Blocks.Math.Feedback y_error;
  Modelica.Blocks.Math.Feedback z_error;
  Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
  Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
  Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
  Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
  Modelica.Blocks.Math.Add motor1_hover_sum;
  Modelica.Blocks.Math.Add motor2_hover_sum;
  Modelica.Blocks.Math.Add motor3_hover_sum;
  Modelica.Blocks.Math.Add motor4_hover_sum;
  Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
  Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);
  MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock controller(
    mpc_acc_limit_xy = 2.7,
    mpc_terminal_gain_xy = 0.12);

equation
  position = sensors.PosMea;
  tracking_error_m = sqrt(
    (position_reference[1] - sensors.PosMea[1]) ^ 2
    + (position_reference[2] - sensors.PosMea[2]) ^ 2
    + (position_reference[3] - sensors.PosMea[3]) ^ 2);

  connect(actuator1.flange_a, chassis.flange_a);
  connect(actuator2.flange_a, chassis.flange_a1);
  connect(actuator3.flange_a, chassis.flange_a2);
  connect(actuator4.flange_a, chassis.flange_a3);
  connect(chassis.frame_a, sensors.frame_a);

  connect(position_reference[1], x_error.u1);
  connect(sensors.PosMea[1], x_error.u2);
  connect(position_reference[2], y_error.u1);
  connect(sensors.PosMea[2], y_error.u2);
  connect(position_reference[3], z_error.u1);
  connect(sensors.PosMea[3], z_error.u2);
  connect(x_error.y, controller.x_error);
  connect(y_error.y, controller.y_error);
  connect(z_error.y, controller.z_error);
  connect(z_reference_rate, controller.z_ref_rate);
  connect(sensors.AngleMea[1], controller.roll_mea);
  connect(sensors.AngleMea[2], controller.pitch_mea);
  connect(sensors.AngleMea[3], controller.yaw_mea);
  connect(yaw_reference, controller.yaw_ref);

  connect(controller.y, motor1_delta_scale.u);
  connect(motor1_delta_scale.y, motor1_hover_sum.u1);
  connect(hover_u1.y, motor1_hover_sum.u2);
  connect(motor1_hover_sum.y, actuator1.u);
  connect(controller.y1, motor2_delta_scale.u);
  connect(motor2_delta_scale.y, motor2_hover_sum.u1);
  connect(hover_u2.y, motor2_hover_sum.u2);
  connect(motor2_hover_sum.y, actuator2.u);
  connect(controller.y2, motor3_delta_scale.u);
  connect(motor3_delta_scale.y, motor3_hover_sum.u1);
  connect(hover_u3.y, motor3_hover_sum.u2);
  connect(motor3_hover_sum.y, actuator3.u);
  connect(controller.y3, motor4_delta_scale.u);
  connect(motor4_delta_scale.y, motor4_hover_sum.u1);
  connect(hover_u4.y, motor4_hover_sum.u2);
  connect(motor4_hover_sum.y, actuator4.u);

  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
      Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {28, 74, 96}, fillColor = {235, 245, 247}, fillPattern = FillPattern.Solid),
      Ellipse(extent = {{-55, 55}, {-15, 15}}, lineColor = {28, 74, 96}),
      Ellipse(extent = {{15, 55}, {55, 15}}, lineColor = {28, 74, 96}),
      Ellipse(extent = {{-55, -15}, {-15, -55}}, lineColor = {28, 74, 96}),
      Ellipse(extent = {{15, -15}, {55, -55}}, lineColor = {28, 74, 96}),
      Line(points = {{-35, 35}, {35, -35}}, color = {28, 74, 96}, thickness = 1.2),
      Line(points = {{35, 35}, {-35, -35}}, color = {28, 74, 96}, thickness = 1.2),
      Text(extent = {{-90, -62}, {90, -88}}, textString = "Linear MPC UAV", textColor = {28, 74, 96})}),
    Diagram(coordinateSystem(extent = {{-140, -100}, {140, 100}})));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end OpenBlocksLinearMPCVehicle;