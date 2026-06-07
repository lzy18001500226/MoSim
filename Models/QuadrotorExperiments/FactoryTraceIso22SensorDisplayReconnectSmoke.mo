model FactoryTraceIso22SensorDisplayReconnectSmoke
  "Sensor-bus reconnect 22: reconnect plant sensor position to navigation display actual_position"
  extends FactoryTraceIso21ControllerRateAliasSmoke;

  Real display_actual_x;
  Real display_actual_y;
  Real display_actual_z;
  Real display_reference_x;
  Real display_reference_y;
  Real display_reference_z;

equation
  connect(sensors1_1.PosMea, navigationDisplay.actual_position);
  display_actual_x = sensors1_1.PosMea[1];
  display_actual_y = sensors1_1.PosMea[2];
  display_actual_z = sensors1_1.PosMea[3];
  display_reference_x = planningReference.position_command[1];
  display_reference_y = planningReference.position_command[2];
  display_reference_z = planningReference.position_command[3];
end FactoryTraceIso22SensorDisplayReconnectSmoke;
