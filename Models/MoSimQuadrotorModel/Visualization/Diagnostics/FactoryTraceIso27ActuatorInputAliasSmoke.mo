within MoSimQuadrotorModel.Visualization.Diagnostics;
model FactoryTraceIso27ActuatorInputAliasSmoke
  "Actuator preflight 27: expose actuator input aliases while preserving Iso26 bridges and output aliases"
  extends FactoryTraceIso26ControllerOutputAliasSmoke;

  Real actuator_input_1;
  Real actuator_input_2;
  Real actuator_input_3;
  Real actuator_input_4;
  Real actuator_input_error_1;
  Real actuator_input_error_2;
  Real actuator_input_error_3;
  Real actuator_input_error_4;
  Real actuator_input_abs_error_sum;

equation
  actuator_input_1 = actuator1_1.u;
  actuator_input_2 = actuator1_2.u;
  actuator_input_3 = actuator1_3.u;
  actuator_input_4 = actuator1_4.u;
  actuator_input_error_1 = actuator_input_1 - pre_actuator_command_1;
  actuator_input_error_2 = actuator_input_2 - pre_actuator_command_2;
  actuator_input_error_3 = actuator_input_3 - pre_actuator_command_3;
  actuator_input_error_4 = actuator_input_4 - pre_actuator_command_4;
  actuator_input_abs_error_sum = abs(actuator_input_error_1) + abs(actuator_input_error_2) + abs(actuator_input_error_3) + abs(actuator_input_error_4);
  annotation(__MWORKS(hide=true,version="26.3.0"));
end FactoryTraceIso27ActuatorInputAliasSmoke;