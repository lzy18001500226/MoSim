within QuadrotorExperiments.DynamicsUpgrade;
model Sunray150DynamicsUpgradeHoverSmoke
  "Hover smoke for the experimental Sunray150 rotor dynamics upgrade"
  Sunray150RflyStyleRotorDynamics dynamics;
equation
  dynamics.motor_command = {
    dynamics.spin_command_sign[1] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[2] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[3] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[4] * dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
  annotation(__MWORKS(hide=true));
end Sunray150DynamicsUpgradeHoverSmoke;
