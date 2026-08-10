within MoSimQuadrotorModel.Vehicle.LegacyDiagnostics;
model HoverSmoke
  "Hover smoke for the experimental Sunray150 rotor dynamics upgrade"
  MoSimQuadrotorModel.Vehicle.Dynamics.RotorActuatorCore dynamics;
equation
  dynamics.motor_command = {
    dynamics.spin_command_sign[1] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[2] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[3] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[4] * dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end HoverSmoke;