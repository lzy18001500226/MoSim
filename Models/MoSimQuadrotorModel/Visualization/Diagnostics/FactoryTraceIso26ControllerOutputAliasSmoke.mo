within MoSimQuadrotorModel.Visualization.Diagnostics;
model FactoryTraceIso26ControllerOutputAliasSmoke
  "Downstream output 26: expose controller/pre-actuator output aliases while preserving Iso25 bridges"
  extends FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;

  Real controller_output_1;
  Real controller_output_2;
  Real controller_output_3;
  Real controller_output_4;
  Real pre_actuator_delta_1;
  Real pre_actuator_delta_2;
  Real pre_actuator_delta_3;
  Real pre_actuator_delta_4;
  Real pre_actuator_command_1;
  Real pre_actuator_command_2;
  Real pre_actuator_command_3;
  Real pre_actuator_command_4;
  Real pre_actuator_command_sum;

equation
  controller_output_1 = controller3_2.y;
  controller_output_2 = controller3_2.y1;
  controller_output_3 = controller3_2.y2;
  controller_output_4 = controller3_2.y3;
  pre_actuator_delta_1 = motor1_delta_scale.y;
  pre_actuator_delta_2 = motor2_delta_scale.y;
  pre_actuator_delta_3 = motor3_delta_scale.y;
  pre_actuator_delta_4 = motor4_delta_scale.y;
  pre_actuator_command_1 = motor1_hover_sum.y;
  pre_actuator_command_2 = motor2_hover_sum.y;
  pre_actuator_command_3 = motor3_hover_sum.y;
  pre_actuator_command_4 = motor4_hover_sum.y;
  pre_actuator_command_sum = pre_actuator_command_1 + pre_actuator_command_2 + pre_actuator_command_3 + pre_actuator_command_4;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso26ControllerOutputAliasSmoke;