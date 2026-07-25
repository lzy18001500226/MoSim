within MoSimQuadrotorModel.SceneTrace.Diagnostics;
model FactoryTraceIso28ActuatorToWrenchBridgeSmoke
  "Bridge Iso27 actuator input aliases into the project-owned Sunray150 physical wrench adapter"
  extends FactoryTraceIso27ActuatorInputAliasSmoke;

  PhysicalWrenchAdapter physical_wrench_adapter;
  Real bridge_command_1(unit = "rad/s");
  Real bridge_command_2(unit = "rad/s");
  Real bridge_command_3(unit = "rad/s");
  Real bridge_command_4(unit = "rad/s");
  Real bridge_command_error_abs_sum;
  Real bridge_total_thrust(unit = "N");
  Real bridge_yaw_moment(unit = "N.m");
  Real bridge_applied_force_z_body(unit = "N");
  Real bridge_applied_yaw_torque_body(unit = "N.m");
  Real bridge_force_application_error(unit = "N");
  Real bridge_torque_application_error(unit = "N.m");
  Real bridge_hover_weight_balance_error(unit = "N");
  Real bridge_motor_order_gate_error;
  Real bridge_yaw_direction_gate_error;

equation
  bridge_command_1 = actuator_input_1;
  bridge_command_2 = actuator_input_2;
  bridge_command_3 = actuator_input_3;
  bridge_command_4 = actuator_input_4;

  physical_wrench_adapter.wrapper.motor_command = {
    bridge_command_1,
    bridge_command_2,
    bridge_command_3,
    bridge_command_4};

  bridge_command_error_abs_sum =
    abs(physical_wrench_adapter.wrapper.motor_command[1] - actuator_input_1) +
    abs(physical_wrench_adapter.wrapper.motor_command[2] - actuator_input_2) +
    abs(physical_wrench_adapter.wrapper.motor_command[3] - actuator_input_3) +
    abs(physical_wrench_adapter.wrapper.motor_command[4] - actuator_input_4);
  bridge_total_thrust = physical_wrench_adapter.wrapper_total_thrust;
  bridge_yaw_moment = physical_wrench_adapter.wrapper_yaw_moment;
  bridge_applied_force_z_body = physical_wrench_adapter.applied_force_z_body;
  bridge_applied_yaw_torque_body = physical_wrench_adapter.applied_yaw_torque_body;
  bridge_force_application_error = physical_wrench_adapter.force_application_error;
  bridge_torque_application_error = physical_wrench_adapter.torque_application_error;
  bridge_hover_weight_balance_error = physical_wrench_adapter.hover_weight_balance_error;
  bridge_motor_order_gate_error = physical_wrench_adapter.motor_order_gate_error;
  bridge_yaw_direction_gate_error = physical_wrench_adapter.yaw_direction_gate_error;

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso28ActuatorToWrenchBridgeSmoke;